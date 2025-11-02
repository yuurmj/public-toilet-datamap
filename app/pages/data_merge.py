import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="행정동별 인구·면적 데이터 결합", layout="wide")

st.title("📊 행정동별 인구·면적 데이터 결합")
st.write("이 페이지에서는 인구 데이터와 면적 데이터를 병합하여 행정동 단위 데이터를 생성합니다.")

# === 파일 경로 설정 ===
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
POP_PATH = DATA_DIR / "population.csv"
AREA_PATH = DATA_DIR / "area.csv"

# === 데이터 로드 함수 ===
@st.cache_data
def load_csv(path):
    try:
        df = pd.read_csv(path, encoding="utf-8")
        st.success(f"✅ 파일 로드 완료: {path.name} ({len(df)}행)")
        return df
    except FileNotFoundError:
        st.error(f"❌ 파일을 찾을 수 없습니다: {path}")
        return None
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        return None

# === 데이터 불러오기 ===
pop_df = load_csv(POP_PATH)
area_df = load_csv(AREA_PATH)

if pop_df is not None and area_df is not None:
    st.subheader("인구 데이터 미리보기")
    st.dataframe(pop_df.head())

    st.subheader("면적 데이터 미리보기")
    st.dataframe(area_df.head())

    # === 공통 키 확인 ===
    st.subheader("🔑 결합 키 설정")
    common_cols = set(pop_df.columns).intersection(area_df.columns)
    key_col = st.selectbox("결합할 기준 컬럼을 선택하세요", list(common_cols) if common_cols else ["행정동"], index=0)

    # === 데이터 병합 ===
    merged_df = pd.merge(pop_df, area_df, on=key_col, how="inner")
    st.subheader("📘 결합 결과 미리보기")
    st.dataframe(merged_df.head())

    # === 저장 옵션 ===
    SAVE_DIR = DATA_DIR / "output"
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SAVE_DIR / "merged_data.csv"

    if st.button("💾 병합 데이터 저장하기"):
        merged_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        st.success(f"병합된 데이터가 저장되었습니다: {out_path}")

else:
    st.warning("인구 데이터 또는 면적 데이터를 불러올 수 없습니다. data 폴더를 확인하세요.")
