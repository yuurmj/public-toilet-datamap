import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import base64
from streamlit_js_eval import get_geolocation

from ml.run_prediction import run_prediction   # 🔥 실제 데이터 기반 예측 엔진

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 아이콘 불러오기
icon1 = img_to_base64("app/theme/DashBoardIcon1.png")
icon2 = img_to_base64("app/theme/DashBoardIcon2.png")
icon3 = img_to_base64("app/theme/DashBoardIcon3.png")
icon4 = img_to_base64("app/theme/DashBoardIcon4.png")
icon5 = img_to_base64("app/theme/DashBoardIcon5.png")

# -------------------------------------------------
# 🔥 실제 데이터 불러오기 & 예측 실행
# -------------------------------------------------
df = run_prediction(pop_rate=10)   # 30만 인구 기반 → pop_rate * 30,000

# KPI 계산
total_toilets = df["시설수"].sum()
acc_ratio = (df["장애인비율"] * df["시설수"]).sum() / total_toilets

population = 300000
toilets_per_100k = total_toilets / population * 100000

improve_cnt = (df["예측등급"] == "부족").sum()  # 개선이 필요한 동 개수

dong_counts = df[["행정동", "시설수"]]

# -------------------------------------------------
# 스타일 / CSS
# -------------------------------------------------
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/suit-font@1.0.0/suit.min.css">
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/sunn-us/SUIT/fonts/static/woff2/SUIT-Regular.woff2');
@import url('https://cdn.jsdelivr.net/gh/sunn-us/SUIT/fonts/static/woff2/SUIT-Bold.woff2');

body, [class*="css"] {
    font-family: 'SUIT', sans-serif !important;
    background-color: #f8f9fc !important;
}

.kpi-card { margin-top:26px; background: #ffffff; padding: 22px; border-radius: 18px; box-shadow: 0 3px 10px rgba(0,0,0,0.04); border: 1px solid #f1f3f7; }
.kpi-value { font-weight: 800; font-size: 22px; }
.kpi-label { font-weight: 500; color: #6c6b7b; font-size: 13px; }

.kpi-flex { display: flex; align-items: center; gap: 16px; text-align: left; }
.kpi-flex img { width: 42px; }

.main-box { background: #ffffff; margin-top:12px; padding: 10px; border-radius: 18px; box-shadow: 0 3px 10px rgba(0,0,0,0.04); border: 1px solid #f1f3f7;}
.right-card { padding: 8px; font-weight:600; font-size:20px; margin:8px 0 16px 16px; }

.bar-row { display:flex; align-items:center; margin:10px 0 14px 0; }
.bar-label { padding:0 0 0 16px; width:70px; font-weight:300; font-size:15px; color:#333; }
.bar-box { flex:1; display:flex; align-items:center; gap:10px; }
.bar-fill { height:12px; border-radius: 0 10px 10px 0; }
.bar-value { width:60px; text-align:right; font-size:15px; font-weight:300; color:#333; }

.donut-wrapper { display: flex; flex-direction: column; align-items: center; padding: 30px 0 35px 0 !important;}
.donut-chart { width: 210px !important; height: 210px !important; border-radius: 50% !important;
 display: flex !important; justify-content: center !important; align-items: center !important;
    box-shadow:
        0 18px 30px rgba(0, 0, 0, 0.18),
        0 10px 20px rgba(0, 0, 0, 0.10),
        0 4px 8px rgba(0, 0, 0, 0.06) !important;
}
.donut-center { width: 150px !important; height: 150px !important; border-radius: 50% !important; background: #ffffff !important; 
    box-shadow: inset 0 10px 20px rgba(0, 0, 0, 0.10), inset 0 5px 10px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.05) !important; display: flex !important; justify-content: center !important; align-items: center !important;}

.center-icon img { width: 46px !important; filter: drop-shadow(0px 3px 5px rgba(0,0,0,0.12));}
.legend-box { margin-top: 16px;}
.legend-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px;}
.legend-dot { width: 14px; height: 14px; border-radius: 50%;}            

.ai-table-card-box {
    background: #ffffff;
    padding: 25px 30px;
    border-radius: 18px;
    border: 1px solid #f1f3f7;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    margin-top: 10px;
}
.ai-title { font-size: 20px; font-weight:700; padding-bottom:18px; }

.ai-wrapper { display:flex; gap:30px; }

.ai-col { flex:1; }

.ai-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 5px;
    border-bottom: 1px solid #f3f4f6;
}

.ai-row:last-child { border-bottom: none; }

.ai-name { font-weight: 600; width: 15%; }

.ai-badge {
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 13px;
    font-weight: 600;
}

.badge-good { background: #F4FCFA; color: #8FDAC8; }
.badge-bad { background: #F9F7FE; color: #BFA9F2; }
.badge-over { background: #F4FCFA; color: #8FDAC8;}

.ai-rate { width: 13%; font-weight: 600; text-align: right; color: #6d6a7c; }
.ai-desc { flex: 1; text-align: center; color: #6d6a7c; font-size: 13px; }

.block-container { padding:0 18px 0 18px !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# KPI 카드 영역
# -------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon1}">
        <div>
            <div class="kpi-value">{total_toilets}</div>
            <div class="kpi-label">총 화장실 수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k2:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon2}">
        <div>
            <div class="kpi-value">{acc_ratio:.1%}</div>
            <div class="kpi-label">장애인 화장실 설치 비율</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k3:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon3}">
        <div>
            <div class="kpi-value">{toilets_per_100k:.1f}</div>
            <div class="kpi-label">인구 대비 화장실 수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k4:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon4}">
        <div>
            <div class="kpi-value">{improve_cnt}+</div>
            <div class="kpi-label">5년간 설치 및 개선 건수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# -------------------------------------------------
# 왼쪽 지도 + AI 예측 결과 카드
# -------------------------------------------------
left, right = st.columns([3.5, 2])

with left:
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # km
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        return 2 * R * np.arcsin(np.sqrt(a))

    loc = get_geolocation()
    if loc is None:
        st.warning("📍 위치 접근 권한을 허용해주세요!")
        st.stop()

    user_lat = loc["coords"]["latitude"]
    user_lon = loc["coords"]["longitude"]

    # ----------------------------
    # 2) 화장실 CSV 불러오기 + 좌표 정리
    # ----------------------------
    df_toilet = pd.read_csv("data/raw/toilets_namgu.csv")

    df_toilet["lat"] = pd.to_numeric(df_toilet["lat"], errors="coerce")
    df_toilet["lon"] = pd.to_numeric(df_toilet["lon"], errors="coerce")

    df_toilet = df_toilet.dropna(subset=["lat", "lon"])

    # ----------------------------
    # 3) 거리 계산 (정확하게)
    # ----------------------------
    df_toilet["distance"] = df_toilet.apply(
        lambda r: haversine(user_lat, user_lon, r["lat"], r["lon"]),
        axis=1
    )


    # 반경 700m 이내의 화장실들
    near = df_toilet[df_toilet["distance"] <= 0.7]

    # 만약 5개보다 적으면 → 가장 가까운 5개 가져오기
    if len(near) < 5:
        near = df_toilet.nsmallest(5, "distance")


    m = folium.Map(location=[user_lat, user_lon], zoom_start=15,tiles="CartoDB Positron")

    # 내 위치 마커 (빨강)
    folium.CircleMarker(
        [user_lat, user_lon],
        radius=8,
        color="red",
        fill=True,
        fill_color="red"
    ).add_to(m)

    # 가까운 화장실 마커 5개 이상 표시 (파랑)
    for _, row in near.iterrows():
        folium.CircleMarker(
            [row["lat"], row["lon"]],
            radius=6,
            color="pulple",
            fill=True,
            fill_color="purple"
        ).add_to(m)

    st_folium(m, height=500, width=900)

    def get_badge_class(grade):
        if grade == "적정":
            return "badge-good"
        elif grade == "부족":
            return "badge-bad"
        else:  # 과잉
            return "badge-over"

    # 결과 카드 생성
    def make_rows(df_part):
        html = ""
        for _, row in df_part.iterrows():
            badge_class = get_badge_class(row["예측등급"])
            html += f"""<div class="ai-row">
        <div class="ai-name">{row['행정동']}</div>
        <div class="ai-badge {badge_class}">{row['예측등급']}</div>
        <div class="ai-rate">{row['설치율']}</div>
        <div class="ai-desc">{row['인구대비화장실수']}</div>
    </div>
    """
        return html


    half = len(df)//2
    ai_html = f"""<div class="ai-table-card-box"><div class="ai-title">AI 예측 결과 카드</div><div class="ai-wrapper"><div class="ai-col">{make_rows(df.iloc[:half])}</div><div class="ai-col">{make_rows(df.iloc[half:])}</div></div></div>"""
    st.markdown(ai_html, unsafe_allow_html=True)


# -------------------------------------------------
# 오른쪽 바 차트 + 도넛 차트
# -------------------------------------------------
with right:

    # 🔥 행정동별 화장실 수
    html_bars = "<div class='main-box'><div class='right-card'>행정동별 화장실 수</div>"

    values = dong_counts["시설수"].tolist()
    regions = dong_counts["행정동"].tolist()
    max_v = max(values)

    for r, v in zip(regions, values):
        color = "#d6c8ff" if v < max_v * 0.7 else "#c3f2d2"
        width = (v / max_v) * 100

        html_bars += (
            f"<div class='bar-row'>"
            f"<div class='bar-label'>{r}</div>"
            f"<div class='bar-box'>"
            f"<div class='bar-fill' style='width:{width}%; background:{color};'></div>"
            f"<div class='bar-value'>{v:,}</div>"
            f"</div>"
            f"</div>"
        )

    html_bars += "</div>"
    st.markdown(html_bars, unsafe_allow_html=True)

    # 🔥 장애인 화장실 비율 도넛
    # 장애인 화장실 설치 비율(0~1 값)
    acc_ratio = 0.422   # 예: 0.422 → 42.2%

    installed_deg = acc_ratio * 360  # 도넛 각도 계산

    donut_style = f"""
    background: conic-gradient(
        #9bdcc9 0deg {installed_deg}deg,
        #c9b7ff {installed_deg}deg 360deg
    );
    """

    html_pie = f"""
    <div class="main-box">
        <div class="right-card">장애인 화장실 비율</div>
        <div class="donut-wrapper">
            <div class="donut-chart" style="{donut_style}">
                <div class="donut-center">
                    <img src="data:image/png;base64,{icon5}" style="width:48px;">
                </div>
            </div>
            <div class="legend-box">
                <div class="legend-item">
                    <div class="legend-dot" style="background:#9bdcc9;"></div>
                    <div>장애인 화장실 설치</div>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background:#c9b7ff;"></div>
                    <div>장애인 화장실 미설치</div>
                </div>
            </div>
        </div>
    </div>
    """

    st.markdown(html_pie, unsafe_allow_html=True)


