# scripts/process_population.py
# - raw/population/population_namgu.csv → processed/population/population_namgu.normalized.csv
# - processed/*.normalized.csv → app/population_app.csv

from pathlib import Path
import pandas as pd
import numpy as np
import re

# -------- 공통 유틸 --------
def read_csv_smart(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    last_err = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc, engine="python")
        except Exception as e:
            last_err = e
    raise last_err

def to_int_safe(x):
    if pd.isna(x):
        return np.nan
    s = re.sub(r"[^0-9]", "", str(x))
    return pd.to_numeric(s, errors="coerce")

def to_float_safe(x):
    if pd.isna(x):
        return np.nan
    # 소수점 포함 숫자만 남김
    s = re.sub(r"[^0-9.]", "", str(x))
    # 소수점이 여러 개인 경우 첫 번째만 유지
    if s.count(".") > 1:
        head, *rest = s.split(".")
        s = head + "." + "".join(rest)
    return pd.to_numeric(s, errors="coerce")

def norm_col(c: str) -> str:
    c = str(c).replace("\ufeff", "")
    c = re.sub(r"\s+", "", c)
    c = re.sub(r"[()\[\]{}·,./\-]", "", c)
    return c.lower()

def normalize_dong_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    s = re.sub(r"\s+", "", name.strip())
    s = re.sub(r"제?\d+동$", "동", s)  # 제2동/2동 → 동
    return s

def looks_like_dong(name: str) -> bool:
    if not isinstance(name, str):
        return False
    n = name.strip()
    if n == "" or ("합계" in n) or ("소계" in n) or (n == "계"):
        return False
    return ("동" in n) and ("구" not in n)

def detect_area_col(columns: list[str]) -> str | None:
    # 정규화된 컬럼명에서 면적 후보 찾기
    pats = [r"area", r"면적", r"제곱킬로미터", r"km2", r"㎢"]
    for c in columns:
        if any(re.search(p, c) for p in pats):
            return c
    return None

# -------- 메인 --------
def main():
    ROOT = Path(__file__).resolve().parents[1]
    DATA = ROOT / "data"
    raw_csv = DATA / "raw" / "population" / "population_namgu.csv"

    df = read_csv_smart(raw_csv)

    # 1) 헤더/값 정리
    df.columns = [norm_col(c) for c in df.columns]
    first_col = df.columns[0]
    df = df.rename(columns={first_col: "dong"})

    # 면적 컬럼 탐지(정규화된 이름 기준)
    area_col_norm = detect_area_col(list(df.columns))
    has_area = area_col_norm is not None

    # 2) 타입 정리: 면적은 float, 나머지는 int로 보정
    for c in df.columns:
        if c == "dong":
            continue
        if has_area and c == area_col_norm:
            df[c] = df[c].apply(to_float_safe)
        else:
            df[c] = df[c].apply(to_int_safe)

    # 3) 총인구 산출
    cols = list(df.columns)
    total_candidates = [c for c in cols if c not in ("dong", area_col_norm) and re.search(r"(총인구|인구수계|인구총|인구계|전체|^계$)", c)]
    male_candidates = [c for c in cols if c not in ("dong", area_col_norm) and re.search(r"(남자|남)(계|합계)?$", c)]
    female_candidates = [c for c in cols if c not in ("dong", area_col_norm) and re.search(r"(여자|여)(계|합계)?$", c)]

    def pick_population(row) -> float:
        for c in total_candidates:
            val = row.get(c, np.nan)
            if pd.notna(val):
                return float(val)
        m = next((row[c] for c in male_candidates if pd.notna(row.get(c))), np.nan)
        f = next((row[c] for c in female_candidates if pd.notna(row.get(c))), np.nan)
        if pd.notna(m) and pd.notna(f):
            return float(m) + float(f)
        nums = [row[c] for c in cols if c not in ("dong", area_col_norm) and pd.notna(row[c])]
        return float(np.nansum(nums)) if nums else np.nan

    df["population"] = df.apply(pick_population, axis=1)

    # 4) 동 필터 + 이름 정규화
    df = df[df["dong"].apply(looks_like_dong)].copy()
    df["dong"] = df["dong"].astype(str).map(normalize_dong_name)

    # 5) 구명/면적/정리
    df["district"] = "남구"
    out_cols = ["district", "dong", "population"]
    if has_area:
        df["area_km2"] = pd.to_numeric(df[area_col_norm], errors="coerce")
        out_cols.append("area_km2")

    df = df[out_cols]
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    if "area_km2" in df.columns:
        df["area_km2"] = pd.to_numeric(df["area_km2"], errors="coerce")

    df = df.dropna(subset=["population"])
    df = df[df["population"] >= 0]

    # 6) 부모동 기준 집계(대연1동~6동 → 대연동 합계)
    agg_map = {"population": "sum"}
    if "area_km2" in df.columns:
        agg_map["area_km2"] = "sum"
    grouped = df.groupby(["district", "dong"], as_index=False).agg(agg_map)

    # 7) 인구밀도(명/km²)
    if "area_km2" in grouped.columns:
        grouped["pop_density_km2"] = np.where(
            (grouped["area_km2"] > 0) & (grouped["population"] > 0),
            grouped["population"] / grouped["area_km2"],
            np.nan
        )
    else:
        grouped["pop_density_km2"] = np.nan

    # 8) 저장
    (DATA / "processed" / "population").mkdir(parents=True, exist_ok=True)
    (DATA / "app").mkdir(parents=True, exist_ok=True)

    out_proc = DATA / "processed" / "population" / "population_namgu.normalized.csv"
    out_app  = DATA / "app" / "population_app.csv"

    cols_export = ["district", "dong", "population", "area_km2", "pop_density_km2"]
    for c in cols_export:
        if c not in grouped.columns:
            grouped[c] = np.nan
    grouped = grouped[cols_export].sort_values(["district", "dong"])

    grouped.to_csv(out_proc, index=False, encoding="utf-8")
    grouped.to_csv(out_app,  index=False, encoding="utf-8")

    print(f"[OK] saved: {out_proc}")
    print(f"[OK] saved: {out_app}")

if __name__ == "__main__":
    main()