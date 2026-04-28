"""Fetch real data from NASA public APIs and save as CSV files."""

import argparse
import time
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

DEFAULT_API_KEY = "DEMO_KEY"
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds


def api_get(url: str, params: dict, label: str, retries: int = MAX_RETRIES) -> requests.Response:
    """GET with exponential backoff and rate-limit handling."""
    for attempt in range(1, retries + 1):
        print(f"  [{label}] attempt {attempt}/{retries} …")
        try:
            resp = requests.get(url, params=params, timeout=60)
            if resp.status_code == 429:
                wait = BACKOFF_BASE ** attempt * 5
                print(f"  Rate limited — waiting {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            if attempt == retries:
                print(f"  ✗ {label} failed after {retries} attempts: {exc}")
                raise
            wait = BACKOFF_BASE ** attempt
            print(f"  Retrying in {wait}s ({exc})")
            time.sleep(wait)


# ── 1. Asteroids (NeoWs) ────────────────────────────────────────────────────

def fetch_asteroids(api_key: str, days: int) -> pd.DataFrame:
    """Fetch near-Earth objects from NeoWs, 7-day windows at a time."""
    print("\n★ Fetching asteroids from NeoWs …")
    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)
    rows = []

    # NeoWs accepts max 7-day windows
    window_start = start
    while window_start <= end:
        window_end = min(window_start + timedelta(days=6), end)
        params = {
            "start_date": window_start.isoformat(),
            "end_date": window_end.isoformat(),
            "api_key": api_key,
        }
        label = f"NeoWs {window_start}→{window_end}"
        resp = api_get("https://api.nasa.gov/neo/rest/v1/feed", params, label)
        data = resp.json()

        for date_str, neos in data.get("near_earth_objects", {}).items():
            for neo in neos:
                diam = neo.get("estimated_diameter", {}).get("kilometers", {})
                for ca in neo.get("close_approach_data", []):
                    rows.append({
                        "neo_id": neo["id"],
                        "name": neo["name"],
                        "estimated_diameter_min_km": diam.get("estimated_diameter_min"),
                        "estimated_diameter_max_km": diam.get("estimated_diameter_max"),
                        "is_potentially_hazardous": neo.get("is_potentially_hazardous_asteroid"),
                        "close_approach_date": ca.get("close_approach_date"),
                        "miss_distance_au": ca.get("miss_distance", {}).get("astronomical"),
                        "miss_distance_km": ca.get("miss_distance", {}).get("kilometers"),
                        "relative_velocity_kmps": ca.get("relative_velocity", {}).get("kilometers_per_second"),
                        "orbiting_body": ca.get("orbiting_body"),
                    })
        window_start = window_end + timedelta(days=1)

    df = pd.DataFrame(rows)
    print(f"  ✓ {len(df)} asteroid close-approach records")
    return df


# ── 2. Solar Events (DONKI) ─────────────────────────────────────────────────

DONKI_ENDPOINTS = {
    "Solar Flare": "https://api.nasa.gov/DONKI/FLR",
    "Coronal Mass Ejection": "https://api.nasa.gov/DONKI/CME",
    "Geomagnetic Storm": "https://api.nasa.gov/DONKI/GST",
}


def _normalize_donki(event: dict, event_type: str) -> dict:
    """Map varying DONKI schemas into a unified row."""
    linked = event.get("linkedEvents") or []
    linked_str = "; ".join(e.get("activityID", "") for e in linked) if linked else ""

    if event_type == "Solar Flare":
        return {
            "event_id": event.get("flrID"),
            "event_type": event_type,
            "start_time": event.get("beginTime"),
            "end_time": event.get("endTime"),
            "class_type": event.get("classType"),
            "source_location": event.get("sourceLocation"),
            "linked_events": linked_str,
            "note": (event.get("note") or "")[:500],
        }
    if event_type == "Coronal Mass Ejection":
        return {
            "event_id": event.get("activityID"),
            "event_type": event_type,
            "start_time": event.get("startTime"),
            "end_time": None,
            "class_type": event.get("type"),
            "source_location": event.get("sourceLocation"),
            "linked_events": linked_str,
            "note": (event.get("note") or "")[:500],
        }
    # Geomagnetic Storm
    return {
        "event_id": event.get("gstID"),
        "event_type": event_type,
        "start_time": event.get("startTime"),
        "end_time": None,
        "class_type": None,
        "source_location": None,
        "linked_events": linked_str,
        "note": (event.get("link") or "")[:500],
    }


def fetch_solar_events(api_key: str, days: int) -> pd.DataFrame:
    """Fetch solar flares, CMEs, and geomagnetic storms from DONKI."""
    print("\n★ Fetching solar events from DONKI …")
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    rows = []

    for etype, url in DONKI_ENDPOINTS.items():
        params = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "api_key": api_key,
        }
        try:
            resp = api_get(url, params, etype)
            events = resp.json()
            if not isinstance(events, list):
                print(f"  ⚠ Unexpected response for {etype}, skipping")
                continue
            for ev in events:
                rows.append(_normalize_donki(ev, etype))
            print(f"  ✓ {len(events)} {etype} events")
        except requests.RequestException:
            print(f"  ⚠ Skipping {etype} due to API error")

    df = pd.DataFrame(rows)
    print(f"  ✓ {len(df)} total solar events")
    return df


# ── 3. Exoplanets (TAP) ─────────────────────────────────────────────────────

EXOPLANET_QUERY = (
    "SELECT pl_name,hostname,discoverymethod,disc_year,pl_orbper,"
    "pl_bmasse,pl_rade,pl_eqt,sy_dist "
    "FROM ps WHERE default_flag=1 ORDER BY disc_year DESC"
)

RENAME_MAP = {
    "pl_name": "planet_name",
    "hostname": "host_star",
    "discoverymethod": "discovery_method",
    "disc_year": "discovery_year",
    "pl_orbper": "orbital_period_days",
    "pl_bmasse": "planet_mass_earth",
    "pl_rade": "planet_radius_earth",
    "pl_eqt": "equilibrium_temp_k",
    "sy_dist": "distance_parsecs",
}


def fetch_exoplanets() -> pd.DataFrame:
    """Query the NASA Exoplanet Archive via TAP (no API key needed)."""
    print("\n★ Fetching exoplanets from NASA Exoplanet Archive …")
    params = {"query": EXOPLANET_QUERY, "format": "csv"}
    resp = api_get(
        "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
        params,
        "Exoplanet Archive",
    )
    df = pd.read_csv(StringIO(resp.text))
    df.rename(columns=RENAME_MAP, inplace=True)

    # Derived column: habitable-zone estimate (180–310 K)
    if "equilibrium_temp_k" in df.columns:
        df["in_habitable_zone"] = df["equilibrium_temp_k"].between(180, 310)
    else:
        df["in_habitable_zone"] = pd.NA

    print(f"  ✓ {len(df)} confirmed exoplanets")
    return df


# ── Main ─────────────────────────────────────────────────────────────────────

def save(df: pd.DataFrame, path: Path, name: str) -> None:
    dest = path / name
    df.to_csv(dest, index=False)
    print(f"  → Saved {dest}  ({len(df)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch NASA open datasets → CSV")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="NASA API key (default: DEMO_KEY)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: <script>/sample)")
    parser.add_argument("--days", type=int, default=None, help="Days of history for NeoWs (default 7) / DONKI (default 365)")
    args = parser.parse_args()

    out = args.output_dir or (Path(__file__).resolve().parent / "sample")
    out.mkdir(parents=True, exist_ok=True)
    neo_days = args.days or 7
    donki_days = args.days or 365

    print(f"Output → {out}")
    print(f"API key: {args.api_key[:4]}{'*' * max(0, len(args.api_key) - 4)}")

    save(fetch_asteroids(args.api_key, neo_days), out, "asteroids.csv")
    save(fetch_solar_events(args.api_key, donki_days), out, "solar_events.csv")
    save(fetch_exoplanets(), out, "exoplanets.csv")

    print("\n✅ All datasets fetched successfully.")


if __name__ == "__main__":
    main()
