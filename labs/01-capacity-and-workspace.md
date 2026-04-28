# Module 01 — Capacity & Workspace Setup

> Day 1 at ZOSA — choosing your SKU and building your analytics home

---

> *Day 1 at Zenith Orbital HQ in Geneva. Dr. Vasquez meets you at the entrance: "Welcome aboard. I've secured a Fabric capacity for us — your first job is to set up our analytics environment. We need separate spaces for development, testing, and production. And please — organize it properly. The last engineer named everything `test_final_v2_REAL`."*

---

## 🏗️ Section 1: Understanding Fabric Capacity

Before you create anything, you need to understand the foundation everything else sits on: **Fabric Capacity**.

A Fabric capacity is a **dedicated pool of compute resources** measured in **Capacity Units (CUs)**. Think of it as the engine that powers all Fabric workloads — Lakehouses, Warehouses, Notebooks, Pipelines, Reports, and more. Without a capacity, your workspaces have no compute to run on.

### SKU Options

| SKU | Capacity Units (CUs) | Recommended Use Case |
|-----|---------------------|----------------------|
| **F2** | 2 | Learning, prototyping, small personal projects |
| **F4** | 4 | Small team development, light analytics |
| **F8** | 8 | Department-level analytics, moderate Spark workloads |
| **F16** | 16 | Multi-team environments, concurrent notebook sessions |
| **F32** | 32 | Production workloads, large-scale data engineering |
| **F64** | 64 | Enterprise production, Real-Time Intelligence, heavy concurrency |

**⚠️ Note:** For this lab, an **F2 trial capacity** is sufficient for Modules 00 through 06. However, if you plan to work through **Module 07 (Real-Time Intelligence)**, you will need an **F64 or higher** — KQL databases and Eventstreams require more compute headroom.

💡 **Tip:** Microsoft offers a free Fabric trial that provisions an F64 capacity for 60 days. If you haven't activated yours yet, go back to [Module 00](00-prerequisites.md) and follow the trial activation steps.

### Capacity vs. Workspace

These two concepts are frequently confused:

- **Capacity** = the compute engine (how much horsepower you have)
- **Workspace** = a logical container for your items (where you organize your work)

A single capacity can power many workspaces, and you assign each workspace to a capacity. Think of it like an office building (capacity) with multiple rooms (workspaces).

### OneLake: One Lake to Rule Them All

Every Fabric tenant gets exactly **one OneLake**. There is no option to create additional ones. OneLake is the unified data lake that underpins all Fabric workloads:

- Workspaces are **logical containers** inside OneLake
- Every item you create (Lakehouse, Warehouse, etc.) stores its data in OneLake
- The data is physically stored in **Delta Parquet** format regardless of which engine wrote it

This is a fundamental architectural decision by Microsoft — it means any engine (Spark, SQL, KQL, Power BI) can access the same data without copies or movement.

---

## 🗂️ Section 2: Creating Your Workspaces

You will now create three workspaces following ZOSA's environment separation strategy: **Development**, **Testing**, and **Production**.

### 2.1 — Create the Development Workspace (ZOSA-Dev)

1. Navigate to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. In the left navigation pane, click **Workspaces**
3. Click **+ New Workspace**

![New Workspace button](../assets/screenshots/01/new-workspace-button.png)

4. Enter the following details:
   - **Name:** `ZOSA-Dev`
   - **Description:** `Zenith Orbital — Development environment for data engineering and analytics`

5. Expand the **Advanced** section
6. Under **License mode**, select your Fabric capacity (Trial or the capacity you provisioned)

![Workspace license mode](../assets/screenshots/01/workspace-license-mode.png)

7. Click **Apply**

✅ **Checkpoint:** You should now see the `ZOSA-Dev` workspace in your workspace list. It will be empty — that's expected.

### 2.2 — Create the Testing Workspace (ZOSA-Test)

1. Click **Workspaces** → **+ New Workspace**
2. Enter the following details:
   - **Name:** `ZOSA-Test`
   - **Description:** `Zenith Orbital — Testing and validation environment`
3. Expand **Advanced** → select the same Fabric capacity
4. Click **Apply**

### 2.3 — Create the Production Workspace (ZOSA-Prod)

1. Click **Workspaces** → **+ New Workspace**
2. Enter the following details:
   - **Name:** `ZOSA-Prod`
   - **Description:** `Zenith Orbital — Production analytics for mission operations`
3. Expand **Advanced** → select the same Fabric capacity
4. Click **Apply**

💡 **Tip:** Naming conventions matter at scale. ZOSA uses the `{Org}-{Environment}` pattern. In enterprise scenarios with multiple business domains, you might extend this to include the domain: `ZOSA-Defense-Dev`, `ZOSA-Science-Dev`, `ZOSA-Operations-Prod`. Pick a convention early and enforce it — your future self will thank you.

---

## 🌐 Section 3: Setting Up Domains

Fabric **Domains** provide a way to logically group workspaces by business area. They don't affect compute or storage — they're an organizational and governance layer that helps administrators manage permissions and policies at the domain level.

### 3.1 — Create the Zenith Orbital Domain

1. Click the **Settings** gear icon (⚙️) in the top-right corner of the Fabric portal
2. Select **Admin portal**

**⚠️ Note:** You need Fabric Admin or Domain Contributor permissions to create domains. If you're using a trial capacity, you are the tenant admin by default.

3. In the Admin portal, navigate to **Domains** in the left menu
4. Click **+ New domain**

![Create new domain](../assets/screenshots/01/create-domain.png)

5. Enter the following:
   - **Name:** `Zenith Orbital`
   - **Description:** `All workspaces for the Zenith Orbital Space Agency analytics platform`
6. Click **Create**

### 3.2 — Assign Workspaces to the Domain

1. Open the **Zenith Orbital** domain you just created
2. Click **Assign workspaces**
3. Search for and select:
   - `ZOSA-Dev`
   - `ZOSA-Test`
   - `ZOSA-Prod`
4. Click **Assign**

![Assign workspaces to domain](../assets/screenshots/01/assign-workspaces-domain.png)

💡 **Tip:** In a larger organization, ZOSA might have separate domains for each division — **Defense**, **Science**, **Operations** — each with their own Dev/Test/Prod workspaces and governance policies. Domains make it possible to delegate administration without giving blanket tenant-wide permissions.

---

## ⚙️ Section 4: Workspace Settings Deep Dive

Now that your workspaces exist, let's configure the development workspace with the right defaults. Navigate to the **ZOSA-Dev** workspace.

1. Click the **Workspace settings** gear icon (⚙️) inside the `ZOSA-Dev` workspace

### 4.1 — OneLake Data Access

Under **OneLake** settings, you'll find the **"Users can access data stored in OneLake with apps external to Fabric"** toggle.

- **Enabled:** External tools (Azure Databricks, Azure Synapse, custom applications) can connect directly to OneLake via the OneLake API or Azure Data Lake Storage Gen2 endpoint
- **Disabled:** Only Fabric-native engines can access the data

For this lab, **leave it enabled** — in Module 05, you'll see how external tools can connect to OneLake data.

### 4.2 — Default Storage Format

The default storage format should be **Delta (Parquet)**. This is the standard for Fabric and should almost never be changed. Here's why:

- **Delta** adds ACID transactions, time travel, and schema enforcement on top of Parquet
- All Fabric engines (Spark, SQL, KQL, Power BI) natively read Delta
- It's the format that enables the "write once, read from anywhere" promise of OneLake

### 4.3 — Spark Settings

Under Spark settings, you can configure:

- **Environment:** Defines the default Spark runtime (libraries, configurations) for notebooks in this workspace. We'll create a custom environment in Module 03.
- **Runtime version:** Choose the Spark runtime version. Use the latest stable version available.

**⚠️ Note:** Don't worry about configuring these in detail right now. These settings become important when you start running Spark notebooks in Module 03 (Data Ingestion). We'll revisit them then.

---

## 🏛️ Section 5: Understanding the OneLake Hierarchy

Before you move on, take a moment to internalize the hierarchy you've just created:

```
Fabric Tenant (your organization)
└── OneLake (one per tenant — the single unified data lake)
    ├── ZOSA-Dev (workspace)
    │   ├── Lakehouse items
    │   ├── Warehouse items
    │   ├── Notebook items
    │   └── Other items...
    ├── ZOSA-Test (workspace)
    │   └── (empty for now)
    └── ZOSA-Prod (workspace)
        └── (empty for now)
```

Key takeaways:

- **Every workspace automatically gets a folder in OneLake.** You don't create this — it just happens.
- **All data lives in OneLake**, regardless of which engine created it. A Spark notebook writing to a Lakehouse and a SQL endpoint writing to a Warehouse both store data in OneLake.
- **This is why cross-engine access works.** You can create a table in a Spark notebook and immediately query it from a SQL endpoint or build a Power BI report on top of it — no ETL, no copies, no movement.

This architecture is the single most important concept in Fabric. Everything you build in the remaining modules leverages this unified storage model.

---

## ✅ Checkpoint

Before moving to Module 02, verify the following:

- [ ] **3 workspaces created:** `ZOSA-Dev`, `ZOSA-Test`, `ZOSA-Prod`
- [ ] **All workspaces assigned to your Fabric capacity** (check under Workspace Settings → Advanced → License mode)
- [ ] **Domain "Zenith Orbital" created** and all 3 workspaces assigned to it
- [ ] **You can navigate to each workspace** and confirm it is empty

If all four checks pass, you're ready for Module 02.

---

> *Dr. Vasquez nods approvingly at your screen. "Clean, organized, separated environments — exactly what we needed. But don't get comfortable. Sofia from security wants to talk to you next. Something about who gets to see what..." She glances at her watch. "You have 10 minutes."*

---

## Navigation

[← Module 00 — Prerequisites](00-prerequisites.md) | [Module 02 — Governance & Security →](02-governance-and-security.md)

[← Back to README](../README.md)
