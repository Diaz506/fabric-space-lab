"""
Generate synthetic data for the Zenith Orbital Space Agency (ZOSA) Fabric lab.

Produces three CSV files in data/sample/:
  - missions.csv   (150 rows, 2020-2026)
  - crew.csv        (200 rows)
  - telemetry.csv   (~2 000 rows, 7 days × 5-min intervals × 2 stations)

All randomness is seeded with 42 for full reproducibility.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "sample"

GROUND_STATIONS = {
    "GS-01": ("Geneva Prime", "Europe"),
    "GS-02": ("Atacama Deep", "South America"),
    "GS-03": ("Mauna Kea Summit", "North America"),
    "GS-04": ("Karoo Array", "Africa"),
    "GS-05": ("Svalbard Arctic", "Europe"),
    "GS-06": ("Tanegashima", "Asia Pacific"),
    "GS-07": ("Parkes South", "Oceania"),
    "GS-08": ("Goldstone", "North America"),
    "GS-09": ("Jodrell Bank", "Europe"),
    "GS-10": ("Tidbinbilla", "Oceania"),
    "GS-11": ("Usuda Deep Space", "Asia Pacific"),
    "GS-12": ("Cebreros", "Europe"),
}

GS_IDS = list(GROUND_STATIONS.keys())

MISSION_TYPES = ["Observation", "Defense", "Research", "Survey"]
STATUSES = ["Completed", "Active", "Planned", "Aborted"]
STATUS_WEIGHTS = [0.50, 0.20, 0.20, 0.10]
PRIORITIES = ["Critical", "High", "Medium", "Low"]

TARGET_OBJECTS = [
    "433 Eros", "101955 Bennu", "162173 Ryugu", "25143 Itokawa",
    "4 Vesta", "1 Ceres", "951 Gaspra", "243 Ida",
    "Kepler-442b", "Kepler-186f", "TRAPPIST-1e", "Proxima Centauri b",
    "TOI-700d", "K2-18b", "LHS 1140b", "HD 40307g",
    "Sector 7G", "Lagrange Point L2", "Oort Cloud Fringe",
    "Kuiper Belt Object 2014 MU69", "Alpha Centauri Region",
    "Mars Orbit Corridor", "Lunar South Pole", "Jupiter Trojans",
]

CODENAME_ADJ = [
    "Silent", "Crimson", "Deep", "Frozen", "Iron", "Velvet", "Rapid",
    "Hollow", "Silver", "Dark", "Bright", "Phantom", "Solar", "Cosmic",
    "Amber", "Crystal", "Thunder", "Quiet", "Nova", "Polar",
]
CODENAME_NOUN = [
    "Echo", "Horizon", "Vanguard", "Zenith", "Apex", "Sentinel",
    "Starfall", "Comet", "Orbit", "Beacon", "Nomad", "Pulsar",
    "Nebula", "Drift", "Flare", "Vertex", "Meridian", "Solstice",
    "Tempest", "Aegis",
]

ROLES = ["Scientist", "Engineer", "Analyst", "Commander", "Technician"]
SPECIALTIES = [
    "Astrophysics", "Orbital Mechanics", "Data Science", "Communications",
    "Propulsion", "Optics", "Astrobiology", "Signal Processing",
]
CLEARANCE_LEVELS = ["Public", "Confidential", "Secret", "Top Secret"]
CLEARANCE_WEIGHTS = [0.40, 0.30, 0.20, 0.10]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _random_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------
def generate_missions(n: int = 150) -> pd.DataFrame:
    """Generate missions.csv with *n* rows spanning 2020-2026."""
    print(f"⏳  Generating {n} missions …")
    used_names: set[str] = set()
    rows = []

    for i in range(n):
        year = random.randint(2020, 2026)
        seq = i + 1
        mission_id = f"ZOSA-{year}-{seq:03d}"

        # Unique codename
        while True:
            name = f"{random.choice(['Operation', 'Project', 'Mission'])} {random.choice(CODENAME_ADJ)} {random.choice(CODENAME_NOUN)}"
            if name not in used_names:
                used_names.add(name)
                break

        status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
        start_date = _random_date(datetime(2020, 1, 1), datetime(2026, 6, 30))

        if status in ("Active", "Planned"):
            end_date = None
        else:
            end_date = start_date + timedelta(days=random.randint(30, 365))

        gs_id = random.choice(GS_IDS)
        _, region = GROUND_STATIONS[gs_id]

        rows.append({
            "mission_id": mission_id,
            "mission_name": name,
            "mission_type": random.choice(MISSION_TYPES),
            "status": status,
            "priority": random.choice(PRIORITIES),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
            "target_object": random.choice(TARGET_OBJECTS),
            "primary_ground_station_id": gs_id,
            "budget_usd": round(random.uniform(500_000, 50_000_000), 2),
            "region": region,
        })

    df = pd.DataFrame(rows)
    print(f"   ✅  missions.csv — {len(df)} rows")
    return df


def generate_crew(n: int = 200) -> pd.DataFrame:
    """Generate crew.csv with *n* rows of personnel records."""
    print(f"⏳  Generating {n} crew members …")
    rows = []

    for i in range(n):
        crew_id = f"ZOSA-P-{i + 1:04d}"
        first = fake.first_name()
        last = fake.last_name()
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@zenithorbital.org"

        gs_id = random.choice(GS_IDS)
        _, region = GROUND_STATIONS[gs_id]

        rows.append({
            "crew_id": crew_id,
            "full_name": full_name,
            "role": random.choice(ROLES),
            "specialty": random.choice(SPECIALTIES),
            "ground_station_id": gs_id,
            "region": region,
            "hire_date": _random_date(datetime(2019, 1, 1), datetime(2026, 3, 1)).strftime("%Y-%m-%d"),
            "clearance_level": random.choices(CLEARANCE_LEVELS, CLEARANCE_WEIGHTS)[0],
            "email": email,
        })

    df = pd.DataFrame(rows)
    print(f"   ✅  crew.csv — {len(df)} rows")
    return df


def generate_telemetry() -> pd.DataFrame:
    """Generate telemetry.csv — 7 days of 5-min readings for two stations."""
    stations = [
        ("GS-01", "Geneva Prime", "Europe"),
        ("GS-06", "Tanegashima", "Asia Pacific"),
    ]
    start = datetime(2026, 4, 1)
    end = datetime(2026, 4, 8)  # exclusive
    timestamps = pd.date_range(start, end, freq="5min", inclusive="left")
    total = len(timestamps) * len(stations)
    print(f"⏳  Generating ~{total} telemetry rows (7 days × 5-min × 2 stations) …")

    rows = []
    for ts in timestamps:
        for gs_id, gs_name, region in stations:
            # Hours since start — drives slow-moving patterns
            hours = (ts - start).total_seconds() / 3600

            signal = np.clip(np.random.normal(-60, 15), -120, -30)
            azimuth = (hours * 15 + np.random.normal(0, 2)) % 360
            elevation = 50 + 30 * np.sin(hours * np.pi / 12) + np.random.normal(0, 2)
            elevation = np.clip(elevation, 15, 85)
            data_rate = np.clip(np.random.normal(100, 30), 1, 250)

            # CPU: baseline with occasional spikes
            cpu = np.clip(np.random.normal(45, 12), 20, 95)
            if random.random() < 0.05:
                cpu = np.clip(cpu + random.uniform(20, 40), 20, 95)

            memory = np.clip(np.random.normal(60, 8), 40, 80)
            disk_io = np.clip(np.random.normal(80, 40), 10, 200)

            # Temperature: slight daily sinusoidal cycle
            temp = 28 + 6 * np.sin((hours - 6) * np.pi / 12) + np.random.normal(0, 1.5)
            temp = np.clip(temp, 18, 45)

            status = random.choices(
                ["Online", "Degraded", "Offline", "Maintenance"],
                [0.95, 0.03, 0.01, 0.01],
            )[0]

            rows.append({
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ground_station_id": gs_id,
                "ground_station_name": gs_name,
                "region": region,
                "signal_strength_dbm": round(float(signal), 2),
                "antenna_azimuth_deg": round(float(azimuth), 2),
                "antenna_elevation_deg": round(float(elevation), 2),
                "data_rate_mbps": round(float(data_rate), 2),
                "cpu_usage_pct": round(float(cpu), 2),
                "memory_usage_pct": round(float(memory), 2),
                "disk_io_mbps": round(float(disk_io), 2),
                "temperature_celsius": round(float(temp), 2),
                "status": status,
            })

    df = pd.DataFrame(rows)
    print(f"   ✅  telemetry.csv — {len(df)} rows")
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📂  Output directory: {OUTPUT_DIR}\n")

    missions = generate_missions()
    missions.to_csv(OUTPUT_DIR / "missions.csv", index=False)

    crew = generate_crew()
    crew.to_csv(OUTPUT_DIR / "crew.csv", index=False)

    telemetry = generate_telemetry()
    telemetry.to_csv(OUTPUT_DIR / "telemetry.csv", index=False)

    print(f"\n🚀  Done — 3 files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
