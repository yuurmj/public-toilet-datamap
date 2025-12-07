import streamlit as st
from datetime import date
from textwrap import dedent

# 페이지 기본 설정
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
h6 {
    color: #374151 !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    margin-top: -10px !important;
    margin-bottom: 30px !important;
            
}

/* 헤더 아래 hr 여백 조절 */
hr {
    margin-top: -16px !important;
}
</style>
""", unsafe_allow_html=True)

# 페이지 제목 및 설명
st.markdown("""
### 지도 설정 및 환경 관리
###### 지도 페이지에서도 설정할 수 있습니다
""")

# 스타일 정의
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
    background-color: #FAFAFB !important;
}

.setting-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 18px 24px;
    margin: 10px 0;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
}
</style>
""", unsafe_allow_html=True)

# 기본 설정값
DEFAULT_SETTINGS = {
    "show_disabled": False,
    "auto_detect": False,
    "map_center_loc": "남구 대연동",
    "last_data_update": date(2025, 11, 17),
    "language": "ko",
}

# 세션 초기화
def init_settings():
    for key, value in DEFAULT_SETTINGS.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_settings()

# 토글 UI 렌더링 함수
def render_toggle(is_on: bool) -> str:
    outer_bg = "#E7E1FF" if is_on else "#E5E7EB"
    circle_bg = "#BFA9F2" if is_on else "#9CA3AF"
    text = "ON" if is_on else "OFF"
    text_color = "#FFFFFF"
    circle_pos = "right:6px;" if is_on else "left:6px;"
    return f"""
    <div style="position:relative; width:100px; height:34px; border-radius:999px; background-color:{outer_bg}; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; width:28px; height:28px; border-radius:50%; background-color:{circle_bg}; {circle_pos} top:3px; display:flex; align-items:center; justify-content:center;">
            <span style="color:{text_color}; font-size:12px; font-weight:600;">{text}</span>
        </div>
    </div>"""

# 알약 배지 렌더링 함수
def render_pill(text: str, bg: str) -> str:
    return f"""
    <div style="padding:8px 20px; border-radius:999px; background-color:{bg}; color:#31333F; font-size:15px; display:inline-block; min-width:120px; text-align:center;">
        {text}</div>"""

# 표 구조 컨테이너
table = st.container()

with table:
    c1, c2, c3 = st.columns([2.5, 3, 1])
    c1.markdown("**Name**")
    c2.markdown("**Description**")
    c3.markdown("**Setting**")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # 장애인 화장실 표시 여부
    html = f"""
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
            {render_toggle(st.session_state.show_accessible_toilets)}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 현재 위치 자동 감지 여부
    html = f"""
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
            {render_toggle(st.session_state.auto_detect_location)}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 기본 지도 위치
    html = f"""
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
            {render_pill(st.session_state.default_map_center, "#E7E1FF")}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 데이터 최신 업데이트일
    html = f"""
    <div class="setting-card" style="display:flex; align-items:center;">
        <div style="flex:2.5;">
            <div style="font-weight:600;">데이터 설정</div>
            <div style="font-size:13px; color:#909090;">Data & Language</div>
        </div>
        <div style="flex:3;">
            <div style="font-weight:500;">데이터 최신 업데이트일 확인</div>
            <div style="font-size:13px; color:#909090;">Last Data Update</div>
        </div>
        <div style="flex:1; text-align:right;">
            {render_pill("2025.11.17", "#D6F3E7")}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 언어 설정
    html = f"""
    <div class="setting-card" style="display:flex; align-items:center;">
        <div style="flex:2.5;">
            <div style="font-weight:600;">언어 설정</div>
            <div style="font-size:13px; color:#909090;">Data & Language</div>
        </div>
        <div style="flex:3;">
            <div style="font-weight:500;">언어 설정 (한국어)</div>
            <div style="font-size:13px; color:#909090;">Language (Korean)</div>
        </div>
        <div style="flex:1; text-align:right;">
            {render_pill("한국어", "#E7E1FF")}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)



# import streamlit as st
# from datetime import date

# # -------------------------------
# # 페이지 설정
# # -------------------------------
# st.set_page_config(page_title="설정", layout="wide")


# # -------------------------------
# # 초기 상태값 설정
# # -------------------------------
# DEFAULT_SETTINGS = {
#     "show_accessible_toilets": True,
#     "auto_detect_location": False,
#     "default_map_center": "남구 대연동",
#     "last_data_update": date(2025, 11, 17),
#     "language": "ko",
# }

# for key, value in DEFAULT_SETTINGS.items():
#     if key not in st.session_state:
#         st.session_state[key] = value


# # -------------------------------
# # CSS
# # -------------------------------
# st.markdown("""
# <style>
# body, html, [data-testid="stAppViewContainer"] {
#     background-color: #FAFAFB !important;
# }

# /* 제목 스타일 */
# .section-title {
#     font-size: 32px;
#     font-weight: 700;
#     margin-bottom: 2px;
#     color: #2B2D33;
# }
# .section-subtitle {
#     font-size: 17px;
#     color: #707070;
#     margin-bottom: 28px;
# }

# /* 테이블 헤더 */
# .table-header {
#     font-size: 20px;
#     font-weight: 600;
#     color: #36383F;
# }
# .table-line {
#     border-bottom: 1px solid #E5E5E5;
#     margin-top: 6px;
#     margin-bottom: 22px;
# }

# /* 카드 스타일 */
# .setting-card {
#     background: #FFFFFF;
#     padding: 24px 28px;
#     border-radius: 22px;
#     box-shadow: 0px 8px 20px rgba(0,0,0,0.06);
#     margin-bottom: 22px;
# }
# </style>
# """, unsafe_allow_html=True)


# # -------------------------------
# # 제목
# # -------------------------------
# st.markdown('<div class="section-title">지도 기능과 위치 기반 서비스를 개인 설정에 맞게 관리하세요</div>', unsafe_allow_html=True)
# st.markdown('<div class="section-subtitle">지도 페이지에서도 설정할 수 있습니다</div>', unsafe_allow_html=True)


# # -------------------------------
# # 표 헤더
# # -------------------------------
# h1, h2, h3 = st.columns([2.5, 3, 1])
# with h1:
#     st.markdown('<div class="table-header">Name</div>', unsafe_allow_html=True)
# with h2:
#     st.markdown('<div class="table-header">Description</div>', unsafe_allow_html=True)
# with h3:
#     st.markdown('<div class="table-header">Setting</div>', unsafe_allow_html=True)

# st.markdown('<div class="table-line"></div>', unsafe_allow_html=True)


# # ============================================================
# #                카드 1: 장애인 화장실 표시 여부             
# # ============================================================
# with st.container():
#     st.markdown('<div class="setting-card">', unsafe_allow_html=True)
#     col1, col2, col3 = st.columns([2.5, 3, 1])

#     with col1:
#         st.markdown("**계정 설정**")
#         st.markdown('<span style="color:#909090; font-size:13px;">Account Settings</span>',
#                     unsafe_allow_html=True)

#     with col2:
#         st.markdown("장애인 화장실 표시 여부")
#         st.markdown('<span style="color:#909090; font-size:13px;">Show accessible toilets</span>',
#                     unsafe_allow_html=True)

#     with col3:
#         st.session_state.show_accessible_toilets = st.toggle(
#             "",
#             value=st.session_state.show_accessible_toilets,
#         )
#     st.markdown("</div>", unsafe_allow_html=True)


# # ============================================================
# #                카드 2: 현재 위치 자동 감지                   
# # ============================================================
# with st.container():
#     st.markdown('<div class="setting-card">', unsafe_allow_html=True)
#     col1, col2, col3 = st.columns([2.5, 3, 1])

#     with col1:
#         st.markdown("**지도/위치 설정**")
#         st.markdown('<span style="color:#909090; font-size:13px;">Map & Location</span>',
#                     unsafe_allow_html=True)

#     with col2:
#         st.markdown("현재 위치 자동 감지 여부")
#         st.markdown('<span style="color:#909090; font-size:13px;">Auto-detect Current Location</span>',
#                     unsafe_allow_html=True)

#     with col3:
#         st.session_state.auto_detect_location = st.toggle(
#             "",
#             value=st.session_state.auto_detect_location,
#         )
#     st.markdown("</div>", unsafe_allow_html=True)


# # ============================================================
# #                카드 3: 기본 지도 위치                       
# # ============================================================
# with st.container():
#     st.markdown('<div class="setting-card">', unsafe_allow_html=True)
#     col1, col2, col3 = st.columns([2.5, 3, 1])

#     with col1:
#         st.markdown("**지도/위치 설정**")
#         st.markdown('<span style="color:#909090; font-size:13px;">Map & Location</span>',
#                     unsafe_allow_html=True)

#     with col2:
#         st.markdown("기본 지도 위치")
#         st.markdown('<span style="color:#909090; font-size:13px;">Default Map Center</span>',
#                     unsafe_allow_html=True)

#     with col3:
#         st.markdown(
#             f'<div style="padding:8px 20px; border-radius:999px; background:#E7E1FF; text-align:center; font-size:15px;">{st.session_state.default_map_center}</div>',
#             unsafe_allow_html=True
#         )
#     st.markdown("</div>", unsafe_allow_html=True)


# # ============================================================
# #                카드 4: 데이터 최신 업데이트일               
# # ============================================================
# with st.container():
#     st.markdown('<div class="setting-card">', unsafe_allow_html=True)
#     col1, col2, col3 = st.columns([2.5, 3, 1])

#     with col1:
#         st.markdown("**데이터 설정**")
#         st.markdown('<span style="color:#909090; font-size:13px;">Data</span>',
#                     unsafe_allow_html=True)

#     with col2:
#         st.markdown("데이터 최신 업데이트일 확인")
#         st.markdown('<span style="color:#909090; font-size:13px;">Last Data Update</span>',
#                     unsafe_allow_html=True)

#     with col3:
#         st.markdown(
#             f'<div style="padding:8px 20px; border-radius:999px; background:#D6F3E7; text-align:center; font-size:15px;">2025.11.17</div>',
#             unsafe_allow_html=True
#         )
#     st.markdown("</div>", unsafe_allow_html=True)


# # ============================================================
# #                카드 5: 언어 설정                            
# # ============================================================
# with st.container():
#     st.markdown('<div class="setting-card">', unsafe_allow_html=True)
#     col1, col2, col3 = st.columns([2.5, 3, 1])

#     with col1:
#         st.markdown("**언어 설정**")
#         st.markdown('<span style="color:#909090; font-size:13px;">Language</span>',
#                     unsafe_allow_html=True)

#     with col2:
#         st.markdown("언어 설정 (한국어)")
#         st.markdown('<span style="color:#909090; font-size:13px;">Language (Korean)</span>',
#                     unsafe_allow_html=True)

#     with col3:
#         st.markdown(
#             f'<div style="padding:8px 20px; border-radius:999px; background:#E7E1FF; text-align:center; font-size:15px;">한국어</div>',
#             unsafe_allow_html=True
#         )
#     st.markdown("</div>", unsafe_allow_html=True)
