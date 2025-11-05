# 기본 입력: data/validated/facilities_valid.csv
# 기본 출력: app/data/output/by_dong_app.csv
# 실행 : python scripts/export_for_app.py --debug
# (참조표가 있을 때 실행 예시)  python scripts/export_for_app.py --centers data/ref/dong_centers.csv --area data/ref/dong_area.csv --pop data/ref/population_by_dong.csv --debug

import argparse
import os
from datetime import datetime
from typing import Optional, List

import pandas as pd


# -------------------- Utils --------------------
def ensure_parent(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def load_csv(path: Optional[str], encoding="utf-8-sig") -> Optional[pd.DataFrame]:
    if not path:
        return None
    try:
        df = pd.read_csv(path, encoding=encoding)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except FileNotFoundError:
        print(f"[WARN] 파일이 없어 스킵합니다: {path}")
        return None


def to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype(float)


def to_int(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    s = s.fillna(0)
    return s.astype(int)


def first_mode(series: pd.Series) -> Optional[str]:
    """가장 많이 등장하는 문자열(법정동 등)을 하나 선택."""
    if series.empty:
        return None
    mode = series.mode(dropna=True)
    return None if mode.empty else str(mode.iloc[0])


def coalesce_cols(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


# -------------------- Core --------------------
def build_by_dong(
    fac: pd.DataFrame,
    centers: Optional[pd.DataFrame],
    area: Optional[pd.DataFrame],
    pop: Optional[pd.DataFrame],
    city_const: str,
    district_const: str,
    version: str,
) -> pd.DataFrame:
    # 필요한 컬럼 존재 확인/보정
    required = ["lat", "lon", "accessible"]
    for col in required:
        if col not in fac.columns:
            raise ValueError(f"[ERROR] 입력 데이터에 필요한 컬럼이 없습니다: {col}")

    # 열 이름 후보 (유연 매핑)
    admin_col = coalesce_cols(fac, ["admin_dong", "행정동", "dong", "동"])
    legal_col = coalesce_cols(fac, ["legal_dong", "법정동"])
    district_col = coalesce_cols(fac, ["district", "구", "군"])

    if admin_col is None:
        raise ValueError("[ERROR] 행정동 컬럼(admin_dong/행정동/dong/동)을 찾을 수 없습니다.")

    # 수치형 캐스팅
    fac["lat"] = to_float(fac["lat"])
    fac["lon"] = to_float(fac["lon"])
    fac["accessible"] = to_int(fac["accessible"])

    # 그룹 집계 (동 기준)
    gb_keys = [admin_col]
    # district/legal 동이 있으면 함께 모드로 보강
    agg = (
        fac.groupby(gb_keys, dropna=False)
        .agg(
            toilets_total=("accessible", "count"),
            toilets_accessible=("accessible", "sum"),
            centroid_lat=("lat", "mean"),   # 참조 중심좌표 있으면 나중에 덮어씀
            centroid_lng=("lon", "mean"),
        )
        .reset_index()
        .rename(columns={admin_col: "admin_dong"})
    )

    # legal_dong / district 모드값 붙이기
    if legal_col:
        legal_map = (
            fac.groupby(admin_col)[legal_col].agg(first_mode).reset_index()
            .rename(columns={admin_col: "admin_dong", legal_col: "legal_dong"})
        )
        agg = agg.merge(legal_map, on="admin_dong", how="left")
    else:
        agg["legal_dong"] = ""

    if district_col:
        dist_map = (
            fac.groupby(admin_col)[district_col].agg(first_mode).reset_index()
            .rename(columns={admin_col: "admin_dong", district_col: "district"})
        )
        agg = agg.merge(dist_map, on="admin_dong", how="left")
    else:
        agg["district"] = district_const

    # city/district 상수 보강(빈 값만)
    agg["city"] = agg.get("city", "")
    agg.loc[agg["city"].isna() | (agg["city"] == ""), "city"] = city_const
    agg.loc[agg["district"].isna() | (agg["district"] == ""), "district"] = district_const

    # admin_dong_code 탐색/조인
    # 우선순위: centers -> area -> population 에 있는 코드 열을 찾아 조인
    def try_merge_code(df_left: pd.DataFrame, df_ref: Optional[pd.DataFrame]) -> pd.DataFrame:
        if df_ref is None:
            return df_left
        # 후보 키
        code_col = coalesce_cols(df_ref, ["admin_dong_code", "행정동코드", "dong_code", "code"])
        name_col = coalesce_cols(df_ref, ["admin_dong", "행정동"])
        if code_col and name_col:
            ref = df_ref[[name_col, code_col]].drop_duplicates()
            ref = ref.rename(columns={name_col: "admin_dong", code_col: "admin_dong_code"})
            return df_left.merge(ref, on="admin_dong", how="left")
        return df_left

    agg = try_merge_code(agg, centers)
    agg = try_merge_code(agg, area)
    agg = try_merge_code(agg, pop)
    if "admin_dong_code" not in agg.columns:
        agg["admin_dong_code"] = ""

    # 중심좌표(참조가 있으면 덮어쓰기)
    if centers is not None:
        # centers는 admin_dong_code 와 lat/lng 혹은 admin_dong 와 lat/lng 를 가질 수 있음
        c_name = coalesce_cols(centers, ["admin_dong", "행정동"])
        c_code = coalesce_cols(centers, ["admin_dong_code", "행정동코드", "dong_code", "code"])
        c_lat = coalesce_cols(centers, ["centroid_lat", "lat_center", "lat", "위도"])
        c_lng = coalesce_cols(centers, ["centroid_lng", "lon_center", "lng", "lon", "경도"])

        if c_lat and c_lng:
            cref = centers.copy()
            # 조인 키 설정: 코드 우선, 없으면 이름
            if c_code and "admin_dong_code" in agg.columns:
                cref = cref.rename(columns={c_code: "admin_dong_code", c_lat: "c_lat", c_lng: "c_lng"})
                agg = agg.merge(cref[["admin_dong_code", "c_lat", "c_lng"]], on="admin_dong_code", how="left")
            elif c_name:
                cref = cref.rename(columns={c_name: "admin_dong", c_lat: "c_lat", c_lng: "c_lng"})
                agg = agg.merge(cref[["admin_dong", "c_lat", "c_lng"]], on="admin_dong", how="left")

            # 있으면 덮어씀
            agg["centroid_lat"] = agg["c_lat"].fillna(agg["centroid_lat"])
            agg["centroid_lng"] = agg["c_lng"].fillna(agg["centroid_lng"])
            agg = agg.drop(columns=[c for c in ["c_lat", "c_lng"] if c in agg.columns])

    # 면적/인구 조인
    def merge_metric(df_left: pd.DataFrame, df_ref: Optional[pd.DataFrame], value_cols: List[str]) -> pd.DataFrame:
        if df_ref is None:
            for v in value_cols:
                if v not in df_left.columns:
                    df_left[v] = 0
            return df_left

        name_col = coalesce_cols(df_ref, ["admin_dong", "행정동"])
        code_col = coalesce_cols(df_ref, ["admin_dong_code", "행정동코드", "dong_code", "code"])

        ref = df_ref.copy()
        # 열 이름 표준화 시도
        rename_map = {}
        for v in value_cols:
            cand = coalesce_cols(ref, [v, v.replace("_km2", ""), v.replace("_km2", "_km²"), v.replace("population", "pop")])
            if cand:
                rename_map[cand] = v
        if rename_map:
            ref = ref.rename(columns=rename_map)

        # 조인 키 우선순위: 코드 -> 이름
        if code_col and "admin_dong_code" in df_left.columns:
            ref = ref.rename(columns={code_col: "admin_dong_code"})
            keep_cols = ["admin_dong_code"] + [v for v in value_cols if v in ref.columns]
            ref = ref[keep_cols].drop_duplicates()
            return df_left.merge(ref, on="admin_dong_code", how="left")
        elif name_col:
            ref = ref.rename(columns={name_col: "admin_dong"})
            keep_cols = ["admin_dong"] + [v for v in value_cols if v in ref.columns]
            ref = ref[keep_cols].drop_duplicates()
            return df_left.merge(ref, on="admin_dong", how="left")
        else:
            for v in value_cols:
                if v not in df_left.columns:
                    df_left[v] = 0
            return df_left

    agg = merge_metric(agg, area, ["area_km2"])
    agg = merge_metric(agg, pop, ["population"])

    # 결측치 채우기/타입 보장
    for c in ["area_km2"]:
        if c in agg.columns:
            agg[c] = to_float(agg[c]).fillna(0.0)
        else:
            agg[c] = 0.0

    for c in ["population"]:
        if c in agg.columns:
            agg[c] = to_int(agg[c])
        else:
            agg[c] = 0

    # 유도 지표 계산
    # toilets_per_10k = toilets_total / population * 10000
    pop_nonpos = agg["population"] <= 0
    agg["toilets_per_10k"] = 0.0
    safe_pop = agg["population"].where(~pop_nonpos, other=1)  # 분모 0 방지
    agg.loc[~pop_nonpos, "toilets_per_10k"] = (agg["toilets_total"] / safe_pop * 10000).astype(float)

    # toilets_density_per_km2 = toilets_total / area_km2
    area_nonpos = agg["area_km2"] <= 0
    agg["toilets_density_per_km2"] = 0.0
    safe_area = agg["area_km2"].where(~area_nonpos, other=1.0)
    agg.loc[~area_nonpos, "toilets_density_per_km2"] = (agg["toilets_total"] / safe_area).astype(float)

    # accessible_ratio = toilets_accessible / toilets_total
    total_nonpos = agg["toilets_total"] <= 0
    agg["accessible_ratio"] = 0.0
    safe_total = agg["toilets_total"].where(~total_nonpos, other=1)
    agg.loc[~total_nonpos, "accessible_ratio"] = (agg["toilets_accessible"] / safe_total).astype(float)

    # 날짜/버전/출처
    agg["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    agg["version"] = version
    if "source" not in agg.columns:
        agg["source"] = ""

    # city/district/legal/admin 문자열 보장
    for c in ["city", "district", "legal_dong", "admin_dong", "admin_dong_code"]:
        if c not in agg.columns:
            agg[c] = ""
        agg[c] = agg[c].fillna("").astype(str)

    # 컬럼 순서 정리 (데이터 사전 기준 경량본)
    cols = [
        "city", "district", "legal_dong", "admin_dong", "admin_dong_code",
        "centroid_lat", "centroid_lng",
        "area_km2", "population",
        "toilets_total", "toilets_accessible",
        "toilets_per_10k", "toilets_density_per_km2", "accessible_ratio",
        "updated_at", "version", "source",
    ]

    # 누락된 컬럼 보호
    for c in cols:
        if c not in agg.columns:
            agg[c] = 0 if c in ["population", "toilets_total", "toilets_accessible"] else ""

    return agg[cols].sort_values(["district", "admin_dong"]).reset_index(drop=True)


# -------------------- Main --------------------
def main():
    parser = argparse.ArgumentParser(description="Export by-dong dataset for dashboard")
    parser.add_argument("--fac", default="data/validated/facilities_valid.csv", help="시설 단위 정제본 CSV")
    parser.add_argument("--centers", default=None, help="(선택) 동 중심좌표 CSV (admin_dong_code/admin_dong + lat/lng)")
    parser.add_argument("--area", default=None, help="(선택) 동 면적 CSV (admin_dong_code/admin_dong + area_km2)")
    parser.add_argument("--pop", default=None, help="(선택) 동 인구 CSV (admin_dong_code/admin_dong + population)")
    parser.add_argument("--out", default="app/data/output/by_dong_app.csv", help="대시보드 출력 CSV")
    parser.add_argument("--city", default="부산광역시", help="도시명 고정값")
    parser.add_argument("--district", default="남구", help="구/군 고정값")
    parser.add_argument("--version", default="1.0.0", help="데이터/스키마 버전")
    parser.add_argument("--encoding", default="utf-8-sig", help="CSV 인코딩")
    parser.add_argument("--debug", action="store_true", help="디버그 로그 출력")
    args = parser.parse_args()

    # 입력 로드
    fac = load_csv(args.fac, encoding=args.encoding)
    if fac is None:
        print(f"[ERROR] 입력 파일을 찾을 수 없습니다: {args.fac}")
        return

    centers = load_csv(args.centers, encoding=args.encoding) if args.centers else None
    area = load_csv(args.area, encoding=args.encoding) if args.area else None
    pop = load_csv(args.pop, encoding=args.encoding) if args.pop else None

    if args.debug:
        print("[DEBUG] facilities shape:", fac.shape)
        print("[DEBUG] facilities cols :", list(fac.columns)[:50])
        if centers is not None:
            print("[DEBUG] centers cols    :", list(centers.columns)[:50])
        if area is not None:
            print("[DEBUG] area cols       :", list(area.columns)[:50])
        if pop is not None:
            print("[DEBUG] population cols :", list(pop.columns)[:50])

    # 산출
    by_dong = build_by_dong(
        fac=fac,
        centers=centers,
        area=area,
        pop=pop,
        city_const=args.city,
        district_const=args.district,
        version=args.version,
    )

    # 저장
    ensure_parent(args.out)
    by_dong.to_csv(args.out, index=False, encoding=args.encoding)

    # 요약 출력
    print("=== Export Summary ===")
    print(f"Input           : {args.fac}")
    print(f"Centers (opt)   : {args.centers}")
    print(f"Area (opt)      : {args.area}")
    print(f"Population (opt): {args.pop}")
    print(f"Output          : {args.out}  ({len(by_dong)} rows)")
    print(f"Columns         : {list(by_dong.columns)}")


if __name__ == "__main__":
    main()
