# <div align=center>:gem:public-toilet-datamap:gem:</div>

  </h1>
  <h3><div align=center>:toilet:내 주변의 공공화장실 찾기:toilet:</div>
</h3>
</div>

<br><br>

<div align=center>
![alt text](image.png)

## 📌 프로젝트 개요

공공화장실 데이터 맵은 **주변의 공공화장실 위치를 직관적으로 확인**할 수 있는 서비스입니다.  
공공데이터포털의 위치 데이터를 활용하고, 지도 API와 연동하여 사용자가 **가장 가까운 화장실을 쉽게 찾고**,  
향후에는 **혼잡도 예측 및 경로 안내 기능**도 제공할 예정입니다.

---

## ✨ 주요 기능

- **1. 데이터 수집 및 전처리**

  - 공공데이터포털 CSV 기반 데이터 수집 (화장실 정보, 인구, 유동인구 등)
  - 기본 항목: 시설명, 주소, 위경도, 화장실 개수, 장애인 화장실 여부
  - 추가 항목: 어린이 화장실, 개방 시간, 기저귀 교환대 등
  - 데이터 정제 및 좌표 변환, DB 테이블 구축

- **2. 공공화장실 현황 분석**

  - 총 화장실 수, 행정동별 분포, 인구 대비 화장실 수 산출
  - 장애인 화장실 접근성 및 부족 지역 분석
  - 지역 간 불균형 분석 (TOP5/LOW5, Gap Score 등)
  - 설치 연도별 추세 및 변화 분석

- **3. 시각화 기능**

  - **지도 기반 시각화**: Folium + Streamlit
    - 마커 및 클러스터 표시, 접근성 지표 색상 차별화
    - 팝업/툴팁으로 상세 정보 제공
  - **차트/그래프 분석**: Matplotlib, Seaborn, Plotly 활용
    - 행정동별 분포, 비율, 랭킹 비교

- **4. 대시보드 제공**

  - Streamlit 기반 통합 대시보드
  - 내 주변 화장실 검색 (위치 자동 감지 + 거리 계산)
  - 지도/차트/테이블/랭킹 비교 시각화
  - 머신러닝 예측 결과 카드 & 지도 오버레이 표시

- **5. 머신러닝 예측 기능 (추가 예정)**
  - 화장실 부족 지역 vs 적정 지역 분류 모델
  - 인구/유동인구 대비 화장실 수 기반 부족 지역 예측
  - Streamlit 대시보드와 연동해 확률 기반 시각화 제공
  </div>

## 👋 Team Members

<table align="center">
  <tr>
    <td align="center" width="180">
      <a href="https://github.com/yuurmj">
        <img src="https://github.com/yuurmj.png?size=140" alt="yuurmj avatar" width="140" />
        <div><sub><b>정유림</b></sub></div>
      </a>
    </td>
    <td align="center" width="180">
      <a href="https://github.com/seohuiwon11">
        <img src="https://github.com/seohuiwon11.png?size=140" alt="seohuiwon11 avatar" width="140" />
        <div><sub><b>서희원</b></sub></div>
      </a>
    </td>
     <td align="center" width="180">
      <a href="https://github.com/USER3">
        <img src="https://github.com/aranlll.png?size=140" alt="aranlll avatar" width="140" />
        <div><sub><b>정아란</b></sub></div>
      </a>
    </td>
  </tr>
</table>
