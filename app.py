import os
import json
import time
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

# Global CSS (glassmorphism + gradient)
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
    .legend {
        display:flex; gap: 10px; align-items:center; margin-top:6px;
    }
    .legend .dot { width:14px; height:14px; border-radius:50%; display:inline-block; }
    .footer-note { color:#475569; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Robust data loader (파일이 없을 때도 앱이 죽지 않도록)
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
    st.error("⚠️ 데이터 파일(data/merchants_seocho.csv)을 찾을 수 없습니다.")
    st.info("레포 루트에 data/merchants_seocho.csv 를 업로드한 뒤 앱을 다시 실행/새로고침하세요.")
    csv_demo = StringIO("""name,type,lat,lon,address,category
CGV 센트럴시티,culture,37.50493,127.00487,서울 서초구 신반포로 176 센트럴시티 내,영화관
GS25 서초역점,tmoney,37.4919,127.0079,서울 서초구 반포대로 서초역 인근,편의점
교대 알라딘 중고서점(서초점),culture,37.4936,127.0144,서울 서초구 서초중앙로 96,서점
""")
    df = pd.read_csv(csv_demo)
else:
    df = pd.read_csv(DATA_PATH)

# Center of Seocho-gu
CENTER = [37.4831, 127.0327]

# -----------------------------
# Header / Hero
# -----------------------------
with st.container():
    st.markdown(
        """
        <div class="hero">
          <div class="pill">🗺️ 서초구 · Giftcard Map</div>
          <h1 style="margin:10px 0 0; font-size:42px; font-weight:900; line-height:1.1">
            티머니 · 문화상품권 <br/>사용처를 한눈에!
          </h1>
          <p style="opacity:.95; font-size:16px; margin-top:8px">
            원하는 상품권 버튼을 누르면 서초구 지도 위에 사용 가능 가맹점이 반짝✨ 나타나요.
            마우스를 올리면 점포 이름과 주소도 보여드릴게요.
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Controls (Buttons)  ✅수정: 선택된 버튼만 하이라이트
# -----------------------------
if "selected" not in st.session_state:
    st.session_state["selected"] = "all"
selected = st.session_state["selected"]

col1, col2, col3, col4 = st.columns([1,1,1,3])
with col1:
    tmoney_clicked = st.button(
        "티머니",
        use_container_width=True,
        type="primary" if selected == "tmoney" else "secondary",
    )
with col2:
    culture_clicked = st.button(
        "문화상품권",
        use_container_width=True,
        type="primary" if selected == "culture" else "secondary",
    )
with col3:
    show_all = st.button(
        "전체 보기",
        use_container_width=True,
        type="primary" if selected == "all" else "secondary",
    )

if tmoney_clicked:
    st.session_state["selected"] = "tmoney"
elif culture_clicked:
    st.session_state["selected"] = "culture"
elif show_all:
    st.session_state["selected"] = "all"

selected = st.session_state["selected"]

# -----------------------------
# Filtering
# -----------------------------
if selected == "tmoney":
    filtered = df[df["type"] == "tmoney"].copy()
elif selected == "culture":
    filtered = df[df["type"] == "culture"].copy()
else:
    filtered = df.copy()

# -----------------------------
# KPIs  ✅수정: 총 가맹점은 고정(필터 영향 없음)
# -----------------------------
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        '<div class="stat-card"><div class="kpi">{}</div><div class="kpi-sub">총 가맹점</div></div>'.format(len(df)),
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        '<div class="stat-card"><div class="kpi">{}</div><div class="kpi-sub">티머니</div></div>'.format(len(df[df["type"]=="tmoney"])),
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        '<div class="stat-card"><div class="kpi">{}</div><div class="kpi-sub">문화상품권</div></div>'.format(len(df[df["type"]=="culture"])),
        unsafe_allow_html=True
    )

# -----------------------------
# Map (pydeck)
# -----------------------------
# Colors
COLOR_T = [14, 165, 233]    # sky-500
COLOR_C = [249, 115, 22]    # orange-500

def assign_color(row):
    return COLOR_T if row["type"] == "tmoney" else COLOR_C

filtered = filtered.copy()
filtered["color"] = filtered.apply(assign_color, axis=1)

# Tooltip HTML
tooltip_html = {
    "html": """
    <div style="font-family: Pretendard, sans-serif; min-width:220px">
        <div style="font-weight:800; font-size:16px; margin-bottom:4px;">{name}</div>
        <div style="font-weight:600; opacity:.75; margin-bottom:6px;">{type_kor} • {category}</div>
        <div style="font-size:13px; opacity:.9;">{address}</div>
    </div>
    """,
    "style": { "backgroundColor": "white", "color": "#0f172a" }
}

# Mapbox token (optional for best style)
MAPBOX = st.secrets.get("MAPBOX_API_KEY", os.environ.get("MAPBOX_API_KEY", None))
map_style = "mapbox://styles/mapbox/dark-v11" if MAPBOX else None

# Create layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered.assign(type_kor=filtered["type"].map({"tmoney":"티머니", "culture":"문화상품권"})),
    get_position='[lon, lat]',
    get_radius=65,
    radius_min_pixels=5,
    radius_max_pixels=60,
    get_fill_color="color",
    pickable=True,
    stroked=True,
    get_line_color=[255,255,255],
    line_width_min_pixels=1,
    auto_highlight=True
)

view_state = pdk.ViewState(latitude=CENTER[0], longitude=CENTER[1], zoom=12.2, pitch=45, bearing=8)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=map_style,
    tooltip=tooltip_html,
)

st.pydeck_chart(r, use_container_width=True)

# Legend
st.markdown(
    """
    <div class="legend">
      <span class="dot" style="background:#0ea5e9"></span> 티머니
      <span class="dot" style="background:#f97316; margin-left:16px;"></span> 문화상품권
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# Merchant list
# -----------------------------
list_left, list_right = st.columns([1,1])
left_df = filtered.iloc[::2]
right_df = filtered.iloc[1::2]

def render_card(row):
    st.markdown(f"""
    <div class="merchant-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:18px; font-weight:800">{row['name']}</div>
        <div class="pill" style="background:{'#0ea5e9' if row['type']=='tmoney' else '#f97316'}; color:white;">
          {'티머니' if row['type']=='tmoney' else '문화상품권'}
        </div>
      </div>
      <div style="margin-top:6px; color:#334155; font-weight:600">{row['category']}</div>
      <div style="margin-top:4px; color:#475569; font-size:14px">{row['address']}</div>
    </div>
    """, unsafe_allow_html=True)

with list_left:
    for _, rrow in left_df.iterrows():
        render_card(rrow)
with list_right:
    for _, rrow in right_df.iterrows():
        render_card(rrow)

st.markdown('<div class="footer-note">※ 현재 데이터는 예시가 포함될 수 있습니다. 운영 전 실제 가맹점으로 교체/검증해 주세요.</div>', unsafe_allow_html=True)

