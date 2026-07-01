# 📜 Module 04 — Data Contracts

> *It's 3 AM when Major Kai Nakamura's pager screams. A potentially hazardous asteroid slipped past ZOSA's alerting system — no warning, no dashboard flag, nothing. By dawn the whole leadership team is on a call. The culprit? NASA quietly renamed a field in the NeoWs feed and changed `is_potentially_hazardous_asteroid` from a boolean to the string `"true"`. Your Bronze table ingested the garbage without complaint, and every downstream filter silently returned zero rows.*
>
> *"This can never happen again," Dr. Vasquez says flatly. "From now on, no data enters the Silver layer without a signed agreement about its shape and quality. Sofia, back me up on this." Sofia Lindqvist nods: "A data contract. The producer promises a schema and quality bar; we reject anything that breaks it — loudly. Build it."*

---

## 🎯 What You'll Build

In this module you'll add a **data contract gate** at the Bronze → Silver boundary — the single most important place to catch bad data before it poisons everything downstream. By the end you'll have:

- A **versioned contract** (YAML) for `asteroids_bronze` describing its schema, quality rules, freshness SLA, and ownership.
- A reusable **validation notebook** that enforces the contract, **quarantines** violating rows, and **fails loudly** on schema drift.
- A **quarantine table** and a validation summary you can alert on.

**Time estimate:** 40 minutes

**Prerequisites:** You need the Bronze tables from [Module 03 — Data Ingestion](03-data-ingestion.md) loaded in `lh_zosa`. This module runs *before* the Medallion transformations in [Module 05](05-medallion-lakehouse.md).

---

## 🧭 Section 1 — What Is a Data Contract?

A **data contract** is an explicit, machine-enforceable agreement between a data **producer** (NASA's feed, an upstream team, an ingestion pipeline) and its **consumers** (your Silver/Gold tables, semantic models, reports, ML models). It answers four questions *before* data flows downstream:

| Pillar | Question it answers | Example for `asteroids_bronze` |
|--------|--------------------|--------------------------------|
| **Schema** | What columns and types must exist? | `is_hazardous` **must** be a `boolean`, not a string |
| **Quality** | What values are valid? | `miss_distance_km` ≥ 0; `neo_id` never null; `close_approach_date` is a real date |
| **SLA / Freshness** | How fresh and complete must it be? | Updated at least daily; ≥ 1 row per day |
| **Ownership** | Who owns it, and what version is this? | Owner: Data Engineering; contract `v1.0.0` |

**Why enforce it at Bronze → Silver?** Bronze is intentionally a faithful, unfiltered copy of the source — you *want* to keep the raw garbage for auditing. But Silver is where data becomes *trusted*. The contract is the checkpoint between "what we received" and "what we promise." Catch drift here and nothing downstream ever sees it.

> 💡 **Contracts vs. governance:** In [Module 02](02-governance-and-security.md) you controlled *who can see* data (RLS/CLS/OLS). A data contract controls *whether data is allowed to move at all*. They're complementary: governance is about access, contracts are about trust.

> 📚 **Official Documentation:**
> - [Data quality in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/governance/data-quality-overview)
> - [Delta Lake schema enforcement & evolution](https://learn.microsoft.com/en-us/azure/databricks/delta/update-schema)
> - [Purview data quality rules](https://learn.microsoft.com/en-us/purview/data-quality-overview)

---

## 📝 Section 2 — Author the Contract

A contract should live *with* the data as a versioned, human-readable artifact. You'll store it as YAML in your Lakehouse `Files` area so both people and pipelines can read it.

1. Open the **`nb_api_ingestion`** notebook from Module 03 (or create a new notebook `nb_data_contracts` and attach `lh_zosa`).
2. Add a cell and run it to write the contract to `Files/contracts/asteroids.v1.yaml`:

```python
contract = """
# Data Contract — asteroids_bronze
# The producer (NASA NeoWs ingestion) guarantees this shape & quality.
name: asteroids_bronze
version: 1.0.0
owner: data-engineering@zosa.example
source: NASA NeoWs API
description: Near-Earth object close-approach records ingested daily.

# --- Schema: required columns and their types ---
schema:
  - {name: neo_id,                    type: string,  nullable: false}
  - {name: name,                      type: string,  nullable: false}
  - {name: absolute_magnitude,        type: double,  nullable: true}
  - {name: is_hazardous,              type: boolean, nullable: false}
  - {name: close_approach_date,       type: string,  nullable: false}
  - {name: miss_distance_km,          type: double,  nullable: false}
  - {name: relative_velocity_kph,     type: double,  nullable: false}
  - {name: estimated_diameter_min_m,  type: double,  nullable: true}
  - {name: estimated_diameter_max_m,  type: double,  nullable: true}

# --- Quality: row-level expectations ---
quality:
  - {column: neo_id,            rule: not_null}
  - {column: neo_id,            rule: unique}
  - {column: miss_distance_km,  rule: min, value: 0}
  - {column: relative_velocity_kph, rule: min, value: 0}
  - {column: estimated_diameter_min_m, rule: max, value: 100000}
  - {column: close_approach_date, rule: matches_regex, value: '^\\d{4}-\\d{2}-\\d{2}$'}

# --- SLA: freshness & volume ---
sla:
  freshness_hours: 24     # data must be no older than 24h
  min_rows_per_day: 1     # at least one record per approach date
"""

mssparkutils.fs.put("Files/contracts/asteroids.v1.yaml", contract, overwrite=True)
print("✅ Contract written to Files/contracts/asteroids.v1.yaml")
```

**What just happened?** You captured the producer's promise as a versioned file that travels with the data. Anyone — human or pipeline — can now read exactly what `asteroids_bronze` is supposed to look like. The `version` field is critical: when NASA legitimately changes the feed, you bump the version and review the change deliberately instead of being surprised at 3 AM.

> ⚠️ **Note on the boolean rule:** Notice the contract declares `is_hazardous` as `boolean`. This is the exact field that broke Major Kai's alerts when it arrived as the string `"true"`. The gate you build next will reject that drift instead of silently ingesting it.

---

## 🚦 Section 3 — Build the Validation Gate

Now build the enforcement engine: a reusable function that loads a contract and checks a DataFrame against it. It separates **schema violations** (structural — fail the whole load) from **row-level quality violations** (quarantine the bad rows, let the good ones through).

Add this cell and run it:

```python
import re, yaml
from pyspark.sql import functions as F

def load_contract(path):
    return yaml.safe_load(mssparkutils.fs.head(path, 100_000))

def validate(df, contract):
    errors, warnings = [], []

    # 1) SCHEMA CHECK — structural, breaking
    actual = dict(df.dtypes)
    type_map = {"string": "string", "double": "double", "boolean": "boolean",
                "long": "bigint", "integer": "int"}
    for field in contract["schema"]:
        cname, ctype = field["name"], field["type"]
        if cname not in actual:
            errors.append(f"MISSING COLUMN: {cname}")
        elif actual[cname] != type_map.get(ctype, ctype):
            errors.append(f"TYPE DRIFT: {cname} is '{actual[cname]}', contract requires '{ctype}'")

    # 2) ROW-LEVEL QUALITY — build a boolean 'is_valid' column
    valid = F.lit(True)
    for q in contract.get("quality", []):
        c, rule = q["column"], q["rule"]
        if c not in actual:
            continue  # schema check already flagged it
        if rule == "not_null":
            valid = valid & F.col(c).isNotNull()
        elif rule == "min":
            valid = valid & (F.col(c) >= q["value"])
        elif rule == "max":
            valid = valid & (F.col(c) <= q["value"])
        elif rule == "matches_regex":
            valid = valid & F.col(c).rlike(q["value"])
        elif rule == "unique":
            dupes = df.groupBy(c).count().filter("count > 1").count()
            if dupes:
                warnings.append(f"UNIQUENESS: {dupes} duplicate value(s) in {c}")

    checked = df.withColumn("_contract_valid", valid)

    # 3) SLA CHECK — volume
    sla = contract.get("sla", {})
    total = checked.count()
    if total < sla.get("min_rows_per_day", 0):
        warnings.append(f"SLA: only {total} rows (min {sla['min_rows_per_day']})")

    return checked, errors, warnings

print("✅ Contract validation engine ready")
```

Now run the gate against `asteroids_bronze`:

```python
contract = load_contract("Files/contracts/asteroids.v1.yaml")
df = spark.read.table("asteroids_bronze")
checked, errors, warnings = validate(df, contract)

# Split good vs. bad rows
passed = checked.filter("_contract_valid = true").drop("_contract_valid")
quarantined = (checked.filter("_contract_valid = false")
                      .withColumn("_quarantined_at", F.current_timestamp())
                      .withColumn("_contract", F.lit(f"{contract['name']} v{contract['version']}")))

print(f"Rows passed:      {passed.count()}")
print(f"Rows quarantined: {quarantined.count()}")
print(f"Schema errors:    {errors}")
print(f"Warnings:         {warnings}")

# BREAKING: schema drift stops the pipeline before Silver
if errors:
    raise ValueError(f"❌ CONTRACT BROKEN — halting load:\n" + "\n".join(errors))

# Persist the clean, contract-compliant data for the Medallion module to consume
passed.write.mode("overwrite").format("delta").saveAsTable("asteroids_bronze_validated")

# Persist rejected rows for investigation instead of throwing them away
if quarantined.count() > 0:
    quarantined.write.mode("append").format("delta").saveAsTable("asteroids_quarantine")

print("✅ Gate passed — asteroids_bronze_validated is safe for Silver")
```

**What just happened?** You built a gate that does three things a silent pipeline never would:

1. **Fails loudly** (`raise ValueError`) on schema drift — the exact failure mode that broke Major Kai's alerts now stops the pipeline dead.
2. **Quarantines** bad rows into `asteroids_quarantine` (with a timestamp and contract version) instead of dropping or ingesting them — so you can investigate *why* the producer sent them.
3. Produces `asteroids_bronze_validated`, a **trusted** input that Module 05 can safely transform to Silver.

> 💡 **Tip:** In production you'd point Module 05's Silver transformation at `asteroids_bronze_validated` instead of the raw `asteroids_bronze`. The contract gate becomes a required upstream step in your Data Pipeline (with the notebook activity set to fail the pipeline on error).

---

## 🔬 Section 4 — Prove It Catches Drift

A contract you never test is just a comment. Let's simulate the incident that started this whole mess and confirm the gate catches it.

```python
# Simulate NASA breaking the feed: is_hazardous arrives as a STRING
bad = spark.read.table("asteroids_bronze").withColumn(
    "is_hazardous", F.col("is_hazardous").cast("string"))

checked, errors, warnings = validate(bad, contract)
print("Schema errors:", errors)
assert any("is_hazardous" in e for e in errors), "Gate failed to catch the drift!"
print("✅ Gate correctly REJECTED the string-typed is_hazardous — Major Kai sleeps tonight")
```

You should see a `TYPE DRIFT: is_hazardous is 'string', contract requires 'boolean'` error. That's the whole point: the drift that once slipped through silently is now a hard, visible failure **before** it can reach a single dashboard.

> ⚠️ **Breaking vs. non-breaking changes:** Not every change is an emergency. Adding a *new optional* column is non-breaking; renaming or retyping a *required* column is breaking. When NASA makes a legitimate change, you don't patch code in a panic — you author `asteroids.v2.yaml`, review the diff, and migrate consumers deliberately. **Versioning turns surprises into decisions.**

---

## 🔔 Section 5 — Wire Up Alerting & Ownership

A quarantine table nobody watches is useless. Two final steps make the contract operational.

**1. Emit a validation summary you can alert on.** Write one row per validation run to a metrics table:

```python
from datetime import datetime

summary = spark.createDataFrame([{
    "contract": f"{contract['name']} v{contract['version']}",
    "run_ts": datetime.utcnow().isoformat(),
    "rows_passed": passed.count(),
    "rows_quarantined": quarantined.count(),
    "schema_errors": len(errors),
    "warnings": len(warnings),
}])
summary.write.mode("append").format("delta").saveAsTable("contract_validation_log")
print("✅ Logged validation run to contract_validation_log")
```

In [Module 08 — Real-Time Intelligence](08-real-time-intelligence.md) you'll learn to set a **Fabric Activator** alert. A natural rule for this table: *when `rows_quarantined > 0` or `schema_errors > 0`, notify the data-engineering channel.* That closes the loop — a broken contract now pages a human instead of failing silently.

**2. Register ownership in Purview.** The contract's `owner` field should map to a real steward:

- Open the **Microsoft Purview** hub (used in [Module 02](02-governance-and-security.md)).
- Find the `asteroids_bronze` asset, assign a **Data Owner**, and attach the contract file as documentation.

> 💡 **Tip:** Treat the `contracts/` folder like source code. Commit it to Git (you'll set up Git integration in [Module 12](12-ci-cd-deployment.md)) so every contract change is reviewed in a pull request — the same rigor you'd apply to application code.

> 📚 **Official Documentation:**
> - [Fabric Activator (Reflex) alerts](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)
> - [Assign data stewards in Purview](https://learn.microsoft.com/en-us/purview/how-to-workflow-manual-approval)

---

## ✅ Checkpoint

Verify that you've completed the following before moving on:

- [ ] Contract `asteroids.v1.yaml` written to `Files/contracts/` in `lh_zosa`
- [ ] Validation engine (`validate`) runs and separates schema errors from row-level violations
- [ ] `asteroids_bronze_validated` table created with only contract-compliant rows
- [ ] `asteroids_quarantine` captures rejected rows (with timestamp + contract version)
- [ ] The drift test in Section 4 **raises/flags** the string-typed `is_hazardous`
- [ ] `contract_validation_log` records a summary row per run
- [ ] You understand the difference between a **breaking** and **non-breaking** contract change

---

> *You drop a screenshot of the failed drift test into the leadership channel: `TYPE DRIFT: is_hazardous is 'string', contract requires 'boolean' — LOAD HALTED`. Dr. Vasquez replies within seconds: "That red error is the most beautiful thing I've seen all week. From now on, nothing untrusted touches Silver." Major Kai adds a single 🛡️. Now that your data is under contract, it's finally safe to refine it — Bronze to Silver to Gold.*

---

**Navigation:**
[← Module 03 — Data Ingestion](03-data-ingestion.md) | [Module 05 — Medallion Lakehouse →](05-medallion-lakehouse.md)

[← Back to README](../README.md)
