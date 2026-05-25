# 📊 Module 06 — Power BI Reports

> **Major Nakamura stood at the center of Mission Control, staring at the wall of blank monitors. "We have the data," she said. "We have the model. But my team is still opening spreadsheets to check mission status." She turned to her analyst. "I need a dashboard on that main screen — something that tells me what's happening *right now*. And the public affairs team? They want an Exoplanet Explorer for the website so the public can browse our discoveries." Two reports, one model. Time to build.**

---

## 🎯 Learning Objectives

By the end of this module, you will:

- Build a **multi-page Mission Control Dashboard** connected to the ZOSA Analytics Model
- Create an **interactive Exoplanet Explorer** report for public engagement
- Apply conditional formatting, bookmarks, tooltips, and slicers
- Design with a space-themed ZOSA color palette
- Publish reports to the ZOSA-Dev workspace and pin visuals to a shared dashboard

## 📋 Prerequisites

| Requirement | Details |
|---|---|
| **Module 05 complete** | ZOSA Analytics Model published with Direct Lake, measures, and RLS |
| **Workspace access** | Contributor or higher on **ZOSA-Dev** |

> 💡 **Tip:** You can build reports directly in the Fabric portal (from the semantic model → **Create report**) or use **Power BI Desktop** connected to the semantic model. This lab uses the web experience by default — no Desktop install required.

> 📚 **Learn more:** [Report Design Best Practices](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)

---

## 1️⃣ Report 1: Mission Control Dashboard

This is Major Nakamura's operational dashboard — the one going up on the big screen in Mission Control. It has three pages, each focused on a different domain.

### Connect to the Semantic Model

1. In the **Fabric portal**, navigate to your **ZOSA-Dev** workspace.
2. Find **ZOSA Analytics Model** → click the **ellipsis (...)** → select **Create report**.
3. A blank report canvas opens, connected to the semantic model. You should see all your Gold tables and measures in the **Data** pane on the right.

> 💡 **Tip:** Because you're connected to the published semantic model, the Direct Lake connection, relationships, and measures are already configured. No data import needed.
>
> **Alternatively**, if you prefer Power BI Desktop: open Desktop → **Home → Get data → Power BI semantic models** → select your workspace → choose **ZOSA Analytics Model** → **Connect**.

### Page 1: Executive Overview

This is the "at-a-glance" page — KPIs across the top, charts below.

#### KPI Cards

1. Create four **Card** visuals across the top of the canvas:

   | Card | Measure / Field | Format |
   |---|---|---|
   | Total Missions | `[Total Missions]` | Whole number |
   | Success Rate | `[Mission Success Rate]` | Percentage, 1 decimal |
   | Active Missions | `[Active Missions]` | Whole number |
   | Critical Asteroids | `[Critical Asteroids]` | Whole number, **red** callout color |

2. For each card:
   - Drag the measure to the canvas and select the **Card** visual type.
   - In **Format → Callout value**, set the font size to **28pt**.
   - For "Critical Asteroids," set the callout color to **red (#FF4444)**.

#### Mission Status Donut Chart

1. Add a **Donut chart** visual below the KPI cards (left side).
2. Configure:
   - **Legend:** `gold_mission_summary[status]`
   - **Values:** `[Total Missions]`
3. In **Format → Data colors**, assign:
   - Completed → Green (`#4CAF50`)
   - Active → Blue (`#2196F3`)
   - Failed → Red (`#F44336`)
   - Planned → Gold (`#FFC107`)

#### Budget by Mission Type (Bar Chart)

1. Add a **Clustered bar chart** (right side, next to the donut).
2. Configure:
   - **Y-axis:** `gold_mission_summary[mission_type]`
   - **X-axis:** `[Total Budget]`
3. Sort descending by Total Budget.
4. In **Format → Data colors**, use a gradient from navy (`#0D1B2A`) to gold (`#FFD700`).

#### Slicers

1. Add a **Date range slicer** at the top of the page:
   - Field: `gold_mission_summary[launch_date]`
   - Style: **Between** (date range picker)
2. Add a **Region dropdown slicer** next to it:
   - Field: `gold_mission_summary[region]`
   - Style: **Dropdown**

> ⚠️ **Important:** Place slicers consistently at the top of every page. Users expect filters in the same location across pages.

> 📚 **Official Documentation:**
> - [Visualizations Overview](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-report-visualizations)
> - [Card Visuals](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card)
> - [Slicers](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers)

### Page 2: Asteroid Threat Monitor

This is the page that keeps Major Nakamura up at night.

#### Threat Scatter Plot

1. Add a **Scatter chart** as the main visual (top half of the page).
2. Configure:
   - **X-axis:** `gold_asteroid_risk[miss_distance_km]`
   - **Y-axis:** `gold_asteroid_risk[relative_velocity_kph]`
   - **Size:** `gold_asteroid_risk[avg_diameter_m]`
   - **Legend (color):** `gold_asteroid_risk[risk_category]`
   - **Tooltips:** Add `gold_asteroid_risk[name]`, `gold_asteroid_risk[hazard_score]`
3. Apply conditional formatting on the legend:
   - Critical → Red (`#FF4444`)
   - High → Orange (`#FF9800`)
   - Medium → Yellow (`#FFC107`)
   - Low → Green (`#4CAF50`)

> 💡 **Tip:** Enable **zoom sliders** on both axes so analysts can zoom into the cluster of near-miss asteroids.

#### Top 10 Hazardous Asteroids Table

1. Add a **Table** visual (bottom-left).
2. Add columns:
   - `gold_asteroid_risk[name]`
   - `gold_asteroid_risk[avg_diameter_m]`
   - `gold_asteroid_risk[miss_distance_km]`
   - `gold_asteroid_risk[relative_velocity_kph]`
   - `gold_asteroid_risk[hazard_score]`
   - `gold_asteroid_risk[risk_category]`
3. Apply a **Top N filter** on the visual:
   - Filter on `hazard_score` → Top **10** → By value: `hazard_score`
4. Add **conditional formatting** on the `risk_category` column:
   - **Background color** → Rules:
     - If value is "Critical" → Red background, white text
     - If value is "High" → Orange background
     - If value is "Medium" → Yellow background
     - If value is "Low" → Green background

#### Hazard Score Card

1. Add a **Card** visual (bottom-right) showing `[Max Hazard Score]`.
2. Add conditional formatting:
   - If value > 20 → Red
   - If value > 10 → Orange
   - Otherwise → Green

> 📚 **Learn more:** [Conditional Formatting](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting)

### Page 3: Solar Activity Timeline

Space weather data for the science team.

#### Solar Events Over Time (Line Chart)

1. Add a **Line chart** (top half).
2. Configure:
   - **X-axis:** `gold_solar_activity[event_month]`
   - **Y-axis:** `gold_solar_activity[event_count]`
   - **Legend:** `gold_solar_activity[event_type]`
3. Set the X-axis to a continuous date axis (not categorical).

#### Severity Breakdown (Stacked Column Chart)

1. Add a **Stacked column chart** (bottom-left).
2. Configure:
   - **X-axis:** `gold_solar_activity[event_type]`
   - **Y-axis:** `gold_solar_activity[high_severity_count]`
   - Add `gold_solar_activity[low_severity_count]` as a second Y-axis value
3. Color the series:
   - high_severity_count → Red/Orange
   - low_severity_count → Green

#### Latest Events Table

1. Add a **Table** visual (bottom-right).
2. Columns: `event_month`, `event_type`, `event_count`, `avg_severity`, `max_severity`
3. Sort by `event_month` descending to show most recent first.
4. Optionally apply a **Top N** filter: Top 15 by `event_month`.

### Add Tooltips and Interactivity

1. **Cross-filtering:** Ensure all visuals on each page cross-filter each other (this is the default behavior).
2. **Tooltip pages:** Optionally create a tooltip page for asteroids:
   - New page → set **Page size** to **Tooltip** in Format pane.
   - Add a mini-card with asteroid name, diameter, velocity, and hazard score.
   - On the scatter chart, set **Tooltip → Page** to your tooltip page.
3. **Drillthrough:** Add a drillthrough page for individual mission details:
   - Create a new page with mission details (launch date, cost, crew, outcomes).
   - Add `gold_mission_summary[mission_id]` as a **drillthrough field**.
   - Right-click any mission in the donut chart → **Drillthrough** → Mission Detail.

> 💡 **Tip:** Custom tooltip pages are a great way to show contextual detail without cluttering the main visuals. Major Nakamura loves hovering over a dot and seeing the asteroid's full profile.

> 📚 **Learn more:** [Tooltips & Drill-through](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tooltips)

---

## 2️⃣ Report 2: Exoplanet Explorer

This is the public-facing report — designed for curiosity, not crisis. The public affairs team wants visitors to explore ZOSA's exoplanet catalog interactively.

### Create a New Report

1. Go back to the **ZOSA-Dev** workspace.
2. Find **ZOSA Analytics Model** → click the **ellipsis (...)** → select **Create report**.
3. A new blank report canvas opens, connected to the same model.

> 💡 **Alternatively in Power BI Desktop:** File → New → Get data → Power BI semantic models → select ZOSA Analytics Model.

### Exoplanet Scatter Plot

1. Add a **Scatter chart** as the centerpiece of the page.
2. Configure:
   - **X-axis:** `gold_exoplanet_catalog[orbital_period_days]` (consider log scale)
   - **Y-axis:** `gold_exoplanet_catalog[planet_mass_earth]`
   - **Legend (color):** `gold_exoplanet_catalog[discovery_method]`
   - **Tooltips:** `gold_exoplanet_catalog[planet_name]`, `gold_exoplanet_catalog[host_star]`, `gold_exoplanet_catalog[distance_ly]`, `gold_exoplanet_catalog[habitability_zone]`
3. Enable **zoom sliders** on both axes.
4. Set axis scaling to **Logarithmic** for orbital period (values span many orders of magnitude).

### Filter Panel

Add the following slicers in a vertical panel on the left side:

| Slicer | Field | Style |
|---|---|---|
| Habitable Zone | `gold_exoplanet_catalog[habitability_zone]` | **Toggle** (Yes/No buttons) |
| Discovery Year | `gold_exoplanet_catalog[discovery_year]` | **Between** (range slider) |
| Distance (ly) | `gold_exoplanet_catalog[distance_ly]` | **Between** (range slider) |
| Discovery Method | `gold_exoplanet_catalog[discovery_method]` | **Dropdown** (multi-select) |

> 💡 **Tip:** Group the slicers inside a **rectangle shape** with a subtle background (`#0D1B2A` at 80% transparency) to create a clean filter panel effect.

### Planet Detail Card

1. Add a **Multi-row card** visual on the right side.
2. Include fields:
   - `planet_name`, `host_star`, `discovery_method`, `discovery_year`
   - `planet_mass_earth`, `orbital_period_days`, `distance_ly`
   - `habitability_zone`, `planet_radius_earth`, `earth_similarity_index`
3. This card updates dynamically when you click a dot on the scatter plot.

### Bookmarks for Preset Views

Create two bookmarks so users can jump to curated views:

#### Bookmark 1: "Habitable Candidates"

1. Set the **Habitable Zone** slicer to **Yes**.
2. Optionally filter distance to < 100 light-years.
3. Go to **View → Bookmarks pane → Add bookmark**.
4. Name it **🌍 Habitable Candidates**.

#### Bookmark 2: "Recent Discoveries"

1. Set the **Discovery Year** slicer to the last 5 years.
2. Clear all other filters.
3. Add bookmark → Name it **🔭 Recent Discoveries**.

#### Add Bookmark Navigation Buttons

1. Go to **Insert → Buttons → Navigator → Bookmark navigator**, or add manual buttons:
   - Add two **Blank buttons** at the top of the page.
   - Label them "🌍 Habitable Candidates" and "🔭 Recent Discoveries".
   - In **Format → Action**, set type to **Bookmark** and select the corresponding bookmark.

> 💡 **Tip:** Bookmarks capture the state of all slicers, filters, and visual selections. They're like "saved searches" that let users explore without getting lost.

> 📚 **Learn more:** [Bookmarks](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-bookmarks)

---

## 3️⃣ Design Tips — The ZOSA Look

Both reports should feel like they belong in a space agency. Here's the ZOSA design system:

### Color Theme

| Role | Color | Hex |
|---|---|---|
| Background (primary) | Deep Space Navy | `#0D1B2A` |
| Background (secondary) | Dark Slate | `#1B2838` |
| Accent (primary) | ZOSA Gold | `#FFD700` |
| Accent (secondary) | Nebula Blue | `#2196F3` |
| Text (primary) | White | `#FFFFFF` |
| Text (secondary) | Silver | `#B0BEC5` |
| Alert / Critical | Red | `#FF4444` |
| Success | Green | `#4CAF50` |
| Warning | Orange | `#FF9800` |

#### Apply the Theme

1. Create a JSON theme file (`zosa-theme.json`):

   ```json
   {
     "name": "ZOSA Mission Control",
     "dataColors": [
       "#FFD700", "#2196F3", "#4CAF50", "#FF9800",
       "#FF4444", "#9C27B0", "#00BCD4", "#E91E63"
     ],
     "background": "#0D1B2A",
     "foreground": "#FFFFFF",
     "tableAccent": "#FFD700"
   }
   ```

2. In Power BI Desktop: **View → Themes → Browse for themes** → select your JSON file.

> 📚 **Learn more:** [Report Themes](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes)

### Typography

- **Titles:** Segoe UI Semibold, 14pt, White
- **Labels:** Segoe UI, 10pt, Silver (`#B0BEC5`)
- **KPI values:** Segoe UI Bold, 28pt, Gold (`#FFD700`)

### Mobile Layout

Field scientists need data on their tablets in remote locations.

1. Go to **View → Mobile layout**.
2. Drag the most critical visuals to the phone canvas:
   - **Page 1:** KPI cards + Mission Status donut
   - **Page 2:** Hazard Score card + Top 10 table
   - **Page 3:** Solar Events line chart
3. Resize visuals to fit the portrait aspect ratio.

> 💡 **Tip:** Mobile layouts are separate from the desktop layout — you can choose which visuals to show on mobile without affecting the desktop experience. Prioritize the "need-to-know" visuals for field use.

> 📚 **Learn more:** [Mobile-Optimized Reports](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-create-mobile-optimized-report-about)

---

## 4️⃣ Publish and Save

Since you built the reports directly in the Fabric portal, they're already saved in your workspace. If you used Power BI Desktop instead, publish here.

### If using Power BI Desktop

1. For each report, go to **File → Publish → Publish to Power BI**.
2. Select the **ZOSA-Dev** workspace.
3. Click **Select**. Wait for the upload to complete.

### Save in the Fabric Portal

1. Click the **Save** icon (💾) in the top-left corner.
2. Name the report (e.g., **Mission Control Dashboard** or **Exoplanet Explorer**).
3. Select the **ZOSA-Dev** workspace as the destination → **Save**.

### Verify in the Service

1. Open the **Fabric portal** → Navigate to **ZOSA-Dev** workspace.
2. Confirm you see:
   - **Mission Control Dashboard** (report)
   - **Exoplanet Explorer** (report)
   - Both reports should be connected to **ZOSA Analytics Model** (no duplicate datasets).

> ⚠️ **Important:** Because you connected to the *published semantic model*, no new dataset is created when you publish. Both reports share the same Direct Lake model — exactly as designed.

> 📚 **Learn more:** [Publishing Reports](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-upload-desktop-files)

### Pin to a Shared Dashboard

1. Open the **Mission Control Dashboard** report in the service.
2. Hover over the **Mission Success Rate** KPI card → click the **📌 Pin** icon.
3. Select **New dashboard** → Name it **ZOSA Mission Control**.
4. Pin additional visuals:
   - Mission Status donut chart
   - Critical Asteroids KPI card
   - Hazard Score card
   - Solar Events line chart
5. Arrange tiles on the dashboard by dragging and resizing.

> 💡 **Tip:** Dashboards are a *Power BI service* concept — they combine pinned visuals from multiple reports onto a single canvas. Think of them as a curated "highlights reel."

> 📚 **Learn more:** [Dashboards in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards)

---

## 5️⃣ Checkpoint

Time to verify everything works end-to-end.

### ✅ Verification Checklist

| # | Check | How to Verify | Expected Result |
|---|---|---|---|
| 1 | Mission Control Dashboard loads | Open report in the Fabric portal | All three pages render with data |
| 2 | Exoplanet Explorer loads | Open report in the Fabric portal | Scatter plot shows planets, slicers work |
| 3 | KPI cards show values | Check Executive Overview page | Non-zero values for all four KPIs |
| 4 | Slicers filter data | Change the date range slicer | All visuals update to reflect the filter |
| 5 | Cross-filtering works | Click a segment in the donut chart | Other visuals filter to that status |
| 6 | Conditional formatting | Look at the asteroid table | Critical rows highlighted in red |
| 7 | Bookmarks work | Click "🌍 Habitable Candidates" button | Filters reset to habitable zone = Yes |
| 8 | RLS filters data | Test as role from Security page (or log in as role member) | Data scoped to that role's region |
| 9 | Mobile layout | Preview mobile layout in Desktop | KPI cards and key visuals visible |
| 10 | Dashboard pins | Open ZOSA Mission Control dashboard | Pinned tiles show live data |

### Test RLS in the Service

1. Navigate to the semantic model → **ellipsis (...)** → **Security**.
2. Click the **ellipsis (...)** next to a role → **Test as role**.
3. Confirm that only the expected region's data appears.

> ⚠️ **Note:** "Test as role" does not work with Direct Lake models using SSO. If you see this error, verify the role definition is correct in **Manage roles** and test by logging in as the assigned user in a private browser window.

> 📚 **Learn more:** [RLS Testing in the Service](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security)

---

## 🎉 Module Complete!

> **Major Nakamura watched the Mission Control dashboard flicker to life on the main screen. Success rates, asteroid threats, solar activity — all in real time, all from one model. Down the hall, the public affairs team was already sharing the Exoplanet Explorer link on social media. "Beautiful," she murmured. Then her comm buzzed. "Major, we're getting live telemetry from the Artemis probe — velocity, temperature, radiation, streaming in every second. Can we get that on the dashboard too?" She smiled. "That's Module 07."**

---

## 🧭 Navigation

[← Module 05 — Semantic Model (Direct Lake)](05-semantic-model.md) | [Module 07 — Real-Time Intelligence →](07-real-time-intelligence.md)

[← Back to README](../README.md)
