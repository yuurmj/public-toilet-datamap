# ml/feature_engineering.py

import pandas as pd
from sklearn.cluster import KMeans
import os
import re

# ---------------------------------------------------------
# 🔥 1) 부산 남구 실제 대표 행정동 인구수
# ---------------------------------------------------------
population_map = {
    "감만동": 13695,
    "대연동": 96746,
    "문현동": 42863,
    "용호동": 78690,
    "용당동": 7527,
    "우암동": 11706,
}

# ---------------------------------------------------------
# 🔥 2) 면적 정보 (km²)
# ---------------------------------------------------------
area_map = {
    "대연동": 5.45,
    "용호동": 4.88,
    "감만동": 4.13,
    "우암동": 2.50,
    "용당동": 2.33,
    "문현동": 1.83,
}

# ---------------------------------------------------------
# 🔥 3) 동 이름 정규화 함수 (하위동 → 대표동)
# ---------------------------------------------------------
def normalize_dong(name):
    if pd.isna(name):
        return "기타"

    name = name.strip()

    # "제3동" → "동"
    name = re.sub(r"제[0-9]+동$", "동", name)

    # "3동" → "동"
    name = re.sub(r"[0-9]+동$", "동", name)

    # 대표동 라벨링
    if "감만" in name: return "감만동"
    if "대연" in name: return "대연동"
    if "문현" in name: return "문현동"
    if "용호" in name: return "용호동"
    if "용당" in name: return "용당동"
    if "우암" in name: return "우암동"

    return "기타"

# ---------------------------------------------------------
# 🔥 4) 특징 추출 함수
# ---------------------------------------------------------
def extract_features(pop_rate=1.0):

    df = pd.read_csv("data/raw/toilets_namgu.csv")

    # ---------------------------------------
    # (1) 동 이름 정규화
    # ---------------------------------------
    df["dong"] = df["dong"].apply(normalize_dong)

    # ---------------------------------------
    # (2) 동별 집계
    # ---------------------------------------
    group = df.groupby("dong").agg(
        시설수=("toilet_id", "count"),
        장애인비율=("accessible", "mean"),
        남자칸수=("male_wc", "sum"),
        여자칸수=("female_wc", "sum"),
        남자장애인칸=("male_wc_disabled", "sum"),
        여자장애인칸=("female_wc_disabled", "sum"),
    ).reset_index()

    # ---------------------------------------
    # (3) 파생 컬럼
    # ---------------------------------------
    group["총장애인칸"] = group["남자장애인칸"] + group["여자장애인칸"]
    group["여성비율"] = group["여자칸수"] / (group["남자칸수"] + group["여자칸수"] + 1)

    # ---------------------------------------
    # (4) 군집 수 계산
    # ---------------------------------------
    coords = df[["lat", "lon"]].values
    kmeans = KMeans(n_clusters=4, random_state=42)
    df["cluster"] = kmeans.fit_predict(coords)

    cluster_counts = df.groupby("dong")["cluster"].nunique()
    group["군집수"] = group["dong"].map(cluster_counts).fillna(1)

    # ---------------------------------------
    # (5) 실제 인구 / 면적 매핑
    # ---------------------------------------
    group["인구"] = group["dong"].map(population_map).fillna(0)
    group["면적"] = group["dong"].map(area_map).fillna(2.5)

    # ---------------------------------------
    # (6) 저장
    # ---------------------------------------
    os.makedirs("data/processed", exist_ok=True)
    group.to_csv("data/processed/group_features.csv", index=False, encoding="utf-8-sig")

    print("✔ feature 저장 완료 — 실제 인구 + 면적 + 대표동 정규화 적용됨")
