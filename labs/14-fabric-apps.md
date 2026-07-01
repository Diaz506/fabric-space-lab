# 🚀 Module 14 — Fabric Apps

> **The Director-General gathered her engineering leads. "Our dashboards tell the story. Our AI agents answer questions. But the ground station crews still copy data into spreadsheets to log maintenance tickets, and the public affairs team wants a web portal where journalists can explore our exoplanet catalog — not a Power BI report, a real *application*." She turned to you. "I heard Fabric can host full-stack apps now — TypeScript, APIs, databases, authentication — all managed. Build us a Crew Operations Portal. And if you can get a public Exoplanet Explorer web app running too? Even better."**

---

**Estimated time:** 60 minutes

---

## 🎯 Learning Objectives

By the end of this module, you will:

- Understand what **Fabric Apps (Preview)** are — a full-stack application platform inside Microsoft Fabric
- Install and use the **Rayfin CLI** to scaffold, develop, and deploy a Fabric App
- Define **TypeScript data models** with decorators that auto-generate SQL schemas and GraphQL APIs
- Implement **row-level authorization** using `@role` decorators
- Deploy a working web application with **Fabric SSO** authentication
- Build a **Crew Operations Portal** connected to ZOSA's Fabric data

## 📋 Prerequisites

| Requirement | Details |
|---|---|
| **Module 05 complete** | Gold layer tables available in the Lakehouse |
| **Workspace access** | Admin or Member on a Fabric-capacity workspace |
| **Tenant setting enabled** | Fabric Apps (Preview) workload enabled by your Fabric admin |
| **Node.js 18+** | Required for Rayfin CLI |
| **Docker Desktop** | Required for local development |

> ⚠️ **Preview notice:** Fabric Apps is in public preview. Features may change before GA.

> 📚 **Learn more:** [What is Fabric Apps?](https://learn.microsoft.com/en-us/fabric/apps/overview)

---

## 13.1 — Understanding Fabric Apps & Rayfin

### What Are Fabric Apps?

**Fabric Apps** is a platform for building and deploying **data-driven web applications** directly inside Microsoft Fabric. Unlike Power BI reports (which visualize data), Fabric Apps let you build custom **interactive applications** — forms, portals, tools — with a managed backend.

When you deploy a Fabric App, Fabric provisions and manages:

| Component | What It Provides |
|---|---|
| **SQL Database in Fabric** | A managed database with your schema (generated from TypeScript models) |
| **GraphQL API** | Auto-generated CRUD endpoints for your data models |
| **Authentication** | Fabric SSO via Microsoft Entra ID — no auth code needed |
| **Static Hosting** | Your frontend (HTML/CSS/JS) served from a public URL on OneLake storage |

### What Is Rayfin?

**Rayfin** is the open-source CLI and SDK for Fabric Apps. It handles:

- Project scaffolding from templates
- Local development with Docker (database + API + frontend)
- Schema generation from TypeScript decorators
- Deployment to Fabric (`rayfin up`)

Think of it as **`azd` (Azure Developer CLI) but for Fabric Apps**.

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Fabric App                          │
├──────────────────────────────────────────────────────┤
│  Static Frontend   │  GraphQL API  │  Auth Service   │
│  (HTML/CSS/JS)     │  /api/graphql │  /auth (SSO)    │
├──────────────────────────────────────────────────────┤
│              SQL Database in Fabric                   │
│         (schema from TypeScript models)              │
└──────────────────────────────────────────────────────┘
         ▲
         │  Deployed via: npx rayfin up
         │
┌────────┴─────────┐
│  Developer (You) │
│  rayfin.yml      │
│  /rayfin/data/   │ ← TypeScript data models
│  /app/           │ ← Frontend code
└──────────────────┘
```

### When to Use Fabric Apps vs. Other Options

| Scenario | Use |
|---|---|
| Custom web portal with forms, CRUD, and business logic | ✅ Fabric Apps |
| Dashboards and data visualization | ❌ Power BI Reports |
| AI agent with persistent state | ✅ Fabric Apps |
| Rapid internal tool / admin interface | ✅ Fabric Apps |
| Complex multi-service microarchitecture | ❌ Azure App Service / Container Apps |
| Public unauthenticated website | ❌ Static Web Apps |

---

## 13.2 — Enable Fabric Apps in Your Tenant

Before creating your first app, a Fabric admin must enable the workload:

1. Sign in to the [Fabric Admin Portal](https://app.fabric.microsoft.com/admin-portal).
2. Navigate to **Tenant settings**.
3. Search for **Fabric Apps (preview)**.
4. Toggle to **Enabled**.
5. Choose: entire organization or specific security groups.
6. Click **Apply** (changes propagate in a few minutes).

> 📝 **Note:** If you're on a Fabric trial, you may already have this enabled. Check by going to your workspace → **+ New item** and looking for **Fabric App**.

---

## 13.3 — Install Rayfin CLI & Scaffold the Project

### Install Prerequisites

```bash
# Verify Node.js 18+
node --version

# Verify Docker is running
docker --version
```

### Scaffold the ZOSA Crew Portal

```bash
# Create a new Fabric App project from a template
npm create @microsoft/rayfin@latest

# When prompted:
#   Project name: zosa-crew-portal
#   Template: default (or blank)
```

This generates the project structure:

```
zosa-crew-portal/
├── rayfin.yml              ← Project configuration
├── rayfin/
│   └── data/
│       └── models.ts       ← TypeScript data models (your schema)
├── app/                    ← Frontend application code
│   ├── index.html
│   ├── src/
│   └── package.json
├── package.json
└── node_modules/
```

### Understand `rayfin.yml`

```yaml
name: zosa-crew-portal
workspace: ZOSA-Dev           # Target Fabric workspace
```

This file tells Rayfin where to deploy and how to configure the app.

---

## 13.4 — Define Data Models

The heart of a Fabric App is its **TypeScript data models**. You decorate classes with Rayfin decorators, and the CLI generates:
- SQL database tables
- GraphQL queries and mutations
- Row-level authorization rules

### ZOSA Crew Operations Model

Edit `rayfin/data/models.ts`:

```typescript
import {
  entity,
  role,
  text,
  boolean,
  date,
  uuid,
  int,
  relation,
} from '@microsoft/rayfin-core';

// --- Crew Members ---
@entity()
@role('authenticated', 'read')  // Any authenticated user can read
@role('authenticated', 'create', {
  policy: (claims) => claims.roles.includes('ops_admin'),
})
export class CrewMember {
  @uuid() id!: string;
  @text({ min: 1, max: 100 }) fullName!: string;
  @text() role!: string;          // Commander, Pilot, Specialist, Engineer
  @text() specialty!: string;
  @text() clearanceLevel!: string; // L1, L2, L3, L4, L5
  @text() homeStation!: string;
  @boolean() isActive!: boolean;
  @date() assignedDate!: Date;
}

// --- Maintenance Tickets ---
@entity()
@role('authenticated', 'read')
@role('authenticated', 'create')  // Any crew can create tickets
@role('authenticated', 'update', {
  policy: (claims, item) => 
    claims.sub === item.assignedTo || claims.roles.includes('ops_admin'),
})
export class MaintenanceTicket {
  @uuid() id!: string;
  @text({ min: 1, max: 200 }) title!: string;
  @text({ max: 2000 }) description!: string;
  @text() priority!: string;       // Critical, High, Medium, Low
  @text() status!: string;         // Open, InProgress, Resolved, Closed
  @text() groundStation!: string;
  @text() assignedTo!: string;     // crew member ID
  @text() createdBy!: string;      // user ID from auth
  @date() createdAt!: Date;
  @date({ optional: true }) resolvedAt?: Date;
}

// --- Mission Log Entries ---
@entity()
@role('authenticated', 'read')
@role('authenticated', 'create', {
  policy: (claims) => claims.roles.includes('mission_lead'),
})
export class MissionLogEntry {
  @uuid() id!: string;
  @text() missionId!: string;
  @text({ min: 1, max: 500 }) entry!: string;
  @text() logType!: string;        // Status, Anomaly, Milestone, Note
  @text() author!: string;
  @date() timestamp!: Date;
}
```

### What the Decorators Do

| Decorator | Purpose |
|---|---|
| `@entity()` | Marks a class as a database table + GraphQL type |
| `@uuid()` | Auto-generated unique ID column |
| `@text({ min, max })` | String column with validation |
| `@boolean()` | Boolean column |
| `@date()` | Timestamp column |
| `@int()` | Integer column |
| `@role(audience, action, options)` | Row-level authorization rule |

### Understanding `@role` Policies

The `@role` decorator controls **who can do what**:

```typescript
// Anyone authenticated can read
@role('authenticated', 'read')

// Only ops_admin role can create
@role('authenticated', 'create', {
  policy: (claims) => claims.roles.includes('ops_admin'),
})

// Only the assigned user or admins can update
@role('authenticated', 'update', {
  policy: (claims, item) => claims.sub === item.assignedTo || claims.roles.includes('ops_admin'),
})
```

This generates **row-level security** enforced at the API layer — no manual SQL policies needed.

---

## 13.5 — Local Development

Run the full stack locally before deploying to Fabric:

```bash
cd zosa-crew-portal

# Install dependencies
npm install

# Start local dev environment (spins up Docker containers)
npx rayfin dev
```

This starts:
- A local SQL database (Docker container)
- A local GraphQL API server
- Your frontend with hot-reload
- A local auth simulator (email/password for testing)

### Test the GraphQL API

Open `http://localhost:4000/api/graphql` in your browser to access the GraphQL playground.

**Create a crew member:**

```graphql
mutation {
  createCrewMember(input: {
    fullName: "Elena Vasquez"
    role: "Commander"
    specialty: "Deep Space Navigation"
    clearanceLevel: "L5"
    homeStation: "Houston"
    isActive: true
    assignedDate: "2026-01-15"
  }) {
    id
    fullName
    role
  }
}
```

**Query all crew:**

```graphql
query {
  crewMembers {
    id
    fullName
    role
    homeStation
    isActive
  }
}
```

**Create a maintenance ticket:**

```graphql
mutation {
  createMaintenanceTicket(input: {
    title: "Antenna array misalignment - Dish 3"
    description: "Tracking accuracy degraded by 0.3 arcsec. Needs recalibration."
    priority: "High"
    status: "Open"
    groundStation: "Perth"
    assignedTo: "elena-vasquez-id"
    createdBy: "current-user-id"
    createdAt: "2026-06-11T10:00:00Z"
  }) {
    id
    title
    status
  }
}
```

> 💡 **Tip:** The GraphQL playground gives you autocomplete and schema docs — explore the auto-generated queries and mutations.

---

## 13.6 — Build the Frontend

The `app/` folder contains your frontend. You can use any framework (React, Vue, Svelte, vanilla JS). The scaffold provides a starter.

### Using the Rayfin Client SDK

The **RayfinClient** provides type-safe access to your GraphQL API:

```typescript
// app/src/main.ts
import { RayfinClient } from '@microsoft/rayfin-client';

const client = new RayfinClient();

// Fetch all open tickets
async function loadTickets() {
  const tickets = await client.maintenanceTickets.findMany({
    where: { status: 'Open' },
    orderBy: { createdAt: 'desc' },
  });
  
  renderTickets(tickets);
}

// Create a new ticket
async function submitTicket(form: FormData) {
  const ticket = await client.maintenanceTickets.create({
    title: form.get('title') as string,
    description: form.get('description') as string,
    priority: form.get('priority') as string,
    status: 'Open',
    groundStation: form.get('station') as string,
    assignedTo: form.get('assignee') as string,
    createdBy: client.auth.currentUser.id,
    createdAt: new Date(),
  });
  
  console.log('Ticket created:', ticket.id);
}
```

### Build a Simple Crew Portal UI

Your frontend could include:

| Page | Purpose |
|---|---|
| **Dashboard** | Open tickets by station, priority breakdown |
| **Crew Directory** | List active crew, search by station/role |
| **Submit Ticket** | Form to create maintenance tickets |
| **Mission Log** | Timeline of mission log entries |

> 💡 **Tip:** Since the GraphQL API handles all data operations and auth, your frontend is purely UI logic — no backend code to write.

---

## 13.7 — Deploy to Fabric

When you're ready to go live:

```bash
# Authenticate with Fabric
npx rayfin login

# Deploy everything to your Fabric workspace
npx rayfin up
```

`rayfin up` does the following:

1. Creates a **Fabric App** item in your workspace (if it doesn't exist)
2. Provisions a **SQL Database in Fabric** with your schema
3. Deploys your **GraphQL API** endpoints
4. Uploads your **static frontend** to OneLake hosting
5. Configures **Fabric SSO** (Microsoft Entra ID)

### After Deployment

Your app is live at:

```
https://zosa-crew-portal-app.rayfin.windows.net/
```

| Endpoint | Purpose |
|---|---|
| `/` | Your frontend (static hosting) |
| `/api/graphql` | Data API (GraphQL) |
| `/auth` | Authentication service (Fabric SSO) |
| `/storage` | File storage |

### Verify in the Fabric Portal

1. Navigate to your workspace in the Fabric portal.
2. You'll see a new **Fabric App** item: `zosa-crew-portal`.
3. Click it to see child items:
   - **SQL Database** — view tables, run queries
   - **Authentication** — see authenticated users
   - **Static Content** — hosting URL

---

## 13.8 — Schema Updates & Iteration

As ZOSA's needs evolve, update your models and redeploy:

### Add a New Field

```typescript
// Add urgency escalation tracking to tickets
export class MaintenanceTicket {
  // ... existing fields ...
  @boolean() escalated!: boolean;
  @date({ optional: true }) escalatedAt?: Date;
  @text({ optional: true }) escalatedTo?: string;
}
```

### Apply Changes

```bash
# Apply schema migration
npx rayfin up db apply
```

Rayfin generates and runs the SQL migration automatically. The GraphQL API updates to expose the new fields.

> ⚠️ **Important:** Schema changes should always be made in code (TypeScript models), not directly in the SQL Database in the portal. Direct DB changes can cause conflicts on the next `rayfin up`.

---

## 13.9 — Permissions & Sharing

### Item Permissions

| Permission | What It Allows |
|---|---|
| **Run and interact** | Open and use the app (default for workspace members) |
| **Edit (Write)** | Deploy code via `rayfin up`, modify settings |
| **Reshare** | Grant other users access (requires workspace Admin) |

### Share the App

To give ZOSA ground station crews access:

1. In the Fabric portal, select the **Fabric App** item.
2. Click **Share** → add users or security groups.
3. Assign **Run and interact** permission.
4. Users sign in with their Microsoft Entra ID credentials — Fabric SSO handles everything.

> 💡 **Key insight:** Authentication is *built in*. You never write login/logout code. Every user who accesses the app URL is authenticated via Fabric SSO automatically.

---

## 13.10 — Challenge: Exoplanet Explorer Web App 🏆

**Scenario:** Build a second Fabric App — an interactive Exoplanet Explorer for ZOSA's public affairs team to share with journalists (authenticated via guest access).

### Requirements:

1. **Data model:**
   ```typescript
   @entity()
   @role('authenticated', 'read')  // Read-only for all authenticated users
   export class Exoplanet {
     @uuid() id!: string;
     @text() planetName!: string;
     @text() hostStar!: string;
     @text() discoveryMethod!: string;
     @text() habitabilityZone!: string;
     @int() distanceLightYears!: number;
     @int() earthSimilarityIndex!: number;
   }
   ```

2. **Frontend:** A searchable, filterable catalog with cards showing planet details.

3. **Data population:** Seed from your Gold layer exoplanet data (export → import via GraphQL mutations or direct SQL insert).

4. **Deploy** as a separate Fabric App in a `ZOSA-Public` workspace.

> 💡 **Bonus:** Use the Rayfin client SDK to add interactive features — let users "favorite" exoplanets (add a `Favorite` entity with a user-to-planet relation).

---

## 13.11 — Checkpoint ✅

Verify your Fabric Apps setup:

| # | Check | Status |
|---|---|---|
| 1 | Rayfin CLI installed and authenticated | ⬜ |
| 2 | TypeScript data models defined with decorators | ⬜ |
| 3 | Local dev environment running (Docker + GraphQL playground) | ⬜ |
| 4 | CRUD operations tested via GraphQL | ⬜ |
| 5 | Frontend connects to API via RayfinClient | ⬜ |
| 6 | App deployed to Fabric (`rayfin up` successful) | ⬜ |
| 7 | Fabric SSO authentication working | ⬜ |
| 8 | App shared with team (Run and interact permission) | ⬜ |
| 9 | (Bonus) Exoplanet Explorer web app deployed | ⬜ |

---

## 🧠 Key Takeaways

| Concept | Summary |
|---|---|
| **Fabric Apps ≠ Power BI Apps** | Fabric Apps are full-stack web applications; Power BI Apps distribute reports |
| **Rayfin CLI** | Scaffolds, develops locally, and deploys Fabric Apps |
| **TypeScript → Everything** | Data models generate SQL schemas, GraphQL APIs, and auth rules |
| **Managed infrastructure** | Fabric handles hosting, database, networking, and scaling |
| **Fabric SSO** | Authentication is built in via Microsoft Entra ID — no auth code required |
| **Schema-first development** | Change models in code → `rayfin up` → database migrates automatically |

---

## 📚 Additional Resources

| Resource | Link |
|---|---|
| Fabric Apps overview | [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/apps/overview) |
| Rayfin CLI reference | [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/apps/cli-reference) |
| Data model decorators | [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/apps/data-models) |
| Fabric Apps permissions | [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/apps/permissions) |
| Local development guide | [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/apps/local-development) |

---

**Navigation:**
[← Module 13 — Monitoring & Optimization](13-monitoring-optimization.md)

[← Back to README](../README.md)
