import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pathlib import Path
import base64
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------
# 0. 경로 & 아이콘 세팅 (톱니바퀴 아이콘)
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
GEAR_PATH = BASE_DIR / "theme" / "gear.png"

with open(GEAR_PATH, "rb") as f:
    GEAR_ICON_B64 = base64.b64encode(f.read()).decode()

# ---------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------
st.set_page_config(
    page_title="공공화장실 데이터맵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------
# 2. Session State
# ---------------------------------------------------
ss = st.session_state

ss.setdefault("selected_toilet", None)
ss.setdefault("show_disabled", False)          # 장애인 화장실 색 구분 토글
ss.setdefault("map_center_loc", "남구 대연동") # 기본 지도 위치
ss.setdefault("auto_detect", False)            # 현재 위치 자동 감지 토글
ss.setdefault("last_clicked_latlng", None)
ss.setdefault("last_clicked_tooltip", None)

ss.setdefault("show_disabled_tmp", ss.show_disabled)
ss.setdefault("auto_detect_tmp", ss.auto_detect)
ss.setdefault("map_center_loc_tmp", ss.map_center_loc)

ss.setdefault("user_location", None)      # (lat, lng)
ss.setdefault("user_location_tmp", None)  # (lat, lng)

# ---------------------------------------------------
# 3. 메인 스타일 + 플로팅 설정 버튼
# ---------------------------------------------------
st.markdown(f"""
<style>
.stApp {{ margin: 0 !important; padding: 0 !important; overflow: hidden !important; }}
.block-container {{ padding: 0 !important; max-width: none !important; }}
header[data-testid="stHeader"] {{
    background: transparent !important;
    z-index: 999;
    pointer-events: none;
}}
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] [data-testid="stToolbar"] {{
    pointer-events: auto; color: #111827;
}}
iframe[title="streamlit_folium.st_folium"] {{
    position: fixed !important; top: 0; left: 0;
    width: 100vw; height: 100vh; z-index: 0;
}}

div[data-testid="stVerticalBlock"]:has(#floating-btn-marker) {{
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 1000;
    width: auto;
}}

div[data-testid="stVerticalBlock"]:has(#floating-btn-marker) button {{
    width: 70px;
    height: 70px;
    padding: 0;
    margin: 0;
    background: transparent;
    border: none;
    box-shadow: none;
    border-radius: 0;
    color: transparent;
    font-size: 0;
    background-image: url("data:image/png;base64,{GEAR_ICON_B64}");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    cursor: pointer;
}}
div[data-testid="stVerticalBlock"]:has(#floating-btn-marker) button:hover {{
    transform: scale(1.05);
    background-color: transparent;
}}

div[data-testid="stDialog"] > div > div {{ border-radius: 24px; padding: 32px; }}

.card-title{{ font-size:22px !important; font-weight:800 !important; margin-bottom:12px !important; color:#111827; }}

.badge-row{{ display:flex; gap:8px; margin-bottom:20px; }}

.badge{{ 
    background:#F3F4F6; 
    color:#4F46E5; 
    padding:6px 12px; 
    border-radius:99px; 
    font-size:12px; 
    font-weight:600; 
}}
.badge.gray{{ background:#F3F4F6; color:#4B5563; }}
.grid-2{{ display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px; }}
.info-label{{ font-size:12px; color:#6B7280; font-weight:500; margin-bottom: 6px;}}
.info-value{{ background:#F9FAFB; padding:10px 12px; border-radius:8px; font-size:14px; color:#111827; border:1px solid #E5E7EB; font-weight:500; }}

.detail-section-title {{ 
    margin-top: 24px; 
    margin-bottom: 8px; 
    font-size: 14px; 
    font-weight: 700; 
    color: #111827; 
}}

/* 테이블 전체 박스 */
.detail-table {{
    width:100%; 
    font-size:13px; 
    border-collapse: collapse; 
    border: 1px solid #E5E7EB;  
    border-radius: 8px; 
    overflow: hidden; 
}}

/* 헤더 셀 */
.detail-table th {{
    text-align:left; 
    color:#4B5563; 
    padding:10px 12px; 
    background:#F8FAFC; 
    font-weight: 600; 
    border: 1px solid #E5E7EB; 
}}

/* 바디 셀 */
.detail-table td {{
    padding:10px 12px; 
    color:#111827; 
    border: 1px solid #E5E7EB;  
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 4. 데이터 로드
# ---------------------------------------------------
@st.cache_data
def load_toilets():
    try:
        df = pd.read_csv("data/processed/toilets/toilets_namgu.normalized.csv")

        need = [
            "toilet_id", "name", "addr",
            "lat", "lng",
            "district", "dong",
            "accessible", "gender_sep",
            "open_time",
            "male_wc", "female_wc",
            "male_wc_disabled", "female_wc_disabled",
        ]
        for c in need:
            if c not in df.columns:
                df[c] = np.nan

        df["accessible"] = pd.to_numeric(df["accessible"], errors="coerce").fillna(0).astype(int)
        for c in ["male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
        df = df.dropna(subset=["lat", "lng"])

        return df

    except Exception as e:
        st.error(f"화장실 데이터를 읽는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

@st.cache_data
def load_loc_map():
    """population_namgu.normalized.csv 에서 동 중심 좌표 로드"""
    try:
        df = pd.read_csv("data/processed/population/population_namgu.normalized.csv")

        # 필요한 컬럼 존재 확인
        for col in ["dong", "center_lat", "center_lng"]:
            if col not in df.columns:
                raise ValueError(f"필수 컬럼이 없습니다: {col}")

        # 공백 제거 + 숫자 형 변환
        df["dong"] = df["dong"].astype(str).str.strip()
        df["center_lat"] = pd.to_numeric(df["center_lat"], errors="coerce")
        df["center_lng"] = pd.to_numeric(df["center_lng"], errors="coerce")

        df = df.dropna(subset=["dong", "center_lat", "center_lng"])

        # "감만동" → (lat, lng) 형태 딕셔너리
        loc_map = {
            row["dong"]: (float(row["center_lat"]), float(row["center_lng"]))
            for _, row in df.iterrows()
        }
        return loc_map

    except Exception as e:
        st.error(f"기본 지도 위치 데이터를 읽는 중 오류가 발생했습니다: {e}")
        # 최소 fallback
        return {"대연동": (35.1370, 129.0920)}

toilets = load_toilets()
LOC_MAP = load_loc_map()

# 만약 기본값이 LOC_MAP에 없으면 첫 번째 키로 교체
if ss.map_center_loc not in LOC_MAP:
    ss.map_center_loc = list(LOC_MAP.keys())[0]
if ss.map_center_loc_tmp not in LOC_MAP:
    ss.map_center_loc_tmp = ss.map_center_loc

# ======================
# 5. 위치/줌 계산
# ======================
OFFSET_LAT = -0.02
OFFSET_LNG =  0.01
DEFAULT_ZOOM = 14.8

def get_center_and_zoom():
    if ss.auto_detect and ss.user_location is not None:
        lat, lng = ss.user_location
        center = [lat + OFFSET_LAT, lng + OFFSET_LNG]
        zoom = DEFAULT_ZOOM
    else:
        base_lat, base_lng = LOC_MAP.get(
            ss.map_center_loc,
            list(LOC_MAP.values())[0]
        )
        center = [base_lat + OFFSET_LAT, base_lng + OFFSET_LNG]
        zoom = DEFAULT_ZOOM

    return center, zoom

# ======================
# 6. 설정 모달
# ======================
@st.dialog(" ", width="large")
def open_settings_modal():
    st.markdown("""
    <style>
        div[data-testid="stDialog"] {
            position: fixed !important;
            inset: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: transparent !important;
            pointer-events: none;
        }
        div[data-testid="stDialog"] > div {
            pointer-events: auto;
        }

        div[data-testid="stDialog"] > div > div {
            background-color: #FAFAFB;
            padding: 30px;
        }

        div[data-testid="stDialog"] h1 {
            font-size: 24px;
            font-weight: 800;
            color: #111827;
            margin-top: -45px !important;
            padding-top: 0 !important;
            margin-bottom: 25px !important;
        }

        div.stMainBlockContainer { padding-top: 0 !important; }

        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 12px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin: 0 0 12px 0;
            width: 100%;
            display: flex !important;
            align-items: center !important;
            height: 60px !important;
            gap: 0 !important;
        }

        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] > div,
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stColumn"],
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stVerticalBlock"],
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stElementContainer"],
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stMarkdown"],
        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stMarkdownContainer"] {
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
        }

        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
        }

        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"]
            [data-testid="stMarkdownContainer"] p {
            font-size: 16px;
            font-weight: 700;
            color:#374151;
            margin: 0 !important;
            padding-top: 2px !important;
            line-height: 1.2;
        }

        div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"]
            [data-testid="stColumn"]:nth-of-type(2) {
            justify-content: flex-end !important;
        }

        div[data-testid="stDialog"] div[data-testid="stToggle"],
        div[data-testid="stDialog"] div[data-testid="stSelectbox"] {
            width: 150px !important;
            min-width: 150px !important;
            max-width: 150px !important;
        }

        div[data-testid="stDialog"] div[data-testid="stToggle"] {
            justify-content: flex-end;
            padding-right: 0px;
        }

        div[data-testid="stDialog"] label[data-baseweb="checkbox"]:has(
            input[aria-checked="true"]
        ) > div {
            background-color: #8FDAC8 !important;
        }

        div[data-testid="stDialog"] [data-testid="stToggleswitch"] > div {
            background-color: #FFFFFF !important;
        }

        div[data-testid="stDialog"] div[data-testid="stSelectbox"] > div > div {
            background-color: #D6F3E7 !important;
            border: none !important;
            border-radius: 8px !important;
            color: #4B5563 !important;
            font-weight: 400;
            font-size: 14px;
            height: 34px;
            padding: 0px 8px;
            display: flex;
            align-items: center;
        }

        div[data-testid="stDialog"] div.stElementContainer {
            margin-bottom: 0px !important;
        }
                
        /* 확인 버튼 */
        div[data-testid="stDialog"] div.stButton > button {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #3133F !important;
            border-radius: 8px !important;
            padding: 0.25rem 1.6rem;
            font-weight: 600;
        }

        div[data-testid="stDialog"] div.stButton > button:hover {
            color: #BFA9F2 !important;
            border: 1px solid #BFA9F2 !important;
        }

    </style>
    """, unsafe_allow_html=True)

    st.title("지도 설정")

    def create_card(label_text, widget_type, key, options=None, disabled=False):
        c1, c2 = st.columns([6, 4], vertical_alignment="center")

        with c1:
            st.markdown(label_text)

        with c2:
            if widget_type == "toggle":
                st.toggle("", key=key, label_visibility="collapsed", disabled=disabled)
            elif widget_type == "selectbox":
                st.selectbox(
                    "", options=options, key=key,
                    label_visibility="collapsed", disabled=disabled
                )

    create_card("장애인 화장실 표시 여부", "toggle", "show_disabled_tmp")
    create_card("현재 위치 자동 감지 여부", "toggle", "auto_detect_tmp")

    districts = list(LOC_MAP.keys())
    create_card("기본 지도 위치", "selectbox", "map_center_loc_tmp", options=districts)

    if ss.auto_detect_tmp:
        loc_data = get_geolocation()
        if loc_data and "coords" in loc_data:
            lat = loc_data["coords"]["latitude"]
            lng = loc_data["coords"]["longitude"]
            ss.user_location_tmp = (float(lat), float(lng))

        if ss.user_location_tmp is None:
            st.caption("현재 위치를 가져오는 중입니다. 브라우저 위치 권한을 허용해 주세요.")
        else:
            st.caption(f"가져온 현재 위치: {ss.user_location_tmp[0]:.4f}, {ss.user_location_tmp[1]:.4f}")
    else:
        ss.user_location_tmp = None

    if st.button("확인", key="settings_confirm"):
        ss.show_disabled = ss.show_disabled_tmp
        ss.auto_detect = ss.auto_detect_tmp
        ss.map_center_loc = ss.map_center_loc_tmp

        if ss.auto_detect and ss.user_location_tmp is not None:
            ss.user_location = ss.user_location_tmp
        else:
            ss.user_location = None

        st.rerun()

# ---------------------------------------------------
# 7. 상세 정보 모달
# ---------------------------------------------------
@st.dialog(" ", width="large")
def show_toilet_modal(row: pd.Series):
    accessible_txt = "장애인 화장실 있음" if row["accessible"] == 1 else "장애인 화장실 없음"
    gender_txt = "남녀 분리" if row["gender_sep"] == 1 else "공용"
    badge_cls = "" if row["accessible"] == 1 else "gray"
    latlon = f"{row['lat']:.5f}, {row['lng']:.5f}"
    open_time = row.get("open_time", "정보 없음")

    st.markdown(f'<div class="card-title">{row["name"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="badge-row"><span class="badge {badge_cls}">{accessible_txt}</span>'
        f'<span class="badge gray">{gender_txt}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div class="grid-2">
        <div><div class="info-label">행정동</div><div class="info-value">{row['district']} {row['dong']}</div></div>
        <div><div class="info-label">좌표</div><div class="info-value">{latlon}</div></div>
    </div>
    <div style="margin-bottom: 16px;">
        <div class="info-label">주소</div>
        <div class="info-value">{row['addr']}</div>
    </div>
    <div class="grid-2">
        <div><div class="info-label">운영 시간</div><div class="info-value">{open_time}</div></div>
        <div><div class="info-label">비고</div><div class="info-value">&nbsp;</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="detail-section-title">변기 구성</div>
    <table class="detail-table">
        <thead>
            <tr><th>구분</th><th>개수</th><th>구분</th><th>개수</th></tr>
        </thead>
        <tbody>
            <tr>
                <td>남자 변기</td><td>{int(row['male_wc'])}</td>
                <td>여자 변기</td><td>{int(row['female_wc'])}</td>
            </tr>
            <tr>
                <td>남자 장애인</td><td>{int(row['male_wc_disabled'])}</td>
                <td>여자 장애인</td><td>{int(row['female_wc_disabled'])}</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# 8. 플로팅 버튼 (모달 열기)
# ---------------------------------------------------
with st.container():
    st.markdown('<div id="floating-btn-marker"></div>', unsafe_allow_html=True)
    if st.button("", key="settings_btn"):
        ss.show_disabled_tmp = ss.show_disabled
        ss.auto_detect_tmp = ss.auto_detect
        ss.map_center_loc_tmp = ss.map_center_loc
        ss.user_location_tmp = ss.user_location
        open_settings_modal()

# ======================
# 9. 지도 중심 / 줌 계산
# ======================
center, zoom_start = get_center_and_zoom()

# ======================
# 10. 지도 생성
# ======================
m = folium.Map(
    location=center,
    zoom_start=zoom_start,
    tiles="cartodbpositron",
    control_scale=True,
)

# ======================
# 11. 마커 렌더링
# ======================
for _, r in toilets.iterrows():
    accessible = int(r.get("accessible", 0))

    if ss.show_disabled:
        color = "#8FDAC8" if accessible == 1 else "#BFA9F2"
    else:
        color = "#BFA9F2"

    folium.CircleMarker(
        location=(float(r["lat"]), float(r["lng"])),
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=2,
        tooltip=r["name"],
    ).add_to(m)

if ss.auto_detect and ss.user_location is not None:
    folium.CircleMarker(
        location=ss.user_location,
        radius=9,
        color="#9CA3AF",
        fill=True,
        fill_color="#9CA3AF",
        fill_opacity=0.95,
        weight=3,
        tooltip="현재 위치",
    ).add_to(m)

# ======================
# 12. 색상 범례
# ======================
legend_html = ""

# 1. 장애인 화장실 구분 모드일 때
if ss.show_disabled:
    legend_items = f"""
<div style="display: flex; align-items: center;">
    <div style="width: 12px; height: 12px; background-color: #8FDAC8; border-radius: 50%; margin-right: 8px;"></div>
    <div style="color: #4B5563;">장애인 화장실 o</div>
</div>
<div style="display: flex; align-items: center;">
    <div style="width: 12px; height: 12px; background-color: #BFA9F2; border-radius: 50%; margin-right: 8px;"></div>
    <div style="color: #4B5563;">장애인 화장실 x</div>
</div>
    """
# 2. 기본 모드일 때
else:
    legend_items = f"""
<div style="display: flex; align-items: center;">
    <div style="width: 12px; height: 12px; background-color: #BFA9F2; border-radius: 50%; margin-right: 8px;"></div>
    <div style="color: #4B5563;">공공화장실</div>
</div>
    """

# 3. 현재 위치가 켜져 있으면 범례에 추가
if ss.auto_detect and ss.user_location is not None:
    legend_items += """
<div style="display: flex; align-items: center;">
    <div style="width: 12px; height: 12px; background-color: #9CA3AF; border-radius: 50%; margin-right: 8px;"></div>
    <div style="color: #4B5563;">현재 위치</div>
</div>
    """

legend_html = f"""
<div style="
    position: fixed; 
    bottom: 24px; left: 24px; 
    z-index: 1000; 
    background-color: white; 
    padding: 16px 20px; 
    border-radius: 16px; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
    font-size: 13px; 
    font-family: -apple-system, sans-serif;
    min-width: 140px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    justify-content: center;
">
    {legend_items}
</div>
"""

st.markdown(legend_html, unsafe_allow_html=True)

# ======================
# 13. 지도 표시 및 클릭 처리
# ======================
map_state = st_folium(
    m,
    width=2000,
    height=2000,
    use_container_width=False,
    returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
    key="folium_map",
)

current_clicked = map_state.get("last_object_clicked") if map_state else None
current_tooltip = map_state.get("last_object_clicked_tooltip") if map_state else None

should_open_modal = False
target_row = None

if current_clicked and current_clicked != ss.last_clicked_latlng:
    ss.last_clicked_latlng = current_clicked
    ss.last_clicked_tooltip = current_tooltip

    lat = current_clicked.get("lat")
    lng = current_clicked.get("lng")
    if lat is not None and lng is not None and not toilets.empty:
        lat = float(lat)
        lng = float(lng)
        dist = np.sqrt((toilets["lat"] - lat) ** 2 + (toilets["lng"] - lng) ** 2)
        idx = dist.idxmin()
        if dist.loc[idx] < 0.0012:
            target_row = toilets.loc[idx]
            should_open_modal = True

elif current_tooltip and current_tooltip != ss.last_clicked_tooltip:
    ss.last_clicked_tooltip = current_tooltip
    row = toilets.loc[toilets["name"] == current_tooltip]
    if not row.empty:
        target_row = row.iloc[0]
        should_open_modal = True

if should_open_modal and target_row is not None:
    show_toilet_modal(target_row)