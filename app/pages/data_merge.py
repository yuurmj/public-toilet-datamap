import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="행정동별 인구·면적 데이터 분석", layout="wide")

st.title("📊 행정동별 인구·면적 데이터 결합 및 집계 분석")
st.write("인구 데이터와 면적 데이터를 병합하고 행정동 단위로 집계하여 인구밀도를 분석합니다.")

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
POP_PATH = DATA_DIR / "population.csv"
AREA_PATH = DATA_DIR / "area.csv"
MERGED_PATH = OUTPUT_DIR / "merged_data.csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@st.cache_data
def load_csv(path: Path):
    try:
        df = pd.read_csv(path, encoding="utf-8")
        st.success(f"{path.name} 로드 완료 ({len(df)}행)")
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None

st.header("1️⃣ 인구 및 면적 데이터 불러오기")
col1, col2 = st.columns(2)

with col1:
    pop_df = load_csv(POP_PATH)
    if pop_df is not None:
        st.subheader("인구 데이터 미리보기")
        st.dataframe(pop_df.head(), use_container_width=True)

with col2:
    area_df = load_csv(AREA_PATH)
    if area_df is not None:
        st.subheader("면적 데이터 미리보기")
        st.dataframe(area_df.head(), use_container_width=True)

if pop_df is not None and area_df is not None:
    st.header("2️⃣ 인구·면적 데이터 결합")
    common_cols = set(pop_df.columns).intersection(area_df.columns)
    key_col = st.selectbox("결합 기준 컬럼 선택", list(common_cols) if common_cols else ["행정동"], index=0)
    merged_df = pd.merge(pop_df, area_df, on=key_col, how="inner")
    st.write(f"결합 완료! 데이터 행 수: {len(merged_df)}")
    st.dataframe(merged_df.head(), use_container_width=True)
    if st.button("💾 병합 데이터 저장"):
        merged_df.to_csv(MERGED_PATH, index=False, encoding="utf-8-sig")
        st.success(f"저장 완료: {MERGED_PATH}")

st.header("3️⃣ 행정동별 집계 및 인구밀도 계산")

if MERGED_PATH.exists():
    merged_df = pd.read_csv(MERGED_PATH, encoding="utf-8")
    region_col = st.selectbox("행정동 컬럼 선택", [c for c in merged_df.columns if "동" in c or "행정" in c], index=0)
    numeric_cols = merged_df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        pop_col = st.selectbox("인구 컬럼 선택", numeric_cols, index=0)
        area_col = st.selectbox("면적 컬럼 선택", numeric_cols, index=1)
        grouped = merged_df.groupby(region_col).agg(
            총인구=(pop_col, "sum"),
            총면적=(area_col, "mean")
        ).reset_index()
        grouped["인구밀도(명/km²)"] = grouped["총인구"] / grouped["총면적"]
        st.subheader("행정동별 집계 결과")
        st.dataframe(grouped.head(), use_container_width=True)
        st.subheader("📊 시각화")
        tab1, tab2 = st.tabs(["총인구", "인구밀도"])
        with tab1:
            fig_pop = px.bar(
                grouped.sort_values("총인구", ascending=False),
                x=region_col, y="총인구",
                title="행정동별 총인구",
                color="총인구",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_pop, use_container_width=True)
        with tab2:
            fig_density = px.bar(
                grouped.sort_values("인구밀도(명/km²)", ascending=False),
                x=region_col, y="인구밀도(명/km²)",
                title="행정동별 인구밀도",
                color="인구밀도(명/km²)",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_density, use_container_width=True)
        grouped_path = OUTPUT_DIR / "grouped_data.csv"
        if st.button("💾 집계 결과 저장"):
            grouped.to_csv(grouped_path, index=False, encoding="utf-8-sig")
            st.success(f"집계 데이터 저장 완료: {grouped_path}")
else:
    st.warning("병합된 데이터가 없습니다. 먼저 위 단계에서 결합을 수행해주세요.")
