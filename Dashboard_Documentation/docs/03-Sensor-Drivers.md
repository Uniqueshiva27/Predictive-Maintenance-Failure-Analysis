# Tab 3: Sensor Drivers

> **Report:** `Github Copilot.pbix` · **Page 3 of 5** · **Canvas:** 3000 × 1440 px, FitToPage

## 1. Purpose

Explains *why* the model predicts failures – which features carry the most influence (SHAP) and how sensor readings differ between failing and normal machines.

**Intended audience:** Reliability engineers, data scientists, maintenance SMEs validating model logic.

## 2. Business questions answered

- Which features drive the failure model the most?
- How many features explain most of the model's behaviour (Pareto)?
- How does the failure rate change across vibration and oil-level ranges?
- Which sensors look different for machines that failed vs normal ones?

## 3. Page layout

1. **Header** – title plus *Asset* (machine type) and *Model* dropdown slicers.
2. **Row 1** – SHAP Feature Importance bar chart, Pareto combo chart with *Top 4 drivers* callout, Top Driver callout and Feature Share treemap.
3. **Row 2** – Failure Rate heatmap (Vibration × Oil Level) and Sensor Profiles (Normal vs Failed).
4. **Footer** – number of features analysed and SHAP source.

## 4. Filters and interactions

| Slicer | Field |
|---|---|
| Asset | `predictions[Machine Type]` |
| Model | `feature_importance[Model]` |

- **Cross-filtering:** selecting a data point in any chart filters or highlights the other visuals on the page.
- **Page / report filters:** none by default – only the visual-level filters listed in the inventory below.

## 5. Visual inventory

| # | Visual | Type | Fields (role: field) | Visual-level filters |
|---|---|---|---|---|
| 1 | **Asset** | Slicer (dropdown) | Values: `predictions[Machine Type]` | – |
| 2 | **Model** | Slicer (dropdown) | Values: `feature_importance[Model]` | – |
| 3 | **SHAP Feature Importance**<br>*Mean absolute SHAP value · normalized share (top 10 features)* | Clustered bar chart | Axis: `feature_importance[Feature Name]` (shown as “Feature”)<br>Values: `[Importance Share]` | `feature_importance[Rank]` ≤ 10 |
| 4 | **Pareto · Driver Contribution** | Line & clustered column combo | Axis: `feature_importance[Feature Name]` (shown as “Feature”)<br>Values: `[Importance Share]` (shown as “Feature share”)<br>Line values: `[Cumulative Share]` (shown as “Cumulative share”) | `feature_importance[Rank]` ≤ 10 |
| 5 | **Card – Top Driver Title** | Card | Values: `[Top Driver Title]` | – |
| 6 | **Card – Top 4 Share Label** | Card | Values: `[Top 4 Share Label]` | – |
| 7 | **Card – Top Driver Share Label** | Card | Values: `[Top Driver Share Label]` | – |
| 8 | **Feature Share**<br>*Top 6 features + all others* | Treemap | Category: `feature_importance[Feature Group]` (shown as “Feature”)<br>Values: `[Importance Share]` | – |
| 9 | **Failure Rate · Vibration × Oil Level**<br>*Actual failure-within-7-days rate by sensor quintile · brighter red = higher rate* | Matrix (heatmap) | Columns: `predictions[Oil Level Band]` (shown as “Oil level”)<br>Rows: `predictions[Vibration Level]` (shown as “Vibration”)<br>Values: `[Failure Rate]`<br>Conditional format / dynamic value: `[Failure Rate Color]` | – |
| 10 | **Sensor Profiles · Normal vs Failed**<br>*Mean standardized sensor value (z-score) for machines that failed within 7 days vs normal* | Clustered column chart | Axis: `Sensor List[Sensor]`<br>Legend: `predictions[Failure Status]`<br>Values: `[Avg Z-Score]` (shown as “Mean z-score”) | – |
| 11 | **Card – Features Analyzed Label** | Card | Values: `[Features Analyzed Label]` | – |
| 12 | **Card – SHAP Source Label** | Card | Values: `[SHAP Source Label]` | – |

**Static text elements:** “❙❙❙”; “Sensor Drivers – feature_importance”; “Highest model influence”; “⚙”; “\|”

## 6. How to read this page

- **Importance share** = a feature's mean |SHAP| ÷ the sum over all features (`feature_importance[Importance_Pct]`).
- **Pareto:** bars = individual share (left axis), yellow line = cumulative share (right axis, 0–100 %).
- **Heatmap:** machines are split into fleet quintiles of vibration (rows) and oil level (columns). Cell value = actual *failure within 7 days* rate; brighter red = higher rate relative to the other cells.
- **Sensor Profiles:** mean z-score of each sensor for Failed vs Normal machines. A large gap means the sensor separates failing machines well.
- The *Asset* slicer affects the heatmap and sensor profiles (predictions table); the *Model* slicer affects the SHAP visuals (feature_importance table).

## 7. Key insights (data as of documentation date)

- Top driver: Operational Hours (≈ 40 % share), then Sound Level (20 %), Vibration (16 %) and Oil Level (11 %); the top 4 explain ≈ 86 %.
- 17 features analysed; the bottom 11 together contribute < 5 %.
- Failure rate rises with vibration (≈ 4.6 % → 7.8 %); oil level has little effect.
- Failed machines average +1.57 σ on Operational Hours; other sensors show only small differences.

## 8. Measures

Every measure placed on the page, plus the measures they depend on.

| Measure | Home table | Format | Display folder |
|---|---|---|---|
| `Importance Share` | feature_importance | `0.0%` | Sensor Drivers |
| `Cumulative Share` | feature_importance | `0%` | Sensor Drivers |
| `Top Driver Title` | feature_importance | – | Sensor Drivers |
| `Top 4 Share Label` | feature_importance | – | Sensor Drivers |
| `Top Driver Share Label` | feature_importance | – | Sensor Drivers |
| `Failure Rate` | predictions | `0.0%` | Sensor Drivers |
| `Failure Rate Color` | predictions | – | Sensor Drivers |
| `Avg Z-Score` | predictions | `0.00` | Sensor Drivers |
| `Features Analyzed Label` | feature_importance | – | Sensor Drivers |
| `SHAP Source Label` | feature_importance | – | Sensor Drivers |
| `Top Driver Name` | feature_importance | – | Sensor Drivers |

### Importance Share

```dax
Importance Share =
SUM ( feature_importance[Importance_Pct] )
```

### Cumulative Share

```dax
Cumulative Share =
VAR r = MAX ( feature_importance[Rank] )
RETURN
    CALCULATE (
        SUM ( feature_importance[Importance_Pct] ),
        REMOVEFILTERS ( feature_importance[Feature], feature_importance[Feature Name], feature_importance[Feature Group], feature_importance[Rank] ),
        feature_importance[Rank] <= r
    )
```

### Top Driver Title

```dax
Top Driver Title =
"Top Driver: " & [Top Driver Name]
```

### Top 4 Share Label

```dax
Top 4 Share Label =
"Top 4 drivers = " & FORMAT ( CALCULATE ( SUM ( feature_importance[Importance_Pct] ), feature_importance[Rank] <= 4 ), "0%" )
```

### Top Driver Share Label

```dax
Top Driver Share Label =
VAR r = MIN ( feature_importance[Rank] )
RETURN FORMAT ( CALCULATE ( SUM ( feature_importance[Importance_Pct] ), feature_importance[Rank] = r ), "0%" ) & " share"
```

### Failure Rate

```dax
Failure Rate =
DIVIDE ( CALCULATE ( COUNTROWS ( predictions ), predictions[Failure_Within_7_Days] = TRUE () ), COUNTROWS ( predictions ) )
```

### Failure Rate Color

_Heat-map colour: interpolates dark maroon to red between the min and max failure rate of the visible Vibration x Oil grid._

```dax
Failure Rate Color =
VAR fr = [Failure Rate]
VAR grid = ALLSELECTED ( predictions[Vibration Level], predictions[Oil Level Band] )
VAR mn = MINX ( grid, [Failure Rate] )
VAR mx = MAXX ( grid, [Failure Rate] )
VAR t = IF ( mx > mn, DIVIDE ( fr - mn, mx - mn ), 0.5 )
VAR r = ROUND ( 58 + t * ( 240 - 58 ), 0 )
VAR g = ROUND ( 18 + t * ( 48 - 18 ), 0 )
VAR b = ROUND ( 32 + t * ( 58 - 32 ), 0 )
VAR hx = "0123456789ABCDEF"
RETURN
    IF ( ISBLANK ( fr ), BLANK (),
        "#"
            & MID ( hx, INT ( r / 16 ) + 1, 1 ) & MID ( hx, MOD ( r, 16 ) + 1, 1 )
            & MID ( hx, INT ( g / 16 ) + 1, 1 ) & MID ( hx, MOD ( g, 16 ) + 1, 1 )
            & MID ( hx, INT ( b / 16 ) + 1, 1 ) & MID ( hx, MOD ( b, 16 ) + 1, 1 ) )
```

### Avg Z-Score

_Mean standardized (z-score) value of the selected sensor for the current Failure Status, relative to all machines in the current filter context._

```dax
Avg Z-Score =
VAR s = SELECTEDVALUE ( 'Sensor List'[Sensor] )
RETURN
    SWITCH (
        s,
        "Operational Hours", DIVIDE ( AVERAGE ( predictions[Operational_Hours] ) - CALCULATE ( AVERAGE ( predictions[Operational_Hours] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Operational_Hours] ), REMOVEFILTERS ( predictions[Failure Status] ) ) ),
        "Sound Level", DIVIDE ( AVERAGE ( predictions[Sound_dB] ) - CALCULATE ( AVERAGE ( predictions[Sound_dB] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Sound_dB] ), REMOVEFILTERS ( predictions[Failure Status] ) ) ),
        "Vibration", DIVIDE ( AVERAGE ( predictions[Vibration_mms] ) - CALCULATE ( AVERAGE ( predictions[Vibration_mms] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Vibration_mms] ), REMOVEFILTERS ( predictions[Failure Status] ) ) ),
        "Oil Level", DIVIDE ( AVERAGE ( predictions[Oil_Level_pct] ) - CALCULATE ( AVERAGE ( predictions[Oil_Level_pct] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Oil_Level_pct] ), REMOVEFILTERS ( predictions[Failure Status] ) ) ),
        "Power Consumption", DIVIDE ( AVERAGE ( predictions[Power_Consumption_kW] ) - CALCULATE ( AVERAGE ( predictions[Power_Consumption_kW] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Power_Consumption_kW] ), REMOVEFILTERS ( predictions[Failure Status] ) ) ),
        "Days Since Maint.", DIVIDE ( AVERAGE ( predictions[Last_Maintenance_Days_Ago] ) - CALCULATE ( AVERAGE ( predictions[Last_Maintenance_Days_Ago] ), REMOVEFILTERS ( predictions[Failure Status] ) ), CALCULATE ( STDEV.P ( predictions[Last_Maintenance_Days_Ago] ), REMOVEFILTERS ( predictions[Failure Status] ) ) )
    )
```

### Features Analyzed Label

```dax
Features Analyzed Label =
FORMAT ( DISTINCTCOUNT ( feature_importance[Feature] ), "0" ) & " features analyzed"
```

### SHAP Source Label

```dax
SHAP Source Label =
"Mean |SHAP| from " & CONCATENATEX ( VALUES ( feature_importance[Model] ), feature_importance[Model], ", " ) & " · failure-within-7-days model"
```

### Top Driver Name

```dax
Top Driver Name =
VAR r = MIN ( feature_importance[Rank] )
RETURN CALCULATE ( MAX ( feature_importance[Feature Name] ), feature_importance[Rank] = r )
```

## 9. Calculated columns and tables

### feature_importance[Feature Group]

Column – data type `string`, sorted by `Feature Group Order`

```dax
IF ( feature_importance[Rank] <= 6, feature_importance[Feature Name], "Other features" )
```

### feature_importance[Feature Name]

Column – data type `string`, sorted by `Rank`

```dax
SWITCH ( feature_importance[Feature], "Operational_Hours", "Operational Hours", "Sound_dB", "Sound Level", "Power_Consumption_kW", "Power Consumption", "Vibration_mms", "Vibration", "Oil_Level_pct", "Oil Level", "Last_Maintenance_Days_Ago", "Days Since Maint.", "Coolant_Level_pct", "Coolant Level", "Installation_Year", "Machine Age", "Temperature_C", "Temperature", "Maintenance_History_Count", "Maint. History", "Failure_History_Count", "Failure History", "Error_Codes_Last_30_Days", "Error Codes (30d)", "Heat_Index", "Heat Index", "Laser_Intensity", "Laser Intensity", "AI_Override_Events", "AI Overrides", "Hydraulic_Pressure_bar", "Hydraulic Pressure", "Coolant_Flow_L_min", "Coolant Flow", SUBSTITUTE ( feature_importance[Feature], "_", " " ) )
```

### predictions[Failure Status]

Column – data type `string`, sorted by `Failure Status Order`

```dax
IF ( predictions[Failure_Within_7_Days], "Failed", "Normal" )
```

### predictions[Machine Type]

Column – data type `string`

```dax
SUBSTITUTE ( predictions[Machine_Type], "_", " " )
```

### predictions[Oil Level Band]

Column – data type `string`, sorted by `Oil Level Band Order`

```dax
VAR o = predictions[Oil_Level_pct]
-- quintile cut points of Oil_Level_pct across the fleet
RETURN SWITCH ( TRUE (), o <= 53.2, "Very low", o <= 64.96, "Low", o <= 75.09, "Medium", o <= 86.9, "High", "Very high" )
```

### predictions[Vibration Level]

Column – data type `string`, sorted by `Vibration Level Order`

```dax
VAR v = predictions[Vibration_mms]
-- quintile cut points of Vibration_mms across the fleet
RETURN SWITCH ( TRUE (), v <= 5.78, "Very low", v <= 8.73, "Low", v <= 11.27, "Medium", v <= 14.2, "High", "Very high" )
```

### feature_importance[Feature Group Order]

Column – data type `int64`, hidden

```dax
MIN ( feature_importance[Rank], 7 )
```

### predictions[Failure Status Order]

Column – data type `int64`, hidden

```dax
IF ( predictions[Failure_Within_7_Days], 2, 1 )
```

### predictions[Oil Level Band Order]

Column – data type `int64`, hidden

```dax
VAR o = predictions[Oil_Level_pct]
RETURN SWITCH ( TRUE (), o <= 53.2, 1, o <= 64.96, 2, o <= 75.09, 3, o <= 86.9, 4, 5 )
```

### predictions[Vibration Level Order]

Column – data type `int64`, hidden

```dax
VAR v = predictions[Vibration_mms]
RETURN SWITCH ( TRUE (), v <= 5.78, 5, v <= 8.73, 4, v <= 11.27, 3, v <= 14.2, 2, 1 )
```

## 10. Data sources

| Table | Columns referenced by this page (visuals and measures) |
|---|---|
| `Sensor List` | `Sensor` |
| `feature_importance` | `Feature`, `Feature Group`, `Feature Name`, `Importance_Pct`, `Model`, `Rank` |
| `predictions` | `Failure Status`, `Failure_Within_7_Days`, `Last_Maintenance_Days_Ago`, `Machine Type`, `Oil Level Band`, `Oil_Level_pct`, `Operational_Hours`, `Power_Consumption_kW`, `Sound_dB`, `Vibration Level`, `Vibration_mms` |

## 11. Limitations and maintenance notes

- Quintile cut-points for vibration and oil level are hard-coded in the calculated columns (derived from the data at build time).
- Box plots are not native to Power BI – sensor distributions are summarised as mean z-scores.
- There is no date column, so no time-period filter is available.
- To regenerate this document after report changes, see [README.md](README.md#regenerating-this-documentation).
