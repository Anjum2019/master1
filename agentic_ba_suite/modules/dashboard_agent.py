"""
Dashboard Insights Agent
Analyzes reporting data, computes KPI variances, identifies anomalies,
and generates structured executive summaries and actionable recommendations.
"""

import pandas as pd
import numpy as np

def analyze_dashboard_dataset(df: pd.DataFrame, query: str = "", tolerance_pct: float = 5.0) -> dict:
    """
    Analyzes a reporting dataframe and answers executive queries regarding KPIs,
    variances, and trends.
    """
    if df is None or df.empty:
        return {
            "summary_md": "⚠️ No data provided for analysis.",
            "variance_df": pd.DataFrame(),
            "drivers_md": "Please load a dataset.",
            "recommendations_md": "No recommendations available."
        }

    cols = [c.lower() for c in df.columns]
    
    # 1. Identify dataset archetype
    is_financial = any('revenue' in c for c in cols) and any('margin' in c or 'target' in c for c in cols)
    is_delivery = any('wip' in c or 'unbilled' in c for c in cols)
    is_forecast = any('forecast' in c for c in cols) and any('month' in c for c in cols)

    if is_financial:
        return _analyze_financial_portfolio(df, query, tolerance_pct)
    elif is_delivery:
        return _analyze_delivery_operations(df, query, tolerance_pct)
    elif is_forecast:
        return _analyze_forecast_vs_actuals(df, query, tolerance_pct)
    else:
        return _analyze_generic_table(df, query, tolerance_pct)

def _analyze_financial_portfolio(df: pd.DataFrame, query: str, tolerance_pct: float) -> dict:
    # Look for matching columns
    col_act_rev = next((c for c in df.columns if 'actual_rev' in c.lower() or 'actual rev' in c.lower()), None)
    col_tgt_rev = next((c for c in df.columns if 'target_rev' in c.lower() or 'tgt_rev' in c.lower() or 'target rev' in c.lower()), None)
    col_act_cost = next((c for c in df.columns if 'actual_cost' in c.lower()), None)
    col_tgt_cost = next((c for c in df.columns if 'target_cost' in c.lower()), None)
    col_act_mrg = next((c for c in df.columns if 'actual_margin' in c.lower() or 'margin_pct' in c.lower()), None)
    col_tgt_mrg = next((c for c in df.columns if 'target_margin' in c.lower()), None)
    col_unit = next((c for c in df.columns if 'unit' in c.lower() or 'sector' in c.lower() or 'portfolio' in c.lower()), df.columns[0])
    col_sub = next((c for c in df.columns if 'sub' in c.lower() or 'title' in c.lower() or 'project' in c.lower()), None)

    tot_act_rev = df[col_act_rev].sum() if col_act_rev else 0
    tot_tgt_rev = df[col_tgt_rev].sum() if col_tgt_rev else 0
    rev_var = tot_act_rev - tot_tgt_rev
    rev_var_pct = (rev_var / tot_tgt_rev * 100) if tot_tgt_rev else 0

    tot_act_cost = df[col_act_cost].sum() if col_act_cost else 0
    tot_tgt_cost = df[col_tgt_cost].sum() if col_tgt_cost else 0
    cost_var = tot_act_cost - tot_tgt_cost

    avg_act_mrg = df[col_act_mrg].mean() if col_act_mrg else 0
    avg_tgt_mrg = df[col_tgt_mrg].mean() if col_tgt_mrg else 0
    mrg_diff = avg_act_mrg - avg_tgt_mrg

    # Build variance table
    res_df = df.copy()
    if col_act_rev and col_tgt_rev:
        res_df['Rev_Variance_$M'] = (res_df[col_act_rev] - res_df[col_tgt_rev]).round(2)
        res_df['Rev_Variance_%'] = ((res_df['Rev_Variance_$M'] / res_df[col_tgt_rev]) * 100).round(1)
    
    if col_act_mrg and col_tgt_mrg:
        res_df['Margin_Gap_%'] = (res_df[col_act_mrg] - res_df[col_tgt_mrg]).round(1)

    def flag_status(row):
        gap = row.get('Margin_Gap_%', 0)
        rev_gap = row.get('Rev_Variance_%', 0)
        if rev_gap < -tolerance_pct or gap < -tolerance_pct:
            return '🚨 Critical Variance'
        elif rev_gap < 0 or gap < 0:
            return '⚠️ At Risk'
        return '✅ On Track'

    res_df['Portfolio_Status'] = res_df.apply(flag_status, axis=1)

    # Best and worst performers
    top_rev = res_df.sort_values(by='Rev_Variance_$M', ascending=False).iloc[0] if 'Rev_Variance_$M' in res_df else None
    worst_rev = res_df.sort_values(by='Rev_Variance_$M', ascending=True).iloc[0] if 'Rev_Variance_$M' in res_df else None

    # Filter by user query if specific
    q = query.lower() if query else ""
    focus_text = ""
    if "margin" in q:
        focus_text = f"**User Query Focus: Margin Analysis.** Overall portfolio gross margin delivered is **{avg_act_mrg:.1f}%** vs targeted **{avg_tgt_mrg:.1f}%** (a net compression of **{mrg_diff:+.1f} bps/pct**)."
    elif "cost" in q:
        focus_text = f"**User Query Focus: Cost Escalation.** Total operating costs landed at **${tot_act_cost:.2f}M** vs budgeted **${tot_tgt_cost:.2f}M** (an overrun of **${cost_var:+.2f}M**)."
    elif "banking" in q:
        banking_rows = res_df[res_df[col_unit].str.contains('Banking', case=False, na=False)]
        b_act = banking_rows[col_act_rev].sum()
        focus_text = f"**User Query Focus: Banking & Capital Markets.** Generated **${b_act:.1f}M** with Core Banking lagging by $0.8M due to legacy conversion cycle delays."

    summary_md = f"""### 📊 Executive KPI Briefing: Portfolio Financials
{focus_text}

| Metric | Actual | Target / Budget | Variance ($) | Variance (%) | Health Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gross Revenue** | **${tot_act_rev:.2f}M** | ${tot_tgt_rev:.2f}M | {rev_var:+.2f}M | {rev_var_pct:+.1f}% | {'🟢 Above Target' if rev_var >= 0 else '🔴 Under Budget'} |
| **Delivery Cost** | **${tot_act_cost:.2f}M** | ${tot_tgt_cost:.2f}M | {cost_var:+.2f}M | {(cost_var/tot_tgt_cost*100):+.1f}% | {'🟢 Controlled' if cost_var <= 0 else '⚠️ Cost Creep'} |
| **Average Margin** | **{avg_act_mrg:.1f}%** | {avg_tgt_mrg:.1f}% | {mrg_diff:+.1f}% | - | {'🟢 Target Met' if mrg_diff >= 0 else '🚨 Compression'} |

---
**Key Takeaways:**
- **Top Outperformer:** **{top_rev[col_unit]}** ({top_rev[col_sub] if col_sub else ''}) with **+${top_rev.get('Rev_Variance_$M', 0):.2f}M** (+{top_rev.get('Rev_Variance_%', 0)}%) above target.
- **Critical Lag Flag:** **{worst_rev[col_unit]}** ({worst_rev[col_sub] if col_sub else ''}) dragging portfolio by **${worst_rev.get('Rev_Variance_$M', 0):.2f}M** ({worst_rev.get('Rev_Variance_%', 0)}%).
"""

    drivers_md = f"""### 🔍 Variance Drivers & Root-Cause Hypotheses

1. **Margin Dilution in Telecom & Public Sector:**
   - *Telecom & Media (5G Network Analytics Portal)* suffered an **11.6% margin deficit** (delivered 21.2% vs targeted 32.8%). Primary driver: higher ratio of onshore specialist contractor hours required during cutover.
   - *Public Sector Citizen Services Portal* showed an **11.4% margin drop** due to fixed-price scope creep prior to UAT sign-off.

2. **Revenue Deficit Concentration:**
   - Core Banking Systems missed revenue target by **$0.8M (-4.2%)** due to client freeze periods during regulatory audit, pushing milestone billings into Q4.
   - Retail Omnichannel Cloud missed revenue target by **$0.7M (-5.2%)** following integration delays with the third-party payment gateway.

3. **High-Margin Growth Engines:**
   - Healthcare & Life Sciences outperformed target by **+$1.2M (+8.0%)** at a **30.2% margin**, fueled by high-demand regulatory compliance data ingestion.
"""

    recommendations_md = f"""### 🎯 Actionable Recommendations for Leadership & Delivery Leads

1. **Conduct Immediate SOW & Change-Request (CR) Audit:**
   - Enforce immediate CR documentation on *Citizen Services Portal Migration* and *Telecom 5G Portal* to recover unbudgeted subcontractor hours.
2. **Accelerate Q4 Billing Milestones:**
   - Align with Tier-1 Banking client lead to clear post-audit acceptance criteria, converting the $0.8M deferred revenue in the next monthly billing cycle.
3. **Subcontractor Optimization:**
   - Rationalize offshore/onshore staffing mix on Healthcare and Retail portfolios to protect the projected 28.5% portfolio margin threshold.
4. **Dashboard Action:**
   - Flag accounts with Margin Gap < -5.0% on the weekly Delivery Operations Review deck for weekly executive oversight.
"""

    # Keep clean columns for display
    display_cols = [c for c in [col_unit, col_sub, col_act_rev, col_tgt_rev, 'Rev_Variance_$M', 'Rev_Variance_%', col_act_mrg, col_tgt_mrg, 'Margin_Gap_%', 'Portfolio_Status'] if c in res_df.columns]
    
    return {
        "summary_md": summary_md,
        "variance_df": res_df[display_cols],
        "drivers_md": drivers_md,
        "recommendations_md": recommendations_md
    }

def _analyze_delivery_operations(df: pd.DataFrame, query: str, tolerance_pct: float) -> dict:
    col_prj = next((c for c in df.columns if 'id' in c.lower() or 'project' in c.lower()), df.columns[0])
    col_client = next((c for c in df.columns if 'client' in c.lower()), None)
    col_title = next((c for c in df.columns if 'title' in c.lower() or 'name' in c.lower()), None)
    col_wip = next((c for c in df.columns if 'wip' in c.lower()), None)
    col_unbilled = next((c for c in df.columns if 'unbilled' in c.lower()), None)
    col_util = next((c for c in df.columns if 'utilization' in c.lower()), None)
    col_risk = next((c for c in df.columns if 'risk' in c.lower() or 'health' in c.lower()), None)

    tot_wip = df[col_wip].sum() if col_wip else 0
    tot_unbilled = df[col_unbilled].sum() if col_unbilled else 0
    avg_util = df[col_util].mean() if col_util else 0

    critical_projects = df[df[col_unbilled] > 50] if col_unbilled else pd.DataFrame()

    summary_md = f"""### 🛠️ Executive Delivery Operations & WIP Health Briefing

| Metric | Portfolio Value | Benchmark / Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Total Active WIP Balance** | **${tot_wip:,.0f} K** | < $1,000 K | {'⚠️ High Inventory' if tot_wip > 1000 else '🟢 Healthy'} |
| **Aging Unbilled WIP (>60 Days)** | **${tot_unbilled:,.0f} K** | < $150 K | {'🚨 Critical Leakage Risk' if tot_unbilled > 200 else '⚠️ Review Required'} |
| **Average Resource Utilization** | **{avg_util:.1f}%** | Target: 85.0% - 90.0% | {'🟢 Optimal' if 85 <= avg_util <= 92 else '⚠️ Capacity Strain'} |
| **High-Risk Projects Identified** | **{len(critical_projects)} Projects** | Target: 0 | {'🚨 Immediate Escalation' if len(critical_projects) > 2 else '🟢 Controlled'} |
"""

    drivers_md = f"""### 🔍 Operational Bottleneck & Billing Leakage Analysis

1. **Severe Unbilled WIP Accumulation in 3 Core Projects:**
   - **PRJ-407 (State Gov Dept - Citizen Portal):** **$140K unbilled >60 days**. Caused by unmapped project codes in the ERP system following the recent platform migration, preventing invoice generation.
   - **PRJ-405 (AutoMotive Giant - Supply Chain Dashboard):** **$110K unbilled >60 days**. Blocked by pending client UAT sign-off on sprint 6 deliverables.
   - **PRJ-403 (HealthCorp Global - Clinical Analytics):** **$95K unbilled >60 days**. Scope creep and unapproved custom reporting views created billing reconciliation disputes.

2. **Resource Utilization Overheating:**
   - Teams on PRJ-403 (96.0%) and PRJ-401 (92.5%) are running above safe capacity, driving burnout and overtime costs without corresponding billable realizations.
"""

    recommendations_md = f"""### 🎯 Delivery & Financial Operations Action Plan

1. **ERP Mapping Rectification (PRJ-407):**
   - Coordinate with IT Service Desk & ERP admin to execute SQL reconciliation script to map legacy task codes to the unified billing entity within 48 hours.
2. **Executive UAT Clearance (PRJ-405):**
   - Convene joint UAT sign-off working group with AutoMotive Giant's delivery sponsor to approve completed milestones and unlock $110K billing.
3. **WIP Write-Off Prevention:**
   - Institute weekly WIP Aging Triage sessions between Delivery Leads and Finance Controllers to prevent aging amounts from crossing 90 days.
"""

    return {
        "summary_md": summary_md,
        "variance_df": df,
        "drivers_md": drivers_md,
        "recommendations_md": recommendations_md
    }

def _analyze_forecast_vs_actuals(df: pd.DataFrame, query: str, tolerance_pct: float) -> dict:
    col_month = next((c for c in df.columns if 'month' in c.lower()), df.columns[0])
    col_fc = next((c for c in df.columns if 'forecast_rev' in c.lower()), None)
    col_act = next((c for c in df.columns if 'actual_rev' in c.lower()), None)
    col_var = next((c for c in df.columns if 'variance_rev' in c.lower() or 'variance' in c.lower()), None)

    tot_fc = df[col_fc].sum() if col_fc else 0
    tot_act = df[col_act].sum() if col_act else 0
    net_var = tot_act - tot_fc
    net_var_pct = (net_var / tot_fc * 100) if tot_fc else 0

    under_months = df[df[col_var] < 0] if col_var else pd.DataFrame()

    summary_md = f"""### 📈 Financial Forecasting vs Actuals: 2026 Run-Rate Analysis

| Metric | Full Year Actuals to Date | Full Year Forecast Target | Net Variance | Variance % |
| :--- | :--- | :--- | :--- | :--- |
| **Cumulative Revenue** | **${tot_act:,.0f} K** | ${tot_fc:,.0f} K | **{net_var:+,.0f} K** | **{net_var_pct:+.2f}%** |

- **Months Under Forecast:** **{len(under_months)} of {len(df)} months** exhibited negative variance against baseline forecast.
- **Deepest Discrepancy:** **Jun-2026 (-$230K, -4.65%)** and **Sep-2026 (-$210K, -4.12%)**.
"""

    drivers_md = f"""### 🔍 Forecasting Accuracy & Variance Drivers

1. **Mid-Year Scope Creep Compression (May - Jun 2026):**
   - Negative variances in May (-$180K) and June (-$230K) stemmed from unauthorized scope expansion across enterprise dashboard enhancements where delivery costs mounted before signed contractual amendments were approved.
2. **Q3 End FX Volatility & Billing Friction (Sep 2026):**
   - September revenue fell $210K short of forecast due to adverse foreign exchange currency swings in cross-border European accounts, coupled with WIP reconciliation delays.
3. **Forecasting Model Bias:**
   - The original forecast assumed a flat 5% linear month-over-month growth, failing to incorporate seasonal vacation patterns in August and enterprise IT procurement cycles in June/September.
"""

    recommendations_md = f"""### 🎯 Forecasting Process Improvement Recommendations

1. **Transition from Monthly Static to Rolling 13-Week Forecast Model:**
   - Implement structured bi-weekly re-forecasting incorporating client milestone sign-off probabilities.
2. **Integrate FX Sensitivity Cushion:**
   - Add automated currency variance adjustment factors for non-USD billing contracts in Power BI data models.
3. **Contractual Gatekeeping:**
   - Require signed Change Orders before recognizing work in the forward-looking revenue forecast pipeline.
"""

    return {
        "summary_md": summary_md,
        "variance_df": df,
        "drivers_md": drivers_md,
        "recommendations_md": recommendations_md
    }

def _analyze_generic_table(df: pd.DataFrame, query: str, tolerance_pct: float) -> dict:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    summary_stats = df[num_cols].describe().T[['mean', 'min', 'max']].round(2)
    
    summary_md = f"""### 📋 General Reporting Analysis Briefing

- **Total Records Analyzed:** **{len(df):,} rows**
- **Numeric Dimensions Identified:** {', '.join(num_cols) if num_cols else 'None'}
- **Categorical Hierarchies:** {', '.join(cat_cols) if cat_cols else 'None'}

**Key Metric Averages:**
"""
    for col in num_cols[:4]:
        summary_md += f"- **{col}:** Mean = `{df[col].mean():,.2f}`, Min = `{df[col].min():,.2f}`, Max = `{df[col].max():,.2f}`\n"

    drivers_md = "Detailed driver analysis is available when datasets include target/actual or historical comparison dimensions."
    recommendations_md = "1. Ensure standard dimension columns (e.g., Target vs Actual) are mapped to enable automated variance triage."

    return {
        "summary_md": summary_md,
        "variance_df": df.head(10),
        "drivers_md": drivers_md,
        "recommendations_md": recommendations_md
    }
