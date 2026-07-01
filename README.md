# 🚀 Fabric Space Lab — End-to-End Microsoft Fabric Workshop

> Build a complete analytics platform for a fictional space agency using Microsoft Fabric —
> from raw NASA data to AI-powered asteroid defense.

![Fabric](https://img.shields.io/badge/Microsoft%20Fabric-2026-blue?logo=microsoft)
![License](https://img.shields.io/badge/license-MIT-green)
![Labs](https://img.shields.io/badge/modules-15-orange)

## 🛸 The Story

**Zenith Orbital Space Agency (ZOSA)** is an international space agency coordinating deep-space
observation, asteroid defense monitoring, and exoplanet research across 12 ground stations worldwide.

Their legacy analytics stack can no longer keep up. The CTO has greenlit a full migration to
Microsoft Fabric. **You've just been hired as ZOSA's Lead Data Engineer.** Your mission: build
the analytics platform from scratch.

Each module advances the story — and your skills — as you progress from an empty Fabric tenant
to a fully operational, AI-enhanced analytics platform.

## 📡 Data Sources

| Source | Type | Description |
|--------|------|-------------|
| [NASA NeoWs API](https://api.nasa.gov/) | Real / Public | Near-Earth asteroid tracking |
| [NASA DONKI API](https://api.nasa.gov/) | Real / Public | Solar flares & space weather events |
| [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) | Real / Public | Confirmed exoplanet catalog |
| ZOSA Missions & Crew | Synthetic | Generated via Python scripts in this repo |
| Ground Station Telemetry | Synthetic | Simulated IoT sensor data |

> **No API key?** Pre-generated sample datasets are included in [`data/sample/`](data/sample/)
> so you can complete every lab without API access.

## 🗺️ Lab Modules

| # | Module | Topics Covered | Est. Time |
|---|--------|---------------|-----------|
| [00](labs/00-prerequisites.md) | **Prerequisites** | Setup, API keys, mission briefing | 20 min |
| [01](labs/01-capacity-and-workspace.md) | **Capacity & Workspaces** | SKU selection, workspace design, domains | 30 min |
| [02](labs/02-governance-and-security.md) | **Governance & Security** | OneLake Security (RLS/CLS/OLS/DDM), Purview, sensitivity labels | 30 min |
| [03](labs/03-data-ingestion.md) | **Data Ingestion** | Lakehouse, Dataflows Gen2, Data Pipelines, OneLake Shortcuts | 45 min |
| [04](labs/04-data-contracts.md) | **Data Contracts** | Schema/quality/SLA contracts, Bronze→Silver validation gate, quarantine, drift detection | 40 min |
| [05](labs/05-medallion-lakehouse.md) | **Medallion Lakehouse** | Bronze → Silver → Gold with Spark notebooks | 60 min |
| [06](labs/06-semantic-model.md) | **Semantic Model** | Direct Lake, DAX measures, RLS/OLS | 40 min |
| [07](labs/07-power-bi-reports.md) | **Power BI Reports** | Mission Control dashboard, Exoplanet Explorer | 45 min |
| [08](labs/08-real-time-intelligence.md) | **Real-Time Intelligence** | Eventstream, Eventhouse, KQL, Real-Time Hub, Activator | 45 min |
| [09](labs/09-data-science.md) | **Data Science & AI** | MLflow, asteroid risk prediction model | 50 min |
| [10](labs/10-ontology-knowledge-graph.md) | **Ontology & Knowledge Graph** | Fabric IQ, Ontology Project, entity mapping | 40 min |
| [11](labs/11-ai-agents.md) | **AI Agents** | Data Agents (GA), Operations Agents (Preview) | 50 min |
| [12](labs/12-ci-cd-deployment.md) | **CI/CD & Deployment** | Git integration, Variable Library, Deployment Pipelines | 30 min |
| [13](labs/13-monitoring-optimization.md) | **Monitoring & Optimization** | Capacity Metrics, CU analysis, cost optimization | 30 min |
| [14](labs/14-fabric-apps.md) | **Fabric Apps** | Rayfin CLI, TypeScript data models, GraphQL APIs, Fabric SSO, full-stack web apps | 60 min |

**Total estimated time:** ~9.5 hours (can be done across multiple sessions)

## 🏗️ Repo Structure

```
fabric-space-lab/
├── README.md               ← You are here
├── CONTRIBUTING.md          ← How to contribute
├── LICENSE                  ← MIT License
├── .gitignore
├── requirements.txt         ← Python dependencies for data scripts
├── data/
│   ├── generate_synthetic.py
│   ├── fetch_nasa_apis.py
│   ├── sample/              ← Pre-generated datasets (CSV)
│   └── README.md            ← Data dictionary
├── labs/                    ← Step-by-step lab modules (Markdown)
├── notebooks/               ← Fabric-ready Jupyter notebooks (.ipynb)
└── assets/
    ├── diagrams/            ← Architecture diagrams (Mermaid + PNG)
    └── screenshots/         ← Step-by-step visual guides
```

## 🚀 Quick Start

1. **Get a Fabric capacity** — [Start a free trial](https://learn.microsoft.com/fabric/get-started/fabric-trial)
2. **Get a NASA API key** — [Register at api.nasa.gov](https://api.nasa.gov/) (free, instant)
3. **Clone this repo:**
   ```bash
   git clone https://github.com/Diaz506/fabric-space-lab.git
   cd fabric-space-lab
   pip install -r requirements.txt
   ```
4. **Start with [Module 00 — Prerequisites](labs/00-prerequisites.md)**

## 🎯 Who Is This For?

- **Data Engineers** looking for hands-on Fabric experience
- **Analytics Engineers** transitioning from legacy platforms
- **Solution Architects** evaluating Fabric capabilities
- **Anyone** who loves space 🌌 and data 📊

## 📋 Prerequisites

- Microsoft Fabric capacity (trial or paid F2+)
- Azure subscription (optional — for ADLS shortcut in Module 03)
- Python 3.10+ (for data generation scripts)
- Power BI Desktop (for Module 06)
- Basic familiarity with SQL, Python, and data concepts

## 📊 Feature Status

This lab covers features at various maturity levels:

| Feature | Status |
|---------|--------|
| OneLake Security, Direct Lake, Eventhouse, Activator | ✅ GA |
| Data Agents | ✅ GA (March 2026) |
| Dataflows Gen2, Data Pipelines, Mirroring | ✅ GA |
| Git Integration, Deployment Pipelines | ✅ GA |
| Fabric IQ / Ontology Projects | ⚠️ Preview |
| Operations Agents | ⚠️ Preview |
| Variable Library | ⚠️ Preview |
| Fabric Apps / Rayfin | ⚠️ Preview |

> Preview features may change before GA. Labs using preview features include a ⚠️ callout.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ and curiosity about the cosmos.*

