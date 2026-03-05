import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page configuration — MUST be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="papernest — Sales Operations",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    import os
    df = pd.read_excel(
        os.path.join(os.path.dirname(__file__), 'datos_bc.xlsx'),
        sheet_name='1. Sales Database'
    )
    df['Sale date'] = pd.to_datetime(df['Sale date'])
    df['Call duration'] = df.iloc[:, 8]
    df['Channel'] = df.iloc[:, 9]
    df['Contract status'] = df['Contract status'].fillna('(empty)')
    return df

df_sales = load_data()

# ---------------------------------------------------------------------------
# CSS — Full papernest branding
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
*, *::before, *::after { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #0E0C1A; }
.block-container { padding-top: 2rem !important; }

/* ── Purple top accent bar ── */
.stApp::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #6B4FBB 0%, #9B7FEB 50%, #6B4FBB 100%);
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #100E1C !important;
    border-right: 1px solid #1E1A35 !important;
    border-left: 3px solid #6B4FBB !important;
    min-width: 250px !important;
    width: 250px !important;
    transform: none !important;
}
button[kind="header"] { display: none !important; }
button[data-testid="baseButton-headerNoPadding"] { display: none !important; }
button[aria-label="Open keyboard shortcuts dialog"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* Sidebar labels */
section[data-testid="stSidebar"] label p {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #6B6B8A !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}

/* Multiselect container */
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #1A1730 !important;
    border: 1px solid #2D2850 !important;
    border-radius: 6px !important;
}

/* Multiselect tags — override cyan with purple */
section[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: #2D1F6E !important;
    border: 1px solid #6B4FBB !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
}
section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #C4A8FF !important;
    font-size: 11px !important;
    font-weight: 500 !important;
}
/* Tag close button */
section[data-testid="stSidebar"] span[data-baseweb="tag"] button {
    color: #9B7FEB !important;
}

/* Sidebar divider */
section[data-testid="stSidebar"] hr {
    border-color: #1E1A35 !important;
    margin: 12px 0 !important;
}

/* ── KPI Cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #13102A 0%, #1A1535 100%) !important;
    border: 1px solid #2A2550 !important;
    border-top: 2px solid #6B4FBB !important;
    border-radius: 10px !important;
    padding: 18px 20px !important;
}
div[data-testid="stMetric"] label p {
    color: #7A7A9A !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    font-weight: 600 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #F0ECFF !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
}

/* ── Dataframe table ── */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
}
.stDataFrame thead tr th {
    background-color: #1E1A35 !important;
    color: #9B7FEB !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    border-bottom: 1px solid #2D2850 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* NUEVAS LÍNEAS PARA EL BOTÓN DE KEYBOARD */
[data-testid="stHelpAction"] { display: none !important; }
button[aria-label="Open keyboard shortcuts dialog"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }

/* Refuerzo para ocultar la barra de herramientas superior completa */
header[data-testid="stHeader"] {
    background: transparent !important;
    display: none !important;

/* ── Section labels ── */
.section-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6B4FBB;
    font-weight: 700;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #2D2850, transparent);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Plotly base layout — NO 'legend' key
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8890A4", size=11),
    margin=dict(l=12, r=12, t=44, b=12),
    xaxis=dict(
        gridcolor="#1E1A35",
        zerolinecolor="#2D2850",
        tickfont=dict(size=11, color="#6B6B8A"),
        showline=False,
    ),
    yaxis=dict(
        gridcolor="#1E1A35",
        zerolinecolor="#2D2850",
        tickfont=dict(size=11, color="#6B6B8A"),
        showline=False,
    ),
    hoverlabel=dict(
        bgcolor="#1E1A35",
        bordercolor="#6B4FBB",
        font=dict(family="Inter", size=12, color="#E2E8F0")
    ),
    title=dict(
        font=dict(size=13, color="#C4C4D8", family="Inter", weight=600),
        x=0,
        xanchor='left',
        pad=dict(l=4)
    )
)

PURPLE_PALETTE = ['#6B4FBB', '#9B7FEB', '#C4A8FF', '#E8DCFF']
STATUS_COLORS  = {"NET": "#6B4FBB", "BRUT": "#F6C90E", "(empty)": "#3D3D5C"}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px 8px 16px 8px;">
            <div style="font-size:18px; font-weight:700; line-height:1.2; letter-spacing:-0.3px;">
                <span style="color:#F0ECFF;">paper</span><span style="color:#9B7FEB;">nest</span>
            </div>
            <div style="color:#3A3A5A; font-size:9px; text-transform:uppercase;
                        letter-spacing:1.8px; margin-top:5px; font-weight:600;">
                Sales Operations Intelligence
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    status_options  = sorted(df_sales['Contract status'].dropna().unique().tolist())
    site_options    = sorted(df_sales['Sales site'].dropna().unique().tolist())
    channel_options = sorted([c for c in df_sales['Channel'].dropna().unique().tolist() if c != '--'])
    offer_options   = ['Elec', 'GasElec']

    selected_status   = st.multiselect("Contract Status",  status_options,  default=status_options,  key="s1")
    selected_sites    = st.multiselect("Sales Site",        site_options,    default=site_options,    key="s2")
    selected_channels = st.multiselect("Channel",           channel_options, default=channel_options, key="s3")
    selected_offers   = st.multiselect("Offer",             offer_options,   default=offer_options,   key="s4")

    st.markdown("---")
    st.markdown("""
        <div style="color:#2D2D4A; font-size:10px; line-height:1.6; padding: 0 2px;">
            Data source: datos_bc.xlsx<br>
            All filters apply simultaneously
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Filter logic
# ---------------------------------------------------------------------------
df = df_sales.copy()
if set(selected_status)   != set(status_options):   df = df[df['Contract status'].isin(selected_status)]
if set(selected_sites)    != set(site_options):     df = df[df['Sales site'].isin(selected_sites)]
if set(selected_channels) != set(channel_options):  df = df[df['Channel'].isin(selected_channels)]
if set(selected_offers)   != set(offer_options):    df = df[df['Offer'].isin(selected_offers)]

df_charts = df[df['Channel'] != '--']
net_df    = df[df['Contract status'] == 'NET'].copy()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
total_contracts  = len(df)
net_contracts    = len(net_df)
brut_contracts   = len(df[df['Contract status'] == 'BRUT'])
total_net_rev    = net_df['Income'].sum()
val_rate         = (net_contracts / (net_contracts + brut_contracts) * 100) if (net_contracts + brut_contracts) > 0 else 0

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="font-size:11px; font-weight:600; letter-spacing:2px;
                    text-transform:uppercase; color:#4A4A6A; margin-bottom:6px;">
            <span style="color:#6B4FBB;">paper</span><span style="color:#4A4A6A;">nest</span>
            &nbsp;·&nbsp; Productivity & Processes Lead
        </div>
        <div style="font-size:22px; font-weight:700; color:#F0ECFF; letter-spacing:-0.3px;">
            Sales Operations Dashboard
        </div>
        <div style="font-size:12px; color:#4A4A6A; margin-top:4px;">
            Showing&nbsp;
            <span style="color:#9B7FEB; font-weight:600;">{total_contracts:,}</span>
            &nbsp;contracts across&nbsp;
            <span style="color:#9B7FEB; font-weight:600;">{df['Sales site'].nunique()}</span>
            &nbsp;sites
        </div>
    </div>
""", unsafe_allow_html=True)

# KPI row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Contracts",      f"{total_contracts:,}")
k2.metric("NET Contracts",        f"{net_contracts:,}")
k3.metric("Total NET Revenue",    f"€{total_net_rev:,.0f}")
k4.metric("Validation Rate",      f"{val_rate:.1f}%")

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 1: Revenue by Site | Channel Stack
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Performance Breakdown</div>', unsafe_allow_html=True)

rev_by_site = net_df.groupby('Sales site', as_index=False)['Income'].sum().sort_values('Income', ascending=True)
fig_rev = px.bar(rev_by_site, x='Income', y='Sales site', orientation='h',
                 title='NET Revenue by Sales Site', color_discrete_sequence=['#6B4FBB'])
fig_rev.update_traces(
    marker_color='#6B4FBB',
    marker_line_width=0,
    hovertemplate='<b>%{y}</b><br>€%{x:,.0f}<extra></extra>'
)
fig_rev.update_layout(**PLOTLY_LAYOUT, height=340, xaxis_title="", yaxis_title="")
fig_rev.update_xaxes(tickprefix="€", tickformat=",.0f")

stack_df = df_charts.groupby(['Channel', 'Contract status'], as_index=False).size().rename(columns={'size': 'Contracts'})
fig_stack = px.bar(stack_df, x='Channel', y='Contracts', color='Contract status',
                   barmode='stack', title='Contracts by Channel & Status',
                   color_discrete_map=STATUS_COLORS)
fig_stack.update_traces(marker_line_width=0,
                        hovertemplate='<b>%{x}</b> · %{data.name}<br>%{y} contracts<extra></extra>')
fig_stack.update_layout(**PLOTLY_LAYOUT, height=340, xaxis_title="", yaxis_title="Contracts")
fig_stack.update_layout(
    legend=dict(orientation="h", yanchor="top", y=-0.12,
                xanchor="center", x=0.5,
                font=dict(size=11, color="#6B6B8A"),
                bgcolor="rgba(0,0,0,0)", title_text="")
)

c1, c2 = st.columns(2)
c1.plotly_chart(fig_rev,   use_container_width=True)
c2.plotly_chart(fig_stack, use_container_width=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: NET by Month | Validation Rate
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Trends & Validation</div>', unsafe_allow_html=True)

net_df['Month'] = net_df['Sale date'].dt.to_period('M').dt.to_timestamp()
net_monthly = net_df.groupby('Month', as_index=False).size().rename(columns={'size': 'NET Contracts'})
fig_line = px.line(net_monthly, x='Month', y='NET Contracts',
                   title='NET Contracts by Month', color_discrete_sequence=['#9B7FEB'])
fig_line.update_traces(
    line=dict(width=2),
    marker=dict(size=5, color='#9B7FEB', line=dict(width=1.5, color='#6B4FBB')),
    fill='tozeroy',
    fillcolor='rgba(107,79,187,0.08)',
    hovertemplate='<b>%{x|%b %Y}</b><br>%{y} NET contracts<extra></extra>'
)
fig_line.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="", yaxis_title="")

site_stats = df.groupby('Sales site', as_index=False).agg(
    NET=('Contract status', lambda s: (s == 'NET').sum()),
    BRUT=('Contract status', lambda s: (s == 'BRUT').sum())
)
site_stats['Rate'] = (site_stats['NET'] / (site_stats['NET'] + site_stats['BRUT']) * 100).round(1)
site_stats = site_stats.sort_values('Rate', ascending=True)

colors_rate = ['#4CAF50' if r >= 60 else '#FF6B6B' for r in site_stats['Rate']]
fig_rate = go.Figure(go.Bar(
    x=site_stats['Rate'],
    y=site_stats['Sales site'],
    orientation='h',
    marker_color=colors_rate,
    marker_line_width=0,
    hovertemplate='<b>%{y}</b><br>%{x:.1f}%<extra></extra>',
    text=[f"{r:.0f}%" for r in site_stats['Rate']],
    textposition='outside',
    textfont=dict(size=11, color='#8890A4')
))
fig_rate.update_layout(**PLOTLY_LAYOUT, height=320)
fig_rate.update_layout(title_text='Validation Rate by Sales Site')
fig_rate.update_xaxes(range=[0, 110], ticksuffix='%', tickvals=[0, 20, 40, 60, 80, 100])


c3, c4 = st.columns(2)
c3.plotly_chart(fig_line, use_container_width=True)
c4.plotly_chart(fig_rate, use_container_width=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Ranked Table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Team Rankings</div>', unsafe_allow_html=True)

ranked = net_df.groupby(['Team', 'Channel', 'Sales site'], as_index=False).agg(
    NET_Contracts=('Unique identifier', 'count'),
    NET_Revenue=('Income', 'sum')
).sort_values('NET_Revenue', ascending=False).reset_index(drop=True)
ranked.index = ranked.index + 1
ranked.index.name = 'Rank'
ranked['NET_Revenue'] = ranked['NET_Revenue'].apply(lambda v: f"€{v:,.1f}")

# Build HTML table
rows_html = ""
for i, row in ranked.iterrows():
    bg = "#13102A" if i % 2 == 0 else "#0E0C1A"
    rows_html += f"""
    <tr style="background:{bg};">
        <td style="padding:10px 12px;color:#6B6B8A;font-size:12px;">{i}</td>
        <td style="padding:10px 12px;color:#E2E8F0;font-weight:500;">{row['Team']}</td>
        <td style="padding:10px 12px;color:#A0AEC0;">{row['Channel']}</td>
        <td style="padding:10px 12px;color:#A0AEC0;">{row['Sales site']}</td>
        <td style="padding:10px 12px;color:#9B7FEB;text-align:right;font-weight:600;">{int(row['NET_Contracts'])}</td>
        <td style="padding:10px 12px;color:#C4A8FF;text-align:right;font-weight:600;">{row['NET_Revenue']}</td>
    </tr>"""

table_html = f"""
<div style="border-radius:8px;overflow:hidden;border:1px solid #1E1A35;">
<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
    <thead>
        <tr style="background:#1E1A35;">
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:left;font-weight:600;">Rank</th>
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:left;font-weight:600;">Team</th>
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:left;font-weight:600;">Channel</th>
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:left;font-weight:600;">Site</th>
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:right;font-weight:600;">NET Contracts</th>
            <th style="padding:10px 12px;color:#6B4FBB;font-size:10px;text-transform:uppercase;letter-spacing:1px;text-align:right;font-weight:600;">NET Revenue</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
</div>"""

st.markdown(table_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 40px 0 20px 0;
            border-top: 1px solid #1A1735; margin-top: 32px;">
    <p style="font-size:11px; color:#2D2D4A; margin:0; letter-spacing:0.3px;">
        Developed by <span style="color:#4A4A6A;">Jonathan M. Tejada Amado</span>
        &nbsp;·&nbsp;
        Built for a specific professional use case as part of a hiring process.
        Will be decommissioned once the process concludes.
    </p>
</div>
""", unsafe_allow_html=True)