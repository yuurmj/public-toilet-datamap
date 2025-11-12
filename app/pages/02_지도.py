import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import plotly.express as px
from scipy.stats import zscore

st.set_page_config(page_title="공공화장실 데이터맵", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fd;
    }
    .stSidebar {
        background-color: #ffffff;
    }
    .css-1d391kg, .css-12oz5g7 {
        background-color: #ffffff !important;
    }
    h1, h2, h3, h4 {
        color: #243269 !important;
    }
    .stButton>button {
        background-color: #4A6CF7;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #3957d1;
        color: #ffffff;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    toilets = pd.read_csv("data/toilets_mock.csv")
    pop = pd.read_csv("data/population_mock.csv")
    needed_cols = ["toilet_id","name","addr","lat","lng","district","dong","accessible","gender_sep","open_time","updated_at"]
    for c in needed_cols:
        if c not in toilets.columns:
            toilets[c] = np.nan
    toilets["accessible"] = toilets["accessible"].fillna(0).astype(int)
    toilets["gender_sep"] = toilets["gender_sep"].fillna(0).astype(int)
    toilets = toilets.dropna(subset=["lat","lng"])
    toilets["district"] = toilets["district"].fillna("미상")
    toilets["dong"] = toilets["dong"].fillna("미상")
    toilets_by_dong = toilets.groupby(["district","dong"], as_index=False).agg(
        toilets_count=("toilet_id","count"),
        accessible_count=("accessible","sum")
    )
    df = toilets_by_dong.merge(pop, on=["district","dong"], how="left")
    df["population"] = df["population"].fillna(0).astype(int)
    df["toilets_per_1k"] = np.where(df["population"]>0, df["toilets_count"]/(df["population"]/1000), np.nan)
    df["accessible_ratio"] = np.where(df["toilets_count"]>0, df["accessible_count"]/df["toilets_count"], np.nan)
    if df["population"].std(ddof=0) == 0 or df["toilets_count"].std(ddof=0) == 0:
        df["gap_score"] = 0.0
    else:
        df["gap_score"] = zscore(df["population"].astype(float), nan_policy='omit') - zscore(df["toilets_count"].astype(float), nan_policy='omit')
    df["rank_best"] = df["toilets_per_1k"].rank(ascending=False, method="dense")
    df["rank_worst"] = df["gap_score"].rank(ascending=False, method="dense")
    return toilets, df

toilets, agg = load_data()

with st.sidebar:
    st.markdown("### 🧭 공공화장실 데이터맵")
    st.markdown("---")
    st.markdown("**메뉴**")
    menu = st.radio("탭 선택", ["홈", "분석", "지도", "예측", "설정", "소개"], index=2)
    st.markdown("---")
    st.subheader("필터")
    districts = ["전체"] + sorted(agg["district"].dropna().unique().tolist())
    sel_district = st.selectbox("구 선택", districts, index=0)
    dongs = ["전체"]
    if sel_district != "전체":
        dongs += sorted(agg.query("district == @sel_district")["dong"].dropna().unique().tolist())
    else:
        dongs += sorted(agg["dong"].dropna().unique().tolist())
    sel_dong = st.selectbox("행정동 선택", dongs, index=0)
    need_accessible = st.selectbox("장애인 화장실", ["전체","있음(1)","없음(0)"], index=0)
    k = st.slider("가까운 화장실 개수(N)", 3, 20, 5)

st.title("🗺️ 지도 기반 공공화장실 현황")

DEFAULT_CENTER = (35.133, 129.100)
st.info("지도에서 원하는 위치를 클릭하면, 주변 최근접 화장실 정보를 확인할 수 있습니다.")

filtered = toilets.copy()
if sel_district != "전체":
    filtered = filtered[filtered["district"] == sel_district]
if sel_dong != "전체":
    filtered = filtered[filtered["dong"] == sel_dong]
if need_accessible != "전체":
    filtered = filtered[filtered["accessible"] == int(need_accessible.endswith("1)"))]

m = folium.Map(location=DEFAULT_CENTER, zoom_start=13, control_scale=True, tiles="cartodbpositron")
for _, r in filtered.iterrows():
    icon_color = "purple" if r["accessible"]==1 else "blue"
    popup_html = f"""
    <b style='color:#4A6CF7'>{r['name']}</b><br>
    주소: {r['addr']}<br>
    구/동: {r['district']} / {r['dong']}<br>
    장애인 화장실: {'예' if r['accessible']==1 else '아니오'}<br>
    남녀 분리: {'예' if r['gender_sep']==1 else '아니오'}<br>
    운영시간: {r['open_time']}
    """
    folium.Marker(location=(r["lat"], r["lng"]),
                  popup=popup_html,
                  tooltip=r["name"],
                  icon=folium.Icon(color=icon_color, icon="info-sign")).add_to(m)

col1, col2 = st.columns([2, 1])

with col1:
    map_state = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
    clicked = map_state.get("last_clicked")
    current_loc = (clicked["lat"], clicked["lng"]) if clicked else DEFAULT_CENTER
    st.caption(f"현재 기준 좌표: {current_loc[0]:.5f}, {current_loc[1]:.5f}")

with col2:
    st.subheader("📍 선택된 위치 정보")
    def get_nearest(df, center, n):
        if len(df)==0:
            return df
        df = df.copy()
        df["distance_km"] = df.apply(lambda r: geodesic(center, (r["lat"], r["lng"])).km, axis=1)
        return df.sort_values("distance_km").head(n)
    nearest_df = get_nearest(filtered, current_loc, k)
    if len(nearest_df) > 0:
        target = nearest_df.iloc[0]
        st.markdown(f"### **<span style='color:#4A6CF7'>{target['name']}</span>**", unsafe_allow_html=True)
        st.markdown(f"**주소:** {target['addr']}")
        st.markdown(f"**행정동:** {target['district']} {target['dong']}")
        st.markdown(f"**장애인 화장실:** {'✅ 있음' if target['accessible']==1 else '❌ 없음'}")
        st.markdown(f"**남녀 분리:** {'남/녀 분리' if target['gender_sep']==1 else '공용'}")
        st.markdown(f"**운영시간:** {target['open_time']}")
        st.markdown(f"**좌표:** {target['lat']:.5f}, {target['lng']:.5f}")
        st.divider()
        st.markdown("#### 주변 화장실 목록")
        st.dataframe(nearest_df[["name","addr","distance_km"]].reset_index(drop=True))
    else:
        st.warning("해당 구역 내 화장실 데이터가 없습니다.")

st.markdown("## 📊 행정동별 통계")

if len(agg)>0:
    if sel_district != "전체":
        chart_df = agg.query("district == @sel_district").copy()
    else:
        chart_df = agg.copy()
    chart_df["label"] = chart_df["district"] + " " + chart_df["dong"]
    fig1 = px.bar(chart_df.sort_values("toilets_count", ascending=False),
                  x="label", y="toilets_count",
                  title="행정동별 화장실 수",
                  color_discrete_sequence=["#4A6CF7"])
    fig1.update_layout(xaxis_title=None, yaxis_title="개수", template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

rank_df = agg.dropna(subset=["toilets_per_1k"]).copy()
top5 = rank_df.sort_values("toilets_per_1k", ascending=False).head(5)
low5 = rank_df.sort_values("toilets_per_1k", ascending=True).head(5)
c1, c2 = st.columns(2)
with c1:
    fig2 = px.bar(top5, x=top5["district"]+" "+top5["dong"], y="toilets_per_1k",
                  title="TOP5 (인구 1천명당)", color_discrete_sequence=["#6F83F7"])
    fig2.update_layout(xaxis_title=None, yaxis_title="개수/1천명", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
with c2:
    fig3 = px.bar(low5, x=low5["district"]+" "+low5["dong"], y="toilets_per_1k",
                  title="LOW5 (인구 1천명당)", color_discrete_sequence=["#A6B4F7"])
    fig3.update_layout(xaxis_title=None, yaxis_title="개수/1천명", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

if len(agg)>0:
    th = agg["gap_score"].quantile(0.8)
    shortage = agg[agg["gap_score"]>=th].sort_values("gap_score", ascending=False)
    st.markdown("### ⚠️ 상위 20% 부족 지역 (Gap Score 기준)")
    st.dataframe(shortage[["district","dong","population","toilets_count","toilets_per_1k","gap_score"]].reset_index(drop=True))
