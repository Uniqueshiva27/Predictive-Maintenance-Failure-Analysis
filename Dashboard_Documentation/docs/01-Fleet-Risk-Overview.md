# Tab 1: Fleet Risk Overview

> **Report:** `Github Copilot.pbix` · **Page 1 of 5** · **Canvas:** 3000 × 1440 px, FitToPage

## 1. Purpose

Operational view of current fleet failure risk. Shows how many machines are at risk, where the risk is concentrated, and which individual machines should be inspected first.

**Intended audience:** Maintenance planners, reliability engineers, plant/operations managers.

## 2. Business questions answered

- How many machines are monitored and how many are high risk?
- Which machine types carry the largest share of high-risk machines?
- Which machines combine a high failure probability with a short remaining useful life?
- Which machines should be inspected first, and what is driving their risk?
- How is the fleet distributed across RUL bands and top failure drivers?

## 3. Page layout

1. **Header** – page title and the *Machine Type* and *Risk Band* dropdown slicers.
2. **Row 1 – KPI cards** – Machines Monitored, High Risk Machines, High Risk %, Avg Failure Probability, Avg Predicted RUL.
3. **Row 2** – Risk Band donut (with centre total), High-Risk Share by Machine Type, Failure Probability vs Predicted RUL scatter.
4. **Row 3** – Inspection Priority table, Machines by RUL Band, Machines by Top Driver.

## 4. Filters and interactions

| Slicer | Field |
|---|---|
| Machine Type | `predictions[Machine Type]` |
| Risk Band | `predictions[Risk_Band]` |

- **Cross-filtering:** selecting a data point in any chart filters or highlights the other visuals on the page.
- **Page / report filters:** none by default – only the visual-level filters listed in the inventory below.

## 5. Visual inventory

| # | Visual | Type | Fields (role: field) | Visual-level filters |
|---|---|---|---|---|
| 1 | **Machine Type** | Slicer (dropdown) | Values: `predictions[Machine Type]` | – |
| 2 | **Risk Band** | Slicer (dropdown) | Values: `predictions[Risk_Band]` | – |
| 3 | **Machines Monitored** | Card | Values: `[Machines Monitored]` | – |
| 4 | **High Risk Machines** | Card | Values: `[High Risk Machines]` | – |
| 5 | **High Risk %** | Card | Values: `[High Risk %]` | – |
| 6 | **Avg Failure Probability** | Card | Values: `[Avg Failure Probability]` | – |
| 7 | **Avg Predicted RUL** | Card | Values: `[Avg Predicted RUL]` | – |
| 8 | **Risk Band** | Donut chart | Axis: `predictions[Risk_Band]`<br>Values: `[Machines]` | – |
| 9 | **High-Risk Share by Machine Type (Top 10)** | 100% stacked bar chart | Axis: `predictions[Machine Type]`<br>Legend: `predictions[Risk_Band]`<br>Tooltips: `[High Risk %]`<br>Values: `[Machines]` | Top 10 `predictions[Machine Type]` by [High Risk %] |
| 10 | **Failure Probability vs Predicted RUL (RUL ≤ 180 days)** | Scatter chart | Axis: `predictions[Machine_ID]`<br>Legend: `predictions[Risk_Band]`<br>X axis: `Average of predictions[Predicted_RUL]` (shown as “Predicted RUL (days)”)<br>Values: `Average of predictions[Failure_Probability]` (shown as “Failure Probability”) | `predictions[Predicted_RUL]` ≤ 180 |
| 11 | **Card – Machines Monitored** | Card | Values: `[Machines Monitored]` (shown as “Machines”) | – |
| 12 | **Inspection Priority (Top 25 by Failure Probability)** | Table | Values: `predictions[Machine_ID]` (shown as “Machine ID”)<br>Values: `predictions[Machine Type]`<br>Values: `Sum of predictions[Failure_Probability]` (shown as “Failure Probability”)<br>Values: `Sum of predictions[Predicted_RUL]` (shown as “Predicted RUL (days)”)<br>Values: `predictions[Top Driver]`<br>Values: `predictions[Risk_Band]` (shown as “Risk Band”) | Top 25 `predictions[Machine_ID]` by Sum of [Failure_Probability] |
| 13 | **Machines by RUL Band** | Clustered column chart | Axis: `predictions[RUL_Band]` (shown as “Predicted RUL”)<br>Values: `[Machines]` | – |
| 14 | **Machines by Top Driver** | Clustered bar chart | Axis: `predictions[Top Driver]`<br>Values: `[Machines]` | – |

**Static text elements:** “Fleet Risk Overview – predictions”

## 6. How to read this page

- **Risk bands** come from the model's failure probability: **High ≥ 70 %**, **Medium 30–70 %**, **Low < 30 %** (column `predictions[Risk_Band]`).
- **Scatter:** each dot is a machine (RUL ≤ 180 days only). The dashed vertical line marks **30 days RUL** and the dashed horizontal line the **70 % high-risk threshold** – the top-left area is the *inspect first* zone.
- **Inspection Priority** lists the 25 machines with the highest failure probability *in the current filter context*; the red data bar visualises the probability.
- **Machines by Top Driver** counts machines by the feature with the largest SHAP contribution to their individual prediction.
- Click any bar, donut slice or table row to cross-filter the rest of the page.

## 7. Key insights (data as of documentation date)

- 500,000 machines monitored; 15,686 (3.1 %) are High risk.
- Average failure probability is 6.0 % and average predicted RUL is ≈ 452 days.
- Operational Hours is the most common top driver among high-risk machines.

## 8. Measures

Every measure placed on the page, plus the measures they depend on.

| Measure | Home table | Format | Display folder |
|---|---|---|---|
| `Machines Monitored` | predictions | `#,0` | Fleet Risk |
| `High Risk Machines` | predictions | `#,0` | Fleet Risk |
| `High Risk %` | predictions | `0.0%` | Fleet Risk |
| `Avg Failure Probability` | predictions | `0.0%` | Fleet Risk |
| `Avg Predicted RUL` | predictions | `#,0 "days"` | Fleet Risk |
| `Machines` | predictions | `#,0` | Fleet Risk |

### Machines Monitored

```dax
Machines Monitored =
COUNTROWS ( predictions )
```

### High Risk Machines

```dax
High Risk Machines =
CALCULATE ( COUNTROWS ( predictions ), KEEPFILTERS ( predictions[Risk_Band] = "High" ) )
```

### High Risk %

```dax
High Risk % =
DIVIDE ( [High Risk Machines], [Machines Monitored] )
```

### Avg Failure Probability

```dax
Avg Failure Probability =
AVERAGE ( predictions[Failure_Probability] )
```

### Avg Predicted RUL

```dax
Avg Predicted RUL =
AVERAGE ( predictions[Predicted_RUL] )
```

### Machines

```dax
Machines =
COUNTROWS ( predictions )
```

## 9. Calculated columns and tables

### predictions[Machine Type]

Column – data type `string`

```dax
SUBSTITUTE ( predictions[Machine_Type], "_", " " )
```

### predictions[Top Driver]

Column – data type `string`

```dax
SWITCH ( predictions[Top_Driver], "Operational_Hours", "Operational Hours", "Sound_dB", "Sound Level", "Power_Consumption_kW", "Power Consumption", "Vibration_mms", "Vibration", "Oil_Level_pct", "Oil Level", "Last_Maintenance_Days_Ago", "Days Since Maint.", "Coolant_Level_pct", "Coolant Level", "Installation_Year", "Machine Age", "Temperature_C", "Temperature", "Maintenance_History_Count", "Maint. History", SUBSTITUTE ( predictions[Top_Driver], "_", " " ) )
```

## 10. Data sources

| Table | Columns referenced by this page (visuals and measures) |
|---|---|
| `predictions` | `Failure_Probability`, `Machine Type`, `Machine_ID`, `Predicted_RUL`, `RUL_Band`, `Risk_Band`, `Top Driver` |

## 11. Limitations and maintenance notes

- The scatter is limited to Predicted RUL ≤ 180 days and Power BI samples points for display.
- Risk-band and RUL-band thresholds are produced upstream in the Python pipeline, not in Power BI.
- To regenerate this document after report changes, see [README.md](README.md#regenerating-this-documentation).
