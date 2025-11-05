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
    .chip-gray { background:#0f172a; color:#e2e8f0; }
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
# Robust data loader
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
# Controls — 단일 클릭 즉시 반영
# -----------------------------
if "selected" not in st.session_state:
    st.session_state["selected"] = "all"
selected = st.session_state["selected"]

col1, col2, col3, col4 = st.columns([1,1,1,3])

tmoney_type  = "primary" if selected == "tmoney" else "secondary"
culture_type = "primary" if selected == "culture" else "secondary"
all_type     = "primary" if selected == "all" else "secondary"

with col1:
    if st.button("티머니", key="tmoney_btn", type=tmoney_type, use_container_width=True):
        st.session_state["selected"] = "tmoney"; st.rerun()
with col2:
    if st.button("문화상품권", key="culture_btn", type=culture_type, use_container_width=True):
        st.session_state["selected"] = "culture"; st.rerun()
with col3:
    if st.button("전체 보기", key="all_btn", type=all_type, use_container_width=True):
        st.session_state["selected"] = "all"; st.rerun()

selected = st.session_state["selected"]
st.caption(f"현재 선택: {'티머니' if selected=='tmoney' else '문화상품권' if selected=='culture' else '전체'}")

# -----------------------------
# 필터 + 옵션
# -----------------------------
if selected == "tmoney":
    filtered = df[df["type"] == "tmoney"].copy()
elif selected == "culture":
    filtered = df[df["type"] == "culture"].copy()
else:
    filtered = df.copy()

# 라벨 표시 토글
show_labels = st.checkbox("지도에 라벨(약어) 표시", value=False)

# -----------------------------
# KPIs — 총 가맹점 고정
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
# 지도 상단 큰 레전드(한눈에 파악)
# -----------------------------
st.markdown(
    """
    <div class="legend-row">
      <span class="chip chip-blue"><span class="badge-dot"></span> 티머니 (파란 점)</span>
      <span class="chip chip-orange"><span class="badge-dot"></span> 문화상품권 (주황 점)</span>
      <span class="chip chip-gray">지도 위 점을 호버하면 상세 정보 표시</span>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Map (pydeck) — Glow + Dot 레이어로 더 고급스럽게
# -----------------------------
COLOR_T = [14, 165, 233]    # sky-500
COLOR_C = [249, 115, 22]    # orange-500

def assign_color(row):
    return COLOR_T if row["type"] == "tmoney" else COLOR_C

filtered = filtered.copy()
filtered["color"] = filtered.apply(assign_color, axis=1)
filtered["type_kor"] = filtered["type"].map({"tmoney": "티머니", "culture": "문화상품권"})
filtered["abbr"] = filtered["type"].map({"tmoney": "T", "culture": "C"})

# 툴팁 (상단 색 배지 + 정보)
def tooltip_html():
    return {
        "html": """
        <div style="font-family: Pretendard, sans-serif; min-width:240px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                         background:{badge};box-shadow:0 0 0 2px rgba(255,255,255,.6) inset"></span>
            <div style="font-weight:800; font-size:16px;">{name}</div>
          </div>
          <div style="font-weight:600; opacity:.8; margin-bottom:6px;">{type_kor} • {category}</div>
          <div style="font-size:13px; opacity:.9;">{address}</div>
        </div>
        """,
        "style": { "backgroundColor": "white", "color": "#0f172a" }
    }

# 레이어 구성: Glow(큰 반경, 낮은 불투명) + Dot(작은 반경, 선명)
glow_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_radius=140,
    radius_min_pixels=8,
    radius_max_pixels=80,
    get_fill_color="color",
    pickable=False,
    stroked=False,
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

# 옵션: 라벨(약어) 표시
if show_labels:
    text_layer = pdk.Layer(
        "TextLayer",
        data=filtered,
        get_position='[lon, lat]',
        get_text="abbr",
        get_color="color",
        get_size=16,
        get_alignment_baseline="'center'",
        get_text_anchor="'middle'",
        pickable=False,
        billboard=True,
    )
    layers.append(text_layer)

MAPBOX = st.secrets.get("MAPBOX_API_KEY", os.environ.get("MAPBOX_API_KEY", None))
map_style = "mapbox://styles/mapbox/dark-v11" if MAPBOX else None

view_state = pdk.ViewState(latitude=37.4831, longitude=127.0327, zoom=12.2, pitch=45, bearing=8)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=map_style,
    tooltip=tooltip_html()
)

st.pydeck_chart(deck, use_container_width=True)

# -----------------------------
# 하단 리스트
# -----------------------------
st.markdown("---")
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

st.markdown('<div class="footer-note">※ 운영 전 실제 가맹점으로 최종 검수해 주세요. (CSV: data/merchants_seocho.csv)</div>', unsafe_allow_html=True)

