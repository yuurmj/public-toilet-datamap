import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import plotly.express as px
from scipy.stats import zscore

st.set_page_config(page_title="공공화장실 대시보드", layout="wide")

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

st.sidebar.header("필터")
districts = ["전체"] + sorted(agg["district"].dropna().unique().tolist())
sel_district = st.sidebar.selectbox("구 선택", districts, index=0)
dongs = ["전체"]
if sel_district != "전체":
    dongs += sorted(agg.query("district == @sel_district")["dong"].dropna().unique().tolist())
else:
    dongs += sorted(agg["dong"].dropna().unique().tolist())
sel_dong = st.sidebar.selectbox("행정동 선택", dongs, index=0)
need_accessible = st.sidebar.selectbox("장애인 화장실", ["전체","있음(1)","없음(0)"], index=0)
k = st.sidebar.slider("가까운 화장실 개수(N)", 3, 20, 5)

DEFAULT_CENTER = (35.133, 129.100)
st.info("지도에서 원하는 위치를 한 번 클릭하면, 해당 좌표 기준으로 최근접 화장실을 계산합니다.")

filtered = toilets.copy()
if sel_district != "전체":
    filtered = filtered[filtered["district"] == sel_district]
if sel_dong != "전체":
    filtered = filtered[filtered["dong"] == sel_dong]
if need_accessible != "전체":
    filtered = filtered[filtered["accessible"] == int(need_accessible.endswith("1)"))]

m = folium.Map(location=DEFAULT_CENTER, zoom_start=13, control_scale=True, tiles="cartodbpositron")
for _, r in filtered.iterrows():
    popup_html = f"""
    <b>{r['name']}</b><br>
    주소: {r['addr']}<br>
    구/동: {r['district']} / {r['dong']}<br>
    장애인 화장실: {'예' if r['accessible']==1 else '아니오'}<br>
    남녀 분리: {'예' if r['gender_sep']==1 else '아니오'}<br>
    운영시간: {r['open_time']}
    """
    icon = folium.Icon(color="green" if r["accessible"]==1 else "blue", icon="info-sign")
    folium.Marker(location=(r["lat"], r["lng"]), popup=popup_html, tooltip=r["name"], icon=icon).add_to(m)

st.subheader("지도")
map_state = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
clicked = map_state.get("last_clicked")
current_loc = (clicked["lat"], clicked["lng"]) if clicked else DEFAULT_CENTER
st.caption(f"현재 기준 좌표: {current_loc[0]:.5f}, {current_loc[1]:.5f}")

def get_nearest(df, center, n):
    if len(df)==0:
        return df
    df = df.copy()
    df["distance_km"] = df.apply(lambda r: geodesic(center, (r["lat"], r["lng"])).km, axis=1)
    return df.sort_values("distance_km").head(n)

nearest_df = get_nearest(filtered, current_loc, k)

st.markdown("### 내 주변 최근접 화장실")
st.dataframe(nearest_df[["name","addr","district","dong","accessible","open_time","distance_km"]].reset_index(drop=True))

st.markdown("## 분석 차트")
if len(agg)>0:
    if sel_district != "전체":
        chart_df = agg.query("district == @sel_district").copy()
    else:
        chart_df = agg.copy()
    chart_df["label"] = chart_df["district"] + " " + chart_df["dong"]
    fig1 = px.bar(chart_df.sort_values("toilets_count", ascending=False), x="label", y="toilets_count", title="행정동별 화장실 수")
    fig1.update_layout(xaxis_title=None, yaxis_title="개수")
    st.plotly_chart(fig1, use_container_width=True)

rank_df = agg.dropna(subset=["toilets_per_1k"]).copy()
top5 = rank_df.sort_values("toilets_per_1k", ascending=False).head(5)
low5 = rank_df.sort_values("toilets_per_1k", ascending=True).head(5)
c1, c2 = st.columns(2)
with c1:
    fig2 = px.bar(top5, x=top5["district"]+" "+top5["dong"], y="toilets_per_1k", title="TOP5 (인구 1천명당)")
    fig2.update_layout(xaxis_title=None, yaxis_title="개수/1천명")
    st.plotly_chart(fig2, use_container_width=True)
with c2:
    fig3 = px.bar(low5, x=low5["district"]+" "+low5["dong"], y="toilets_per_1k", title="LOW5 (인구 1천명당)")
    fig3.update_layout(xaxis_title=None, yaxis_title="개수/1천명")
    st.plotly_chart(fig3, use_container_width=True)

sel = agg.copy()
if sel_district != "전체":
    sel = sel[sel["district"]==sel_district]
if sel_dong != "전체":
    sel = sel[sel["dong"]==sel_dong]
if len(sel)>0:
    tot = sel["toilets_count"].sum()
    acc = sel["accessible_count"].sum()
    pie_df = pd.DataFrame({"type":["장애인 화장실","일반"], "count":[acc, max(tot-acc,0)]})
    fig4 = px.pie(pie_df, names="type", values="count", title="장애인 화장실 비율")
    st.plotly_chart(fig4, use_container_width=True)

if len(agg)>0:
    th = agg["gap_score"].quantile(0.8)
    shortage = agg[agg["gap_score"]>=th].sort_values("gap_score", ascending=False)
    st.markdown("### 상위 20% 부족 지역 (Gap Score 기준)")
    st.dataframe(shortage[["district","dong","population","toilets_count","toilets_per_1k","gap_score"]].reset_index(drop=True))
