# Module 05 — Semantic Model (Direct Lake)

> **Story time 🛰️:** The science directors burst into the data-engineering bullpen at 08:00 sharp.
> *"We need dashboards — yesterday."* You lean back in your chair and smile.
> *"Direct Lake gives us blazing-fast queries without importing a single byte of data."*
> The directors exchange puzzled glances. Time to show them what Fabric can really do.

---

## 🔍 1 — What Is Direct Lake?

Direct Lake is Microsoft Fabric's **third query mode** — and it combines the best parts of Import and DirectQuery while dodging their biggest trade-offs.

| Capability | Import | DirectQuery | **Direct Lake** |
|---|---|---|---|
| Query speed | ⚡ Fast (in-memory) | 🐢 Depends on source | ⚡ Fast (columnar read from Delta) |
| Data freshness | ⏰ Stale until refresh | ✅ Real-time | ✅ Near-real-time (auto-sync) |
| Data duplication | ❌ Full copy in model | ✅ No copy | ✅ No copy — reads parquet directly |
| Works with Delta tables | ❌ Needs import | ✅ Via SQL endpoint | ✅ Native OneLake access |
| Memory footprint | 🔴 High | 🟢 Low | 🟢 Low (on-demand columnar cache) |

> 💡 **How it works under the hood:** Direct Lake memory-maps the Delta/Parquet files in OneLake and loads column segments on demand — no ETL, no scheduled refresh, no V-Order shuffle. When you add new data to the Gold layer, the model picks it up automatically.

> ⚠️ **Important:** Direct Lake requires your data to live in a Fabric Lakehouse or Warehouse. External Delta tables (e.g., on ADLS Gen2 via shortcut) work only if a OneLake shortcut is configured first.

> 📚 **Official Documentation:**
> - [Direct Lake Overview](https://learn.microsoft.com/en-us/power-bi/enterprise/directlake-overview)
> - [Direct Lake vs Import vs DirectQuery](https://learn.microsoft.com/en-us/power-bi/connect-data/service-dataset-modes-understand)

---

## 🏗️ 2 — Create the Semantic Model

You will now build the **ZOSA Analytics Model** on top of the Gold tables you created in Module 04.

### Steps

1. Open your **lh_zosa** in the Fabric portal.
2. In the Lakehouse ribbon, click **New Power BI semantic model**.
3. Name the model: `ZOSA Analytics Model`.
4. In the table picker, select the **Gold layer** tables:
   - `gold_asteroid_risk`
   - `gold_mission_summary`
   - `gold_solar_activity`
   - `gold_exoplanet_catalog`
5. Also add these **Silver layer** tables (you will need them for relationships):
   - `missions_silver`
   - `crew_silver`
   - `telemetry_silver`
6. Click **Confirm**. Fabric creates a Direct Lake semantic model and opens the **Model view**.

> 💡 **Tip:** If you don't see the Gold tables, make sure the notebooks from Module 04 ran successfully and that the tables are registered in the Lakehouse explorer.

> 📚 **Learn more:** [Create Semantic Models in Fabric](https://learn.microsoft.com/en-us/fabric/data-warehouse/semantic-models)

---

## 🔗 3 — Define Relationships (Star Schema)

A clean star schema means faster queries and simpler DAX. Your **fact table** is `gold_mission_summary`; the rest are dimensions.

### Steps

1. In the **Model view**, switch to **Diagram layout** (the icon that looks like connected boxes).
2. Create the following relationships by dragging columns between tables:

| From (Fact / Table) | Column | To (Dimension) | Column | Cardinality | Cross-filter |
|---|---|---|---|---|---|
| `gold_mission_summary` | `region` | `crew_silver` | `region` | Many-to-many | Single |
| `gold_mission_summary` | `ground_station_id` | `telemetry_silver` | `ground_station_id` | Many-to-one | Single |
| `gold_mission_summary` | `mission_id` | `missions_silver` | `mission_id` | Many-to-one | Single |
| `gold_asteroid_risk` | `discovery_date` | `gold_solar_activity` | `observation_date` | Many-to-one | Single |
| `gold_exoplanet_catalog` | `mission_id` | `gold_mission_summary` | `mission_id` | Many-to-one | Single |

3. After wiring the relationships, your diagram should look like a classic **star** with `gold_mission_summary` at the center.

> 💡 **Tip:** If Fabric auto-detected relationships, review them carefully. Auto-detection sometimes creates incorrect cardinalities — always validate manually.

```
                  crew_silver
                       │ region
                       │
 gold_solar_activity ──┤ discovery_date
                       │
          gold_mission_summary  ◄── fact table
               │             │
   ground_station_id     mission_id
               │             │
     telemetry_silver   missions_silver
                             │
                    gold_exoplanet_catalog
```

> 📚 **Official Documentation:**
> - [Star Schema Design Guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
> - [Understand Model Relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand)

---

## 📐 4 — Create DAX Measures

In the **Model view**, select a table in the **Data** pane and use the formula bar to add the following measures to `gold_mission_summary` (or create a dedicated `_Measures` table for organization).

### 4.1 Hazard Index

```dax
Hazard Index =
    AVERAGE(gold_asteroid_risk[hazard_score])
```

> This gives mission control a single number summarizing the current asteroid threat level.

### 4.2 Mission Success Rate

```dax
Mission Success Rate =
    DIVIDE(
        CALCULATE(
            COUNTROWS(gold_mission_summary),
            gold_mission_summary[status] = "Completed"
        ),
        COUNTROWS(gold_mission_summary)
    )
```

> 💡 **Why `DIVIDE` instead of `/`?** `DIVIDE` handles division-by-zero gracefully — returning `BLANK()` instead of an error.

### 4.3 Critical Asteroids

```dax
Critical Asteroids =
    CALCULATE(
        COUNTROWS(gold_asteroid_risk),
        gold_asteroid_risk[risk_category] = "Critical"
    )
```

### 4.4 Habitable Candidates

```dax
Habitable Candidates =
    CALCULATE(
        COUNTROWS(gold_exoplanet_catalog),
        gold_exoplanet_catalog[habitability_zone] = "Habitable Zone"
    )
```

### 4.5 Total Missions

```dax
Total Missions =
    COUNTROWS(gold_mission_summary)
```

### 4.6 Active Missions

```dax
Active Missions =
    CALCULATE(
        COUNTROWS(gold_mission_summary),
        gold_mission_summary[status] = "Active"
    )
```

### 4.7 Total Budget

```dax
Total Budget =
    SUM(gold_mission_summary[total_budget_usd])
```

### 4.8 Max Hazard Score

```dax
Max Hazard Score =
    MAX(gold_asteroid_risk[hazard_score])
```

### 4.9 Near-Earth Objects

```dax
Near-Earth Objects =
    COUNTROWS(gold_asteroid_risk)
```

### Validation

After creating all nine measures, click on each one in the **Fields** pane and confirm it returns a reasonable value (not blank, not an error). If a measure shows an error, double-check column names against the Gold tables — typos in column references are the most common issue.

> 📚 **Learn more:** [DAX Reference](https://learn.microsoft.com/en-us/dax/dax-overview)

---

## 🔒 5 — Implement Row-Level Security (RLS)

Row-Level Security restricts which rows a user can see based on their identity. ZOSA's European analysts should see only missions from their region.

### Steps

1. In the semantic model, switch to the **Manage roles** view (Model tab → Manage roles).
2. Click **New role** and name it: `Europe_Analysts`.
3. Select the table `gold_mission_summary`.
4. In the DAX filter expression box, enter:

```dax
[region] = "Europe"
```

5. Click **Save**.

### Test the Role

1. In the model toolbar, click **View as** → select **Europe_Analysts**.
2. Navigate to the Data view and verify that `gold_mission_summary` only shows rows where `region = "Europe"`.
3. Confirm that measures like **Mission Success Rate** recalculate using only the filtered rows.
4. Click **Stop viewing as role** when done.

> 💡 **Recall:** In Module 02, you configured **OneLake Security** at the storage layer. RLS operates at the **semantic model** layer — a complementary defense. OneLake Security controls who can *access* the files; RLS controls who can *see which rows* once they have access.

> ⚠️ **Important:** RLS only applies when users query through the semantic model (e.g., Power BI reports). Direct Lakehouse SQL queries bypass RLS entirely — OneLake Security is your backstop there.

> 📚 **Learn more:** [Row-Level Security in Semantic Models](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security)

---

## 🛡️ 6 — Configure Object-Level Security (OLS)

Object-Level Security hides entire columns or tables from specific roles. ZOSA's `budget_usd` column in `gold_mission_summary` should be visible only to executives.

### Steps (via Tabular Editor)

1. **Connect Tabular Editor to your model:**
   - Open **Tabular Editor** (download from [tabulareditor.com](https://tabulareditor.com) if needed).
   - Connect using the **XMLA endpoint** of your Fabric workspace. Find it under **Workspace settings → Premium → Workspace connection**.
   - Select `ZOSA Analytics Model`.

2. **Create an OLS role:**
   - In the **Roles** node, create a new role called `Non_Executive`.
   - Under **Table Permissions**, set `gold_mission_summary` to **Read**.

3. **Hide the column:**
   - Expand `gold_mission_summary` → `Columns` → right-click `budget_usd`.
   - Under **Object-Level Security**, set the `Non_Executive` role to **None** (no access).

4. **Save and deploy** back to the Fabric service.

> 💡 **XMLA Endpoint Access:** The XMLA read/write endpoint is available in Fabric capacities (F SKUs). Make sure your workspace is assigned to a capacity and that XMLA read/write is enabled in the **Admin portal → Capacity settings**.

> ⚠️ **Important:** OLS is configured through external tools (Tabular Editor, SSMS) because the Fabric portal does not yet have a native OLS editor. Always test OLS changes in a development workspace before promoting to production.

> 📚 **Official Documentation:**
> - [XMLA Endpoint Connectivity](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-connect-tools)
> - [External Tools (Tabular Editor)](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-external-tools)

---

## ✅ 7 — Checkpoint

Before moving on, verify that everything is in place:

- [ ] **Semantic model** `ZOSA Analytics Model` exists in your workspace and uses **Direct Lake** mode.
- [ ] **Seven tables** are loaded: four Gold, three Silver.
- [ ] **Relationships** form a star schema centered on `gold_mission_summary`.
- [ ] **Nine DAX measures** return valid values:
  - `Hazard Index` — a decimal number
  - `Mission Success Rate` — a percentage (0–1 range)
  - `Critical Asteroids` — an integer count
  - `Habitable Candidates` — an integer count
  - `Total Missions` — an integer count
  - `Active Missions` — an integer count
  - `Total Budget` — a currency value
  - `Max Hazard Score` — a decimal number
  - `Near-Earth Objects` — an integer count
- [ ] **RLS role** `Europe_Analysts` filters correctly (verified with "View as").
- [ ] **OLS** hides `budget_usd` for `Non_Executive` role (verified in Tabular Editor).

> 🎉 **Congratulations!** Your semantic model is ready. The science directors won't need to wait until tomorrow — they can start exploring data *right now*. But raw numbers aren't enough; they want beautiful, interactive visuals. That's exactly what you'll build in Module 06.

---

**Navigation:**
[← Module 04 — Medallion Lakehouse](04-medallion-lakehouse.md) | [Module 06 — Power BI Reports →](06-power-bi-reports.md)

[← Back to README](../README.md)
