# ZOSA Platform — Architecture Diagrams

Reference diagrams for the Zenith Orbital Space Agency analytics platform built on Microsoft Fabric.
These are referenced from individual lab modules.

---

## 1. Overall ZOSA Architecture

High-level view of the complete analytics platform: data sources, ingestion, storage, processing, consumption, AI, and management layers.

```mermaid
flowchart LR
    %% ── Data Sources ──
    subgraph SRC["Data Sources"]
        direction TB
        subgraph NASA["NASA APIs"]
            NEO["NeoWs\n(Asteroids)"]
            DONKI["DONKI\n(Solar Events)"]
            EXO["Exoplanet\nArchive"]
        end
        subgraph INTERNAL["ZOSA Internal Systems"]
            MDB["Missions DB"]
            CDB["Crew DB"]
            TEL["Ground Station\nTelemetry"]
        end
    end

    %% ── Ingestion ──
    subgraph ING["Ingestion Layer"]
        DF["Dataflows Gen2"]
        DP["Data Pipelines"]
        ES["Eventstream"]
        SC["OneLake\nShortcuts"]
    end

    %% ── Storage ──
    subgraph OL["OneLake"]
        LH["Lakehouse\n(Delta Tables)"]
        EH["Eventhouse\n(KQL Database)"]
    end

    %% ── Processing ──
    subgraph PROC["Processing"]
        NB["Spark Notebooks"]
        subgraph MED["Medallion Architecture"]
            BRZ["Bronze\n(Raw)"]
            SLV["Silver\n(Cleaned)"]
            GLD["Gold\n(Aggregated)"]
        end
    end

    %% ── Consumption ──
    subgraph CON["Consumption"]
        SM["Direct Lake\nSemantic Model"]
        PBI["Power BI\nReports"]
        RTD["Real-Time\nDashboard"]
        KQL["KQL Queries"]
    end

    %% ── AI Layer ──
    subgraph AI["AI & Intelligence"]
        ML["ML Models\n(MLflow)"]
        IQ["Fabric IQ\nOntology"]
        DA["Data Agents"]
        OA["Operations\nAgents"]
    end

    %% ── Management ──
    subgraph MGT["Management"]
        GIT["Git\nIntegration"]
        DPL["Deployment\nPipelines"]
        CAP["Capacity\nMetrics"]
    end

    %% ── Connections: Sources → Ingestion ──
    NEO --> DF
    DONKI --> DF
    EXO --> DP
    MDB --> SC
    CDB --> SC
    TEL --> ES

    %% ── Ingestion → OneLake ──
    DF --> LH
    DP --> LH
    ES --> EH
    SC --> LH

    %% ── OneLake → Processing ──
    LH --> NB
    NB --> BRZ --> SLV --> GLD

    %% ── Processing & Storage → Consumption ──
    GLD --> SM --> PBI
    EH --> RTD
    EH --> KQL

    %% ── AI connections ──
    GLD --> ML
    GLD --> IQ
    IQ --> DA
    IQ --> OA

    %% ── Management spans everything ──
    GIT -.-> LH
    DPL -.-> LH
    CAP -.-> OL
```

---

## 2. Medallion Lakehouse Flow

Detailed view of the Bronze → Silver → Gold pipeline showing tables, transformations, and downstream consumption.

```mermaid
flowchart TD
    %% ── Raw Sources ──
    subgraph RAW["Raw Data (CSV / JSON)"]
        R1["asteroids.csv"]
        R2["solar_events.json"]
        R3["exoplanets.csv"]
        R4["missions.csv"]
        R5["crew.csv"]
        R6["telemetry.json"]
    end

    %% ── Bronze Layer ──
    subgraph BRONZE["Bronze Layer — Raw Ingestion"]
        B1["asteroids_raw"]
        B2["solar_events_raw"]
        B3["exoplanets_raw"]
        B4["missions_raw"]
        B5["crew_raw"]
        B6["telemetry_raw"]
    end

    NB1["🔧 Notebook:\nbronze_ingestion"]

    R1 --> NB1
    R2 --> NB1
    R3 --> NB1
    R4 --> NB1
    R5 --> NB1
    R6 --> NB1

    NB1 --> B1
    NB1 --> B2
    NB1 --> B3
    NB1 --> B4
    NB1 --> B5
    NB1 --> B6

    %% ── Silver Layer ──
    subgraph SILVER["Silver Layer — Cleaned & Typed"]
        S1["asteroids_clean\n(typed, deduped)"]
        S2["solar_events_clean\n(parsed timestamps)"]
        S3["exoplanets_clean\n(unit-normalized)"]
        S4["missions_clean\n(status validated)"]
        S5["crew_clean\n(roles standardized)"]
        S6["telemetry_clean\n(anomalies flagged)"]
        SJ["missions_crew_joined\n(missions ⋈ crew)"]
    end

    NB2["🔧 Notebook:\nsilver_transform"]

    B1 --> NB2
    B2 --> NB2
    B3 --> NB2
    B4 --> NB2
    B5 --> NB2
    B6 --> NB2

    NB2 --> S1
    NB2 --> S2
    NB2 --> S3
    NB2 --> S4
    NB2 --> S5
    NB2 --> S6

    S4 --> SJ
    S5 --> SJ

    %% ── Gold Layer ──
    subgraph GOLD["Gold Layer — Business Aggregations"]
        G1["gold_asteroid_risk\n(threat score, proximity)"]
        G2["gold_mission_summary\n(status, duration, crew count)"]
        G3["gold_solar_activity\n(daily/weekly aggregates)"]
        G4["gold_exoplanet_catalog\n(habitability index)"]
    end

    NB3["🔧 Notebook:\ngold_aggregate"]

    S1 --> NB3
    SJ --> NB3
    S2 --> NB3
    S3 --> NB3

    NB3 --> G1
    NB3 --> G2
    NB3 --> G3
    NB3 --> G4

    %% ── Consumption ──
    subgraph CONSUME["Consumption"]
        DL["Direct Lake\nSemantic Model"]
        PBI["Power BI Reports"]
    end

    G1 --> DL
    G2 --> DL
    G3 --> DL
    G4 --> DL
    DL --> PBI
```

---

## 3. Real-Time Intelligence Pipeline

Real-time data flow from ground station sensors through Eventstream, Eventhouse, dashboards, and alerting.

```mermaid
flowchart LR
    %% ── Sources ──
    subgraph SRC["Real-Time Sources"]
        GS["Ground Station\nSensors"]
        ADF["Asteroid\nDetection Feed"]
    end

    %% ── Ingestion ──
    subgraph INGEST["Eventstream"]
        ES["Eventstream\nIngestion"]
        FLT["In-stream\nFiltering"]
        ENRICH["In-stream\nEnrichment"]
    end

    %% ── Hot Path ──
    subgraph HOT["Hot Path (Eventhouse)"]
        KDB["KQL Database"]
        MV1["Materialized View:\nlatest_telemetry"]
        MV2["Materialized View:\nnear_earth_alerts"]
    end

    %% ── Cold Path ──
    subgraph COLD["Cold Path (OneLake)"]
        LH["Lakehouse\n(Historical Archive)"]
        NOTE["Retention:\n> 30 days"]
    end

    %% ── Dashboards ──
    subgraph DASH["Visualization"]
        RTD["Real-Time Dashboard\n(auto-refresh)"]
        KQ["Ad-hoc\nKQL Queries"]
    end

    %% ── Alerting ──
    subgraph ALERT["Activator (Alerts)"]
        RULE["Rule: asteroid\ndistance < 0.05 AU"]
        EMAIL["📧 Email\nNotification"]
        TEAMS["💬 Teams\nMessage"]
        TRIG["📓 Trigger\nNotebook"]
    end

    %% ── Flow ──
    GS --> ES
    ADF --> ES
    ES --> FLT --> ENRICH

    ENRICH --> KDB
    KDB --> MV1
    KDB --> MV2

    KDB -->|"> 30 days\n(data aging)"| LH
    LH --- NOTE

    MV1 --> RTD
    MV2 --> RTD
    KDB --> KQ

    MV2 --> RULE
    RULE --> EMAIL
    RULE --> TEAMS
    RULE --> TRIG
```

---

## 4. CI/CD Deployment Flow

Git-integrated deployment pipeline from source control through Dev, Test, and Production workspaces.

```mermaid
flowchart LR
    %% ── Source Control ──
    subgraph GH["Source Control"]
        REPO["GitHub Repo\n(Source of Truth)"]
        FEAT["Feature\nBranches"]
        MAIN["main\nBranch"]
    end

    %% ── Dev Workspace ──
    subgraph DEV["ZOSA-Dev Workspace"]
        DEV_LH["Lakehouse"]
        DEV_NB["Notebooks"]
        DEV_SM["Semantic Model"]
        DEV_PBI["Reports"]
    end

    %% ── Test Workspace ──
    subgraph TEST["ZOSA-Test Workspace"]
        TEST_LH["Lakehouse"]
        TEST_NB["Notebooks"]
        TEST_SM["Semantic Model"]
        TEST_PBI["Reports"]
    end

    %% ── Prod Workspace ──
    subgraph PROD["ZOSA-Prod Workspace"]
        PROD_LH["Lakehouse"]
        PROD_NB["Notebooks"]
        PROD_SM["Semantic Model"]
        PROD_PBI["Reports"]
    end

    %% ── Variable Library ──
    subgraph VARS["Variable Library"]
        V_DEV["Dev Config\n(small capacity)"]
        V_TEST["Test Config\n(sample data)"]
        V_PROD["Prod Config\n(full capacity)"]
    end

    %% ── Deployment Pipeline ──
    PIPE["Fabric\nDeployment Pipeline"]

    %% ── Flow ──
    FEAT -->|"Pull Request"| MAIN
    MAIN -->|"Git Integration\n(auto-sync)"| DEV

    DEV -->|"Deploy"| PIPE
    PIPE -->|"Stage 1:\nDev → Test"| TEST
    PIPE -->|"Stage 2:\nTest → Prod"| PROD

    TEST ---|"🔒 Approval\nGate"| PROD

    V_DEV -.->|"env vars"| DEV
    V_TEST -.->|"env vars"| TEST
    V_PROD -.->|"env vars"| PROD
```
