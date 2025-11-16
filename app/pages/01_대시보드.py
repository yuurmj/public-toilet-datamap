import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import base64

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

icon1 = img_to_base64("app/theme/DashBoardIcon1.png")
icon2 = img_to_base64("app/theme/DashBoardIcon2.png")
icon3 = img_to_base64("app/theme/DashBoardIcon3.png")
icon4 = img_to_base64("app/theme/DashBoardIcon4.png")
icon5 = img_to_base64("app/theme/DashBoardIcon5.png")

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
    background: conic-gradient( #9bdcc9 0deg 72deg, #c9b7ff 72deg 360deg) !important; display: flex !important; justify-content: center !important; align-items: center !important;
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

.ai-name { font-weight: 600; width: 50px; }

.ai-badge {
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 13px;
    font-weight: 600;
}

.badge-good { background: #F4FCFA; color: #8FDAC8; }
.badge-bad { background: #F9F7FE; color: #BFA9F2; }

.ai-rate { width: 40px; font-weight: 600; text-align: center; color: #6d6a7c; }

.ai-desc { flex: 1; text-align: center; color: #6d6a7c; font-size: 13px; }
.block-container { padding:0 18px 0 18px !important; }
</style>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon1}">
        <div>
            <div class="kpi-value">1000</div>
            <div class="kpi-label">총 화장실 수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k2:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon2}">
        <div>
            <div class="kpi-value">20%</div>
            <div class="kpi-label">장애인 화장실 설치 비율</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k3:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon3}">
        <div>
            <div class="kpi-value">190+</div>
            <div class="kpi-label">인구 대비 화장실 수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with k4:
    st.markdown(f'''
    <div class="kpi-card kpi-flex">
        <img src="data:image/png;base64,{icon4}">
        <div>
            <div class="kpi-value">12+</div>
            <div class="kpi-label">5년간 설치 및 개선 건수</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

left, right = st.columns([3.5, 2])

with left:
    st.markdown('<div class="main-box1">', unsafe_allow_html=True)
    center = [37.5665, 126.9780]
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB Positron")
    folium.Marker(location=center, tooltip="서울시청").add_to(m)
    st_folium(m, width=850, height=457)
    st.markdown('</div>', unsafe_allow_html=True)    
    df = pd.DataFrame({
        "행정동": ["우암동", "대연동", "용당동", "용호동", "문현동", "감만동"],
        "판단": ["부족", "적정", "적정", "부족", "적정", "부족"],
        "비율": ["65%", "89%", "72%", "65%", "89%", "72%"],
        "설명": [
            "인구 대비 화장실 1/800명", "인구 대비 화장실 1/100명", "인구 대비 화장실 1/200명",
            "인구 대비 화장실 1/800명", "인구 대비 화장실 1/100명", "인구 대비 화장실 1/200명"
        ]
    })

    left_df = df.iloc[:3]
    right_df = df.iloc[3:]

    def make_rows(df):
        html = ""
        for _, row in df.iterrows():
            badge = "badge-good" if row["판단"] == "적정" else "badge-bad"
            html += f"""<div class="ai-row">
                <div class="ai-name">{row['행정동']}</div>
                <div class="ai-badge {badge}">{row['판단']}</div>
                <div class="ai-rate">{row['비율']}</div>
                <div class="ai-desc">{row['설명']}</div>
            </div>
            """
        return html

    ai_html = f"""<div class="ai-table-card-box">
        <div class="ai-title">AI 예측 결과 카드</div>
        <div class="ai-wrapper">
            <div class="ai-col">{make_rows(left_df)}</div>
            <div class="ai-col">{make_rows(right_df)}</div>
        </div>
    </div>
    """

    st.markdown(ai_html, unsafe_allow_html=True)


with right:

    html_bars = "<div class='main-box'><div class='right-card'>행정동별 화장실 수</div>"

    regions = ["대연동", "우암동", "감만동", "용호동", "용당동", "문현동"]
    values = [23400, 15000, 30000, 22000, 10000, 23400]
    max_v = max(values)

    for r, v in zip(regions, values):
        color = "#d6c8ff" if r in ["대연동","감만동","문현동"] else "#c3f2d2"
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

    html_pie = f"""
    <div class="main-box">
        <div class="right-card">장애인 화장실 비율</div>
        <div class="donut-wrapper">
            <div class="donut-chart">
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