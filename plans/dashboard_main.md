# New dashboard/main.py Specification

Below is the complete code to replace the existing `dashboard/main.py`. This version loads real data from `datos_bc.xlsx` and implements the exact specification provided.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Data Loading (real data from Excel)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel('datos_bc.xlsx', sheet_name='1. Sales Database')
    df['Sale date'] = pd.to_datetime(df['Sale date'])
    df['Call duration'] = df.iloc[:, 8]   # col I
    df['Channel'] = df.iloc[:, 9]         # col J
    # Fill empty Contract status with "(empty)"
    df['Contract status'] = df['Contract status'].fillna('(empty)')
    return df

df_sales = load_data()

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="papernest — Sales Operations Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Custom CSS (inject via st.markdown)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global */
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #1A1A2E; }

/* Purple top border */
.stApp::before {
    content: '';
    display: block;
    height: 4px;
    background: #6B4FBB;
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
}

/* Sidebar — always visible, no collapse */
section[data-testid="stSidebar"] {
    background-color: #13111C !important;
    border-left: 4px solid #6B4FBB !important;
    min-width: 260px !important;
    width: 260px !important;
    transform: none !important;
}
button[kind="header"] { display: none !important; }

/* Sidebar filter labels */
section[data-testid="stSidebar"] label {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #A0AEC0 !important;
    font-weight: 600 !important;
}

/* Multiselect tags */
section[data-testid="stSidebar"] .stMultiSelect span {
    font-size: 12px !important;
    padding: 2px 8px !important;
}

/* KPI cards */
div[data-testid="stMetric"] {
    background-color: #16213E;
    border-left: 3px solid #6B4FBB;
    border-radius: 8px;
    padding: 20px 24px;
}
div[data-testid="stMetric"] label {
    color: #A0AEC0 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Plotly layout (NO 'legend' key here)
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#CBD5E0", size=12),
    margin=dict(l=40, r=24, t=50, b=40),
    xaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
    yaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
)

PURPLE_PALETTE = ['#6B4FBB', '#9B7FEB', '#C4A8FF', '#E8DCFF']
STATUS_COLORS = {"NET": "#6B4FBB", "BRUT": "#F6C90E"}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # Logo HTML
    st.markdown(
        "<span style='color:#FFFFFF;font-size:22px;font-weight:700;'>📄 paper</span>"
        "<span style='color:#6B4FBB;font-size:22px;font-weight:700;'>nest</span>"
        "<p style='color:#A0AEC0;font-size:11px;margin-top:0;'>Operations Intelligence</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Contract Status filter
    status_options = sorted(df_sales['Contract status'].unique().tolist())
    selected_status = st.multiselect(
        "Contract Status",
        options=status_options,
        default=status_options,
        key="status_filter"
    )

    # Sales Site filter
    site_options = sorted(df_sales['Sales site'].unique().tolist())
    selected_sites = st.multiselect(
        "Sales Site",
        options=site_options,
        default=site_options,
        key="site_filter"
    )

    # Channel filter (exclude '--')
    channel_options = sorted([c for c in df_sales['Channel'].unique().tolist() if c != '--'])
    selected_channels = st.multiselect(
        "Channel",
        options=channel_options,
        default=channel_options,
        key="channel_filter"
    )

    # Offer filter (hardcoded Elec, GasElec only)
    offer_options = ['Elec', 'GasElec']
    selected_offers = st.multiselect(
        "Offer",
        options=offer_options,
        default=offer_options,
        key="offer_filter"
    )

# ---------------------------------------------------------------------------
# Filter logic
# ---------------------------------------------------------------------------
df = df_sales.copy()

# Apply filters only if selection differs from all options
if set(selected_status) != set(status_options):
    df = df[df['Contract status'].isin(selected_status)]

if set(selected_sites) != set(site_options):
    df = df[df['Sales site'].isin(selected_sites)]

if set(selected_channels) != set(channel_options):
    df = df[df['Channel'].isin(selected_channels)]

if set(selected_offers) != set(offer_options):
    df = df[df['Offer'].isin(selected_offers)]

# Exclude '--' from charts (but keep in dataset for KPIs)
df_charts = df[df['Channel'] != '--']

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# Sales Operations Dashboard")
st.markdown(
    f"<span style='color:#A0AEC0;font-size:0.85rem;'>"
    f"Showing <strong style='color:#6B4FBB'>{len(df):,}</strong> contracts "
    f"across <strong style='color:#6B4FBB'>{df['Sales site'].nunique()}</strong> sites"
    f"</span>",
    unsafe_allow_html=True
)

st.markdown("")

# ---------------------------------------------------------------------------
# KPI Row (4 columns)
# ---------------------------------------------------------------------------
total_contracts = len(df)
net_contracts = len(df[df['Contract status'] == 'NET'])
total_net_revenue = df.loc[df['Contract status'] == 'NET', 'Income'].sum()
validation_rate = (net_contracts / total_contracts * 100) if total_contracts > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TOTAL CONTRACTS", f"{total_contracts:,}")
col2.metric("NET CONTRACTS", f"{net_contracts:,}")
col3.metric("TOTAL NET REVENUE (€)", f"{total_net_revenue:,.0f}")
col4.metric("VALIDATION RATE", f"{validation_rate:.1f}%")

st.markdown("")

# ---------------------------------------------------------------------------
# Charts Row 1 (2 columns)
# ---------------------------------------------------------------------------
# LEFT — Horizontal bar: "NET Revenue by Sales Site"
net_df = df[df['Contract status'] == 'NET']
rev_by_site = net_df.groupby('Sales site', as_index=False)['Income'].sum()
rev_by_site = rev_by_site.sort_values('Income', ascending=True)

fig_rev = px.bar(
    rev_by_site,
    x='Income',
    y='Sales site',
    orientation='h',
    title='NET Revenue by Sales Site',
    color_discrete_sequence=['#6B4FBB']
)
fig_rev.update_layout(**PLOTLY_LAYOUT, height=380)
fig_rev.update_traces(hovertemplate='<b>%{y}</b><br>Revenue: €%{x:,.0f}<extra></extra>')

# RIGHT — Stacked bar: "Contract Count by Channel & Status"
stack_df = df_charts.groupby(['Channel', 'Contract status'], as_index=False).size()
stack_df = stack_df.rename(columns={'size': 'Contracts'})

fig_stack = px.bar(
    stack_df,
    x='Channel',
    y='Contracts',
    color='Contract status',
    barmode='stack',
    title='Contract Count by Channel & Status',
    color_discrete_map=STATUS_COLORS
)
fig_stack.update_layout(**PLOTLY_LAYOUT, height=380)
fig_stack.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    margin=dict(t=60, b=80)
)
fig_stack.update_traces(hovertemplate='<b>%{x}</b> - %{data.name}<br>Contracts: %{y}<extra></extra>')

col_left1, col_right1 = st.columns(2)
col_left1.plotly_chart(fig_rev, use_container_width=True)
col_right1.plotly_chart(fig_stack, use_container_width=True)

# ---------------------------------------------------------------------------
# Charts Row 2 (2 columns)
# ---------------------------------------------------------------------------
# LEFT — Line chart: "NET Contracts by Month"
net_df['Month'] = net_df['Sale date'].dt.to_period('M').dt.to_timestamp()
net_monthly = net_df.groupby('Month', as_index=False).size()
net_monthly = net_monthly.rename(columns={'size': 'NET Contracts'})

fig_line = px.line(
    net_monthly,
    x='Month',
    y='NET Contracts',
    title='NET Contracts by Month',
    color_discrete_sequence=['#6B4FBB']
)
fig_line.update_traces(
    line=dict(width=2.5),
    marker=dict(size=7),
    fill='tozeroy',
    fillcolor='rgba(107, 79, 187, 0.1)'
)
fig_line.update_layout(**PLOTLY_LAYOUT, height=380)
fig_line.update_traces(hovertemplate='<b>%{x|%b %Y}</b><br>NET Contracts: %{y}<extra></extra>')

# RIGHT — Horizontal bar: "Validation Rate % by Sales Site"
site_stats = df.groupby('Sales site', as_index=False).agg(
    NET=('Contract status', lambda s: (s == 'NET').sum()),
    TOTAL=('Contract status', 'count')
)
site_stats['Validation Rate'] = (site_stats['NET'] / site_stats['TOTAL'] * 100).round(1)
site_stats = site_stats.sort_values('Validation Rate', ascending=True)

fig_rate = px.bar(
    site_stats,
    x='Validation Rate',
    y='Sales site',
    orientation='h',
    title='Validation Rate % by Sales Site',
    color=site_stats['Validation Rate'].apply(lambda r: '#4CAF50' if r >= 60 else '#FF6B6B')
)
fig_rate.update_layout(**PLOTLY_LAYOUT, height=380)
fig_rate.update_xaxes(range=[0, 100], ticksuffix='%')
fig_rate.update_traces(hovertemplate='<b>%{y}</b><br>Validation Rate: %{x:.1f}%<extra></extra>')

col_left2, col_right2 = st.columns(2)
col_left2.plotly_chart(fig_line, use_container_width=True)
col_right2.plotly_chart(fig_rate, use_container_width=True)

# ---------------------------------------------------------------------------
# Ranked Table
# ---------------------------------------------------------------------------
ranked = net_df.groupby(['Team', 'Channel', 'Sales site'], as_index=False).agg(
    NET_Contracts=('Unique identifier', 'count'),
    NET_Revenue=('Income', 'sum')
)
ranked = ranked.sort_values('NET_Revenue', ascending=False).reset_index(drop=True)
ranked.index = ranked.index + 1
ranked.index.name = 'Rank'

st.markdown("")
st.markdown("### Top Performing Teams")
st.dataframe(
    ranked[['Team', 'Channel', 'Sales site', 'NET_Contracts', 'NET_Revenue']],
    use_container_width=True
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding-top:40px; 
border-top:1px solid #2D3748; margin-top:40px;">
<p style="font-size:11px; color:#4A5568;">
Developed by Jonathan M. Tejada Amado · This dashboard was built 
for a specific professional use case as part of a hiring process. 
It will be decommissioned once the process concludes.
</p></div>
""", unsafe_allow_html=True)