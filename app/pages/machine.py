import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

@st.cache_data
def load_data():
    data = pd.DataFrame({
        "dong": ["대연동","용호동","문현동","감만동","우암동"],
        "population": [30000, 45000, 20000, 15000, 5000],
        "floating": [5000, 8000, 2000, 1000, 500],
        "toilets": [5, 7, 2, 1, 0],
        "accessible": [3, 4, 1, 0, 0]
    })
    data["toilet_ratio"] = data["toilets"] / data["population"]
    data["label"] = (data["toilet_ratio"] < 0.0005).astype(int)
    return data

df = load_data()

X = df[["population","floating","toilets","accessible"]]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

df["prediction"] = model.predict(X)
proba = model.predict_proba(X)
if proba.shape[1] == 1:
    df["probability"] = proba[:,0]
else:
    df["probability"] = proba[:,1]

st.set_page_config(page_title="공중화장실 데이터맵", layout="wide")

st.title("🚻 공중화장실 데이터맵 + 머신러닝 예측")

st.subheader("📊 원본 데이터")
st.dataframe(df)

st.subheader("📈 행정동별 인구 대비 화장실 수")
fig = px.bar(df, x="dong", y="toilet_ratio", color="label",
             labels={"dong":"행정동","toilet_ratio":"인구 대비 화장실 비율"},
             title="행정동별 화장실 비율 (빨강=부족, 파랑=적정)")
st.plotly_chart(fig, use_container_width=True)

coords = {
    "대연동": (35.133, 129.101),
    "용호동": (35.120, 129.118),
    "문현동": (35.145, 129.068),
    "감만동": (35.129, 129.075),
    "우암동": (35.115, 129.082),
}

st.subheader("🗺️ 공중화장실 부족 지역 지도")
m = folium.Map(location=[35.13,129.10], zoom_start=13)

for _, row in df.iterrows():
    lat, lon = coords[row["dong"]]
    color = "red" if row["prediction"]==1 else "green"
    popup = f"""
    <b>{row['dong']}</b><br>
    인구: {row['population']}명<br>
    화장실 수: {row['toilets']}개<br>
    부족확률: {row['probability']*100:.1f}%
    """
    folium.CircleMarker(
        location=(lat, lon),
        radius=12,
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=popup
    ).add_to(m)

st_folium(m, width=800, height=500)

st.subheader("🃏 머신러닝 예측 카드")
for _, row in df.iterrows():
    status = "부족" if row["prediction"]==1 else "적정"
    st.metric(label=row["dong"], value=f"{status} ({row['probability']*100:.1f}%)")
