# Module 10 — AI Agents

> Ask in plain English, act automatically — Data Agents and Operations Agents bring natural language intelligence and autonomous workflows to your unified data estate.

| ⏱ Estimated time | 45 minutes |
|---|---|
| 🎯 Goal | Create a **Data Agent** (GA) for natural language Q&A and an **Operations Agent** (Preview) for automated threat response — both grounded to the ontology you built in Module 09. |
| 📋 Prerequisites | Modules [07](07-activator-alerts.md), [08](08-data-science.md), and [09](09-ontology-knowledge-graph.md) completed. Gold lakehouse tables populated. ZOSA Knowledge Model ontology published. |

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

- **Grounded to your ontology** — the agent doesn't just guess at table relationships. It operates on the shared business meaning you defined in Module 09. When someone asks about "dangerous asteroids," the agent *knows* that means `hazard_score > 100` because your ontology says so.
- **Not just ad-hoc SQL** — Data Agents understand business concepts, hierarchies, and relationships. They translate intent into precise queries across lakehouses, warehouses, and semantic models.
- **Security-aware** — every query respects Row-Level Security (RLS), Column-Level Security (CLS), and Object-Level Security (OLS). Users only see what they're authorized to see.

> 💡 **Key distinction:** Data Agents are the GA product name. You may see older references to "AI Skills" in documentation — they refer to the same capability, but **always use "Data Agent"** going forward.

> 📚 **Official Documentation:**
> - [AI Skills Overview](https://learn.microsoft.com/en-us/fabric/data-science/concept-ai-skill)
> - [Create an AI Skill](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-ai-skill)
> - [Fabric Copilot Overview](https://learn.microsoft.com/en-us/fabric/get-started/copilot-fabric-overview)

---

### 🛠️ Step 1 — Create a Data Agent

1. Open your **ZOSA-Dev** workspace in the Fabric portal.

2. Click **+ New** → **Data Agent**.

3. Configure the agent:

   | Setting | Value |
   |---|---|
   | **Name** | `ZOSA Mission Intelligence` |
   | **Description** | Natural language Q&A for ZOSA mission data, asteroid risk, and exoplanet catalog |

4. On the **Grounding** tab, connect the agent to your data sources:
   - Select **ZOSA Knowledge Model** (the ontology from Module 09)
   - Add grounding sources:
     - ✅ Gold Lakehouse tables
     - ✅ ZOSA semantic model

5. Click **Create**.

> 📝 **Note:** Connecting the ontology is the critical step. Without it, the agent would rely on column names and basic metadata to interpret queries. With it, the agent has full context: business definitions, relationships, hierarchies, and validated business rules.

---

### 🎯 Step 2 — Configure Grounding Sources

Select which entities and tables the agent can query. You're giving it a "lens" into your data estate.

1. In the agent configuration, go to **Grounding → Select Tables**.

2. Enable the following Gold lakehouse tables:

   | Table | Purpose |
   |---|---|
   | `gold_asteroid_risk` | Near-Earth object tracking with hazard scores and risk categories |
   | `gold_mission_summary` | Mission assignments, statuses, crew, and ground stations |
   | `gold_exoplanet_catalog` | Exoplanet discoveries with habitability scores |
   | `gold_solar_activity` | Solar flare events, intensity, and impact assessments |

3. Review the **ontology mappings** — the agent should show which ontology entities map to which tables. Confirm the mappings look correct.

> 🔑 **Why this matters:** The ontology provides the semantic layer. When a user asks about "dangerous asteroids," the agent resolves this through the ontology:
> - "dangerous" → `risk_category IN ('Critical', 'High')` (from the ontology's business rule)
> - "asteroids" → `gold_asteroid_risk` table (from the entity mapping)
>
> Without the ontology, the agent would have to guess what "dangerous" means.

---

### 🧪 Step 3 — Test Natural Language Queries

Time to put the agent through its paces. Open the **Test** panel and try these queries:

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

> ⚠️ **Expected behavior:** If your RLS rules from Module 06 are active, this last query should only return results for crew members the current user is authorized to see. Try testing with different user accounts to verify.

For each query, review:
- ✅ Did the agent return the correct results?
- ✅ Does the generated SQL/KQL make sense?
- ✅ Did it use the ontology definitions to resolve ambiguous terms?

---

### ⚙️ Step 4 — Fine-Tune Agent Behavior

You can improve accuracy by adding custom instructions and example Q&A pairs.

1. Go to **Agent Settings → Instructions**.

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

4. Under **Response Settings**, configure:
   - **Show generated SQL/KQL:** ✅ Yes (transparency for technical users)
   - **Include confidence score:** ✅ Yes
   - **Max results per query:** 50

> 📚 **Learn more:** [AI Skill Instructions](https://learn.microsoft.com/en-us/fabric/data-science/ai-skill-instructions)

---

### 🔗 Step 5 — Share the Agent

1. Go to **Manage Access** on the Data Agent.

2. Assign permissions:

   | Role | Access |
   |---|---|
   | ZOSA-Science team | Can use the agent (query) |
   | ZOSA-Defense team | Can use the agent (query) |
   | ZOSA-Admin team | Can use and configure the agent |

3. The Data Agent **inherits all security layers** — RLS, CLS, and OLS rules apply automatically. You don't need to configure security separately for the agent.

> 💡 **Tip:** Share the agent URL with Major Nakamura's team. They can access it directly from the Fabric portal or embed it in a Power BI report for inline Q&A.

> 📚 **Official Documentation:**
> - [Copilot for Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/copilot)
> - [Copilot for Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/copilot-notebooks-overview)
> - [Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)

---

## ⚡ Part B — Operations Agent (Preview)

> ⚠️ **Preview Notice:** Operations Agents are currently in **Preview**. Features, APIs, and UX may change before General Availability. Do not use for production-critical automation without a fallback plan.

### 🤖 What Are Operations Agents?

Operations Agents are **autonomous agents that interpret live signals, make decisions, and take action**. They don't just report — they *act*.

Think of the difference this way:
- **Data Agent:** "Which asteroids are dangerous?" → returns a table of results
- **Operations Agent:** A new dangerous asteroid is detected → *automatically* generates a threat brief, notifies the Defense team, and creates a mission proposal

Operations Agents are powered by the ontology and can chain multiple actions together in response to data events.

> 📚 **Official Documentation:**
> - [Data Activator / Reflex](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)
> - [Azure OpenAI in Fabric](https://learn.microsoft.com/en-us/fabric/data-science/ai-services/how-to-use-openai-sdk-synapse)

---

### 📐 Step 6 — Design the Automation

Before building, plan the workflow. When the ML model (Module 08) scores a new asteroid as **Critical**, or the Activator (Module 07) fires an alert, the Operations Agent should:

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

1. Open your **ZOSA-Dev** workspace.

2. Click **+ New** → **Operations Agent**.

3. Configure:

   | Setting | Value |
   |---|---|
   | **Name** | `ZOSA Threat Response` |
   | **Description** | Automated threat response for critical asteroid detections |

4. **Configure the Trigger:**
   - Trigger type: **Data change**
   - Source table: `gold_asteroid_risk`
   - Condition: `risk_category = 'Critical'`
   - Evaluation: On new rows

5. **Define Action 1 — Generate Report:**
   - Action type: **Generate content**
   - Template: Threat assessment brief (markdown format)
   - Parameters (dynamically bound to the triggering event):
     - `{{asteroid_name}}` — from the new row
     - `{{hazard_score}}` — from the new row
     - `{{miss_distance_au}}` — from the new row
     - `{{estimated_close_approach}}` — from the new row
     - `{{risk_category}}` — from the new row

6. **Define Action 2 — Send Teams Notification:**
   - Action type: **Send notification**
   - Channel: `ZOSA-Defense`
   - Message: Include the generated threat brief
   - Priority: **Urgent**

7. **Define Action 3 — Create Mission Proposal:**
   - Action type: **Insert data**
   - Target table: `mission_proposals`
   - Row values:
     - `proposal_name`: `"Threat Response: {{asteroid_name}}"`
     - `source_asteroid_id`: `{{asteroid_id}}`
     - `priority`: `Critical`
     - `status`: `Pending Review`
     - `created_by`: `ZOSA Threat Response Agent`
     - `created_at`: `{{current_timestamp}}`

8. Click **Save and Activate**.

> 📝 **Note:** Actions pass parameters dynamically using the event context. Each `{{placeholder}}` is resolved at runtime from the triggering data change. This is what makes Operations Agents powerful — they chain context-aware actions without hardcoded values.

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
   df.write.mode("append").saveAsTable("zosa_lakehouse.gold_asteroid_risk")
   ```

3. **Watch the Operations Agent trigger.** Within a few minutes:
   - ✅ A threat assessment brief should be generated
   - ✅ A Teams notification should appear in the ZOSA-Defense channel
   - ✅ A new row should appear in `mission_proposals`

4. Verify each step completed successfully in the agent's **Execution History**.

> ⚠️ **Cleanup:** After testing, remove the test row to avoid confusion:
> ```python
> spark.sql("DELETE FROM zosa_lakehouse.gold_asteroid_risk WHERE neo_reference_id = 'TEST-2029-XR7'")
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

---

## 🛡️ Agent Governance

Both Data Agents and Operations Agents include governance controls critical for a defense scenario like ZOSA.

### Audit Trails

Every interaction is logged:
- **Data Agent:** Each natural language query, the generated SQL/KQL, the results returned, and the user who asked
- **Operations Agent:** Each trigger event, every action executed, parameters passed, and outcomes

### Approval Workflows

Operations Agents can be configured to require **human approval** before executing critical actions:

| Risk Level | Approval Behavior |
|---|---|
| **Low** (informational) | Fully automatic — no approval needed |
| **Medium** (notifications) | Automatic with post-action review |
| **High** (data writes) | Requires approval before executing |
| **Critical** (external actions) | Requires multi-person approval |

For ZOSA, you might configure Action 3 (creating mission proposals) to require approval from a Defense team lead before the row is inserted.

### Human-in-the-Loop Patterns

Configure when and how humans are involved:
- **Pre-action approval:** Agent pauses and waits for human sign-off
- **Post-action review:** Agent acts immediately but flags the action for review
- **Escalation:** If the agent can't resolve ambiguity, it escalates to a human operator

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
> You smile. That's Module 11.

---

## 🧭 Navigation

| Previous | Next |
|---|---|
| [← Module 09 — Ontology & Knowledge Graph](09-ontology-knowledge-graph.md) | [Module 11 — CI/CD & Deployment →](11-ci-cd-deployment.md) |

[← Back to README](../README.md)

