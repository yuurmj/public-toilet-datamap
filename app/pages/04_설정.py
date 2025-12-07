import streamlit as st
from datetime import date

st.set_page_config(page_title="설정", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 0rem !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
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

DEFAULT_SETTINGS = {
    "show_disabled": False,
    "auto_detect": False,
    "map_center_loc": "남구 대연동",
    "last_data_update": date(2025, 11, 17),
    "language": "ko",
}

for key, value in DEFAULT_SETTINGS.items():
    if key not in st.session_state:
        st.session_state[key] = value

def render_toggle(is_on: bool) -> str:
    bg = "#E7E1FF" if is_on else "#E5E7EB"
    circle = "#BFA9F2" if is_on else "#9CA3AF"
    text = "ON" if is_on else "OFF"
    pos = "right:6px;" if is_on else "left:6px;"
    return f"""<div style="position:relative; width:100px; height:34px; border-radius:999px;
         background-color:{bg}; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; width:28px; height:28px; border-radius:50%;
             background-color:{circle}; {pos} top:3px; display:flex; align-items:center; 
             justify-content:center;">
            <span style="color:white; font-size:12px; font-weight:600;">{text}</span>
        </div>
    </div>"""

def render_pill(text: str, bg: str) -> str:
    return f"""<div style="padding:8px 20px; border-radius:999px; background-color:{bg};
         color:#31333F; font-size:15px; display:inline-block; min-width:120px;
         text-align:center;">
        {text}</div>"""

st.markdown("### 지도 설정 및 환경 관리")
st.markdown("###### 지도 페이지에서도 설정할 수 있습니다")

col1, col2, col3 = st.columns([2.5, 3, 1])
col1.markdown("**Name**")
col2.markdown("**Description**")
col3.markdown("**Setting**")
st.markdown("<hr/>", unsafe_allow_html=True)

real_toggle_show = st.toggle(
    "show_disabled_real",
    value=st.session_state.show_disabled,
    key="show_disabled_real",
    label_visibility="collapsed"
)
st.session_state.show_disabled = real_toggle_show

st.markdown(f"""
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
        {render_toggle(real_toggle_show)}
    </div>
</div>
""", unsafe_allow_html=True)

real_toggle_auto = st.toggle(
    "auto_detect_real",
    value=st.session_state.auto_detect,
    key="auto_detect_real",
    label_visibility="collapsed"
)
st.session_state.auto_detect = real_toggle_auto

st.markdown(f"""
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
        {render_toggle(real_toggle_auto)}
    </div>
</div>
""", unsafe_allow_html=True)

districts = ["남구 대연동", "남구 감만동", "남구 용호동", "남구 우암동", "남구 문현동"]

selected_center = st.selectbox(
    "기본 지도 위치",
    districts,
    index=districts.index(st.session_state.map_center_loc),
    key="map_center_loc_select",
    label_visibility="collapsed"
)
st.session_state.map_center_loc = selected_center

st.markdown(f"""
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
        {render_pill(selected_center, "#E7E1FF")}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
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
""", unsafe_allow_html=True)

st.markdown(f"""
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
""", unsafe_allow_html=True)
