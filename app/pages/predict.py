import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- 기본 설정 --------------------
st.set_page_config(page_title="공공화장실 예측", layout="wide")

# -------------------- CSS --------------------
st.markdown("""
    <style>
    body, .main {
        background-color: #f7f8fc;
        font-family: 'Pretendard', sans-serif;
    }

    /* 불필요한 빈 블록 제거 */
    section[data-testid="stVerticalBlock"] div:empty {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 카드 공통 디자인 */
    .card {
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        padding: 22px 28px;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e2247;
        margin-bottom: 10px;
    }

    /* 시뮬레이션 표 */
    .sim-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
        font-size: 14px;
        color: #222;
    }
    .sim-table th {
        background-color: #fafafa;
        font-weight: 600;
        padding: 8px;
        border-bottom: 1px solid #eee;
    }
    .sim-table td {
        padding: 8px;
        border-bottom: 1px solid #f2f2f2;
    }

    .sim-icon { font-size: 20px; color: #5e3ed6; }
    .up { color: #9D8DF1; font-weight: 700; }
    .down { color: #71D6C9; font-weight: 700; }

    .sim-btn {
        background-color: #C9B8FF;
        color: white;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    .sim-btn:hover { background-color: #A694F9; }

    .model-info {
        font-size: 14px;
        line-height: 1.7em;
        color: #222;
    }

    div[data-testid="stPlotlyChart"] {
        height: 100% !important;
        max-height: 270px !important;
    }

    /* 🔧 여백 및 자동 높이 제거 핵심 */
    div[data-testid="stVerticalBlock"] {
        height: fit-content !important;
        min-height: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    div[data-testid="stColumn"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    section[data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 데이터 --------------------
data = pd.DataFrame({
    "행정동": ["대연동", "용호동", "우암동", "문현동"],
    "예측 등급": ["부족", "적정", "과잉", "부족"],
    "권장설치수": [2, 0, 0, 1],
    "설치율": ["65%", "90%", "110%", "75%"],
    "인구 대비 화장실수": ["1/1800명", "2/1800명", "3/1800명", "1/1800명"]
})
grade_colors = {"부족": "#A6E3C2", "적정": "#B5B5B5", "과잉": "#CABAF7"}

# -------------------- 상단 (예측결과 / 지역별분포) --------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚻 공공화장실 예측 결과 · 📊 예측 결과</div>', unsafe_allow_html=True)
    st.dataframe(
        data.style.applymap(
            lambda v: f"color: {grade_colors.get(v, 'black')}" if v in grade_colors else "",
            subset=["예측 등급"]
        ),
        use_container_width=True
    )
    st.checkbox("부족 지역만 보기")
    st.checkbox("설치순 낮은 순으로 정렬")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗺️ 지역별 분포</div>', unsafe_allow_html=True)
    fig = px.bar(
        data,
        x="행정동",
        y="권장설치수",
        color="예측 등급",
        color_discrete_map=grade_colors,
        height=250
    )
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- 하단 (시뮬레이션 / 모델정보) --------------------
bottom1, bottom2 = st.columns(2)

with bottom1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔮 시뮬레이션</div>', unsafe_allow_html=True)
    html = """
    <table class="sim-table">
        <thead><tr>
            <th></th><th>인구변화율</th><th>예산배율</th><th>장애인화장실 비율</th><th>예측하기</th>
        </tr></thead>
        <tbody>
            <tr>
                <td class="sim-icon">👤</td>
                <td class="up">110%</td>
                <td class="up">200%</td>
                <td>30% 이상</td>
                <td><button class="sim-btn">Simulation</button></td>
            </tr>
            <tr>
                <td class="sim-icon">👤</td>
                <td class="down">90%</td>
                <td class="down">50%</td>
                <td>10% 이상</td>
                <td><button class="sim-btn">Simulation</button></td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with bottom2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🤖 모델 정보</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="model-info">
    • <b>사용 데이터:</b> 인구, 면적, 시설 수<br>
    • <b>예측 방법:</b> 회귀 모델<br>
    • <b>R²:</b> 0.87
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
