import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Network Copilot",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 10
if "data_limit" not in st.session_state:
    st.session_state.data_limit = 100

# ─────────────────────────────────────────────
#  CSS — Black & Violet + Animated Star Field
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;600&display=swap');

/* ── Star field canvas sits behind everything ── */
#stars-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
}

/* ── Base ── */
html, body, [class*="css"], .stApp {
    background: #000000 !important;
    color: #E0D7FF !important;
    font-family: 'Inter', sans-serif;
}
.stApp { background: transparent !important; }
.block-container {
    padding: 1.2rem 2rem 2rem 2rem !important;
    max-width: 100% !important;
    position: relative; z-index: 1;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, rgba(60,0,120,0.55) 0%, rgba(20,0,50,0.7) 100%);
    border: 1px solid rgba(150,80,255,0.4);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 0 40px rgba(120,40,255,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero::before {
    content: '';
    position: absolute; top: 0; left: -100%; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #BF5FFF, #7B00FF, #BF5FFF, transparent);
    animation: hero-scan 4s linear infinite;
}
@keyframes hero-scan {
    0%   { left: -100%; }
    100% { left: 100%; }
}
.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.1rem; font-weight: 900;
    color: #FFFFFF;
    letter-spacing: 0.1em;
    margin: 0 0 0.3rem 0;
    text-shadow: 0 0 30px rgba(191,95,255,0.7), 0 0 60px rgba(123,0,255,0.3);
}
.hero-sub {
    color: rgba(191,95,255,0.7);
    font-size: 0.78rem;
    font-weight: 300;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.hero-status {
    position: absolute; top: 1.6rem; right: 2rem;
    display: flex; align-items: center; gap: 0.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
}
.dot-pulse {
    width: 8px; height: 8px; border-radius: 50%;
    animation: dot-blink 1.4s ease-in-out infinite;
}
@keyframes dot-blink {
    0%,100% { opacity:1; box-shadow: 0 0 0 0 currentColor; }
    50%      { opacity:0.6; box-shadow: 0 0 0 5px transparent; }
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.4rem;
}
.kpi-card {
    background: rgba(20,0,45,0.6);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden;
    backdrop-filter: blur(10px);
    transition: transform 0.25s, box-shadow 0.25s;
    cursor: default;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(123,0,255,0.25);
}
.kpi-card::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 12px;
    padding: 1px;
    background: linear-gradient(135deg, var(--accent), transparent 60%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}
.kpi-card.c1 { --accent: #BF5FFF; }
.kpi-card.c2 { --accent: #7B00FF; }
.kpi-card.c3 { --accent: #9D4EDD; }
.kpi-card.c4 { --accent: #FF4DFF; }
.kpi-label {
    font-size: 0.65rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: rgba(191,95,255,0.6);
    margin-bottom: 0.5rem;
    font-family: 'Share Tech Mono', monospace;
}
.kpi-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.9rem; font-weight: 700;
    line-height: 1; margin-bottom: 0.25rem;
    color: #FFFFFF;
    text-shadow: 0 0 20px var(--accent);
}
.kpi-unit {
    font-size: 0.7rem; color: rgba(224,215,255,0.4);
    font-family: 'Share Tech Mono', monospace;
}
/* shimmer sweep on kpi cards */
.kpi-card::after {
    content: '';
    position: absolute; top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(191,95,255,0.06), transparent);
    animation: shimmer 4s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
}
.kpi-card.c1 { --delay: 0s; }
.kpi-card.c2 { --delay: 0.8s; }
.kpi-card.c3 { --delay: 1.6s; }
.kpi-card.c4 { --delay: 2.4s; }
@keyframes shimmer { 0%,100%{left:-100%} 50%{left:100%} }

/* ── Section headers ── */
.sec-head {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.22em;
    text-transform: uppercase; color: #BF5FFF;
    border-bottom: 1px solid rgba(123,0,255,0.3);
    padding-bottom: 0.45rem; margin: 1.4rem 0 1rem 0;
}

/* ── Alert rows ── */
.alert-row {
    display: flex; align-items: center; gap: 1rem;
    background: rgba(255,77,255,0.04);
    border: 1px solid rgba(255,77,255,0.18);
    border-left: 3px solid #FF4DFF;
    border-radius: 7px;
    padding: 0.65rem 1rem; margin-bottom: 0.45rem;
    animation: slide-in 0.35s ease;
}
@keyframes slide-in { from{opacity:0;transform:translateX(-10px)} to{opacity:1;transform:none} }
.a-host   { font-family: 'Share Tech Mono', monospace; color: #FF4DFF; font-size: 0.82rem; min-width: 110px; }
.a-reason { color: #E0D7FF; font-size: 0.82rem; flex: 1; }
.a-time   { color: rgba(191,95,255,0.5); font-size: 0.72rem; font-family: 'Share Tech Mono', monospace; }

/* ── Host table ── */
.htable { width:100%; border-collapse:collapse; }
.htable th {
    font-family:'Share Tech Mono',monospace; font-size:0.65rem;
    letter-spacing:0.15em; text-transform:uppercase;
    color:rgba(191,95,255,0.55); border-bottom:1px solid rgba(123,0,255,0.3);
    padding:0.5rem 0.7rem; text-align:left;
}
.htable td {
    font-size:0.82rem; color:#E0D7FF;
    border-bottom:1px solid rgba(123,0,255,0.1);
    padding:0.55rem 0.7rem;
}
.htable tr:hover td { background:rgba(123,0,255,0.06); }
.badge-ok   { background:rgba(0,255,136,0.08); color:#00FF88; border:1px solid rgba(0,255,136,0.25); border-radius:4px; padding:1px 8px; font-size:0.65rem; font-family:'Share Tech Mono',monospace; }
.badge-warn { background:rgba(255,77,255,0.08); color:#FF4DFF; border:1px solid rgba(255,77,255,0.25); border-radius:4px; padding:1px 8px; font-size:0.65rem; font-family:'Share Tech Mono',monospace; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(10,0,25,0.95) !important;
    border-right: 1px solid rgba(123,0,255,0.25) !important;
}
section[data-testid="stSidebar"] * { color: #E0D7FF !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(123,0,255,0.3); gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    color: rgba(191,95,255,0.5) !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 0.6rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    color: #BF5FFF !important;
    border-bottom: 2px solid #BF5FFF !important;
    background: transparent !important;
}

/* ── Refresh progress ── */
.prog-wrap { background:rgba(20,0,45,0.6); border:1px solid rgba(123,0,255,0.25); border-radius:8px; padding:0.7rem 1rem; margin-bottom:1rem; backdrop-filter:blur(8px); }
.prog-label { font-size:0.65rem; color:rgba(191,95,255,0.55); letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.35rem; font-family:'Share Tech Mono',monospace; }
.prog-track { background:rgba(123,0,255,0.15); border-radius:3px; height:3px; }
.prog-fill  { background:linear-gradient(90deg,#7B00FF,#BF5FFF,#FF4DFF); border-radius:3px; height:3px; transition:width 1s linear; }

/* ── No-data box ── */
.no-data {
    background:rgba(60,0,120,0.2); border:1px solid rgba(191,95,255,0.25);
    border-radius:12px; padding:3rem; text-align:center; margin-top:2rem;
}

/* ── Footer ── */
.foot {
    text-align:center; padding:1.2rem 0 0.4rem;
    font-family:'Share Tech Mono',monospace; font-size:0.62rem;
    color:rgba(123,0,255,0.4); letter-spacing:0.15em; text-transform:uppercase;
    border-top:1px solid rgba(123,0,255,0.2); margin-top:2rem;
}
</style>

<!-- ── Animated Star Field ── -->
<canvas id="stars-canvas"></canvas>
<script>
(function(){
    const canvas = document.getElementById('stars-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H, stars = [], nebulas = [];

    function resize(){
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function initStars(){
        stars = [];
        for(let i=0; i<220; i++){
            stars.push({
                x: Math.random()*W, y: Math.random()*H,
                r: Math.random()*1.4+0.2,
                speed: Math.random()*0.12+0.02,
                opacity: Math.random()*0.7+0.2,
                twinkleSpeed: Math.random()*0.02+0.005,
                twinkleDir: Math.random()<0.5?1:-1,
                color: Math.random()<0.15 ? '#BF5FFF' : (Math.random()<0.08 ? '#FF4DFF' : '#FFFFFF')
            });
        }
        nebulas = [];
        for(let i=0; i<4; i++){
            nebulas.push({
                x: Math.random()*W, y: Math.random()*H,
                rx: Math.random()*200+100, ry: Math.random()*120+60,
                hue: Math.random()<0.5 ? '123,0,255' : '191,95,255',
                opacity: Math.random()*0.06+0.02
            });
        }
    }

    function draw(){
        ctx.clearRect(0,0,W,H);

        // nebula blobs
        nebulas.forEach(n=>{
            const g = ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,Math.max(n.rx,n.ry));
            g.addColorStop(0,   `rgba(${n.hue},${n.opacity})`);
            g.addColorStop(0.5, `rgba(${n.hue},${n.opacity*0.4})`);
            g.addColorStop(1,   `rgba(${n.hue},0)`);
            ctx.save();
            ctx.scale(n.rx/Math.max(n.rx,n.ry), n.ry/Math.max(n.rx,n.ry));
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(n.x*(Math.max(n.rx,n.ry)/n.rx), n.y*(Math.max(n.rx,n.ry)/n.ry), Math.max(n.rx,n.ry), 0, Math.PI*2);
            ctx.fill();
            ctx.restore();
        });

        // stars
        stars.forEach(s=>{
            s.opacity += s.twinkleSpeed * s.twinkleDir;
            if(s.opacity >= 0.95 || s.opacity <= 0.1) s.twinkleDir *= -1;
            s.y += s.speed;
            if(s.y > H){ s.y=0; s.x=Math.random()*W; }

            ctx.save();
            ctx.globalAlpha = s.opacity;
            ctx.fillStyle = s.color;
            if(s.r > 1.0){
                // glow for bigger stars
                const g = ctx.createRadialGradient(s.x,s.y,0,s.x,s.y,s.r*3);
                g.addColorStop(0, s.color);
                g.addColorStop(1, 'transparent');
                ctx.fillStyle = g;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r*3, 0, Math.PI*2);
                ctx.fill();
            }
            ctx.fillStyle = s.color;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
            ctx.fill();
            ctx.restore();
        });

        requestAnimationFrame(draw);
    }

    resize();
    initStars();
    draw();
    window.addEventListener('resize', ()=>{ resize(); initStars(); });
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  AUTO-REFRESH (streamlit-autorefresh)
#  Add to dashboard/requirements.txt:
#    streamlit-autorefresh
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:Share Tech Mono,monospace;color:#BF5FFF;font-size:0.72rem;
                letter-spacing:0.18em;text-transform:uppercase;
                border-bottom:1px solid rgba(123,0,255,0.3);padding-bottom:0.7rem;margin-bottom:1rem;'>
        ⚙ Controls
    </div>""", unsafe_allow_html=True)

    refresh_interval = st.slider("Auto-refresh (s)", 5, 60, 10, 5)
    data_limit       = st.slider("Data points",     50, 500, 100, 50)

    st.markdown("<br>", unsafe_allow_html=True)
    manual_refresh = st.button("↺  Refresh Now", use_container_width=True)
    if manual_refresh:
        st.cache_data.clear()
        st.rerun()

    # progress bar (visual only, driven by autorefresh timer)
    now_s = int(time.time()) % refresh_interval
    pct   = int((now_s / refresh_interval) * 100)
    st.markdown(f"""
    <div class='prog-wrap'>
        <div class='prog-label'>Refresh cycle</div>
        <div class='prog-track'>
            <div class='prog-fill' style='width:{pct}%;'></div>
        </div>
    </div>
    <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;
                color:rgba(191,95,255,0.4);text-align:center;'>
        {datetime.now().strftime('%H:%M:%S')}
    </div>""", unsafe_allow_html=True)

# ── REAL auto-refresh via JS timer ──
if HAS_AUTOREFRESH:
    st_autorefresh(interval=refresh_interval * 1000, key="autorefresh")
else:
    # fallback: warn once
    st.sidebar.warning("pip install streamlit-autorefresh for auto-refresh")

# ─────────────────────────────────────────────
#  DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=4)
def fetch_metrics(limit):
    try:
        r = requests.get(f"{API_BASE_URL}/metrics/latest", params={"limit": limit}, timeout=3)
        return r.json()["metrics"] if r.status_code == 200 else []
    except Exception:
        return []

@st.cache_data(ttl=4)
def fetch_alerts():
    try:
        r = requests.get(f"{API_BASE_URL}/alerts", timeout=3)
        return r.json()["alerts"] if r.status_code == 200 else []
    except Exception:
        return []

@st.cache_data(ttl=30)
def fetch_hosts():
    try:
        r = requests.get(f"{API_BASE_URL}/hosts", timeout=3)
        return r.json()["hosts"] if r.status_code == 200 else []
    except Exception:
        return []

metrics_data = fetch_metrics(data_limit)
alerts_data  = fetch_alerts()
hosts_data   = fetch_hosts()

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
api_ok = len(metrics_data) > 0
sc, st_ = ("#00FF88", "ONLINE") if api_ok else ("#FF4DFF", "NO SIGNAL")

st.markdown(f"""
<div class='hero'>
  <div class='hero-status'>
    <div class='dot-pulse' style='background:{sc};color:{sc};'></div>
    <span style='color:{sc};'>{st_}</span>
  </div>
  <div class='hero-title'>🛸 AI NETWORK COPILOT</div>
  <div class='hero-sub'>Real-time supervision &amp; anomaly detection · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NO DATA STATE
# ─────────────────────────────────────────────
if not metrics_data:
    st.markdown("""
    <div class='no-data'>
        <div style='font-family:Orbitron,sans-serif;color:#FF4DFF;font-size:1.1rem;margin-bottom:0.6rem;'>
            ✕ NO DATA RECEIVED
        </div>
        <div style='color:rgba(191,95,255,0.6);font-size:0.82rem;'>
            Make sure the API is running on
            <code style='color:#BF5FFF;'>http://localhost:8000</code>
            and <code style='color:#BF5FFF;'>simulator_v2.py</code> is generating data.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df         = pd.DataFrame(metrics_data)
df["ts"]   = pd.to_datetime(df["ts"])
anom_df    = df[df["is_anomaly"] == True]

avg_lat    = df["latency"].mean()
avg_traf   = df["traffic"].mean()
avg_err    = df["error_rate"].mean()
anom_count = int(df["is_anomaly"].sum())
anom_pct   = (anom_count / len(df)) * 100

# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='kpi-grid'>
  <div class='kpi-card c1'>
    <div class='kpi-label'>Avg Latency</div>
    <div class='kpi-value'>{avg_lat:.1f}</div>
    <div class='kpi-unit'>milliseconds</div>
  </div>
  <div class='kpi-card c2'>
    <div class='kpi-label'>Avg Traffic</div>
    <div class='kpi-value'>{avg_traf:.1f}</div>
    <div class='kpi-unit'>Mbps</div>
  </div>
  <div class='kpi-card c3'>
    <div class='kpi-label'>Avg Error Rate</div>
    <div class='kpi-value'>{avg_err:.2f}</div>
    <div class='kpi-unit'>percent</div>
  </div>
  <div class='kpi-card c4'>
    <div class='kpi-label'>Anomalies</div>
    <div class='kpi-value'>{anom_count}</div>
    <div class='kpi-unit'>{anom_pct:.1f}% of {len(df)} samples</div>
  </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY SHARED THEME
#  NOTE: No xaxis/yaxis here — added per-chart
#        to avoid the "multiple values" TypeError
# ─────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,0,25,0.5)",
    font=dict(family="Share Tech Mono, monospace", color="rgba(191,95,255,0.6)", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(123,0,255,0.3)", borderwidth=1,
                font=dict(color="#E0D7FF")),
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(20,0,45,0.9)", bordercolor="#BF5FFF",
                    font=dict(family="Share Tech Mono", color="#E0D7FF"))
)

GRID_X = dict(gridcolor="rgba(123,0,255,0.15)", showgrid=True, zeroline=False, color="rgba(191,95,255,0.4)")
GRID_Y = dict(gridcolor="rgba(123,0,255,0.15)", showgrid=True, zeroline=False, color="rgba(191,95,255,0.4)")

HOST_COLORS = {"R1": "#BF5FFF", "SW1": "#7B00FF", "WEB_SERVER": "#FF4DFF"}

def styled_line(metric, title, unit):
    fig = go.Figure()
    for host in df["host"].unique():
        hdf = df[df["host"] == host]
        fig.add_trace(go.Scatter(
            x=hdf["ts"], y=hdf[metric], mode="lines", name=host,
            line=dict(color=HOST_COLORS.get(host, "#BF5FFF"), width=1.8),
            fill="tozeroy",
            fillcolor=HOST_COLORS.get(host, "#BF5FFF").replace("#", "rgba(") + ",0.04)".replace("rgba(", "rgba(")
                if False else "rgba(0,0,0,0)",
            hovertemplate=f"<b>{host}</b><br>%{{y:.2f}} {unit}<extra></extra>"
        ))
    if not anom_df.empty:
        fig.add_trace(go.Scatter(
            x=anom_df["ts"], y=anom_df[metric], mode="markers", name="Anomaly",
            marker=dict(color="#FF4DFF", size=9, symbol="x",
                        line=dict(width=2, color="#FF4DFF")),
            hovertemplate="<b>⚠ Anomaly</b><br>%{y:.2f} " + unit + "<extra></extra>"
        ))
    fig.update_layout(
        **BASE_LAYOUT,
        xaxis=GRID_X,
        yaxis=GRID_Y,
        title=dict(text=title, font=dict(family="Orbitron", color="#BF5FFF", size=12)),
        height=280
    )
    return fig

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["⬛  Overview", "⚠  Alerts", "📈  Charts"])

# ── TAB 1 ─────────────────────────────────────
with tab1:
    cl, cr = st.columns([1.1, 0.9], gap="large")

    with cl:
        st.markdown("<div class='sec-head'>// Host Status</div>", unsafe_allow_html=True)
        hs = df.groupby("host").agg(
            latency=("latency","mean"), error_rate=("error_rate","mean"),
            traffic=("traffic","mean"), anomalies=("is_anomaly","sum")
        ).round(2).reset_index()

        rows = ""
        for _, r in hs.iterrows():
            badge = f"<span class='badge-warn'>{int(r.anomalies)} alerts</span>" \
                    if r.anomalies > 0 else "<span class='badge-ok'>OK</span>"
            rows += f"""<tr>
                <td style='font-family:Share Tech Mono,monospace;color:#BF5FFF;'>{r.host}</td>
                <td>{r.latency:.1f} ms</td>
                <td>{r.error_rate:.2f}%</td>
                <td>{r.traffic:.1f} Mbps</td>
                <td>{badge}</td>
            </tr>"""
        st.markdown(f"""
        <table class='htable'>
          <thead><tr><th>Host</th><th>Latency</th><th>Errors</th><th>Traffic</th><th>Status</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)

    with cr:
        st.markdown("<div class='sec-head'>// Anomaly Distribution</div>", unsafe_allow_html=True)
        if anom_count > 0:
            ph = df.groupby("host")["is_anomaly"].sum().reset_index()
            ph = ph[ph["is_anomaly"] > 0]
            fig_pie = go.Figure(go.Pie(
                labels=ph["host"], values=ph["is_anomaly"], hole=0.6,
                marker=dict(colors=["#BF5FFF","#7B00FF","#FF4DFF"],
                            line=dict(color="#000000", width=2)),
                textfont=dict(family="Share Tech Mono", color="#E0D7FF", size=11),
            ))
            fig_pie.update_layout(
                **BASE_LAYOUT, height=260,
                xaxis=GRID_X, yaxis=GRID_Y,
                annotations=[dict(
                    text=f"<b>{anom_count}</b>",
                    font=dict(size=22, color="#FF4DFF", family="Orbitron"),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:3rem 0;color:#00FF88;
                        font-family:Share Tech Mono,monospace;font-size:0.85rem;
                        border:1px solid rgba(0,255,136,0.15);border-radius:10px;
                        background:rgba(0,255,136,0.02);'>
                ✓ ALL SYSTEMS NORMAL
            </div>""", unsafe_allow_html=True)

# ── TAB 2 ─────────────────────────────────────
with tab2:
    st.markdown("<div class='sec-head'>// Active Alerts</div>", unsafe_allow_html=True)
    if alerts_data:
        adf = pd.DataFrame(alerts_data)
        adf["ts"] = pd.to_datetime(adf["ts"])
        for _, r in adf.head(30).iterrows():
            st.markdown(f"""
            <div class='alert-row'>
                <span class='a-host'>⚠ {r.host}</span>
                <span class='a-reason'>{r.reason}</span>
                <span class='a-time'>{r.ts.strftime('%H:%M:%S')}</span>
            </div>""", unsafe_allow_html=True)
        if len(adf) > 30:
            st.markdown(f"<div style='color:rgba(191,95,255,0.4);font-size:0.72rem;text-align:center;margin-top:0.5rem;'>"
                        f"Showing 30 of {len(adf)} alerts</div>", unsafe_allow_html=True)

        st.markdown("<div class='sec-head' style='margin-top:1.5rem;'>// Alert Reasons</div>", unsafe_allow_html=True)
        rc = adf["reason"].value_counts().reset_index()
        rc.columns = ["reason","count"]
        fig_bar = go.Figure(go.Bar(
            x=rc["count"], y=rc["reason"], orientation="h",
            marker=dict(
                color=rc["count"],
                colorscale=[[0,"#3C0078"],[0.5,"#7B00FF"],[1,"#FF4DFF"]],
                line=dict(color="rgba(0,0,0,0)")
            ),
            text=rc["count"], textposition="outside",
            textfont=dict(color="#E0D7FF", family="Share Tech Mono"),
        ))
        # NOTE: xaxis/yaxis passed directly here, NOT via **BASE_LAYOUT to avoid conflict
        fig_bar.update_layout(
            **BASE_LAYOUT,
            height=200,
            xaxis=dict(showgrid=False, visible=False,
                       color="rgba(191,95,255,0.4)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)",
                       color="rgba(191,95,255,0.4)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:3rem;color:#00FF88;
                    font-family:Share Tech Mono,monospace;
                    border:1px solid rgba(0,255,136,0.15);border-radius:10px;
                    background:rgba(0,255,136,0.02);'>
            ✓ ALL SYSTEMS NORMAL — NO ACTIVE ALERTS
        </div>""", unsafe_allow_html=True)

# ── TAB 3 ─────────────────────────────────────
with tab3:
    st.markdown("<div class='sec-head'>// Latency &amp; Error Rate</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(styled_line("latency", "LATENCY", "ms"), use_container_width=True)
    with c2:
        st.plotly_chart(styled_line("error_rate", "ERROR RATE", "%"), use_container_width=True)

    st.markdown("<div class='sec-head'>// Network Traffic</div>", unsafe_allow_html=True)
    st.plotly_chart(styled_line("traffic", "TRAFFIC", "Mbps"), use_container_width=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='foot'>
  AI Network Copilot · Stage Project · {datetime.now().year}
  &nbsp;·&nbsp; {len(df)} samples · Hosts: {' · '.join(hosts_data)}
</div>""", unsafe_allow_html=True)