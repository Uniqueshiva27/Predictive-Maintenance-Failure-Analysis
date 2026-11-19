"""Generate per-tab documentation for Github Copilot.pbix from its PBIR report and a TMDL model export.

Usage: python docs/generate_docs.py "Github Copilot.pbix" <tmdl-folder> docs
"""
import json, os, re, sys, zipfile
from collections import OrderedDict

PBIX, TMDL, OUTDIR = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------------------------------------------------------------- TMDL parsing
def unquote(name):
    name = name.strip()
    return name[1:-1].replace("''", "'") if name.startswith("'") and name.endswith("'") else name

def parse_tmdl(folder):
    tables = OrderedDict()
    tdir = os.path.join(folder, "tables")
    for fn in sorted(os.listdir(tdir)):
        lines = open(os.path.join(tdir, fn), encoding="utf-8").read().splitlines()
        tname = unquote(lines[0].split(" ", 1)[1])
        t = {"measures": OrderedDict(), "columns": OrderedDict(), "calc_source": None}
        i, desc = 1, []
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("\t///"):
                desc.append(ln.strip()[3:].strip()); i += 1; continue
            m = re.match(r"^\t(measure|column|partition) (.+?)(?: =(?: (.*))?)?$", ln)
            if not m:
                if not ln.startswith("\t\t"):
                    desc = []
                i += 1; continue
            kind, name, inline = m.group(1), unquote(m.group(2)), m.group(3)
            i += 1
            expr_lines, props = [], {}
            if inline and inline.strip() != "```":
                expr_lines.append(inline)
            while i < len(lines) and (lines[i].startswith("\t\t\t") or
                                      (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith("\t\t\t"))):
                expr_lines.append(lines[i][3:]); i += 1
            while i < len(lines) and lines[i].startswith("\t\t") and not lines[i].startswith("\t\t\t"):
                p = lines[i].strip()
                if p.startswith("source ="):
                    i += 1; src = []
                    while i < len(lines) and (lines[i].startswith("\t\t\t") or lines[i].strip() == ""):
                        src.append(lines[i][4:] if lines[i].startswith("\t\t\t\t") else lines[i][3:]); i += 1
                    props["source"] = "\n".join(src).strip()
                    continue
                k, sep, v = p.partition(":")
                props[k.strip()] = v.strip() if sep else True
                i += 1
            expr = "\n".join(expr_lines).strip()
            if kind == "measure":
                t["measures"][name] = {"expr": expr, "format": props.get("formatString", ""),
                                       "folder": props.get("displayFolder", ""), "desc": " ".join(desc)}
            elif kind == "column":
                sb = props.get("sortByColumn")
                t["columns"][name] = {"expr": expr or None, "type": props.get("dataType", ""),
                                      "hidden": "isHidden" in props, "sortBy": unquote(sb) if isinstance(sb, str) else "",
                                      "desc": " ".join(desc)}
            elif kind == "partition" and inline and inline.strip() == "calculated":
                t["calc_source"] = props.get("source")
            desc = []
        tables[tname] = t
    return tables

MODEL = parse_tmdl(TMDL)
MEASURES = {m: (t, d) for t, td in MODEL.items() for m, d in td["measures"].items()}

def measure_deps(expr):
    return [x for x in re.findall(r"(?<![\w'\]])\[([^\]]+)\]", expr) if x in MEASURES]

def column_refs(expr):
    return [(unquote(tbl), c) for tbl, c in re.findall(r"('(?:[^']|'')+'|\b\w+)\[([^\]]+)\]", expr)]

# ---------------------------------------------------------------- PBIR parsing
z = zipfile.ZipFile(PBIX)
names = z.namelist()
pages_meta = json.loads(z.read("Report/definition/pages/pages.json"))
AGG = {0: "Sum", 1: "Average", 2: "Count", 3: "Min", 4: "Max", 5: "Distinct count"}

def lit_value(o):
    try:
        v = o["expr"]["Literal"]["Value"]
        return v[1:-1].replace("''", "'") if v.startswith("'") else v
    except (KeyError, TypeError):
        return None

def src(e):
    ref = e["Expression"]["SourceRef"]
    return ref.get("Entity") or ref.get("Source")

def field_label(f):
    """Returns (label, kind, table, property)."""
    if "Measure" in f:
        return f"[{f['Measure']['Property']}]", "measure", src(f["Measure"]), f["Measure"]["Property"]
    if "Column" in f:
        e = src(f["Column"])
        return f"{e}[{f['Column']['Property']}]", "column", e, f["Column"]["Property"]
    if "Aggregation" in f:
        c = f["Aggregation"]["Expression"]["Column"]
        e = src(c)
        return f"{AGG.get(f['Aggregation']['Function'], 'Agg')} of {e}[{c['Property']}]", "column", e, c["Property"]
    return "?", "?", None, None

VTYPE = {"card": "Card", "slicer": "Slicer (dropdown)", "donutChart": "Donut chart", "scatterChart": "Scatter chart",
         "hundredPercentStackedBarChart": "100% stacked bar chart", "clusteredColumnChart": "Clustered column chart",
         "clusteredBarChart": "Clustered bar chart", "tableEx": "Table", "pivotTable": "Matrix (heatmap)",
         "gauge": "Gauge", "treemap": "Treemap", "lineClusteredColumnComboChart": "Line & clustered column combo",
         "textbox": "Text box", "shape": "Shape"}
ROLE = {"Category": "Axis", "Y": "Values", "Y2": "Line values", "Series": "Legend", "X": "X axis",
        "Values": "Values", "Rows": "Rows", "Columns": "Columns", "Group": "Category", "Tooltips": "Tooltips",
        "MinValue": "Minimum", "MaxValue": "Maximum", "TargetValue": "Target"}

def describe_filter(f):
    flt = f.get("filter", {})
    target = field_label(f["field"])[0]
    if f.get("type") == "TopN":
        q = flt["From"][0]["Expression"]["Subquery"]["Query"]
        by = field_label(q["OrderBy"][0]["Expression"])[0]
        by = re.sub(r"\b\w+\[", "[", by) if "of" not in by else by.split(" of ")[0] + " of " + re.sub(r"^\w+", "", by.split(" of ")[1])
        return f"Top {q['Top']} `{target}` by {by}"
    if f.get("type") == "Advanced":
        c = flt["Where"][0]["Condition"]["Comparison"]
        op = {0: "=", 1: ">", 2: "≥", 3: "<", 4: "≤"}[c["ComparisonKind"]]
        return f"`{target}` {op} {c['Right']['Literal']['Value'].rstrip('DL')}"
    return f.get("type", "")

def text_of_textbox(v):
    try:
        paras = v["visual"]["objects"]["general"][0]["properties"]["paragraphs"]
        return " ".join("".join(r["value"] for r in p["textRuns"]) for p in paras).strip()
    except (KeyError, IndexError):
        return ""

def load_page(pid):
    page = json.loads(z.read(f"Report/definition/pages/{pid}/page.json"))
    pre = f"Report/definition/pages/{pid}/visuals/"
    vis = [json.loads(z.read(n)) for n in names if n.startswith(pre) and n.endswith("visual.json")]
    vis.sort(key=lambda v: (round(v["position"]["y"] / 60), v["position"]["x"]))
    return page, vis

def container_text(v, obj):
    for t in v["visual"].get("visualContainerObjects", {}).get(obj, []):
        p = t["properties"]
        if "text" in p and lit_value(p.get("show", {})) != "false":
            return lit_value(p["text"])
    return None

# ---------------------------------------------------------------- Narrative content per tab
NARRATIVE = {
"Fleet Risk Overview": {
 "file": "01-Fleet-Risk-Overview.md",
 "purpose": "Operational view of current fleet failure risk. Shows how many machines are at risk, where the risk is concentrated, and which individual machines should be inspected first.",
 "audience": "Maintenance planners, reliability engineers, plant/operations managers.",
 "questions": ["How many machines are monitored and how many are high risk?",
               "Which machine types carry the largest share of high-risk machines?",
               "Which machines combine a high failure probability with a short remaining useful life?",
               "Which machines should be inspected first, and what is driving their risk?",
               "How is the fleet distributed across RUL bands and top failure drivers?"],
 "layout": ["**Header** – page title and the *Machine Type* and *Risk Band* dropdown slicers.",
            "**Row 1 – KPI cards** – Machines Monitored, High Risk Machines, High Risk %, Avg Failure Probability, Avg Predicted RUL.",
            "**Row 2** – Risk Band donut (with centre total), High-Risk Share by Machine Type, Failure Probability vs Predicted RUL scatter.",
            "**Row 3** – Inspection Priority table, Machines by RUL Band, Machines by Top Driver."],
 "read": ["**Risk bands** come from the model's failure probability: **High ≥ 70 %**, **Medium 30–70 %**, **Low < 30 %** (column `predictions[Risk_Band]`).",
          "**Scatter:** each dot is a machine (RUL ≤ 180 days only). The dashed vertical line marks **30 days RUL** and the dashed horizontal line the **70 % high-risk threshold** – the top-left area is the *inspect first* zone.",
          "**Inspection Priority** lists the 25 machines with the highest failure probability *in the current filter context*; the red data bar visualises the probability.",
          "**Machines by Top Driver** counts machines by the feature with the largest SHAP contribution to their individual prediction.",
          "Click any bar, donut slice or table row to cross-filter the rest of the page."],
 "insights": ["500,000 machines monitored; 15,686 (3.1 %) are High risk.",
              "Average failure probability is 6.0 % and average predicted RUL is ≈ 452 days.",
              "Operational Hours is the most common top driver among high-risk machines."],
 "limits": ["The scatter is limited to Predicted RUL ≤ 180 days and Power BI samples points for display.",
            "Risk-band and RUL-band thresholds are produced upstream in the Python pipeline, not in Power BI."],
},
"Model Trust": {
 "file": "02-Model-Trust.md",
 "purpose": "Shows how reliable the predictive models are, so users can calibrate how much to trust the risk scores on the other tabs.",
 "audience": "Data scientists, reliability engineers, decision makers approving model use.",
 "questions": ["How accurate is the selected failure-prediction model (Accuracy, Precision, Recall, F1, ROC-AUC)?",
               "How accurate is the Remaining-Useful-Life regression model (MAE, RMSE, R²)?",
               "How does LightGBM compare with Random Forest and XGBoost?",
               "How many failures are missed and what might that cost?",
               "Is the false-alarm rate within the acceptable target?"],
 "layout": ["**Header** – title, subtitle and a *Best model* badge.",
            "**Row 1 – 8 KPI cards** – five classification metrics for the selected model and three RUL-regression metrics.",
            "**Row 2** – Classification metrics by model (clustered columns) and a 2 × 2 confusion matrix built from cards.",
            "**Row 3** – Missed failures (FN) panel, False alarm rate gauge, Model selection summary.",
            "**Footer** – source note and page number."],
 "read": ["The **selected model** is the row in `model_metrics` with `Selected_For_Dashboard = TRUE` (currently LightGBM). All classification KPI cards follow this flag.",
          "**Confusion matrix:** TN = healthy predicted healthy, FP = false alarm, FN = missed failure, TP = failure caught. Percentages are of all validation observations.",
          "**Miss rate** = FN ÷ (FN + TP). **False alarm rate** = FP ÷ (FP + TN), compared with a 3 % target on the gauge.",
          "**Estimated exposure** = FN × *Cost per Missed Failure* (illustrative $5,000)."],
 "insights": ["LightGBM: Accuracy 96.4 %, Precision 71.0 %, Recall 66.4 %, F1 68.6 %, ROC-AUC 98.3 %.",
              "Validation set: 100,000 observations – TN 92,422, FP 1,618, FN 2,002, TP 3,958.",
              "False-alarm rate 1.7 % (within the 3 % target); miss rate 33.6 %.",
              "RUL model (Random Forest Regressor): MAE 38.8 days, RMSE 49.1 days, R² 0.971."],
 "limits": ["KPI card sub-labels ('LightGBM · validation', 'RF Regressor · validation') are static text.",
            "Cost per missed failure and the false-alarm target are fixed measures – edit `Cost per Missed Failure` and `False Alarm Target` to change them.",
            "Random Forest has a marginally higher precision (71.05 % vs 70.98 %) than LightGBM."],
},
"Sensor Drivers": {
 "file": "03-Sensor-Drivers.md",
 "purpose": "Explains *why* the model predicts failures – which features carry the most influence (SHAP) and how sensor readings differ between failing and normal machines.",
 "audience": "Reliability engineers, data scientists, maintenance SMEs validating model logic.",
 "questions": ["Which features drive the failure model the most?",
               "How many features explain most of the model's behaviour (Pareto)?",
               "How does the failure rate change across vibration and oil-level ranges?",
               "Which sensors look different for machines that failed vs normal ones?"],
 "layout": ["**Header** – title plus *Asset* (machine type) and *Model* dropdown slicers.",
            "**Row 1** – SHAP Feature Importance bar chart, Pareto combo chart with *Top 4 drivers* callout, Top Driver callout and Feature Share treemap.",
            "**Row 2** – Failure Rate heatmap (Vibration × Oil Level) and Sensor Profiles (Normal vs Failed).",
            "**Footer** – number of features analysed and SHAP source."],
 "read": ["**Importance share** = a feature's mean |SHAP| ÷ the sum over all features (`feature_importance[Importance_Pct]`).",
          "**Pareto:** bars = individual share (left axis), yellow line = cumulative share (right axis, 0–100 %).",
          "**Heatmap:** machines are split into fleet quintiles of vibration (rows) and oil level (columns). Cell value = actual *failure within 7 days* rate; brighter red = higher rate relative to the other cells.",
          "**Sensor Profiles:** mean z-score of each sensor for Failed vs Normal machines. A large gap means the sensor separates failing machines well.",
          "The *Asset* slicer affects the heatmap and sensor profiles (predictions table); the *Model* slicer affects the SHAP visuals (feature_importance table)."],
 "insights": ["Top driver: Operational Hours (≈ 40 % share), then Sound Level (20 %), Vibration (16 %) and Oil Level (11 %); the top 4 explain ≈ 86 %.",
              "17 features analysed; the bottom 11 together contribute < 5 %.",
              "Failure rate rises with vibration (≈ 4.6 % → 7.8 %); oil level has little effect.",
              "Failed machines average +1.57 σ on Operational Hours; other sensors show only small differences."],
 "limits": ["Quintile cut-points for vibration and oil level are hard-coded in the calculated columns (derived from the data at build time).",
            "Box plots are not native to Power BI – sensor distributions are summarised as mean z-scores.",
            "There is no date column, so no time-period filter is available."],
},
"Machine Segments": {
 "file": "04-Machine-Segments.md",
 "purpose": "Shows the K-means machine segments (clusters), how they separate in PCA space, and which segment carries the most failure risk.",
 "audience": "Fleet managers, reliability engineers, maintenance strategy teams.",
 "questions": ["How many segments exist and how are machines distributed?",
               "Which segment has the highest failure rate and how does it compare with the fleet average?",
               "What is the risk-band mix and average RUL of each segment?",
               "What action should be prioritised?"],
 "layout": ["**Header** – title and source note.",
            "**Row 1 – 4 KPI cards** – Total machines, Overall failure rate, Avg RUL, Highest-risk segment.",
            "**Row 2** – PC1 vs PC2 cluster scatter, Failure rate by cluster (with fleet-average line), Risk band mix by cluster.",
            "**Row 3** – Cluster profile table and Smart narrative panel."],
 "read": ["**Clusters** (`predictions[Cluster]`) come from K-means in the Python pipeline; **PC1/PC2** are the first two principal components used for plotting.",
          "**Failure rate** = share of machines with `Failure_Within_7_Days = TRUE`.",
          "In the **Cluster profile** table the failure-rate cell is **red** when above the fleet average, **green** otherwise; the total row shows fleet values and Avg RUL has data bars.",
          "The **Smart narrative** text and badges are measures and update automatically with the data."],
 "insights": ["3 clusters of ≈ 166 k machines each.",
              "C2 is the highest-risk segment: 18.1 % failure rate (3.0 × the 6.0 % fleet average) and avg RUL ≈ 123 days.",
              "C1 and C3 have 0 % observed failures with avg RUL ≈ 449 and ≈ 782 days.",
              "Average temperature, vibration and oil level are nearly identical across clusters – segments are separated mainly by life-cycle stage (RUL / operational hours)."],
 "limits": ["PC1 spans ≈ ±50,000 while PC2 spans ≈ ±185, so clusters appear as vertical bands rather than round groups; the scatter is sampled.",
            "If the fleet-average reference line does not render, re-add it in the Analytics pane using the `Fleet Failure Rate` measure."],
},
"Page 1": {
 "file": "05-Page-1.md",
 "purpose": "Blank placeholder page (1920 × 1080) with no visuals yet. Reserved for future content.",
 "audience": "Report authors.",
 "questions": ["None yet – the page is empty."],
 "layout": ["Empty canvas using the report's default (FleetRiskDark) theme, without the dark page background applied to the other tabs."],
 "read": ["Nothing to read yet. Add visuals in Power BI Desktop, or delete the page (right-click the tab ▸ *Delete page*) if it is not needed."],
 "insights": [],
 "limits": ["Uses a 1920 × 1080 canvas while the other tabs use 3000 × 1440 – resize it (*Format ▸ Canvas settings*) for consistency if you build on it."],
},
}

def esc(s):
    return s.replace("|", "\\|")

# ---------------------------------------------------------------- Rendering
def render_page(pid, idx, total):
    page, vis = load_page(pid)
    name = page["displayName"]
    meta = NARRATIVE.get(name) or {"file": f"{idx:02d}-{name.replace(' ', '-')}.md", "purpose": "", "audience": "",
                                   "questions": [], "layout": [], "read": [], "insights": [], "limits": []}
    used_measures, used_columns, slicers, rows, labels = [], set(), [], [], []
    for v in vis:
        vt = v["visual"]["visualType"]
        if vt in ("textbox", "shape"):
            t = text_of_textbox(v)
            if t:
                labels.append(t)
            continue
        fields, vis_measures = [], []
        for role, rd in v["visual"].get("query", {}).get("queryState", {}).items():
            for p in rd.get("projections", []):
                lbl, kind, ent, prop = field_label(p["field"])
                disp = f" (shown as “{p['displayName']}”)" if p.get("displayName") else ""
                fields.append(f"{ROLE.get(role, role)}: `{lbl}`{disp}")
                if kind == "measure":
                    vis_measures.append(prop)
                elif kind == "column":
                    used_columns.add((ent, prop))
        for objs in v["visual"].get("objects", {}).values():
            for o in objs:
                for mm in re.findall(r'"Measure": \{"Expression": \{"SourceRef": \{"Entity": "[^"]+"\}\}, "Property": "([^"]+)"',
                                     json.dumps(o.get("properties", {}))):
                    fields.append(f"Conditional format / dynamic value: `[{mm}]`")
                    vis_measures.append(mm)
        for m in vis_measures:
            if m not in used_measures:
                used_measures.append(m)
        filters = [describe_filter(f) for f in v.get("filterConfig", {}).get("filters", [])]
        title = container_text(v, "title")
        if vt == "slicer":
            slicers.append((title, fields[0].split(": ", 1)[1] if fields else ""))
        if not title:
            title = f"Card – {vis_measures[0]}" if vt == "card" and vis_measures else VTYPE.get(vt, vt)
        rows.append((title, VTYPE.get(vt, vt), fields, filters, container_text(v, "subTitle")))

    closure, stack = [], list(used_measures)
    while stack:
        m = stack.pop(0)
        if m in closure or m not in MEASURES:
            continue
        closure.append(m)
        stack.extend(measure_deps(MEASURES[m][1]["expr"]))
    for m in closure:
        used_columns.update(column_refs(MEASURES[m][1]["expr"]))

    calc_cols, calc_tables = [], []
    for t, c in sorted(used_columns, key=lambda x: (x[0] or "", x[1])):
        td = MODEL.get(t)
        if not td:
            continue
        cd = td["columns"].get(c)
        if cd and cd["expr"]:
            calc_cols.append((t, c, cd))
        if td["calc_source"] and t not in calc_tables:
            calc_tables.append(t)
    for t, c, cd in list(calc_cols):
        sb = cd["sortBy"]
        if sb and not any(a == t and b2 == sb for a, b2, _ in calc_cols):
            sbd = MODEL[t]["columns"].get(sb)
            if sbd and sbd["expr"]:
                calc_cols.append((t, sb, sbd))
    src_tables = sorted({t for t, _ in used_columns if t in MODEL} | {MEASURES[m][0] for m in closure})

    sec = iter(range(1, 20))
    L = [f"# Tab {idx}: {name}\n",
         f"> **Report:** `Github Copilot.pbix` · **Page {idx} of {total}** · **Canvas:** {page['width']} × {page['height']} px, {page.get('displayOption', '')}\n",
         f"## {next(sec)}. Purpose\n", meta["purpose"] + "\n", f"**Intended audience:** {meta['audience']}\n",
         f"## {next(sec)}. Business questions answered\n"]
    L += [f"- {q}" for q in meta["questions"]] + ["", f"## {next(sec)}. Page layout\n"]
    L += [f"{i + 1}. {s}" for i, s in enumerate(meta["layout"])] + ["", f"## {next(sec)}. Filters and interactions\n"]
    if slicers:
        L += ["| Slicer | Field |", "|---|---|"] + [f"| {t} | {esc(f)} |" for t, f in slicers] + [""]
    else:
        L.append("This page has no slicers.\n")
    L += ["- **Cross-filtering:** selecting a data point in any chart filters or highlights the other visuals on the page.",
          "- **Page / report filters:** none by default – only the visual-level filters listed in the inventory below.\n",
          f"## {next(sec)}. Visual inventory\n",
          "| # | Visual | Type | Fields (role: field) | Visual-level filters |", "|---|---|---|---|---|"]
    for n, (title, vt, fields, filters, sub) in enumerate(rows, 1):
        tt = f"**{esc(title)}**" + (f"<br>*{esc(sub)}*" if sub else "")
        L.append(f"| {n} | {tt} | {vt} | {'<br>'.join(esc(f) for f in fields) or '–'} | {'<br>'.join(esc(f) for f in filters) or '–'} |")
    L.append("")
    if labels:
        L.append("**Static text elements:** " + "; ".join(f"“{esc(l)}”" for l in labels) + "\n")
    L.append(f"## {next(sec)}. How to read this page\n")
    L += [f"- {s}" for s in meta["read"]] + [""]
    if meta["insights"]:
        L.append(f"## {next(sec)}. Key insights (data as of documentation date)\n")
        L += [f"- {s}" for s in meta["insights"]] + [""]
    L += [f"## {next(sec)}. Measures\n",
          "Every measure placed on the page, plus the measures they depend on.\n",
          "| Measure | Home table | Format | Display folder |", "|---|---|---|---|"]
    for m in closure:
        t, d = MEASURES[m]
        L.append(f"| `{m}` | {t} | {('`' + esc(d['format']) + '`') if d['format'] else '–'} | {d['folder'] or '–'} |")
    L.append("")
    for m in closure:
        t, d = MEASURES[m]
        L.append(f"### {m}\n")
        if d["desc"]:
            L.append(f"_{d['desc']}_\n")
        L += ["```dax", f"{m} =", d["expr"], "```\n"]
    if calc_cols or calc_tables:
        L.append(f"## {next(sec)}. Calculated columns and tables\n")
        for t, c, cd in calc_cols:
            notes = [f"data type `{cd['type']}`"] + ([f"sorted by `{cd['sortBy']}`"] if cd["sortBy"] else []) + (["hidden"] if cd["hidden"] else [])
            L += [f"### {t}[{c}]\n", "Column – " + ", ".join(notes) + "\n", "```dax", cd["expr"], "```\n"]
        for t in calc_tables:
            L += [f"### Calculated table: {t}\n", "```dax", MODEL[t]["calc_source"], "```\n"]
    L += [f"## {next(sec)}. Data sources\n", "| Table | Columns referenced by this page (visuals and measures) |", "|---|---|"]
    for t in src_tables:
        cols = sorted({c for tt, c in used_columns if tt == t})
        L.append(f"| `{t}` | {', '.join('`' + c + '`' for c in cols) or '(measures only)'} |")
    L += ["", f"## {next(sec)}. Limitations and maintenance notes\n"] + [f"- {s}" for s in meta["limits"]]
    L.append("- To regenerate this document after report changes, see [README.md](README.md#regenerating-this-documentation).\n")
    return meta["file"], name, "\n".join(L), len(rows), len(closure)

os.makedirs(OUTDIR, exist_ok=True)
index = []
for i, pid in enumerate(pages_meta["pageOrder"], 1):
    fn, name, content, nv, nm = render_page(pid, i, len(pages_meta["pageOrder"]))
    open(os.path.join(OUTDIR, fn), "w", encoding="utf-8").write(content)
    index.append((i, name, fn, nv, nm))
    print(f"wrote {fn}: {nv} visuals, {nm} measures")

rels = open(os.path.join(TMDL, "relationships.tmdl"), encoding="utf-8").read()
rel_rows = []
for blk in rels.split("relationship ")[1:]:
    fc = re.search(r"fromColumn: (.+)", blk).group(1).strip()
    tc = re.search(r"toColumn: (.+)", blk).group(1).strip()
    rel_rows.append(f"| `{fc}` | `{tc}` | Many → One | {'Both' if 'bothDirections' in blk else 'Single'} |")

L = ["# Dashboard Documentation – Github Copilot.pbix\n",
     "Functional and technical documentation for every tab of the Predictive Maintenance Power BI report. "
     "For a short end-user guide see [ReadMe/README.md](../ReadMe/README.md).\n",
     "## Tabs\n", "| # | Tab | Document | Data visuals | Measures | Purpose |", "|---|---|---|---|---|---|"]
for i, name, fn, nv, nm in index:
    purpose = NARRATIVE.get(name, {}).get("purpose", "").split(". ")[0].rstrip(".")
    L.append(f"| {i} | {name} | [{fn}]({fn}) | {nv} | {nm} | {purpose}. |")
L += ["", "## Data model\n", "| Table | Kind | Measures | Calculated columns |", "|---|---|---|---|"]
for t, td in MODEL.items():
    kind = "Calculated table (DAX)" if td["calc_source"] else "Imported"
    L.append(f"| `{t}` | {kind} | {len(td['measures'])} | {sum(1 for c in td['columns'].values() if c['expr'])} |")
L += ["", "### Relationships\n", "| From (many) | To (one) | Cardinality | Cross-filter |", "|---|---|---|---|"] + rel_rows
L += ["", "## Visual theme\n",
      "All tabs use the custom **FleetRiskDark** theme (`Report/StaticResources/RegisteredResources/FleetRiskDark.json`): "
      "page background `#0B1426`, visual background `#13203A`, borders `#2A3A5C`, text `#FFFFFF` / `#AEB9CC`. "
      "Semantic colours: High / bad `#F0505A`, Medium `#F5B335`, Low / good `#1FD1A0`, accent cyan `#22D3EE` / `#3FD6F2`.\n",
      "## Regenerating this documentation\n",
      "The tab documents are generated from the report definition (PBIR inside the `.pbix`) and a TMDL export of the semantic model.\n",
      "1. Open the report in Power BI Desktop and export the semantic model to a TMDL folder "
      "(Power BI Modeling MCP server `ExportToTmdlFolder`, or Tabular Editor ▸ *Save to folder* in TMDL format).",
      "2. From the project folder run:\n",
      "```powershell",
      "python docs\\generate_docs.py \"Github Copilot.pbix\" <tmdl-folder> docs",
      "```\n",
      "Narrative sections (purpose, questions, how to read, insights, limitations) live in the `NARRATIVE` dictionary in "
      "`generate_docs.py`; visual inventories, filters, measures, DAX and data sources are extracted automatically.\n"]
open(os.path.join(OUTDIR, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("wrote README.md")
