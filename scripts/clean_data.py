import pandas as pd
from pathlib import Path
import re

def _read_csv_smart(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue

    # 마지막 시도 실패 시 기본으로 시도(에러 발생)
    return pd.read_csv(path)

def _to_bool_safe(series: pd.Series) -> pd.Series:
    # 0/1, "0"/"1", True/False, Y/N, yes/no 대응
    mapping = {"1": True, "0": False, "y": True, "n": False, "yes": True, "no": False, "true": True, "false": False}
    s = series.copy()
    # 숫자/문자 혼재 안전 변환
    s = s.astype(str).str.strip().str.lower().map(mapping)
    return s.fillna(False).astype(bool)

def clean_toilets_csv(input_path, output_path, district_code="NMG"):
    # CSV 불러오기
    df = pd.read_csv(input_path)

    # 1. 컬럼명 표준화
    rename_map = {
        "시설명": "name",
        "주소": "addr",
        "위도": "lat",
        "경도": "lon",
        "남자변기": "male_wc",
        "여자변기": "female_wc",
        "장애인남자": "male_wc_disabled",
        "장애인여자": "female_wc_disabled",
        "장애인화장실유무": "accessible",
        "구": "district",
        "동": "dong"
    }
    exist_map = {k: v for k, v in rename_map.items() if k in df.columns}
    if exist_map:
        df = df.rename(columns=exist_map)

    # 2. toilet_id 자동 생성
    if "toilet_id" not in df.columns:
        df.insert(0, 'toilet_id', [f"{district_code}-{i:04d}" for i in range(1, len(df)+1)])

    # 3. 숫자형 변환
    numeric_cols = ["lat", "lon", "male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 위/경도 6자리로 통일 + 결측 제거(지도 오류 방지)
    if "lat" in df and "lon" in df:
        df["lat"] = df["lat"].round(6)
        df["lon"] = df["lon"].round(6)
        df = df.dropna(subset=["lat", "lon"])

    # 변기 개수 NaN → 0
    for col in ["male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled"]:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    # 4) 접근성(accessible) 안전 변환 + 보정
    if "accessible" in df.columns:
        df["accessible"] = _to_bool_safe(df["accessible"])
    else:
        # accessible 컬럼이 없다면 만들기(False 기본)
        df["accessible"] = False

    # 장애인 변기 개수가 존재하면 accessible 보정(True)
    if {"male_wc_disabled", "female_wc_disabled"}.issubset(df.columns):
        has_disabled_wc = (df["male_wc_disabled"] + df["female_wc_disabled"]) > 0
        df.loc[has_disabled_wc, "accessible"] = True

    # 5) 텍스트 정리: 공백/행정동 표준화/주소 프리픽스 제거
    for col in ["name", "addr", "district", "dong"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "dong" in df.columns:
        # 예: 대연5동 → 대연동
        df["dong"] = df["dong"].str.replace(r"\d+동", "동", regex=True)

    if "addr" in df.columns:
        # 예: "부산광역시 남구 " 제거(가독성)
        df["addr"] = df["addr"].str.replace(r"^부산광역시\s*남구\s*", "", regex=True)

    # 6) 파생 지표: disabled_ratio
    if {"male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled"}.issubset(df.columns):
        denom = (df["male_wc"] + df["female_wc"]).replace(0, 1)  # 0분모 방지
        df["disabled_ratio"] = (
            (df["male_wc_disabled"] + df["female_wc_disabled"]) / denom
        ).round(3)

    # 7) 중복 제거(이름+주소 기준)
    before = len(df)
    if {"name", "addr"}.issubset(df.columns):
        df = df.drop_duplicates(subset=["name", "addr"])
    dropped = before - len(df)

    # 8) 저장
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    # 요약 출력
    print(f"전처리 완료! 저장: {output_path}")
    print(f"- 총 행 수: {len(df)}  (중복 제거 {dropped}건)")

if __name__ == "__main__":
    clean_toilets_csv(
        "data/raw/toilets_namgu.csv",
        "data/processed/toilets_namgu_cleaned.csv",
        district_code="NMG",
    )