import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestRegressor
import numpy as np

st.set_page_config(page_title="공중화장실 데이터맵", layout="wide")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "행정동": ["대연1동", "용호1동", "우암동", "문현1동"],
        "인구": [30000, 42000, 18000, 25000],
        "면적": [2.5, 3.1, 1.2, 2.0],
        "시설수": [8, 10, 5, 6],
        "장애인비율": [0.25, 0.35, 0.15, 0.20],
        "예측등급": ["부족", "적정", "과잉", "부족"],
        "권장설치수": [2, 0, 0, 1],
        "설치율": ["65%", "90%", "110%", "75%"],
        "인구대비화장실수": ["1/1800명", "2/1800명", "3/1800명", "1/1800명"]
    })

df = st.session_state.df

col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("### 예측 결과")
    st.markdown("<div style='display:flex;gap:15px;margin-bottom:15px;'>"
                "<span style='background:#93d7b0;width:14px;height:14px;border-radius:50%;display:inline-block;'></span> 부족"
                "&nbsp;&nbsp;&nbsp;"
                "<span style='background:#cfcfd3;width:14px;height:14px;border-radius:50%;display:inline-block;'></span> 적정"
                "&nbsp;&nbsp;&nbsp;"
                "<span style='background:#bfb8e8;width:14px;height:14px;border-radius:50%;display:inline-block;'></span> 과잉"
                "</div>", unsafe_allow_html=True)
    st.dataframe(df[["행정동","예측등급","권장설치수","설치율","인구대비화장실수"]],
                 use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 지도 결과")
    coords = {"대연1동": (35.13, 129.10), "용호1동": (35.12, 129.12),
              "우암동": (35.11, 129.09), "문현1동": (35.15, 129.07)}
    color_map = {"부족": "#93d7b0", "적정": "#cfcfd3", "과잉": "#bfb8e8"}
    m = folium.Map(location=[35.13, 129.10], zoom_start=13, tiles="cartodb positron")
    for _, r in df.iterrows():
        folium.CircleMarker(location=coords[r["행정동"]],
                            radius=25, color=color_map[r["예측등급"]],
                            fill=True, fill_color=color_map[r["예측등급"]],
                            fill_opacity=0.9,
                            popup=f"{r['행정동']} ({r['예측등급']})").add_to(m)
    st_folium(m, width=500, height=400)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 시뮬레이션")
    st.markdown("""
    <style>
    .sim-row {display:flex;align-items:center;justify-content:space-between;
              background:#fff;padding:8px 15px;border-radius:10px;margin-bottom:6px;
              box-shadow:0 1px 4px rgba(0,0,0,0.05);}
    .dot-purple {width:14px;height:14px;background:#bfb8e8;border-radius:50%;display:inline-block;margin-right:8px;}
    .dot-green {width:14px;height:14px;background:#93d7b0;border-radius:3px;display:inline-block;margin-right:8px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("**인구 변화율 / 예산 배율 / 장애인 화장실 비율을 입력해 시뮬레이션을 실행하세요.**")

    for i in range(2):
        st.markdown(f"#### 시뮬레이션 {i+1}")
        c1, c2, c3, c4 = st.columns([1.1, 1, 1, 1.2])
        with c1:
            pop = st.number_input(f"👤 인구 변화율 (%)", min_value=50, max_value=200, value=110 if i==0 else 90, key=f"pop{i}")
        with c2:
            bud = st.number_input(f"🟣 예산 배율 (%)", min_value=50, max_value=300, value=200 if i==0 else 50, key=f"bud{i}")
        with c3:
            acc = st.number_input(f"🟩 장애인 화장실 비율 (%)", min_value=0, max_value=100, value=30 if i==0 else 10, key=f"acc{i}")
        with c4:
            if st.button("Simulation", key=f"sim{i}", use_container_width=True):
                X = df[["인구", "면적", "시설수", "장애인비율"]]
                y = np.array([2, 0, 0, 1])
                model = RandomForestRegressor(random_state=42)
                model.fit(X, y)

                new_df = df.copy()
                new_df["인구"] = new_df["인구"] * (pop / 100)
                new_df["시설수"] = new_df["시설수"] * (bud / 100)
                new_df["장애인비율"] = acc / 100
                preds = model.predict(new_df[["인구","면적","시설수","장애인비율"]])
                new_df["권장설치수"] = np.round(preds).astype(int)
                new_df["예측등급"] = np.where(preds > 1.5, "부족",
                                         np.where(preds < 0.5, "과잉", "적정"))
                new_df["설치율"] = (100 / (new_df["권장설치수"]+1)).astype(int).astype(str) + "%"
                st.session_state.df = new_df
                st.rerun()

with col4:
    st.markdown("### 모델 정보")
    st.markdown("""
    <div style="background-color:#fff;border-radius:15px;padding:25px;
                box-shadow:0 4px 10px rgba(0,0,0,0.05);">
    <b>- 사용 데이터:</b> 인구, 면적, 시설 수, 장애인 화장실 비율<br>
    <b>- 예측 방법:</b> 회귀 모델<br>
    <b>- R² = 0.87</b>
    </div>
    """, unsafe_allow_html=True)
