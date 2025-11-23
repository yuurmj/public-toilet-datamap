import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import base64

st.set_page_config(page_title="공중화장실 데이터맵", layout="wide")


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

profile_icon = img_to_base64("app/theme/PredictionModel.png")
sim_icon = img_to_base64("app/theme/PredictionSimulation.png")


if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "행정동": ["대연1동", "용호1동", "우암동", "문현1동"],
        "인구": [30000, 42000, 18000, 25000],
        "면적": [2.5, 3.1, 1.2, 2.0],
        "시설수": [8, 10, 5, 6],
        "장애인비율": [0.25, 0.35, 0.15, 0.20],
        "예측등급": ["부족", "적정", "과잉", "부족"],
        "권장설치수": [2, 0, 0, 1],
        "설치율": ["65%", "90%", "110%", "75%"],
        "인구대비화장실수": ["1/1800명", "2/1800명", "3/1800명", "1/1800명"]
    })

df = st.session_state.df


global_css = """
<style>
.filter-box {
    background: #ffffff;
    padding: 16px 22px;
    border-radius: 16px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 17px;
    color: #333;
    font-weight: 500;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
}
.filter-check {
    width: 22px;
    height: 22px;
}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)


col1, col2 = st.columns([1, 1])

with col1:

    only_bad = st.checkbox("부족 지역만 보기", key="only_bad", label_visibility="collapsed")
    sort_low = st.checkbox("설치율 낮은 순으로 정렬", key="sort_low", label_visibility="collapsed")

    html = f"""
    <style>
    .predict-title {{
        margin-left: 20px !important;
    }}
    .left-box {{
        background: #ffffff;
        padding: 20px 25px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }}
    .legend-box {{
        display: flex;
        gap: 20px;
        margin: 0px 30px 0px 0;
        font-size: 17px;
        align-items: center;
        justify-content: flex-end;
        font-weight: 600;
    }}
    .dot {{
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }}
    table, th, td {{
        border: none !important;
        text-align: center !important;
    }}
    .tbl {{
        width: 100%;
        border-collapse: separate !important;
        border-spacing: 0 16px !important;
        font-size: 15px;
        color: #3F3D56;
    }}
    .tbl thead tr th {{
        border-bottom: 1px solid #E5E7EB !important;
        padding: 12px 5px;
        font-size: 14px;
        color: #030229;
        text-align: center !important;
        font-weight: 400;
    }}
    .tbl tbody tr td {{
        padding: 16px 5px;
        border: none !important;
        text-align: left;
        color:#030229;
    }}
    .grade-bad {{ background: #D6F3E7; padding: 6px 12px; border-radius: 9px;color:#030229; }}
    .grade-mid {{ background: #9CA3AF; padding: 6px 12px; border-radius: 9px; color:#030229; }}
    .grade-good {{ background: #E7E1FF; padding: 6px 12px; border-radius: 9px;color:#030229; }}
    .arrow {{
        font-size: 10px;
        margin-left: 6px;
        color: #9CA3AF;
        border-radius:3px;
    }}
    div[data-testid="stCheckbox"] {{
        display: none !important;
    }}

    .block-container {{
        padding: 0 20px !important;
    }}
    </style>
    <div class='left-box'>
        <h4 class="predict-title">예측 결과</h4>
        <div class='legend-box'>
            <div><span class='dot' style='background:#93d7b0;'></span> 부족</div>
            <div><span class='dot' style='background:#cfcfd3;'></span> 적정</div>
            <div><span class='dot' style='background:#bfb8e8;'></span> 과잉</div>
        </div>
        <table class='tbl'>
            <thead>
                <tr>
                    <th>행정동 <span class="arrow">▼</span></th>
                    <th>예측 등급 <span class="arrow">▼</span></th>
                    <th>권장설치수 <span class="arrow">▼</span></th>
                    <th>설치율 <span class="arrow">▼</span></th>
                    <th>인구 대비 화장실수 <span class="arrow">▼</span></th>
                </tr>
            </thead>
            <tbody>
    """

    for _, r in df.iterrows():
        grade = r["예측등급"]
        grade_class = "grade-bad" if grade == "부족" else "grade-mid" if grade == "적정" else "grade-good"

        html += f"""<tr>
            <td>{r['행정동']}</td>
            <td><span class='{grade_class}'>{r['예측등급']}</span></td>
            <td>{r['권장설치수']}</td>
            <td>{r['설치율']}</td>
            <td>{r['인구대비화장실수']}</td>
        </tr>
        """

    html += """</tbody></table></div>"""
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="filter-box">
        <input type="checkbox" class="filter-check" {'checked' if only_bad else ''} onclick="document.getElementById('only_bad').click()">
        부족 지역만 보기
    </div>

    <div class="filter-box">
        <input type="checkbox" class="filter-check" {'checked' if sort_low else ''} onclick="document.getElementById('sort_low').click()">
        설치율 낮은 순으로 정렬
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 지도 결과")

    coords = {
        "대연1동": (35.13, 129.10),
        "용호1동": (35.12, 129.12),
        "우암동": (35.11, 129.09),
        "문현1동": (35.15, 129.07)
    }
    color_map = {"부족": "#93d7b0", "적정": "#cfcfd3", "과잉": "#bfb8e8"}

    m = folium.Map(location=[35.13, 129.10], zoom_start=13, tiles="cartodb positron")

    for _, r in df.iterrows():
        folium.CircleMarker(
            location=coords[r["행정동"]],
            radius=25,
            color=color_map[r["예측등급"]],
            fill=True,
            fill_color=color_map[r["예측등급"]],
            fill_opacity=0.9,
            popup=f"{r['행정동']} ({r['예측등급']})"
        ).add_to(m)

    st_folium(m, width=800, height=600)


col3, col4 = st.columns([1.5, 1])

# 시뮬레이션 아이콘 base64 변환
sim_icon = img_to_base64("app/theme/PredictionSimulation.png")

with col3:

    sim_icon = img_to_base64("app/theme/PredictionSimulation.png")
    arrow_down_icon = img_to_base64("app/theme/PurpleArrowDown.svg")
    arrow_down_icon2 = img_to_base64("app/theme/GreenArrowDown.svg")

    sim_html = f"""
    <style>
    .sim-box {{background: #ffffff; padding: 32px 10px; border-radius: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); margin-top:15px;font-family: 'SUIT';}}
    .sim-title {{ font-size: 20px; font-weight: 700; margin-bottom: 32px; margin-left:20px;color: #030229;}}
    .sim-header {{text-align:center;display:grid;grid-template-columns: 40px 1fr 1fr 1fr 1fr;padding: 0 4px 16px 4px;font-size:15px;font-weight:600;color:#3f3d56;border-bottom: 1px solid #f1f1f1}}
    .sim-row {{display: grid;grid-template-columns: 60px 1fr 1fr 1fr 0.8fr 20px;align-items: center;padding: 20px 6px;border-bottom: 1px solid #f1f1f1;text-align:center;}}
    .sim-icon {{width:42px;height:42px;border-radius:50%;}}
    .sim-input-container {{display: flex;align-items: center; width: 100%;padding: 0 5%;  }}
    .sim-text {{font-size:15px;font-weight:400;color:#030229;}}
    .sim-btn {{padding:0px 15px;background:#bFA9F2;padding:10px 22px;color:white;font-size:15px;border-radius:12px;border:none;cursor:pointer;font-weight:400;}}
    .sim-btn:hover {{opacity:0.9; }}
    .sim-input {{width:100px;background:#f3f5f9;border-radius:12px;margin-left:5px;padding:8px 12px;border:none;outline:none;font-size:15px;font-weight:400;color:#030229;background;transparent;text-align:center;}}
    .arrow-btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: none;
        background: transparent;
        cursor: pointer;
        padding: 4px;
    }}
    .arrow-btn img {{
        width: 16px;
        height: 16px;
    }}
    </style>
    <div class='sim-box'>
        <div class='sim-title'>시뮬레이션</div>
        <div class='sim-header'>
            <div></div>
            <div>인구변화율</div>
            <div >예산배율</div>
            <div>장애인화장실 비율</div>
            <div>예측하기</div>
        </div>
        <!-- Row 1 -->
        <div class='sim-row'>
            <img src="data:image/png;base64,{sim_icon}" class="sim-icon">
            <div class="sim-input-container">
                <input id="sim1_pop" class="sim-input" value="110%"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon}">
                    </button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_bud" class="sim-input" value="200%"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon}">
                    </button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_acc" class="sim-input" value="30%이상"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon}">
                    </button>
            </div>
            <button class="sim-btn" onclick="window.location.href='/?sim1=1&pop='+document.getElementById('sim1_pop').value+'&bud='+document.getElementById('sim1_bud').value+'&acc='+document.getElementById('sim1_acc').value">
                Simulation
            </button>
        </div>
        <div class='sim-row'>
            <img src="data:image/png;base64,{sim_icon}" class="sim-icon">
            <div class="sim-input-container">
                <input id="sim1_pop" class="sim-input" value="90%"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon2}">
                    </button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_bud" class="sim-input" value="50%"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon2}">
                    </button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_acc" class="sim-input" value="10%이상"/>
                    <button class="arrow-btn">
                        <img src="data:image/svg+xml;base64,{arrow_down_icon2}">
                    </button>
            </div>
            <button class="sim-btn" onclick="window.location.href='/?sim1=1&pop='+document.getElementById('sim1_pop').value+'&bud='+document.getElementById('sim1_bud').value+'&acc='+document.getElementById('sim1_acc').value">
                Simulation
            </button>
        </div>
    </div>
    """

    st.markdown(sim_html, unsafe_allow_html=True)




with col4:

    html_model = f"""
    <style>
    .model-box {{
        background: #ffffff;
        padding: 35px 40px;
        border-radius: 30px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.07);
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 25px;
        width: 100%;
    }}
    .model-img {{
        width: 85px;
        height: 85px;
        border-radius: 50%;
        object-fit: cover;
    }}
    .model-title {{
        font-size: 22px;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 14px;
    }}
    .model-text {{
        font-size: 16px;
        color: #444;
        line-height: 1.6;
    }}
    .model-divider {{
        width: 100%;
        border-bottom: 1px solid #eaeaea;
        margin-top: 22px;
    }}
    </style>
    <div class="model-box">
        <img src="data:image/png;base64,{profile_icon}" class="model-img">
        <div>
            <div class="model-title">모델 정보</div>
            <div class="model-text">
                - 사용 데이터: 인구, 면적, 시설 수<br>
                - 예측 방법: 회귀 모델<br>
                - R² = 0.87
            </div>
        </div>
        <div class="model-divider"></div>
    </div>
    """

    st.markdown(html_model, unsafe_allow_html=True)
