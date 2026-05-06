# Module 03 — Data Ingestion

> First data drop — NASA feeds, internal databases, and OneLake

> *Your inbox pings at 6 AM: "Data transfer approved — NASA feed credentials attached. Also, IT says the old missions database export is ready. You have 6 datasets hitting your desk today. Time to build the ingestion layer." — Dr. Vasquez*

---

## 🏗️ Section 1: Create the Lakehouse

Your first job is standing up the central storage layer — a **Lakehouse** in your development workspace.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New** → **Lakehouse**.
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

You have two approaches: a **Notebook** (code-first) or a **Data Pipeline** (low-code). Both achieve the same result — a `asteroids_bronze` table in your lakehouse.

---

### Option A: Notebook — Code-First API Ingestion

This is the most flexible approach. You write PySpark code that calls the API, parses JSON, and writes directly to a Delta table.

1. Navigate to **ZOSA-Dev** workspace.
2. Click **+ New** → **Notebook**.
3. Name it `nb_api_ingestion`.
4. In the first cell, attach the notebook to your lakehouse: click **Add lakehouse** in the left Explorer → select `lh_zosa`.
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
df.write.mode("overwrite").format("delta").saveAsTable("lh_zosa.asteroids_bronze")

print(f"✅ Loaded {df.count()} asteroid records into asteroids_bronze")
```

6. Run the cell — you should see the success message with the row count.

**What just happened?** You called a live REST API from a Fabric notebook, transformed nested JSON into a flat structure using PySpark, and persisted it directly as a Delta table. No CSV files, no local downloads, no uploads.

---

### Option B: Data Pipeline — Low-Code API Ingestion

If you prefer a **no-code approach**, you can use a Data Pipeline with a **Web Activity** to call the API and a **Notebook Activity** to transform and load the response.

1. Navigate to **ZOSA-Dev** workspace.
2. Click **+ New** → **Data Pipeline**.
3. Name it `pl_api_asteroid_ingestion` and click **Create**.
4. On the landing page, click **Pipeline activity** (under "Start with a blank canvas"). An activity picker appears — type `Web` in the **Search** box and select **Web** to add it to the canvas.
5. In the **General** tab of the Web activity, configure:
   - **Name:** `Get NASA NEO Data`
   - **Description:** `Fetches near-Earth objects from NASA NeoWs API for the specified date range`
6. In the **Settings** tab, configure the connection:
   - **Connection:** Select **Create new connection** from the dropdown. The **"Connect data source"** wizard opens (labeled **Web v2**):
     - **Base Url:** `https://api.nasa.gov`
     - **Token Audience Uri:** *(leave empty)*
     - **Connection name:** auto-fills as `https://api.nasa.gov` (you can rename it, e.g., `NASA API`)
     - **Data gateway:** `(none)`
     - **Authentication kind:** **Anonymous**
     - **Privacy Level:** `None`
     - Click **Connect**
   - Back on the Settings tab, configure:
     - **Relative URL:** `/neo/rest/v1/feed?start_date=2024-01-01&end_date=2024-01-07&api_key=YOUR_NASA_API_KEY`
     - **Method:** `GET`
     - **Headers:** *(leave empty)*
7. From the **Activities** ribbon, add a **Set Variable** activity. Connect it to the Web activity using the **On success** connector (green arrow):
   - **General** tab — Name: `Store API Response`
   - **Settings** tab:
     - **Variable type:** select **Pipeline variable**
     - **Name:** click **+ New** to create a variable called `api_response` (type: String)
     - **Value:** `@string(activity('Get NASA NEO Data').output)`

   > ⚠️ **Note:** The Web activity output **is** the parsed response body directly (there is no `.Response` sub-property). The output payload is limited to **4 MB**, so this pattern works well for small API responses like the NeoWs weekly feed.

8. From the **Activities** ribbon, add a **Notebook** activity. Connect it to the Set Variable activity using the **On success** connector:
   - **General** tab — Name: `Transform and Load Asteroids`
   - **Settings** tab:
     - **Connection:** *(leave as default or select your workspace connection)*
     - **Workspace:** `ZOSA-Dev`
     - **Notebook:** select `nb_api_ingestion` from the dropdown (the notebook from Option A)
     - **Base parameters / Advanced settings:** *(leave defaults for now)*
   - This pattern is common: the pipeline **orchestrates** (handles scheduling, retries, alerts) while the notebook **transforms**.

**💡 Tip:** In production, you'd parameterize the date range and schedule the pipeline to run daily — pulling only the latest NEO data each time. The notebook handles the JSON parsing; the pipeline handles the "when" and "what if it fails."

---

### Which approach should you use?

| Factor | Notebook | Data Pipeline |
|--------|----------|---------------|
| **Flexibility** | Full Python/PySpark — any API shape | Limited to built-in activities |
| **Scheduling** | Needs pipeline wrapper or manual trigger | Built-in scheduler with retries |
| **Error handling** | Try/except in code | Visual retry policies, alerts |
| **Best for** | Complex transformations, nested JSON | Simple REST → table patterns |
| **ZOSA recommendation** | ✅ Use for initial development | ✅ Use for production orchestration |

**Best practice:** Develop in a notebook, then wrap it in a pipeline for production scheduling.

> 📚 **Official Documentation:**
> - [Notebooks in Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook)
> - [REST API ingestion with Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/connector-rest-overview)
> - [Web Activity in Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/web-activity)

---

## 📂 Section 3: Upload Remaining Data (Internal Sources)

The asteroids came from a live API, but ZOSA's remaining datasets come from **internal database exports** — the IT team delivered them as CSVs. This is common in enterprises: some data is API-driven, some arrives as file drops.

1. Open `lh_zosa` and click **Files** in the left Explorer panel.
2. Click **Upload** → **Upload folder**.
3. Browse to the `data/sample/` folder from your cloned repository and upload its contents (crew, missions, telemetry, solar events, exoplanets CSVs).
4. Once the upload finishes, expand the **Files** section — you should see your CSV files listed.

These are **raw CSVs** sitting in the Files area. They are *not* yet queryable as tables — think of this as your staging area.

**💡 Tip:** If you also want to pull solar events and exoplanets from NASA APIs (DONKI and Exoplanet Archive), you can extend the notebook from Section 2 with additional cells. The sample CSVs are a shortcut for the remaining datasets.

---

## 🔄 Section 4: Dataflows Gen2 — Low-Code Ingestion

Let's start with a **low-code** approach. You'll use **Dataflows Gen2** to ingest `crew.csv` with some light transformations — promoting headers, fixing data types, and filtering bad rows.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New** → **Dataflow Gen2**.
3. In the Dataflow editor, click **Get Data** → **Text/CSV**.
4. Browse to the uploaded `crew.csv` file in your Lakehouse's Files section via the **OneLake** connector and click **Next**.
5. In the **Power Query** editor, apply these transforms:
   - Click **Use first row as headers** (on the Home ribbon) to promote the header row.
   - Select the `hire_date` column → change its data type to **Date**.
   - Verify other columns have correct types (text for names, integer for IDs).
   - Click the dropdown on `crew_id` → **Remove empty** to filter out any rows with null crew IDs.
   - In the **Query Settings** panel on the right, rename the query to `crew_ingestion`.
6. Click **Add data destination** → **Lakehouse** at the bottom of the editor.
7. Select `lh_zosa` → **Tables** → enter the table name `crew_bronze`.
8. Click **Publish**.
9. The dataflow will begin refreshing. Monitor the status in the workspace — it should show **Succeeded** within a minute or two.

**What just happened?** Dataflows Gen2 is a **Power Query-based**, low-code ingestion tool. It supports **150+ connectors**, runs on managed Spark under the hood, and is ideal for business users and simple transforms. Think of it as the approachable on-ramp to data ingestion in Fabric.

> 📚 **Official Documentation:**
> - [Dataflows Gen2](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-dataflow-gen2)
> - [Power Query in Dataflows](https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview)

---

## 🔧 Section 5: Data Pipeline — Orchestrated Ingestion

One table down, five to go. Instead of creating five more dataflows, you'll build a **Data Pipeline** that ingests the remaining CSVs in parallel.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New** → **Data Pipeline**.
3. Name it `pl_ingest_all_sources` and click **Create**.
4. For each of your remaining CSV files (`solar_events.csv`, `exoplanets.csv`, `missions.csv`, `crew.csv`, `telemetry.csv`), add a **Copy Data** activity:
   - Drag a **Copy Data** activity onto the canvas.
   - **Source** tab: set the source to your **Lakehouse Files** (browse to the specific CSV).
   - **Destination** tab: set the destination to your **Lakehouse Tables**, with a table name following the pattern `<dataset>_bronze` (e.g., `asteroids_bronze`).
   - Under **Mapping**, verify column mappings and set the file format to **DelimitedText** (CSV) with header row enabled.
5. Since none of these activities depend on each other, **wire them in parallel**: connect the pipeline's **Start** node to all five Copy Data activities directly.
6. Add a **pipeline parameter** for reusability:
   - Click on the pipeline canvas background → **Parameters** tab → **+ New**.
   - Name: `source_folder`, Type: **String**, Default value: `sample`.
   - Update each Copy Data activity's source path to reference `@pipeline().parameters.source_folder` so you can point the pipeline at different folders later.
7. Click **Run** (▷) to execute the pipeline.
8. Monitor the **Output** tab at the bottom — you should see all five activities running simultaneously and completing within a few minutes.

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
