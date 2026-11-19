"""
Step 1 - Export Power BI data for the Predictive Maintenance dashboard
----------------------------------------------------------------------
Uses the same models as predictive-maintenance-failure-analytics.py and saves:

  1. predictions.csv          -> main table (one row per machine): sensors + predictions
  2. model_metrics.csv        -> Random Forest vs XGBoost vs LightGBM (+ RUL regressor)
  3. feature_importance.csv   -> SHAP importance per feature (Sensor Drivers page)
  4. confusion_matrix.csv     -> confusion matrix of the selected model (Model Trust page)
  5. cluster_summary.csv      -> failure rate per KMeans cluster

Run:  python export_powerbi_data.py
"""

import os
import warnings
import numpy as np
import pandas as pd
import shap
import lightgbm as lgb
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, mean_squared_error,
                             mean_absolute_error, r2_score)
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")

# ===================== SETTINGS (edit if needed) =====================
DATA_PATH = r"C:/Users/ss57/OneDrive - Caterpillar/Documents 1/Shiva/Uniqueshiva27/Prescriptive Analytics Project/factory_sensor_simulator_2040.csv"
OUTPUT_DIR = os.path.join(os.path.dirname(DATA_PATH), "powerbi_export")
HIGH_RISK = 0.70        # probability >= 70%  -> High
MEDIUM_RISK = 0.30      # probability 30-70%  -> Medium, below -> Low
SHAP_SAMPLE = 2000      # rows used for global SHAP importance
RANDOM_STATE = 42
# =====================================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- 1. Load data ----------
df = pd.read_csv(DATA_PATH)
print("Loaded:", df.shape)

if "Machine_ID" not in df.columns:
    df.insert(0, "Machine_ID", [f"M-{i:06d}" for i in range(1, len(df) + 1)])

# ---------- 2. Features (same logic as your notebook) ----------
features = df.select_dtypes(include=[np.number]).drop(
    columns=["Remaining_Useful_Life_days", "Failure_Within_7_Days"], errors="ignore")
feature_names = list(features.columns)

imputer = SimpleImputer(strategy="mean")
X = pd.DataFrame(imputer.fit_transform(features), columns=feature_names)
y = df["Failure_Within_7_Days"].astype(int)
y_reg = df["Remaining_Useful_Life_days"]

idx_train, idx_test = train_test_split(np.arange(len(df)), test_size=0.2,
                                       random_state=RANDOM_STATE)
X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]

# ---------- 3. Train the 3 classifiers ----------
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
    "XGBoost": xgb.XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE),
    "LightGBM": lgb.LGBMClassifier(random_state=RANDOM_STATE, verbose=-1),
}

metric_rows = []
for name, m in models.items():
    m.fit(X_train, y_train)
    pred = m.predict(X_test)
    prob = m.predict_proba(X_test)[:, 1]
    metric_rows.append({
        "Model": name, "Task": "Classification (Failure within 7 days)",
        "Accuracy": accuracy_score(y_test, pred),
        "Precision": precision_score(y_test, pred, zero_division=0),
        "Recall": recall_score(y_test, pred, zero_division=0),
        "F1": f1_score(y_test, pred, zero_division=0),
        "ROC_AUC": roc_auc_score(y_test, prob) if y_test.nunique() > 1 else np.nan,
        "MAE_days": np.nan, "RMSE_days": np.nan, "R2": np.nan,
    })
    print(f"{name}: F1 = {metric_rows[-1]['F1']:.3f}")

# Best model by F1 drives the dashboard predictions
best_name = max(metric_rows, key=lambda r: r["F1"])["Model"]
best = models[best_name]
print("Selected model for dashboard:", best_name)

# ---------- 4. RUL regression ----------
reg = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
reg.fit(X_train, y_reg.iloc[idx_train])
reg_pred_test = reg.predict(X_test)
metric_rows.append({
    "Model": "Random Forest Regressor", "Task": "Regression (Remaining Useful Life)",
    "Accuracy": np.nan, "Precision": np.nan, "Recall": np.nan, "F1": np.nan, "ROC_AUC": np.nan,
    "MAE_days": mean_absolute_error(y_reg.iloc[idx_test], reg_pred_test),
    "RMSE_days": np.sqrt(mean_squared_error(y_reg.iloc[idx_test], reg_pred_test)),
    "R2": r2_score(y_reg.iloc[idx_test], reg_pred_test),
})
metrics_df = pd.DataFrame(metric_rows)
metrics_df["Selected_For_Dashboard"] = metrics_df["Model"].eq(best_name)

# ---------- 5. Per-row SHAP contributions -> Top driver ----------
def positive_class(sv):
    if isinstance(sv, list):
        return sv[1]
    if np.ndim(sv) == 3:
        return sv[:, :, 1]
    return sv

if best_name == "XGBoost":
    contrib = best.get_booster().predict(xgb.DMatrix(X), pred_contribs=True)[:, :-1]
elif best_name == "LightGBM":
    contrib = best.predict(X, pred_contrib=True)[:, :-1]
else:  # Random Forest: fast approximate SHAP for every row
    contrib = positive_class(shap.TreeExplainer(best).shap_values(X, approximate=True))

top_idx = np.argmax(contrib, axis=1)  # feature pushing risk UP the most
top_driver = np.array(feature_names)[top_idx]
top_driver_value = contrib[np.arange(len(X)), top_idx]

# Global importance (exact SHAP on a sample)
sample = X.sample(min(SHAP_SAMPLE, len(X)), random_state=RANDOM_STATE)
sv_sample = positive_class(shap.TreeExplainer(best).shap_values(sample))
fi = pd.DataFrame({
    "Feature": feature_names,
    "Mean_Abs_SHAP": np.abs(sv_sample).mean(axis=0),
    "Mean_SHAP": sv_sample.mean(axis=0),
}).sort_values("Mean_Abs_SHAP", ascending=False)
fi["Rank"] = range(1, len(fi) + 1)
fi["Importance_Pct"] = fi["Mean_Abs_SHAP"] / fi["Mean_Abs_SHAP"].sum()
fi["Model"] = best_name

# ---------- 6. Clustering (PCA + KMeans, same as notebook) ----------
pca = PCA(n_components=2, random_state=RANDOM_STATE)
pcs = pca.fit_transform(X)
clusters = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=10).fit_predict(pcs)

# ---------- 7. Build predictions table ----------
out = df.copy()
out["Failure_Probability"] = best.predict_proba(X)[:, 1].round(4)
out["Predicted_Failure"] = (out["Failure_Probability"] >= 0.5).astype(int)
out["Risk_Band"] = np.select(
    [out["Failure_Probability"] >= HIGH_RISK, out["Failure_Probability"] >= MEDIUM_RISK],
    ["High", "Medium"], default="Low")
out["Risk_Sort"] = out["Risk_Band"].map({"High": 1, "Medium": 2, "Low": 3})
out["Predicted_RUL"] = reg.predict(X).round(1)
out["RUL_Band"] = pd.cut(out["Predicted_RUL"], bins=[-np.inf, 7, 30, 60, np.inf],
                         labels=["0-7 Days", "8-30 Days", "31-60 Days", "60+ Days"]).astype(str)
out["RUL_Band_Sort"] = out["RUL_Band"].map({"0-7 Days": 1, "8-30 Days": 2, "31-60 Days": 3, "60+ Days": 4})
out["Top_Driver"] = top_driver
out["Top_Driver_SHAP"] = top_driver_value.round(4)
out["Cluster"] = ["C" + str(c + 1) for c in clusters]
out["PC1"] = pcs[:, 0].round(4)
out["PC2"] = pcs[:, 1].round(4)
if "Vibration_mms" in out.columns:
    out["High_Vibration"] = (out["Vibration_mms"] > 20).astype(int)
if "Oil_Level_pct" in out.columns:
    out["Low_Oil"] = (out["Oil_Level_pct"] < 30).astype(int)
out["Data_Split"] = "Train"
out.loc[out.index[idx_test], "Data_Split"] = "Test"   # filter to Test for honest evaluation visuals
out["Model_Used"] = best_name

# ---------- 8. Confusion matrix + cluster summary ----------
cm = confusion_matrix(y_test, best.predict(X_test), labels=[0, 1])
cm_df = pd.DataFrame([
    {"Actual": "No Failure", "Predicted": "No Failure", "Count": cm[0, 0], "Label": "TN"},
    {"Actual": "No Failure", "Predicted": "Failure", "Count": cm[0, 1], "Label": "FP"},
    {"Actual": "Failure", "Predicted": "No Failure", "Count": cm[1, 0], "Label": "FN"},
    {"Actual": "Failure", "Predicted": "Failure", "Count": cm[1, 1], "Label": "TP"},
])
cm_df["Model"] = best_name

cluster_df = out.groupby("Cluster").agg(
    Machines=("Machine_ID", "count"),
    Observed_Failure_Rate=("Failure_Within_7_Days", "mean"),
    Avg_Failure_Probability=("Failure_Probability", "mean"),
    Avg_Predicted_RUL=("Predicted_RUL", "mean"),
).reset_index()

# ---------- 9. Save ----------
out.to_csv(os.path.join(OUTPUT_DIR, "predictions.csv"), index=False)
metrics_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "model_metrics.csv"), index=False)
fi.round(6).to_csv(os.path.join(OUTPUT_DIR, "feature_importance.csv"), index=False)
cm_df.to_csv(os.path.join(OUTPUT_DIR, "confusion_matrix.csv"), index=False)
cluster_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "cluster_summary.csv"), index=False)

print("\nDone! Files saved to:", OUTPUT_DIR)
print(metrics_df.round(3).to_string(index=False))
