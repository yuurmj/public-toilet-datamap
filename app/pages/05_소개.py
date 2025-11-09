import streamlit as st

st.set_page_config(page_title="소개", page_icon="ℹ️", layout="wide")

# 스타일
st.markdown("""
<style>
.main { background:#f8f9fd; }
h1,h2,h3,h4 { color:#243269 !important; }
.block-card {
  border:1px solid #e5e7eb; border-radius:16px;
  background:rgba(255,255,255,.92); backdrop-filter: blur(6px);
  box-shadow:0 2px 8px rgba(15,23,42,.06);
  padding:18px 20px; margin-bottom:16px;
}
</style>
""", unsafe_allow_html=True)

# 상단 인트로
st.markdown("## 공중화장실 데이터맵 소개")
st.write("데이터로 연결하는 **시민 편의 플랫폼**")
st.info("공중화장실 설치 효율성을 높이기 위한 데이터 기반 분석 플랫폼입니다.")

# 카드형 섹션 4개
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 팀 소개")
    st.markdown(
        """
        <div class="block-card">
          <ul style="margin:0 0 0 1rem">
            <li>정아란 : 커미터</li>
            <li>서희원 : 메인테이너</li>
            <li>정유림 : 리더</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

with c2:
    st.markdown("#### 기술 스택")
    st.markdown(
        """
        <div class="block-card">
          <ul style="margin:0 0 0 1rem">
            <li>PYTHON</li>
            <li>GIT HUB</li>
            <li>FIGMA</li>
            <li>NOTION</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

c3, c4 = st.columns(2)

with c3:
    st.markdown("#### 데이터 출처")
    st.markdown(
        """
        <div class="block-card">
          <ul style="margin:0 0 0 1rem">
            <li>전국 공중 화장실 표준 데이터</li>
            <li>Big-데이터웨이브</li>
            <li>부산 남구 자원 순환 포털 등</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

with c4:
    st.markdown("#### 향후 계획")
    st.markdown(
        """
        <div class="block-card">
          1) 시민 참여형 제보 기능 추가<br/>
          2) 화면·음성 안내 등 장애인 맞춤 기능 강화<br/>
          3) 위치 및 혼잡 예측 서비스<br/>
          4) 시뮬레이션 기반 설비 개선
        </div>
        """, unsafe_allow_html=True
    )
