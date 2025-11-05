import os
import pandas as pd
import streamlit as st
import pydeck as pdk
from pathlib import Path
from io import StringIO

# -----------------------------
# Page config & base style
# -----------------------------
st.set_page_config(
    page_title="서초구 상품권 사용처 지도",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global CSS (glassmorphism + gradient + badges + legend)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;700;800;900&display=swap');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif; }
    .hero {
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
        border-radius: 24px;
        padding: 28px 30px;
        color: white;
        box-shadow: 0 20px 60px rgba(16,24,40,0.25);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }
    .hero:after{
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle at center, rgba(255,255,255,0.35), transparent 60%);
        filter: blur(10px);
        border-radius: 50%;
    }
    .pill {
        display:inline-flex; align-items:center; gap:8px;
        background: rgba(255,255,255,0.18);
        padding: 10px 14px; border-radius: 999px; font-weight: 700;
        backdrop-filter: blur(6px);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.25);
    }
    .stat-card {
        border-radius: 20px; padding: 16px 18px;
        background: rgba(255,255,255,0.6);
        box-shadow: 0 10px 28px rgba(2,6,23,0.08);
        border: 1px solid rgba(2,6,23,0.08);
    }
    .merchant-card {
        border-radius:18px; padding:14px 16px; margin-bottom:10px;
        background: rgba(250, 250, 252, 0.8); border: 1px solid rgba(2,6,23,0.06);
    }
    .kpi { font-size: 32px; font-weight: 800; letter-spacing:-0.5px;}
    .kpi-sub { color:#334155; font-weight:600; }
    .legend-row {
        display:flex; gap: 12px; align-items:center; justify-content:flex-start;
        margin: 8px 0 6px 2px;
    }
    .chip {
        display:inline-flex; align-items:center; gap:8px;
        padding: 8px 12px; border-radius: 999px; font-weight: 800; color: white;
        box-shadow: 0 10px 20px rgba(2,6,23,0.15);
    }
    .chip-blue { background:#0ea5e9; }
    .chip-orange { background:#f97316; }
    .badge-dot {
        width:12px; height:12px; border-radius:50%; display:inline-block; background:white; opacity:.9;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.3);
    }
    .footer-note { color:#475569; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Data Load
# -----------------------------
CANDIDATES = [
    Path("data/merchants_seocho.csv"),
    Path(__file__).parent / "data" / "merchants_seocho.csv",
]
DATA_PATH = None
for p in CANDIDATES:
    if p.exists():
        DATA_PATH = p
        break

if DATA_PATH is None:
    st.error("⚠️ data/merchants_seocho.csv 파일을 찾지 못했습니다.")
    csv_demo = StringIO("""name,type,lat,lon,address,category
CGV 센트럴시티,culture,37.50493,127.00487,서울 서초구 신반포로 176,영화관
GS25 서초역점,tmoney,37.4919,127.0079,서울 서초구 반포대로,편의점
""")
    df = pd.read_csv(csv_demo)
else:
    df = pd.read_csv(DATA_PATH)

CENTER = [37.4831, 127.0327]

# -----------------------------
# Hero Section
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="pill">🗺️ 서초구 · Giftcard Map</div>
      <h1 style="margin:10px 0 0; font-size:42px; font-weight:900; line-height:1.1">
        티머니 · 문화상품권 <br/>가맹점 지도
      </h1>
      <p style="opacity:.95; font-size:16px; margin-top:8px">
        서초구에서 사용할 수 있는 가맹점을 한눈에 확인해보세요 ✨
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Toggle Buttons
# -----------------------------
if "selected" not in st.session_state:
    st.session_state["selected"] = "all"
selected = st.session_state["selected"]

col1, col2, col3 = st.columns([1,1,1])
if col1.button("티머니", type="primary" if selected=="tmoney" else "secondary"):
    st.session_state["selected"] = "tmoney"; st.rerun()
if col2.button("문화상품권", type="primary" if selected=="culture" else "secondary"):
    st.session_state["selected"] = "culture"; st.rerun()
if col3.button("전체 보기", type="primary" if selected=="all" else "secondary"):
    st.session_state["selected"] = "all"; st.rerun()

selected = st.session_state["selected"]
st.caption(f"현재 선택: {'티머니' if selected=='tmoney' else '문화상품권' if selected=='culture' else '전체'}")

# -----------------------------
# Filter Data
# -----------------------------
if selected == "tmoney":
    filtered = df[df["type"] == "tmoney"].copy()
elif selected == "culture":
    filtered = df[df["type"] == "culture"].copy()
else:
    filtered = df.copy()

show_labels = st.checkbox("지도에 라벨 표시", value=False)

# -----------------------------
# KPI Cards
# -----------------------------
k1, k2, k3 = st.columns(3)
with k1: st.markdown(f'<div class="stat-card"><div class="kpi">{len(df)}</div><div class="kpi-sub">총 가맹점</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="stat-card"><div class="kpi">{len(df[df["type"]=="tmoney"])}</div><div class="kpi-sub">티머니</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="stat-card"><div class="kpi">{len(df[df["type"]=="culture"])}</div><div class="kpi-sub">문화상품권</div></div>', unsafe_allow_html=True)

# -----------------------------
# Legend Row (문구 삭제됨)
# -----------------------------
st.markdown(
    """
    <div class="legend-row">
      <span class="chip chip-blue"><span class="badge-dot"></span> 티머니 (파란 점)</span>
      <span class="chip chip-orange"><span class="badge-dot"></span> 문화상품권 (주황 점)</span>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Map (Glow + Dot Style)
# -----------------------------
COLOR_T = [14,165,233]
COLOR_C = [249,115,22]

filtered["color"] = filtered["type"].map({"tmoney": COLOR_T, "culture": COLOR_C})
filtered["abbr"] = filtered["type"].map({"tmoney": "T", "culture": "C"})
filtered["type_kor"] = filtered["type"].map({"tmoney": "티머니", "culture": "문화상품권"})

glow_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_radius=140,
    radius_min_pixels=8,
    radius_max_pixels=80,
    get_fill_color="color",
    opacity=0.18,
)

dot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_radius=65,
    radius_min_pixels=5,
    radius_max_pixels=60,
    get_fill_color="color",
    pickable=True,
    stroked=True,
    get_line_color=[255,255,255],
    line_width_min_pixels=1,
    auto_highlight=True,
)

layers = [glow_layer, dot_layer]

if show_labels:
    layers.append(
        pdk.Layer(
            "TextLayer",
            data=filtered,
            get_position='[lon, lat]',
            get_text="abbr",
            get_color="color",
            get_size=16,
            get_alignment_baseline="'center'",
            get_text_anchor="'middle'",
            billboard=True,
        )
    )

view_state = pdk.ViewState(latitude=37.4831, longitude=127.0327, zoom=12.2, pitch=45, bearing=8)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={"html": "{name}<br/>{type_kor} · {category}<br/>{address}"}
)

st.pydeck_chart(deck, use_container_width=True)

# -----------------------------
# Merchant List
# -----------------------------
st.markdown("---")
left, right = st.columns(2)
for i, r in filtered.iloc[::2].iterrows():
    with left:
        st.markdown(f"""
        <div class="merchant-card">
            <div style="font-size:18px; font-weight:800">{r['name']}</div>
            <div style="margin-top:6px; color:#334155; font-weight:600">{r['category']}</div>
            <div style="margin-top:4px; color:#475569; font-size:14px">{r['address']}</div>
        </div>
        """, unsafe_allow_html=True)

for i, r in filtered.iloc[1::2].iterrows():
    with right:
        st.markdown(f"""
        <div class="merchant-card">
            <div style="font-size:18px; font-weight:800">{r['name']}</div>
            <div style="margin-top:6px; color:#334155; font-weight:600">{r['category']}</div>
            <div style="margin-top:4px; color:#475569; font-size:14px">{r['address']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer-note">※ 실제 운영 전 최신 가맹점으로 검수해주세요.</div>', unsafe_allow_html=True)
