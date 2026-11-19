# Dashboard Documentation – Github Copilot.pbix

Functional and technical documentation for every tab of the Predictive Maintenance Power BI report. For a short end-user guide see [ReadMe/README.md](../ReadMe/README.md).

## Tabs

| # | Tab | Document | Data visuals | Measures | Purpose |
|---|---|---|---|---|---|
| 1 | Fleet Risk Overview | [01-Fleet-Risk-Overview.md](01-Fleet-Risk-Overview.md) | 14 | 6 | Operational view of current fleet failure risk. |
| 2 | Model Trust | [02-Model-Trust.md](02-Model-Trust.md) | 29 | 32 | Shows how reliable the predictive models are, so users can calibrate how much to trust the risk scores on the other tabs. |
| 3 | Sensor Drivers | [03-Sensor-Drivers.md](03-Sensor-Drivers.md) | 12 | 11 | Explains *why* the model predicts failures – which features carry the most influence (SHAP) and how sensor readings differ between failing and normal machines. |
| 4 | Machine Segments | [04-Machine-Segments.md](04-Machine-Segments.md) | 11 | 16 | Shows the K-means machine segments (clusters), how they separate in PCA space, and which segment carries the most failure risk. |
| 5 | Page 1 | [05-Page-1.md](05-Page-1.md) | 0 | 0 | Blank placeholder page (1920 × 1080) with no visuals yet. |

## Data model

| Table | Kind | Measures | Calculated columns |
|---|---|---|---|
| `Model Metrics Long` | Calculated table (DAX) | 0 | 0 |
| `Model Summary` | Calculated table (DAX) | 0 | 0 |
| `Sensor List` | Imported | 0 | 0 |
| `cluster_summary` | Imported | 0 | 0 |
| `confusion_matrix` | Imported | 22 | 0 |
| `factory_sensor_simulator_2040` | Imported | 0 | 0 |
| `feature_importance` | Imported | 8 | 3 |
| `model_metrics` | Imported | 12 | 0 |
| `predictions` | Imported | 23 | 8 |

### Relationships

| From (many) | To (one) | Cardinality | Cross-filter |
|---|---|---|---|
| `predictions.Machine_ID` | `factory_sensor_simulator_2040.Machine_ID` | Many → One | Both |
| `predictions.Cluster` | `cluster_summary.Cluster` | Many → One | Single |
| `confusion_matrix.Model` | `model_metrics.Model` | Many → One | Single |
| `feature_importance.Model` | `model_metrics.Model` | Many → One | Single |

## Visual theme

All tabs use the custom **FleetRiskDark** theme (`Report/StaticResources/RegisteredResources/FleetRiskDark.json`): page background `#0B1426`, visual background `#13203A`, borders `#2A3A5C`, text `#FFFFFF` / `#AEB9CC`. Semantic colours: High / bad `#F0505A`, Medium `#F5B335`, Low / good `#1FD1A0`, accent cyan `#22D3EE` / `#3FD6F2`.

## Regenerating this documentation

The tab documents are generated from the report definition (PBIR inside the `.pbix`) and a TMDL export of the semantic model.

1. Open the report in Power BI Desktop and export the semantic model to a TMDL folder (Power BI Modeling MCP server `ExportToTmdlFolder`, or Tabular Editor ▸ *Save to folder* in TMDL format).
2. From the project folder run:

```powershell
python docs\generate_docs.py "Github Copilot.pbix" <tmdl-folder> docs
```

Narrative sections (purpose, questions, how to read, insights, limitations) live in the `NARRATIVE` dictionary in `generate_docs.py`; visual inventories, filters, measures, DAX and data sources are extracted automatically.
