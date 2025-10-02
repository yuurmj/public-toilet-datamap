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

st.subheader("지역별 화장실 지도")
highlight_nearby = st.checkbox("내 주변 N개 하이라이트", value=True)


center_lat, center_lon = 37.5663, 126.9779
if sel_district != "전체" and not base.empty:
    center_lat, center_lon = float(base["lat"].mean()), float(base["lon"].mean())
if user_lat and user_lon:
    center_lat, center_lon = float(user_lat), float(user_lon)

m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

# 사용자 위치 마커 + 반경 원(500m)
if user_lat and user_lon:
    folium.Marker(
        [user_lat, user_lon],
        tooltip="내 위치",
        popup="내 위치",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(m)
    folium.Circle(
        [user_lat, user_lon],
        radius=500,             # 미터
        color="blue",
        fill=True, fill_opacity=0.05
    ).add_to(m)

# 가까운 N개 계산
near = None
if user_lat and user_lon and nearest_n > 0 and not base.empty:
    tmp = base.copy()
    tmp["distance_km"] = tmp.apply(
        lambda r: haversine(user_lat, user_lon, r["lat"], r["lon"]), axis=1
    )
    near = tmp.sort_values("distance_km").head(nearest_n)

