# Predictive Maintenance Dashboard – User Guide

This guide explains how to open, read, and use the Power BI dashboard in `Github Copilot.pbix`. The dashboard shows which machines are likely to fail, how much to trust the model, what drives failures, and how machines group into segments.

> 📘 **Detailed per-tab documentation** – layout, visual inventory, filters, every measure's DAX, calculated columns and data sources – is in the [docs](../docs/README.md) folder.

---

## 1. Getting started

### Requirements
- **Power BI Desktop**, a recent version (the report uses the PBIR report format).
- The CSV / data files listed in [Data sources](#7-data-sources), if you want to refresh the data.

### Opening the report
1. Double-click `Github Copilot.pbix`, or open it from Power BI Desktop with **File ▸ Open**.
2. Wait for the model to load. It holds about 500,000 machine records, so the first load can take a minute.
3. Use the page tabs at the bottom to move between the four dashboards.

### Refreshing the data
1. Replace the source files with new exports using the same file names and columns.
2. Select **Home ▸ Refresh**.
3. All KPIs, charts, narratives and labels are measure-driven and update automatically. The exceptions are listed in [Known limitations](#9-known-limitations).

---

## 2. Dashboard pages

| # | Tab | Question it answers | Main source |
|---|-----|---------------------|-------------|
| 1 | **Fleet Risk Overview** | Which machines are at risk and which to inspect first? | `predictions` |
| 2 | **Model Trust** | How accurate and reliable is the failure model? | `model_metrics`, `confusion_matrix` |
| 3 | **Sensor Drivers** | Which sensors and features drive failure predictions? | `feature_importance`, `predictions` |
| 4 | **Machine Segments** | How do machines group, and which segment is riskiest? | `predictions`, `cluster_summary` |

---

## 3. Fleet Risk Overview

**Purpose:** a daily operational view of fleet risk and the inspection priority list.

### Filters (top right)
- **Machine Type** – limit every visual on the page to one or more machine types.
- **Risk Band** – focus on High, Medium or Low risk machines.

### KPI cards
| Card | Meaning |
|------|---------|
| Machines Monitored | Number of machines in the current filter |
| High Risk Machines | Machines in the **High** risk band |
| High Risk % | High-risk machines ÷ machines monitored |
| Avg Failure Probability | Average predicted probability of failure within 7 days |
| Avg Predicted RUL | Average predicted Remaining Useful Life, in days |

### Visuals
- **Risk Band (donut)** – share of machines in each risk band. Thresholds: **High ≥ 70%**, **Medium 30–70%**, **Low < 30%** failure probability.
- **High-Risk Share by Machine Type (Top 10)** – the 10 machine types with the highest share of high-risk machines, split by risk band.
- **Failure Probability vs Predicted RUL** – one dot per machine, limited to machines with RUL ≤ 180 days.
  - Dots in the **top-left corner** (high probability, short RUL) should be inspected first.
  - Dashed reference lines mark 30 days RUL and the 70% high-risk threshold.
- **Inspection Priority** – the top 25 machines by failure probability, with machine type, predicted RUL, top driver and risk band. Red data bars show the probability.
- **Machines by RUL Band** – machine counts for 0–7, 8–30, 31–60 and 60+ days of predicted RUL.
- **Machines by Top Driver** – how often each sensor or feature is the strongest SHAP driver for a machine.

**How to use it:** filter to a machine type, scan the scatter for top-left points, then work down the **Inspection Priority** table.

---

## 4. Model Trust

**Purpose:** shows how far the predictions on the other pages can be trusted.

### KPI cards
- **Accuracy, Precision, Recall, F1, ROC-AUC** – classification metrics for the **selected model**: the row in `model_metrics` where `Selected_For_Dashboard = TRUE`, currently **LightGBM**.
- **RUL MAE / RMSE** – average error (in days) of the Remaining Useful Life regression model.
- **R squared** – share of RUL variance the regression model explains.

### Visuals
- **Classification metrics by model** – compares Random Forest, XGBoost and LightGBM across the five metrics.
- **Confusion matrix** – validation results for the selected model:
  - **TN** – healthy machines correctly predicted as healthy.
  - **FP** – false alarms: predicted to fail, but did not.
  - **FN** – missed failures: failed, but were predicted healthy.
  - **TP** – failures correctly predicted.
- **Missed failures (FN)**:
  - Shows the number of missed failures and the estimated financial exposure.
  - Exposure = FN × an *illustrative* **$5,000** per missed failure.
  - The miss rate bar shows FN ÷ (FN + TP).
- **False alarm rate** – gauge of FP ÷ (FP + TN) against a **3% target**. The badge shows whether the model is within target.
- **Model selection summary** – the chosen model with its best F1, ROC-AUC and failure detection (TP / all actual failures).

**Customising:**
- To change the cost per missed failure, edit the `Cost per Missed Failure` measure.
- To change the false-alarm target, edit `False Alarm Target`.
- Both measures are in the `confusion_matrix` table.

---

## 5. Sensor Drivers

**Purpose:** explains which inputs the model relies on most and how sensor readings relate to failures.

### Filters
- **Asset** – machine type. Affects the heatmap and sensor profiles.
- **Model** – which model's feature importance to show. Affects the SHAP visuals.

### Visuals
- **SHAP Feature Importance** – top 10 features by mean absolute SHAP value, shown as a share of total importance.
- **Pareto · Driver Contribution**:
  - Bars show each feature's share; the yellow line shows the cumulative share.
  - The callout gives how much the top 4 drivers explain.
- **Top Driver** – the single most influential feature and its share.
- **Feature Share (treemap)** – the top 6 features, with all remaining features grouped as *Other features*.
- **Failure Rate · Vibration × Oil Level**:
  - Heatmap of the actual failure-within-7-days rate, with machines split into fifths (quintiles) by vibration and by oil level.
  - Brighter red means a higher failure rate.
- **Sensor Profiles · Normal vs Failed**:
  - The average standardised value (z-score) of the top sensors for failed vs normal machines.
  - The bigger the gap between the red and cyan bars, the more that sensor separates failing machines.

---

## 6. Machine Segments

**Purpose:** groups machines into K-means clusters and highlights the riskiest segment.

### KPI cards
- **Total machines**, **Overall failure rate** (fleet average), **Avg RUL**.
- **Highest-risk segment** – the cluster with the highest observed failure rate.

### Visuals
- **Machine segments | PC1 vs PC2** – machines plotted on the first two principal components and coloured by cluster. Power BI samples the points for performance.
- **Failure rate by cluster** – observed failure rate per cluster, with a dashed fleet-average line.
- **Risk band mix by cluster** – the High / Medium / Low mix inside each cluster.
- **Cluster profile** – per-cluster machine count, average temperature, vibration, oil level, failure rate and RUL.
  - The failure-rate cell turns **red** when the cluster is above the fleet average and **green** otherwise.
  - The total row shows fleet-level values.
- **Smart narrative** – an auto-generated sentence naming the highest-risk cluster and its failure rate, with a multiple of the fleet average and that cluster's average RUL.

---

## 7. Data sources

| Table | Source | Content |
|-------|--------|---------|
| `predictions` | predictions export | One row per machine: sensor readings, failure probability, risk band, predicted RUL, top SHAP driver, cluster, PC1/PC2 |
| `model_metrics` | `model_metrics.csv` | Validation metrics for each classification and regression model |
| `confusion_matrix` | `confusion_matrix.csv` | TN / FP / FN / TP counts for the selected model |
| `feature_importance` | `feature_importance.csv` | Mean absolute SHAP value, rank and share per feature |
| `cluster_summary` | `cluster_summary.csv` | Per-cluster machine counts, failure rate and RUL |
| `factory_sensor_simulator_2040` | `factory_sensor_simulator_2040.csv` | Raw sensor data |

The model outputs are produced by `predictive-maintenance-failure-analytics.py` / `.ipynb` and exported for Power BI by `export_powerbi_data.py`.

### Helper objects added to the model
- **Measures** are grouped in display folders: *Fleet Risk*, *Model Trust*, *Sensor Drivers*, *Machine Segments*.
- **Calculated tables:**
  - `Model Metrics Long` – metrics unpivoted, for the model comparison chart.
  - `Model Summary` – rows for the model selection summary.
  - `Sensor List` – the sensors shown in Sensor Profiles.
- **Calculated columns:**
  - `predictions[Machine Type]`, `predictions[Top Driver]` and `feature_importance[Feature Name]` – friendly display names.
  - `predictions[Vibration Level]` and `predictions[Oil Level Band]` – the quintile bands.
  - `predictions[Failure Status]` – Normal / Failed.
  - `feature_importance[Feature Group]` – top 6 features plus *Other features*.

---

## 8. Tips for interacting with the report

- **Cross-filtering:** click any bar, slice or table row to filter the other visuals on the page. Click it again, or click empty space, to clear.
- **Drill into detail:** hover over a visual and use **More options (…) ▸ Show as a table** to see the underlying numbers.
- **Focus mode:** use the focus icon in a visual's header to enlarge it.
- **Export:** use **More options (…) ▸ Export data** to export summarised data from any visual.
- **Reset filters:** clear slicers with the eraser icon, or reopen the file.

---

## 9. Known limitations

- **Fixed band cut-offs:** risk band, RUL band and sensor quintile thresholds are fixed values. The quintile cut-offs in `Vibration Level` and `Oil Level Band` were calculated from the current data and do not update on refresh.
- **Fixed card subtitles:** on **Model Trust**, the "LightGBM · validation" and "RF Regressor · validation" card subtitles are fixed text.
- **Illustrative exposure:** the $5,000 cost per missed failure is an illustrative assumption, not a real cost figure.
- **Scatter sampling:** both scatter charts show a sample of the points because of the 500,000-row data volume.
- **No date filter:** the data has no date column, so there is no time filter.
- **No box plots:** Power BI has no built-in box plot, so sensor distributions are shown as mean z-scores.

---

## 10. Backups

Backup copies made before each dashboard page was added are kept next to the report:

- `Github Copilot - backup before dashboard.pbix`
- `Github Copilot - backup before model trust.pbix`
- `Github Copilot - backup before sensor drivers.pbix`
- `Github Copilot - backup before machine segments.pbix`

You can delete them once you are happy with the final report.
