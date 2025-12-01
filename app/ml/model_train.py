# ml/model_train.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_model(budget_rate=1.0):
    df = pd.read_csv("data/processed/group_features.csv")

    df["적정시설수"] = (
        (df["인구"] / (2500 / budget_rate)) +
        (df["면적"] * 2.5) +
        (df["장애인비율"] * (8 * budget_rate))
    ).round()

    X = df[[
        "시설수", "장애인비율", "남자칸수", "여자칸수",
        "총장애인칸", "여성비율", "군집수", "인구", "면적"
    ]]
    y = df["적정시설수"]

    model = RandomForestRegressor(n_estimators=300, random_state=42)
    model.fit(X, y)

    joblib.dump(model, "data/processed/recommend_model.pkl")
    print("✔ 모델 저장 완료")
