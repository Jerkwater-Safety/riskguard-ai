import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# --- SET PAGE CONFIG ---
st.set_page_config(page_title="RiskGuard AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- INDUSTRY BENCHMARKS ---
INDUSTRY_DEFAULTS = {
    "Manufacturing": {"TRIR": 2.8, "Avg_Claim": 32000},
    "Construction": {"TRIR": 2.5, "Avg_Claim": 45000},
    "Healthcare": {"TRIR": 3.9, "Avg_Claim": 28000},
    "Logistics": {"TRIR": 4.2, "Avg_Claim": 35000}
}

# --- DATA GENERATOR ---
def generate_sample_data():
    causes = ['Overexertion', 'Slips/Falls', 'Struck-By', 'Repetitive Motion', 'Motor Vehicle']
    depts = ['Warehouse', 'Assembly', 'Logistics', 'Administration', 'Maintenance']
    data = []
    for i in range(100):
        date = datetime.now() - timedelta(days=np.random.randint(1, 1000))
        status = np.random.choice(['Open', 'Closed'], p=[0.3, 0.7])
        cause = np.random.choice(causes)
        dept = np.random.choice(depts)
        
        # Financials
        paid_med = np.random.lognormal(mean=8, sigma=1)
        paid_ind = paid_med * 0.4
        
        # If open, assign reserves
        res_med = np.random.lognormal(mean=8.5, sigma=1.2) if status == 'Open' else 0
        res_ind = res_med * 0.5 if status == 'Open' else 0
        
        total_incurred = paid_med + paid_ind + res_med + res_ind
        report_lag = np.random.randint(0, 15)
        
        data.append([
            f"WC-{1000+i}", date, status, cause, dept, 
            round(paid_med, 2), round(paid_ind, 2), 
            round(res_med, 2), round(res_ind, 2), 
            round(total_incurred, 2), report_lag
        ])
    
    return pd.DataFrame(data, columns=[
        'Claim_ID', 'Date', 'Status', 'Cause', 'Department', 
        'Paid_Medical', 'Paid_Indemnity', 'Reserve_Medical', 
        'Reserve_Indemnity', 'Total_Incurred', 'Report_Lag'
    ])

# --- APP START ---
df = generate_sample_data() 

st.title("🛡️ RiskGuard AI Pro")
st.markdown("### *Enterprise Workers' Compensation Intelligence & Financial Recovery*")

# --- KPI CALCULATIONS ---
total_incurred = df['Total_Incurred'].sum()
total_paid = df['Paid_Medical'].sum() + df['Paid_Indemnity'].sum()
total_outstanding = df['Reserve_Medical'].sum() + df['Reserve_Indemnity'].sum()
open_claims_count = len(df[df['Status'] == 'Open'])

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analytics", "💸 Leakage", "📉 Benchmarking", "🔍 Safety Audit", "💼 Reserve Tracker"
])

# (Tabs 1-4 placeholder logic)
for t in [tab1, tab2, tab3, tab4]:
    t.write("Dashboard component loading...")

# --- TAB 5: OPEN CLAIM RESERVE TRACKER ---
with tab5:
    st.header("💼 Open Claim Reserve & Tail Risk Tracker")
    st.write("Monitor open claims to ensure reserve adequacy and prevent 'Creeping Severity'.")

    # Metrics Row
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Total Outstanding (Reserves)", f"${total_outstanding:,.0f}", help="Future money set aside")
    r2.metric("Open Claims", open_claims_count)
    
    paid_ratio = (total_paid/total_incurred)*100 if total_incurred > 0 else 0
    r3.metric("Paid-to-Incurred Ratio", f"{paid_ratio:.1f}%")
    r4.metric("Potential Blow-up Risk", "High", delta="3 claims")

    st.divider()

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Reserve Composition: Medical vs. Indemnity")
        open_df = df[df['Status'] == 'Open']
        if not open_df.empty:
            res_by_cause = open_df.groupby('Cause')[['Reserve_Medical', 'Reserve_Indemnity']].sum().reset_index()
            fig_res = px.bar(res_by_cause, x='Cause', y=['Reserve_Medical', 'Reserve_Indemnity'], 
                            title="Open Reserves by Incident Type", barmode='stack',
                            color_discrete_sequence=['#1f77b4', '#ff7f0e'])
            st.plotly_chart(fig_res, use_container_width=True)
        else:
            st.write("No open claims found.")

    with c2:
        st.subheader("Reserve Distribution")
        res_pie = pd.DataFrame({
            "Type": ["Medical Reserve", "Indemnity Reserve"],
            "Amount": [df['Reserve_Medical'].sum(), df['Reserve_Indemnity'].sum()]
        })
        st.plotly_chart(px.pie(res_pie, values='Amount', names='Type', hole=0.4), use_container_width=True)

    st.divider()
    
    st.subheader("🚩 High-Risk 'Audit Needed' Claims")
    st.write("The following open claims have reserves exceeding $50,000.")
    
    high_risk_claims = df[(df['Status'] == 'Open') & (df['Total_Incurred'] > 50000)].sort_values(by='Total_Incurred', ascending=False)
    
    st.dataframe(high_risk_claims[['Claim_ID', 'Date', 'Cause', 'Department', 'Total_Incurred']], 
                 use_container_width=True, hide_index=True)

    st.info("""
    **Pro-Tip for Claims Management:** Any claim open longer than 18 months with no medical activity in the last 60 days should be targeted for **Settlement / C&R (Compromise and Release)**.
    """)
