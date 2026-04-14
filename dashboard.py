## Streamlit Dashboard
# Tokyo Olympics 2021 - Medal Efficiency Project
# Run with: streamlit run dashboard.py

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page config (must be first) ────────────────────────────────────────────────
st.set_page_config(
    page_title="Tokyo Olympics 2021 Medal Efficiency",
    page_icon="🥇",
    layout="wide",
)

# ── Global CSS animations ──────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0);    }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.92); }
    to   { opacity: 1; transform: scale(1);    }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}

/* ── Metric cards: entrance + hover lift ── */
[data-testid="stMetric"] {
    animation: fadeInUp 0.55s ease-out both;
    border-radius: 10px;
    padding: 4px 6px;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,129,200,0.18);
}
[data-testid="stMetricValue"] {
    animation: scaleIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;
    animation-delay: 0.15s;
}

/* ── Key Findings cards: entrance + hover lift ── */
div[data-testid="stAlert"] {
    animation: fadeInUp 0.5s ease-out both;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    cursor: default;
}
div[data-testid="stAlert"]:hover {
    transform: translateY(-6px) !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.18) !important;
}

/* ── Charts: entrance ── */
[data-testid="stPlotlyChart"] {
    animation: fadeInUp 0.7s ease-out both;
}

/* ── Section headers ── */
h1, h2, h3 {
    animation: fadeIn 0.5s ease-out both;
}

/* ── Column stagger (entrance delay) ── */
[data-testid="column"]:nth-child(1) { animation: fadeInUp 0.5s ease-out 0.05s both; }
[data-testid="column"]:nth-child(2) { animation: fadeInUp 0.5s ease-out 0.15s both; }
[data-testid="column"]:nth-child(3) { animation: fadeInUp 0.5s ease-out 0.25s both; }
[data-testid="column"]:nth-child(4) { animation: fadeInUp 0.5s ease-out 0.35s both; }

/* ── Sidebar filter labels ── */
section[data-testid="stSidebar"] label {
    transition: color 0.2s ease;
}

/* ── Download button hover ── */
[data-testid="stDownloadButton"] button {
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(0,129,200,0.35) !important;
}

/* ── Selectbox and multiselect: subtle focus glow ── */
[data-testid="stSelectbox"]:focus-within,
[data-testid="stMultiSelect"]:focus-within {
    box-shadow: 0 0 0 2px rgba(0,129,200,0.35);
    border-radius: 6px;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    animation: fadeIn 0.6s ease-out both;
}
</style>
""", unsafe_allow_html=True)

# ── Olympic color palette ──────────────────────────────────────────────────────
OLY_BLUE   = "#0081C8"
OLY_YELLOW = "#FCB131"
OLY_BLACK  = "#000000"
OLY_GREEN  = "#00A651"
OLY_RED    = "#EE334E"
OLY_PALETTE = [OLY_BLUE, OLY_YELLOW, OLY_RED, OLY_GREEN, OLY_BLACK]

PLOTLY_TRANSITION = dict(duration=550, easing="cubic-in-out")

METRIC_LABELS = {
    "medals_per_athlete":         "Medals per Athlete",
    "medals_per_million_pop":     "Medals per Million Population",
    "medals_per_billion_gdp":     "Medals per $B GDP",
    "weighted_score_per_athlete": "Weighted Score per Athlete",
    "gold_percentage":            "Gold %",
}

# ── Helper: number formatting ──────────────────────────────────────────────────
def fmt_population(n):
    if pd.isna(n): return "N/A"
    n = float(n)
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    if n >= 1_000:         return f"{n/1_000:.1f}K"
    return str(int(n))

def fmt_gdp(n):
    if pd.isna(n): return "N/A"
    n = float(n)
    if n >= 1_000_000_000_000: return f"${n/1_000_000_000_000:.2f}T"
    if n >= 1_000_000_000:     return f"${n/1_000_000_000:.1f}B"
    if n >= 1_000_000:         return f"${n/1_000_000:.1f}M"
    return f"${n:,.0f}"

def flag_emoji(code):
    if not isinstance(code, str) or len(code) != 3: return ""
    iso3_to_iso2 = {
        "ARG":"AR","ARM":"AM","AUS":"AU","AUT":"AT","AZE":"AZ","BEL":"BE",
        "BFA":"BF","BGR":"BG","BHR":"BH","BHS":"BS","BLR":"BY","BMU":"BM",
        "BRA":"BR","BWA":"BW","CAN":"CA","CHE":"CH","CHN":"CN","CIV":"CI",
        "COL":"CO","CUB":"CU","CZE":"CZ","DEU":"DE","DNK":"DK","DOM":"DO",
        "ECU":"EC","EGY":"EG","ESP":"ES","EST":"EE","ETH":"ET","FIN":"FI",
        "FJI":"FJ","FRA":"FR","GBR":"GB","GEO":"GE","GHA":"GH","GRC":"GR",
        "GRD":"GD","HKG":"HK","HRV":"HR","HUN":"HU","IDN":"ID","IND":"IN",
        "IRL":"IE","IRN":"IR","ISR":"IL","ITA":"IT","JAM":"JM","JOR":"JO",
        "JPN":"JP","KAZ":"KZ","KEN":"KE","KGZ":"KG","KOR":"KR","KWT":"KW",
        "LTU":"LT","LVA":"LV","MAR":"MA","MDA":"MD","MEX":"MX","MKD":"MK",
        "MNG":"MN","MYS":"MY","NAM":"NA","NGA":"NG","NLD":"NL","NOR":"NO",
        "NZL":"NZ","PHL":"PH","POL":"PL","PRI":"PR","PRT":"PT","QAT":"QA",
        "ROU":"RO","RUS":"RU","SAU":"SA","SMR":"SM","SRB":"RS","SVK":"SK",
        "SVN":"SI","SWE":"SE","SYR":"SY","THA":"TH","TKM":"TM","TUN":"TN",
        "TUR":"TR","TWN":"TW","UGA":"UG","UKR":"UA","USA":"US","UZB":"UZ",
        "VEN":"VE","XKX":"XK","ZAF":"ZA",
    }
    iso2 = iso3_to_iso2.get(code.upper(), "")
    if len(iso2) == 2:
        return chr(0x1F1E6 + ord(iso2[0]) - ord('A')) + chr(0x1F1E6 + ord(iso2[1]) - ord('A'))
    return ""

def short_name(name):
    overrides = {
        "United States of America": "the USA",
        "People's Republic of China": "China",
        "Republic of Korea": "South Korea",
        "Russian Olympic Committee": "the ROC",
    }
    return overrides.get(name, name)

# ── Helper: Key Findings text ──────────────────────────────────────────────────
def athlete_rate_phrase(rate, medals, athletes):
    if rate <= 0: return "none of their athletes won a medal"
    pct = rate * 100
    if athletes <= 12:
        return f"{medals} of their {athletes} athletes came home with a medal"
    elif pct >= 40:
        return f"{pct:.0f}% of their athletes won a medal"
    else:
        return f"roughly 1 in every {max(2, round(1/rate))} athletes won a medal"

def cost_per_medal_phrase(medals_per_billion_gdp):
    if medals_per_billion_gdp <= 0: return "N/A"
    m = 1_000 / medals_per_billion_gdp
    return f"${m:,.0f} million" if m < 1_000 else f"${m/1_000:.1f} billion"

def people_per_medal_phrase(medals_per_million_pop):
    if medals_per_million_pop <= 0: return "N/A"
    p = 1_000_000 / medals_per_million_pop
    return f"{p:,.0f} people" if p < 1_000_000 else f"{p/1_000_000:.1f} million people"

# ── Animated counter HTML component ───────────────────────────────────────────
def counter_card(label, end_value, is_float=False, prefix="", suffix="",
                 accent="#0081C8", delay_ms=0):
    """Renders a count-up animated metric card via st.components.v1.html()."""
    fmt = "parseFloat(v.toFixed(3))" if is_float else "Math.round(v)"
    html = f"""<!DOCTYPE html><html><head><style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
              background: transparent; }}
      .card {{
        background: rgba(0,129,200,0.06);
        border: 1px solid rgba(0,129,200,0.18);
        border-radius: 10px;
        padding: 14px 10px 12px;
        text-align: center;
        height: 82px;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        gap: 4px;
      }}
      .lbl {{
        color: #888;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 500;
      }}
      .val {{
        color: {accent};
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1;
        transition: color 0.3s;
      }}
    </style></head><body>
    <div class="card">
      <p class="lbl">{label}</p>
      <p class="val" id="v">{prefix}0{suffix}</p>
    </div>
    <script>
      setTimeout(function() {{
        var el = document.getElementById("v");
        var target = {float(end_value)};
        var dur = 1200;
        var start = performance.now();
        function ease(t) {{ return 1 - Math.pow(1-t, 3); }}
        function tick(now) {{
          var p = Math.min((now - start) / dur, 1);
          var v = target * ease(p);
          el.textContent = "{prefix}" + {fmt} + "{suffix}";
          if (p < 1) requestAnimationFrame(tick);
        }}
        requestAnimationFrame(tick);
      }}, {delay_ms});
    </script>
    </body></html>"""
    return html


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    url = ("https://raw.githubusercontent.com/Hrish52/Tokyo-Olympics-2021-Analytics"
           "/refs/heads/main/olympics_final_analysis.csv")
    df = pd.read_csv(url, index_col=0)
    if "country_code" in df.columns:
        df["flag"]         = df["country_code"].apply(flag_emoji)
        df["display_name"] = df["flag"] + " " + df.index
    else:
        df["display_name"] = df.index
    return df

# ── Lottie (optional — degrades gracefully if package absent) ─────────────────
@st.cache_data
def load_lottie_url(url):
    try:
        import requests
        r = requests.get(url, timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

# ── Banner ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg,#0081C8 0%,#003580 100%);
            padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 1.5rem;
            animation: fadeInUp 0.8s ease-out both;">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 268 86"
       width="240" height="77"
       style="display:block; margin-bottom:1rem;
              filter:drop-shadow(0 2px 6px rgba(0,0,0,0.35));">
    <rect x="0" y="0" width="268" height="86" rx="12" fill="white"/>
    <circle cx="84"  cy="50" r="27" fill="none" stroke="#FCB131" stroke-width="8"/>
    <circle cx="184" cy="50" r="27" fill="none" stroke="#00A651" stroke-width="8"/>
    <circle cx="34"  cy="32" r="27" fill="none" stroke="#0081C8" stroke-width="8"/>
    <circle cx="134" cy="32" r="27" fill="none" stroke="#000000" stroke-width="8"/>
    <circle cx="234" cy="32" r="27" fill="none" stroke="#EE334E" stroke-width="8"/>
  </svg>
  <h1 style="color:white; margin:0; font-size:2.4rem; font-weight:800;
             letter-spacing:-0.5px;">
      Tokyo 2021 — Who <em>Really</em> Won the Olympics?
  </h1>
  <p style="color:rgba(255,255,255,0.85); font-size:1.1rem; margin:0.6rem 0 0 0;">
      Medal efficiency analytics: comparing results against athletes, population &amp; GDP
  </p>
</div>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Loading Olympic data…"):
    df_full = load_data()

# ── Session state defaults (run once) ─────────────────────────────────────────
if "filter_sizes" not in st.session_state:
    st.session_state["filter_sizes"] = df_full["country_size_category"].unique().tolist()
if "filter_medals" not in st.session_state:
    st.session_state["filter_medals"] = (int(df_full["total"].min()), int(df_full["total"].max()))
if "filter_gdp" not in st.session_state:
    st.session_state["filter_gdp"] = df_full["gdp_category"].unique().tolist()
if "selected_metric" not in st.session_state:
    st.session_state["selected_metric"] = "medals_per_athlete"
if "selected_country" not in st.session_state:
    st.session_state["selected_country"] = df_full.index.sort_values()[0]
if "compare_countries" not in st.session_state:
    opts = df_full.index.sort_values().tolist()
    st.session_state["compare_countries"] = opts[:3]

# ── Sidebar: filters + Lottie trophy ──────────────────────────────────────────
st.sidebar.title("🎯 Filters")

try:
    from streamlit_lottie import st_lottie
    lottie_data = load_lottie_url(
        "https://lottie.host/2eff8a49-7480-467b-8079-f2c81be8c452/UKYVeXPx9A.json"
    )
    if lottie_data:
        with st.sidebar:
            st_lottie(lottie_data, height=130, key="sidebar_trophy", speed=0.8)
except ImportError:
    pass

selected_sizes = st.sidebar.multiselect(
    "Country Size",
    options=df_full["country_size_category"].unique(),
    key="filter_sizes",
)
medal_range = st.sidebar.slider(
    "Total Medals Range",
    min_value=int(df_full["total"].min()),
    max_value=int(df_full["total"].max()),
    key="filter_medals",
)
selected_gdp = st.sidebar.multiselect(
    "GDP Category",
    options=df_full["gdp_category"].unique(),
    key="filter_gdp",
)


_sizes = st.session_state.get("filter_sizes", selected_sizes)
_medals = st.session_state.get("filter_medals", medal_range)
_gdp = st.session_state.get("filter_gdp", selected_gdp)

df = df_full[
    (df_full["country_size_category"].isin(_sizes))
    & (df_full["total"] >= _medals[0])
    & (df_full["total"] <= _medals[1])
    & (df_full["gdp_category"].isin(_gdp))
].copy()

# ── Key Findings ───────────────────────────────────────────────────────────────
st.subheader("💡 Key Findings")

if len(df) == 0:
    st.warning("No countries match the current filters — adjust the sidebar to see findings.")
else:
    top_eff_name = df["medals_per_athlete"].idxmax()
    top_eff      = df.loc[top_eff_name]
    eff_phrase   = athlete_rate_phrase(
        top_eff["medals_per_athlete"], int(top_eff["total"]), int(top_eff["athlete_count"])
    )
    top_raw_name     = df["total"].idxmax()
    top_raw          = df.loc[top_raw_name]
    top_raw_eff_rank = int((df["medals_per_athlete"] > top_raw["medals_per_athlete"]).sum() + 1)

    large        = df[df["athlete_count"] >= 20] if (df["athlete_count"] >= 20).any() else df
    top_pc_name  = large["medals_per_million_pop"].idxmax()
    top_pc       = large.loc[top_pc_name]

    top_gdp_name = df["medals_per_billion_gdp"].idxmax()
    top_gdp      = df.loc[top_gdp_name]

    kf1, kf2, kf3, kf4 = st.columns(4)
    with kf1:
        st.info(
            f"🥇 **{top_eff_name}** had the sharpest strike rate in this view — "
            f"{eff_phrase}. That kind of precision is what separates a great "
            f"Olympic programme from simply sending a large squad."
        )
    with kf2:
        st.info(
            f"📊 **{short_name(top_raw_name)}** topped the medal table with "
            f"{int(top_raw['total'])} medals, but it took {int(top_raw['athlete_count'])} "
            f"athletes to get there. Switch to a per-athlete measure and they drop to "
            f"#{top_raw_eff_rank} out of {len(df)} — size is doing a lot of the work."
        )
    with kf3:
        st.info(
            f"🌍 **{top_pc_name}** (population {fmt_population(top_pc['population'])}) "
            f"won {int(top_pc['total'])} medals — one for every "
            f"{people_per_medal_phrase(top_pc['medals_per_million_pop'])}. "
            f"Among nations that sent at least 20 athletes, no country came closer "
            f"to turning its whole population into medal contenders."
        )
    with kf4:
        st.info(
            f"💰 Each medal **{short_name(top_gdp_name)}** won cost roughly "
            f"{cost_per_medal_phrase(top_gdp['medals_per_billion_gdp'])} of GDP — "
            f"the most economical return in this view. "
            f"Winning medals is not simply a matter of how much a nation spends."
        )

st.markdown("---")

# ── Summary metric cards (animated counters) ──────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

if len(df) > 0:
    top_eff_row = df.loc[df["medals_per_athlete"].idxmax()]
    top_pop_row = df.loc[df["medals_per_million_pop"].idxmax()]
    top_gdp_row = df.loc[df["medals_per_billion_gdp"].idxmax()]

    with c1:
        components.html(
            counter_card("Countries in View", len(df), accent=OLY_BLUE, delay_ms=0),
            height=90,
        )
    with c2:
        components.html(
            counter_card("Most Efficient · Athletes", int(top_eff_row["total"]),
                         prefix="🥇 ", suffix=" medals", accent=OLY_YELLOW, delay_ms=100),
            height=90,
        )
    with c3:
        components.html(
            counter_card("Most Efficient · Per Capita",
                         round(top_pop_row["medals_per_million_pop"], 1),
                         is_float=True, suffix=" /M people", accent=OLY_GREEN, delay_ms=200),
            height=90,
        )
    with c4:
        components.html(
            counter_card("Most Efficient · GDP",
                         round(top_gdp_row["medals_per_billion_gdp"], 2),
                         is_float=True, suffix=" /$B GDP", accent=OLY_RED, delay_ms=300),
            height=90,
        )

    # Country names below the counters
    st.caption(
        f"Athlete efficiency leader: **{top_eff_row['display_name']}** · "
        f"Per-capita leader: **{top_pop_row['display_name']}** · "
        f"GDP efficiency leader: **{top_gdp_row['display_name']}**"
    )

# ── Traditional vs Efficiency ──────────────────────────────────────────────────
st.header("📊 The Traditional View vs Reality")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Traditional Medal Count (Top 10)")
    top10_total = df.nlargest(10, "total").copy()
    top10_total["label"] = top10_total["display_name"]
    fig_total = px.bar(
        top10_total, x="label", y="total", color="gold",
        color_continuous_scale=[[0, OLY_BLUE], [0.5, OLY_YELLOW], [1, OLY_RED]],
        title="Top 10 by Total Medal Count",
        labels={"label": "Country", "total": "Total Medals", "gold": "Gold"},
    )
    fig_total.update_layout(xaxis_tickangle=-35, transition=PLOTLY_TRANSITION)
    st.plotly_chart(fig_total, use_container_width=True)
    st.caption(
        "The usual suspects dominate purely because they send hundreds of athletes. "
        "Team size is the biggest predictor of raw totals."
    )

with col_right:
    st.subheader("Efficiency View (Top 10)")
    top10_eff = df.nlargest(10, "medals_per_athlete").copy()
    top10_eff["label"] = top10_eff["display_name"]
    fig_eff = px.bar(
        top10_eff, x="label", y="medals_per_athlete",
        color="medals_per_athlete",
        color_continuous_scale=[[0, OLY_GREEN], [1, OLY_YELLOW]],
        title="Top 10 by Medals per Athlete",
        labels={"label": "Country", "medals_per_athlete": "Medals / Athlete"},
    )
    fig_eff.update_layout(xaxis_tickangle=-35, transition=PLOTLY_TRANSITION)
    st.plotly_chart(fig_eff, use_container_width=True)
    st.caption(
        "A completely different leaderboard emerges. Small nations with elite, "
        "targeted programmes lead the way."
    )

# ── Scatter: Athletes vs Medals ────────────────────────────────────────────────
st.header("🔍 Team Size vs Medal Haul")
fig_scatter = px.scatter(
    df, x="athlete_count", y="total",
    size="population", color="country_size_category",
    color_discrete_sequence=OLY_PALETTE,
    hover_name="display_name",
    hover_data={"gold": True, "silver": True, "bronze": True,
                "medals_per_athlete": ":.3f", "display_name": False},
    title="Athletes Sent vs Total Medals",
    labels={"athlete_count": "Number of Athletes", "total": "Total Medals",
            "country_size_category": "Country Size"},
)
fig_scatter.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color="white")))
fig_scatter.update_layout(transition=PLOTLY_TRANSITION)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown(
    "> **Insight:** Countries **above** the trend line are over-performing relative "
    "to their team size. Look for small bubbles high on the chart — they are the "
    "true punchers-above-weight."
)

# ── Efficiency Rankings ────────────────────────────────────────────────────────
st.header("🏆 Efficiency Rankings")
metric_key = st.selectbox(
    "Choose efficiency metric:",
    options=list(METRIC_LABELS.keys()),
    format_func=lambda k: METRIC_LABELS[k],
    key="selected_metric",
)
top15 = df.nlargest(15, metric_key).copy()
top15["label"] = top15["display_name"]
fig_rank = px.bar(
    top15, x=metric_key, y="label", orientation="h",
    color=metric_key,
    color_continuous_scale=[[0, OLY_BLUE], [0.5, OLY_YELLOW], [1, OLY_RED]],
    title=f"Top 15 Countries — {METRIC_LABELS[metric_key]}",
    labels={"label": "Country", metric_key: METRIC_LABELS[metric_key]},
)
fig_rank.update_layout(
    yaxis={"categoryorder": "total ascending"},
    coloraxis_showscale=False,
    transition=PLOTLY_TRANSITION,
)
st.plotly_chart(fig_rank, use_container_width=True)
sorted_top15 = top15.nlargest(2, metric_key)
leader = sorted_top15.iloc[0]
second = sorted_top15.iloc[1] if len(sorted_top15) > 1 else sorted_top15.iloc[0]
ratio  = leader[metric_key] / second[metric_key] if second[metric_key] else 1
st.caption(
    f"**{leader['display_name']}** leads with **{leader[metric_key]:.2f}** — "
    f"{ratio:.1f}× ahead of **{second['display_name']}** ({second[metric_key]:.2f})."
)

# ── GDP vs Population Efficiency Matrix ───────────────────────────────────────
st.header("⚖️ Who Punches Above Their Weight?")
fig_matrix = px.scatter(
    df, x="medals_per_million_pop", y="medals_per_billion_gdp",
    size="total", color="country_size_category",
    color_discrete_sequence=OLY_PALETTE,
    hover_name="display_name",
    hover_data={"total": True, "gold": True, "population": False,
                "gdp": False, "display_name": False},
    title="Population Efficiency vs GDP Efficiency",
    labels={
        "medals_per_million_pop": "Medals per Million Population",
        "medals_per_billion_gdp": "Medals per $B GDP",
        "country_size_category":  "Country Size",
    },
)
fig_matrix.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color="white")))
med_x = df["medals_per_million_pop"].median()
med_y = df["medals_per_billion_gdp"].median()
fig_matrix.add_vline(x=med_x, line_dash="dot", line_color="grey", opacity=0.5)
fig_matrix.add_hline(y=med_y, line_dash="dot", line_color="grey", opacity=0.5)
fig_matrix.add_annotation(x=med_x * 2.5, y=med_y * 2.5,
    text="⭐ True over-performers", showarrow=False, font=dict(color="grey", size=11))
fig_matrix.update_layout(transition=PLOTLY_TRANSITION)
st.plotly_chart(fig_matrix, use_container_width=True)
st.markdown(
    "> **Top-right quadrant** = efficient on *both* population and GDP. "
    "Dashed lines are medians. Countries here extract the most medals from "
    "both their people and their economy."
)

# ── Country Deep Dive ──────────────────────────────────────────────────────────
st.header("🔬 Country Deep Dive")
country_options = df.index.sort_values().tolist()
if st.session_state.get("selected_country") not in df.index:
    st.session_state["selected_country"] = country_options[0] if country_options else None
selected_country = st.selectbox(
    "Select a country to inspect:",
    options=country_options,
    format_func=lambda c: df.loc[c, "display_name"] if c in df.index else c,
    key="selected_country",
)
country_data = df.loc[selected_country]

# Animated counter cards for numeric metrics
m1, m2, m3 = st.columns(3)
with m1:
    components.html(counter_card("Total Medals",  int(country_data["total"]),
                                 accent=OLY_BLUE, delay_ms=0),   height=90)
    components.html(counter_card("Gold Medals",   int(country_data["gold"]),
                                 prefix="🥇 ", accent="#DAA520", delay_ms=80), height=90)
with m2:
    components.html(counter_card("Athletes Sent", int(country_data["athlete_count"]),
                                 accent=OLY_GREEN, delay_ms=160), height=90)
    components.html(counter_card("Medals per Athlete",
                                 country_data["medals_per_athlete"],
                                 is_float=True, accent=OLY_YELLOW, delay_ms=240), height=90)
with m3:
    st.metric("Population", fmt_population(country_data["population"]))
    st.metric("GDP",        fmt_gdp(country_data["gdp"]))

# Rankings + donut
rank_col, donut_col = st.columns([1, 1])
n = len(df)
with rank_col:
    st.subheader(f"Rankings for {country_data['display_name']}")
    rank_athlete = (df["medals_per_athlete"]     > country_data["medals_per_athlete"]).sum() + 1
    rank_pop     = (df["medals_per_million_pop"] > country_data["medals_per_million_pop"]).sum() + 1
    rank_gdp     = (df["medals_per_billion_gdp"] > country_data["medals_per_billion_gdp"]).sum() + 1
    st.markdown(f"""
Based on the current filtered dataset of **{n}** countries:

| Metric | Rank |
|---|---|
| Medals per Athlete       | **#{rank_athlete} of {n}** |
| Per Capita Efficiency    | **#{rank_pop} of {n}**     |
| GDP Efficiency           | **#{rank_gdp} of {n}**     |
| Population               | **{fmt_population(country_data['population'])}** |
| GDP                      | **{fmt_gdp(country_data['gdp'])}**               |
""")

with donut_col:
    st.subheader("Medal Breakdown")
    gold_v, silver_v, bronze_v = (int(country_data["gold"]),
                                   int(country_data["silver"]),
                                   int(country_data["bronze"]))
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Gold", "Silver", "Bronze"],
        values=[gold_v, silver_v, bronze_v],
        hole=0.55,
        marker_colors=["#FFD700", "#C0C0C0", "#CD7F32"],
        textinfo="label+value",
        hovertemplate="%{label}: %{value}<extra></extra>",
    )])
    fig_donut.update_layout(
        showlegend=True,
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        transition=PLOTLY_TRANSITION,
        annotations=[dict(
            text=f"<b>{gold_v+silver_v+bronze_v}</b><br>medals",
            x=0.5, y=0.5, font_size=16, showarrow=False
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Country Comparison ─────────────────────────────────────────────────────────
st.header("🆚 Compare Countries")
st.caption("Select 2–3 countries to see them side by side on a normalised radar.")
# Guard: keep only countries still in current filtered df
_cmp_current = [c for c in st.session_state.get("compare_countries", []) if c in df.index]
if not _cmp_current:
    _cmp_current = country_options[:3] if len(country_options) >= 3 else country_options
st.session_state["compare_countries"] = _cmp_current
compare_countries = st.multiselect(
    "Choose countries to compare:",
    options=country_options,
    format_func=lambda c: df.loc[c, "display_name"] if c in df.index else c,
    max_selections=3,
    key="compare_countries",
)

if len(compare_countries) >= 2:
    metrics_to_compare = [
        ("total",                  "Total Medals"),
        ("medals_per_athlete",     "Medals / Athlete"),
        ("medals_per_million_pop", "Medals / M Pop"),
        ("medals_per_billion_gdp", "Medals / $B GDP"),
        ("gold_percentage",        "Gold %"),
    ]
    fig_cmp = go.Figure()
    colors  = [OLY_BLUE, OLY_RED, OLY_GREEN]
    for i, country in enumerate(compare_countries):
        row    = df.loc[country]
        normed = [
            round(row[m] / df[m].max() * 100, 2) if df[m].max() else 0
            for m, _ in metrics_to_compare
        ]
        labels = [lbl for _, lbl in metrics_to_compare]
        fig_cmp.add_trace(go.Scatterpolar(
            r=normed + [normed[0]], theta=labels + [labels[0]],
            fill="toself", name=df.loc[country, "display_name"],
            line_color=colors[i], opacity=0.75,
        ))
    fig_cmp.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Normalised Performance Radar (100 = best in filtered dataset)",
        legend=dict(orientation="h", y=-0.15),
        height=420,
        transition=PLOTLY_TRANSITION,
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    rows = []
    for country in compare_countries:
        row = df.loc[country]
        rows.append({
            "Country":         row["display_name"],
            "Total Medals":    int(row["total"]),
            "Gold":            int(row["gold"]),
            "Athletes":        int(row["athlete_count"]),
            "Medals/Athlete":  round(row["medals_per_athlete"], 3),
            "Medals/M Pop":    round(row["medals_per_million_pop"], 2),
            "Medals/$B GDP":   round(row["medals_per_billion_gdp"], 3),
            "Population":      fmt_population(row["population"]),
            "GDP":             fmt_gdp(row["gdp"]),
        })
    st.dataframe(pd.DataFrame(rows).set_index("Country"), use_container_width=True)
else:
    st.info("Select at least 2 countries above to enable the comparison view.")

# ── Medal Distribution Treemap ─────────────────────────────────────────────────
st.header("🗺️ Medal Distribution")
temp_df = df.reset_index()
fig_tree = px.treemap(
    temp_df, path=["country_size_category", "country"],
    values="total", color="medals_per_athlete",
    color_continuous_scale=[[0, OLY_BLUE], [0.5, OLY_YELLOW], [1, OLY_RED]],
    hover_data=["gold", "silver", "bronze"],
    title="Medal Distribution — Size = Total Medals, Colour = Medals per Athlete",
)
fig_tree.update_layout(margin=dict(t=50, l=25, r=25, b=25), transition=PLOTLY_TRANSITION)
st.plotly_chart(fig_tree, use_container_width=True)
st.caption(
    "Bright yellow/red tiles are the most efficient. Large but dark blue tiles "
    "sent many athletes and won many medals, but at a lower conversion rate."
)

# ── Full Data Table ────────────────────────────────────────────────────────────
st.header("📋 Full Data")
display_df = df.sort_values("total", ascending=False).copy()
display_df["Population"]             = display_df["population"].apply(fmt_population)
display_df["GDP"]                    = display_df["gdp"].apply(fmt_gdp)
display_df["medals_per_athlete"]     = display_df["medals_per_athlete"].round(3)
display_df["medals_per_million_pop"] = display_df["medals_per_million_pop"].round(2)
display_df["medals_per_billion_gdp"] = display_df["medals_per_billion_gdp"].round(3)

table_cols = [c for c in [
    "display_name", "gold", "silver", "bronze", "total",
    "athlete_count", "medals_per_athlete",
    "medals_per_million_pop", "medals_per_billion_gdp",
    "Population", "GDP", "country_size_category", "gdp_category",
] if c in display_df.columns]

st.dataframe(
    display_df[table_cols].rename(columns={
        "display_name":           "Country",
        "gold":                   "Gold",
        "silver":                 "Silver",
        "bronze":                 "Bronze",
        "total":                  "Total",
        "athlete_count":          "Athletes",
        "medals_per_athlete":     "Medals/Athlete",
        "medals_per_million_pop": "Medals/M Pop",
        "medals_per_billion_gdp": "Medals/$B GDP",
        "country_size_category":  "Size Category",
        "gdp_category":           "GDP Category",
    }),
    use_container_width=True,
    column_config={
        "Gold":           st.column_config.NumberColumn(format="%d 🥇"),
        "Silver":         st.column_config.NumberColumn(format="%d 🥈"),
        "Bronze":         st.column_config.NumberColumn(format="%d 🥉"),
        "Total":          st.column_config.NumberColumn(format="%d"),
        "Athletes":       st.column_config.NumberColumn(format="%d"),
        "Medals/Athlete": st.column_config.ProgressColumn(
            min_value=0, max_value=float(display_df["medals_per_athlete"].max()), format="%.3f"),
        "Medals/M Pop":   st.column_config.ProgressColumn(
            min_value=0, max_value=float(display_df["medals_per_million_pop"].max()), format="%.2f"),
        "Medals/$B GDP":  st.column_config.ProgressColumn(
            min_value=0, max_value=float(display_df["medals_per_billion_gdp"].max()), format="%.3f"),
    },
    hide_index=True,
)
st.info(f"Displaying {len(df)} countries based on your current filters.")

# ── Download ───────────────────────────────────────────────────────────────────
st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=df.to_csv().encode("utf-8"),
    file_name="tokyo_olympics_2021_filtered.csv",
    mime="text/csv",
)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "**Data Sources:** Tokyo 2021 Olympics dataset · World Bank (GDP & Population 2021) · "
    "IMF/UN (Cuba, Venezuela, Taiwan)  \n"
    "**Built with:** Python · Pandas · Plotly · Streamlit · Claude AI"
)
