import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import zscore # load_data에 필요
import io

# =========================
# 페이지 기본 설정
# =========================
st.set_page_config(
    page_title="공공화장실 데이터맵 | 분석",
    layout="wide"
)

# =========================
# 📊 글로벌 스타일
# =========================
st.markdown("""
<style>
/* 전체 배경 */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
    background-color: #FAFAFB !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}
            
/* 메인 컨테이너 */
[data-testid="stAppViewContainer"] .main .block-container, .stMainBlockContainer {
    padding: 0 32px;
    max-width: 1200px;
    margin-bottom: 0;
}

.stHorizontalBlock {
    gap: 20px;
}
            
/* 폰트 공통 */
h1, h2, h3, h4, label, div, span {
    font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    color: #222222;
}

/* 상단 메트릭 카드 */
.analytics-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 20px 24px 18px;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
    height: 135px; /* 카드 높이 유지 */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
}

.metric-label {
    font-size: 14px;
    color: #374151;
}
.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #222222;
    margin-top: 4px;
}
.metric-sub {
    margin-top: 4px;
    font-size: 13px;
    color: #9FA8BA; /* 기본 텍스트 색상 */
    display: flex;
    align-items: center;
    gap: 4px;
}
.metric-sub span.icon {
    font-size: 13px;
    /* 아이콘 색상은 HTML 내부에서 개별 적용 */
}

/* Plotly 차트 관련 스타일 */
.js-plotly-plot .plotly .main-svg {
    background-color: rgba(0,0,0,0) !important;
    overflow: visible !important; /* 텍스트가 잘리지 않도록 overflow 허용 */
}
/* Plotly 텍스트 색상 */
.infolayer .g-gdata .g-t .text {
    fill: #222222 !important; 
}
/* nsewdrag 요소 숨기기 */
.rect.nsewdrag.drag {
    pointer-events: none !important;
    opacity: 0 !important;
}

/* =========================
   상단 우측 "구 선택" 버튼
   ========================= */

/* selectbox 컨테이너를 오른쪽에, 카드 사이즈로 */
div[data-testid="stSelectbox"] {
    width: 150px;
    margin-left: auto;      
    margin-top: 0;
    margin-bottom: 0;
}

/* 라벨 숨기기 */
div[data-testid="stSelectbox"] > label {
    display: none !important;
}

/* 바깥 박스를 하얀 카드처럼 */
div[data-testid="stSelectbox"] > div {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    height: 45px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
}

/* 선택 텍스트 스타일 */
div[data-testid="stSelectbox"] [data-baseweb="select"] {
    font-size: 16px;
    font-weight: 600;
    color: #3F3D56;
}

/* 내부 배경/테두리 제거해서 바깥 카드와 일체감 */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* 텍스트 + 아이콘 정렬 */
div[data-testid="stSelectbox"] [data-baseweb="select"] div[role="combobox"] {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

/* 드롭다운 아이콘 */
div[data-testid="stSelectbox"] svg {
    color: #8F8F99;
    width: 20px;
    height: 20px;
}
""", unsafe_allow_html=True)


# =========================
# 💾 데이터 로드 및 처리
# =========================
@st.cache_data
def load_data():
    try:
        toilets = pd.read_csv("data/toilets_mock.csv")
        pop = pd.read_csv("data/population_mock.csv")
    except FileNotFoundError:
        st.error("오류: 'data/toilets_mock.csv' 또는 'data/population_mock.csv' 파일을 찾을 수 없습니다. (이전 대화에서 생성한) 해당 파일들이 'data' 폴더 내에 있는지 확인해주세요.")
        return pd.DataFrame(), pd.DataFrame(), 0

    needed = [
        "toilet_id", "name", "addr", "lat", "lng",
        "district", "dong",
        "accessible", "gender_sep",
        "male_wc", "female_wc"
    ]
    for c in needed:
        if c not in toilets.columns:
            toilets[c] = np.nan

    toilets["district"] = toilets["district"].fillna("남구")
    toilets["dong"] = toilets["dong"].fillna("미상")
    toilets["accessible"] = toilets["accessible"].fillna(0).astype(int)
    toilets["male_wc"] = toilets["male_wc"].fillna(0).astype(int)
    toilets["female_wc"] = toilets["female_wc"].fillna(0).astype(int)
    
    toilets = toilets.dropna(subset=["lat", "lng"]) 

    toilets["bowls_sum"] = toilets[["male_wc", "female_wc"]].sum(axis=1, min_count=1)

    by = toilets.groupby(["district", "dong"], as_index=False).agg(
        toilets_count=("toilet_id", "count"),
        accessible_count=("accessible", "sum"),
        bowls_total=("bowls_sum", "sum"),
    )

    df = by.merge(pop, on=["district", "dong"], how="left")
    df["population"] = df["population"].fillna(0).astype(int)

    df["toilets_per_1k"] = np.where(
        df["population"] > 0,
        (df["toilets_count"] / df["population"]) * 1000.0, # 1천명 당 개수
        np.nan
    )
    df["accessible_ratio"] = np.where(
        df["toilets_count"] > 0,
        df["accessible_count"] / df["toilets_count"],
        np.nan
    )

    if df["population"].std(ddof=0) > 0 and df["toilets_count"].std(ddof=0) > 0:
        df["gap_score"] = (
            zscore(df["population"].astype(float), nan_policy="omit")
            - zscore(df["toilets_count"].astype(float), nan_policy="omit")
        )
    else:
        df["gap_score"] = 0.0

    if "density_per_km2" not in df.columns:
        df["density_per_km2"] = np.nan # 면적당 밀도 (데이터 없음)

    bowls_avg = toilets["bowls_sum"].replace(0, np.nan).mean()
    
    if df.empty:
        st.error("데이터를 불러왔으나, 처리 후 집계(agg) 데이터가 비어있습니다.")
        return pd.DataFrame(), pd.DataFrame(), 0
        
    return toilets, df, bowls_avg

# 데이터 로드 실행
toilets, agg, bowls_avg = load_data()

if agg.empty:
    st.stop()

# =========================
# 구 선택 버튼
# =========================
gu_list = sorted(agg["district"].dropna().unique())
gu_options = ["전체"] + gu_list
default_index = gu_options.index("남구") if "남구" in gu_options else 0

left_spacer, right_box = st.columns([4, 1])
with right_box:
    st.markdown('<div class="gu-select-row"><div class="gu-select-card">', unsafe_allow_html=True)
    selected_gu = st.selectbox(
        "",
        options=gu_options,
        index=default_index,
        label_visibility="collapsed",
        key="gu_select_top"
    )
    st.markdown('</div></div>', unsafe_allow_html=True)

# =========================
# 📈 상단 요약 카드 4개
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    total = int(agg["toilets_count"].sum())
    st.markdown(f"""
<div class="analytics-card">
  <div class="metric-label">총 화장실 수</div>
  <div class="metric-value">{total:,}</div>
  <div class="metric-sub"><span class="icon" style="color:#BFA9F2;">▲</span>평균 대비 +8.2%</div>
</div>
""", unsafe_allow_html=True)

with c2:
    acc_total = agg['accessible_count'].sum()
    total_count = agg['toilets_count'].sum()
    acc_ratio = (acc_total / total_count) * 100 if total_count > 0 else 0
    st.markdown(f"""
<div class="analytics-card">
  <div class="metric-label">장애인 화장실 비율</div>
  <div class="metric-value">{acc_ratio:.1f}%</div>
  <div class="metric-sub"><span class="icon" style="color:#8FDAC8;">▼</span>평균 대비 -3.1%p</div>
</div>
""", unsafe_allow_html=True)

with c3:
    bowls_text = f"{bowls_avg:.1f}" if not np.isnan(bowls_avg) else "N/A"
    st.markdown(f"""
<div class="analytics-card">
  <div class="metric-label">화장실 당 평균 변기 수</div>
  <div class="metric-value">{bowls_text}</div>
  <div class="metric-sub"><span class="icon" style="color:#BFA9F2;">▲</span>평균 대비 +15%</div>
</div>
""", unsafe_allow_html=True)

with c4:
    pop_sum = agg["population"].sum()
    t_sum = agg["toilets_count"].sum()
    ratio = int(pop_sum / t_sum) if t_sum > 0 else 0
    st.markdown(f"""
<div class="analytics-card">
  <div class="metric-label">인구 대비 화장실</div>
  <div class="metric-value">1 / {ratio:,}</div>
  <div class="metric-sub">평균 인원 수</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # 여백

# =========================
# 🛠️ 헬퍼 함수 정의
# =========================

def chart_card(title: str, fig, subtitle: str | None = None, height: int = 250):

    fig_html = fig.to_html(include_plotlyjs='cdn', full_html=False)
    sub = f'<div class="chart-subtitle">{subtitle}</div>' if subtitle else ""
    
    card_internal_height = height + 50 
    
    html = f"""
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }}
    .chart-card {{
      background-color: #FFFFFF;
      border-radius: 24px;
      padding: 20px 24px 18px;
      height: {card_internal_height}px;
      box-sizing: border-box;
    }}
    .chart-title {{
      font-size: 18px; /* 폰트 크기 18px */
      font-weight: 700; /* 폰트 굵기 700 */
      margin-bottom: 10px;
      color: #222222;
    }}
    .chart-subtitle {{
      font-size: 11px;
      color: #9FA8BA;
      margin-bottom: 8px;
    }}
    .js-plotly-plot .plotly .main-svg {{
      background-color: rgba(0,0,0,0) !important;
      overflow: visible !important; /* 텍스트 잘림 방지 */
    }}
    .infolayer .g-gdata .g-t .text {{
        fill: #222222 !important;
    }}
    .rect.nsewdrag.drag {{
        pointer-events: none !important;
        opacity: 0 !important;
    }}
  </style>
</head>
<body>
  <div class="chart-card">
    <div class="chart-title">{title}</div>
    {sub}
    {fig_html}
  </div>
</body>
</html>
"""
    components.html(html, height=card_internal_height, scrolling=False)


def ratio_card(df):
    """인구 대비 화장실 수 그리드 카드 컴포넌트를 생성합니다."""
    
    df_calc = df.dropna(subset=['toilets_per_1k']).copy()
    if not df_calc.empty:
        low_q = df_calc['toilets_per_1k'].quantile(0.33)
        high_q = df_calc['toilets_per_1k'].quantile(0.66)
    else:
        low_q, high_q = 0, 0

    def classify(x):
        if pd.isna(x): return '평균'
        if x <= low_q: return '부족'
        if x > high_q: return '충분'
        return '평균'

    df['type'] = df['toilets_per_1k'].apply(classify)

    colors = {
        "부족": "#D6F3E7", # 민트
        "충분": "#E7E1FF", # 라벤더
        "평균": "#EEEEEE"  # 회색
    }
    df['color'] = df['type'].map(colors)

    target_dongs = ['대연동', '용호동', '문현동', '감만동', '우암동', '용당동']
    card_data = []
    
    for dong in target_dongs:
        row = df[df['dong'] == dong]
        if not row.empty:
            r = row.iloc[0]
            value_str = f"{r['toilets_per_1k']:.2f}" if pd.notna(r['toilets_per_1k']) else "N/A"
            card_data.append({"dong": dong, "value": value_str, "color": r['color']})
        else:
            card_data.append({"dong": dong, "value": "N/A", "color": "#EEEEEE"})

    html_cards = ""
    for item in card_data:
        html_cards += f"""
        <div class="pill" style="background:{item['color']};">
          <span class="pill-label">{item['dong']}</span>
          <span class="pill-value">{item['value']}</span>
        </div>
        """

    html = f"""
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{ margin: 0; padding: 0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }}
    .chart-card {{
      background-color: #FFFFFF;
      border-radius: 24px;
      padding: 20px 24px 18px;
      height: 300px; 
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      justify-content: center; 
    }}
    .chart-title {{ 
        font-size: 18px; /* 폰트 크기 18px */
        font-weight: 700; /* 폰트 굵기 700 */
        margin-bottom: 4px; 
        color: #222222; 
    }}
    .chart-subtitle {{ font-size: 12px; color: #374151; opacity: 0.7; margin-bottom: 6px; }}
    .grid-container {{ 
        display: grid; 
        grid-template-columns: repeat(3, 1fr); 
        gap: 8px; 
        margin-top: 15px; /* 부제목과 그리드 간 간격 */
    }}
    .pill {{
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      width: 100%; aspect-ratio: 1 / 1; border-radius: 12px;
      font-size: 13px; font-weight: 500; color: #222222; padding: 0;
    }}
    .pill-label {{ font-size: 12px; font-weight: 500; margin-bottom: 2px; }}
    .pill-value {{ font-size: 20px; font-weight: 700; }}
    .legend {{ display: flex; justify-content: center; gap: 15px; margin-top: 20px; font-size: 12px; color: #374151; opacity: 0.7; }}
    .legend-item {{ display: flex; align-items: center; gap: 5px; }}
    .legend-color {{ width: 12px; height: 12px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div>
    <div class="chart-card">
        <div>
            <div class="chart-title">인구 대비 화장실 수</div>
            <div class="chart-subtitle">1천 명당 공중화장실 수 기준</div>
            <div class="grid-container">{html_cards}</div>
            <div class="legend">
                <div class="legend-item"><div class="legend-color" style="background:{colors['부족']};"></div><span>부족</span></div>
                <div class="legend-item"><div class="legend-color" style="background:{colors['평균']};"></div><span>평균</span></div>
                <div class="legend-item"><div class="legend-color" style="background:{colors['충분']};"></div><span>충분</span></div>
            </div>
        </div>
    </div>
  </div>
</body>
</html>
"""
    components.html(html, height=300, scrolling=False)

# =========================
# 📑 중단 3개 카드
# =========================
colA, colB, colC = st.columns([1.2, 1.2, 1.0])

# --- 차트 1: 행정동별 화장실 수 ---
with colA:
    df1 = agg.copy()
    color_map_1 = {
        '문현동': '#D6F3E7', '감만동': '#E7E1FF', '대연동': '#D6F3E7',
        '용호동': '#E7E1FF', '우암동': '#D6F3E7', '용당동': '#E7E1FF'
    }
    
    fig1 = px.bar(
        df1.sort_values("toilets_count", ascending=True),
        y="dong",
        x="toilets_count",
        orientation="h",
        color="dong",
        color_discrete_map=color_map_1,
        text="toilets_count"
    )
    fig1.update_layout(
        xaxis_title="", yaxis_title="",
        template="plotly_white",
        height=250, 
        margin=dict(l=40, r=40, t=0, b=20), # 좌우 여백 40 (차트 꽉 차게)
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(tickfont=dict(size=12), fixedrange=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        bargap=0.6,
        dragmode=False
    )
    fig1.update_traces(
        texttemplate='%{x:,}', 
        textposition='outside',
        cliponaxis=False 
    )
    chart_card("행정동별 화장실 수", fig1, height=250)

# --- 차트 2: 장애인 화장실 설치 비율 ---
with colB:
    df2 = agg.copy()
    color_map_2 = {
        '문현동': '#E7E1FF', '감만동': '#D6F3E7', '대연동': '#E7E1FF',
        '용호동': '#D6F3E7', '우암동': '#E7E1FF', '용당동': '#D6F3E7'
    }

    fig2 = px.bar(
        df2.sort_values("accessible_ratio", ascending=True),
        y="dong",
        x="accessible_ratio",
        orientation="h",
        color="dong",
        color_discrete_map=color_map_2,
        text="accessible_ratio"
    )
    fig2.update_layout(
        xaxis_title="", yaxis_title="",
        template="plotly_white",
        height=250,
        margin=dict(l=40, r=40, t=0, b=20), # 좌우 여백 40 (차트 꽉 차게)
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(tickfont=dict(size=12), fixedrange=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        bargap=0.6,
        dragmode=False
    )
    fig2.update_traces(
        texttemplate='%{x:.0%}', 
        textposition='outside',
        cliponaxis=False
    )
    chart_card("장애인 화장실 설치 비율", fig2, height=250)

# --- 차트 3: 인구 대비 화장실 수 ---
with colC:
    ratio_card(agg)

# =========================
# 📋 하단 테이블 카드
# =========================

tbl = agg.copy()
tbl = tbl.rename(columns={
    "dong": "행정동",
    "toilets_count": "총 화장실 수",
    "accessible_ratio": "장애인 화장실 비율",
    "toilets_per_1k": "인구 대비 화장실 수",
    "density_per_km2": "면적당 밀도"
})

tbl['장애인 화장실 비율'] = tbl['장애인 화장실 비율'].apply(
    lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"
)
tbl['인구 대비 화장실 수'] = tbl['인구 대비 화장실 수'].apply(
    lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
)
tbl['면적당 밀도'] = tbl['면적당 밀도'].apply(
    lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
)

tbl_display = tbl[[
    "행정동",
    "총 화장실 수",
    "장애인 화장실 비율",
    "인구 대비 화장실 수",
    "면적당 밀도"
]]

html_table = tbl_display.to_html(index=False, classes="", border=0, na_rep="N/A")

table_html = f"""
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }}
    .table-card {{
      background-color: #FFFFFF;
      border-radius: 24px;
      padding: 20px 24px 18px;
      font-size: 13px;
      height: auto;
      box-sizing: border-box;
      overflow-y: auto;
    }}
    h3 {{
      font-size: 18px; /* 폰트 크기 18px */
      font-weight: 700; /* 폰트 굵기 700 */
      margin: 0 0 24px 0; /* 제목과 테이블 간 간격 24px */
      color: #222222;
      text-align: left; /* 제목 왼쪽 정렬 */
    }}
    table {{
      width: 100%; /* 테이블 너비 100% */
      border-collapse: collapse;
      table-layout: fixed; /* 테이블 레이아웃 고정 */
    }}
    thead tr th {{
      background-color: #E7E1FF;
      color: #374151;
      font-weight: 600;
      padding: 10px 12px;
      font-size: 13px;
      text-align: center; /* 헤더 왼쪽 정렬 */
      position: sticky;
      top: 0;
      white-space: nowrap; 
    }}
    tbody tr td {{
      border-top: 1px solid #F0F1F5;
      padding: 8px 12px;
      font-size: 13px;
      color: #374151;
      text-align: center; /* 본문 왼쪽 정렬 */
      white-space: nowrap; 
    }}
    
    /* 첫 번째 열(행정동) 너비 */
    th:nth-child(1), td:nth-child(1) {{
        width: 20%; 
    }}
    
    /* 나머지 숫자 열들 오른쪽 정렬 */
    th:nth-child(2), td:nth-child(2),
    th:nth-child(3), td:nth-child(3),
    th:nth-child(4), td:nth-child(4),
    th:nth-child(5), td:nth-child(5) {{
        text-align: center;
        width: 18%;
    }}
  </style>
</head>
<body>
  <div class="table-card">
    <h3>공중화장실 세부 현황</h3>
    {html_table}
  </div>
</body>
</html>
"""

components.html(table_html, height=370, scrolling=True)