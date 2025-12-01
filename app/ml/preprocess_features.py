"""
사용 예시
---------
$ python ml/preprocess_features.py \
    --input data/processed/by_dong.csv \
    --output-dir ml/processed \
    --label gap_score \
    --drop-cols notes source updated_at version admin_dong_code
"""

import argparse
import json
import os
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib


REQUIRED_COLS = [
    # 식별/범주
    "city", "district", "legal_dong", "admin_dong",
    # 좌표 요약
    "centroid_lat", "centroid_lng",
    # 참조 값
    "area_km2", "population",
    # 화장실 집계
    "toilets_total", "toilets_accessible",
    "male_urinals_total", "male_toilets_total", "female_toilets_total",
]

DERIVED_FORMULAE = {
    "toilets_per_10k": lambda df: df["toilets_total"] / df["population"] * 10000,
    "toilets_density_per_km2": lambda df: df["toilets_total"] / df["area_km2"].replace(0, np.nan),
    "accessible_ratio": lambda df: (df["toilets_accessible"] / df["toilets_total"].replace(0, np.nan))
}


def parse_args():
    ap = argparse.ArgumentParser(description="Preprocess features for ML from by_dong dataset.")
    ap.add_argument("--input", "-i", default="data/processed/by_dong.csv", help="입력 CSV 경로")
    ap.add_argument("--output-dir", "-o", default="ml/processed", help="전처리 산출물 저장 디렉터리")
    ap.add_argument("--label", "-y", default="", help="레이블 컬럼명 (선택)")
    ap.add_argument("--drop-cols", nargs="*", default=[], help="제거할 컬럼 리스트(공백 구분)")
    ap.add_argument("--scaler", choices=["standard"], default="standard", help="수치형 스케일러 선택")
    return ap.parse_args()


def ensure_required(df: pd.DataFrame, required: List[str]):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {missing}")


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col, fn in DERIVED_FORMULAE.items():
        if col not in df.columns:
            df[col] = fn(df)
    # NaN 발생(분모 0 등) → 0으로 대체
    df["toilets_density_per_km2"] = df["toilets_density_per_km2"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["accessible_ratio"] = df["accessible_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["toilets_per_10k"] = df["toilets_per_10k"].replace([np.inf, -np.inf], np.nan).fillna(0)
    return df


def build_preprocessor(numeric_cols: List[str], categorical_cols: List[str]) -> ColumnTransformer:
    numeric_pipeline = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])

    categorical_pipeline = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols)
        ],
        remainder="drop",
        verbose_feature_names_out=False
    )
    return preprocessor


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # 1) 로드
    df = pd.read_csv(args.input)
    ensure_required(df, REQUIRED_COLS)

    # 2) 파생 특성 보강
    df = add_derived_columns(df)

    # 3) 드롭할 컬럼 제거
    drop_cols = set(args.drop_cols or [])
    # 학습에 불필요할 확률이 높은 기본 제거 후보(필요 시 유지 가능)
    default_drop = {"city", "district", "updated_at", "version", "source", "notes", "admin_dong_code"}
    drop_cols = list(drop_cols.union(default_drop).intersection(set(df.columns)))
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 4) 레이블 분리(선택)
    y = None
    if args.label:
        if args.label not in df.columns:
            raise ValueError(f"레이블 컬럼 '{args.label}' 이(가) 존재하지 않습니다.")
        y = df[args.label].values
        df = df.drop(columns=[args.label])

    # 5) 열 타입 별 분리
    categorical_cols = ["legal_dong", "admin_dong"]
    categorical_cols = [c for c in categorical_cols if c in df.columns]

    numeric_cols = [c for c in df.columns if c not in categorical_cols]

    # 6) 전처리기 구성 및 학습
    preprocessor = build_preprocessor(numeric_cols=numeric_cols, categorical_cols=categorical_cols)
    X = preprocessor.fit_transform(df)

    # 7) 특성명 추출
    # 수치형
    num_features = numeric_cols
    # 범주형(원-핫)
    ohe: OneHotEncoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_feature_names = ohe.get_feature_names_out(categorical_cols).tolist() if categorical_cols else []
    feature_names = num_features + cat_feature_names

    # 8) 산출물 저장
    np.save(os.path.join(args.output_dir, "X.npy"), X)
    if y is None:
        np.save(os.path.join(args.output_dir, "y.npy"), np.array([]))
    else:
        np.save(os.path.join(args.output_dir, "y.npy"), y)

    with open(os.path.join(args.output_dir, "feature_names.json"), "w", encoding="utf-8") as f:
        json.dump(feature_names, f, ensure_ascii=False, indent=2)

    joblib.dump(preprocessor, os.path.join(args.output_dir, "preprocessor.pkl"))

    # 디버그 프리뷰(원본 5행)
    df.head(5).to_parquet(os.path.join(args.output_dir, "dataset_preview.parquet"), index=False)

    print(f"[완료] 전처리 완료: X.shape={X.shape}, y.shape={(0 if y is None else y.shape)}")
    print(f" - 저장 경로: {args.output_dir}")
    print(f" - 수치형 특성: {len(numeric_cols)}개, 범주형 특성(원-핫 후): {len(cat_feature_names)}개")
    if args.label:
        print(f" - 레이블: '{args.label}'")


if __name__ == "__main__":
    main()