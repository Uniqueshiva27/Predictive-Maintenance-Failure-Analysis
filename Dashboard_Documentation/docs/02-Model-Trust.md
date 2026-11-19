# Tab 2: Model Trust

> **Report:** `Github Copilot.pbix` · **Page 2 of 5** · **Canvas:** 3000 × 1440 px, FitToPage

## 1. Purpose

Shows how reliable the predictive models are, so users can calibrate how much to trust the risk scores on the other tabs.

**Intended audience:** Data scientists, reliability engineers, decision makers approving model use.

## 2. Business questions answered

- How accurate is the selected failure-prediction model (Accuracy, Precision, Recall, F1, ROC-AUC)?
- How accurate is the Remaining-Useful-Life regression model (MAE, RMSE, R²)?
- How does LightGBM compare with Random Forest and XGBoost?
- How many failures are missed and what might that cost?
- Is the false-alarm rate within the acceptable target?

## 3. Page layout

1. **Header** – title, subtitle and a *Best model* badge.
2. **Row 1 – 8 KPI cards** – five classification metrics for the selected model and three RUL-regression metrics.
3. **Row 2** – Classification metrics by model (clustered columns) and a 2 × 2 confusion matrix built from cards.
4. **Row 3** – Missed failures (FN) panel, False alarm rate gauge, Model selection summary.
5. **Footer** – source note and page number.

## 4. Filters and interactions

This page has no slicers.

- **Cross-filtering:** selecting a data point in any chart filters or highlights the other visuals on the page.
- **Page / report filters:** none by default – only the visual-level filters listed in the inventory below.

## 5. Visual inventory

| # | Visual | Type | Fields (role: field) | Visual-level filters |
|---|---|---|---|---|
| 1 | **Card – Best Model Label** | Card | Values: `[Best Model Label]` | – |
| 2 | **Accuracy** | Card | Values: `[Model Accuracy]` (shown as “LightGBM · validation”) | – |
| 3 | **Precision** | Card | Values: `[Model Precision]` (shown as “LightGBM · validation”) | – |
| 4 | **Recall** | Card | Values: `[Model Recall]` (shown as “LightGBM · validation”) | – |
| 5 | **F1** | Card | Values: `[Model F1]` (shown as “LightGBM · validation”) | – |
| 6 | **ROC-AUC** | Card | Values: `[Model ROC-AUC]` (shown as “LightGBM · validation”) | – |
| 7 | **RUL MAE** | Card | Values: `[RUL MAE]` (shown as “RF Regressor · validation”) | – |
| 8 | **RMSE** | Card | Values: `[RUL RMSE]` (shown as “RF Regressor · validation”) | – |
| 9 | **R squared** | Card | Values: `[R Squared]` (shown as “RF Regressor · validation”) | – |
| 10 | **Classification metrics by model**<br>*Validation results – Random Forest vs XGBoost vs LightGBM* | Clustered column chart | Axis: `Model Metrics Long[Metric]`<br>Legend: `Model Metrics Long[Model]`<br>Values: `Sum of Model Metrics Long[Value]` (shown as “Metric value”) | – |
| 11 | **Card – Confusion Matrix Subtitle** | Card | Values: `[Confusion Matrix Subtitle]` | – |
| 12 | **TN** | Card | Values: `[TN]` | – |
| 13 | **FP** | Card | Values: `[FP]` | – |
| 14 | **Card – TN %** | Card | Values: `[TN %]` | – |
| 15 | **Card – FP %** | Card | Values: `[FP %]` | – |
| 16 | **FN** | Card | Values: `[FN]` | – |
| 17 | **TP** | Card | Values: `[TP]` | – |
| 18 | **Card – FN %** | Card | Values: `[FN %]` | – |
| 19 | **Card – TP %** | Card | Values: `[TP %]` | – |
| 20 | **Card – FN** | Card | Values: `[FN]` | – |
| 21 | **Gauge** | Gauge | Maximum: `[Gauge Max]`<br>Minimum: `[Gauge Min]`<br>Target: `[False Alarm Target]`<br>Values: `[False Alarm Rate]` | – |
| 22 | **Card – Selected Model** | Card | Values: `[Selected Model]` | – |
| 23 | **Card – Exposure Label** | Card | Values: `[Exposure Label]` | – |
| 24 | **Table** | Table | Values: `Model Summary[Item]` (shown as “Measure”)<br>Values: `Model Summary[Value]` (shown as “LightGBM”) | – |
| 25 | **Card – Exposure Note** | Card | Values: `[Exposure Note]` | – |
| 26 | **Card – Miss Rate Label** | Card | Values: `[Miss Rate Label]` | – |
| 27 | **Card – False Alarm Detail** | Card | Values: `[False Alarm Detail]` | – |
| 28 | **Clustered bar chart** | Clustered bar chart | Values: `[Miss Rate]` | – |
| 29 | **Card – False Alarm Status** | Card | Values: `[False Alarm Status]` | – |

**Static text elements:** “Model Trust – model_metrics & confusion_matrix”; “Predictive Maintenance \| Model validation & failure detection”; “Validation data”; “Confusion matrix \| LightGBM”; “PREDICTED”; “No failure”; “Failure”; “No failure”; “ACTUAL”; “Failure”; “Percentages of all observations”; “Missed failures (FN)”; “False alarm rate”; “Model selection summary”; “⚠”; “✔”; “Actual failure predicted as no failure”; “Recommended for threshold review”; “Source: model_metrics.csv + confusion_matrix.csv”; “MODEL TRUST / 02”

## 6. How to read this page

- The **selected model** is the row in `model_metrics` with `Selected_For_Dashboard = TRUE` (currently LightGBM). All classification KPI cards follow this flag.
- **Confusion matrix:** TN = healthy predicted healthy, FP = false alarm, FN = missed failure, TP = failure caught. Percentages are of all validation observations.
- **Miss rate** = FN ÷ (FN + TP). **False alarm rate** = FP ÷ (FP + TN), compared with a 3 % target on the gauge.
- **Estimated exposure** = FN × *Cost per Missed Failure* (illustrative $5,000).

## 7. Key insights (data as of documentation date)

- LightGBM: Accuracy 96.4 %, Precision 71.0 %, Recall 66.4 %, F1 68.6 %, ROC-AUC 98.3 %.
- Validation set: 100,000 observations – TN 92,422, FP 1,618, FN 2,002, TP 3,958.
- False-alarm rate 1.7 % (within the 3 % target); miss rate 33.6 %.
- RUL model (Random Forest Regressor): MAE 38.8 days, RMSE 49.1 days, R² 0.971.

## 8. Measures

Every measure placed on the page, plus the measures they depend on.

| Measure | Home table | Format | Display folder |
|---|---|---|---|
| `Best Model Label` | model_metrics | – | Model Trust |
| `Model Accuracy` | model_metrics | `0.0%` | Model Trust |
| `Model Precision` | model_metrics | `0.0%` | Model Trust |
| `Model Recall` | model_metrics | `0.0%` | Model Trust |
| `Model F1` | model_metrics | `0.0%` | Model Trust |
| `Model ROC-AUC` | model_metrics | `0.0%` | Model Trust |
| `RUL MAE` | model_metrics | `0.0 "d"` | Model Trust |
| `RUL RMSE` | model_metrics | `0.0 "d"` | Model Trust |
| `R Squared` | model_metrics | `0.000` | Model Trust |
| `Confusion Matrix Subtitle` | confusion_matrix | – | Model Trust |
| `TN` | confusion_matrix | `#,0` | Model Trust |
| `FP` | confusion_matrix | `#,0` | Model Trust |
| `TN %` | confusion_matrix | `0.0%` | Model Trust |
| `FP %` | confusion_matrix | `0.0%` | Model Trust |
| `FN` | confusion_matrix | `#,0` | Model Trust |
| `TP` | confusion_matrix | `#,0` | Model Trust |
| `FN %` | confusion_matrix | `0.0%` | Model Trust |
| `TP %` | confusion_matrix | `0.0%` | Model Trust |
| `Gauge Max` | confusion_matrix | `0%` | Model Trust |
| `Gauge Min` | confusion_matrix | `0%` | Model Trust |
| `False Alarm Target` | confusion_matrix | `0%` | Model Trust |
| `False Alarm Rate` | confusion_matrix | `0.0%` | Model Trust |
| `Selected Model` | model_metrics | – | Model Trust |
| `Exposure Label` | confusion_matrix | – | Model Trust |
| `Exposure Note` | confusion_matrix | – | Model Trust |
| `Miss Rate Label` | confusion_matrix | – | Model Trust |
| `False Alarm Detail` | confusion_matrix | – | Model Trust |
| `Miss Rate` | confusion_matrix | `0.0%` | Model Trust |
| `False Alarm Status` | confusion_matrix | – | Model Trust |
| `Total Observations` | confusion_matrix | `#,0` | Model Trust |
| `Estimated Exposure` | confusion_matrix | `\$#,0` | Model Trust |
| `Cost per Missed Failure` | confusion_matrix | `\$#,0` | Model Trust |

### Best Model Label

```dax
Best Model Label =
"Best model: " & [Selected Model]
```

### Model Accuracy

```dax
Model Accuracy =
CALCULATE ( MAX ( model_metrics[Accuracy] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### Model Precision

```dax
Model Precision =
CALCULATE ( MAX ( model_metrics[Precision] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### Model Recall

```dax
Model Recall =
CALCULATE ( MAX ( model_metrics[Recall] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### Model F1

```dax
Model F1 =
CALCULATE ( MAX ( model_metrics[F1] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### Model ROC-AUC

```dax
Model ROC-AUC =
CALCULATE ( MAX ( model_metrics[ROC_AUC] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### RUL MAE

```dax
RUL MAE =
CALCULATE ( MAX ( model_metrics[MAE_days] ), NOT ISBLANK ( model_metrics[MAE_days] ) )
```

### RUL RMSE

```dax
RUL RMSE =
CALCULATE ( MAX ( model_metrics[RMSE_days] ), NOT ISBLANK ( model_metrics[RMSE_days] ) )
```

### R Squared

```dax
R Squared =
CALCULATE ( MAX ( model_metrics[R2] ), NOT ISBLANK ( model_metrics[R2] ) )
```

### Confusion Matrix Subtitle

```dax
Confusion Matrix Subtitle =
"Validation set: " & FORMAT ( [Total Observations], "#,0" ) & " observations"
```

### TN

```dax
TN =
CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "TN" )
```

### FP

```dax
FP =
CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "FP" )
```

### TN %

```dax
TN % =
DIVIDE ( [TN], [Total Observations] )
```

### FP %

```dax
FP % =
DIVIDE ( [FP], [Total Observations] )
```

### FN

```dax
FN =
CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "FN" )
```

### TP

```dax
TP =
CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "TP" )
```

### FN %

```dax
FN % =
DIVIDE ( [FN], [Total Observations] )
```

### TP %

```dax
TP % =
DIVIDE ( [TP], [Total Observations] )
```

### Gauge Max

```dax
Gauge Max =
0.10
```

### Gauge Min

```dax
Gauge Min =
0
```

### False Alarm Target

```dax
False Alarm Target =
0.03
```

### False Alarm Rate

```dax
False Alarm Rate =
DIVIDE ( [FP], [FP] + [TN] )
```

### Selected Model

```dax
Selected Model =
CALCULATE ( MAX ( model_metrics[Model] ), model_metrics[Selected_For_Dashboard] = TRUE () )
```

### Exposure Label

```dax
Exposure Label =
FORMAT ( [Estimated Exposure], "$#,0" ) & " estimated exposure"
```

### Exposure Note

```dax
Exposure Note =
"Illustrative cost: " & FORMAT ( [FN], "#,0" ) & " × " & FORMAT ( [Cost per Missed Failure], "$#,0" ) & " per missed failure"
```

### Miss Rate Label

```dax
Miss Rate Label =
"Miss rate: " & FORMAT ( [Miss Rate], "0.0%" ) & " of actual failures"
```

### False Alarm Detail

```dax
False Alarm Detail =
FORMAT ( [FP], "#,0" ) & " false positives / " & FORMAT ( [FP] + [TN], "#,0" ) & " actual negatives"
```

### Miss Rate

```dax
Miss Rate =
DIVIDE ( [FN], [FN] + [TP] )
```

### False Alarm Status

```dax
False Alarm Status =
IF ( [False Alarm Rate] <= [False Alarm Target], "✔  Target ≤ " & FORMAT ( [False Alarm Target], "0%" ) & " · Within target", "✖  Target ≤ " & FORMAT ( [False Alarm Target], "0%" ) & " · Above target" )
```

### Total Observations

```dax
Total Observations =
SUM ( confusion_matrix[Count] )
```

### Estimated Exposure

```dax
Estimated Exposure =
[FN] * [Cost per Missed Failure]
```

### Cost per Missed Failure

```dax
Cost per Missed Failure =
5000
```

## 9. Calculated columns and tables

### Calculated table: Model Metrics Long

```dax
VAR m =
    ADDCOLUMNS (
        FILTER ( model_metrics, NOT ISBLANK ( model_metrics[Accuracy] ) ),
        "@Order", SWITCH ( model_metrics[Model], "Random Forest", 1, "XGBoost", 2, "LightGBM", 3, 9 )
    )
RETURN
UNION (
    SELECTCOLUMNS ( m, "Model", model_metrics[Model], "Model Order", [@Order], "Metric", "Accuracy", "Metric Order", 1, "Value", model_metrics[Accuracy] ),
    SELECTCOLUMNS ( m, "Model", model_metrics[Model], "Model Order", [@Order], "Metric", "Precision", "Metric Order", 2, "Value", model_metrics[Precision] ),
    SELECTCOLUMNS ( m, "Model", model_metrics[Model], "Model Order", [@Order], "Metric", "Recall", "Metric Order", 3, "Value", model_metrics[Recall] ),
    SELECTCOLUMNS ( m, "Model", model_metrics[Model], "Model Order", [@Order], "Metric", "F1", "Metric Order", 4, "Value", model_metrics[F1] ),
    SELECTCOLUMNS ( m, "Model", model_metrics[Model], "Model Order", [@Order], "Metric", "ROC-AUC", "Metric Order", 5, "Value", model_metrics[ROC_AUC] )
)
```

### Calculated table: Model Summary

```dax
VAR _sel = FILTER ( model_metrics, model_metrics[Selected_For_Dashboard] = TRUE () )
VAR _f1 = MAXX ( _sel, model_metrics[F1] )
VAR _auc = MAXX ( _sel, model_metrics[ROC_AUC] )
VAR _tp = CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "TP" )
VAR _fnc = CALCULATE ( SUM ( confusion_matrix[Count] ), confusion_matrix[Label] = "FN" )
RETURN
SELECTCOLUMNS (
    {
        ( "Best F1", 1, FORMAT ( _f1, "0.0%" ) ),
        ( "Best ROC-AUC", 2, FORMAT ( _auc, "0.0%" ) ),
        ( "Failure detection", 3, FORMAT ( _tp, "#,0" ) & " / " & FORMAT ( _tp + _fnc, "#,0" ) )
    },
    "Item", [Value1], "Order", [Value2], "Value", [Value3]
)
```

## 10. Data sources

| Table | Columns referenced by this page (visuals and measures) |
|---|---|
| `Model Metrics Long` | `Metric`, `Model`, `Value` |
| `Model Summary` | `Item`, `Value` |
| `confusion_matrix` | `Count`, `Label` |
| `model_metrics` | `Accuracy`, `F1`, `MAE_days`, `Model`, `Precision`, `R2`, `RMSE_days`, `ROC_AUC`, `Recall`, `Selected_For_Dashboard` |

## 11. Limitations and maintenance notes

- KPI card sub-labels ('LightGBM · validation', 'RF Regressor · validation') are static text.
- Cost per missed failure and the false-alarm target are fixed measures – edit `Cost per Missed Failure` and `False Alarm Target` to change them.
- Random Forest has a marginally higher precision (71.05 % vs 70.98 %) than LightGBM.
- To regenerate this document after report changes, see [README.md](README.md#regenerating-this-documentation).
