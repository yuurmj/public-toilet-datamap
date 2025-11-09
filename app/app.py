import streamlit as st

st.set_page_config(
    page_title="공중화장실 데이터맵",
    page_icon="🚻",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("## 🚻 공중화장실 데이터맵")
    st.caption("데이터로 연결하는 시민 편의 플랫폼")
    st.divider()
    st.page_link("pages/05_소개.py", label="소개")  
    # st.page_link("pages/01_분석.py", label="분석", disabled=True)  
    st.page_link("pages/02_지도.py", label="지도")
    # st.page_link("pages/03_예측.py", label="예측", disabled=True)
    # st.page_link("pages/90_설정.py", label="설정", disabled=True)
    st.divider()

# 홈 본문
st.title("공중화장실 데이터맵")
st.write("좌측 **사이드바**에서 페이지를 선택하세요. (소개/지도 등)")
