# Module 11 — CI/CD & Deployment

> From Dev to Prod — Git integration, Variable Library, and Deployment Pipelines

**Estimated time:** 50 minutes

---

## The Story So Far

Dr. Vasquez calls an all-hands meeting:

> *"We've been building in Dev for weeks. The mission board meets Friday and they need production dashboards. It's time to go live — but we do it the right way. No cowboy deployments."*

Major Nakamura adds: *"If someone breaks production, they're on asteroid-naming duty for a month."*

Point taken. Let's set up a proper deployment process.

---

## 11.1 — CI/CD Patterns Overview

Microsoft Fabric supports multiple deployment patterns. Choosing the right one depends on your team's maturity and requirements:

| Pattern | Description | Best For |
|---|---|---|
| **Pipeline-only** | Use Fabric Deployment Pipelines alone without Git | Small teams, quick wins, minimal setup |
| **Git + Deployment Pipelines** ⭐ | Connect workspaces to Git, use Deployment Pipelines for promotion | **Recommended for most teams.** Version control + governed promotion |
| **Full CI/CD (GitHub Actions)** | Git integration + GitHub Actions/Azure DevOps pipelines to automate deployments | Enterprise teams with existing CI/CD, automated testing requirements |
| **Python CI/CD (fabric-cicd)** | Code-first approach using the `fabric-cicd` Python package | Advanced teams wanting full programmatic control |

> 💡 **Our recommendation:** Start with **Git + Deployment Pipelines**. It gives you version control, change tracking, and governed promotion without the overhead of full CI/CD automation. Graduate to GitHub Actions or `fabric-cicd` when your team is ready.

---

## 11.2 — Enable Git Integration

Git integration in Fabric supports both **GitHub** and **Azure DevOps**. We'll use GitHub since that's where ZOSA stores its code.

### Step-by-Step: Connect ZOSA-Dev to GitHub

1. **Open ZOSA-Dev workspace** in the Fabric portal

2. **Navigate to Workspace settings:**
   - Click the **gear icon** (⚙️) → **Workspace settings**
   - Select the **Git integration** tab

3. **Connect to GitHub:**
   - Under **Git provider**, select **GitHub**
   - Click **Connect** and authenticate with your GitHub account
   - Select the repository: `zosa-fabric-analytics`
   - Select the branch: `develop`
   - Set the **Root folder** to `/fabric-items`
   - Click **Connect and sync**

4. **Verify the connection:**
   - You should see a **Git status** column appear next to each item in the workspace
   - Items show as **Uncommitted** (they exist in the workspace but not yet in Git)

5. **Commit existing items to Git:**
   - Click **Source control** in the top toolbar
   - Review the changes — you'll see all your workspace items listed
   - Add a commit message: `Initial commit: ZOSA Dev workspace items`
   - Click **Commit**

### What Gets Stored in Git?

Once committed, your Fabric items appear as JSON and code files in the repo:

```
/fabric-items/
├── ZOSA_Lakehouse.Lakehouse/
│   └── .platform
├── Asteroid_Ingestion.Notebook/
│   ├── notebook-content.py
│   └── .platform
├── Risk_Assessment_Pipeline.DataPipeline/
│   ├── pipeline-content.json
│   └── .platform
├── Threat_Response_Model.MLModel/
│   └── .platform
├── ZOSA_Semantic_Model.SemanticModel/
│   ├── definition.pbism
│   ├── model.bim
│   └── .platform
└── Mission_Control_Report.Report/
    ├── definition.pbir
    ├── report.json
    └── .platform
```

> 💡 **Key benefit:** Every change to a Fabric item now creates a Git commit. You get full history, diffs, and the ability to roll back.

---

## 11.3 — Variable Library (Preview)

> ⚠️ **Preview Feature:** Variable Library is currently in Preview. Features and behavior may change before general availability.

The **Variable Library** lets you define workspace-level variables that change across environments. Instead of hardcoding connection strings or lakehouse names, you reference variables that swap automatically during deployment.

### Create a Variable Library

1. In the **ZOSA-Dev workspace**, click **+ New item** → **Variable Library**
2. Name it: `ZOSA_Environment_Config`

### Define Variables

Add the following variables to the library:

| Variable Name | Description |
|---|---|
| `lakehouse_name` | Target lakehouse for all notebooks and pipelines |
| `connection_string` | SQL analytics endpoint connection string |
| `capacity_id` | Fabric capacity resource ID |
| `alert_email` | Email for pipeline failure alerts |
| `refresh_schedule` | Cron expression for scheduled refreshes |

### Configure Value Sets

Value sets let you define different values for each environment:

**Dev Value Set:**
```json
{
  "lakehouse_name": "ZOSA_Lakehouse_Dev",
  "connection_string": "jdbc:sqlserver://zosa-dev-endpoint.datawarehouse.fabric.microsoft.com",
  "capacity_id": "/subscriptions/.../capacities/zosa-dev-f64",
  "alert_email": "dev-team@zosa.space",
  "refresh_schedule": "0 */2 * * *"
}
```

**Test Value Set:**
```json
{
  "lakehouse_name": "ZOSA_Lakehouse_Test",
  "connection_string": "jdbc:sqlserver://zosa-test-endpoint.datawarehouse.fabric.microsoft.com",
  "capacity_id": "/subscriptions/.../capacities/zosa-test-f32",
  "alert_email": "qa-team@zosa.space",
  "refresh_schedule": "0 6 * * *"
}
```

**Prod Value Set:**
```json
{
  "lakehouse_name": "ZOSA_Lakehouse_Prod",
  "connection_string": "jdbc:sqlserver://zosa-prod-endpoint.datawarehouse.fabric.microsoft.com",
  "capacity_id": "/subscriptions/.../capacities/zosa-prod-f64",
  "alert_email": "ops-team@zosa.space",
  "refresh_schedule": "0 */1 * * *"
}
```

### Version Control

Because Git integration is enabled, the Variable Library is stored as JSON in your repo. This means:

- Variable definitions are **version-controlled** alongside your Fabric items
- Changes to variables go through the same **PR review process** as code
- You can **diff** variable changes across commits
- Rollback is as simple as reverting a Git commit

---

## 11.4 — Create a Deployment Pipeline

Fabric **Deployment Pipelines** provide a governed way to promote items from Dev → Test → Prod.

### Create the ZOSA Deployment Pipeline

1. In the Fabric portal, go to **Workspaces** in the left nav
2. Click **Deployment pipelines** → **+ New pipeline**
3. Name it: `ZOSA Analytics Pipeline`
4. Add a description: `Promotes ZOSA space analytics items from Dev through Test to Production`

### Configure Pipeline Stages

The pipeline has three stages by default: **Development**, **Test**, **Production**.

1. **Assign workspaces to stages:**

   | Stage | Workspace |
   |---|---|
   | Development | ZOSA-Dev |
   | Test | ZOSA-Test |
   | Production | ZOSA-Prod |

2. For each stage, click **Assign a workspace** and select the corresponding workspace

3. After assigning all three, you'll see a visual pipeline showing items in each stage

> 💡 **Tip:** If the Test and Prod workspaces don't exist yet, create them first. The pipeline can also create them for you by deploying to an empty stage.

### Configure Deployment Rules

Deployment rules control how items change when promoted between stages. Configure rules to automatically use the Variable Library:

1. Click the **⚙️** icon on a pipeline stage
2. Under **Deployment rules**, set:
   - Lakehouse connections → use Variable Library value set for the target stage
   - Data source connections → use Variable Library value set for the target stage

---

## 11.5 — Deploy Dev → Test

Time for the first deployment. Dr. Vasquez watches from over your shoulder.

### Run the Deployment

1. Open the **ZOSA Analytics Pipeline**
2. In the **Development** stage, click **Deploy to next stage** (→ Test)
3. Review the deployment summary:
   - Items to deploy: Lakehouses, Notebooks, Pipelines, Semantic Models, Reports
   - Variable Library values will swap to the **Test** value set
4. Click **Deploy**
5. Wait for deployment to complete (this may take a few minutes)

### Verify in the Test Workspace

1. Navigate to the **ZOSA-Test** workspace
2. Confirm all items are present:

   | Item | Status |
   |---|---|
   | ZOSA_Lakehouse_Test | ✅ Created with Test name |
   | Asteroid_Ingestion notebook | ✅ Deployed, connections updated |
   | Risk_Assessment_Pipeline | ✅ Deployed, connections updated |
   | ZOSA_Semantic_Model | ✅ Deployed |
   | Mission_Control_Report | ✅ Deployed, connected to Test model |
   | Eventstream items | ✅ Deployed (paused — will configure for Test) |

3. Run a quick smoke test:
   - Open the semantic model → verify it connects to the Test lakehouse
   - Open the report → verify visuals render (even with empty data)
   - Run the ingestion pipeline manually with a small test batch

> ✅ **Test deployment successful.** Dr. Vasquez unclenches slightly.

---

## 11.6 — Deploy Test → Prod

Production deployments require more ceremony.

### Pre-Production Checklist

Before deploying to Prod, verify:

- [ ] All pipeline runs succeeded in Test
- [ ] Semantic model refresh completes without errors
- [ ] Reports render correctly with test data
- [ ] Eventstream processes events end-to-end
- [ ] ML model predictions return valid results
- [ ] Variable Library Prod values are reviewed and correct
- [ ] Stakeholders have signed off (Dr. Vasquez, Major Nakamura)

### Approval Gates

> 💡 **Best practice:** Configure approval gates so deployments to Production require human review.

In the deployment pipeline settings:

1. Click the **⚙️** icon on the **Production** stage
2. Enable **Pre-deployment approval**
3. Add approvers: Dr. Vasquez (data lead), Major Nakamura (ops lead)
4. Deployment to Prod will now pause and notify approvers before executing

### Execute the Production Deployment

1. In the pipeline, click **Deploy to next stage** (Test → Production)
2. Approvers receive a notification
3. After approval, the deployment proceeds automatically
4. Variable Library values swap to the **Prod** value set

### Post-Deployment Verification

1. Navigate to **ZOSA-Prod** workspace
2. Verify all items deployed and connections point to production resources
3. Run the full pipeline end-to-end
4. Confirm the Mission Control report loads with live data

> *Dr. Vasquez sends a message to the mission-board channel: "Production dashboards are live. Board meeting is a go."*

---

## 11.7 — Branching Strategy

Now that Git integration is in place, establish a branching strategy for ongoing development:

### Recommended Branch Model

```
main ─────────────────────────────────────── Production (ZOSA-Prod)
  │
  └── develop ────────────────────────────── Development (ZOSA-Dev)
        │
        ├── feature/new-risk-metric ──────── Feature work
        ├── feature/debris-tracking ──────── Feature work
        └── hotfix/pipeline-fix ──────────── Urgent fixes
```

### How It Works

| Action | Process |
|---|---|
| **New feature** | Create `feature/*` branch from `develop`. Connect a personal workspace for testing. |
| **Code review** | Open a Pull Request from `feature/*` → `develop`. Reviewers check diffs in GitHub. |
| **Merge to Dev** | After PR approval, merge to `develop`. ZOSA-Dev workspace syncs automatically. |
| **Promote to Test** | Use Deployment Pipeline: Dev → Test. QA team validates. |
| **Release to Prod** | Merge `develop` → `main` via PR. Then deploy Test → Prod with approval gate. |
| **Hotfix** | Branch `hotfix/*` from `main`. Fix, test, PR to `main`. Cherry-pick back to `develop`. |

### PR-Based Promotion

Pull Requests add governance:

- **Required reviewers** — at least 1 approval before merge
- **Status checks** — run validation (e.g., lint notebooks, check variable references)
- **Diff visibility** — see exactly what changed in Fabric item definitions
- **Audit trail** — every change is linked to a PR with discussion history

---

## 11.8 — Code-First CI/CD with fabric-cicd

For teams wanting full programmatic control, the **`fabric-cicd`** Python package enables code-first deployments.

### Installation

```bash
pip install fabric-cicd
```

### Example: Automated Deployment Script

```python
from fabric_cicd import FabricWorkspace, publish_all_items

# Connect to the target workspace
target = FabricWorkspace(
    workspace_id="your-workspace-guid",
    repository_directory="/path/to/fabric-items",
    item_type_in_scope=[
        "Notebook",
        "DataPipeline",
        "SemanticModel",
        "Report",
        "Lakehouse",
        "MLModel",
        "Eventstream"
    ]
)

# Publish all items from Git to the workspace
publish_all_items(target)
```

### GitHub Actions Integration

You can call `fabric-cicd` from a GitHub Actions workflow:

```yaml
name: Deploy to Fabric
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install fabric-cicd
      - run: python scripts/deploy_to_fabric.py
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
```

> 💡 **When to use `fabric-cicd`:** When you need automated testing gates, multi-workspace orchestration, or integration with existing CI/CD systems. For most teams, Git + Deployment Pipelines is sufficient.

---

## 11.9 — Checkpoint ✅

Verify your deployment pipeline is operational:

| Check | Status |
|---|---|
| ZOSA-Dev workspace connected to GitHub (`develop` branch) | ⬜ |
| All Fabric items committed to Git | ⬜ |
| Variable Library created with Dev, Test, Prod value sets | ⬜ |
| Deployment Pipeline configured: Dev → Test → Prod | ⬜ |
| Successful deployment from Dev → Test | ⬜ |
| Test workspace items verified | ⬜ |
| Production deployment with approval gates | ⬜ |
| Branching strategy documented and team-aligned | ⬜ |

### What You Built

- ✅ Git-backed version control for all Fabric items
- ✅ Environment-aware Variable Library with Dev/Test/Prod configs
- ✅ Governed Deployment Pipeline with three stages
- ✅ Approval gates for production deployments
- ✅ Branching strategy for ongoing development

---

## Story Transition

Major Nakamura pulls you aside after the deployment:

> *"Production is live. The board loved the dashboards. But now comes the hard part — keeping it running. Marcus Chen from Finance is already asking questions about our capacity bill. You'll want to get ahead of that."*

Time to monitor and optimize.

---

**Navigation:**
[← Module 10 — AI Agents](10-ai-agents.md) | [Module 12 — Monitoring & Optimization →](12-monitoring-optimization.md)

[← Back to README](../README.md)

