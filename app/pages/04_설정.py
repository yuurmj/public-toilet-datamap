import streamlit as st
from datetime import date

# 1) 페이지 기본 설정
st.set_page_config(page_title="설정", layout="wide")

# 토글 UI
def render_toggle(is_on: bool) -> str:
    """글자가 동그라미 안에 들어가는 알약형 토글 (고정형 UI)"""
    if is_on:
        outer_bg = "#F0E7FF"   # 연한 보라
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

    # ⚠️ 주석(<!-- -->)은 빼고 깔끔하게 두는 게 안전해
    return f"""
    <div style="
        position:relative;
        width:80px;
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




# 표 형태 레이아웃 틀 만들기 (Name / Description / Setting)
# 표 전체를 하나의 컨테이너로
table = st.container()

with table:
    # 헤더 행
    c1, c2, c3 = st.columns([2, 3, 2])

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
    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**계정 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Account Settings</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "장애인 화장실 표시 여부  \n"
            "<span style='color:#909090; font-size:13px;'>Show accessible toilets</span>",
            unsafe_allow_html=True,
        )

    with c3:
        html = render_toggle(True)
        st.markdown(render_toggle(True), unsafe_allow_html=True)



#지도/위치 – 현재 위치 자동 감지 여부
    st.markdown("")  # 행 사이 여백

    # 지도/위치 설정 – 현재 위치 자동 감지 여부
    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**지도/위치 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Map & Location</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "현재 위치 자동 감지 여부  \n"
            "<span style='color:#909090; font-size:13px;'>Auto-detect Current Location</span>",
            unsafe_allow_html=True,
        )

    with c3:
        html = render_toggle(False)
        st.markdown(render_toggle(False), unsafe_allow_html=True)



# 기본 지도 위치
    # 기본 지도 위치 (보라색 배지)
    st.markdown("")

    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**지도/위치 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Map & Location</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "기본 지도 위치  \n"
            "<span style='color:#909090; font-size:13px;'>Default Map Center</span>",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div style='padding:6px 14px; 
                        border-radius:999px; 
                        background-color:#E7E1FF; 
                        font-weight:350; 
                        display:inline-block;'>
                남구 대연동
            </div>
            """,
            unsafe_allow_html=True,
        )




# 검색 & 필터 – 가까운 화장실 개수 기본값
    st.markdown("")

    # ④ 검색 & 필터 설정
    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**검색 & 필터 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Search & Filters</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "가까운 화장실 개수 기본값  \n"
            "<span style='color:#909090; font-size:13px;'>Default Number of Nearby Toilets</span>",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div style='padding:6px 16px; 
                        border-radius:999px; 
                        background-color:#D6F3E7;
                        color:#31333F;
                        font-weight:350;
                        display:inline-block;
                        text-align:center;'>
                5개
            </div>
            """,
            unsafe_allow_html=True,
        )



# 데이터 & 언어 – 데이터 최신 업데이트일 확인
    st.markdown("")

    # ⑤ 데이터 & 언어 – 데이터 최신 업데이트일
    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**데이터 & 언어 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Data & Language</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "데이터 최신 업데이트일 확인  \n"
            "<span style='color:#909090; font-size:13px;'>Last Data Update</span>",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div style='padding:6px 16px; 
                        border-radius:999px; 
                        background-color:#E7E1FF; 
                        color:#31333F;
                        font-weight:350;
                        display:inline-block;
                        text-align:center;'>
                2025.10.03
            </div>
            """,
            unsafe_allow_html=True,
        )




# 데이터 & 언어 – 언어 선택 (한국어만 가능)
    st.markdown("")

    # ⑥ 데이터 & 언어 – 언어 선택
    c1, c2, c3 = st.columns([2, 3, 2])

    with c1:
        st.markdown(
            "**데이터 & 언어 설정**  \n"
            "<span style='color:#909090; font-size:13px;'>Data & Language</span>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "언어 선택(한국어/영어)  \n"
            "<span style='color:#909090; font-size:13px;'>Language Selection (Korean / English)</span>",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div style='padding:6px 16px; 
                        border-radius:999px; 
                        background-color:#D6F3E7;
                        color:#31333F;
                        font-weight:350;
                        display:inline-block;
                        text-align:center;'>
                한국어
            </div>
            """,
            unsafe_allow_html=True,
        )
