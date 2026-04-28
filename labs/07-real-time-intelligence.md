# Module 07 — Real-Time Intelligence

> **BREAKING:** Geneva Prime ground station detected a new near-Earth object on an unusual trajectory. Major Nakamura bursts into the data center: *"We need real-time alerts. Not tomorrow — NOW. If something comes within 0.05 AU, I want to know within seconds."*

**⏱️ Estimated time:** 45–60 minutes

---

## 🌐 1 — Real-Time Hub Overview

The **Real-Time Hub** is Fabric's centralized management surface for all streaming artifacts — Eventstreams, Eventhouse databases, and Activator alerts live here in one place. Think of it as Mission Control for every piece of data that moves in real time.

1. In the Fabric portal, click **Real-Time Hub** in the left navigation pane.
2. Explore the three tabs:
   - **My streams** — Eventstreams you own or have access to.
   - **All streams** — Organization-wide streaming sources.
   - **Alerts** — Active Activator rules and their status.

> 💡 **Tip:** As you build artifacts in this module, return to the Real-Time Hub to see them appear automatically. It is the single pane of glass for everything real-time.

---

## 🏠 2 — Create an Eventhouse

An **Eventhouse** is Fabric's real-time analytics engine, optimized for time-series and log data. It delivers sub-second query performance using the Kusto Query Language (KQL). Inside an Eventhouse you create one or more KQL databases to organize your data.

### Steps

1. Navigate to your **ZOSA** workspace.
2. Click **+ New item** → select **Eventhouse**.
3. Name it: `zosa_eventhouse` → click **Create**.
4. Once the Eventhouse opens, a default KQL database is created automatically. Rename it to `asteroid_detections` (or create a new one with that name).
5. Confirm the database appears under your Eventhouse in the workspace list.

> 📖 **Why Eventhouse?** Traditional Lakehouse queries run in seconds to minutes. Eventhouse returns results in *milliseconds* — essential when Major Nakamura wants to know about a close approach *now*, not after the next Spark job finishes.

---

## 📡 3 — Create an Eventstream

An **Eventstream** is a no-code streaming pipeline that captures, transforms, and routes real-time events. For this lab you will simulate live asteroid detections using a Custom App source.

### Steps

1. In your workspace, click **+ New item** → select **Eventstream**.
2. Name it: `asteroid_feed` → click **Create**.
3. In the Eventstream canvas, click **New source** → **Custom App**.
4. Copy the **connection string / endpoint URL** shown — you will need it for the simulator script below.

### Simulator Script

Create a Python file `simulate_detections.py` on your local machine and run it while you work through the rest of this module:

```python
import requests
import json
import time
import random
from datetime import datetime

# Paste the connection string from Eventstream Custom App source
ENDPOINT = "YOUR_EVENTSTREAM_ENDPOINT"

OBJECTS = ["2024 XR1", "2025 AB3", "2024 QZ7", "2025 KN9", "2024 VT2"]
STATIONS = ["GS-01", "GS-03", "GS-06", "GS-11"]

print("🚀 Asteroid detection simulator started — Ctrl+C to stop")

while True:
    event = {
        "detection_id": f"DET-{random.randint(10000, 99999)}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "object_name": random.choice(OBJECTS),
        "miss_distance_au": round(random.uniform(0.01, 0.5), 4),
        "velocity_kmps": round(random.uniform(5.0, 35.0), 2),
        "estimated_diameter_km": round(random.uniform(0.01, 2.0), 3),
        "ground_station_id": random.choice(STATIONS),
        "is_potentially_hazardous": random.random() < 0.3,
    }
    try:
        resp = requests.post(ENDPOINT, json=event)
        status = "✅" if resp.status_code < 300 else f"⚠️ {resp.status_code}"
        print(f"{status} Sent {event['detection_id']} — {event['object_name']} at {event['miss_distance_au']} AU")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(5)
```

> ⚠️ **Important:** Replace `YOUR_EVENTSTREAM_ENDPOINT` with the actual endpoint URL copied from step 4. Keep the script running in a terminal for the remainder of this module.

---

## 🔗 4 — Direct Ingestion to Eventhouse

With **direct ingestion**, the Eventstream routes raw events straight into your Eventhouse KQL database — no intermediate Lakehouse or transformation step required.

### Steps

1. Return to the `asteroid_feed` Eventstream canvas.
2. Click **New destination** → **Eventhouse**.
3. Select:
   - **Workspace:** your ZOSA workspace
   - **Eventhouse:** `zosa_eventhouse`
   - **KQL Database:** `asteroid_detections`
4. Under **Table**, choose **Create new** → name it `asteroid_detections`.
5. Fabric auto-detects the schema from incoming events. Review the column mapping:

   | Source field | Column name | Data type |
   |---|---|---|
   | `detection_id` | `detection_id` | `string` |
   | `timestamp` | `timestamp` | `datetime` |
   | `object_name` | `object_name` | `string` |
   | `miss_distance_au` | `miss_distance_au` | `real` |
   | `velocity_kmps` | `velocity_kmps` | `real` |
   | `estimated_diameter_km` | `estimated_diameter_km` | `real` |
   | `ground_station_id` | `ground_station_id` | `string` |
   | `is_potentially_hazardous` | `is_potentially_hazardous` | `bool` |

6. Click **Publish**. Within seconds, events from the simulator start landing in the Eventhouse.

> 💡 **Tip:** Click **Data preview** on the destination node to confirm rows are arriving.

---

## 🔍 5 — KQL Queries

Open a **KQL Queryset** against your `asteroid_detections` database to explore the live data.

1. In your workspace, click **+ New item** → **KQL Queryset**.
2. Name it `asteroid_exploration` and connect it to the `asteroid_detections` database.

### Last 10 Detections

```kql
asteroid_detections
| order by timestamp desc
| take 10
```

### Close Approaches (< 0.05 AU) in the Last Hour

```kql
asteroid_detections
| where timestamp > ago(1h)
| where miss_distance_au < 0.05
| project timestamp, object_name, miss_distance_au, velocity_kmps
| order by miss_distance_au asc
```

### Detection Rate per 10-Minute Window

```kql
asteroid_detections
| summarize count() by bin(timestamp, 10m)
| render timechart
```

### Hazardous Object Breakdown

```kql
asteroid_detections
| where timestamp > ago(1h)
| summarize
    total = count(),
    hazardous = countif(is_potentially_hazardous),
    closest = min(miss_distance_au)
  by object_name
| extend hazard_pct = round(100.0 * hazardous / total, 1)
| order by closest asc
```

> 📖 **Note:** KQL is purpose-built for time-series analytics. Queries that would take minutes in SQL run in milliseconds here because the Eventhouse indexes data by time automatically.

---

## 📊 6 — Materialized Views

**Materialized views** pre-compute rolling aggregations inside the Eventhouse. Dashboards read from the view instead of scanning raw data, which dramatically improves performance at scale.

Run the following command in your KQL Queryset:

```kql
.create materialized-view HourlyDetectionSummary on table asteroid_detections
{
    asteroid_detections
    | summarize
        total_detections = count(),
        hazardous_count = countif(is_potentially_hazardous),
        min_distance = min(miss_distance_au),
        avg_velocity = avg(velocity_kmps)
      by bin(timestamp, 1h)
}
```

Verify the view is working:

```kql
HourlyDetectionSummary
| order by timestamp desc
| take 24
```

> 💡 **Tip:** Materialized views update incrementally as new data arrives — you do not need to refresh them manually. They are ideal for dashboard tiles that display hourly or daily summaries.

---

## 📈 7 — Real-Time Dashboard

Create a live dashboard that Mission Control can display on the big screen.

### Steps

1. In your workspace, click **+ New item** → **Real-Time Dashboard**.
2. Name it: `Asteroid Mission Control`.
3. Click **+ Add tile** and connect to the `asteroid_detections` database.

### Suggested Tiles

| Tile | KQL Query | Visual type |
|---|---|---|
| **Total Detections (24 h)** | `asteroid_detections \| where timestamp > ago(24h) \| count` | Stat / KPI card |
| **Closest Approach** | `asteroid_detections \| where timestamp > ago(1h) \| summarize min(miss_distance_au)` | Gauge |
| **Detection Timeline** | `asteroid_detections \| summarize count() by bin(timestamp, 10m) \| render timechart` | Time chart |
| **Hazardous Rate** | `HourlyDetectionSummary \| extend rate = round(100.0 * hazardous_count / total_detections, 1) \| project timestamp, rate \| render timechart` | Time chart |
| **Ground Station Activity** | `asteroid_detections \| where timestamp > ago(1h) \| summarize count() by ground_station_id \| render piechart` | Pie chart |

4. After adding all tiles, click **Manage** → **Auto refresh** → set interval to **30 seconds**.
5. Click **Save** and optionally pin the dashboard to the workspace home.

> 🎯 **Pro tip:** Drag and resize tiles to create a Mission Control layout. Put the closest-approach gauge front and center — that is the number Major Nakamura cares about most.

---

## 🚨 8 — Activator — Set Alert

**Activator** lets you define automated alerts that fire when real-time data meets a condition. No code required — you configure everything visually.

### Steps

1. Open your `Asteroid Mission Control` Real-Time Dashboard.
2. Hover over the **Closest Approach** gauge tile.
3. Click the **ellipsis (…)** menu → **Set alert**.
4. Configure the alert rule:

   | Setting | Value |
   |---|---|
   | **Condition** | `min_distance` is less than `0.05` |
   | **Evaluate every** | 1 minute |
   | **Alert name** | `Close Approach Warning` |

5. Add **Actions**:
   - ✉️ **Send an email** → enter Major Nakamura's email address.
   - 💬 **Post to a Teams channel** → select the ZOSA Mission Control channel.
   - 📓 **Run a Fabric notebook** → select a notification/logging notebook (optional).

6. Click **Create**. The Activator item appears in your workspace.

> 📖 **How it works:** Activator evaluates the condition on the schedule you set. When the condition is true, it executes *all* configured actions and passes event context (object name, distance, velocity) as dynamic parameters. You can view the alert history and manage all Activator items from the **Real-Time Hub → Alerts** tab.

> ⚠️ **Important:** In this lab, use your own email to test. You should receive an alert within a few minutes because the simulator generates close approaches (< 0.05 AU) roughly 10% of the time.

---

## ❄️ 9 — Hot/Cold Data Pattern

Real-time and batch analytics work best together. Here is the architecture ZOSA uses:

```
                        ┌─────────────────────┐
  Ground Stations ──▶   │   Eventstream        │
                        │   (asteroid_feed)    │
                        └────────┬────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼                          ▼
          ┌─────────────────┐       ┌──────────────────┐
          │   Eventhouse     │       │   Lakehouse       │
          │   (HOT PATH)     │       │   (COLD PATH)     │
          │                  │       │                    │
          │ • Last 30 days   │       │ • Full history     │
          │ • Sub-second KQL │       │ • Spark / SQL      │
          │ • Dashboards     │       │ • ML training      │
          │ • Activator      │       │ • Power BI (batch) │
          └─────────────────┘       └──────────────────┘
                    │                          ▲
                    └── Retention policy ──────┘
                        (auto-export after 30d)
```

### Key Concepts

- **Hot path (Eventhouse):** Holds the last 30 days of data. Optimized for sub-second KQL queries, live dashboards, and Activator alerts. This is where Mission Control looks when an asteroid is approaching *right now*.

- **Cold path (Lakehouse via OneLake):** Stores the full historical archive. Queried via the Lakehouse SQL analytics endpoint or Spark notebooks for batch analytics, Power BI semantic models, and ML training. This is where Dr. Osei's data science team runs predictive models.

- **Automatic transition:** Configure an Eventhouse **retention policy** to export data older than 30 days to OneLake automatically. Cold data remains queryable — it just moves to a more cost-effective storage tier.

### Configure Retention (Optional)

```kql
// Set 30-day retention on the asteroid_detections table
.alter table asteroid_detections policy retention
```
```json
{
    "SoftDeletePeriod": "30.00:00:00",
    "Recoverability": "Enabled"
}
```

> 💡 **Tip:** In a production scenario, you would also configure a **data export rule** or use the Eventstream's second destination to write simultaneously to both the Eventhouse and the Lakehouse. This gives you real-time *and* historical coverage from a single stream.

---

## ✅ Checkpoint

Verify that all components are working end-to-end:

- [ ] **Eventhouse** `zosa_eventhouse` created with KQL database `asteroid_detections`
- [ ] **Eventstream** `asteroid_feed` receiving simulated events from the Python script
- [ ] **KQL queries** return results in the KQL Queryset
- [ ] **Materialized view** `HourlyDetectionSummary` returns aggregated data
- [ ] **Real-Time Dashboard** `Asteroid Mission Control` shows live data with 30-second refresh
- [ ] **Activator alert** `Close Approach Warning` configured for miss distance < 0.05 AU

> 🎉 If all boxes are checked, ZOSA now has a complete real-time detection pipeline — from ground station to Major Nakamura's phone in seconds.

---

## 🔮 Story Closing

> The Real-Time Dashboard glows on the main screen in Mission Control. A simulated asteroid detection flashes — **0.03 AU**. Within seconds, Major Nakamura's phone buzzes with the alert. He looks up at the screen, then at you.
>
> *"This is exactly what we needed. Now… Dr. Osei wants to know if we can* predict *which asteroids are dangerous before they get close."*
>
> **Next up:** Machine learning models in Fabric.

---

**Navigation:**
[← Module 06 — Power BI Reports](06-power-bi-reports.md) | [Module 08 — Data Science →](08-data-science.md)

[← Back to README](../README.md)
