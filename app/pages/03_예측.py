import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import base64

st.set_page_config(page_title="공중화장실 데이터맵", layout="wide")

# --- 이미지 base64 변환 ---
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

profile_icon = img_to_base64("app/theme/PredictionModel.png")
sim_icon = img_to_base64("app/theme/PredictionSimulation.png")
arrow_down_icon = img_to_base64("app/theme/PurpleArrowDown.svg")
arrow_down_icon2 = img_to_base64("app/theme/GreenArrowDown.svg")

# --- 초기 데이터 ---
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


# --- 컬럼 레이아웃 ---
col1, col2 = st.columns([1, 1])

# --- 필터, 테이블 ---
with col1:

    table_container = st.empty()

    # --- 렌더링 함수 ---
    def render_table(only_bad=False, sort_low=False):
        df_filtered = df.copy()
        if only_bad:
            df_filtered = df_filtered[df_filtered["예측등급"]=="부족"]
        if sort_low:
            df_filtered = df_filtered.sort_values(by="설치율")

        html = f"""
        <style>
        .left-box {{
            background: #ffffff;
            padding: 20px 25px;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            margin-bottom: 20px;
        }}
        table, th, td {{ border: none !important; text-align: center !important; }}
        .tbl {{ width: 100%; border-collapse: separate !important; border-spacing: 0 16px !important; font-size: 15px; color: #3F3D56; }}
        .tbl thead tr th {{ border-bottom: 1px solid #E5E7EB !important; padding: 12px 5px; font-size: 14px; color: #030229; font-weight: 400; }}
        .tbl tbody tr td {{ padding: 16px 5px; text-align: left; color:#030229; }}
        .grade-bad {{ background: #D6F3E7; padding: 6px 12px; border-radius: 9px; }}
        .grade-mid {{ background: #9CA3AF; padding: 6px 12px; border-radius: 9px; }}
        .grade-good {{ background: #E7E1FF; padding: 6px 12px; border-radius: 9px; }}
        </style>
        <div class='left-box'>
        <h4>예측 결과</h4>
        <table class='tbl'>
            <thead>
                <tr>
                    <th>행정동</th>
                    <th>예측 등급</th>
                    <th>권장설치수</th>
                    <th>설치율</th>
                    <th>인구 대비 화장실수</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, r in df_filtered.iterrows():
            grade_class = (
                "grade-bad" if r["예측등급"]=="부족" 
                else "grade-mid" if r["예측등급"]=="적정" 
                else "grade-good"
            )
            html += f"""<tr>
                    <td>{r['행정동']}</td>
                    <td><span class='{grade_class}'>{r['예측등급']}</span></td>
                    <td>{r['권장설치수']}</td>
                    <td>{r['설치율']}</td>
                    <td>{r['인구대비화장실수']}</td>
                </tr>
            """
        html += "</tbody></table></div>"

        table_container.markdown(html, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div.stVerticalBlock, div.stHorizontalBlock {
        width: 100% !important;
        max-width: 100% !important;
        gap:0 20px !important;
    }
    div.stCheckbox {
        background: #ffffff;
        padding: 14px 22px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        width: 500px;
    }
    div.stCheckbox > label {
        font-size: 16px;
        font-weight: 500;
        width: 100%;
        display: flex;
        align-items: center;
    }
    div.stCheckbox input[type="checkbox"] {
        width: 18px;
        height: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        only_bad = st.checkbox("부족 지역만 보기")
        sort_low = st.checkbox("설치율 높은 순으로 정렬")

    render_table(only_bad, sort_low)


# --- 지도 ---
with col2:
    st.markdown("### 지도 결과")
    coords = {"대연1동": (35.13, 129.10), "용호1동": (35.12, 129.12), "우암동": (35.11, 129.09), "문현1동": (35.15, 129.07)}
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


# --- 시뮬레이션 + 모델 정보 ---
col3, col4 = st.columns([1.5, 1])
# --- 시뮬레이션 + 모델 정보 ---
col3, col4 = st.columns([1.5, 1])

with col3:
    sim_html = f"""
    <style>
    .sim-box {{background: #ffffff; padding: 32px 10px; border-radius: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); margin-top:15px;font-family: 'SUIT';}}
    .sim-title {{ font-size: 20px; font-weight: 700; margin-bottom: 32px; margin-left:20px;color: #030229;}}
    .sim-header {{text-align:center;display:grid;grid-template-columns: 40px 1fr 1fr 1fr 1fr;padding: 0 4px 16px 4px;font-size:15px;font-weight:600;color:#3f3d56;border-bottom: 1px solid #f1f1f1}}
    .sim-row {{display: grid;grid-template-columns: 60px 1fr 1fr 1fr 0.8fr 20px;align-items: center;padding: 20px 6px;border-bottom: 1px solid #f1f1f1;text-align:center;}}

    .sim-icon {{width:42px;height:42px;border-radius:50%;}}
    .sim-input-container {{display: flex;align-items: center; width: 100%;padding: 0 5%;  }}
    .sim-input {{width:100px;background:#f3f5f9;border-radius:12px;margin-left:5px;padding:8px 12px;border:none;outline:none;font-size:15px;font-weight:400;color:#030229;text-align:center;}}
    .sim-btn {{padding:10px 22px;background:#bFA9F2;color:white;border-radius:12px;border:none;font-weight:400;}}
    .arrow-btn {{display: inline-flex;align-items: center;justify-content: center;width: 32px;height: 32px;border-radius: 50%;border: none;background: transparent;padding: 4px;}}
    .arrow-btn img {{width: 16px;height: 16px;}}
    </style>
    <div class='sim-box'>
        <div class='sim-title'>시뮬레이션</div>
        <div class='sim-header'>
            <div></div>
            <div>인구변화율</div>
            <div>예산배율</div>
            <div>장애인화장실 비율</div>
            <div>예측하기</div>
        </div>
        <!-- Row 1 -->
        <div class='sim-row'>
            <img src="data:image/png;base64,{sim_icon}" class="sim-icon">
            <div class="sim-input-container">
                <input id="sim1_pop" class="sim-input" value="110%"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon}"></button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_bud" class="sim-input" value="200%"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon}"></button>
            </div>
            <div class="sim-input-container">
                <input id="sim1_acc" class="sim-input" value="30%이상"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon}"></button>
            </div>
            <button class="sim-btn" onclick="window.location.href='/?sim1=1&pop='+document.getElementById('sim1_pop').value+'&bud='+document.getElementById('sim1_bud').value+'&acc='+document.getElementById('sim1_acc').value">Simulation</button>
        </div>
        <!-- Row 2 -->
        <div class='sim-row'>
            <img src="data:image/png;base64,{sim_icon}" class="sim-icon">
            <div class="sim-input-container">
                <input id="sim2_pop" class="sim-input" value="90%"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon2}"></button>
            </div>
            <div class="sim-input-container">
                <input id="sim2_bud" class="sim-input" value="50%"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon2}"></button>
            </div>
            <div class="sim-input-container">
                <input id="sim2_acc" class="sim-input" value="10%이상"/>
                <button class="arrow-btn"><img src="data:image/svg+xml;base64,{arrow_down_icon2}"></button>
            </div>
            <button class="sim-btn" onclick="window.location.href='/?sim2=1&pop='+document.getElementById('sim2_pop').value+'&bud='+document.getElementById('sim2_bud').value+'&acc='+document.getElementById('sim2_acc').value">Simulation</button>
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
    .model-img {{ width: 85px; height: 85px; border-radius: 50%; object-fit: cover; }}
    .model-title {{ font-size: 22px; font-weight: 700; color: #1f1f1f; margin-bottom: 14px; }}
    .model-text {{ font-size: 16px; color: #444; line-height: 1.6; }}
    .model-divider {{ width: 100%; border-bottom: 1px solid #eaeaea; margin-top: 22px; }}
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
