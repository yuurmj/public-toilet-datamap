import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path

st.set_page_config(page_title="행정동별 화장실 수 막대그래프", layout="wide")
st.title(" 행정동별 화장실 수")

# CSV 경로
CSV_PATH = Path("data/admin_metrics.csv")

# 데이터 로드 admin_name,toilets필요
if not CSV_PATH.exists():
    st.error("data/admin_metrics.csv 파일이 필요합니다. (admin_name,toilets)")
    st.stop()

df = pd.read_csv(CSV_PATH)

# 숫자형 보정
if "toilets" not in df.columns or "admin_name" not in df.columns:
    st.error("CSV에 'admin_name' 과 'toilets' 컬럼이 필요합니다.")
    st.stop()

df["toilets"] = pd.to_numeric(df["toilets"], errors="coerce")

# 막대그래프 생성
bar = (
    alt.Chart(df.dropna(subset=["toilets"]))
    .mark_bar()
    .encode(
        x=alt.X("toilets:Q", title="화장실 수"),
        y=alt.Y("admin_name:N", sort="-x", title="행정동"),
        tooltip=["admin_name", alt.Tooltip("toilets:Q", title="화장실 수", format=",.0f")]
    )
    .properties(height=500)
)

st.altair_chart(bar, use_container_width=True)
