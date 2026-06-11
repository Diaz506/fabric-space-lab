# 📱 Module 13 — Fabric Apps

> **The Director-General leaned back in her chair. "We have dashboards, real-time alerts, ML predictions, and AI agents — but our stakeholders still have to hunt through workspaces to find what they need." She pulled up a proposal on her screen. "I want *one door* for each audience: a curated app for Mission Control, another for the Science Division, and a public-facing portal for our exoplanet discoveries. Package everything. Make it seamless."**

---

**Estimated time:** 40 minutes

---

## 🎯 Learning Objectives

By the end of this module, you will:

- Understand what **Fabric Apps** (Power BI Apps) are and when to use them
- Create a **Mission Control App** that bundles reports, dashboards, and metrics for ops teams
- Create a **Science Division App** with data exploration and ML insights
- Configure **audience-based access** with different content for different user groups
- Set up **automatic installation** and update policies
- Customize navigation, branding, and landing pages

## 📋 Prerequisites

| Requirement | Details |
|---|---|
| **Modules 05–06 complete** | Semantic model and reports published to ZOSA-Dev |
| **Module 11 complete** | Content promoted to ZOSA-Prod via deployment pipelines |
| **Workspace role** | Member or Admin on the source workspace |

> 📚 **Learn more:** [Create and publish Power BI apps](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-create-distribute-apps)

---

## 13.1 — Understanding Fabric Apps

### What Is a Fabric App?

A **Fabric App** is a packaged collection of content — reports, dashboards, paginated reports, metrics, and even datamart queries — distributed to consumers as a single navigable experience. Think of it as a **curated portal** with its own navigation pane, landing page, and access controls.

| Concept | Description |
|---|---|
| **App** | A read-only bundle of content published from a workspace |
| **Audience** | A named group of users who see a specific subset of the app's content |
| **Navigation** | Custom sidebar with sections, links, and ordering |
| **Landing page** | The first thing users see when they open the app |
| **Auto-install** | Push the app to users automatically — no manual "Get apps" required |

### When to Use Apps vs. Direct Workspace Access

| Scenario | Use |
|---|---|
| Consumers who only need to *view* curated content | ✅ Fabric App |
| Developers who need to edit reports and models | ❌ Direct workspace access |
| Different audiences need different subsets of content | ✅ Fabric App with multiple audiences |
| Embedding content in external portals | ❌ Power BI Embedded |

> 💡 **Key principle:** Workspaces are for *builders*. Apps are for *consumers*.

---

## 13.2 — Create the Mission Control App

This app targets ZOSA's operations team — the people in Mission Control who need real-time status at a glance.

### Step 1: Prepare the Workspace Content

1. Navigate to your **ZOSA-Prod** workspace in the Fabric portal.
2. Verify the following items are present (promoted from ZOSA-Dev via deployment pipelines in Module 11):
   - 📊 **Mission Control Dashboard** (report from Module 06)
   - 📊 **Exoplanet Explorer** (report from Module 06)
   - 📈 **ZOSA Analytics Model** (semantic model from Module 05)
   - ⚡ **Real-Time Alerts Dashboard** (from Module 07, if created)

### Step 2: Create the App

1. In **ZOSA-Prod** workspace, click **Create app** in the top toolbar.
2. The app creation wizard opens with three tabs: **Setup**, **Content**, and **Audiences**.

### Step 3: Configure Setup

| Field | Value |
|---|---|
| App name | `ZOSA Mission Control` |
| Description | `Real-time operational dashboards for Mission Control teams` |
| App logo | Upload `assets/logos/zosa-logo.png` (or use a space-themed icon) |
| Landing page | Mission Control Dashboard |
| App contact | Your ZOSA email or distribution group |

> 💡 **Tip:** The app name appears in users' Apps list and in search results. Keep it clear and professional.

### Step 4: Configure Content & Navigation

The **Content** tab lets you choose which workspace items to include and how to organize them.

1. Select the items to include:
   - ✅ Mission Control Dashboard
   - ✅ Real-Time Alerts Dashboard
   - ✅ Exoplanet Explorer
   - ❌ ZOSA Analytics Model (consumers don't need direct model access)

2. Organize the navigation:
   ```
   📁 Operations
      ├── 📊 Mission Control Dashboard
      └── ⚡ Real-Time Alerts
   📁 Science
      └── 🔭 Exoplanet Explorer
   ```

3. To create sections: click **New section** → name it → drag items into it.
4. To add external links (optional): click **New link** → add a URL to ZOSA's internal wiki or incident tracker.

### Step 5: Configure Audiences

Audiences let you show different content to different user groups.

1. **Audience 1 — Operations Team:**
   - Name: `Operations`
   - Content: All items (Mission Control Dashboard, Real-Time Alerts, Exoplanet Explorer)
   - Access: Add the `ZOSA-MissionControl-Ops` security group

2. **Audience 2 — Leadership:**
   - Name: `Leadership`
   - Content: Mission Control Dashboard, Exoplanet Explorer (exclude real-time alerts — too detailed)
   - Access: Add the `ZOSA-Leadership` security group

3. Click **Publish app**.

> 📝 **Note:** Each audience gets their own navigation experience. A user in the "Leadership" audience will never see the Real-Time Alerts item.

---

## 13.3 — Create the Science Division App

A second app for ZOSA's researchers and data scientists.

### Step 1: Create the App

1. In **ZOSA-Prod** workspace, click **Create app** again (a workspace can publish multiple apps — but only one app *per workspace* in the current Fabric model, so you may need a **ZOSA-Science** workspace).

> ⚠️ **Important:** Each workspace can publish **one app**. If you need a separate Science app, create a **ZOSA-Science** workspace and add or shortcut the relevant content there.

2. Alternatively, use the **multiple audiences** approach within the same app (configured in the previous step).

### Step 2: Science App Content

If using a separate workspace:

| Item | Source |
|---|---|
| Exoplanet Explorer report | Copy or link from ZOSA-Prod |
| Asteroid Risk Model Results | Report built on ML predictions (Module 08) |
| Data Quality Scorecard | Report on Bronze → Silver data quality metrics (Module 04) |

### Step 3: Navigation Structure

```
📁 Exploration
   └── 🔭 Exoplanet Explorer
📁 Risk Assessment
   └── ☄️ Asteroid Risk Predictions
📁 Data Quality
   └── 📋 Quality Scorecard
```

### Step 4: Publish

- Audience: `ZOSA-Science-Team` security group
- Landing page: Exoplanet Explorer
- Click **Publish app**

---

## 13.4 — Auto-Install & Update Policies

### Enable Auto-Install

Push the app directly to users' Apps list without requiring them to search for it:

1. Open the **Fabric Admin Portal** → **Tenant settings**.
2. Under **Content pack and app settings**, enable:
   - ✅ **Push apps to end users**
3. Back in the app settings:
   - Edit the app → **Setup** tab → toggle **Install this app automatically** → Save.

> 📝 **Note:** Auto-install requires **admin consent** at the tenant level. In production, work with your Fabric admin.

### Update the App

When content changes in the workspace (new reports, updated dashboards):

1. Go to the workspace → click **Update app**.
2. Review changes in the Content tab (new items appear with a ✨ indicator).
3. Assign new items to audiences as needed.
4. Click **Update app** — all consumers see the changes immediately.

> 💡 **Best practice:** Combine with Module 11's deployment pipelines — promote content to ZOSA-Prod first, *then* update the app.

---

## 13.5 — Branding & Customization

### Custom Theme

Apply the ZOSA brand to the app experience:

1. In the workspace, go to **Settings → Theme**.
2. Upload a custom JSON theme file:

```json
{
  "name": "ZOSA Space Theme",
  "dataColors": [
    "#2196F3", "#4CAF50", "#FFC107", "#F44336",
    "#9C27B0", "#00BCD4", "#FF5722", "#607D8B"
  ],
  "background": "#0D1B2A",
  "foreground": "#E0E0E0",
  "tableAccent": "#2196F3"
}
```

3. Reports within the app will inherit this theme unless overridden at the report level.

### Custom Landing Page Tips

- Use a **report page** as the landing page with:
  - A ZOSA logo and welcome message (text box or image)
  - Key metric cards showing real-time status
  - Navigation buttons linking to other pages (using bookmarks or page navigation)

---

## 13.6 — App Permissions & Row-Level Security

Apps respect the **RLS roles** you configured in Module 05. This means:

| User | RLS Role | What They See |
|---|---|---|
| Ground station operator (Perth) | `Station_Perth` | Only Perth station data |
| Mission lead (all stations) | `Mission_Lead` | All station data |
| Leadership | `Leadership` | Aggregated metrics, no PII |

> 💡 **Key insight:** You don't configure RLS *in the app* — it flows through from the semantic model. The app just packages and distributes; security is enforced at the data layer.

### Verify RLS in the App

1. Open the app as a test user (use **"View as" → specific user** in the report).
2. Confirm that data filters correctly based on the user's RLS role.
3. Confirm that OLS (Object-Level Security) hides sensitive columns as expected.

---

## 13.7 — Monitoring App Usage

Track how your apps are being consumed:

### Usage Metrics Report

1. In the workspace, find your published report → click **ellipsis (...)** → **View usage metrics report**.
2. Key metrics to track:

| Metric | What It Tells You |
|---|---|
| Report views per day | Adoption rate |
| Unique viewers | Reach |
| Most-viewed pages | What content is valuable |
| Performance (avg. load time) | User experience quality |

### Admin Portal — App Analytics

1. **Admin portal** → **Usage metrics** → filter by app name.
2. See total installs, active users, and engagement trends.

> 📚 **Learn more:** [Monitor usage metrics](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-usage-metrics)

---

## 13.8 — Challenge: Public Exoplanet Portal 🏆

**Scenario:** ZOSA wants a public-facing portal where anyone can explore confirmed exoplanets. Build it as a Fabric App with restricted access (no sensitive operational data).

### Requirements:

1. Create a **ZOSA-Public** workspace with only:
   - Exoplanet Explorer report (read-only, no RLS — all exoplanet data is public)
   - A custom landing page with ZOSA branding and educational content

2. Create an app from this workspace:
   - Audience: `ZOSA-PublicAccess` group (external users with guest access)
   - Navigation: Single-page, clean, no operational items

3. **Bonus:** Add a QR code link that opens the app directly on mobile devices.

> 💡 **Real-world note:** For truly public (unauthenticated) access, you'd use **Power BI Embedded** or **Publish to Web**. Fabric Apps require authentication, making them ideal for *authenticated external users* (B2B guest access via Entra ID).

---

## 13.9 — Checkpoint ✅

Verify your Fabric Apps setup:

| # | Check | Status |
|---|---|---|
| 1 | Mission Control app created and published | ⬜ |
| 2 | At least 2 audiences configured with different content visibility | ⬜ |
| 3 | Navigation organized into logical sections | ⬜ |
| 4 | Auto-install enabled (or documented why not) | ⬜ |
| 5 | RLS verified through the app experience | ⬜ |
| 6 | App usage metrics accessible | ⬜ |
| 7 | (Bonus) Public Exoplanet Portal app created | ⬜ |

---

## 🧠 Key Takeaways

| Concept | Summary |
|---|---|
| **Apps vs. Workspaces** | Workspaces are for builders; apps are for consumers |
| **Audiences** | Control which users see which content within the same app |
| **Security** | RLS/OLS flows through from the semantic model — apps don't override it |
| **Distribution** | Auto-install pushes apps to users; update propagates changes instantly |
| **Governance** | Combine with deployment pipelines for controlled promotion |

---

## 📚 Additional Resources

| Resource | Link |
|---|---|
| Create and publish apps | [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-create-distribute-apps) |
| App audiences | [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-create-distribute-apps#create-and-manage-multiple-audiences) |
| Push apps to users | [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-create-distribute-apps#automatically-install-apps-for-end-users) |
| Usage metrics | [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-usage-metrics) |

---

**Navigation:**
[← Module 12 — Monitoring & Optimization](12-monitoring-optimization.md)

[← Back to README](../README.md)
