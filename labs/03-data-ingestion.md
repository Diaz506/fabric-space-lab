# Module 03 — Data Ingestion

> First data drop — NASA feeds, internal databases, and OneLake

> *Your inbox pings at 6 AM: "Data transfer approved — NASA feed credentials attached. Also, IT says the old missions database export is ready. You have 6 datasets hitting your desk today. Time to build the ingestion layer." — Dr. Vasquez*

---

## 🏗️ Section 1: Create the Lakehouse

Your first job is standing up the central storage layer — a **Lakehouse** in your development workspace.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New** → **Lakehouse**.
3. Name it `zosa_lakehouse` and click **Create**.

You now have a Lakehouse with two areas:

- **Files** — for unstructured or raw file uploads (CSVs, Parquet, images, anything).
- **Tables** — for managed **Delta Lake** tables that you can query with SQL and Spark.

**💡 Tip:** Notice that Fabric automatically created a **SQL Analytics Endpoint** alongside your Lakehouse. This is a read-only SQL interface that lets you query your Delta tables using T-SQL — no Spark cluster required. You'll use it at the end of this module to verify your ingestion.

> 📚 **Official Documentation:**
> - [Lakehouse Overview](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)
> - [Create a Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/create-lakehouse)

---

## 📂 Section 2: Upload Sample Data (Quick Path)

If you're using the pre-generated sample data from the cloned repo, this is the fastest way to get files into your Lakehouse.

1. Open `zosa_lakehouse` and click **Files** in the left Explorer panel.
2. Click **Upload** → **Upload folder**.
3. Browse to the `data/sample/` folder from your cloned repository and upload its contents.
4. Once the upload finishes, expand the **Files** section — you should see your CSV files listed.

These are **raw CSVs** sitting in the Files area. They are *not* yet queryable as tables — think of this as your staging area.

**💡 Tip:** If you want to pull live data from NASA APIs instead, run `python data/fetch_nasa_apis.py --api-key YOUR_KEY` locally first, then upload those generated CSVs alongside (or instead of) the sample files.

---

## 🔄 Section 3: Dataflows Gen2 — Low-Code Ingestion

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
7. Select `zosa_lakehouse` → **Tables** → enter the table name `crew_bronze`.
8. Click **Publish**.
9. The dataflow will begin refreshing. Monitor the status in the workspace — it should show **Succeeded** within a minute or two.

**What just happened?** Dataflows Gen2 is a **Power Query-based**, low-code ingestion tool. It supports **150+ connectors**, runs on managed Spark under the hood, and is ideal for business users and simple transforms. Think of it as the approachable on-ramp to data ingestion in Fabric.

> 📚 **Official Documentation:**
> - [Dataflows Gen2](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-dataflow-gen2)
> - [Power Query in Dataflows](https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview)

---

## 🔧 Section 4: Data Pipeline — Orchestrated Ingestion

One table down, five to go. Instead of creating five more dataflows, you'll build a **Data Pipeline** that ingests all six CSVs in parallel.

1. Navigate to the **ZOSA-Dev** workspace.
2. Click **+ New** → **Data Pipeline**.
3. Name it `ingest_all_sources` and click **Create**.
4. For each of your six CSV files (`asteroids.csv`, `solar_events.csv`, `exoplanets.csv`, `missions.csv`, `crew.csv`, `telemetry.csv`), add a **Copy Data** activity:
   - Drag a **Copy Data** activity onto the canvas.
   - **Source** tab: set the source to your **Lakehouse Files** (browse to the specific CSV).
   - **Destination** tab: set the destination to your **Lakehouse Tables**, with a table name following the pattern `<dataset>_bronze` (e.g., `asteroids_bronze`).
   - Under **Mapping**, verify column mappings and set the file format to **DelimitedText** (CSV) with header row enabled.
5. Since none of these activities depend on each other, **wire them in parallel**: connect the pipeline's **Start** node to all six Copy Data activities directly.
6. Add a **pipeline parameter** for reusability:
   - Click on the pipeline canvas background → **Parameters** tab → **+ New**.
   - Name: `source_folder`, Type: **String**, Default value: `sample`.
   - Update each Copy Data activity's source path to reference `@pipeline().parameters.source_folder` so you can point the pipeline at different folders later.
7. Click **Run** (▷) to execute the pipeline.
8. Monitor the **Output** tab at the bottom — you should see all six activities running simultaneously and completing within a few minutes.

**What just happened?** Data Pipelines are Fabric's **orchestration engine**. The **Copy Activity** handles data movement, but pipelines can also trigger Notebooks, Dataflows, Stored Procedures, and more. Think of them as the conductor — they don't transform data themselves, but they make sure everything runs in the right order.

> 📚 **Official Documentation:**
> - [Data Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/create-first-pipeline-with-sample-data)
> - [Copy Activity](https://learn.microsoft.com/en-us/fabric/data-factory/copy-data-activity)

---

## 🔗 Section 5: OneLake Shortcuts (Optional Advanced)

If you have an **Azure subscription**, you can experience one of Fabric's most powerful features: **shortcuts** — zero-copy references to external data.

1. In the Azure portal, create an **Azure Data Lake Storage Gen2** storage account (or use an existing one).
2. Create a container (e.g., `zosa-external`) and upload one dataset — say, `exoplanets.csv` — into it.
3. Back in Fabric, open `zosa_lakehouse`.
4. In the Explorer panel, right-click **Tables** (or **Files**) and select **New shortcut**.
5. Choose **Azure Data Lake Storage Gen2**.
6. Provide the **storage account URL** (e.g., `https://<account>.dfs.core.windows.net`) and authenticate with your Azure credentials.
7. Browse to the container and select the folder or file.
8. Click **Create**. The data now appears as a table in your Lakehouse — **zero copy**.

**Why this matters:** Shortcuts reference external data without duplicating it. The data stays in its original location but becomes queryable through OneLake, just like any native table. This is perfect for **cross-domain data sharing**, **multi-cloud scenarios**, and keeping storage costs down.

**⚠️ Note:** Shortcuts are **read-only** references. You can query the data but you cannot modify the source through a shortcut. Any writes need to happen at the original storage location.

> 📚 **Learn more:** [OneLake Shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)

---

## ✅ Section 6: Verify Your Ingestion

Time to confirm everything landed correctly.

1. Open `zosa_lakehouse` → expand the **Tables** section in the Explorer panel.
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

- [ ] Lakehouse `zosa_lakehouse` created in ZOSA-Dev workspace
- [ ] 6 Bronze-layer tables loaded with data (`asteroids_bronze`, `solar_events_bronze`, `exoplanets_bronze`, `missions_bronze`, `crew_bronze`, `telemetry_bronze`)
- [ ] You can query all tables via the SQL Analytics Endpoint
- [ ] You understand the difference between **Dataflows Gen2** (low-code, Power Query-based) and **Data Pipelines** (orchestration engine with Copy Activity)

---

> *You send Dr. Vasquez a screenshot of the SQL query results — six datasets, all loaded. She replies within seconds: "Impressive. Raw data is in. But raw data is like unprocessed telescope images — noisy and hard to read. Tomorrow, we refine it. The science team is waiting."*

---

**Navigation:**
[← Module 02 — Governance & Security](02-governance-and-security.md) | [Module 04 — Medallion Lakehouse →](04-medallion-lakehouse.md)

[← Back to README](../README.md)
