# 🏗️ Module 04 — Medallion Lakehouse

> "Think of our Bronze data like raw radio signals from deep space," Dr. Osei explains during the morning standup. "Full of noise, duplicates, and mixed formats. Your job is to process them — filter the noise (Silver), then create the star maps that our scientists can actually use (Gold). That's the Medallion Architecture."

---

## 🎯 What You'll Build

In this module you'll transform raw ingested data into a production-ready **Medallion Architecture** — the industry-standard pattern for organizing data in a Lakehouse. By the end, you'll have **6 Silver tables** (cleaned) and **4 Gold tables** (aggregated), all queryable from the SQL Analytics Endpoint.

**Time estimate:** 45–60 minutes

---

## 📐 Section 1 — Understanding the Medallion Architecture

The Medallion Architecture organizes your data into three progressive layers of quality:

![Medallion Flow](../assets/diagrams/architecture.md#medallion-lakehouse-flow)

| Layer | Purpose | Characteristics | ZOSA Example |
|-------|---------|-----------------|--------------|
| 🥉 **Bronze** | Raw landing zone | Schema-on-read, append-only, exact copy of source | `asteroids_bronze` — raw JSON from NASA API |
| 🥈 **Silver** | Conformance zone | Cleaned, typed, deduplicated, validated. Schema-on-write | `asteroids_silver` — parsed dates, cast numerics, no duplicates |
| 🥇 **Gold** | Delivery zone | Business-ready aggregations and joins. Optimized for consumption | `gold_asteroid_risk` — hazard scores, risk categories |

> 💡 **Fabric advantage:** All three layers live as **Delta tables** in the same Lakehouse. No separate storage accounts, no ETL orchestration between zones — just notebooks writing to different tables.

### Why Medallion?

- **Reprocessing safety** — Bronze is your immutable source of truth. If Silver logic changes, just re-run the notebook.
- **Separation of concerns** — Data engineers own Bronze→Silver; analysts own Silver→Gold.
- **Incremental complexity** — Each layer adds value without coupling to the others.

> 📚 **Official Documentation:**
> - [Medallion Architecture](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)
> - [Lakehouse & Delta Tables](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)
> - [Delta Lake Format](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-and-delta-tables)

---

## 🗒️ Section 2 — Create Your First Notebook

Time to write your first Spark notebook. This is where the real data engineering happens.

1. Open the **ZOSA-Dev** workspace in Fabric
2. Click **+ New item** → **Notebook**
3. Name it: `01-bronze-to-silver`
4. In the notebook toolbar, click **+ Add data items** → **Existing Lakehouse** → select `lh_zosa`

> 💡 **What just happened?** You now have a PySpark notebook connected to your Lakehouse. Fabric provides a managed Spark pool — no cluster configuration needed. The `spark` session object is pre-initialized, and all Lakehouse tables are accessible via `spark.read.table("<table_name>")`.

### Notebook Environment Quick Reference

| Feature | Detail |
|---------|--------|
| **Language** | PySpark (Python + Spark) |
| **Spark pool** | Managed by Fabric — auto-starts, auto-scales |
| **Table access** | `spark.read.table("<table>")` |
| **File access** | `Files/` folder in the Lakehouse |
| **Cell execution** | `Shift+Enter` to run current cell |

> 📚 **Official Documentation:**
> - [Notebooks in Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook)
> - [Spark in Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-compute)

---

## 🥈 Section 3 — Bronze → Silver Transformations

Each Bronze table gets its own cell in the notebook. The pattern is consistent:

1. **Read** the Bronze table
2. **Deduplicate** on natural keys
3. **Cast** columns to proper types
4. **Validate** — filter out null keys and invalid values
5. **Write** as a Silver Delta table

### 3.1 — Asteroids

> ⚠️ **Note:** This code assumes `asteroids_bronze` was created by the **API notebook** (Lab 03, Section 2), which writes columns named `is_hazardous`, `relative_velocity_kph`, `estimated_diameter_min_m`, and `estimated_diameter_max_m`. If you used the **CSV sample file** instead (via pipeline), the column names differ (`is_potentially_hazardous`, `relative_velocity_kmps`, `estimated_diameter_min_km`, `estimated_diameter_max_km`). In that case, rename columns before applying the transforms below:
> ```python
> df = df.withColumnRenamed("is_potentially_hazardous", "is_hazardous") \
>        .withColumnRenamed("relative_velocity_kmps", "relative_velocity_kph") \
>        .withColumnRenamed("estimated_diameter_min_km", "estimated_diameter_min_m") \
>        .withColumnRenamed("estimated_diameter_max_km", "estimated_diameter_max_m")
> ```

```python
# Cell 1: Asteroids Bronze → Silver
from pyspark.sql.functions import col, to_date, trim

df = spark.read.table("asteroids_bronze")

silver_asteroids = (df
    .dropDuplicates(["neo_id", "close_approach_date"])
    .withColumn("close_approach_date", to_date(col("close_approach_date")))
    .withColumn("miss_distance_km", col("miss_distance_km").cast("double"))
    .withColumn("relative_velocity_kph", col("relative_velocity_kph").cast("double"))
    .withColumn("estimated_diameter_min_m", col("estimated_diameter_min_m").cast("double"))
    .withColumn("estimated_diameter_max_m", col("estimated_diameter_max_m").cast("double"))
    .withColumn("absolute_magnitude", col("absolute_magnitude").cast("double"))
    .withColumn("name", trim(col("name")))
    .filter(col("neo_id").isNotNull())
)

silver_asteroids.write.mode("overwrite").format("delta").saveAsTable("asteroids_silver")
print(f"✅ asteroids_silver: {silver_asteroids.count()} rows")
```

### 3.2 — Solar Events

```python
# Cell 2: Solar Events Bronze → Silver
from pyspark.sql.functions import col, to_timestamp, trim, upper

df = spark.read.table("solar_events_bronze")

silver_solar = (df
    .dropDuplicates(["event_id"])
    .withColumn("start_time", to_timestamp(col("start_time")))
    .withColumn("end_time", to_timestamp(col("end_time")))
    .withColumn("event_type", trim(upper(col("event_type"))))
    .withColumn("class_type", trim(col("class_type")))
    .withColumn("source_location", trim(col("source_location")))
    .withColumn("note", trim(col("note")))
    .filter(col("event_id").isNotNull())
)

silver_solar.write.mode("overwrite").format("delta").saveAsTable("solar_events_silver")
print(f"✅ solar_events_silver: {silver_solar.count()} rows")
```

### 3.3 — Exoplanets

```python
# Cell 3: Exoplanets Bronze → Silver
from pyspark.sql.functions import col, trim

df = spark.read.table("exoplanets_bronze")

silver_exoplanets = (df
    .dropDuplicates(["planet_name"])
    .withColumn("planet_name", trim(col("planet_name")))
    .withColumn("discovery_year", col("discovery_year").cast("int"))
    .withColumn("orbital_period_days", col("orbital_period_days").cast("double"))
    .withColumn("planet_radius_earth", col("planet_radius_earth").cast("double"))
    .withColumn("planet_mass_earth", col("planet_mass_earth").cast("double"))
    .withColumn("equilibrium_temp_k", col("equilibrium_temp_k").cast("double"))
    .withColumn("distance_parsecs", col("distance_parsecs").cast("double"))
    .withColumn("distance_ly", col("distance_parsecs") * 3.26156)
    .filter(col("planet_name").isNotNull())
)

silver_exoplanets.write.mode("overwrite").format("delta").saveAsTable("exoplanets_silver")
print(f"✅ exoplanets_silver: {silver_exoplanets.count()} rows")
```

### 3.4 — Missions

```python
# Cell 4: Missions Bronze → Silver
from pyspark.sql.functions import col, to_date, trim, when

df = spark.read.table("missions_bronze")

valid_statuses = ["Planned", "Active", "Completed", "Cancelled", "On Hold"]

silver_missions = (df
    .dropDuplicates(["mission_id"])
    .withColumn("mission_name", trim(col("mission_name")))
    .withColumn("launch_date", to_date(col("start_date")))
    .withColumn("end_date", to_date(col("end_date")))
    .withColumn("budget_usd", col("budget_usd").cast("double"))
    .withColumn("target_object", trim(col("target_object")))
    .withColumn("status",
        when(col("status").isin(valid_statuses), col("status"))
        .otherwise("Unknown"))
    .filter(col("mission_id").isNotNull())
    .drop("start_date")
)

silver_missions.write.mode("overwrite").format("delta").saveAsTable("missions_silver")
print(f"✅ missions_silver: {silver_missions.count()} rows")
```

### 3.5 — Crew

```python
# Cell 5: Crew Bronze → Silver
from pyspark.sql.functions import col, to_date, trim, split as spark_split

df = spark.read.table("crew_bronze")

silver_crew = (df
    .dropDuplicates(["crew_id"])
    .withColumn("full_name", trim(col("full_name")))
    .withColumn("first_name", trim(spark_split(col("full_name"), " ").getItem(0)))
    .withColumn("last_name", trim(spark_split(col("full_name"), " ").getItem(1)))
    .withColumn("role", trim(col("role")))
    .withColumn("specialty", trim(col("specialty")))
    .withColumn("hire_date", to_date(col("hire_date")))
    .withColumn("email", trim(col("email")))
    .withColumn("clearance_level", trim(col("clearance_level")))
    .filter(col("crew_id").isNotNull())
    .filter(col("email").rlike("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))
)

silver_crew.write.mode("overwrite").format("delta").saveAsTable("crew_silver")
print(f"✅ crew_silver: {silver_crew.count()} rows")
```

### 3.6 — Telemetry

```python
# Cell 6: Telemetry Bronze → Silver
from pyspark.sql.functions import col, to_timestamp, trim, when

df = spark.read.table("telemetry_bronze")

valid_statuses = ["Nominal", "Warning", "Critical", "Offline", "Maintenance", "Online"]

silver_telemetry = (df
    .dropDuplicates(["timestamp", "ground_station_id"])
    .withColumn("timestamp", to_timestamp(col("timestamp")))
    .withColumn("signal_strength_dbm", col("signal_strength_dbm").cast("double"))
    .withColumn("antenna_azimuth_deg", col("antenna_azimuth_deg").cast("double"))
    .withColumn("antenna_elevation_deg", col("antenna_elevation_deg").cast("double"))
    .withColumn("data_rate_mbps", col("data_rate_mbps").cast("double"))
    .withColumn("cpu_usage_pct", col("cpu_usage_pct").cast("double"))
    .withColumn("memory_usage_pct", col("memory_usage_pct").cast("double"))
    .withColumn("disk_io_mbps", col("disk_io_mbps").cast("double"))
    .withColumn("temperature_celsius", col("temperature_celsius").cast("double"))
    .withColumn("ground_station_id", trim(col("ground_station_id")))
    .withColumn("ground_station_name", trim(col("ground_station_name")))
    .withColumn("status",
        when(col("status").isin(valid_statuses), col("status"))
        .otherwise("Unknown"))
    .filter(col("timestamp").isNotNull())
    .filter(col("ground_station_id").isNotNull())
)

silver_telemetry.write.mode("overwrite").format("delta").saveAsTable("telemetry_silver")
print(f"✅ telemetry_silver: {silver_telemetry.count()} rows")
```

> 💡 **Tip:** Paste all six cells into the notebook first (use **+ Code** to add new cells), then click **Run all** from the ribbon. The first cell takes 30–60 seconds while the Spark session starts up; the rest execute quickly in sequence. Check the output of each cell for the ✅ success messages and row counts.

> 📚 **Learn more:** [Data Wrangler](https://learn.microsoft.com/en-us/fabric/data-science/data-wrangler) — for visual, no-code data exploration and transformation in notebooks.

### Verify Silver Tables

After all cells complete, navigate to `lh_zosa` → expand **Tables**. You should see six new Silver tables alongside your Bronze tables:

- `asteroids_silver`
- `solar_events_silver`
- `exoplanets_silver`
- `missions_silver`
- `crew_silver`
- `telemetry_silver`

Click on any Silver table to preview the data and confirm that types were cast correctly (e.g., `miss_distance_km` shows as numeric, `close_approach_date` as date).

---

## 🥇 Section 4 — Silver → Gold Aggregations

Create a new notebook: **+ New item** → **Notebook** → name it `02-silver-to-gold`. Click **+ Add data items** → **Existing Lakehouse** → select `lh_zosa`.

Gold tables are purpose-built for reporting and analytics. They answer specific business questions.

### 4.1 — gold_asteroid_risk

> 🎯 **Business question:** Which near-Earth objects pose the greatest risk, and how should we categorize them?

```python
# Cell 1: Asteroid Risk Scoring
from pyspark.sql.functions import col, when, round as spark_round

silver = spark.read.table("asteroids_silver")

gold_asteroid_risk = (silver
    .withColumn("avg_diameter_m",
        (col("estimated_diameter_min_m") + col("estimated_diameter_max_m")) / 2)
    .withColumn("hazard_score",
        spark_round(
            (1 / (col("miss_distance_km") + 1)) *
            col("relative_velocity_kph") *
            col("avg_diameter_m") * 10, 2
        ))
    .withColumn("risk_category",
        when(col("hazard_score") > 1000, "Critical")
        .when(col("hazard_score") > 100, "High")
        .when(col("hazard_score") > 10, "Medium")
        .otherwise("Low"))
    .select("neo_id", "name", "close_approach_date", "miss_distance_km",
            "relative_velocity_kph", "avg_diameter_m", "is_hazardous",
            "hazard_score", "risk_category")
    .orderBy(col("hazard_score").desc())
)

gold_asteroid_risk.write.mode("overwrite").format("delta").saveAsTable("gold_asteroid_risk")
print(f"✅ gold_asteroid_risk: {gold_asteroid_risk.count()} rows")
```

### 4.2 — gold_mission_summary

> 🎯 **Business question:** How are missions performing, and how do they relate to crew and ground stations?

```python
# Cell 2: Mission Summary (detail-level, one row per mission)
from pyspark.sql.functions import (
    col, year, datediff, round as spark_round, when
)

silver = spark.read.table("missions_silver")

gold_mission_summary = (silver
    .withColumn("launch_year", year(col("launch_date")))
    .withColumn("duration_days",
        when(col("end_date").isNotNull(),
             datediff(col("end_date"), col("launch_date")))
        .otherwise(None))
    .withColumn("budget_category",
        when(col("budget_usd") > 5000000, "High")
        .when(col("budget_usd") > 1000000, "Medium")
        .otherwise("Low"))
    .select(
        "mission_id", "mission_name", "mission_type", "status",
        "priority", "launch_date", "end_date", "launch_year",
        "duration_days", "target_object",
        "primary_ground_station_id", "budget_usd", "budget_category",
        "region"
    )
    .orderBy("launch_date")
)

gold_mission_summary.write.mode("overwrite").format("delta").saveAsTable("gold_mission_summary")
print(f"✅ gold_mission_summary: {gold_mission_summary.count()} rows")
```

### 4.3 — gold_solar_activity

> 🎯 **Business question:** What's the trend of solar activity over time, and how severe are the events?

```python
# Cell 3: Solar Activity Timeline
from pyspark.sql.functions import (
    col, date_trunc, count, avg as spark_avg,
    round as spark_round, max as spark_max,
    sum as spark_sum, when
)

silver = spark.read.table("solar_events_silver")

# Derive a severity score from the solar flare class_type (X=5, M=4, C=3, B=2, A=1)
gold_solar_activity = (silver
    .withColumn("severity",
        when(col("class_type").startswith("X"), 5)
        .when(col("class_type").startswith("M"), 4)
        .when(col("class_type").startswith("C"), 3)
        .when(col("class_type").startswith("B"), 2)
        .when(col("class_type").startswith("A"), 1)
        .otherwise(0))
    .withColumn("event_month", date_trunc("month", col("start_time")))
    .groupBy("event_month", "event_type")
    .agg(
        count("*").alias("event_count"),
        spark_round(spark_avg("severity"), 2).alias("avg_severity"),
        spark_max("severity").alias("max_severity"),
        spark_sum(when(col("severity") >= 4, 1).otherwise(0)).alias("high_severity_count"),
        spark_sum(when(col("severity") < 4, 1).otherwise(0)).alias("low_severity_count")
    )
    .orderBy("event_month", "event_type")
)

gold_solar_activity.write.mode("overwrite").format("delta").saveAsTable("gold_solar_activity")
print(f"✅ gold_solar_activity: {gold_solar_activity.count()} rows")
```

### 4.4 — gold_exoplanet_catalog

> 🎯 **Business question:** Which exoplanets are the most Earth-like, and where should ZOSA focus future observations?

```python
# Cell 4: Exoplanet Habitability Catalog
from pyspark.sql.functions import (
    col, when, abs as spark_abs, round as spark_round,
    row_number
)
from pyspark.sql.window import Window

silver = spark.read.table("exoplanets_silver")

# Simplified Earth Similarity Index (ESI)
# Based on radius, temperature, and orbital period relative to Earth
# Earth values: radius=1, temp=255K, orbital_period=365.25 days
gold_exoplanet_catalog = (silver
    .filter(col("planet_radius_earth").isNotNull())
    .filter(col("equilibrium_temp_k").isNotNull())
    .withColumn("radius_similarity",
        1 - spark_abs(col("planet_radius_earth") - 1) / col("planet_radius_earth"))
    .withColumn("temp_similarity",
        1 - spark_abs(col("equilibrium_temp_k") - 255) / col("equilibrium_temp_k"))
    .withColumn("period_similarity",
        when(col("orbital_period_days").isNotNull(),
             1 - spark_abs(col("orbital_period_days") - 365.25) / col("orbital_period_days"))
        .otherwise(0))
    .withColumn("earth_similarity_index",
        spark_round(
            (col("radius_similarity") + col("temp_similarity") + col("period_similarity")) / 3, 4
        ))
    .withColumn("habitability_zone",
        when(
            (col("equilibrium_temp_k").between(180, 310)) &
            (col("planet_radius_earth").between(0.5, 2.5)),
            "Habitable Zone"
        ).otherwise("Outside HZ"))
    .withColumn("rank",
        row_number().over(
            Window.orderBy(col("earth_similarity_index").desc())
        ))
    .select("rank", "planet_name", "host_star", "discovery_year",
            "discovery_method", "distance_ly", "planet_radius_earth",
            "planet_mass_earth", "equilibrium_temp_k", "orbital_period_days",
            "earth_similarity_index", "habitability_zone")
    .orderBy("rank")
)

gold_exoplanet_catalog.write.mode("overwrite").format("delta").saveAsTable("gold_exoplanet_catalog")
print(f"✅ gold_exoplanet_catalog: {gold_exoplanet_catalog.count()} rows")
```

### Verify Gold Tables

After all cells complete, navigate to `lh_zosa` → expand **Tables**. You should see four new Gold tables:

- `gold_asteroid_risk`
- `gold_mission_summary`
- `gold_solar_activity`
- `gold_exoplanet_catalog`

Click on `gold_asteroid_risk` and verify you see columns like `hazard_score` and `risk_category`. Check `gold_exoplanet_catalog` for the `earth_similarity_index` and `habitability_zone` columns.

---

## 🔄 Section 5 — Incremental Load Pattern

In this lab we use **full overwrite** (`mode("overwrite")`) for simplicity. In production, you'd use a **watermark-based incremental pattern** to process only new data.

### How It Works

1. Add a `_loaded_at` timestamp column when writing Silver tables
2. Track the last successful watermark (max `_loaded_at` value)
3. On subsequent runs, only process rows where the source timestamp exceeds the watermark

### Incremental Pattern Example

```python
from pyspark.sql.functions import col, current_timestamp, max as spark_max

# Read the current watermark (last load time)
try:
    watermark = (spark.read.table("asteroids_silver")
        .select(spark_max("_loaded_at")).collect()[0][0])
except:
    watermark = None  # First run — process everything

# Read only new Bronze rows
df = spark.read.table("asteroids_bronze")
if watermark:
    df = df.filter(col("_ingested_at") > watermark)

# Apply Silver transformations...
silver = (df
    .dropDuplicates(["neo_id", "close_approach_date"])
    # ... (same transformations as before)
    .withColumn("_loaded_at", current_timestamp())
)

# Append instead of overwrite
silver.write.mode("append").format("delta").saveAsTable("asteroids_silver")
```

> ⚠️ **For this lab**, stick with `mode("overwrite")`. The incremental pattern is shown here for reference — you'll use it when you operationalize your pipelines in a real project.

> 📚 **Learn more:** [Incremental Refresh & Load Patterns](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-notebook-load-data)

---

## ✅ Section 6 — Validate Your Medallion Lakehouse

Open the **SQL Analytics Endpoint** for your Lakehouse and run this validation query:

```sql
-- Medallion Layer Validation
SELECT 'Bronze' AS layer, 'asteroids' AS dataset, COUNT(*) AS rows FROM asteroids_bronze
UNION ALL SELECT 'Bronze', 'solar_events', COUNT(*) FROM solar_events_bronze
UNION ALL SELECT 'Bronze', 'exoplanets', COUNT(*) FROM exoplanets_bronze
UNION ALL SELECT 'Bronze', 'missions', COUNT(*) FROM missions_bronze
UNION ALL SELECT 'Bronze', 'crew', COUNT(*) FROM crew_bronze
UNION ALL SELECT 'Bronze', 'telemetry', COUNT(*) FROM telemetry_bronze
UNION ALL SELECT 'Silver', 'asteroids', COUNT(*) FROM asteroids_silver
UNION ALL SELECT 'Silver', 'solar_events', COUNT(*) FROM solar_events_silver
UNION ALL SELECT 'Silver', 'exoplanets', COUNT(*) FROM exoplanets_silver
UNION ALL SELECT 'Silver', 'missions', COUNT(*) FROM missions_silver
UNION ALL SELECT 'Silver', 'crew', COUNT(*) FROM crew_silver
UNION ALL SELECT 'Silver', 'telemetry', COUNT(*) FROM telemetry_silver
UNION ALL SELECT 'Gold', 'asteroid_risk', COUNT(*) FROM gold_asteroid_risk
UNION ALL SELECT 'Gold', 'mission_summary', COUNT(*) FROM gold_mission_summary
UNION ALL SELECT 'Gold', 'solar_activity', COUNT(*) FROM gold_solar_activity
UNION ALL SELECT 'Gold', 'exoplanet_catalog', COUNT(*) FROM gold_exoplanet_catalog
ORDER BY layer, dataset;
```

You should see:

- **Bronze ≥ Silver** for each dataset (Silver may have fewer rows after deduplication and filtering)
- **Gold** tables with aggregated rows (fewer rows, richer columns)
- **No empty tables** — every layer should have data

> 💡 **Pro tip:** You can also browse tables visually in the Lakehouse explorer. Click any table to preview its data and schema.

> 📚 **Learn more:** [SQL Analytics Endpoint](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint)

---

## 🏁 Checkpoint

Verify your Medallion Lakehouse is complete:

- [ ] **6 Bronze tables** exist from Module 03 (asteroids, solar_events, exoplanets, missions, crew, telemetry)
- [ ] **6 Silver tables** created — cleaned, typed, deduplicated
- [ ] **4 Gold tables** created — asteroid_risk, mission_summary, solar_activity, exoplanet_catalog
- [ ] Both notebooks (`01-bronze-to-silver`, `02-silver-to-gold`) run without errors
- [ ] Gold tables contain meaningful aggregations (hazard scores, summary stats, rankings)
- [ ] You can query all layers from the SQL Analytics Endpoint

> Dr. Osei pulls up the `gold_asteroid_risk` table on the main screen. "Look at this — every near-Earth object ranked by hazard score, clean and queryable. *This* is what the science directors have been waiting for." She turns to you. "Now they want dashboards. Time to build the models."

---

**Navigation:**
[← Module 03 — Data Ingestion](03-data-ingestion.md) | [Module 05 — Semantic Model →](05-semantic-model.md)

[← Back to README](../README.md)
