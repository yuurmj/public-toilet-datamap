<div align="center">
  <h1>🚽 공공화장실 데이터맵 - Public Toilet Datamap 🚽</h1>
  <h3>공공데이터 통합 시각화 및 머신러닝을 활용한 화장실 부족 지역 예측 서비스</h3>
</div>

<br>
<br>

## 📌 프로젝트 개요
**공공화장실 데이터 맵**은 주변의 **공공화장실 위치**를 직관적으로 확인할 수 있는 서비스입니다.<br>
공공데이터포털의 위치 데이터를 활용하여 지도 API와의 연동을 통해 사용자가 **가장 가까운 화장실**을 쉽게 찾을 수 있습니다.<br>

## ✨ 주요 기능

### 1. 데이터 수집 및 전처리
- 공공데이터포털 CSV 기반 데이터 수집 
- 기본 항목: 시설명, 주소, 위경도, 화장실 개수, 장애인 화장실 여부
- 데이터 정제 및 좌표 변환, DB 테이블 구축

### 2. 공공화장실 현황 분석
- 총 화장실 수, 행정동별 분포, 인구 대비 화장실 수 산출
- 장애인 화장실 접근성 및 부족 지역 분석
- 지역 간 불균형 분석
- 설치 연도별 추세 및 변화 분석
   
### 3. 시각화 기능
- 지도 기반 시각화 : Folium + Streamlit
  - 마커 및 클러스터 표시, 접근성 지표 색상 차별화
  - 팝업/툴팁으로 상세 정보 제공
- 차트/그래프 분석 : Matplotlib, Seaborn, Plotly 활용
  - 행정동별 분포, 비율, 랭킹 비교
  
### 4. 대시보드 제공
- Streamlit 기반 통합 대시보드
- 내 주변 화장실 검색
- 지도/차트/테이블/랭킹 비교 시각화
- 머신러닝 예측 결과 카드 & 지도 오버레이 표시

### 5. 머신러닝 예측 기능
- 화장실 부족 지역 vs 적정 지역 분류 모델
- 인구/유동인구 대비 화장실 수 기반 부족 지역 예측
- Streamlit 대시보드와 연동해 확률 기반 시각화 제공

## 💻 실행 방법 

이 프로젝트는 **Python 3.9 이상** 환경에서 실행하는 것을 권장합니다.

### 1. 저장소 클론
```bash
git clone [https://github.com/your-repo/public-toilet-datamap.git](https://github.com/your-repo/public-toilet-datamap.git)
cd public-toilet-datamap
```

### 2. 패키지 설치

```bash
pip install streamlit pandas numpy folium streamlit-folium streamlit-js-eval
```

### 3. 애플리케이션 실행

```bash
streamlit run app/HOME.py
```

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
