import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from pathlib import Path

st.set_page_config(page_title="행정동별 인구·면적 데이터 분석", layout="wide")

st.title("📊 행정동별 인구·면적 데이터 결합 및 EDA 분석")

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
        return pd.read_csv(path, encoding="utf-8")
    except:
        return None

pop_df = load_csv(POP_PATH)
area_df = load_csv(AREA_PATH)

if pop_df is not None and area_df is not None:
    common_cols = set(pop_df.columns).intersection(area_df.columns)
    key_col = list(common_cols)[0] if common_cols else "행정동"
    merged_df = pd.merge(pop_df, area_df, on=key_col, how="inner")
    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(MERGED_PATH, index=False, encoding="utf-8-sig")
else:
    if MERGED_PATH.exists():
        merged_df = pd.read_csv(MERGED_PATH, encoding="utf-8")
    else:
        st.error("인구·면적 데이터를 찾을 수 없습니다.")
        st.stop()

st.header("1️⃣ 행정동별 기본 집계")

region_col = st.selectbox("행정동 컬럼 선택", [c for c in merged_df.columns if "동" in c or "행정" in c], index=0)
numeric_cols = merged_df.select_dtypes(include="number").columns.tolist()
pop_col = st.selectbox("인구 컬럼 선택", numeric_cols, index=0)
area_col = st.selectbox("면적 컬럼 선택", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)

grouped = merged_df.groupby(region_col).agg(
    총인구=(pop_col, "sum"),
    총면적=(area_col, "mean")
).reset_index()
grouped["인구밀도(명/km²)"] = grouped["총인구"] / grouped["총면적"]

st.dataframe(grouped.head(), use_container_width=True)

st.header("2️⃣ 시각화 분석")
tab1, tab2, tab3, tab4 = st.tabs(["인구 및 밀도", "분포도", "상관관계", "히트맵"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_pop = px.bar(
            grouped.sort_values("총인구", ascending=False),
            x=region_col, y="총인구",
            title="행정동별 총인구",
            color="총인구", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_pop, use_container_width=True)
    with c2:
        fig_density = px.bar(
            grouped.sort_values("인구밀도(명/km²)", ascending=False),
            x=region_col, y="인구밀도(명/km²)",
            title="행정동별 인구밀도",
            color="인구밀도(명/km²)", color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_density, use_container_width=True)

with tab2:
    fig_dist = ff.create_distplot(
        [grouped["총인구"], grouped["총면적"], grouped["인구밀도(명/km²)"]],
        group_labels=["총인구", "총면적", "인구밀도(명/km²)"],
        colors=["#1f77b4", "#2ca02c", "#d62728"]
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    fig_box = px.box(
        grouped.melt(id_vars=[region_col], value_vars=["총인구", "총면적", "인구밀도(명/km²)"]),
        x="variable", y="value", color="variable", title="지표별 분포 비교"
    )
    st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    corr = grouped[["총인구", "총면적", "인구밀도(명/km²)"]].corr()
    st.dataframe(corr.style.background_gradient(cmap="RdBu_r", axis=None))
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="상관관계 히트맵")
    st.plotly_chart(fig_corr, use_container_width=True)

with tab4:
    try:
        fig_heat = px.density_heatmap(
            grouped, x="총면적", y="총인구", z="인구밀도(명/km²)",
            nbinsx=20, nbinsy=20, color_continuous_scale="Viridis",
            title="면적 대비 인구 및 밀도 히트맵"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.warning(f"히트맵 생성 실패: {e}")

st.header("3️⃣ 결과 저장")
grouped_path = OUTPUT_DIR / "grouped_data.csv"
if st.button("💾 집계 결과 저장"):
    grouped.to_csv(grouped_path, index=False, encoding="utf-8-sig")
    st.success(f"집계 데이터 저장 완료: {grouped_path}")
