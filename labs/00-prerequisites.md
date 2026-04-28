# Module 00 — Prerequisites

> Setup, API keys, and your mission briefing

⏱️ **Estimated time:** 30 minutes

---

## 🚀 Your Mission Begins

> Welcome aboard, Engineer.
>
> You've just been recruited by **Zenith Orbital Space Agency** — an international organization coordinating deep-space observation, asteroid defense monitoring, and exoplanet research from 12 ground stations around the world.
>
> Your predecessor left suddenly (something about "too many Excel files"), and you're inheriting a legacy analytics stack that's held together with duct tape and stored procedures.
>
> The CTO, **Dr. Elena Vasquez**, has one directive: *migrate everything to Microsoft Fabric.*
>
> Your mission starts now.

---

## 🗺️ What You'll Build

Over the next 13 modules (~8 hours total), you'll go from an empty Fabric tenant to a fully operational, AI-powered analytics platform for ZOSA. Here's the journey:

| Module | Title | What You'll Do |
|--------|-------|----------------|
| **00** | Prerequisites | ← You are here |
| **01** | Capacity & Workspace Setup | Provision Fabric capacity and configure workspaces |
| **02** | Lakehouse & Bronze Layer | Create your first Lakehouse and ingest raw data |
| **03** | Shortcuts & OneLake | Connect external sources with shortcuts |
| **04** | Silver Layer — Notebooks | Clean and transform data with PySpark notebooks |
| **05** | Gold Layer — Data Warehouse | Build a star schema in the Fabric warehouse |
| **06** | Semantic Model & Power BI | Create reports and a semantic model |
| **07** | Real-Time Intelligence | Stream telemetry with Eventhouse and KQL |
| **08** | Data Activator | Set up alerts and automated triggers |
| **09** | Data Science & ML | Train and deploy ML models in Fabric |
| **10** | Data Factory Pipelines | Orchestrate end-to-end ETL pipelines |
| **11** | CI/CD & Deployment Pipelines | Version control and automated deployments |
| **12** | Governance & Administration | Security, lineage, and capacity management |

---

## ✅ Prerequisites Checklist

> **💡 Heads-up for Module 02:** To fully validate security rules (RLS, CLS, DDM), you'll need **Entra ID admin rights** to create 2 test users. If you're on a Fabric trial tenant, you already have admin rights. We'll walk you through it in Module 02.

### 1. Microsoft Fabric Capacity

You need access to a Fabric-enabled workspace. Two options:

- **Option A — Free 60-day trial (recommended for learners):**
  Sign up at [Microsoft Fabric Trial](https://learn.microsoft.com/fabric/get-started/fabric-trial). No credit card required.

- **Option B — Paid capacity:**
  F2 minimum, F64 recommended for the full experience (especially real-time and Data Science modules).

**How to verify:**

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Click **Settings** (⚙️ gear icon) → **Admin portal** or **Account**
3. Confirm you see **Fabric (Preview)** or **Fabric** enabled

> **⚠️ Note:** If your organization's admin has disabled Fabric, you'll need to request access or use a personal Microsoft account for the trial.

---

### 2. NASA API Key

We use real NASA data to populate the ZOSA universe.

1. Register at **[https://api.nasa.gov/](https://api.nasa.gov/)** — it's free and instant
2. You'll receive an API key via email

> **💡 Tip:** You can also use `DEMO_KEY` for low-rate testing (30 requests/hour, 50 requests/day). Not ideal for full data generation but fine for testing.

> **⚠️ Note:** If you'd rather skip the API calls entirely, pre-generated sample data is included in the repo under `data/sample/`. See [Path B](#path-b--use-pre-generated-sample-data) below.

---

### 3. Python 3.10+

Required for running data generation and transformation scripts.

**Verify your installation:**

```bash
python --version
# Expected: Python 3.10.x or higher
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

> **💡 Tip:** Consider using a virtual environment to keep things clean:
> ```bash
> python -m venv .venv
> source .venv/bin/activate   # macOS/Linux
> .venv\Scripts\activate      # Windows
> pip install -r requirements.txt
> ```

---

### 4. Power BI Desktop

Required for **Module 06** (Semantic Model & Power BI).

- Download from [https://powerbi.microsoft.com/desktop/](https://powerbi.microsoft.com/desktop/)
- Or install via the **Microsoft Store** (auto-updates)

> **⚠️ Note:** Power BI Desktop is Windows-only. If you're on macOS/Linux, you can use the Power BI Service in your browser for most tasks, but the Desktop experience is richer.

---

### 5. Git

Required for **Module 11** (CI/CD & Deployment Pipelines).

**Verify your installation:**

```bash
git --version
# Expected: git version 2.x.x
```

If not installed, download from [https://git-scm.com/](https://git-scm.com/).

---

### 6. Azure Subscription (Optional)

Only needed if you want to complete the **ADLS Gen2 shortcut** exercise in **Module 03**.

- A [free Azure account](https://azure.microsoft.com/free/) works fine
- You'll create a small storage account (costs pennies)

> **💡 Tip:** If you don't have an Azure subscription, you can skip the ADLS shortcut exercise and still complete 95% of the lab.

---

## 📦 Clone & Setup

```bash
git clone https://github.com/Diaz506/fabric-space-lab.git
cd fabric-space-lab
pip install -r requirements.txt
```

### Path A — Generate Fresh Data from NASA APIs

*Recommended for the most realistic experience:*

```bash
python data/fetch_nasa_apis.py --api-key YOUR_KEY
python data/generate_synthetic.py
```

This will fetch real asteroid, exoplanet, and solar event data, then generate synthetic telemetry and mission records for ZOSA's 12 ground stations.

### Path B — Use Pre-generated Sample Data

If you'd rather skip the API calls, sample data is already included in `data/sample/`. No additional steps needed — the lab notebooks will detect and use it automatically.

---

## 👥 Meet Your Team

Throughout these labs, you'll interact with key ZOSA personnel. Get to know them:

> **Dr. Elena Vasquez** — *CTO*
> Astrophysicist turned executive. Recruited you personally. Demands data-driven decisions and has zero patience for "it's in a spreadsheet somewhere." Your direct boss.

> **Major Kai Nakamura** — *Director of Planetary Defense*
> Former JAXA mission controller. Needs real-time asteroid tracking alerts with sub-minute latency. Sleeps with a pager. Will be your most demanding stakeholder.

> **Dr. Amara Osei** — *Chief Data Scientist*
> Published 47 papers on orbital mechanics. Wants ML models for collision risk prediction and anomaly detection. Thinks in dataframes.

> **Sofia Lindqvist** — *CISO (Chief Information Security Officer)*
> Security-first mindset. Her first question is always: "Who sees what?" Will audit every workspace permission you set. Do not disappoint her.

> **Marcus Chen** — *CFO*
> Watches every capacity unit like a hawk. Will quiz you on cost optimization. If your pipeline wastes CUs, you'll hear about it.

---

## 🌍 Ground Stations Reference

ZOSA operates 12 ground stations worldwide. This data is used throughout the lab as reference/dimension data.

| ID | Station Name | Region | Location |
|------|-------------------|---------------|--------------------------|
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

---

## ✅ Checkpoint

Before moving on, verify you have:

- [ ] Fabric capacity enabled (trial or paid)
- [ ] NASA API key saved (or you're using sample data)
- [ ] Python 3.10+ installed with dependencies (`pip install -r requirements.txt`)
- [ ] Repository cloned and ready
- [ ] Power BI Desktop installed *(can defer to Module 06)*
- [ ] Git installed *(can defer to Module 11)*

> **✅ Checkpoint:** All set? Dr. Vasquez is waiting. Let's provision your Fabric workspace.

---

**Navigation:**
[← Back to README](../README.md) | [Module 01 — Capacity & Workspace Setup →](01-capacity-and-workspace.md)

