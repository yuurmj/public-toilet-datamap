import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="공공화장실 데이터맵 | 지도", layout="wide")

# 상태값
if "selected_toilet" not in st.session_state:
    st.session_state.selected_toilet = None

# 전역 레이아웃/모달/표/마커 hover 스타일
st.markdown("""
<style>
/* 레이아웃 */
html, body, #root, .stApp, [data-testid="stAppViewContainer"] {
  height: 100vh !important; overflow: hidden !important; background: #F4F5FB !important;
}
header[data-testid="stHeader"] { display:none !important; }
.block-container, [data-testid="stAppViewContainer"] .main { padding:0 !important; margin:0 !important; }

/* dialog 높이 자동 */
[data-testid="stDialog"] > div, [data-testid="stDialog"] > div > div, [data-testid="stDialog"] > div > div > div{
  height:auto !important; max-height:none !important; min-height:0 !important; overflow:visible !important;
}
/* 오버레이 투명 */
section[data-testid="stDialog"] { background:transparent !important; }
section[data-testid="stDialog"] > div:first-child { background:transparent !important; }

/* dialog 컨테이너(위치만) */
[data-testid="stDialog"] > div{
  position:fixed !important; top:56px !important; right:56px !important; left:auto !important;
  background:transparent !important; box-shadow:none !important; padding:0 !important; width:auto !important; z-index:9999 !important;
}
/* 카드 */
[data-testid="stDialog"] > div > div{
  position:relative !important; width:clamp(600px, 44vw, 720px) !important;
  border-radius:24px !important; background:#fff !important; box-shadow:0 24px 60px rgba(25,32,56,.25) !important;
}
/* 내용 패딩 */
[data-testid="stDialog"] > div > div [data-testid="stVerticalBlock"]{ padding:8px 32px 24px !important; gap:0 !important; }
/* 닫기 버튼 */
[data-testid="stDialog"] button[aria-label="Close"]{
  position:absolute !important; top:14px !important; right:14px !important;
  background:#fff !important; border-radius:999px !important; width:28px !important; height:28px !important;
  color:#111827 !important; box-shadow:none !important;
}

/* 제목/배지/필드 */
.card-title{ font-size:32px !important; line-height:1.35 !important; letter-spacing:-0.01em !important;
  font-weight:900 !important; color:#111827 !important; margin:0 0 10px 0 !important; padding:0 0 10px 0 !important; }
.badge-row{ display:flex !important; gap:16px !important; margin:10px 0 23px 0 !important; padding:10px 0 23px 0 !important; }
.badge{ font-size:12px !important; padding:7px 12px !important; border-radius:999px !important;
  background:#F3F4FF !important; color:#4F46E5 !important; font-weight:600 !important; }
.badge.gray{ background:#F3F4F6 !important; color:#4B5563 !important; }
.grid-2{ display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:20px; }
.field-full{ margin-bottom:20px; }
.info-label{ font-size:13px; color:#111827; margin-bottom:10px; font-weight:500; }
.info-value{ display:flex; align-items:center; min-height:46px; padding:12px 14px; font-size:13px; font-weight:500; color:#111827;
  background:#F9FAFB; border:1px solid #E5E7EB; border-radius:10px; }

/* 표 */
.detail-section-title{ margin:18px 0 10px 0; font-size:13px; font-weight:500; color:#111827; }
.table-wrap{ border:1px solid #E5E7EB; border-radius:12px; overflow:hidden; background:#fff; }
.detail-table{ width:100%; border-collapse:separate; border-spacing:0; font-size:13px; }
.detail-table thead th{ background:#F8FAFC; color:#6B7280; font-weight:700; text-align:left; padding:12px 14px; border-bottom:1px solid #E5E7EB; }
.detail-table tbody td{ color:#111827; padding:12px 14px; border-top:1px solid #F1F5F9; vertical-align:middle; }
.detail-table tbody tr:nth-child(even) td{ background:#FCFDFE; }
.detail-table td.num, .detail-table th.num{ text-align:center; width:88px; }

/* 마커 hover 효과 */
.leaflet-container path.leaflet-interactive{ transition: filter .12s ease; cursor: pointer; }
.leaflet-container path.leaflet-interactive:hover{ filter: drop-shadow(0 0 8px rgba(168,85,247,.6)); }
</style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_toilets():
    df = pd.read_csv("data/toilets_mock.csv")
    need = ["toilet_id","name","addr","lat","lng","district","dong","accessible","gender_sep",
            "open_time","male_wc","female_wc","male_wc_disabled","female_wc_disabled"]
    for c in need:
        if c not in df.columns:
            df[c] = np.nan
    df["accessible"] = df["accessible"].fillna(0).astype(int)
    df["gender_sep"] = df["gender_sep"].fillna(0).astype(int)
    for c in ["male_wc","female_wc","male_wc_disabled","female_wc_disabled"]:
        df[c] = df[c].fillna(0).astype(int)
    df = df.dropna(subset=["lat","lng"])
    return df

toilets = load_toilets()

# 모달 그리기
@st.dialog(" ", width="large")
def show_toilet_modal(row: pd.Series):
    title = row["name"]
    accessible_txt = "장애인 화장실 있음" if row["accessible"] == 1 else "장애인 화장실 없음"
    gender_txt = "남녀 분리" if row["gender_sep"] == 1 else "공용"
    badge_class = "" if row["accessible"] == 1 else "gray"
    latlon = f"{row['lat']:.5f}, {row['lng']:.5f}"
    open_time = row.get("open_time", "정보 없음")

    st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="badge-row"><span class="badge {badge_class}">{accessible_txt}</span>'
        f'<span class="badge gray">{gender_txt}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'''
        <div class="grid-2">
          <div class="field">
            <div class="info-label">행정동</div>
            <div class="info-value">{row["district"]} {row["dong"]}</div>
          </div>
          <div class="field">
            <div class="info-label">좌표 (lat, lon)</div>
            <div class="info-value">{latlon}</div>
          </div>
        </div>
        <div class="field-full">
          <div class="info-label">주소</div>
          <div class="info-value">{row["addr"]}</div>
        </div>
        <div class="grid-2">
          <div class="field">
            <div class="info-label">운영 시간</div>
            <div class="info-value">{open_time}</div>
          </div>
          <div class="field">
            <div class="info-label">비고</div>
            <div class="info-value">&nbsp;</div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    table_html = f"""
    <div class="detail-section-title">변기 구성</div>
    <div class="table-wrap">
      <table class="detail-table">
        <thead>
          <tr><th>구분</th><th class="num">개수</th><th>구분</th><th class="num">개수</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>남자 변기 수</td><td class="num">{int(row["male_wc"])}</td>
            <td>여자 변기 수</td><td class="num">{int(row["female_wc"])}</td>
          </tr>
          <tr>
            <td>남자 장애인 변기 수</td><td class="num">{int(row["male_wc_disabled"])}</td>
            <td>여자 장애인 변기 수</td><td class="num">{int(row["female_wc_disabled"])}</td>
          </tr>
        </tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# 지도 생성
DEFAULT_CENTER = (35.1300, 129.0900)
m = folium.Map(location=DEFAULT_CENTER, zoom_start=13, tiles="cartodbpositron", control_scale=True)

# 마커(툴팁은 hover/click 식별용)
for _, r in toilets.iterrows():
    cm = folium.CircleMarker(
        location=(r["lat"], r["lng"]),
        radius=6, color="#A855F7", fill=True, fill_color="#A855F7", fill_opacity=0.85
    ).add_to(m)
    folium.Tooltip(r["name"], sticky=True, direction="top", opacity=0.9).add_to(cm)

# 지도 호스트
st.markdown('<div id="map-anchor"></div>', unsafe_allow_html=True)

# 지도 렌더링(클릭 좌표 + 클릭한 마커의 툴팁 텍스트 반환)
map_state = st_folium(
    m,
    height=900,
    width=None,
    use_container_width=True,
    returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
    key="folium_map",
)

# 고정 배치
st.markdown("""
<script>
(function(){
  function fit(){
    const anchor = document.getElementById('map-anchor');
    if(!anchor) return;
    const box = anchor.parentElement;
    const sb = document.querySelector('section[data-testid="stSidebar"]')
             || document.querySelector('aside[data-testid="stSidebar"]');
    const left = sb ? sb.getBoundingClientRect().width : 0;
    Object.assign(box.style, {
      position:'fixed', top:'0', right:'0', bottom:'0', left: left + 'px',
      height:'100vh', width:'auto', margin:'0', padding:'0', zIndex: 1, background:'transparent'
    });
    const iframe = box.querySelector('iframe');
    if (iframe){ iframe.style.width='100%'; iframe.style.height='100%'; iframe.style.display='block'; }
  }
  new ResizeObserver(fit).observe(document.body);
  window.addEventListener('load', fit, { once: true });
  setTimeout(fit, 0);
})();
</script>
""", unsafe_allow_html=True)

# 클릭 → 모달 열기 (동일 마커 재클릭도 항상 열리도록 좌표 클릭 우선 사용)
CLICK_DEG_THRESHOLD = 0.0012  # 약 130m

clicked = map_state.get("last_object_clicked")
clicked_name = map_state.get("last_object_clicked_tooltip")

# 좌표 클릭이 있으면 최근접 매칭
if clicked and len(toilets) > 0:
    lat, lng = clicked.get("lat"), clicked.get("lng")
    if lat is not None and lng is not None:
        dist = np.sqrt((toilets["lat"] - lat)**2 + (toilets["lng"] - lng)**2)
        idx = dist.idxmin()
        if dist.loc[idx] < CLICK_DEG_THRESHOLD:
            st.session_state.selected_toilet = toilets.loc[idx]

# 좌표 클릭이 없고, 툴팁 텍스트만 온 경우(모바일 등) 이름으로 매칭
if st.session_state.selected_toilet is None and clicked_name:
    row = toilets.loc[toilets["name"] == clicked_name]
    if not row.empty:
        st.session_state.selected_toilet = row.iloc[0]

# 모달 표시 (닫으면 rerun되고 다음 클릭에서 다시 열림)
if st.session_state.selected_toilet is not None:
    show_toilet_modal(st.session_state.selected_toilet)
    st.session_state.selected_toilet = None