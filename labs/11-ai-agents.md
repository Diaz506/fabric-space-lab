# Module 11 — AI Agents

> Ask in plain English, act automatically — Data Agents and Operations Agents bring natural language intelligence and autonomous workflows to your unified data estate.

| ⏱ Estimated time | 45 minutes |
|---|---|
| 🎯 Goal | Create a **Data Agent** (GA) for natural language Q&A and an **Operations Agent** (GA) for automated threat response — both grounded to the ontology you built in Module 10. |
| 📋 Prerequisites | Modules [08](08-real-time-intelligence.md), [09](09-data-science.md), and [10](10-ontology-knowledge-graph.md) completed. Gold lakehouse tables populated. ZOSA Knowledge Model ontology published. |

---

## 🎬 The Story So Far

> Major Nakamura, Director of Planetary Defense, corners you at lunch in the ZOSA cafeteria.
>
> *"I don't want to learn KQL. I don't want to write DAX. I want to ask: **Which asteroids are dangerous?** And when one IS dangerous, I want the system to **do something about it** — automatically."*
>
> You glance at Dr. Vasquez, who raises an eyebrow. You know the ontology is ready. The ML models are scoring risk in real time. The Activator is firing alerts. All the pieces are in place — you just need to put a conversational interface on top and wire up the automation.

---

## 📘 Part A — Data Agent (GA)

### 🤖 What Are Data Agents?

Data Agents provide **natural language Q&A** over your entire data estate. They were announced as GA at **FabCon Atlanta (March 2026)** and represent the evolution of what was previously called "AI Skills."

What makes Data Agents special:

- **Grounded to your ontology** — the agent doesn't just guess at table relationships. It operates on the shared business meaning you defined in Module 10. When someone asks about "dangerous asteroids," the agent *knows* that means `hazard_score > 100` because your ontology says so.
- **Not just ad-hoc SQL** — Data Agents understand business concepts, hierarchies, and relationships. They translate intent into precise queries across lakehouses, warehouses, and semantic models.
- **Security-aware** — every query respects Row-Level Security (RLS), Column-Level Security (CLS), and Object-Level Security (OLS). Users only see what they're authorized to see.

> 💡 **Key distinction:** Data Agents are the GA product name. You may see older references to "AI Skills" in documentation — they refer to the same capability, but **always use "Data Agent"** going forward.

> 📚 **Official Documentation:**
> - [Fabric data agent concept](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)
> - [Create a Fabric data agent (end-to-end tutorial)](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial)
> - [Fabric Copilot Overview](https://learn.microsoft.com/en-us/fabric/get-started/copilot-fabric-overview)

---

### 🆕 What's New (June 2026)

Data Agents have moved fast since the March 2026 GA. The most relevant recent additions:

- **Creator Agent (Preview)** — an AI assistant that *builds and refines your data agent for you* (schema exploration, few-shot generation, instructions). You'll try it in Step 2b below.
- **Mirrored databases as a source** — alongside lakehouses, warehouses, semantic models, KQL databases, and ontologies, you can now ground an agent on a **mirrored database**.
- **Service Principal authentication (Preview)** — agents can authenticate as a service principal (not just a signed-in user), enabling the automated, CI/CD-driven consumption you set up in [Module 12](12-ci-cd-deployment.md).
- **Microsoft 365 Copilot integration (GA)** — publish an agent so users can ask questions in **Teams and Excel**, not just the Fabric portal.
- **Observability via Microsoft Foundry (Preview)** — richer monitoring of agent performance and query behavior.
- **Purview DLP enforcement (GA)** — Data Loss Prevention policies can restrict what an agent returns, on top of RLS/CLS/OLS.
- **Response sizing** — agent answers are optimized for *conversational insights* (a capped number of rows/columns per request), not bulk data export.

---

### 🛠️ Step 1 — Create a Data Agent

1. Open your **ZOSA-Dev** workspace in the Fabric portal.

2. Click **+ New Item** → search for **"Fabric data agent"** → select it.

3. Name the agent: **`ZOSA Mission Intelligence`**.

4. After creation, the **OneLake catalog** opens automatically. Add your data sources (up to **5 total** — lakehouses, warehouses, semantic models, KQL databases, mirrored databases, or ontologies in any combination):
   - Select **ZOSA Knowledge Model** (the ontology from Module 10) → click **Add**
   - Select the **Gold Lakehouse** → click **Add**
   - Optionally add the **ZOSA semantic model** → click **Add**

> 📝 **Note:** Fabric data agents use a **Microsoft-managed Azure OpenAI** instance — you do not need to create or supply your own Azure OpenAI key or access token. Authentication is handled automatically under your Microsoft Entra ID identity.

> 📝 **Note:** Connecting the ontology is the critical step. Without it, the agent would rely on column names and basic metadata to interpret queries. With it, the agent has full context: business definitions, relationships, hierarchies, and validated business rules.

---

### 🎯 Step 2 — Configure Data Sources

Select which entities and tables the agent can query. You're giving it a "lens" into your data estate.

1. In the **Explorer** pane on the left side of the agent page, you'll see the data sources you added. Use the **checkboxes** next to each table to make tables available or unavailable to the AI.

2. Enable the following Gold lakehouse tables:

   | Table | Purpose |
   |---|---|
   | `gold_asteroid_risk` | Near-Earth object tracking with hazard scores and risk categories |
   | `gold_mission_summary` | Mission assignments, statuses, crew, and ground stations |
   | `gold_exoplanet_catalog` | Exoplanet discoveries with habitability scores |
   | `gold_solar_activity` | Solar flare events, intensity, and impact assessments |

3. To add more data sources later, click **+ Data source** in the Explorer pane — the OneLake catalog will reopen.

4. Review the **ontology mappings** — the agent should show which ontology entities map to which tables. Confirm the mappings look correct.

> 🔑 **Why this matters:** The ontology provides the semantic layer. When a user asks about "dangerous asteroids," the agent resolves this through the ontology:
> - "dangerous" → `risk_category IN ('Critical', 'High')` (from the ontology's business rule)
> - "asteroids" → `gold_asteroid_risk` table (from the entity mapping)
>
> Without the ontology, the agent would have to guess what "dangerous" means.

---

### 🧠 Step 2b — Build with AI: Creator Agent (Preview)

Manually writing agent instructions and example queries is tedious. The **Creator Agent** is a specialized AI assistant that does the heavy lifting for you — it explores your schema, learns from past query patterns, and generates the four configuration artifacts that drive answer quality:

| Configuration | What it controls |
|---|---|
| **Agent Instructions** | High-level rules for how the agent reasons and picks data sources |
| **Data Source Instructions** | How to use specific tables, columns, joins, and the data model |
| **Data Source Descriptions** | What each source contains and how it's organized |
| **Example Queries** | Natural-language questions paired with queries that capture business logic |

> ⚠️ **Preview scope:** Creator Agent currently supports **SQL and Eventhouse data sources only**. It won't appear for a lakehouse/ontology/semantic-model agent. To try it in ZOSA, attach a supported source — for example the **Eventhouse you built in [Module 08](08-real-time-intelligence.md)** or your lakehouse's **SQL analytics endpoint** — to a data agent, with the relevant tables selected.

**To launch it:** open your data agent and select **Build agent with AI** in the ribbon. This opens the Creator Agent chat. (**Test data agent** switches back to the normal test mode.)

**The recommended loop — Explore → Learn → Generate → Validate → Apply:**

1. **Explore** the schema:

   ```text
   Explore the schema and tell me which tables are relevant for asteroid threat reporting.
   ```

2. **Learn** from query history (when you have permission to view it):

   ```text
   Look at recent query patterns and suggest a few representative few-shot examples.
   ```

3. **Generate** instructions and examples:

   ```text
   Generate Data Source Instructions so the agent uses the correct join keys and date grain,
   and suggest five few-shots about hazardous asteroids and solar activity.
   ```

4. **Validate** with a read-only query:

   ```text
   Run a sample query to verify objects with miss_distance_au < 0.05 in the next 30 days.
   ```

5. **Apply** — review each suggestion and click **Accept** to apply it, then switch to **Test mode** to try sample questions.

> ⚠️ **Two things to know:** Creator Agent runs **read-only** queries only (data modifications are blocked), and accepting a suggestion **replaces** the corresponding configuration block during preview — so review changes before applying.

> 📚 **Official Documentation:**
> - [Creator agent for data agent (Preview)](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-creator-agent-overview)
> - [Configure Fabric data agent tenant settings](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings)

---

### 🧪 Step 3 — Test Natural Language Queries

Time to put the agent through its paces. The chat interface is **built directly into the agent page** — type your questions in the chat box and review the results.

#### Basic Lookups

```text
Which asteroids passed within 0.1 AU last month?
```

```text
Show me all missions assigned to the Tanegashima ground station.
```

```text
What was the strongest solar flare this year?
```

#### Aggregations

```text
How many habitable exoplanets have we discovered?
```

```text
What is our mission success rate by region?
```

#### Security-Scoped Queries

```text
List crew members with Top Secret clearance at European stations.
```

> ⚠️ **Expected behavior:** If your RLS rules from Module 07 are active, this last query should only return results for crew members the current user is authorized to see. Try testing with different user accounts to verify.

For each query, review:
- ✅ Did the agent return the correct results?
- ✅ Does the generated SQL/KQL make sense?
- ✅ Did it use the ontology definitions to resolve ambiguous terms?

---

### ⚙️ Step 4 — Fine-Tune Agent Behavior

You can improve accuracy by adding custom instructions and example Q&A pairs.

1. In the agent page, select the **Instructions** section (in the agent configuration area).

2. Add custom instructions:

   ```text
   When asked about "dangerous asteroids" or "threats," filter by 
   risk_category IN ('Critical', 'High').
   
   When asked about "habitable" exoplanets, use habitability_score > 0.7.
   
   Always include the asteroid name and discovery date in risk queries.
   
   When reporting mission success rates, exclude missions with status = 'Planned'.
   ```

3. Add **example Q&A pairs** for disambiguation:

   | User Question | Expected Behavior |
   |---|---|
   | "What's coming close?" | Query `gold_asteroid_risk` for objects with `miss_distance_au < 0.05` in the next 30 days |
   | "Any solar storms?" | Query `gold_solar_activity` for flares with `intensity_class IN ('X', 'M')` in the past 7 days |
   | "Station status" | Query `gold_mission_summary` grouped by `ground_station` showing active mission count |

> 📚 **Learn more:** [Creator agent for data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-creator-agent-overview) — use it to generate and refine these instructions and few-shot examples automatically.

---

### 🔗 Step 5 — Share the Agent

Data Agents are shared through **workspace permissions**. Users with access to the workspace can use the agent.

1. Ensure the appropriate teams have workspace roles:

   | Role | Access |
   |---|---|
   | ZOSA-Science team | Viewer or Contributor (can query the agent) |
   | ZOSA-Defense team | Viewer or Contributor (can query the agent) |
   | ZOSA-Admin team | Admin or Member (can configure the agent) |

2. The Data Agent **inherits all security layers** — RLS, CLS, and OLS rules apply automatically. You don't need to configure security separately for the agent.

3. **Take it beyond the portal (GA):** publish the agent into **Microsoft 365 Copilot** so Major Nakamura's team can ask questions directly in **Teams and Excel** — the same governed, permission-aware answers, delivered where they already work. For automated or CI/CD-driven consumption, authenticate the agent with a **service principal** (Preview) instead of a user identity.

> 💡 **Tip:** Share the agent URL with Major Nakamura's team. They can access it directly from the Fabric portal.

> 📚 **Official Documentation:**
> - [Copilot for Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/copilot)
> - [Copilot for Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/copilot-notebooks-overview)
> - [Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)

---

## ⚡ Part B — Operations Agent (GA)

> ✅ **Now Generally Available:** Operations Agents reached **GA in June 2026** (rolled out to all regions), graduating from the preview announced at Build/FabCon 2026. You may still see a residual "Preview" tag in older tenants until the GA build fully propagates.

### 🤖 What Are Operations Agents?

Operations Agents are **autonomous agents that interpret live signals, make decisions, and take action**. They don't just report — they *act*.

Think of the difference this way:
- **Data Agent:** "Which asteroids are dangerous?" → returns a table of results
- **Operations Agent:** A new dangerous asteroid is detected → *automatically* generates a threat brief, notifies the Defense team, and creates a mission proposal

Operations Agents are powered by the ontology and can chain multiple actions together in response to data events. In plain language you describe a goal; the agent **generates the monitoring rules** (grounded in your Fabric IQ ontology), **watches continuously** via Real-Time Intelligence, **investigates** anomalies, and **acts** — surfacing a recommendation or, with your authorization, running the fix itself.

### 🆕 What's New at GA (June 2026)

- **Chat-based creator that asks before it guesses** — setup is a conversation. For vague or compound goals like *"keep threat alerts reasonable across all stations,"* the agent asks clarifying questions instead of silently picking an interpretation, and lets you **preview the generated rules before you commit**.
- **Acts across Fabric** — beyond notifying, an authorized agent can **run Fabric pipelines**, **execute notebooks**, **invoke User Data Functions (UDFs)**, and **kick off Power Automate workflows**. Every action is **scoped, audited, and reversible** — the agent gets only the powers you grant.
- **Teams-native collaboration** — it posts insights and charts into your team's channel, with **recommended actions an authorized teammate can approve and trigger inline**.
- **Ask the agent in natural language** — *"What rules are you monitoring right now?"*, *"When did this rule last fire?"*, *"What values have increased?"* — sourced answers without opening a separate report.
- **Tracing & auditability** — new activity screens show which rule fired, on what data, what the agent reasoned, the action taken, and **who authorized it**.
- **Governed with the rest of your AI estate** — Operations Agents are now integrated with **Microsoft Agent 365 (A365)** and **Microsoft Entra ID**, so identity, access, and lifecycle are managed centrally alongside your other org agents.

> 📚 **Official Documentation:**
> - [Operations Agent](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/operations-agent)
> - [Data Activator / Reflex](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)

---

### 📐 Step 6 — Design the Automation

Before building, plan the workflow. When the ML model (Module 09) scores a new asteroid as **Critical**, or the Activator (Module 08) fires an alert, the Operations Agent should:

```
┌─────────────────────────────────────────────────────┐
│  TRIGGER: New row in gold_asteroid_risk              │
│           where risk_category = 'Critical'           │
├─────────────────────────────────────────────────────┤
│  ACTION 1: Generate threat assessment brief          │
│            (asteroid name, hazard_score,             │
│             miss_distance, estimated_impact_date)    │
├─────────────────────────────────────────────────────┤
│  ACTION 2: Send Teams notification                   │
│            to "ZOSA-Defense" channel                 │
│            with brief attached                       │
├─────────────────────────────────────────────────────┤
│  ACTION 3: Insert mission proposal                   │
│            into mission_proposals table              │
│            with status = 'Pending Review'            │
└─────────────────────────────────────────────────────┘
```

---

### 🛠️ Step 7 — Create the Operations Agent

> ⚠️ **Tenant Admin Requirement:** Before creating an Operations Agent, ensure your Fabric admin has enabled the **Operations Agent** feature, along with **Microsoft Copilot and Azure OpenAI** settings in the admin portal. Cross-geo processing and storage for AI may also need to be enabled if your capacity is outside US/EU regions.

1. On the Fabric home page, select the ellipsis (**...**) icon, then select **Create**.

2. In the **Create** pane, go to the **Real-Time Intelligence** section and select **Operations agent**.

3. Enter the name: **`ZOSA Threat Response`** and select the ZOSA-Dev workspace.

4. Click **Create**.

5. On the **Agent Setup** page, configure the following sections:

   **Business Goals:**
   ```text
   Monitor asteroid threat data in real-time. When a new critical-risk asteroid 
   is detected, generate a threat assessment, notify the Defense team, and 
   propose a mission response.
   ```

   **Instructions:**
   ```text
   Focus on rows in the asteroid risk data where risk_category = 'Critical'.
   When a critical asteroid is detected, recommend sending a threat brief to 
   the Defense team and creating a mission proposal.
   Always include asteroid name, hazard score, miss distance, and estimated 
   close approach date in threat assessments.
   ```

   **Knowledge Source:**
   - Select your **Eventhouse** (or **Ontology** if available) as the data source for the agent to monitor.

   **Actions:**
   Define the actions the agent can take. Each action has a name, description, and optional parameters:

   | Action Name | Description | Parameters |
   |---|---|---|
   | `Send Threat Brief` | Notify ZOSA-Defense channel with a threat assessment | `asteroid_name`, `hazard_score`, `miss_distance_au` |
   | `Create Mission Proposal` | Insert a mission proposal for review | `asteroid_name`, `priority`, `source_asteroid_id` |

6. **Configure each action** by selecting it and connecting it to an **Activator** item:
   - Select the workspace and Activator item
   - Click **Copy** to copy the connection string
   - Click **Open flow builder** to create a **Power Automate flow** that gets triggered by the action
   - Paste the connection string in the flow's **Connection string** field
   - Use **dynamic content** to pass action parameters into the flow (e.g., send a Teams message, insert a row)

   > 💡 **More action types (GA):** Beyond Power Automate flows, an authorized agent can also **run a Fabric pipeline** (e.g., refresh `gold_asteroid_risk`), **execute a notebook** (run remediation logic), or **invoke a User Data Function (UDF)** for a targeted, parameterized action. All actions are scoped, audited, and reversible.

7. Click **Save** to generate the agent's playbook. Review the playbook — it outlines the goals, instructions, data, and actions you defined.

8. When satisfied with the configuration, click **Start** in the toolbar to activate the agent.

### 📱 Step 7b — Install the Teams App

To receive proactive messages from the Operations Agent:

1. Open **Microsoft Teams** → go to the **Apps** store.
2. Search for **"Fabric Operations Agent"** and install the app.
3. Once installed, the agent can send messages in Teams when it identifies data matching your defined rules.
4. Messages include a summary of insights and recommended actions. Select **Yes** to approve or **No** to reject each recommendation directly in Teams.

---

### 🧪 Step 8 — Test End-to-End

Simulate a critical asteroid detection to verify the full workflow.

1. Open a **notebook** in your ZOSA-Dev workspace.

2. Insert a test row:

   ```python
   from pyspark.sql import Row
   from datetime import datetime, timedelta

   test_asteroid = Row(
       neo_reference_id="TEST-2029-XR7",
       name="2029 XR7",
       hazard_score=187.4,
       min_miss_distance_au=0.0023,
       risk_category="Critical",
       max_relative_velocity_kmps=28.7,
       avg_diameter_km=0.34,
       close_approach_count=1,
       is_potentially_hazardous=True
   )

   df = spark.createDataFrame([test_asteroid])
   df.write.mode("append").saveAsTable("gold_asteroid_risk")
   ```

3. **Watch the Operations Agent respond.** When the agent detects the new critical data:
   - ✅ You should receive a **Teams message** from the Fabric Operations Agent app with a threat assessment and recommended actions
   - ✅ Select **Yes** to approve the recommended action (e.g., sending a notification or creating a mission proposal)
   - ✅ The approved action triggers the connected Power Automate flow

4. Verify each step completed successfully in the agent's **Execution History**.

> ⚠️ **Cleanup:** After testing, remove the test row to avoid confusion:
> ```python
> spark.sql("DELETE FROM dbo.gold_asteroid_risk WHERE neo_reference_id = 'TEST-2029-XR7'")
> ```

---

### 📊 Step 9 — Monitor Agent Execution

1. Open the Operations Agent and go to the **Monitoring** tab.

2. Review:
   - **Execution history** — each trigger event and the actions taken
   - **Success/failure status** — per action in the chain
   - **Execution duration** — how long each action took
   - **Error details** — if any action failed, review the error message and stack trace

3. Set up **alerting on agent failures** — if the Operations Agent itself fails, you want to know immediately. Configure a secondary Activator alert on the agent's execution log.

4. **Ask the agent directly (GA).** Instead of digging through logs, query it in natural language: *"What rules are you monitoring right now?"*, *"When did the critical-asteroid rule last fire?"*, or *"What's changed in the threat data today?"* The agent returns a plain-language, sourced answer.

5. **Review the audit trail.** The tracing/activity screens show which rule fired, on which data, what the agent reasoned, the action it recommended or took, and **who authorized it** — the audit surface you need to run an autonomous agent in a governed defense environment.

---

## 🛡️ Agent Governance

Both Data Agents and Operations Agents include governance controls critical for a defense scenario like ZOSA.

### Audit Trails

Every interaction is logged:
- **Data Agent:** Each natural language query, the generated SQL/KQL, the results returned, and the user who asked
- **Operations Agent:** Each trigger event, every action executed, parameters passed, and outcomes

### Approval Workflows

Operations Agents use a **Teams-based approval model**. When the agent makes a recommendation, recipients receive a Teams message with context and suggested actions:

- Select **Yes** to approve the recommendation — the agent executes the action using the **creator's permissions** (delegated identity).
- Select **No** to reject the recommendation.
- You can adjust parameters before giving final approval.

> ⚠️ **Important:** The agent operates using the delegated identity and permissions of its creator. When a recipient approves a recommendation, the agent executes the action on behalf of the creator.

### Human-in-the-Loop Patterns

The Teams-based approval model provides human oversight:
- **Pre-action approval:** The agent sends a recommendation in Teams and waits for Yes/No before executing
- **Parameter review:** Recipients can adjust action parameters before approving
- **Escalation:** If the agent can't resolve ambiguity, it surfaces the issue for human review
- **Recipient management:** Update who receives agent messages via the **Agent behavior** settings

### Security Inheritance

Data Agents respect **all security layers** configured in your Fabric estate:
- Row-Level Security (RLS)
- Column-Level Security (CLS)
- Object-Level Security (OLS)
- Workspace roles and permissions

> 🔑 **This is critical for ZOSA:** When Major Nakamura queries the Data Agent, he sees defense-relevant data. When a scientist queries the same agent, they see science-relevant data. Same agent, same ontology, different views — all enforced automatically.

> 📚 **Official Documentation:**
> - [Semantic Link](https://learn.microsoft.com/en-us/fabric/data-science/semantic-link-overview)

---

## ✅ Checkpoint

Verify you've completed all key objectives:

- [ ] Data Agent `ZOSA Mission Intelligence` created and grounded to the ZOSA Knowledge Model ontology
- [ ] Natural language queries return accurate, ontology-informed results
- [ ] Custom instructions and example Q&A pairs configured for disambiguation
- [ ] Agent shared with appropriate teams, RLS verified with different user accounts
- [ ] Operations Agent `ZOSA Threat Response` configured with trigger on `gold_asteroid_risk`
- [ ] Three actions defined: generate report, send Teams notification, create mission proposal
- [ ] End-to-end test completed — simulated critical asteroid triggers full workflow
- [ ] Agent execution history shows all logged actions with success status
- [ ] Test data cleaned up

---

## 🎬 Story Closing

> Major Nakamura watches the Operations Agent fire in real-time after the simulated detection. A threat brief appears in the ZOSA-Defense Teams channel within seconds. The mission proposals table updates automatically.
>
> *"This,"* he says, tapping the screen, *"is why we migrated to Fabric."*
>
> Dr. Vasquez nods, but she's already thinking ahead. *"Now let's make sure this runs reliably in production. We need CI/CD pipelines, deployment gates, and a rollback plan. One workspace for dev, one for prod — no cowboy deployments."*
>
> You smile. That's Module 12.

---

## 🧭 Navigation

| Previous | Next |
|---|---|
| [← Module 10 — Ontology & Knowledge Graph](10-ontology-knowledge-graph.md) | [Module 12 — CI/CD & Deployment →](12-ci-cd-deployment.md) |

[← Back to README](../README.md)

