# scripts/process_toilets.py
from pathlib import Path
import argparse, re
import pandas as pd
import numpy as np

NEEDED = [
    "toilet_id","name","addr","lat","lng",
    "male_wc","female_wc","male_wc_disabled","female_wc_disabled",
    "accessible","gender_sep","district","dong","open_time"
]

ENCODINGS = ["utf-8-sig","cp949","euc-kr"]

def read_csv_smart(p: Path) -> pd.DataFrame:
    last = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(p, encoding=enc)
        except Exception as e:
            last = e
    raise last

def pick(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def as_int(x):
    if pd.isna(x):
        return np.nan
    s = re.sub(r"[^0-9]", "", str(x))
    return pd.to_numeric(s, errors="coerce")

def as_bool01(x):
    s = str(x).strip().lower()
    if s in {"1","y","yes","true","t","가능","있음","사용","o","ok","예"}: return 1
    if s in {"0","n","no","false","f","불가","없음","미사용","x","아니오"}: return 0
    return pd.to_numeric(s, errors="coerce") if re.fullmatch(r"\d+", s) else 0

def ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    for c in NEEDED:
        if c not in df.columns:
            df[c] = np.nan
    return df[NEEDED].copy()

def standardize_latlng(df: pd.DataFrame) -> pd.DataFrame:
    lat_cand = pick(df, ["lat","위도","y","latitude"])
    lng_cand = pick(df, ["lng","lon","경도","x","longitude"])
    if lat_cand and lat_cand != "lat":
        df = df.rename(columns={lat_cand:"lat"})
    if lng_cand and lng_cand not in {"lng"}:
        df = df.rename(columns={lng_cand:"lng"})
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat","lng"])
    df = df[(df["lat"].between(-90,90)) & (df["lng"].between(-180,180))]
    return df

def series_or_default(df: pd.DataFrame, col: str, default=0) -> pd.Series:
    return df[col] if col in df.columns else pd.Series(default, index=df.index)

def normalize_one(src: Path, out_dir: Path, default_district: str):
    raw = read_csv_smart(src)

    # 문자열 트리밍 (applymap 경고 우회: object 컬럼만 개별 처리)
    for c in raw.select_dtypes(include=["object"]).columns:
        raw[c] = raw[c].map(lambda x: x.strip() if isinstance(x, str) else x)

    # 유연 매핑
    col_map = {}
    name_col = pick(raw, ["name","시설명","화장실명"])
    addr_col = pick(raw, ["addr","주소"])
    dong_col = pick(raw, ["dong","행정동"])
    id_col   = pick(raw, ["toilet_id","id","시설id","시설ID"])
    m_wc     = pick(raw, ["male_wc","남자변기수","남대변기","남자대변기수"])
    f_wc     = pick(raw, ["female_wc","여자변기수","여대변기","여자대변기수"])
    m_wc_d   = pick(raw, ["male_wc_disabled","남자장애인변기수","남장애인"])
    f_wc_d   = pick(raw, ["female_wc_disabled","여자장애인변기수","여장애인"])
    acc_col  = pick(raw, ["accessible","장애인화장실","무장애"])
    gsep_col = pick(raw, ["gender_sep","남녀분리","남녀구분"])
    open_col = pick(raw, ["open_time","운영시간","개방시간"])

    if name_col: col_map[name_col] = "name"
    if addr_col: col_map[addr_col] = "addr"
    if dong_col: col_map[dong_col] = "dong"
    if id_col:   col_map[id_col]   = "toilet_id"
    if m_wc:     col_map[m_wc]     = "male_wc"
    if f_wc:     col_map[f_wc]     = "female_wc"
    if m_wc_d:   col_map[m_wc_d]   = "male_wc_disabled"
    if f_wc_d:   col_map[f_wc_d]   = "female_wc_disabled"
    if acc_col:  col_map[acc_col]  = "accessible"
    if gsep_col: col_map[gsep_col] = "gender_sep"
    if open_col: col_map[open_col] = "open_time"

    df = raw.rename(columns=col_map)
    df = standardize_latlng(df)

    if "district" not in df.columns:
        df["district"] = default_district
    if "open_time" not in df.columns:
        df["open_time"] = ""

    # 수치형 보정
    for c in ["male_wc","female_wc","male_wc_disabled","female_wc_disabled"]:
        if c in df.columns:
            df[c] = df[c].apply(as_int).fillna(0).astype(int)
        else:
            df[c] = 0

    # 불리언(0/1) 보정: 컬럼 없으면 동일 길이의 시리즈로 기본값 생성
    df["accessible"] = series_or_default(df, "accessible", 0).apply(as_bool01).fillna(0).clip(0,1).astype(int)
    df["gender_sep"] = series_or_default(df, "gender_sep", 0).apply(as_bool01).fillna(0).clip(0,1).astype(int)

    # ID 생성(없으면 파일명+동+일련)
    if "toilet_id" not in df.columns or df["toilet_id"].isna().all():
        df = df.reset_index(drop=True)
        stem = src.stem
        df["toilet_id"] = [
            f"{default_district}-{str(df.loc[i,'dong'])}-{i+1:04d}"
            for i in range(len(df))
        ]
    else:
        df["toilet_id"] = df["toilet_id"].astype(str)

    # 최소 스키마 보장 및 저장
    df = ensure_cols(df)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{src.stem}.normalized.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] {src.name} -> {out_path} ({len(df)} rows)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", help="단일 원본 CSV 경로(옵션)")
    ap.add_argument("--indir", default="data/raw/toilets", help="원본 폴더")
    ap.add_argument("--outdir", default="data/processed/toilets", help="정규화 폴더")
    ap.add_argument("--district", default="남구")
    args = ap.parse_args()

    out_dir = Path(args.outdir)
    if args.infile:
        normalize_one(Path(args.infile), out_dir, args.district)
    else:
        for src in sorted(Path(args.indir).glob("*.csv")):
            normalize_one(src, out_dir, args.district)

if __name__ == "__main__":
    main()