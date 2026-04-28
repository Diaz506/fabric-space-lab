# Module 02 — Governance & Security

> Locking down space data with OneLake Security, Purview, and defense-in-depth

---

> **Sofia Lindqvist**, ZOSA's CISO, catches you in the hallway. *"Before a single byte of space data touches those workspaces, we need to lock them down. We handle asteroid threat data, crew personnel records, and classified mission details. I need defense-in-depth — not just one lock on the door, but locks on every drawer inside."*

You have three empty workspaces from Module 01. Before any data lands, you need to configure security at every layer. Let's build Sofia's defense-in-depth.

---

## 🛡️ 1 — The Defense-in-Depth Model

Fabric security isn't a single gate — it's a series of concentric walls. Each layer is **complementary**, not an alternative. If one layer is misconfigured, the others still protect you.

```
┌─────────────────────────────────────────────┐
│  TENANT                                     │
│  Admin settings, Conditional Access, MFA    │
│  ┌─────────────────────────────────────┐    │
│  │  WORKSPACE                          │    │
│  │  Roles: Admin, Member, Contributor, │    │
│  │         Viewer                      │    │
│  │  ┌─────────────────────────────┐    │    │
│  │  │  ITEM                       │    │    │
│  │  │  Per-item sharing &         │    │    │
│  │  │  permissions                │    │    │
│  │  │  ┌─────────────────────┐    │    │    │
│  │  │  │  DATA               │    │    │    │
│  │  │  │  RLS, CLS, OLS,    │    │    │    │
│  │  │  │  DDM (OneLake      │    │    │    │
│  │  │  │  Security)         │    │    │    │
│  │  │  └─────────────────────┘    │    │    │
│  │  └─────────────────────────────┘    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

| Layer | What It Controls | Configured Where |
|-------|-----------------|------------------|
| **Tenant** | Who can use Fabric at all, MFA, Conditional Access | Microsoft Entra admin center, Fabric Admin portal |
| **Workspace** | Who can access a workspace and what they can do | Workspace → Manage access |
| **Item** | Sharing individual reports, lakehouses, or pipelines | Item → Share / Manage permissions |
| **Data** | Row, column, object, and masking rules inside datasets | OneLake Security, T-SQL, Tabular Editor |

**💡 Tip:** Think of it like a building. Tenant security is the perimeter fence, workspace security is the building door, item security is the office door, and data security is the locked file cabinet inside the office.

---

## 👥 2 — Workspace Roles & Entra ID Security Groups

Instead of assigning permissions to individual users, you'll create **Entra ID security groups** and assign those groups to workspace roles. This is how real organizations manage access at scale.

### Step 1: Create Test Users

To properly validate security rules later, you need accounts that represent different personas. You'll create **2 test users** in addition to your admin account.

1. Navigate to [entra.microsoft.com](https://entra.microsoft.com)
2. Go to **Users** → **All users**
3. Click **New user** → **Create new user**
4. Create each user:

| Display Name | User Principal Name | Password | Purpose |
|-------------|---------------------|----------|---------|
| **ZOSA Scientist** | `zosa.scientist@{your-tenant}.onmicrosoft.com` | Set a temporary password | Tests restricted data views |
| **ZOSA Executive** | `zosa.executive@{your-tenant}.onmicrosoft.com` | Set a temporary password | Tests executive-level access |

5. Click **Create** for each user

### Step 1b: Assign Fabric Licenses (M365 Admin Center)

License assignments are managed in the **Microsoft 365 Admin Center**, not Entra ID.

1. Go to [admin.microsoft.com](https://admin.microsoft.com)
2. Navigate to **Users** → **Active users**
3. Select each test user → click **Licenses and apps**
4. Assign a **Microsoft Fabric (Free)** license (or your trial license)
5. Click **Save changes**

### Step 1c: First Sign-In

1. Open an **InPrivate / Incognito** browser window
2. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
3. Sign in as the test user and change the temporary password
4. Repeat for the second test user

> **💡 Tip:** Use separate browser profiles or InPrivate windows to test as different users. This avoids cached-auth confusion that can make security appear broken.

> **⚠️ Note:** Your admin account (the one you've been using) acts as the third persona — the admin/engineer with full access. No need to create a separate user for this.

### Step 2: Create Security Groups

1. In Entra, go to **Groups** → **All groups**
2. Click **New group**
3. Configure each group:
   - **Group type:** Security
   - **Group name:** (see table below)
   - **Group description:** (see table below)
   - **Microsoft Entra roles can be assigned to the group:** **No** (we use these for Fabric workspace roles, not Entra admin roles)
   - **Membership type:** Assigned
   - **Members:** Click "No members selected" and add the correct member (see table below)
4. Click **Create**

Create these four groups and assign the **correct members**:

| Group Name | Description | Members |
|------------|-------------|---------|
| `ZOSA-Admins` | Fabric administrators and platform owners | Your admin account |
| `ZOSA-Engineers` | Data engineers who build and maintain pipelines | Your admin account |
| `ZOSA-Scientists` | Data scientists and analysts who consume data | `zosa.scientist` test user |
| `ZOSA-Executives` | Executive stakeholders who view dashboards | `zosa.executive` test user |

**Why this separation matters:** Your admin account is in the builder groups (Admins + Engineers) so you can create and manage everything. The test users are in the consumer groups (Scientists + Executives) so you can validate that security rules actually restrict their access.

### Step 3: Assign Groups to Workspace Roles

Open each workspace → click **Manage access** → **Add people or groups** → search for the Entra group → assign the role.

| Group | ZOSA-Dev Role | ZOSA-Test Role | ZOSA-Prod Role |
|-------|---------------|----------------|----------------|
| ZOSA-Admins | Admin | Admin | Admin |
| ZOSA-Engineers | Member | Member | Contributor |
| ZOSA-Scientists | Contributor | Contributor | Viewer |
| ZOSA-Executives | Viewer | Viewer | Viewer |

Here's what each role can do:

| Permission | Admin | Member | Contributor | Viewer |
|-----------|-------|--------|-------------|--------|
| Manage workspace settings & access | ✅ | ❌ | ❌ | ❌ |
| Add/remove people | ✅ | ✅ | ❌ | ❌ |
| Create, edit, delete items | ✅ | ✅ | ✅ | ❌ |
| Read and view items | ✅ | ✅ | ✅ | ✅ |
| Share items & grant access | ✅ | ✅ | ❌ | ❌ |

**⚠️ Note:** Default to the **Viewer** role. Elevate only with justification. This is the principle of **least privilege** — give people the minimum access they need to do their job.

**💡 Tip:** Always assign roles via groups, never individuals. Groups scale, are auditable, and make offboarding instant — remove a user from the group and all their Fabric access disappears.

---

## 🏷️ 3 — Sensitivity Labels & Microsoft Purview

Sensitivity labels classify your data and enforce protection policies automatically. They travel with the data — if someone exports a report to PDF, the label (and its restrictions) follow.

### Step 1: Enable Sensitivity Labels in Fabric

1. Go to the **Fabric Admin portal** → **Tenant settings**
2. Under **Information protection**, enable:
   - ✅ *Allow users to apply sensitivity labels for content*
   - ✅ *Apply sensitivity labels from data sources to their data in Fabric*

### Step 2: Create Labels in Microsoft Purview

1. Navigate to [purview.microsoft.com](https://purview.microsoft.com) → **Information Protection** → **Sensitivity labels**
2. Click **+ Create a label** — this opens the **New sensitivity label** wizard

You'll create **4 labels**. Priority is determined by their **position in the label list** — the label at the top has the highest priority (wins when multiple labels could apply). After creating all 4, you'll reorder them.

Click **+ Create a label** — this opens the **New sensitivity label** wizard. The wizard has 5 steps:

---

#### 🔁 Repeat the wizard for each label below:

**A) Label details** (first page of the wizard)

| Field | Top Secret | Confidential | Internal | Public |
|-------|------------|--------------|----------|--------|
| **Name** | `TopSecret` | `Confidential` | `Internal` | `Public` |
| **Display name** | `Top Secret` | `Confidential` | `Internal` | `Public` |
| **Label priority** | Leave as default | Leave as default | Leave as default | Leave as default |
| **Description for users** | Classified mission data — maximum protection | Sensitive business data — restricted sharing | For internal ZOSA use only | Open data — no restrictions apply |
| **Description for admins** | Full encryption, no copy/paste/print, access audit | Encryption, block external sharing | Watermark on exports | No protection applied |

> **💡 About Priority:** The priority number you see is just the label's **position in the list**. In Purview, **the label at the bottom of the list has the highest priority** (it wins when multiple labels apply). After creating all 4 labels, you'll reorder them in Step 2E.
> 
> **💡 Tip:** The **Name** field cannot contain spaces (use `TopSecret` not `Top Secret`). The **Display name** is what users see and can have spaces.

**B) Scope** — Define where this label can be used:

| Label | Items (files, emails) | Groups & sites |
|-------|-----------------------|----------------|
| **Public** | ✅ Check | ✅ Check |
| **Internal** | ✅ Check | ✅ Check |
| **Confidential** | ✅ Check | ✅ Check |
| **Top Secret** | ✅ Check | ❌ Uncheck (applied at item level, not container) |

**C) Items** — "Choose protection settings for the types of items you selected":

This page shows two checkboxes. Check them based on the label:

| Label | ☐ Control access | ☐ Apply content marking |
|-------|-------------------|------------------------|
| **Public** | ❌ Leave unchecked | ❌ Leave unchecked |
| **Internal** | ❌ Leave unchecked | ✅ Check |
| **Confidential** | ✅ Check | ✅ Check |
| **Top Secret** | ✅ Check | ✅ Check |

**If you checked "Control access"** → the next page is **Access control**:

First, select the radio button: ◉ **Configure access control settings**

Then configure the dropdowns and permissions:

| Setting | Confidential | Top Secret |
|---------|-------------|------------|
| **Assign permissions now or let users decide?** | `Assign permissions now` | `Assign permissions now` |
| **User access to content expires** | `Never` | `Never` |
| **Allow offline access** | `Always` | `Never` (forces re-authentication) |
| **Assign permissions to specific users and groups** | Click **Assign permissions** → **Add all users in your organization** | Click **Assign permissions** → **Add all users in your organization** → then edit to remove **Copy** and **Print** rights |

**If you checked "Apply content marking"** → the next page is **Content marking**:

1. Toggle **Content marking** to **On**
2. Check the boxes and click **Customize text** to configure each:

| Label | ☐ Add a watermark | ☐ Add a header | ☐ Add a footer |
|-------|-------------------|----------------|----------------|
| **Internal** | ❌ | ❌ | ✅ Check → Customize text → `ZOSA Internal` |
| **Confidential** | ✅ Check → Customize text → `Confidential` | ✅ Check → Customize text → `ZOSA Confidential` | ❌ |
| **Top Secret** | ✅ Check → Customize text → `TOP SECRET` | ✅ Check → Customize text → `🔴 TOP SECRET — ZOSA CLASSIFIED` | ❌ |

> **💡 Info:** All content markings apply to documents. Only headers and footers apply to emails and meeting invites — watermarks do not appear in emails.

> **💡 Note:** For Public, since both checkboxes are unchecked, the wizard skips directly to the next step (no protection pages shown).

**D) Groups & sites** — "Define protection settings for groups and sites":

This page shows three checkboxes under **Protection settings** plus an **Auto apply settings** section:

| Label | ☐ Privacy and external user access | ☐ External sharing and Conditional Access | ☐ Private teams discoverability |
|-------|-------------------------------------|-------------------------------------------|-------------------------------|
| **Public** | ✅ Check | ❌ Leave unchecked | ❌ Leave unchecked |
| **Internal** | ✅ Check | ❌ Leave unchecked | ❌ Leave unchecked |
| **Confidential** | ✅ Check | ✅ Check | ❌ Leave unchecked |

**If you checked "Privacy and external user access"** → configure on the next page:

| Label | Privacy | External user access |
|-------|---------|---------------------|
| **Public** | **Public** — anyone in the org can access | ✅ Let group owners add external users |
| **Internal** | **Private** — only members can access | ❌ Don't let group owners add external users |
| **Confidential** | **Private** — only members can access | ❌ Don't let group owners add external users |

**If you checked "External sharing and Conditional Access"** → configure on the next page:

| Label | External sharing from SharePoint sites | Conditional Access |
|-------|----------------------------------------|-------------------|
| **Confidential** | Only people in your organization | Require MFA (if Conditional Access policies are configured) |

**Auto apply settings** → Leave the "Apply a label to channel meetings" dropdown as default for all labels.

> **💡 Note:** Top Secret has Groups & sites **unchecked in Scope** (Step B), so this page won't appear for that label.

**E) Finish** — Review the summary and click **Create label**

After creation, you'll see **"Your sensitivity label was created"** with two options:

- ○ Publish label to users' apps
- ◉ **Don't create a policy yet** ← Select this one!

> **⚠️ Select "Don't create a policy yet"** for each label. We'll publish all 4 labels together in a single policy in Step 3. Publishing them one at a time creates unnecessary duplicate policies.

Click **Done**, then repeat the wizard for the next label until all 4 are created.

After creating all 4 labels, **reorder them** in the labels list. In Purview, **bottom = highest priority** (the context menu confirms: "Move to bottom (highest priority)"). Arrange them so:

1. 🟢 **Public** (top — lowest priority)
2. 🔵 **Internal**
3. 🟠 **Confidential**
4. 🔴 **Top Secret** (bottom — highest priority)

> **💡 How to reorder:** Right-click a label → use **Move up / Move down** or **"Move to bottom (highest priority)"** to place Top Secret at the bottom.

---

### Step 3: Publish Labels with a Policy

Labels exist but aren't usable until you publish them:

1. In **Sensitivity labels**, click **Publish labels** (top toolbar)
2. Click **Choose sensitivity labels to publish** → select all 4 labels (Public, Internal, Confidential, Top Secret)
3. **Assign admin units** → Leave as default (Full directory)
4. **Publish to users and groups** → Add your ZOSA security groups:
   - `ZOSA-Admins`
   - `ZOSA-Engineers`
   - `ZOSA-Scientists`
   - `ZOSA-Executives`
5. **Policy settings**:
   - ✅ *Users must provide a justification to remove a label or lower its classification*
   - **Default label for documents**: `Internal`
   - **Default label for emails**: `Internal`
6. **Name your policy**: `ZOSA Sensitivity Policy`
7. Click **Submit**

> **⏳ Note:** Label policies can take **up to 24 hours** to propagate to all users. If labels don't appear immediately in Fabric, wait and check again later.

### Step 4: Apply Labels to Fabric Items

> **⚠️ Important:** Sensitivity labels in Fabric are applied to **individual items** (lakehouses, reports, datasets, notebooks, etc.) — not to workspaces. There is no workspace-level label setting in Fabric.

Labels will be applied as you create items throughout the lab. Here's the plan:

| Module | Item | Label to Apply |
|--------|------|---------------|
| **Module 03** | `zosa_lakehouse` (Lakehouse) | **Confidential** |
| **Module 05** | `ZOSA Semantic Model` | **Confidential** |
| **Module 06** | Power BI reports | **Confidential** |
| **Module 08** | ML experiments & models | **Top Secret** |

**How to apply a label to any Fabric item:**

1. Navigate to the item in your workspace
2. Click **… (More options)** next to the item name
3. Select **Sensitivity label** (or find it in the item's **Settings**)
4. Choose the appropriate label from the dropdown
5. Click **Apply**

> **💡 Tip:** If you set a default label in your publishing policy (we set `Internal`), new items will automatically get that label. You only need to manually change items that require a higher classification like **Confidential** or **Top Secret**.

**⚠️ Licensing Requirement — Read Before Proceeding:**

Sensitivity labels require specific Microsoft 365 licensing. Since January 2024, Microsoft **strictly enforces** these requirements — there is no grace period.

| Feature | Minimum License Required |
|---------|--------------------------|
| **Manual labeling** (apply labels to items) | Microsoft 365 **E3**, Business Premium, EMS E3/E5, or AIP **P1** |
| **Auto-labeling** (classify & label automatically) | Microsoft 365 **E5**, E5 Compliance add-on, or E5 Information Protection & Governance add-on |

For this lab, you need **at least E3 or AIP P1** to manually apply sensitivity labels. If your tenant only has F1/E1 licenses, you can **skip this section** and come back once you've upgraded — the rest of the lab does not depend on sensitivity labels.

> **Trial tenants:** If you're using a Microsoft 365 E5 trial, sensitivity labels are included. You can start a trial at [admin.microsoft.com](https://admin.microsoft.com) → **Billing** → **Purchase services** → search for "Microsoft 365 E5".

### Step 5: Configure Endorsement

Endorsement lets you mark trusted, validated datasets so users know which data to rely on:

1. Navigate to a dataset → **…** (more options) → **Settings** → **Endorsement**
2. Options:
   - **Promoted** — recommended by the data owner
   - **Certified** — validated and approved by a designated certifier (set in Admin portal)

**💡 Tip:** In later modules, once you build your Gold-layer datasets, you'll mark them as **Certified**. This tells analysts: "This is the single source of truth."

### Step 6: Enable Microsoft Purview Unified Catalog

#### 6a) Enable Admin API Settings (required before scanning)

Before Purview can scan your Fabric tenant, you must enable API access:

1. Go to [admin.powerbi.com](https://admin.powerbi.com) → **Tenant settings**
2. Search for and enable these settings under **Admin API settings**:
   - ✅ **Allow service principals to use Power BI APIs** → Apply to `ZOSA-Admins` group
   - ✅ **Allow service principals to access read-only admin APIs** → Apply to `ZOSA-Admins` group
   - ✅ **Enhance admin APIs responses with detailed metadata** → Enable for entire organization
3. **Wait ~15 minutes** for the settings to propagate

> **⚠️ Without these settings**, the scan will fail with error `3871 UserErrorDataScanPowerBIBasicMetadataFailure`. This is a common gotcha.

#### 6b) Register Fabric in Data Map

1. In [purview.microsoft.com](https://purview.microsoft.com), go to **Data Map** (left sidebar)
2. Click **Register** (or **+ Add Source**) → Select **Microsoft Fabric**
3. Configure the registration:
   - **Source name**: `ZOSA Fabric Tenant`
   - **Registration scope**: Select **Tenant** (scans all workspaces)
   - **Tenant ID**: Your Entra tenant GUID (find it in Entra ID → Overview)
4. Grant Purview permission to read Fabric metadata when prompted
5. Click **Save and Run** to start the initial scan
6. Once the scan completes, go to **Unified Catalog** to browse your discovered Fabric assets

This gives your organization a searchable inventory of every dataset, report, and lakehouse — with lineage tracking.

> **💡 Note:** The scan may take a few minutes depending on the number of items in your workspaces. You can set up a recurring schedule for automatic discovery of new items.

---

## 🔐 4 — OneLake Security (GA)

OneLake Security is the **unified data access control layer** for Microsoft Fabric. Once configured, permissions propagate to **all engines** — Spark notebooks, SQL analytics endpoints, Power BI semantic models, Dataflows, and even Copilot. You define rules once; they're enforced everywhere.

**⚠️ Note: OneLake Security, once enabled on a lakehouse, cannot be turned off. Plan your roles and rules carefully before flipping the switch.**

### Enabling OneLake Security

1. Open **ZOSA-Dev** workspace
2. Navigate to your Lakehouse (you'll create one in Module 03 — for now, understand the process)
3. Click **Manage OneLake Security**
4. Toggle **Enable OneLake Security** → Confirm

Once enabled, you'll see the role management interface where you can create roles with specific data access rules.

---

### 🔒 4a — Row-Level Security (RLS)

**Scenario:** ZOSA operates ground stations across the globe. Scientists at each station should only see observation data from **their region**. A European analyst shouldn't browse Asian station data.

#### How to Configure RLS

1. In the OneLake Security panel, click **New Role**
2. **Role name:** `Europe_Analysts`
3. Under **Table rules**, select the `observations` table
4. Add a filter expression:

```dax
[region] = "Europe"
```

5. Click **Save**
6. Assign the `ZOSA-Scientists` group (or a subset) to this role

Repeat for other regions:

| Role Name | Filter Expression |
|-----------|-------------------|
| `Europe_Analysts` | `[region] = "Europe"` |
| `NorthAmerica_Analysts` | `[region] = "North America"` |
| `Asia_Analysts` | `[region] = "Asia"` |
| `Global_Analysts` | *(no filter — sees all rows)* |

**How it works:** When a European analyst queries the `observations` table, Fabric automatically appends the filter. They literally cannot see rows outside their region — not in SQL, not in Spark, not in Power BI.

**💡 Tip:** For SQL analytics endpoints, the equivalent filter uses a `WHERE` clause injected at query time:

```sql
-- This is what Fabric does behind the scenes for Europe_Analysts
SELECT * FROM observations WHERE region = 'Europe'
```

---

### 🔒 4b — Column-Level Security (CLS)

**Scenario:** Budget data and crew security clearance levels are highly sensitive. Scientists and engineers need to work with mission and crew tables, but they should **never see** the `budget_usd` or `clearance_level` columns.

#### How to Configure CLS

Use the **SQL analytics endpoint** of your lakehouse and run T-SQL `DENY` statements:

```sql
-- Block scientists from seeing budget data
DENY SELECT ON dbo.missions(budget_usd) TO [ZOSA-Scientists];

-- Block scientists from seeing clearance levels
DENY SELECT ON dbo.crew(clearance_level) TO [ZOSA-Scientists];

-- Block engineers from seeing budget data (only execs need this)
DENY SELECT ON dbo.missions(budget_usd) TO [ZOSA-Engineers];
```

**What happens:** If a scientist runs `SELECT * FROM missions`, the `budget_usd` column is simply **not returned**. No error — the column is invisible. If they explicitly reference it (`SELECT budget_usd FROM missions`), they get a permission error.

**🧪 How to verify:** Sign in as `zosa.scientist` in an InPrivate browser → open the SQL analytics endpoint → run `SELECT * FROM missions` → the `budget_usd` column should not appear in the results.

---

### 🔒 4c — Object-Level Security (OLS)

**Scenario:** ZOSA has a `classified_defense_missions` table containing data about planetary defense operations. This table should be **completely invisible** to anyone without defense clearance.

#### How to Configure OLS

OLS is configured via the **Tabular Editor** (a free external tool) or the **XMLA endpoint**:

1. Download and install [Tabular Editor](https://tabulareditor.com/)
2. Connect to your Fabric semantic model via the XMLA endpoint
3. Navigate to the `classified_defense_missions` table
4. Set the **Object Level Security** property:
   - For the `ZOSA-Scientists` role: **None** (table is hidden)
   - For the `ZOSA-Engineers` role: **None** (table is hidden)
   - For the `ZOSA-Admins` role: **Read** (table is visible)
5. Save and publish the model

**What happens:** When a scientist opens the semantic model in Power BI, the `classified_defense_missions` table simply **doesn't appear** in the field list. They can't query it, they can't reference it, they don't even know it exists.

**💡 Tip:** OLS is the most restrictive data security layer — it hides entire tables or columns from the model itself. Use it for truly classified data that certain roles should have zero awareness of.

---

### 🔒 4d — Dynamic Data Masking (DDM)

**Scenario:** External analysts occasionally access crew data for scheduling purposes. They need to see that records exist, but crew email addresses and full names should be **partially masked**.

#### How to Configure DDM

Use T-SQL on the SQL analytics endpoint:

```sql
-- Mask email addresses (shows first letter and domain: j***@zosa.org)
ALTER TABLE crew
ALTER COLUMN email ADD MASKED WITH (FUNCTION = 'email()');

-- Partial mask on names (shows first and last character: S***a)
ALTER TABLE crew
ALTER COLUMN full_name ADD MASKED WITH (FUNCTION = 'partial(1,"***",1)');

-- Default mask on crew IDs (shows XXXX)
ALTER TABLE crew
ALTER COLUMN crew_id ADD MASKED WITH (FUNCTION = 'default()');
```

**What happens:** Users with `UNMASK` permission see the real data. Everyone else sees the masked version. An external analyst querying crew data would see:

| crew_id | full_name | email |
|---------|-----------|-------|
| XXXX | S***a | s***@zosa.org |
| XXXX | M***l | m***@zosa.org |

To grant unmasking to specific users:

```sql
-- Admins can see real data
GRANT UNMASK TO [ZOSA-Admins];
```

**🧪 How to verify:** Sign in as `zosa.scientist` in an InPrivate browser → open the SQL analytics endpoint → run `SELECT TOP 5 * FROM crew` → emails should appear as `s***@zosa.org`. Then sign in as your admin account → same query → real data appears.

**💡 Tip:** DDM is different from the other layers. It doesn't block access — it **obscures** the actual values. Use it for PII that needs to be present but not readable.

---

## 🧩 5 — Putting It All Together

Here's a summary of which security layer protects what at ZOSA:

| Data to Protect | Who's Blocked | Security Layer | Where Configured |
|----------------|---------------|----------------|------------------|
| Observation data by region | Scientists outside the region | **RLS** | OneLake Security roles |
| Budget amounts | Non-executive roles | **CLS** | T-SQL `DENY` on SQL endpoint |
| Classified missions table | Non-defense personnel | **OLS** | Tabular Editor / XMLA |
| Crew PII (email, name) | External analysts | **DDM** | T-SQL `ALTER COLUMN` masking |
| Workspace access | Unauthorized users | **Workspace Roles** | Workspace → Manage access |
| Data classification | Policy enforcement | **Sensitivity Labels** | Microsoft Purview |
| Data discovery & lineage | Shadow data sprawl | **Purview Unified Catalog** | purview.microsoft.com |

**Key takeaway:** No single layer does it all. Sofia wants defense-in-depth because **each layer covers a different threat vector**. Workspace roles stop unauthorized users from opening the door. RLS/CLS/OLS/DDM stop authorized users from seeing data beyond their need-to-know.

---

## ✅ Checkpoint

Verify you've completed the following:

- [ ] Created 2 test users in Entra ID (`zosa.scientist` and `zosa.executive`) and signed in once with each
- [ ] Created 4 Entra ID security groups (`ZOSA-Admins`, `ZOSA-Engineers`, `ZOSA-Scientists`, `ZOSA-Executives`)
- [ ] Assigned your admin account to `ZOSA-Admins` + `ZOSA-Engineers`, test users to `ZOSA-Scientists` + `ZOSA-Executives`
- [ ] Assigned groups to appropriate workspace roles in ZOSA-Dev, ZOSA-Test, and ZOSA-Prod
- [ ] Sensitivity labels configured and applied to workspaces (Confidential baseline)
- [ ] Endorsement process understood (Promoted vs. Certified)
- [ ] You understand the 4 data security layers: **RLS** (row filter), **CLS** (column deny), **OLS** (object hide), **DDM** (value mask)
- [ ] OneLake Security planning documented — you'll implement the data-level rules in Module 04 after data is loaded

### 🧪 How You'll Validate Security (Preview)

You've defined the rules — but how do you prove they work? Here's what you'll do once data exists (Modules 04–05):

| Security Layer | Validation Method |
|---------------|-------------------|
| **RLS** | Power BI → **Modeling** → **View as Role** → select `Europe_Analysts` and confirm only European data appears |
| **CLS** | Sign in as `zosa.scientist` in an InPrivate browser → open the SQL analytics endpoint → run `SELECT * FROM missions` → confirm `budget_usd` column is missing |
| **DDM** | Sign in as `zosa.scientist` → query `SELECT * FROM crew` → confirm emails show as `s***@zosa.org` |
| **OLS** | Sign in as `zosa.scientist` → open the Power BI semantic model → confirm `classified_defense_missions` table is not visible |

**⚠️ Note:** We've configured workspace roles and sensitivity labels now. The data-level security (RLS, CLS, OLS, DDM) will be **implemented** in Module 04 after you ingest data in Module 03. You can't secure tables that don't exist yet! For now, make sure you understand the concepts and have your plan ready.

---

> Sofia reviews your security plan and nods slowly. *"This is solid. Defense-in-depth, least privilege, everything auditable. I'll sign off on moving forward."* She pauses at the door. *"Oh, and one more thing — the first data drop from NASA arrives tomorrow. Don't let any of it land unencrypted."*
>
> You glance at your plan: data ingestion is next. Time to build the pipelines.

---

[← Module 01 — Capacity & Workspace Setup](01-capacity-and-workspace.md) | [Module 03 — Data Ingestion →](03-data-ingestion.md)

[← Back to README](../README.md)
