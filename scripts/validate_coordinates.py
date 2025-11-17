# 입력:  public-toilet-datamap/data/raw/toilets_namgu.csv
# 출력:  public-toilet-datamap/data/validated/facilities_valid.csv (이상치 제외)
# 빠른 실행: python scripts/validate_coordinates.py --debug
# hw 대시보드-Streamlit에서 사용

# 지역이 바뀌면 입력에 nomalize_dong_names.py 스크립트 사용 필요!!!!!!

import argparse
import os
import pandas as pd
from typing import Tuple, List, Optional


def find_first_existing(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """데이터프레임에서 후보 컬럼명 중 존재하는 첫 컬럼 반환."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def coerce_float(series: pd.Series) -> pd.Series:
    """문자열/공백 등을 float로 안전 변환."""
    return pd.to_numeric(series.astype(str).str.strip(), errors="coerce")


def validate_coordinates(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    bbox: Tuple[float, float, float, float],
    swap_detect: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    좌표 검증/정제 로직 수행 (GeoJSON 폴리곤 검사 없음)
    반환: (valid_df, invalid_df, stats)
    """
    stats = {
        "total": len(df),
        "dropped_nan": 0,
        "dropped_zero": 0,
        "dropped_physically_impossible": 0,
        "swapped": 0,
        "dropped_out_of_range": 0,
        "kept": 0,
    }

    # 1) NaN 제거
    df[lat_col] = coerce_float(df[lat_col])
    df[lon_col] = coerce_float(df[lon_col])

    nan_mask = df[[lat_col, lon_col]].isna().any(axis=1)
    nan_rows = df[nan_mask].copy()
    stats["dropped_nan"] = int(nan_mask.sum())
    df = df[~nan_mask].copy()

    # 2) (0,0) 제거
    zero_mask = (df[lat_col] == 0) | (df[lon_col] == 0)
    zero_rows = df[zero_mask].copy()
    stats["dropped_zero"] = int(zero_mask.sum())
    df = df[~zero_mask].copy()

    # 3) 물리적으로 불가능한 값 제거(|lat|>90, |lon|>180)
    phys_mask = (df[lat_col].abs() > 90) | (df[lon_col].abs() > 180)
    phys_rows = df[phys_mask].copy()
    stats["dropped_physically_impossible"] = int(phys_mask.sum())
    df = df[~phys_mask].copy()

    # 4) lat/lon 뒤바뀜 감지 및 교정
    lat_min, lat_max, lon_min, lon_max = bbox
    if swap_detect:
        swapped_mask = df[lat_col].between(lon_min, lon_max) & df[lon_col].between(lat_min, lat_max)
        stats["swapped"] = int(swapped_mask.sum())
        if stats["swapped"] > 0:
            tmp_lat = df.loc[swapped_mask, lat_col].copy()
            df.loc[swapped_mask, lat_col] = df.loc[swapped_mask, lon_col].values
            df.loc[swapped_mask, lon_col] = tmp_lat.values

    # 5) BBOX 범위 필터
    range_mask = df[lat_col].between(lat_min, lat_max) & df[lon_col].between(lon_min, lon_max)
    out_range_rows = df[~range_mask].copy()
    stats["dropped_out_of_range"] = int((~range_mask).sum())
    df = df[range_mask].copy()

    # 6) 결과 구성
    valid_df = df.copy()
    invalid_df = pd.concat(
        [
            nan_rows.assign(_invalid_reason="NaN lat/lon"),
            zero_rows.assign(_invalid_reason="Zero lat/lon"),
            phys_rows.assign(_invalid_reason="Physically impossible lat/lon"),
            out_range_rows.assign(_invalid_reason="Out of BBOX"),
        ],
        ignore_index=True
    )

    stats["kept"] = len(valid_df)
    return valid_df, invalid_df, stats


def main():
    parser = argparse.ArgumentParser(description="Validate and clean facility coordinates.")
    parser.add_argument(
        "--input",
        default="data/raw/toilets_namgu.csv",
        help="입력 CSV 경로"
    )
    parser.add_argument(
        "--output",
        default="data/validated/facilities_valid.csv",
        help="정제된 결과 CSV 경로"
    )
    parser.add_argument(
        "--invalid-output",
        default="data/validated/facilities_invalid.csv",
        help="제외/문제 행 로그 CSV 경로"
    )
    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        default=[35.0, 36.0, 128.0, 130.0],
        metavar=("LAT_MIN", "LAT_MAX", "LON_MIN", "LON_MAX"),
        help="위경도 BBOX (기본: 35 36 128 130)"
    )
    parser.add_argument(
        "--no-swap-detect",
        action="store_true",
        help="lat/lon 뒤바뀜 자동 교정 비활성화"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV 인코딩 (기본: utf-8-sig)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드: 컬럼/행 수 출력"
    )

    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # CSV 로드
    try:
        df = pd.read_csv(args.input, encoding=args.encoding)
    except FileNotFoundError:
        print(f"[ERROR] 입력 파일을 찾을 수 없습니다: {args.input}")
        return
    except UnicodeDecodeError as e:
        print(f"[ERROR] 인코딩 오류 발생. --encoding cp949 로 재시도해보세요.\n{e}")
        return

    if args.debug:
        print("[DEBUG] Loaded CSV shape:", df.shape)
        print("[DEBUG] Columns:", list(df.columns))
        print("[DEBUG] Head:\n", df.head(3))

    # 문자열 공백/개행 정리
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # 컬럼명 확인
    id_col = find_first_existing(df, ["toilet_id", "facility_id", "id", "oilet_id"])
    lat_col = find_first_existing(df, ["lat", "latitude", "위도"])
    lon_col = find_first_existing(df, ["lon", "lng", "longitude", "경도"])

    if args.debug:
        print(f"[DEBUG] Detected columns -> id:{id_col}, lat:{lat_col}, lon:{lon_col}")

    if lat_col is None or lon_col is None:
        print("[ERROR] lat/lon 컬럼을 찾을 수 없습니다.")
        return

    # 검증 실행
    try:
        valid_df, invalid_df, stats = validate_coordinates(
            df=df,
            lat_col=lat_col,
            lon_col=lon_col,
            bbox=tuple(args.bbox),
            swap_detect=not args.no_swap_detect
        )
    except Exception as e:
        print("[ERROR] 검증 중 오류 발생:", e)
        return

    # 저장
    valid_df.to_csv(args.output, index=False, encoding="utf-8-sig")
    if len(invalid_df) > 0:
        invalid_df.to_csv(args.invalid_output, index=False, encoding="utf-8-sig")

    # 결과 출력
    print("=== Coordinate Validation Summary ===")
    print(f"Input file       : {args.input}")
    print(f"Output (valid)   : {args.output}  ({stats['kept']} rows)")
    print(f"Invalid log      : {args.invalid_output}  ({len(invalid_df)} rows)")
    print(f"BBOX             : lat[{args.bbox[0]}, {args.bbox[1]}], lon[{args.bbox[2]}, {args.bbox[3]}]")
    print(f"Total rows       : {stats['total']}")
    print(f"Dropped - NaN    : {stats['dropped_nan']}")
    print(f"Dropped - Zero   : {stats['dropped_zero']}")
    print(f"Dropped - Phys   : {stats['dropped_physically_impossible']}")
    print(f"Dropped - BBOX   : {stats['dropped_out_of_range']}")
    print(f"Swapped lat/lon  : {stats['swapped']}")
    print("=====================================")


if __name__ == "__main__":
    main()
