import streamlit as st
from textwrap import dedent

st.set_page_config(page_title="소개", layout="wide")

st.markdown(
    """
<style>
/* 기본 레이아웃/배경 */
.block-container {
    padding-top: 0rem !important;
}
header[data-testid="stHeader"] { display:none !important; }
#MainMenu { display:none !important; }
footer { display:none !important; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main { 
    background-color: #FAFAFB !important;  
}

/* 카드 공통 */
.setting-card {  
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 22px 26px;
    margin: 10px 0 18px 0;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
    height: 240px;
    display: flex;
    flex-direction: column;
}

/* 상단 소개 카드 */
.intro-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 26px 32px;
    margin-top: 24px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06);
}

/* 제목 가운데 정렬 */
.card-title-center {
    display:flex;
    justify-content:center;
    align-items:center;
    font-weight:700;
    font-size:22px;
    margin-bottom:12px;
}

/* 팀 소개 내부 레이아웃 */
.team-layout {
    margin-top:7px;           /* 제목과 내용 사이 간격 */
    font-weight:700;
    font-size:22px;
}

/* 오른쪽 이름 리스트 */
.team-layout ul {
    margin:0;
    padding-left:0.2rem;
    font-size:16px;
    line-height:2.65;
}
</style>
""",
    unsafe_allow_html=True,
)

TEAM_CARD_HTML = dedent("""
<div class="setting-card">
  <div class="card-title-center" style="display:flex; align-items:center; gap:8px;">
    <img src="https://img.icons8.com/?size=100&id=52966&format=png&color=000000"
         style="width:26px; height:26px;" />
    <span style="font-weight:700; font-size:25px;">팀 소개</span>
  </div>

  <div class="team-layout"
       style="display:flex; align-items:flex-start; gap:25px; margin-left:120px; 
              font-size:30px; font-weight: 900; line-height:1.55;">
    <div style="font-weight:700; color:#8FDAC8;">
      <div>아</div>
      <div>희</div>
      <div>유</div>
    </div>
    <ul style="margin:0; color:#5a5a5a;">
      <li><a href="https://github.com/aranlll" target="_blank">정아란</a> (커미터)</li>
      <li><a href="https://github.com/seohuiwon11" target="_blank">서희원</a> (메인테이너)</li>
      <li><a href="https://github.com/yuurmj" target="_blank">정유림</a> (리더)</li>
    </ul>

  </div>
</div>
""")


st.markdown(
    """
<div class="intro-card">
  <div style="font-size:33px; font-weight:700; margin-bottom:3px;">
    공중화장실 데이터맵 소개
  </div>
  <div style="font-size:20px; margin-top:8px;">
  <span style="font-weight:700; color:#8FDAC8;">내 근처의 화장실 위치</span>
  부터
  <span style="font-weight:700; color:#8FDAC8;">머신러닝을 이용한 예측, 분석, 통계</span>
  까지 데이터를 연결하는 시민 편의 플랫폼
</div>
</div>
""",
    unsafe_allow_html=True,
)


c1, c2 = st.columns(2)

with c1:
    st.markdown(TEAM_CARD_HTML, unsafe_allow_html=True)

with c2:
    st.markdown(
        """
        <div class="setting-card">
          <div class="card-title-center">
            <img src="https://img.icons8.com/?size=100&id=43657&format=png&color=000000"
                 style="width:28px; margin-right:8px;" />
            <span style="font-weight:700; font-size:25px;">기술 스택</span>
          </div>

          <!-- 아이콘 + 카테고리 -->
          <div style="display:flex; justify-content:space-between; text-align:center; margin-top:12px;">
              <div style="flex:1;">
                <div style="font-size:17px; font-weight:600; color:#5a5a5a; margin-bottom:25px;">Programming</div>
                <img src="https://img.icons8.com/?size=100&id=101379&format=png&color=8FDAC8"
                     style="width:32px;" />
              </div>
              <div style="flex:1;">
                <div style="font-size:17px; font-weight:600; color:#5a5a5a; margin-bottom:25px;">Collaboration</div>
                <img src="https://img.icons8.com/?size=100&id=62856&format=png&color=8FDAC8"
                     style="width:32px;" />
              </div>
              <div style="flex:1;">
                <div style="font-size:17px; font-weight:600; color:#5a5a5a; margin-bottom:25px;">Design</div>
                <img src="https://img.icons8.com/?size=100&id=59822&format=png&color=8FDAC8"
                     style="width:32px;" />
              </div>
              <div style="flex:1;">
                <div style="font-size:17px; font-weight:600; color:#5a5a5a; margin-bottom:25px;">Docs / PM</div>
                <img src="https://img.icons8.com/?size=100&id=23265&format=png&color=8FDAC8"
                     style="width:32px;" />
              </div>
          </div>
          <!-- 기술 항목 -->
          <div style="
                display:flex; 
                justify-content:space-between; 
                text-align:center;
                margin-top:8px;
                font-size:22px;
                font-weight:700;
                color:#333;">
              <div style="flex:1;">PYTHON</div>
              <div style="flex:1;">GITHUB</div>
              <div style="flex:1;">FIGMA</div>
              <div style="flex:1;">NOTION</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




c3, c4 = st.columns(2)

with c3:
    st.markdown(
        """
        <div class="setting-card">
          <div class="card-title-center">
            <img src="https://img.icons8.com/?size=100&id=5ZDqqbvHOkKs&format=png&color=000000"
                 style="width:28px; margin-right:8px;" />
            <span style="font-weight:700; font-size:25px;">데이터 출처</span>
          </div>

          <div class="card-body">
            <ul style="margin:0 0 0 1.1rem;">
              <li>전국 공중 화장실 표준 데이터</li>
              <li>Big-데이터웨이브</li>
              <li>부산 남구 자원 순환 포털 등</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="setting-card">
          <div class="card-title-center">
            <img src="https://img.icons8.com/?size=100&id=52536&format=png&color=000000"
                 style="width:28px; margin-right:8px;" />
            <span style="font-weight:700; font-size:25px;">향후 계획</span>
          </div>

          <div class="card-body">
            <ol style="margin:0 0 0 1.1rem;">
              <li>시민 참여형 제보 기능 추가</li>
              <li>화면·음성 안내 등 장애인 맞춤 기능 강화</li>
              <li>위치 및 혼잡 예측 서비스</li>
              <li>시뮬레이션 기반 설비 개선</li>
            </ol>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
