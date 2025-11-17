#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 동 이름 정규화 스크립트

"""
사용 예시

python scripts/normalize_dong_names.py \
  --input data/raw/toilets_namgu.csv \
  --output data/processed/toilets_namgu_normalized.csv \
  --report data/processed/normalize_report.csv \
  --fallback-legal-as-admin \
  --report-missing-per-legal
"""

import re
import sys
import argparse
import unicodedata
from typing import Optional, Tuple

import pandas as pd

# ----- 설정: 표준 목록 -----

LEGAL_DONG_ENUM = ["대연동", "용호동", "문현동", "감만동", "우암동", "용당동"]

ADMIN_DONG_ENUM = [
    "대연1동", "대연3동", "대연4동", "대연5동", "대연6동",
    "용호1동", "용호2동", "용호3동", "용호4동",
    "문현1동", "문현2동", "문현3동", "문현4동",
    "감만1동", "감만2동",
    "우암동", "용당동",
]

# 내부 코드 규칙
ADMIN_CODE_PREFIX = "NG-"  # Nam-gu
ADMIN_CODE_MAP = {
    # 대연
    "대연1동": "DY1", "대연3동": "DY3", "대연4동": "DY4", "대연5동": "DY5", "대연6동": "DY6",
    # 용호
    "용호1동": "YH1", "용호2동": "YH2", "용호3동": "YH3", "용호4동": "YH4",
    # 문현
    "문현1동": "MH1", "문현2동": "MH2", "문현3동": "MH3", "문현4동": "MH4",
    # 감만
    "감만1동": "GM1", "감만2동": "GM2",
    # 단일
    "우암동": "UA", "용당동": "YD",
}

# 한글 숫자 → 아라비아 숫자 매핑
KNUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5", "육": "6", "칠": "7", "팔": "8", "구": "9", "영": "0", "공": "0"}

# 주소에서 행정동 추출용 정규식
ADMIN_PATTERN = re.compile(
    r"(대연(?:제)?[123456]동|용호(?:제)?[1234]동|문현(?:제)?[1234]동|감만(?:제)?[12]동|우암동|용당동)"
)

# ----- 유틸 함수 -----

def normalize_spaces(text: str) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text.strip())
    return text

def normalize_korean_numbers(text: str) -> str:
    """대연제1동/대연1동/대연일동 → 대연1동 형태로 통일"""
    if not text:
        return text
    t = text
    # '제' 제거
    t = t.replace("제", "")
    # 한글 숫자 → 숫자
    for k, v in KNUM.items():
        t = t.replace(k, v)
    # '  동' 등 공백 정리
    t = t.replace(" 동", "동")
    return t

def to_legal_dong(raw_dong: str) -> Optional[str]:
    """법정동 표준화: '대연동/문현동/...' 중 하나로 매핑"""
    if not raw_dong:
        return None
    s = normalize_spaces(raw_dong)
    # 숫자 접미 제거 후 동 붙이기 (대연, 대연4동 등 → 대연동)
    s_basic = re.sub(r"[0-9]+동$", "동", normalize_korean_numbers(s))
    if s_basic in ["대연", "용호", "문현", "감만", "우암", "용당"]:
        s_basic = s_basic + "동"
    return s_basic if s_basic in LEGAL_DONG_ENUM else None

def to_admin_dong(source: str) -> Optional[str]:
    """
    행정동 표준화: 주소/원문 문자열에서 추출.
    - 대연제4동/대연4동/대연사동/대연 四 동 → 대연4동
    """
    if not source:
        return None
    s = normalize_spaces(source)
    m = ADMIN_PATTERN.search(s)
    if not m:
        return None
    cand = normalize_korean_numbers(m.group(1))
    # 숫자 앞 0 제거 등 소정리
    cand = re.sub(r"([가-힣]+)0*([1-9])동$", r"\1\2동", cand)
    return cand if cand in ADMIN_DONG_ENUM else None

def admin_code(admin_dong: Optional[str]) -> Optional[str]:
    if not admin_dong:
        return None
    code = ADMIN_CODE_MAP.get(admin_dong)
    return ADMIN_CODE_PREFIX + code if code else None

def latlon_in_busan(lat: float, lon: float) -> bool:
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return False
    # 부산 근사 범위 (느슨한 검증)
    return (34.0 <= lat <= 36.5) and (127.0 <= lon <= 131.0)

# ----- 메인 처리 -----

def normalize_frame(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    반환:
      - normalized_df: 정규화/보완된 본 데이터
      - report_df: 경고/미매핑 리포트
    """
    logs = []

    # 컬럼 보정
    for col in ["name", "addr", "dong", "district"]:
        if col not in df.columns:
            df[col] = ""

    # 도시/구 고정
    df["city"] = "부산광역시"
    # 입력에 district가 있으면 신뢰, 없거나 공백이면 남구로 보정
    df["district"] = df["district"].apply(lambda x: "남구" if normalize_spaces(x) == "" else normalize_spaces(x))

    # 법정동
    df["legal_dong"] = df["dong"].apply(lambda x: to_legal_dong(x) or "")

    # 행정동: 우선 기존 컬럼이 있다면 사용, 없으면 주소/이름에서 추출
    if "admin_dong" in df.columns:
        df["admin_dong"] = df["admin_dong"].apply(lambda x: normalize_korean_numbers(normalize_spaces(x)) if pd.notna(x) else "")
    else:
        df["admin_dong"] = ""

    # 주소/이름에서 추출 (비어있는 경우만)
    mask_empty_admin = df["admin_dong"].eq("")
    df.loc[mask_empty_admin, "admin_dong"] = df.loc[mask_empty_admin, "addr"].apply(lambda x: to_admin_dong(x) or "")
    # 여전히 비었다면 name에서도 시도
    mask_empty_admin = df["admin_dong"].eq("")
    df.loc[mask_empty_admin, "admin_dong"] = df.loc[mask_empty_admin, "name"].apply(lambda x: to_admin_dong(x) or "")

    # 행정동이 끝까지 비어 있으면, 법정동 단일 동(우암/용당)은 그대로 채움
    mask_still_empty = df["admin_dong"].eq("")
    df.loc[mask_still_empty & df["legal_dong"].eq("우암동"), "admin_dong"] = "우암동"
    df.loc[mask_still_empty & df["legal_dong"].eq("용당동"), "admin_dong"] = "용당동"

    # 내부 코드
    df["admin_dong_code"] = df["admin_dong"].apply(admin_code)

    # 좌표 검증 로그
    if "lat" in df.columns and "lon" in df.columns:
        bad_geo = ~df.apply(lambda r: latlon_in_busan(r.get("lat"), r.get("lon")), axis=1)
        if bad_geo.any():
            logs.append(pd.DataFrame({
                "issue": "OUT_OF_RANGE_LATLON",
                "toilet_id": df.loc[bad_geo, "toilet_id"] if "toilet_id" in df.columns else "",
                "name": df.loc[bad_geo, "name"],
                "lat": df.loc[bad_geo, "lat"],
                "lon": df.loc[bad_geo, "lon"],
            }))

    # 미매핑 로그: legal/admin 둘 중 하나라도 비었으면 보고
    missing_mask = df["legal_dong"].eq("") | df["admin_dong"].eq("")
    if missing_mask.any():
        logs.append(pd.DataFrame({
            "issue": "MISSING_DONG_MAPPING",
            "toilet_id": df.loc[missing_mask, "toilet_id"] if "toilet_id" in df.columns else "",
            "name": df.loc[missing_mask, "name"],
            "addr": df.loc[missing_mask, "addr"],
            "raw_dong": df.loc[missing_mask, "dong"] if "dong" in df.columns else "",
            "legal_dong": df.loc[missing_mask, "legal_dong"],
            "admin_dong": df.loc[missing_mask, "admin_dong"],
        }))

    report_df = pd.concat(logs, ignore_index=True) if logs else pd.DataFrame(columns=["issue"])
    return df, report_df


def parse_args():
    ap = argparse.ArgumentParser(description="Normalize legal/admin dong names for Nam-gu dataset.")
    ap.add_argument("--input", "-i", required=True, help="입력 CSV 경로 (예: data/processed/toilets_namgu_cleaned.csv)")
    ap.add_argument("--output", "-o", required=True, help="정규화 CSV 경로 (예: data/processed/toilets_namgu_normalized.csv)")
    ap.add_argument("--report", "-r", default="", help="리포트 CSV 경로 (예: data/processed/normalize_report.csv)")
    # 추가 옵션
    ap.add_argument("--fallback-legal-as-admin", action="store_true",
                    help="행정동 미매핑 시 admin_dong을 legal_dong으로 대체합니다(임시 폴백).")
    ap.add_argument("--report-missing-per-legal", action="store_true",
                    help="법정동별 행정동 미매핑 건수 요약을 콘솔에 출력합니다.")
    return ap.parse_args()


def main():
    args = parse_args()

    df = pd.read_csv(args.input)
    normalized, report = normalize_frame(df)

    # --- 폴백 처리 (옵션) ---
    if args.fallback_legal_as_admin:
        missing_mask = normalized["admin_dong"].eq("")
        # 우암/용당은 위에서 이미 채워졌으므로, 나머지 미매핑 건에 한해 법정동 → 행정동 대입
        normalized.loc[missing_mask, "admin_dong"] = normalized.loc[missing_mask, "legal_dong"]
        # 코드 재부여
        normalized["admin_dong_code"] = normalized["admin_dong"].apply(admin_code)

    # --- 리포트 요약 (옵션) ---
    if args.report_missing_per_legal:
        missing_mask = normalized["admin_dong"].eq("")
        summary = (normalized.assign(missing=missing_mask)
                   .groupby("legal_dong", dropna=False)["missing"].sum()
                   .sort_values(ascending=False))
        print("[요약] 법정동별 행정동 미매핑 건수")
        for k, v in summary.items():
            print(f" - {k if k else '(빈값)'}: {int(v)}건")

    # 저장
    normalized.to_csv(args.output, index=False, encoding="utf-8-sig")
    if args.report:
        report.to_csv(args.report, index=False, encoding="utf-8-sig")

    # 요약 출력
    total = len(normalized)
    missing_legal = (normalized["legal_dong"] == "").sum()
    missing_admin = (normalized["admin_dong"] == "").sum()
    print(f"[완료] 총 {total}행 처리 | 미매핑(법정동): {missing_legal} | 미매핑(행정동): {missing_admin}")
    if args.report and len(report) > 0:
        print(f"[리포트] {args.report} 에 {len(report)}건 기록")


if __name__ == "__main__":
    main()