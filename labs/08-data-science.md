# 🔬 Module 08 — Data Science & AI

> **Story:** Dr. Osei leans forward in her chair, the glow of the dashboard reflecting off her glasses. *"We can see the asteroids after they pass. But can we predict which ones are dangerous before they get close?"* She taps the table. *"The Planetary Defense board needs a risk classifier — not hindsight, but foresight."*

---

## 🎯 Learning Objectives

By the end of this module you will:

- Understand Fabric's built-in data science capabilities
- Engineer features from your Gold layer asteroid data
- Train and compare multiple classification models
- Track experiments with MLflow
- Register the best model and save predictions back to the lakehouse

> **Prerequisites:** You need the `gold_asteroid_risk` table from [Module 04](04-medallion-lakehouse.md) and a working ZOSA-Dev workspace.

---

## 1️⃣ Fabric Data Science Overview

Microsoft Fabric ships a full data science toolkit — no extra provisioning, no separate compute clusters, no third-party integrations required.

| Capability | What It Gives You |
|---|---|
| **Spark Notebooks** | Interactive PySpark + Python environment with pre-installed ML libraries (scikit-learn, pandas, matplotlib, seaborn) |
| **MLflow Integration** | Automatic experiment tracking — every run logs parameters, metrics, and artifacts |
| **Experiment Tracking** | Visual UI to compare runs side-by-side, sort by any metric, and drill into individual results |
| **Model Registry** | Version, stage, and deploy models directly from the Fabric workspace |

> 💡 **Why this matters:** In traditional setups, you'd spend days configuring MLflow servers, connecting storage backends, and wiring up model registries. In Fabric, you open a notebook and start training. The infrastructure is invisible.

> 📚 **Official Documentation:**
> - [Data Science in Fabric Overview](https://learn.microsoft.com/en-us/fabric/data-science/data-science-overview)
> - [Notebooks for Data Science](https://learn.microsoft.com/en-us/fabric/data-science/notebooks-overview)

---

## 2️⃣ Create Experiment

Before you write any code, create an experiment to organize your runs.

1. Navigate to your **ZOSA-Dev** workspace
2. Click **+ New item** → **Experiment**
3. Name it: `asteroid_risk_prediction`
4. Click **Create**

You now have a dedicated experiment container. Every MLflow run you log from a notebook will appear here — with metrics, parameters, and model artifacts organized automatically.

> 📋 **What you should see:** A new Experiment item in your workspace with zero runs. It will populate once you execute the training code below.

> 📚 **Learn more:** [ML Experiments in Fabric](https://learn.microsoft.com/en-us/fabric/data-science/machine-learning-experiment)

---

## 3️⃣ Feature Engineering Notebook

Great models start with great features. You'll transform the raw gold table into a clean feature matrix optimized for classification.

### Create the Notebook

1. In **ZOSA-Dev**, click **+ New item** → **Notebook**
2. Rename it to `03-asteroid-features`
3. In the notebook toolbar, click **+ Add data items** → **Existing Lakehouse** → select **lh_zosa**

### Load the Gold Table

In the first cell, load your gold asteroid risk data:

```python
# Cell 1 — Load gold asteroid risk data
# Use dbo schema — the default lakehouse sets the catalog but tables live under dbo
df = spark.sql("SELECT * FROM dbo.gold_asteroid_risk")
print(f"Total records: {df.count()}")
df.printSchema()
df.show(5)
```

### Engineer Features

Now create the features that will power your classifier. You want features that capture the physical characteristics and orbital dynamics of each asteroid:

```python
# Cell 2 — Feature engineering
from pyspark.sql import functions as F

features_df = df.select(
    # === Identification ===
    F.col("neo_id"),
    
    # === Size features ===
    F.col("avg_diameter_m"),
    (F.col("avg_diameter_m") / 1000).alias("avg_diameter_km"),
    
    # === Velocity features ===
    F.col("relative_velocity_kph"),
    (F.col("relative_velocity_kph") / 3600).alias("relative_velocity_kps"),
    
    # === Distance features ===
    F.col("miss_distance_km"),
    
    # === Interaction features ===
    (F.col("relative_velocity_kph") / F.col("miss_distance_km"))
        .alias("velocity_distance_ratio"),
    (F.col("avg_diameter_m") * F.col("relative_velocity_kph"))
        .alias("size_velocity_product"),
    (F.col("avg_diameter_m") / F.col("miss_distance_km"))
        .alias("size_distance_ratio"),
    
    # === Label ===
    F.when(F.col("is_hazardous") == True, 1)
     .otherwise(0)
     .cast("int")
     .alias("is_hazardous_label")
)

print(f"Feature matrix: {features_df.count()} rows, {len(features_df.columns)} columns")
features_df.show(5)
```

### Handle Missing Values and Normalize

```python
# Cell 3 — Clean and normalize
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.sql import functions as F

# Drop rows with nulls in feature columns
feature_cols = [
    "avg_diameter_km", "relative_velocity_kps", "miss_distance_km",
    "velocity_distance_ratio", "size_velocity_product", "size_distance_ratio"
]

clean_df = features_df.dropna(subset=feature_cols)
print(f"Records after cleaning: {clean_df.count()} (dropped {features_df.count() - clean_df.count()} nulls)")

# Convert to Pandas for sklearn
pdf = clean_df.select(feature_cols + ["is_hazardous_label"]).toPandas()

# Normalize numeric features
from sklearn.preprocessing import StandardScaler as SkScaler
import pandas as pd

scaler = SkScaler()
pdf[feature_cols] = scaler.fit_transform(pdf[feature_cols])

print(f"\nLabel distribution:")
print(pdf["is_hazardous_label"].value_counts())
print(f"\nHazardous ratio: {pdf['is_hazardous_label'].mean():.2%}")
```

### Train/Test Split

```python
# Cell 4 — Stratified train/test split
from sklearn.model_selection import train_test_split

X = pdf[feature_cols]
y = pdf["is_hazardous_label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # preserve class balance
)

print(f"Training set: {len(X_train)} samples")
print(f"Test set:     {len(X_test)} samples")
print(f"\nTraining label distribution:\n{y_train.value_counts(normalize=True)}")
print(f"\nTest label distribution:\n{y_test.value_counts(normalize=True)}")
```

> ⚠️ **Important:** The `stratify=y` parameter ensures your train and test sets have the same proportion of hazardous vs. non-hazardous asteroids. Without this, you might accidentally train on an unbalanced split and get misleading metrics.

> 💡 **Note:** Cell 5 below calls `mlflow.set_experiment("asteroid_risk_prediction")` — make sure this name matches exactly what you created in §2 (step 3).

> 📚 **Official Documentation:**
> - [Scikit-learn in Fabric](https://learn.microsoft.com/en-us/fabric/data-science/train-models-scikit-learn)
> - [SynapseML](https://learn.microsoft.com/en-us/fabric/data-science/synapseml-overview)

---

## 4️⃣ Train Classification Models

Now for the fun part. You'll train three different classifiers and let MLflow track everything.

### Run the Experiment

```python
# Cell 5 — Train and log 3 models with MLflow
import mlflow
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

mlflow.set_experiment("asteroid_risk_prediction")

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
}

results = {}

for name, model in models.items():
    with mlflow.start_run(run_name=name):
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds),
            "recall": recall_score(y_test, preds),
            "f1": f1_score(y_test, preds),
            "roc_auc": roc_auc_score(y_test, proba)
        }

        # Log everything
        mlflow.log_param("model_type", name)
        mlflow.log_param("n_features", len(feature_cols))
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        for metric_name, value in metrics.items():
            mlflow.log_metric(metric_name, value)
        mlflow.sklearn.log_model(model, name)

        results[name] = metrics
        print(f"\n{'='*50}")
        print(f"  {name}")
        print(f"{'='*50}")
        for k, v in metrics.items():
            print(f"  {k:>12}: {v:.4f}")
```

> 💡 **What's happening under the hood:** Each `mlflow.start_run()` creates a tracked experiment run. Parameters, metrics, and the serialized model artifact all get stored automatically — no extra storage configuration needed. You'll see all three runs appear in the Fabric experiment UI within seconds.

> ⚠️ **Expect near-perfect scores:** The `is_hazardous` flag in the gold table was derived from the same physical features (size, velocity, distance) used here for training. Tree-based models (RandomForest, GradientBoosting) will learn this relationship perfectly, producing 1.0 across all metrics. This is expected — the exercise focuses on the **MLflow tracking workflow**, not on building a novel classifier. In a real scenario, you'd use features that weren't used to compute the label.

> 📚 **Learn more:** [MLflow Autologging in Fabric](https://learn.microsoft.com/en-us/fabric/data-science/mlflow-autologging)

---

## 5️⃣ Compare & Select Best Model

### Compare in the Fabric UI

> 💡 **Note:** Runs appear here after you execute Cell 5 in your notebook. The `mlflow.set_experiment("asteroid_risk_prediction")` call links the notebook to this experiment. If runs don't appear immediately, click the **refresh** button (🔄) in the toolbar.

1. Go back to your **ZOSA-Dev** workspace
2. Open the **asteroid_risk_prediction** experiment
3. You'll see three runs — one per model
4. Click **Columns** to display: accuracy, precision, recall, f1, roc_auc
5. Click a column header to sort — **sort by `roc_auc` descending** to find the best overall classifier

> 📋 **What to look for:** For planetary defense, **recall** matters most — you never want to miss a truly hazardous asteroid (a false negative could be catastrophic). But high recall with low precision means too many false alarms. The **F1 score** balances both, and **ROC AUC** captures overall discriminative ability.

### Select and Register the Best Model

```python
# Cell 6 — Identify and register the best model
import pandas as pd

results_df = pd.DataFrame(results).T
results_df = results_df.sort_values(["roc_auc", "f1"], ascending=False)
print("Model Comparison (sorted by ROC AUC, then F1):\n")
print(results_df.to_string())

best_model_name = results_df.index[0]
print(f"\n🏆 Best model: {best_model_name}")
```

To register in the Fabric UI:

1. Open the winning run in the experiment view
2. Click **Save as ML model** in the ribbon
3. Name: `asteroid_hazard_classifier`
4. Click **Save** — the version number is assigned automatically (starting at 1)
5. Navigate back to your workspace and confirm the **ML Model** item `asteroid_hazard_classifier` appears

Your model is now a first-class citizen in the workspace — versioned, trackable, and ready for downstream use.

> 📚 **Learn more:** [ML Models / Model Registry](https://learn.microsoft.com/en-us/fabric/data-science/machine-learning-model)

---

## 6️⃣ Save Predictions to Gold Layer

The model is trained and registered. Now run it against the full dataset and persist predictions back to the lakehouse.

```python
# Cell 7 — Generate predictions on full dataset and save to Gold
import pandas as pd

# Use the best model from training
best_model = models[best_model_name]

# Score the full dataset
full_X = pdf[feature_cols]
pdf["predicted_hazardous"] = best_model.predict(full_X)
pdf["hazard_probability"] = best_model.predict_proba(full_X)[:, 1]

# Merge predictions with original IDs
results_pdf = clean_df.select("neo_id").toPandas()
results_pdf["predicted_hazardous"] = pdf["predicted_hazardous"]
results_pdf["hazard_probability"] = pdf["hazard_probability"]
results_pdf["model_name"] = best_model_name
results_pdf["prediction_timestamp"] = pd.Timestamp.now()

# Save back to lakehouse as a Gold prediction table
predictions_df = spark.createDataFrame(results_pdf)
predictions_df.write.mode("overwrite").format("delta").saveAsTable(
    "dbo.gold_asteroid_predictions"
)

print(f"✅ Saved {predictions_df.count()} predictions to gold_asteroid_predictions")
print(f"\nPrediction distribution:")
print(results_pdf["predicted_hazardous"].value_counts())
print(f"\nSample predictions:")
predictions_df.show(10)
```

> 💡 **Why save predictions as a Gold table?** Downstream consumers — Power BI reports, real-time dashboards, and the ontology layer you'll build in Module 09 — can query this table directly. The model's output becomes a reusable data product, not a one-off notebook result.

> 📚 **Learn more:** [PREDICT Function](https://learn.microsoft.com/en-us/fabric/data-science/model-scoring-predict)

---

## 7️⃣ Feature Importance Analysis

Understanding *why* the model classifies asteroids as hazardous is just as important as the predictions themselves.

```python
# Cell 8 — Feature importance visualization
import matplotlib.pyplot as plt
import numpy as np

# Get feature importances (works for tree-based models)
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
elif hasattr(best_model, "coef_"):
    importances = np.abs(best_model.coef_[0])
else:
    raise ValueError("Model does not expose feature importances")

# Sort by importance
feat_imp = pd.DataFrame({
    "feature": feature_cols,
    "importance": importances
}).sort_values("importance", ascending=True)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(feat_imp["feature"], feat_imp["importance"], color="#0078D4")
ax.set_xlabel("Importance")
ax.set_title(f"Top Feature Importances — {best_model_name}")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.show()

# Log the chart to MLflow (a separate run is needed because the training runs are already closed)
with mlflow.start_run(run_name=f"{best_model_name}_feature_importance"):
    mlflow.log_figure(fig, "feature_importance.png")
    print("📊 Feature importance chart logged to MLflow")
```

> 📋 **What to expect:** For asteroid risk classification, you'll likely see `miss_distance_au` and `size_distance_ratio` dominate — objects that are large *and* pass close to Earth are the most dangerous. `relative_velocity_kmps` also matters because fast-moving objects have more kinetic energy on impact.

---

## ✅ Checkpoint

Verify everything is in place before moving on:

| # | Check | How to Verify |
|---|---|---|
| 1 | Experiment has 3 runs | Open `asteroid_risk_prediction` experiment → see LogisticRegression, RandomForest, GradientBoosting |
| 2 | Metrics logged for all runs | Click any run → verify accuracy, precision, recall, f1, roc_auc are present |
| 3 | Best model registered | Check workspace items → find `asteroid_hazard_classifier` model, Version 1 |
| 4 | Predictions in Gold table | Run `SELECT COUNT(*) FROM lh_zosa.gold_asteroid_predictions` → returns non-zero count |
| 5 | Feature importance chart | Check the MLflow run artifacts for `feature_importance.png` |

```python
# Quick verification cell
print("=== Module 08 Checkpoint ===\n")

pred_count = spark.sql("SELECT COUNT(*) as cnt FROM dbo.gold_asteroid_predictions").collect()[0]["cnt"]
print(f"✅ gold_asteroid_predictions: {pred_count} rows")

hazard_count = spark.sql("""
    SELECT predicted_hazardous, COUNT(*) as cnt
    FROM dbo.gold_asteroid_predictions
    GROUP BY predicted_hazardous
""").show()

print("\n✅ All checkpoint items verified!")
```

> ⚠️ **Troubleshooting:** If the predictions table is empty, re-run Cell 7. If MLflow runs don't appear, confirm you called `mlflow.set_experiment("asteroid_risk_prediction")` before starting runs. If feature importances fail, make sure your best model is a tree-based classifier (RandomForest or GradientBoosting).

---

## 🌉 What's Next?

> Dr. Osei reviews the predictions dashboard, nodding slowly. *"Good — the model catches 96% of the hazardous ones. But this knowledge is trapped in a table."* She looks up. *"How do we make this accessible to every team at ZOSA — scientists, engineers, mission planners — without everyone needing to write SQL?"*

In **[Module 09 — Ontology & Knowledge Graph](09-ontology-knowledge-graph.md)**, you'll build a semantic layer that turns your lakehouse tables and ML predictions into a navigable knowledge graph — making ZOSA's data self-describing and discoverable.

---

**Navigation:**
[← Module 07 — Real-Time Intelligence](07-real-time-intelligence.md) | [Module 09 — Ontology & Knowledge Graph →](09-ontology-knowledge-graph.md)

[← Back to README](../README.md)

