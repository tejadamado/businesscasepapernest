import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# Page config — MUST be first
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="papernest — Operational Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    path = os.path.join(os.path.dirname(__file__), 'datos_bc.xlsx')

    df = pd.read_excel(path, sheet_name='1. Sales Database')

    # Col I = Call duration (index 8), Col J = Channel (index 9)
    df['Call duration'] = df.iloc[:, 8]
    df['Channel']       = df.iloc[:, 9]

    # '--' is the literal marker for missing data
    # Flag BEFORE replacing so we capture the gap correctly
    df['has_duration'] = df['Call duration'].apply(
        lambda x: False if (pd.isna(x) or str(x).strip() == '--') else True
    )

    # Replace '--' with NaN for numeric operations
    df['Call duration'] = df['Call duration'].replace('--', None)
    df['Call duration'] = pd.to_numeric(df['Call duration'], errors='coerce')

    # Normalize contract status — empty cells = abandoned contracts
    df['Contract status'] = df['Contract status'].fillna('(empty)')

    # Normalize channel
    df['Channel'] = df['Channel'].fillna('--').astype(str)

    return df

df_sales = load_data()

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #0E0C1A; }
.block-container { padding-top: 2rem !important; }

.stApp::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #6B4FBB 0%, #9B7FEB 50%, #6B4FBB 100%);
    width: 100%;
    position: fixed;
    top: 0; left: 0;
    z-index: 9999;
}

section[data-testid="stSidebar"] {
    background-color: #100E1C !important;
    border-right: 1px solid #1E1A35 !important;
    border-left: 3px solid #6B4FBB !important;
    min-width: 250px !important;
    width: 250px !important;
    transform: none !important;
}
button[kind="header"] { display: none !important; }

section[data-testid="stSidebar"] label p {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #6B6B8A !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #1A1730 !important;
    border: 1px solid #2D2850 !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: #2D1F6E !important;
    border: 1px solid #6B4FBB !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #C4A8FF !important;
    font-size: 11px !important;
}
section[data-testid="stSidebar"] span[data-baseweb="tag"] button {
    color: #9B7FEB !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #1E1A35 !important;
    margin: 12px 0 !important;
}

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
}

.insight-box {
    background: linear-gradient(135deg, #13102A 0%, #1A1535 100%);
    border: 1px solid #2A2550;
    border-left: 3px solid #6B4FBB;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 8px 0;
}
.insight-warn {
    border-left-color: #F6C90E !important;
    background: linear-gradient(135deg, #1A1500 0%, #1A1A00 100%) !important;
}
.insight-good {
    border-left-color: #4CAF50 !important;
    background: linear-gradient(135deg, #001A00 0%, #001500 100%) !important;
}
.insight-bad {
    border-left-color: #FF6B6B !important;
    background: linear-gradient(135deg, #1A0000 0%, #150000 100%) !important;
}

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

#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Cleanest UI possible ── */
header, [data-testid="stHeader"] { visibility: hidden; height: 0; }
[data-testid="collapseSidebar"] { display: none !important; }
section[data-testid="stSidebar"] button { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Plotly base layout
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8890A4", size=11),
    margin=dict(l=12, r=12, t=44, b=12),
    xaxis=dict(gridcolor="#1E1A35", zerolinecolor="#2D2850",
               tickfont=dict(size=11, color="#6B6B8A"), showline=False),
    yaxis=dict(gridcolor="#1E1A35", zerolinecolor="#2D2850",
               tickfont=dict(size=11, color="#6B6B8A"), showline=False),
    hoverlabel=dict(bgcolor="#1E1A35", bordercolor="#6B4FBB",
                    font=dict(family="Inter", size=12, color="#E2E8F0")),
    title=dict(font=dict(size=13, color="#C4C4D8", family="Inter"),
               x=0, xanchor='left', pad=dict(l=4))
)

STATUS_COLORS = {"NET": "#6B4FBB", "BRUT": "#F6C90E", "(empty)": "#3D3D5C"}
PURPLE_PALETTE = ['#6B4FBB', '#9B7FEB', '#C4A8FF', '#E8DCFF']

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px 4px 8px 4px;">
            <div style="font-size:20px; font-weight:700; line-height:1.2;">
                <span style="color:#F0ECFF;">paper</span><span style="color:#9B7FEB;">nest</span>
            </div>
            <div style="color:#4A4A6A; font-size:10px; text-transform:uppercase;
                        letter-spacing:1.5px; margin-top:4px; font-weight:500;">
                Operational Intelligence
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    site_opts    = sorted([s for s in df_sales['Sales site'].dropna().unique() if s != '--'])
    channel_opts = sorted([c for c in df_sales['Channel'].dropna().unique() if c != '--'])
    op_opts      = sorted(df_sales['Type of operation'].dropna().unique().tolist())
    offer_opts   = ['Elec', 'GasElec']

    sel_sites    = st.multiselect("Sales Site",          site_opts,    default=site_opts,    key="f1")
    sel_channels = st.multiselect("Channel",             channel_opts, default=channel_opts, key="f2")
    sel_ops      = st.multiselect("Type of Operation",   op_opts,      default=op_opts,      key="f3")
    sel_offers   = st.multiselect("Offer",               offer_opts,   default=offer_opts,   key="f4")

    st.markdown("---")
    st.markdown("""<div style="color:#2D2D4A; font-size:10px; line-height:1.8;">
        Filters apply to all sections<br>
        Insights update automatically
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Filter logic
# ─────────────────────────────────────────────────────────────────────────────
df = df_sales.copy()
if set(sel_sites)    != set(site_opts):    df = df[df['Sales site'].isin(sel_sites)]
if set(sel_channels) != set(channel_opts): df = df[df['Channel'].isin(sel_channels + ['--'])]
if set(sel_ops)      != set(op_opts):      df = df[df['Type of operation'].isin(sel_ops)]
if set(sel_offers)   != set(offer_opts):   df = df[df['Offer'].isin(sel_offers)]

df_charts = df[df['Channel'] != '--'].copy()

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="font-size:22px; font-weight:700; color:#F0ECFF; letter-spacing:-0.3px;">
            Operational Intelligence Dashboard
        </div>
        <div style="font-size:12px; color:#4A4A6A; margin-top:4px;">
            CRM–Telephony gap · Conversion efficiency · Channel margin analysis
            &nbsp;·&nbsp;
            <span style="color:#9B7FEB; font-weight:600;">{len(df):,}</span> contracts in view
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — CRM / Telephony Gap
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 — CRM / Telephony Sync Gap</div>',
            unsafe_allow_html=True)

missing_df  = df[df['has_duration'] == False].copy()
present_df  = df[df['has_duration'] == True].copy()
n_missing   = len(missing_df)
n_present   = len(present_df)
n_total     = len(df)
pct_missing = n_missing / n_total * 100 if n_total > 0 else 0

# KPI row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Contracts",        f"{n_total:,}")
k2.metric("Missing Call Duration",  f"{n_missing:,}",
          delta=f"-{pct_missing:.1f}% of DB", delta_color="inverse")
k3.metric("With Call Duration",     f"{n_present:,}")
k4.metric("Gap Rate",               f"{pct_missing:.1f}%")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# Charts row
c1, c2 = st.columns(2)

with c1:
    # Missing by Channel — stacked by Contract status
    miss_ch = (missing_df[missing_df['Channel'] != '--']
               .groupby(['Channel','Contract status'], as_index=False)
               .size().rename(columns={'size':'Count'}))
    fig = px.bar(miss_ch, x='Channel', y='Count', color='Contract status',
                 barmode='stack', title='Missing Call Duration by Channel',
                 color_discrete_map=STATUS_COLORS)
    fig.update_traces(marker_line_width=0,
                      hovertemplate='<b>%{x}</b> · %{data.name}<br>%{y} contracts<extra></extra>')
    fig.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="", yaxis_title="Contracts")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15,
                                  xanchor="center", x=0.5,
                                  bgcolor="rgba(0,0,0,0)", title_text="",
                                  font=dict(size=11, color="#6B6B8A")))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Missing by Sales Site
    miss_site = (missing_df.groupby('Sales site', as_index=False)
                 .size().rename(columns={'size':'Missing'})
                 .sort_values('Missing', ascending=True))
    miss_site = miss_site[miss_site['Sales site'] != '--']
    fig2 = px.bar(miss_site, x='Missing', y='Sales site', orientation='h',
                  title='Missing Call Duration by Sales Site',
                  color_discrete_sequence=['#9B7FEB'])
    fig2.update_traces(marker_line_width=0,
                       hovertemplate='<b>%{y}</b><br>%{x} missing records<extra></extra>')
    fig2.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

# Auto-insights for section 1
worst_ch = (missing_df[missing_df['Channel'] != '--']
            .groupby('Channel').size().idxmax())
worst_ch_n = missing_df[missing_df['Channel'] == worst_ch].shape[0]
worst_site = (missing_df[missing_df['Sales site'] != '--']
              .groupby('Sales site').size().idxmax())
worst_site_n = missing_df[missing_df['Sales site'] == worst_site].shape[0]

st.markdown(f"""
<div class="insight-box insight-warn">
    ⚠️ <strong>{n_missing:,} contracts ({pct_missing:.1f}%) have no call duration recorded</strong>
    — desynchronisation between CRM and telephony system.
    Highest exposure: <strong>{worst_ch}</strong> channel ({worst_ch_n} records)
    and <strong>{worst_site}</strong> site ({worst_site_n} records).
    Recommended fix: automated daily reconciliation job to flag mismatches before they enter analysis pipelines.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Conversion Efficiency
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">02 — Conversion Efficiency</div>',
            unsafe_allow_html=True)

def conversion_rate(df_in, group_col):
    g = df_in.groupby([group_col, 'Contract status']).size().unstack(fill_value=0).reset_index()
    for s in ['BRUT','NET','(empty)']:
        if s not in g.columns: g[s] = 0
    g['Total']       = g[['BRUT','NET','(empty)']].sum(axis=1)
    g['Conv Rate %'] = (g['NET'] / g['Total'] * 100).round(2)
    g.columns.name  = None
    return g.sort_values('Conv Rate %', ascending=False)

# Overall conversion KPIs
net_total  = len(df[df['Contract status'] == 'NET'])
brut_total = len(df[df['Contract status'] == 'BRUT'])
emp_total  = len(df[df['Contract status'] == '(empty)'])
conv_overall = net_total / len(df) * 100 if len(df) > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Overall Conv. Rate",  f"{conv_overall:.1f}%")
k2.metric("NET Contracts",       f"{net_total:,}")
k3.metric("BRUT Contracts",      f"{brut_total:,}")
k4.metric("Empty (no status)",   f"{emp_total:,}")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

c3, c4 = st.columns(2)

with c3:
    # Conversion rate by Site
    site_conv = conversion_rate(df[df['Sales site'] != '--'], 'Sales site')
    avg_rate  = site_conv['Conv Rate %'].mean()
    colors_site = ['#4CAF50' if r >= avg_rate else '#FF6B6B'
                   for r in site_conv['Conv Rate %']]
    fig3 = go.Figure(go.Bar(
        x=site_conv['Conv Rate %'],
        y=site_conv['Sales site'],
        orientation='h',
        marker_color=colors_site,
        marker_line_width=0,
        text=[f"{r:.1f}%" for r in site_conv['Conv Rate %']],
        textposition='outside',
        textfont=dict(size=11, color='#8890A4'),
        hovertemplate='<b>%{y}</b><br>Conv Rate: %{x:.1f}%<br>'
                      'NET: %{customdata[0]} | BRUT: %{customdata[1]} | Empty: %{customdata[2]}<extra></extra>',
        customdata=site_conv[['NET','BRUT','(empty)']].values
    ))
    fig3.add_vline(x=avg_rate, line_dash="dash", line_color="#6B4FBB",
                   annotation_text=f"Avg {avg_rate:.1f}%",
                   annotation_font_color="#9B7FEB", annotation_font_size=10)
    fig3.update_layout(**PLOTLY_LAYOUT, height=320,
                       title_text='Conversion Rate by Sales Site')
    fig3.update_xaxes(range=[0, site_conv['Conv Rate %'].max() * 1.25],
                      ticksuffix='%')
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    # Conversion rate by Channel
    ch_conv = conversion_rate(df_charts, 'Channel')
    avg_ch  = ch_conv['Conv Rate %'].mean()
    colors_ch = ['#4CAF50' if r >= avg_ch else '#FF6B6B'
                 for r in ch_conv['Conv Rate %']]
    fig4 = go.Figure(go.Bar(
        x=ch_conv['Conv Rate %'],
        y=ch_conv['Channel'],
        orientation='h',
        marker_color=colors_ch,
        marker_line_width=0,
        text=[f"{r:.1f}%" for r in ch_conv['Conv Rate %']],
        textposition='outside',
        textfont=dict(size=11, color='#8890A4'),
        hovertemplate='<b>%{y}</b><br>Conv Rate: %{x:.1f}%<extra></extra>',
    ))
    fig4.add_vline(x=avg_ch, line_dash="dash", line_color="#6B4FBB",
                   annotation_text=f"Avg {avg_ch:.1f}%",
                   annotation_font_color="#9B7FEB", annotation_font_size=10)
    fig4.update_layout(**PLOTLY_LAYOUT, height=320,
                       title_text='Conversion Rate by Channel')
    fig4.update_xaxes(range=[0, ch_conv['Conv Rate %'].max() * 1.25],
                      ticksuffix='%')
    st.plotly_chart(fig4, use_container_width=True)

# Conversion by Type of Operation
op_conv = conversion_rate(df, 'Type of operation')
c5, c6 = st.columns(2)

with c5:
    colors_op = ['#4CAF50' if r >= op_conv['Conv Rate %'].mean() else '#FF6B6B'
                 for r in op_conv['Conv Rate %']]
    fig5 = go.Figure(go.Bar(
        x=op_conv['Conv Rate %'],
        y=op_conv['Type of operation'],
        orientation='h',
        marker_color=colors_op,
        marker_line_width=0,
        text=[f"{r:.1f}%" for r in op_conv['Conv Rate %']],
        textposition='outside',
        textfont=dict(size=11, color='#8890A4'),
        hovertemplate='<b>%{y}</b><br>Conv Rate: %{x:.1f}%<extra></extra>',
    ))
    fig5.update_layout(**PLOTLY_LAYOUT, height=260,
                       title_text='Conversion Rate by Type of Operation')
    fig5.update_xaxes(range=[0, op_conv['Conv Rate %'].max() * 1.3], ticksuffix='%')
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    # EMPTY breakdown by site — shows where data quality is worst
    empty_site = (df[df['Contract status'] == '(empty)']
                  .groupby('Sales site', as_index=False).size()
                  .rename(columns={'size':'Empty Count'})
                  .query("`Sales site` != '--'")
                  .sort_values('Empty Count', ascending=True))
    fig6 = px.bar(empty_site, x='Empty Count', y='Sales site', orientation='h',
                  title='Empty Status Contracts by Site',
                  color_discrete_sequence=['#3D3D5C'])
    fig6.update_traces(marker_line_width=0,
                       hovertemplate='<b>%{y}</b><br>%{x} empty contracts<extra></extra>')
    fig6.update_layout(**PLOTLY_LAYOUT, height=260, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig6, use_container_width=True)

# Auto-insights for section 2
best_site  = site_conv.iloc[0]
worst_site_conv = site_conv.iloc[-1]
best_ch    = ch_conv.iloc[0]
best_op    = op_conv.iloc[0]
worst_op   = op_conv.iloc[-1]
gap_ops    = best_op['Conv Rate %'] - worst_op['Conv Rate %']

st.markdown(f"""
<div class="insight-box insight-good">
    🏆 <strong>{best_site['Sales site']}</strong> leads conversion at
    <strong>{best_site['Conv Rate %']:.1f}%</strong>
    ({best_site['NET']:.0f} NET contracts).
    <strong>{best_ch['Channel']}</strong> is the top-performing channel at
    <strong>{best_ch['Conv Rate %']:.1f}%</strong>.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box insight-bad">
    ⬇️ <strong>{worst_site_conv['Sales site']}</strong> is the lowest-performing site at
    <strong>{worst_site_conv['Conv Rate %']:.1f}%</strong>
    — {avg_rate - worst_site_conv['Conv Rate %']:.1f}pp below average.
    Closing half this gap would generate ~{int(worst_site_conv['Total'] * (avg_rate - worst_site_conv['Conv Rate %']) / 100 / 2)} additional NET contracts
    without acquiring new leads.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box insight-warn">
    📋 <strong>{best_op['Type of operation']}</strong> converts at
    <strong>{best_op['Conv Rate %']:.1f}%</strong> vs
    <strong>{worst_op['Conv Rate %']:.1f}%</strong> for
    <strong>{worst_op['Type of operation']}</strong>
    — a <strong>{gap_ops:.1f}pp gap</strong>.
    Prioritising {best_op['Type of operation']} leads in routing logic
    would immediately improve NTR.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Channel Margin Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">03 — Channel Margin Analysis</div>',
            unsafe_allow_html=True)

net_df = df[df['Contract status'] == 'NET'].copy()
ch_margin = (df_charts.groupby('Channel', as_index=False).agg(
    Total_Contracts=('Unique identifier', 'count'),
    NET_Contracts=('Contract status', lambda x: (x == 'NET').sum()),
    NET_Revenue=('Income', lambda x: x[df_charts.loc[x.index,'Contract status']=='NET'].sum()),
))
ch_margin['Margin %']       = (ch_margin['NET_Contracts'] /
                                ch_margin['Total_Contracts'] * 100).round(1)
ch_margin['Revenue/Lead']   = (ch_margin['NET_Revenue'] /
                                ch_margin['Total_Contracts']).round(2)
ch_margin = ch_margin.sort_values('NET_Revenue', ascending=False)

k1, k2, k3, k4 = st.columns(4)
for i, (_, row) in enumerate(ch_margin.iterrows()):
    [k1, k2, k3, k4][i].metric(
        f"{row['Channel']}",
        f"{row['Margin %']:.1f}% margin",
        f"€{row['NET_Revenue']:,.0f} NET revenue"
    )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

c7, c8 = st.columns(2)

with c7:
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(
        x=ch_margin['Channel'],
        y=ch_margin['Margin %'],
        name='Margin %',
        marker_color='#6B4FBB',
        marker_line_width=0,
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
    ))
    fig7.add_trace(go.Scatter(
        x=ch_margin['Channel'],
        y=ch_margin['Total_Contracts'],
        name='Total Contracts',
        mode='lines+markers',
        line=dict(color='#F6C90E', width=2),
        marker=dict(size=8, color='#F6C90E'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Volume: %{y}<extra></extra>'
    ))
    fig7.update_layout(**PLOTLY_LAYOUT, height=340,
                       title_text='Margin % vs Volume by Channel')
    fig7.update_layout(
        yaxis=dict(title='Margin %', ticksuffix='%',
                   gridcolor="#1E1A35", color="#6B6B8A"),
        yaxis2=dict(title='Total Contracts', overlaying='y', side='right',
                    showgrid=False, color="#F6C90E"),
        legend=dict(orientation="h", yanchor="top", y=-0.15,
                    xanchor="center", x=0.5,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#6B6B8A"))
    )
    st.plotly_chart(fig7, use_container_width=True)

with c8:
    fig8 = go.Figure(go.Bar(
        x=ch_margin['Channel'],
        y=ch_margin['Revenue/Lead'],
        marker_color=PURPLE_PALETTE[:len(ch_margin)],
        marker_line_width=0,
        text=[f"€{v:.2f}" for v in ch_margin['Revenue/Lead']],
        textposition='outside',
        textfont=dict(size=11, color='#8890A4'),
        hovertemplate='<b>%{x}</b><br>Revenue per lead: €%{y:.2f}<extra></extra>'
    ))
    fig8.update_layout(**PLOTLY_LAYOUT, height=340,
                       title_text='Revenue per Lead by Channel')
    fig8.update_yaxes(tickprefix="€")
    st.plotly_chart(fig8, use_container_width=True)

# Auto-insights for section 3
margin_range = ch_margin['Margin %'].max() - ch_margin['Margin %'].min()
lowest_vol   = ch_margin.sort_values('Total_Contracts').iloc[0]
highest_vol  = ch_margin.sort_values('Total_Contracts').iloc[-1]
scale_target = lowest_vol['Total_Contracts'] * 3
potential_rev = scale_target * lowest_vol['Revenue/Lead']

st.markdown(f"""
<div class="insight-box insight-good">
    📊 <strong>All channels operate within a {margin_range:.1f}pp margin band</strong>
    ({ch_margin['Margin %'].min():.1f}%–{ch_margin['Margin %'].max():.1f}%).
    Margin is <strong>not</strong> the differentiator between channels — volume is.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box insight-warn">
    🚀 <strong>{lowest_vol['Channel']}</strong> has the lowest volume
    ({lowest_vol['Total_Contracts']:.0f} contracts) but a competitive margin
    of <strong>{lowest_vol['Margin %']:.1f}%</strong>.
    Scaling to 3× current volume (~{scale_target:.0f} contracts) would generate
    an estimated <strong>€{potential_rev:,.0f}</strong> additional NET revenue
    with no process change required.
    The growth lever is <strong>volume, not efficiency</strong>.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
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