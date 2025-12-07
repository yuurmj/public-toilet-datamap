# ml/run_prediction.py
import pandas as pd
import joblib
import os

def run_prediction(pop_rate=1.0, budget_rate=1.0, acc_min_rate=0.0):
    from ml.feature_engineering import extract_features
    from ml.model_train import train_model

    extract_features(pop_rate=pop_rate)
    train_model(budget_rate=budget_rate)

    df = pd.read_csv("data/processed/group_features.csv")

    df.rename(columns={"dong": "행정동"}, inplace=True)

    model = joblib.load("data/processed/recommend_model.pkl")

    X = df[[
        "시설수", "장애인비율", "남자칸수", "여자칸수",
        "총장애인칸", "여성비율", "군집수", "인구", "면적"
    ]]

    df["권장설치수"] = model.predict(X).round().astype(int)

    # 기본 등급
    def base_grade(r, need):
        if r < need: return "부족"
        if r == need: return "적정"
        return "과잉"

    df["예측등급"] = [base_grade(r,n) for r,n in zip(df["시설수"], df["권장설치수"])]

    # 🔥 옵션 B: 적정인데 장애인 비율 미달이면 → 부족으로 강등
    for i in df.index:
        if df.loc[i, "예측등급"] == "적정" and df.loc[i, "장애인비율"] < acc_min_rate:
            df.loc[i, "예측등급"] = "부족"

    # 설치율 계산
    df["설치율값"] = (df["시설수"] / df["권장설치수"].replace(0,1)) * 100
    df["설치율"] = df["설치율값"].round().astype(int).astype(str) + "%"

    df["인구대비화장실수"] = df["시설수"].apply(lambda x: f"{x}/18000명")

    result = df[[
        "행정동", "예측등급", "권장설치수", "설치율",
        "인구대비화장실수", "시설수",
        "장애인비율", "여성비율", "군집수", "인구", "면적"
    ]]

    os.makedirs("data/processed", exist_ok=True)
    result.to_json("data/processed/prediction_result.json", orient="records", indent=4, force_ascii=False)

    return result
