import streamlit as st
from datetime import date
from textwrap import dedent

# 1) 페이지 기본 설정
st.set_page_config(page_title="설정", layout="wide")

# Streamlit 기본 헤더/메뉴/푸터 제거
st.markdown("""
<style>
/* 메인 컨테이너의 기본 padding 제거 */  /* 추가 */
.block-container {
    padding-top: 0rem !important;
}
            
/* 상단 헤더 숨기기 */
header[data-testid="stHeader"] {
    display: none !important;
}

/* 상단 메뉴 바 숨기기 */
#MainMenu {
    display: none !important;
}

/* 푸터 숨기기 */
footer {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* 전체 배경 회색 */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
    background-color: #FAFAFB !important;
}

/* 공통 카드 박스 (흰색 박스) */
.setting-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 18px 24px;
    margin: 10px 0;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
}
</style>
""", unsafe_allow_html=True)


# 토글 UI
def render_toggle(is_on: bool) -> str:
    """글자가 동그라미 안에 들어가는 알약형 토글 (고정형 UI)"""
    if is_on:
        outer_bg = "#E7E1FF"   # 연한 보라
        circle_bg = "#BFA9F2"  # 진한 보라
        text = "ON"
        text_color = "#FFFFFF"
        circle_pos = "right:6px;"   # 원 위치
    else:
        outer_bg = "#E5E7EB"   # 연한 회색
        circle_bg = "#9CA3AF"  # 진한 회색
        text = "OFF"
        text_color = "#FFFFFF"
        circle_pos = "left:6px;"

    return f"""
    <div style="
        position:relative;
        width:100px;
        height:34px;
        border-radius:999px;
        background-color:{outer_bg};
        display:flex;
        align-items:center;
        justify-content:center;
    ">
        <div style="
            position:absolute;
            width:28px;
            height:28px;
            border-radius:50%;
            background-color:{circle_bg};
            {circle_pos}
            top:3px;
            display:flex;
            align-items:center;
            justify-content:center;
        ">
            <span style="color:{text_color}; font-size:12px; font-weight:600;">
                {text}
            </span>
        </div>
    </div>
    """

# 알약형 배지 UI
def render_pill(text: str, bg: str) -> str:
    return f"""<div style="
            padding:8px 20px;
            border-radius:999px;
            background-color:{bg};
            color:#31333F;
            font-weight:350;
            font-size:15px;
            display:inline-block;
            text-align:center;
            min-width:120px;
        ">
            {text}
        </div>
    """




# 표 형태 레이아웃 틀 만들기 (Name / Description / Setting)
# 표 전체를 하나의 컨테이너로
table = st.container()

with table:
    # 헤더 행
    c1, c2, c3 = st.columns([2.5, 3, 1])

    c1.markdown("**Name**")
    c2.markdown("**Description**")
    c3.markdown("**Setting**")

    st.markdown(
    """
    <div style='margin-top:-10px; margin-bottom:0px;'>
        <hr style='margin:0; padding:0; border:0; border-top:1px solid #ddd;'/>
    </div>
    """,
    unsafe_allow_html=True
)


# 계정 설정 – 장애인 화장실 표시 여부
    # 계정 설정
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">
    <div style="flex:2.5;">
        <div style="font-weight:600;">계정 설정</div>
        <div style="font-size:13px; color:#909090;">Account Settings</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">장애인 화장실 표시 여부</div>
        <div style="font-size:13px; color:#909090;">Show accessible toilets</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_toggle(True)}
    </div>
    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)



#지도/위치 – 현재 위치 자동 감지 여부
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">

    <div style="flex:2.5;">
        <div style="font-weight:600;">지도/위치 설정</div>
        <div style="font-size:13px; color:#909090;">Map & Location</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">현재 위치 자동 감지 여부</div>
        <div style="font-size:13px; color:#909090;">Auto-detect Current Location</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_toggle(False)}
    </div>

    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)




# 기본 지도 위치
    # 기본 지도 위치 (보라색 배지)
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">

    <div style="flex:2.5;">
        <div style="font-weight:600;">지도/위치 설정</div>
        <div style="font-size:13px; color:#909090;">Map & Location</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">기본 지도 위치</div>
        <div style="font-size:13px; color:#909090;">Default Map Center</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_pill("남구 대연동", "#E7E1FF")}
    </div>

    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)





# 검색 & 필터 – 가까운 화장실 개수 기본값
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">

    <div style="flex:2.5;">
        <div style="font-weight:600;">검색 & 필터 설정</div>
        <div style="font-size:13px; color:#909090;">Search & Filters</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">가까운 화장실 개수 기본값</div>
        <div style="font-size:13px; color:#909090;">Default Number of Nearby Toilets</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_pill("5개", "#D6F3E7")}
    </div>

    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)



# 데이터 & 언어 – 데이터 최신 업데이트일 확인
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">

    <div style="flex:2.5;">
        <div style="font-weight:600;">데이터 & 언어 설정</div>
        <div style="font-size:13px; color:#909090;">Data & Language</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">데이터 최신 업데이트일 확인</div>
        <div style="font-size:13px; color:#909090;">Last Data Update</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_pill("2025.11.17", "#E7E1FF")}
    </div>

    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)





# 데이터 & 언어 – 언어 선택 (한국어만 가능)
    html = dedent(f"""
    <div class="setting-card" style="display:flex; align-items:center;">

    <div style="flex:2.5;">
        <div style="font-weight:600;">데이터 & 언어 설정</div>
        <div style="font-size:13px; color:#909090;">Data & Language</div>
    </div>

    <div style="flex:3;">
        <div style="font-weight:500;">언어 설정 (한국어)</div>
        <div style="font-size:13px; color:#909090;">Language (Korean)</div>
    </div>

    <div style="flex:1; text-align:right;">
        {render_pill("한국어", "#D6F3E7")}
    </div>

    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)

