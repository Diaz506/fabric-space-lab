# 📊 Data Dictionary — Zenith Orbital Space Agency

This directory contains Python scripts to generate and fetch data for the lab, plus pre-generated sample datasets in `sample/`.

## Quick Start

```bash
# Generate synthetic ZOSA data (missions, crew, telemetry)
python generate_synthetic.py

# Fetch real NASA data (requires API key in .env or as argument)
python fetch_nasa_apis.py --api-key YOUR_KEY
# Or use DEMO_KEY for low-rate testing:
python fetch_nasa_apis.py --api-key DEMO_KEY
```

## Real Data (NASA APIs)

### asteroids.csv

Near-Earth Objects from NASA NeoWs API.

| Column | Type | Description |
|--------|------|-------------|
| neo_id | string | NASA NEO reference ID |
| name | string | Asteroid designation (e.g., "433 Eros") |
| estimated_diameter_min_km | float | Estimated minimum diameter (km) |
| estimated_diameter_max_km | float | Estimated maximum diameter (km) |
| is_potentially_hazardous | boolean | NASA's potentially hazardous flag |
| close_approach_date | date | Date of closest approach to Earth |
| miss_distance_au | float | Miss distance in astronomical units |
| miss_distance_km | float | Miss distance in kilometers |
| relative_velocity_kmps | float | Velocity relative to Earth (km/s) |
| orbiting_body | string | Body being orbited (typically "Earth") |

### solar_events.csv

Space weather events from NASA DONKI API.

| Column | Type | Description |
|--------|------|-------------|
| event_id | string | DONKI event identifier |
| event_type | string | CME, Solar Flare, Geomagnetic Storm, etc. |
| start_time | datetime | Event start timestamp (UTC) |
| end_time | datetime | Event end timestamp (UTC, nullable) |
| class_type | string | Classification (e.g., X1.5, M3.2 for flares) |
| source_location | string | Solar coordinates of the event |
| linked_events | string | Comma-separated related event IDs |
| note | string | Event description from DONKI |

### exoplanets.csv

Confirmed exoplanets from NASA Exoplanet Archive.

| Column | Type | Description |
|--------|------|-------------|
| planet_name | string | Planet designation (e.g., "Kepler-442b") |
| host_star | string | Host star name |
| discovery_method | string | Transit, Radial Velocity, Imaging, etc. |
| discovery_year | int | Year of confirmed discovery |
| orbital_period_days | float | Orbital period in Earth days |
| planet_mass_earth | float | Mass relative to Earth |
| planet_radius_earth | float | Radius relative to Earth |
| equilibrium_temp_k | float | Equilibrium temperature (Kelvin) |
| distance_parsecs | float | Distance from Earth in parsecs |
| in_habitable_zone | boolean | Whether in the star's habitable zone (derived) |

## Synthetic Data (ZOSA Internal)

### missions.csv

ZOSA mission records (2020–2026).

| Column | Type | Description |
|--------|------|-------------|
| mission_id | string | ZOSA mission identifier (e.g., "ZOSA-2024-047") |
| mission_name | string | Mission codename (e.g., "Operation Starfall") |
| mission_type | string | Observation, Defense, Research, Survey |
| status | string | Planned, Active, Completed, Aborted |
| priority | string | Critical, High, Medium, Low |
| start_date | date | Mission start date |
| end_date | date | Mission end date (nullable if Active/Planned) |
| target_object | string | Target asteroid/exoplanet/region name |
| primary_ground_station_id | string | Primary ground station ID |
| budget_usd | float | Allocated budget in USD |
| region | string | Ground station region (for RLS demo) |

### crew.csv

ZOSA personnel records.

| Column | Type | Description |
|--------|------|-------------|
| crew_id | string | Personnel ID (e.g., "ZOSA-P-0042") |
| full_name | string | Full name |
| role | string | Scientist, Engineer, Analyst, Commander, Technician |
| specialty | string | Astrophysics, Orbital Mechanics, Data Science, Comms, etc. |
| ground_station_id | string | Assigned ground station |
| region | string | Ground station region (for RLS demo) |
| hire_date | date | Date hired |
| clearance_level | string | Public, Confidential, Secret, Top Secret |
| email | string | ZOSA email address |

### telemetry.csv

Ground station sensor readings (simulated IoT data, 5-min intervals).

| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | Reading timestamp (UTC, 5-min intervals) |
| ground_station_id | string | Ground station identifier |
| ground_station_name | string | Human-readable station name |
| region | string | Geographic region |
| signal_strength_dbm | float | Signal strength in dBm (-120 to -30) |
| antenna_azimuth_deg | float | Antenna azimuth angle (0–360°) |
| antenna_elevation_deg | float | Antenna elevation angle (0–90°) |
| data_rate_mbps | float | Data throughput in Mbps |
| cpu_usage_pct | float | Station CPU usage percentage |
| memory_usage_pct | float | Station memory usage percentage |
| disk_io_mbps | float | Disk I/O throughput |
| temperature_celsius | float | Equipment temperature |
| status | string | Online, Degraded, Offline, Maintenance |

## Ground Stations Reference

| ID | Name | Region | Location |
|----|------|--------|----------|
| GS-01 | Geneva Prime | Europe | Geneva, Switzerland |
| GS-02 | Atacama Deep | South America | Atacama Desert, Chile |
| GS-03 | Mauna Kea Summit | North America | Hawaii, USA |
| GS-04 | Karoo Array | Africa | Karoo, South Africa |
| GS-05 | Svalbard Arctic | Europe | Svalbard, Norway |
| GS-06 | Tanegashima | Asia Pacific | Tanegashima, Japan |
| GS-07 | Parkes South | Oceania | Parkes, Australia |
| GS-08 | Goldstone | North America | California, USA |
| GS-09 | Jodrell Bank | Europe | Cheshire, UK |
| GS-10 | Tidbinbilla | Oceania | Canberra, Australia |
| GS-11 | Usuda Deep Space | Asia Pacific | Nagano, Japan |
| GS-12 | Cebreros | Europe | Cebreros, Spain |

