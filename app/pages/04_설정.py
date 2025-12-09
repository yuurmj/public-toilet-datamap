import streamlit as st
from datetime import date

st.set_page_config(page_title="설정", layout="wide")


st.markdown(
    """<style>
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background-color: #FAFAFB !important;
}

/* 설정 섹션 카드 감싸는 큰 박스 제거 */
div.stVerticalBlock.st-emotion-cache-tn0cau.e196pkbe2 {
    background: transparent !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}
div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.e4man114{
    padding-top: 30px !important;
}
/* h3 밑 여백 줄이기 */
.st-emotion-cache-3uj0rx h3 {
  padding-bottom: 0.1rem; /* 기존 1rem → 0.25rem */
  margin-bottom: 0;        /* 혹시 margin이 생길 경우 제거 */
}
}
#b543a7a3 {
  color: #2c2c2c; /* 진한 회색 */
}
/* 1,2,3번 줄: marker를 가진 VerticalBlock 전체를 카드처럼 */
div[data-testid="stVerticalBlock"]:has(#setting-row-1),
div[data-testid="stVerticalBlock"]:has(#setting-row-2),
div[data-testid="stVerticalBlock"]:has(#setting-row-3) {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 18px 24px;
    margin: 10px 0;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
}

/* 안쪽 여백 조금 정리 */
div[data-testid="stVerticalBlock"]:has(#setting-row-1) > div,
div[data-testid="stVerticalBlock"]:has(#setting-row-2) > div,
div[data-testid="stVerticalBlock"]:has(#setting-row-3) > div {
    padding: 0 !important;
}
            

/* === 토글 색상 커스텀 === */

/* 첫 번째 토글 (장애인 화장실 표시 여부) */
div[data-testid="stToggle"]:nth-of-type(1) div[role="switch"] {
    background-color: #D8CBFF !important;  /* OFF일 때 */
}
div[data-testid="stToggle"]:nth-of-type(1) div[role="switch"][aria-checked="true"] {
    background-color: #A78BFA !important;  /* ON일 때 */
}

/* 두 번째 토글 (현재 위치 자동 감지 여부) */
div[data-testid="stToggle"]:nth-of-type(2) div[role="switch"] {
    background-color: #CFF3EA !important;  /* OFF일 때 */
}
div[data-testid="stToggle"]:nth-of-type(2) div[role="switch"][aria-checked="true"] {
    background-color: #5BD5B7 !important;  /* ON일 때 */
}


/* 아래 4,5번은 기존 setting-card 그대로 사용 */
.setting-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 18px 24px;
    margin: 10px 0;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
}

div[data-testid="column"] > div {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
</style>""",
    unsafe_allow_html=True,
)


DEFAULT_SETTINGS = {
    "show_disabled": False,
    "auto_detect": False,
    "map_center_loc": "대연동",
    "last_data_update": date(2025, 11, 17),
    "language": "한국어",
}

for key, value in DEFAULT_SETTINGS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def render_pill(text: str, bg: str) -> str:
    return f"""<div style="
        padding:8px 20px;
        border-radius:999px;
        background-color:{bg};
        color:#31333F;
        font-size:15px;
        display:inline-block;
        min-width:120px;
        text-align:center;">
        {text}
    </div>"""


st.markdown(
    "<p style='font-size:35px; font-weight:600;'>Settings</p>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#909090; font-size:18px; font-weight:500; margin-top:-25px;'>지도 페이지에서도 설정할 수 있습니다</p>",
    unsafe_allow_html=True
)

st.markdown("""
<div style="
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    padding-bottom: 0px;
    margin-bottom: -5px;
    margin-top:35px;
">
    <div style="flex:2.5; font-size:18px; font-weight:600; padding-left:25px;">Name</div>
    <div style="flex:2.5; font-size:18px; font-weight:600;">Description</div>
    <div style="flex:1; font-size:18px; font-weight:600; text-align:right; padding-right:75px;">Setting</div>
</div>
<hr style="margin-top:8px; margin-bottom:5px; border: 0.5px solid #E5E5E5;">
""", unsafe_allow_html=True)


with st.container():
    st.markdown('<div id="setting-row-1"></div>', unsafe_allow_html=True)

    colA, colB, colC = st.columns([2.5, 3.2, 0.8])

    with colA:
        st.markdown("""<div style=" height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:600; font-size:17px;">계정 설정</span>
                <span style="font-size:13px; color:#909090;">Account Settings</span>
            </div>""", unsafe_allow_html=True)

    with colB:
        st.markdown("""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:500; font-size:17px;">장애인 화장실 표시 여부</span>
                <span style="font-size:13px; color:#909090; margin-top:0px;">Show accessible toilets</span>
            </div>
        """, unsafe_allow_html=True)


    with colC:
        st.markdown(
            '<span id="toggle-show-disabled-marker"></span>', unsafe_allow_html=True
        )
        real_toggle_show = st.toggle(
            "show_disabled_real",
            value=st.session_state.show_disabled,
            label_visibility="collapsed",
        )
        st.session_state.show_disabled = real_toggle_show

with st.container():
    st.markdown('<div id="setting-row-2"></div>', unsafe_allow_html=True)

    colA, colB, colC = st.columns([2.5, 3.2, 0.8])
        
    with colA:
        st.markdown("""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:600; font-size:17px;">지도/위치 설정</span>
                <span style="font-size:13px; color:#909090; margin-top:0px;">Map & Location</span>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:500; font-size:17px;">현재 위치 자동 감지 여부</span>
                <span style="font-size:13px; color:#909090; margin-top:0px;">Default Map Center</span>
            </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown(
            '<span id="toggle-auto-detect-marker"></span>', unsafe_allow_html=True
        )

        real_toggle_auto = st.toggle(
            "auto_detect_real",
            value=st.session_state.auto_detect,
            label_visibility="collapsed",
        )
        st.session_state.auto_detect = real_toggle_auto


districts = ["대연동", "감만동", "용호동", "우암동", "문현동"]

with st.container():
    st.markdown('<div id="setting-row-3"></div>', unsafe_allow_html=True)

    colA, colB, colC = st.columns([2.5, 3, 1])

    with colA:
        st.markdown("""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:600; font-size:17px;">지도/위치 설정</span>
                <span style="font-size:13px; color:#909090; margin-top:0px;">Map & Location</span>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center; margin-top:-10px;">
                <span style="font-weight:500; font-size:17px;">기본 지도 위치</span>
                <span style="font-size:13px; color:#909090; margin-top:0px;">Default Map Center</span>
            </div>
        """, unsafe_allow_html=True)


    with colC:
        selected_center = st.selectbox(
            "",
            districts,
            index=districts.index(st.session_state.map_center_loc),
            label_visibility="collapsed",
        )
        st.session_state.map_center_loc = selected_center


st.markdown(f"""
<div class="setting-card" style="display:flex; align-items:center;">
    <div style="flex:2.5;">
        <div style="font-weight:600; font-size:17px;">데이터 설정</div>
        <div style="font-size:13px; color:#909090; margin-top:0px;">Data & Language</div>
    </div>
    <div style="flex:3;">
        <div style="font-weight:500; font-size:17px;">데이터 최신 업데이트일 확인</div>
        <div style="font-size:13px; color:#909090; margin-top:0px;">Last Data Update</div>
    </div>
    <div style="flex:1; text-align:right;">
        {render_pill("2025.11.17", "#D6F3E7")}
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown(f"""
<div class="setting-card" style="display:flex; align-items:center;">
    <div style="flex:2.5;">
        <div style="font-weight:600; font-size:17px;">언어 설정</div>
        <div style="font-size:13px; color:#909090; margin-top:0px;">Data & Language</div>
    </div>
    <div style="flex:3;">
        <div style="font-weight:500; font-size:17px;">언어 설정 (한국어)</div>
        <div style="font-size:13px; color:#909090; margin-top:0px;">Language (Korean)</div>
    </div>
    <div style="flex:1; text-align:right;">
        {render_pill("한국어", "#E7E1FF")}
    </div>
</div>
""", unsafe_allow_html=True)

