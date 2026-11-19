# Tab 4: Machine Segments

> **Report:** `Github Copilot.pbix` · **Page 4 of 5** · **Canvas:** 3000 × 1440 px, FitToPage

## 1. Purpose

Shows the K-means machine segments (clusters), how they separate in PCA space, and which segment carries the most failure risk.

**Intended audience:** Fleet managers, reliability engineers, maintenance strategy teams.

## 2. Business questions answered

- How many segments exist and how are machines distributed?
- Which segment has the highest failure rate and how does it compare with the fleet average?
- What is the risk-band mix and average RUL of each segment?
- What action should be prioritised?

## 3. Page layout

1. **Header** – title and source note.
2. **Row 1 – 4 KPI cards** – Total machines, Overall failure rate, Avg RUL, Highest-risk segment.
3. **Row 2** – PC1 vs PC2 cluster scatter, Failure rate by cluster (with fleet-average line), Risk band mix by cluster.
4. **Row 3** – Cluster profile table and Smart narrative panel.

## 4. Filters and interactions

This page has no slicers.

- **Cross-filtering:** selecting a data point in any chart filters or highlights the other visuals on the page.
- **Page / report filters:** none by default – only the visual-level filters listed in the inventory below.

## 5. Visual inventory

| # | Visual | Type | Fields (role: field) | Visual-level filters |
|---|---|---|---|---|
| 1 | **Card – Machines Monitored** | Card | Values: `[Machines Monitored]` | – |
| 2 | **Card – Fleet Failure Rate** | Card | Values: `[Fleet Failure Rate]` | – |
| 3 | **Card – Avg Predicted RUL** | Card | Values: `[Avg Predicted RUL]` | – |
| 4 | **Card – Highest Risk Cluster** | Card | Values: `[Highest Risk Cluster]` | – |
| 5 | **Machine segments \| PC1 vs PC2**<br>*Each point is a machine, coloured by K-means cluster (sampled for display)* | Scatter chart | Axis: `predictions[Machine_ID]`<br>Legend: `predictions[Cluster]`<br>X axis: `Average of predictions[PC1]` (shown as “PC1”)<br>Values: `Average of predictions[PC2]` (shown as “PC2”) | – |
| 6 | **Failure rate by cluster** | Clustered column chart | Axis: `predictions[Cluster]`<br>Values: `[Segment Failure Rate]` (shown as “Failure rate”)<br>Conditional format / dynamic value: `[Fleet Failure Rate]` | – |
| 7 | **Risk band mix by cluster** | 100% stacked bar chart | Axis: `predictions[Cluster]`<br>Legend: `predictions[Risk_Band]` (shown as “Risk band”)<br>Values: `[Machines]` | – |
| 8 | **Cluster profile**<br>*Failure rate cell is red when above the fleet average* | Table | Values: `predictions[Cluster]`<br>Values: `[Machines]` (shown as “Machine count”)<br>Values: `[Avg Temperature]` (shown as “Avg Temperature (°C)”)<br>Values: `[Avg Vibration]` (shown as “Avg Vibration (mm/s)”)<br>Values: `[Avg Oil Level]` (shown as “Avg Oil Level (%)”)<br>Values: `[Segment Failure Rate]` (shown as “Failure Rate”)<br>Values: `[Avg Predicted RUL]` (shown as “Avg RUL (days)”)<br>Conditional format / dynamic value: `[Segment Rate Color]` | – |
| 9 | **Card – Cluster Narrative** | Card | Values: `[Cluster Narrative]` | – |
| 10 | **Card – Cluster Multiple Label** | Card | Values: `[Cluster Multiple Label]` | – |
| 11 | **Card – Cluster RUL Label** | Card | Values: `[Cluster RUL Label]` | – |

**Static text elements:** “❙❙❙”; “Machine Segments – cluster_summary”; “Source: predictions + cluster_summary”; “Total machines”; “Overall failure rate”; “Avg RUL”; “Highest-risk segment”; “⚙”; “⚠”; “⏲”; “◈”; “💡  \|  Smart narrative”

## 6. How to read this page

- **Clusters** (`predictions[Cluster]`) come from K-means in the Python pipeline; **PC1/PC2** are the first two principal components used for plotting.
- **Failure rate** = share of machines with `Failure_Within_7_Days = TRUE`.
- In the **Cluster profile** table the failure-rate cell is **red** when above the fleet average, **green** otherwise; the total row shows fleet values and Avg RUL has data bars.
- The **Smart narrative** text and badges are measures and update automatically with the data.

## 7. Key insights (data as of documentation date)

- 3 clusters of ≈ 166 k machines each.
- C2 is the highest-risk segment: 18.1 % failure rate (3.0 × the 6.0 % fleet average) and avg RUL ≈ 123 days.
- C1 and C3 have 0 % observed failures with avg RUL ≈ 449 and ≈ 782 days.
- Average temperature, vibration and oil level are nearly identical across clusters – segments are separated mainly by life-cycle stage (RUL / operational hours).

## 8. Measures

Every measure placed on the page, plus the measures they depend on.

| Measure | Home table | Format | Display folder |
|---|---|---|---|
| `Machines Monitored` | predictions | `#,0` | Fleet Risk |
| `Fleet Failure Rate` | predictions | `0.0%` | Machine Segments |
| `Avg Predicted RUL` | predictions | `#,0 "days"` | Fleet Risk |
| `Highest Risk Cluster` | predictions | – | Machine Segments |
| `Segment Failure Rate` | predictions | `0.0%` | Machine Segments |
| `Machines` | predictions | `#,0` | Fleet Risk |
| `Avg Temperature` | predictions | `0.0` | Machine Segments |
| `Avg Vibration` | predictions | `0.00` | Machine Segments |
| `Avg Oil Level` | predictions | `0.0` | Machine Segments |
| `Segment Rate Color` | predictions | – | Machine Segments |
| `Cluster Narrative` | predictions | – | Machine Segments |
| `Cluster Multiple Label` | predictions | – | Machine Segments |
| `Cluster RUL Label` | predictions | – | Machine Segments |
| `Failure Rate` | predictions | `0.0%` | Sensor Drivers |
| `Highest Risk Cluster Rate` | predictions | `0.0%` | Machine Segments |
| `Highest Risk Cluster RUL` | predictions | `#,0 "days"` | Machine Segments |

### Machines Monitored

```dax
Machines Monitored =
COUNTROWS ( predictions )
```

### Fleet Failure Rate

```dax
Fleet Failure Rate =
CALCULATE ( [Segment Failure Rate], REMOVEFILTERS ( predictions[Cluster] ), REMOVEFILTERS ( cluster_summary ) )
```

### Avg Predicted RUL

```dax
Avg Predicted RUL =
AVERAGE ( predictions[Predicted_RUL] )
```

### Highest Risk Cluster

```dax
Highest Risk Cluster =
MAXX ( TOPN ( 1, VALUES ( predictions[Cluster] ), [Segment Failure Rate], DESC ), predictions[Cluster] )
```

### Segment Failure Rate

```dax
Segment Failure Rate =
IF ( COUNTROWS ( predictions ) > 0, [Failure Rate] + 0 )
```

### Machines

```dax
Machines =
COUNTROWS ( predictions )
```

### Avg Temperature

```dax
Avg Temperature =
AVERAGE ( predictions[Temperature_C] )
```

### Avg Vibration

```dax
Avg Vibration =
AVERAGE ( predictions[Vibration_mms] )
```

### Avg Oil Level

```dax
Avg Oil Level =
AVERAGE ( predictions[Oil_Level_pct] )
```

### Segment Rate Color

_Red when the segment's failure rate is above the fleet average, otherwise green._

```dax
Segment Rate Color =
IF ( [Segment Failure Rate] > [Fleet Failure Rate], "#B4232F", "#12806F" )
```

### Cluster Narrative

```dax
Cluster Narrative =
"Cluster " & [Highest Risk Cluster] & " has the highest failure rate at " & FORMAT ( [Highest Risk Cluster Rate], "0.0%" ) & " – prioritize inspection"
```

### Cluster Multiple Label

```dax
Cluster Multiple Label =
"↗  " & FORMAT ( DIVIDE ( [Highest Risk Cluster Rate], [Segment Failure Rate] ), "0.0" ) & "× fleet average"
```

### Cluster RUL Label

```dax
Cluster RUL Label =
"Avg RUL: " & FORMAT ( [Highest Risk Cluster RUL], "#,0" ) & " days"
```

### Failure Rate

```dax
Failure Rate =
DIVIDE ( CALCULATE ( COUNTROWS ( predictions ), predictions[Failure_Within_7_Days] = TRUE () ), COUNTROWS ( predictions ) )
```

### Highest Risk Cluster Rate

```dax
Highest Risk Cluster Rate =
VAR c = [Highest Risk Cluster]
RETURN CALCULATE ( [Segment Failure Rate], predictions[Cluster] = c )
```

### Highest Risk Cluster RUL

```dax
Highest Risk Cluster RUL =
VAR c = [Highest Risk Cluster]
RETURN CALCULATE ( [Avg Predicted RUL], predictions[Cluster] = c )
```

## 9. Data sources

| Table | Columns referenced by this page (visuals and measures) |
|---|---|
| `predictions` | `Cluster`, `Failure_Within_7_Days`, `Machine_ID`, `Oil_Level_pct`, `PC1`, `PC2`, `Predicted_RUL`, `Risk_Band`, `Temperature_C`, `Vibration_mms` |

## 10. Limitations and maintenance notes

- PC1 spans ≈ ±50,000 while PC2 spans ≈ ±185, so clusters appear as vertical bands rather than round groups; the scatter is sampled.
- If the fleet-average reference line does not render, re-add it in the Analytics pane using the `Fleet Failure Rate` measure.
- To regenerate this document after report changes, see [README.md](README.md#regenerating-this-documentation).
