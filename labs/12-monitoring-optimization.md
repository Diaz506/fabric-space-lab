# Module 12 — Monitoring & Optimization

> The CFO asks about costs — Capacity Metrics, CU analysis, and optimization strategies

**Estimated time:** 45 minutes

---

## The Story So Far

Three months in. Everything is running in production. Eventstreams are flowing, pipelines are refreshing, dashboards are live, and the ML model is predicting asteroid threats daily.

Then Marcus Chen, the CFO, slides a printout across your desk:

> *"Our Fabric bill is 40% higher than projected. I need to know where the capacity units are going — and how to bring them down."*

Time to put on your FinOps hat.

---

## 12.1 — Fabric Capacity Metrics App

The **Microsoft Fabric Capacity Metrics** app gives you detailed visibility into how your capacity is being consumed.

### What Are Capacity Units (CUs)?

Every operation in Fabric consumes **Capacity Units (CUs)** — a normalized measure of compute:

| SKU | CUs | Typical Use |
|---|---|---|
| F2 | 2 CUs | Dev/test, small teams |
| F32 | 32 CUs | Departmental workloads |
| F64 | 64 CUs | Production analytics (ZOSA's current tier) |
| F128 | 128 CUs | Large-scale enterprise |

CU consumption is measured in **CU-seconds**. A query that uses 4 CUs for 10 seconds consumes 40 CU-seconds. Fabric tracks consumption over **30-second evaluation windows** — if you exceed your capacity's CU allowance in a window, smoothing and throttling kick in.

### Install the Capacity Metrics App

1. Go to **Microsoft AppSource** (appsource.microsoft.com)
2. Search for **"Microsoft Fabric Capacity Metrics"**
3. Click **Get it now** and install it to a workspace (use ZOSA-Prod or a dedicated monitoring workspace)
4. After installation, open the app and connect it to your capacity
5. The app will begin populating with data — historical data goes back **14 days**

### Navigate the Monitoring Hub

The Fabric portal also has a built-in **Monitoring hub**:

1. Click **Monitoring hub** in the left navigation
2. View active and recent operations across all workspaces
3. Filter by workspace, item type, status, and time range

---

## 12.2 — Analyze CU Consumption

Open the Capacity Metrics app and dig into ZOSA's consumption patterns.

### CU Usage by Workload Type

The app breaks down consumption by workload engine:

| Workload | CU Usage (30-day avg) | % of Total | Notes |
|---|---|---|---|
| **Spark (Notebooks)** | 18.4 CU-hrs/day | 38% | ML training notebook is the top consumer |
| **Eventstream** | 11.2 CU-hrs/day | 23% | Continuous real-time processing |
| **SQL Analytics** | 8.7 CU-hrs/day | 18% | Semantic model queries, SQL endpoint |
| **Power BI** | 6.1 CU-hrs/day | 13% | Report renders, DAX queries |
| **Data Pipelines** | 3.8 CU-hrs/day | 8% | Orchestration, Copy activities |

### Peak vs. Off-Peak Patterns

Look at the **hourly consumption chart**:

- **Peak hours (09:00–17:00 UTC):** CU usage averages 85% of capacity — driven by interactive report queries, ad-hoc notebook runs, and pipeline refreshes
- **Off-peak hours (22:00–06:00 UTC):** CU usage drops to 15% — only Eventstream and scheduled refreshes running
- **Spike events:** ML model retraining (Tuesdays, 02:00 UTC) causes a 2-hour burst to 95% capacity

### Top Consuming Items

Drill into the **item-level breakdown**:

| Item | Avg CU/day | Observation |
|---|---|---|
| `Threat_Response_Model` notebook | 9.2 CU-hrs | Full model retraining runs weekly — very expensive |
| Eventstream (asteroid telemetry) | 8.1 CU-hrs | Always on, continuous ingestion |
| `Risk_Assessment_Pipeline` | 3.4 CU-hrs | Runs every hour, includes Spark transforms |
| Mission Control Report | 2.8 CU-hrs | High viewer count, complex DAX |
| Scheduled semantic model refresh | 2.1 CU-hrs | Full refresh 4x daily |

### Interactive vs. Background Consumption

Fabric categorizes consumption into two buckets:

- **Interactive:** User-initiated queries, report renders, notebook executions. These get priority scheduling.
- **Background:** Scheduled refreshes, pipeline runs, Eventstream processing. These can be smoothed over time.

> 💡 **Key insight:** Background operations can be **deferred** during peak hours, while interactive operations get immediate CUs. Understanding this split is crucial for optimization.

---

## 12.3 — Identify Throttling

When consumption exceeds your capacity's CU allowance, Fabric applies a progressive response:

### The Throttling Cascade

| Phase | Trigger | Effect |
|---|---|---|
| **Smoothing** | Usage exceeds capacity in a 30-second window | Background jobs are spread over a longer window (up to 24 hours). No user impact. |
| **Throttling** | Sustained overage after smoothing | Interactive queries are delayed. Users experience slower report loads and query responses. |
| **Rejection** | Extreme sustained overage | New requests are rejected with an error. Critical — immediate action required. |

### Spotting Throttling Events

In the Capacity Metrics app:

1. Go to the **Throttling** tab
2. Look for:
   - 🟡 **Yellow bars** — smoothing active (background jobs deferred)
   - 🟠 **Orange bars** — throttling active (interactive delays)
   - 🔴 **Red bars** — rejection events (requests failing)
3. Correlate throttling events with specific items using the **timeline view**

For ZOSA, you discover:
- **Tuesday mornings** see throttling during ML model retraining
- **Occasional spikes** when Dr. Osei runs ad-hoc Spark analysis during peak hours
- **No rejections** — we're close to the edge but not over

---

## 12.4 — Optimization Strategies

Now for the part Marcus Chen cares about. Here's how to reduce CU consumption:

### 1. Pause/Resume Capacity During Off-Hours

ZOSA's capacity runs 24/7 but is only busy 10 hours/day.

**Option A — Azure Automation Runbook:**

```powershell
# Schedule this to run at 22:00 UTC (pause) and 06:00 UTC (resume)

# Pause capacity
Update-AzFabricCapacity `
  -ResourceGroupName "zosa-rg" `
  -CapacityName "zosa-prod-f64" `
  -State "Paused"

# Resume capacity
Update-AzFabricCapacity `
  -ResourceGroupName "zosa-rg" `
  -CapacityName "zosa-prod-f64" `
  -State "Active"
```

**Option B — Azure Logic App** with a recurrence trigger and Azure Resource Manager actions.

> ⚠️ **Important:** When capacity is paused, all Fabric operations stop — Eventstreams, scheduled refreshes, everything. Plan accordingly. Consider keeping a smaller capacity (F2) for critical real-time streams.

**Estimated savings:** ~58% capacity cost (14 hours/day paused)

### 2. Optimize Spark Notebooks

The ML training notebook is the single biggest consumer. Optimize it:

```python
# BEFORE: Reading full dataset every time
df = spark.read.format("delta").load("Tables/asteroid_observations")
df_features = df.select("*").filter(df.year >= 2020)

# AFTER: Partition pruning + column selection + caching
df = (spark.read.format("delta")
      .load("Tables/asteroid_observations")
      .filter("observation_year >= 2020")   # Pushdown filter to Delta
      .select("asteroid_id", "velocity", "diameter",
              "distance_km", "risk_score", "observation_date"))

df.cache()  # Cache for reuse in multiple training steps
```

Additional Spark optimizations:
- **Partition tables** by date (already done in Module 4 — verify it's being leveraged)
- **Use V-Order** optimization on Delta tables for faster reads
- **Reduce shuffles** — avoid `repartition()` unless necessary, prefer `coalesce()` for reducing partitions
- **Set appropriate executor counts** — don't use `spark.conf.set("spark.executor.instances", 20)` for a 1GB dataset

**Estimated savings:** 30–50% reduction in Spark CU consumption

### 3. Eventstream Efficiency

The asteroid telemetry Eventstream runs 24/7 but derives multiple outputs:

- **Derived stream for ML features** — only needed during training (weekly)
- **Derived stream for archival** — can batch instead of stream
- **Real-time alerting stream** — must stay active

**Action:** Pause derived streams that don't need real-time processing during off-hours. Keep only the critical alerting stream active 24/7.

**Estimated savings:** 15–20% reduction in Eventstream CU consumption

### 4. Monitor Direct Lake Fallback

Direct Lake mode reads directly from OneLake — but it can **fall back to DirectQuery** if:
- Table sizes exceed memory limits
- Too many columns are loaded
- Row-level security is complex

**How to detect fallback:**

1. Open the **Semantic model** in the Fabric portal
2. Go to **Settings** → **Direct Lake behavior**
3. Check the **Refresh history** for fallback events
4. In the Capacity Metrics app, look for SQL analytics CU spikes that correlate with report usage

**Fix it:**
- Split large tables into fact/dimension with proper star schema
- Remove unused columns from the model
- Ensure Delta tables have V-Order optimization enabled

### 5. Semantic Model Optimization

Reduce the model's memory footprint:

- **Remove unused columns** — does the model really need all 47 columns from the asteroid table?
- **Remove unused tables** — staging tables shouldn't be in the semantic model
- **Optimize cardinality** — high-cardinality text columns (like `asteroid_name` with 50K uniques) are expensive
- **Use calculated columns sparingly** — prefer measures over calculated columns
- **Disable auto date/time** — it creates hidden date tables for every date column

### 6. Right-Size Capacity

After 30 days of monitoring:
- If peak sustained usage is consistently below **50% of capacity** → consider downsizing
- If throttling occurs frequently → consider upsizing or optimizing first

For ZOSA: After optimizations, if average consumption drops from 85% to 45% of F64, consider moving to **F32** and pocketing the savings.

---

## 12.5 — Set Up Alerts

Don't wait for Marcus Chen to tell you there's a problem. Set up proactive alerts.

### Configure Alerts in the Capacity Metrics App

| Alert | Condition | Action |
|---|---|---|
| **High CU Usage** | CU usage > 80% sustained for 30+ minutes | Email ops-team@zosa.space |
| **Throttling Detected** | Any throttling event | Email ops-team@zosa.space + Teams notification |
| **Rejection Event** | Any rejection event | Email ops-team@zosa.space + page on-call engineer |
| **Pipeline Failure** | Any data pipeline fails | Email dev-team@zosa.space |
| **Refresh Failure** | Semantic model refresh fails | Email dev-team@zosa.space |

### Configure Data Pipeline Alerts

For pipeline-specific alerts:

1. Open the **ZOSA-Prod** workspace
2. Navigate to each critical pipeline
3. Click **Settings** → **Notifications**
4. Enable alerts for: **Failed**, **Cancelled**, **Succeeded** (optional)
5. Set recipients

### Azure Monitor Integration

For enterprise alerting, integrate Fabric capacity metrics with Azure Monitor:

1. In the Azure portal, navigate to your Fabric capacity resource
2. Go to **Metrics** → configure alert rules on capacity utilization
3. Connect to **Action Groups** for email, SMS, webhook, or PagerDuty notifications

---

## 12.6 — Cost Optimization Checklist

Summary of all recommendations for Marcus Chen:

| # | Optimization | Current Cost Impact | Estimated Savings | Effort |
|---|---|---|---|---|
| 1 | Pause/Resume capacity off-hours | 24/7 capacity cost | **~58% cost reduction** | Low — Azure Automation setup |
| 2 | Optimize Spark notebooks | 38% of CU consumption | **30–50% Spark savings** | Medium — code changes |
| 3 | Pause non-critical Eventstreams | 23% of CU consumption | **15–20% Eventstream savings** | Low — configuration |
| 4 | Fix Direct Lake fallback | Hidden DirectQuery costs | **Variable — depends on fallback frequency** | Medium — model redesign |
| 5 | Optimize semantic model | 13% of CU consumption | **10–20% Power BI savings** | Low — column cleanup |
| 6 | Right-size capacity (after optimization) | F64 cost | **Up to 50%** if F32 suffices | Low — SKU change |
| 7 | Schedule ML training off-peak | Tuesday peak throttling | **Eliminates throttling events** | Low — schedule change |

> 💡 **Combined impact:** Implementing items 1, 2, and 3 alone could bring ZOSA's Fabric costs back to projected levels — and possibly below.

Marcus Chen reviews the plan:

> *"If you can deliver even half of these savings, I'll approve the budget for that second capacity you've been asking about."*

---

## 12.7 — ZOSA Graduation Ceremony 🎓

Six months after your first day, ZOSA's analytics platform is running in production. Real-time asteroid monitoring, AI-powered risk predictions, automated threat responses — all on Microsoft Fabric.

Dr. Vasquez presents you with the **"Order of the Golden Capacity Unit"** award at the quarterly all-hands. Major Nakamura gives you a nod of approval. Dr. Osei is already planning v2 of the ML model. Marcus Chen admits the cost is *"acceptable."* And Sofia? She's already asking about the next security feature.

> **Welcome to the team, Engineer. Your mission continues.** 🚀

---

## 12.8 — What's Next?

Your Fabric journey doesn't end here. Areas to explore:

| Topic | Description |
|---|---|
| **Advanced ML with Fabric** | Deep learning, MLflow model registry, A/B testing of models |
| **Copilot in Fabric** | AI-assisted DAX, SQL, Spark code generation, natural language queries |
| **Cross-Tenant Sharing** | Share datasets across organizations with Fabric's external data sharing |
| **Fabric REST APIs** | Automate workspace management, item deployment, and monitoring programmatically |
| **OneLake Data Hub** | Discover and govern data across the entire organization |
| **Fabric Databases (Mirroring)** | Mirror Azure SQL, Cosmos DB, or Snowflake data into OneLake |
| **Power BI Embedded** | Embed ZOSA dashboards into the mission control web application |
| **GraphQL API in Fabric** | Expose Fabric data through GraphQL for custom applications |

---

## 12.9 — Final Checkpoint ✅

The complete ZOSA Space Analytics Platform:

| Module | What You Built | Status |
|---|---|---|
| 1 | Workspace setup & architecture | ⬜ |
| 2 | Lakehouse & medallion architecture | ⬜ |
| 3 | Data ingestion pipelines | ⬜ |
| 4 | Spark notebooks & transformations | ⬜ |
| 5 | SQL analytics & warehouse | ⬜ |
| 6 | Real-time with Eventstream & KQL | ⬜ |
| 7 | Semantic model & Power BI reports | ⬜ |
| 8 | Security, governance & compliance | ⬜ |
| 9 | Activator alerts & automation | ⬜ |
| 10 | AI Agents with Fabric | ⬜ |
| 11 | CI/CD & Deployment Pipelines | ⬜ |
| 12 | Monitoring & Optimization | ⬜ |

> 🎯 **Congratulations!** You've built a complete, production-grade analytics platform on Microsoft Fabric — from raw data ingestion to real-time monitoring, AI-powered predictions, governed deployments, and cost-optimized operations.

---

**Navigation:**
[← Module 11 — CI/CD & Deployment](11-ci-cd-deployment.md)

[← Back to README](../README.md)

