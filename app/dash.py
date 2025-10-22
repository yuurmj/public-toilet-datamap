from pathlib import Path
import json
from math import radians
import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import streamlit.components.v1 as components

# st.set_page_config(page_title="공공화장실 대시보드", layout="wide")


# APP_DIR = Path(__file__).resolve().parent      # app/
# ROOT_DIR = APP_DIR.parent                      # 프로젝트 루트
# CSV_PATH = ROOT_DIR / "data" / "restrooms_min.csv"   # 실제 파일명에 맞게

# @st.cache_data
# def load_data(path: Path) -> pd.DataFrame:
#     return pd.read_csv(path, encoding="utf-8")

# if not CSV_PATH.exists():
#     st.error(f"데이터 파일을 찾을 수 없음: {CSV_PATH}")
#     st.stop()

# df = load_data(CSV_PATH)

# st.title("공공화장실 대시보드")

coords_json = None
sel_district = "전체"
nearest_n = 5

try:
    base
except NameError:
    base = pd.DataFrame(columns=["lat", "lon", "name", "address", "access_score", "accessible", "open_24h"])

PALETTE = {
    "main1":    "#BFA9F2",
    "main2":    "#8FDAC8",
    "mainText": "#374151",
    "heading":  "#111827",
    "sub1":     "#E7E1FF",
    "sub2":     "#D6F3E7",
    "subText":  "#9CA3AF",
    "bg":       "#FAFAFB",
}


# 위치 파싱 & 거리 계산
def haversine(lat1, lon1, lat2, lon2):
    # 지구 반경(km)
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2.0)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

user_lat = user_lon = None
try:
    if coords_json:
        parsed = json.loads(coords_json)
        user_lat, user_lon = parsed.get("lat"), parsed.get("lon")
except Exception:
    pass


st.markdown(f"""
<style>
.stApp {{ background: {PALETTE["bg"]}; color: {PALETTE["mainText"]}; }}
h1, h2, h3, h4, h5, h6 {{ color: {PALETTE["heading"]}; }}
section[data-testid="stSidebar"] {{
  background: {PALETTE["sub1"]};
  color: {PALETTE["mainText"]};
  border-right: 1px solid {PALETTE["subText"]}22;
}}
label, .stMarkdown p, .stTextInput label {{ color: {PALETTE["mainText"]}; }}
.stButton>button {{
  background: linear-gradient(90deg, {PALETTE["main1"]}, {PALETTE["main2"]});
  color: #111; border: 0; border-radius: 10px; padding: .6rem 1rem;
  box-shadow: 0 6px 16px rgba(0,0,0,.08);
}}
.stButton>button:hover {{ filter: brightness(0.98); }}
</style>
""", unsafe_allow_html=True)


st.subheader("지역별 화장실 지도")
highlight_nearby = st.checkbox("내 주변 N개 하이라이트", value=True)


center_lat, center_lon = 37.5663, 126.9779
if sel_district != "전체" and not base.empty:
    center_lat, center_lon = float(base["lat"].mean()), float(base["lon"].mean())
if user_lat and user_lon:
    center_lat, center_lon = float(user_lat), float(user_lon)

m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB positron")

# 사용자 위치 마커 + 반경 원(500m)
if user_lat and user_lon:
    folium.CircleMarker(
        [user_lat, user_lon],
        radius=9,
        color=PALETTE["main2"],
        fill=True, fill_opacity=0.9,
        fillColor=PALETTE["main2"],
        popup="내 위치",
    ).add_to(m)
    folium.Circle(
        [user_lat, user_lon],
        radius=500,             # 미터
        color=PALETTE["subText"],
        fill=True, fill_opacity=0.07,
        weight=1
    ).add_to(m)

# 가까운 N개 계산
near = None
if user_lat and user_lon and nearest_n > 0 and not base.empty:
    tmp = base.copy()
    tmp["distance_km"] = tmp.apply(
        lambda r: haversine(user_lat, user_lon, r["lat"], r["lon"]), axis=1
    )
    near = tmp.sort_values("distance_km").head(nearest_n)



# 전체(또는 필터된) 마커
cluster_all = MarkerCluster(name="전체 시설").add_to(m)

def score_color(score):
    try:
        s = float(score)
    except Exception:
        return PALETTE["subText"]   
    if s < 50:
        return "#D59BE3"            
    if s < 80:
        return PALETTE["main1"]    
    return PALETTE["main2"]        

for _, row in base.iterrows():
    popup_html = f"""
    <div style='font-size:14px;color:{PALETTE["mainText"]}'>
      <b style='color:{PALETTE["heading"]}'>{row['name']}</b><br/>
      주소: {row['address']}<br/>
      접근성 점수: {row.get('access_score', '')}<br/>
      장애인 화장실: {'예' if row.get('accessible',0)==1 else '아니오'}<br/>
      24시간: {'예' if row.get('open_24h',0)==1 else '아니오'}
    </div>
    """
    c = score_color(row.get("access_score", np.nan))
    folium.CircleMarker(
        [row["lat"], row["lon"]],
        radius=6,
        color=c,                 # stroke
        fill=True,
        fill_opacity=0.95,
        fillColor=c,             # fill
        weight=2,
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(cluster_all)



# 4) 가까운 N개 하이라이트
if highlight_nearby and near is not None and len(near) > 0:
    fg_near = folium.FeatureGroup(name=f"내 주변 {len(near)}개", show=True).add_to(m)
    for _, r in near.iterrows():
        folium.CircleMarker(
            [r["lat"], r["lon"]],
            radius=8,
            color=PALETTE["main1"],
            fill=True, fill_opacity=1.0,
            fillColor=PALETTE["main1"],
            weight=3,
            popup=folium.Popup(
                f"<b style='color:{PALETTE['heading']}'>{r['name']}</b><br/>"
                f"<span style='color:{PALETTE['mainText']}'>거리: {r['distance_km']:.3f} km</span>",
                max_width=260
            )
        ).add_to(fg_near)

st_folium(m, width=None, height=640)
