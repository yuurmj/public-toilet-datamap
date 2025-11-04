# 입력: data/validated/facilities_valid.csv
# 출력: reports/summary.md  (누적 append)
# 실행: python scripts/test_data_quality.py 아니면 python scripts/test_data_quality.py --debug
# hw

import argparse
import os
from datetime import datetime
import pandas as pd


# ---------- 유틸 ----------
def ensure_parent(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def load_csv(path: str, encoding="utf-8-sig") -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding=encoding)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] 입력 파일을 찾을 수 없습니다: {path}")
    # 문자열 공백/개행 정리
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


# ---------- 개별 체크 ----------
def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    rate = df.isna().mean().sort_values(ascending=False)
    return rate.to_frame("missing_rate").reset_index(names="column")


def check_duplicates(df: pd.DataFrame) -> dict:
    hard = df.duplicated(subset=[c for c in ["toilet_id", "facility_id", "id"] if c in df.columns]).sum()
    soft_keys = [c for c in ["name", "dong"] if c in df.columns]
    soft = df.duplicated(subset=soft_keys).sum() if soft_keys else 0
    return {"hard_dupes": int(hard), "soft_dupes": int(soft)}


def check_coordinate_anomalies(df: pd.DataFrame, bbox) -> int:
    if not {"lat", "lon"}.issubset(df.columns):
        return 0
    lat = pd.to_numeric(df["lat"], errors="coerce")
    lon = pd.to_numeric(df["lon"], errors="coerce")
    lat_ok = lat.between(bbox[0], bbox[1], inclusive="both")
    lon_ok = lon.between(bbox[2], bbox[3], inclusive="both")
    return int((~(lat_ok & lon_ok)).sum())


def check_logic(df: pd.DataFrame) -> dict:
    issues = 0
    details = {}

    # 음수 값
    for c in ["male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled", "accessible"]:
        if c in df.columns:
            neg = int((pd.to_numeric(df[c], errors="coerce") < 0).sum())
            if neg:
                details[f"negative_{c}"] = neg
                issues += neg

    # disabled > total
    if {"male_wc", "male_wc_disabled"}.issubset(df.columns):
        m = int((pd.to_numeric(df["male_wc_disabled"], errors="coerce") >
                 pd.to_numeric(df["male_wc"], errors="coerce")).sum())
        if m:
            details["male_disabled_gt_total"] = m
            issues += m

    if {"female_wc", "female_wc_disabled"}.issubset(df.columns):
        f = int((pd.to_numeric(df["female_wc_disabled"], errors="coerce") >
                 pd.to_numeric(df["female_wc"], errors="coerce")).sum())
        if f:
            details["female_disabled_gt_total"] = f
            issues += f

    # accessible 0/1 이외
    if "accessible" in df.columns:
        acc = pd.to_numeric(df["accessible"], errors="coerce")
        invalid = int((~acc.isin([0, 1])).sum())
        if invalid:
            details["accessible_not_binary"] = invalid
            issues += invalid

    details["logic_errors"] = issues
    return details


# ---------- 리포팅 ----------
def append_markdown(report_path: str, text: str):
    ensure_parent(report_path)
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(text)


# ---------- 메인 ----------
def main():
    parser = argparse.ArgumentParser(description="Quality Assurance for facilities dataset")
    parser.add_argument("--fac", default="data/validated/facilities_valid.csv", help="시설 단위 유효 데이터 CSV")
    parser.add_argument("--report", default="reports/summary.md", help="마크다운 리포트 경로")
    parser.add_argument("--encoding", default="utf-8-sig", help="CSV 인코딩")
    parser.add_argument("--bbox", nargs=4, type=float, default=[35.0, 36.0, 128.0, 130.0],
                        metavar=("LAT_MIN", "LAT_MAX", "LON_MIN", "LON_MAX"), help="BBOX")
    parser.add_argument("--debug", action="store_true", help="디버그 로그 출력")
    args = parser.parse_args()

    # 로드
    fac = load_csv(args.fac, encoding=args.encoding)

    if args.debug:
        print("[DEBUG] fac shape:", fac.shape)
        print("[DEBUG] fac cols :", list(fac.columns)[:50])
        print("[DEBUG] fac head :\n", fac.head(3))

    # 체크 실행
    missing_df = check_missing(fac)
    dupes = check_duplicates(fac)
    coord_anom = check_coordinate_anomalies(fac, tuple(args.bbox))
    logic = check_logic(fac)

    # 요약 수치
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_rows = len(fac)
    top5_missing = missing_df.sort_values("missing_rate", ascending=False).head(5)

    # 리포트 작성
    md = []
    md.append(f"\n## [{ts}] QA Summary\n")
    md.append(f"- **Input**: `{args.fac}`  \n")
    md.append(f"- **Rows**: {total_rows}  \n")
    md.append(f"- **BBOX**: lat[{args.bbox[0]}, {args.bbox[1]}], lon[{args.bbox[2]}, {args.bbox[3]}]  \n")
    md.append(f"- **Duplicates**: hard={dupes['hard_dupes']}, soft={dupes['soft_dupes']}  \n")
    md.append(f"- **Coordinate anomalies** (BBOX out): {coord_anom}  \n")
    md.append(f"- **Logic errors**: {logic.get('logic_errors', 0)}  \n")

    if not top5_missing.empty:
        md.append("\n**Missing rate (Top 5)**\n\n")
        md.append("| column | missing_rate |\n|---|---|\n")
        for _, r in top5_missing.iterrows():
            md.append(f"| {r['column']} | {round(float(r['missing_rate'])*100, 2)}% |\n")

    detail_keys = [k for k in logic.keys() if k != "logic_errors" and logic[k] > 0]
    if detail_keys:
        md.append("\n**Logic error details**\n\n")
        for k in detail_keys:
            md.append(f"- {k}: {logic[k]}\n")

    md.append("\n---\n")
    append_markdown(args.report, "".join(md))
    print(f"[OK] 보고서 갱신: {args.report}")


if __name__ == "__main__":
    main()
