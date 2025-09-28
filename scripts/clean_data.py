import pandas as pd
from pathlib import Path

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
    df.rename(columns=rename_map, inplace=True) 

    # 2. toilet_id 자동 생성
    if "toilet_id" not in df.columns:
        df.insert(0, 'toilet_id', [f"{district_code}-{i:04d}" for i in range(1, len(df)+1)])

    # 3. 데이터 타입 변환
    numeric_cols = ["lat", "lon", "male_wc", "female_wc", "male_wc_disabled", "female_wc_disabled"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. 결측치 처리
    df = df.dropna(subset=["lat", "lon"])

    # 5. w저장
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"전처리 완료! 저장: {output_path}")

if __name__ == "__main__":
    clean_toilets_csv(
        "data/raw/toilets_namgu.csv",
        "data/processed/toilets_namgu_cleaned.csv",
        district_code="NMG"
    )