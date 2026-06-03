# Module 03 — Data Ingestion

> First data drop — NASA feeds, internal databases, and OneLake

> *Your inbox pings at 6 AM: "Data transfer approved — NASA feed credentials attached. Also, IT says the old missions database export is ready. You have 6 datasets hitting your desk today. Time to build the ingestion layer." — Dr. Vasquez*

---

## 🏗️ Section 1: Create the Lakehouse

Your first job is standing up the central storage layer — a **Lakehouse** in your development workspace.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New item** → **Lakehouse**.
3. Name it `lh_zosa` and click **Create**.

You now have a Lakehouse with two areas:

- **Files** — for unstructured or raw file uploads (CSVs, Parquet, images, anything).
- **Tables** — for managed **Delta Lake** tables that you can query with SQL and Spark.

**💡 Tip:** Notice that Fabric automatically created a **SQL Analytics Endpoint** alongside your Lakehouse. This is a read-only SQL interface that lets you query your Delta tables using T-SQL — no Spark cluster required. You'll use it at the end of this module to verify your ingestion.

> 📚 **Official Documentation:**
> - [Lakehouse Overview](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)
> - [Create a Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/create-lakehouse)

---

## 🌐 Section 2: Ingest Data from a Public API

In real-world scenarios, data doesn't arrive as CSV files on your desktop — it comes from **REST APIs, databases, and streaming sources**. Let's ingest asteroid data directly from NASA's Near-Earth Object (NeoWs) API **inside Fabric**, no local tools required.

You'll follow a two-step approach that mirrors how production teams work:

1. **Develop** the ingestion logic in a Notebook (flexible, debuggable)
2. **Productionize** by wrapping it in a Data Pipeline (scheduling, retries, monitoring)

---

### Step 1: Create the Ingestion Notebook

This is your development environment. You write PySpark code that calls the API, parses JSON, and writes directly to a Delta table.

1. Navigate to **ZOSA-Dev** workspace.
2. Click **+ New item** → **Notebook**.
3. Name it `nb_api_ingestion`.
4. Attach the notebook to your lakehouse: in the left panel, click **+ Add data items** → select **Existing Lakehouse** → choose `lh_zosa`. You should see **Tables** and **Files** folders appear under `lh_zosa`.

   > ⚠️ **Common mistake:** Make sure you add a **Lakehouse**, not a Warehouse. A Lakehouse shows **Tables** and **Files** folders. A Warehouse shows **Schemas** and **Security** folders — if you see those, remove it and add the Lakehouse instead.
5. Paste this code into a cell and run it:

```python
import requests
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType, DateType

# NASA NeoWs API — Near-Earth Objects for the past 7 days
API_KEY = "YOUR_NASA_API_KEY"  # Replace with your key from api.nasa.gov
url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date=2024-01-01&end_date=2024-01-07&api_key={API_KEY}"

response = requests.get(url)
data = response.json()

# Flatten the nested JSON into rows
rows = []
for date, neos in data["near_earth_objects"].items():
    for neo in neos:
        rows.append(Row(
            neo_id=neo["id"],
            name=neo["name"],
            absolute_magnitude=float(neo.get("absolute_magnitude_h", 0)),
            is_hazardous=neo["is_potentially_hazardous_asteroid"],
            close_approach_date=date,
            miss_distance_km=float(neo["close_approach_data"][0]["miss_distance"]["kilometers"]),
            relative_velocity_kph=float(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"]),
            estimated_diameter_min_m=float(neo["estimated_diameter"]["meters"]["estimated_diameter_min"]),
            estimated_diameter_max_m=float(neo["estimated_diameter"]["meters"]["estimated_diameter_max"])
        ))

# Create DataFrame and write as Delta table
df = spark.createDataFrame(rows)
df.write.mode("overwrite").format("delta").saveAsTable("asteroids_bronze")

print(f"✅ Loaded {df.count()} asteroid records into asteroids_bronze")
```

6. Run the cell — you should see the success message with the row count.

**What just happened?** You called a live REST API from a Fabric notebook, transformed nested JSON into a flat structure using PySpark, and persisted it directly as a Delta table. No CSV files, no local downloads, no uploads.

---

### Step 2: Wrap in a Data Pipeline (Production Orchestration)

Your notebook works — but in production you can't rely on someone clicking "Run" every morning. You need **scheduling, automatic retries, failure alerts, and run history**. That's what a Data Pipeline provides.

The pipeline doesn't duplicate the notebook's logic. It simply **calls** the notebook on a schedule and adds operational guardrails around it.

1. Navigate to **ZOSA-Dev** workspace.
2. Click **+ New item** → **Data Pipeline**.
3. Name it `pl_api_asteroid_ingestion` and click **Create**.
4. On the landing page, click **Pipeline activity** (under "Start with a blank canvas"). An activity picker appears — type `Notebook` in the **Search** box and select **Notebook** to add it to the canvas.
5. In the **General** tab, configure:
   - **Name:** `Ingest Asteroids from NASA`
6. In the **Settings** tab, configure:
   - **Connection:** *(leave as default or select your workspace connection)*
   - **Workspace:** `ZOSA-Dev`
   - **Notebook:** select `nb_api_ingestion` from the dropdown
   - **Base parameters:** *(leave empty for now — the API key is hardcoded in the notebook)*
   - **Advanced settings:** *(leave defaults)*
7. Click **Run** (▷) in the toolbar to execute the pipeline. Monitor the **Output** tab at the bottom — the Notebook activity should complete with a green checkmark. It may take 1–2 minutes as it starts a Spark session.
8. Once the pipeline succeeds, navigate to `lh_zosa` → **Tables** and verify that `asteroids_bronze` has been refreshed with data.

**What you gained:** The pipeline wraps your notebook with production capabilities:

| Capability | How to enable |
|-----------|---------------|
| **Run daily at 6 AM** | Click **Schedule** in the toolbar → set a recurrence trigger |
| **Retry on failure** | Select the Notebook activity → **General** tab → set Retry count to 3 |
| **Email on failure** | Click **Trigger** → **Add trigger** → configure alerts |
| **Run history** | Click **View run history** to see all past executions |
| **Parameterize dates** | Add pipeline parameters and pass them to the notebook via Base parameters |

**💡 Tip:** To parameterize the date range, add `start_date` and `end_date` pipeline parameters, pass them to the notebook via **Base parameters**, and read them in the notebook with `notebookutils.notebook.get_arg("start_date")`. This lets you backfill historical data or schedule incremental daily pulls.

---

### 💡 When to use Web Activity in pipelines

The **Web Activity** is useful in pipelines when you need to:
- Check an API health endpoint before proceeding (with an **If Condition** activity)
- Fetch a short-lived auth token for downstream activities
- Trigger an external webhook or notify another system
- Call a simple REST endpoint where the response drives pipeline control flow

It's **not** the right tool for ingesting large API responses into a lakehouse — that's what notebooks excel at.

> 📚 **Official Documentation:**
> - [Notebooks in Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook)
> - [Data Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-pipeline-with-sample-data)
> - [Web Activity in Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/web-activity)

---

## 📂 Section 3: Upload Remaining Data (Internal Sources)

The asteroids came from a live API, but ZOSA's remaining datasets come from **internal database exports** — the IT team delivered them as CSVs. This is common in enterprises: some data is API-driven, some arrives as file drops.

1. Open `lh_zosa` and click **Files** in the left Explorer panel.
2. Click **Get data** → **Upload files**.
3. Browse to the `data/sample/` folder from your cloned repository and select all CSV files to upload:
   - `crew.csv` — astronaut roster
   - `missions.csv` — mission manifest
   - `telemetry.csv` — spacecraft sensor readings
   - `solar_events.csv` — geomagnetic storm events
   - `exoplanets.csv` — confirmed exoplanet catalog

   > ℹ️ You'll also see `asteroids.csv` in the folder — you can skip it since we already ingested asteroids from the live API in Section 2. Uploading it won't cause problems; it just won't be used.

4. Once the upload finishes, expand the **Files** section — you should see your five CSV files listed.

These are **raw CSVs** sitting in the Files area. They are *not* yet queryable as tables — think of this as your staging area.

---

## 🔄 Section 4: Dataflows Gen2 — Low-Code Ingestion

Let's start with a **low-code** approach. You'll use **Dataflows Gen2** to ingest `crew.csv` with some light transformations — promoting headers, fixing data types, and filtering bad rows.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New item** → **Dataflow Gen2**.
3. Name it `df_crew_ingestion` by clicking on the default name at the top-left of the editor.
4. Click **Get Data** → **Text/CSV**.
5. Browse to the uploaded `crew.csv` file in your Lakehouse's Files section via the **OneLake** connector and click **Next**.
6. On the **Preview file data** screen, verify the settings:
   - **File origin:** 65001: Unicode (UTF-8)
   - **Delimiter:** Comma
   - **Data type detection:** Based on first 200 rows
   - Confirm the preview table shows your columns (`crew_id`, `full_name`, `role`, etc.) with headers correctly detected. Click **Create**.
7. In the **Power Query** editor, apply these transforms:
   - Click **Use first row as headers** (on the Home ribbon) to promote the header row.
   - Select the `hire_date` column → change its data type to **Date**.
   - Verify other columns have correct types (text for names, integer for IDs).
   > 💡 **Note:** If the **Applied steps** panel already shows "Promoted headers" and "Changed column types", Fabric auto-applied these from the preview screen — you can skip the steps above and just verify the results look correct.
   - Click the dropdown on `crew_id` → **Remove empty** to filter out any rows with null crew IDs.
   - In the **Query Settings** panel on the right, rename the query to `crew_ingestion`.
8. Set the data destination:
   - At the bottom-right of the editor, click the `+` next to **Data destination** → select **Lakehouse**.
   - On the **Connect to data destination** screen, leave the connection as "Lakehouse admin (none)" with Organizational account authentication → click **Next**.
   - On the **Choose destination target** screen, keep **New table** selected.
   - Change the **Table name** to `crew_bronze`.
   - In the left panel, scroll (or use the Search box) to find the **ZOSA-Dev** workspace → expand it → select `lh_zosa`.
   - Click **Next** to confirm.
   - On the **Choose destination settings** screen, verify the column mapping looks correct (all columns mapped 1:1, `hire_date` as Date). Leave **Use automatic settings** toggled on and click **Save settings**.
9. Click **Save & run** (top-left in the Home ribbon) to publish the dataflow and trigger a refresh.
10. Verify the run completed successfully:
    - In the Power Query editor, click **Recent runs** (top ribbon) to check the status — it should show **Succeeded** within a minute or two.
    - Navigate back to the **ZOSA-Dev** workspace → open `lh_zosa` → expand **Tables**. You should see a new `crew_bronze` table with 9 columns and your crew data loaded.

**What just happened?** Dataflows Gen2 is a **Power Query-based**, low-code ingestion tool. It supports **150+ connectors**, runs on managed Spark under the hood, and is ideal for business users and simple transforms. Think of it as the approachable on-ramp to data ingestion in Fabric.

> 📚 **Official Documentation:**
> - [Dataflows Gen2](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-dataflow-gen2)
> - [Power Query in Dataflows](https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview)

---

## 🔧 Section 5: Data Pipeline — Orchestrated Ingestion

One table down, four to go. Instead of creating more dataflows, you'll build a **Data Pipeline** that ingests the remaining CSVs in parallel.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New item** → **Data Pipeline**.
3. Name it `pl_ingest_all_sources` and click **Create**.
4. On the pipeline landing page ("Build a pipeline to organize and move your data"), click the **Pipeline activity** card under "Start with a blank canvas." A popup appears with an activity list — select **Copy data** (under "Move and transform") to add your first Copy Data activity to the canvas.

   > 💡 **Alternative approach:** You could create 4 separate Copy Data activities (one per file) on the canvas — that works fine for a small number of files. However, we'll use a **metadata-driven approach** with a ForEach loop, which is more scalable and realistic for production pipelines.

5. Delete the Copy Data activity you just added (we'll place it inside a ForEach instead). First, set up a pipeline parameter with the file list:
   - Click on the pipeline **canvas background** (deselect any activity) → in the bottom panel, click the **Parameters** tab → **+ New**.
   - Name: `files`, Type: **Array**, Default value:
     ```json
     [
       {"source": "missions.csv", "destination": "missions_bronze"},
       {"source": "telemetry.csv", "destination": "telemetry_bronze"},
       {"source": "solar_events.csv", "destination": "solar_events_bronze"},
       {"source": "exoplanets.csv", "destination": "exoplanets_bronze"}
     ]
     ```
6. Add a **ForEach** activity:
   - From the **Activities** tab in the ribbon → under "Control flow" → select **ForEach** and add it to the canvas.
   - **General** tab: Rename it to `ForEach_Ingest_CSVs`.
   - **Settings** tab:
     - Check **Sequential** if you want one-at-a-time execution, or leave it **unchecked** for parallel execution (recommended — all 4 run simultaneously).
     - **Items**: Click the text field → select **Pipeline expression** (or click "Add dynamic content") → enter: `@pipeline().parameters.files`
7. Add a **Copy Data** activity **inside** the ForEach:
   - Double-click the ForEach activity (or click the ✏️ pencil icon) to open its inner canvas.
   - Add a **Copy data** activity from the Activities ribbon.
   - **Source** tab:
     - **Connection**: Lakehouse admin (Preview)
     - **Lakehouse**: `lh_zosa`
     - **Root folder**: Select **Files**
     - **File path**: Leave Directory empty. For File name, click the text field → **Add dynamic content** → enter: `@item().source`
     - **File format**: Change from Binary to **DelimitedText** → click **Settings** and verify **First row as header** is checked.
   - **Destination** tab:
     - **Connection**: Lakehouse admin (Preview)
     - **Lakehouse**: `lh_zosa`
     - **Root folder**: Select **Tables**
     - Check **Enter manually** → in the Table name field, click → **Add dynamic content** → enter: `@item().destination`
     - **Table action**: Select **Overwrite**.

   > 💡 **Table action options:**
   > - **Append** — adds rows to the existing table (use for incremental loads)
   > - **Overwrite** — replaces the entire table on each run (use for full refreshes)
   > - **Upsert** — inserts new rows and updates existing ones by matching a key column (use for change-data-capture scenarios)

8. Navigate back to the main pipeline canvas (click the pipeline name in the breadcrumb at the top).
9. Click **Run** (▷) to execute the pipeline.
10. Monitor the **Output** tab at the bottom — you should see the ForEach activity running and completing all four copies within a few minutes. Click on the ForEach run to see individual activity statuses.
11. **Verify the results:** Navigate to `lh_zosa` → expand **Tables**. You should now see all four new tables:
    - `missions_bronze`
    - `telemetry_bronze`
    - `solar_events_bronze`
    - `exoplanets_bronze`
    
    Click on any table to preview its data and confirm rows were loaded successfully.

**What just happened?** Data Pipelines are Fabric's **orchestration engine**. The **Copy Activity** handles data movement, but pipelines can also trigger Notebooks, Dataflows, Stored Procedures, and more. Think of them as the conductor — they don't transform data themselves, but they make sure everything runs in the right order.

> 📚 **Official Documentation:**
> - [Data Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-pipeline-with-sample-data)
> - [Copy Activity](https://learn.microsoft.com/en-us/fabric/data-factory/copy-data-activity)

---

## 🔗 Section 6: OneLake Shortcuts (Optional Advanced)

If you have an **Azure subscription**, you can experience one of Fabric's most powerful features: **shortcuts** — zero-copy references to external data.

1. In the Azure portal, create an **Azure Data Lake Storage Gen2** storage account (or use an existing one).
2. Create a container (e.g., `zosa-external`) and upload one dataset — say, `exoplanets.csv` — into it.
3. Back in Fabric, open `lh_zosa`.
4. In the Explorer panel, right-click **Tables** (or **Files**) and select **New shortcut**.
5. Choose **Azure Data Lake Storage Gen2**.
6. Provide the **storage account URL** (e.g., `https://<account>.dfs.core.windows.net`) and authenticate with your Azure credentials.
7. Browse to the container and select the folder or file.
8. Click **Create**. The data now appears as a table in your Lakehouse — **zero copy**.

**Why this matters:** Shortcuts reference external data without duplicating it. The data stays in its original location but becomes queryable through OneLake, just like any native table. This is perfect for **cross-domain data sharing**, **multi-cloud scenarios**, and keeping storage costs down.

**⚠️ Note:** Shortcuts are **read-only** references. You can query the data but you cannot modify the source through a shortcut. Any writes need to happen at the original storage location.

> 📚 **Learn more:** [OneLake Shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)

---

## ✅ Section 7: Verify Your Ingestion

Time to confirm everything landed correctly.

1. Open `lh_zosa` → expand the **Tables** section in the Explorer panel.
2. You should see **six tables**:
   - `asteroids_bronze`
   - `solar_events_bronze`
   - `exoplanets_bronze`
   - `missions_bronze`
   - `crew_bronze`
   - `telemetry_bronze`
3. Click on any table → **Preview data** to eyeball the rows and verify column names look correct.
4. Now switch to the **SQL Analytics Endpoint** (click the dropdown next to the Lakehouse name at the top and select it).
5. Open a **New SQL query** and run:

```sql
SELECT COUNT(*) AS row_count, 'asteroids' AS dataset FROM asteroids_bronze
UNION ALL
SELECT COUNT(*), 'solar_events' FROM solar_events_bronze
UNION ALL
SELECT COUNT(*), 'exoplanets' FROM exoplanets_bronze
UNION ALL
SELECT COUNT(*), 'missions' FROM missions_bronze
UNION ALL
SELECT COUNT(*), 'crew' FROM crew_bronze
UNION ALL
SELECT COUNT(*), 'telemetry' FROM telemetry_bronze;
```

You should see a result set with six rows — one per dataset — each showing a non-zero row count. If any table shows zero rows, go back and check the corresponding Copy Data activity in your pipeline.

---

## ✅ Checkpoint

Verify that you've completed the following before moving on:

- [ ] Lakehouse `lh_zosa` created in ZOSA-Dev workspace
- [ ] 6 Bronze-layer tables loaded with data (`asteroids_bronze`, `solar_events_bronze`, `exoplanets_bronze`, `missions_bronze`, `crew_bronze`, `telemetry_bronze`)
- [ ] You can query all tables via the SQL Analytics Endpoint
- [ ] You understand the difference between **Dataflows Gen2** (low-code, Power Query-based) and **Data Pipelines** (orchestration engine with Copy Activity)

---

> *You send Dr. Vasquez a screenshot of the SQL query results — six datasets, all loaded. She replies within seconds: "Impressive. Raw data is in. But raw data is like unprocessed telescope images — noisy and hard to read. Tomorrow, we refine it. The science team is waiting."*

---

**Navigation:**
[← Module 02 — Governance & Security](02-governance-and-security.md) | [Module 04 — Medallion Lakehouse →](04-medallion-lakehouse.md)

[← Back to README](../README.md)
