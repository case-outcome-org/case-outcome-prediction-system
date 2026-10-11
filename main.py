from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Case Outcome Prediction System")

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "cases_clean.csv"
MODEL_FILE = PROJECT_DIR / "models" / "outcome_model_v2.joblib"


@app.get("/")
def home():
    return {"message": "Case Outcome Prediction System API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/analytics")
def analytics():
    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Cleaned dataset not found. Run prepare_data.py first.",
        )

    df = pd.read_csv(DATA_FILE)
    total_cases = len(df)

    outcome_counts = df["label"].value_counts().to_dict()
    outcome_percentages = {
        label: round(count * 100 / total_cases, 1)
        for label, count in outcome_counts.items()
    }

    category_table = (
        df.groupby(["case_category", "label"])
        .size()
        .unstack(fill_value=0)
    )

    return {
        "total_cases": total_cases,
        "outcome_counts": outcome_counts,
        "outcome_percentages": outcome_percentages,
        "outcomes_by_category": category_table.to_dict(orient="index"),
    }


@app.get("/similar-cases")
def similar_cases(category: str, case_type: str, limit: int = 10):
    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Cleaned dataset not found. Run prepare_data.py first.",
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50.",
        )

    df = pd.read_csv(DATA_FILE)

    requested_category = category.strip().casefold()
    requested_type = case_type.strip().casefold()

    category_match = (
        df["case_category"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
        == requested_category
    )
    type_match = (
        df["case_type"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
        == requested_type
    )

    df["match_score"] = category_match.astype(int) + type_match.astype(int)
    df = df[df["match_score"] > 0].copy()

    matched_category = category_match.loc[df.index]
    matched_type = type_match.loc[df.index]

    df["match_basis"] = "same case type"
    df.loc[matched_category & ~matched_type, "match_basis"] = "same category"
    df.loc[matched_category & matched_type, "match_basis"] = (
        "same category and type"
    )

    columns = [
        "match_score",
        "name",
        "case_category",
        "case_type",
        "label",
        "match_basis",
    ]

    matches = (
        df.sort_values("match_score", ascending=False)[columns]
        .head(limit)
        .to_dict(orient="records")
    )

    return {
        "query": {"category": category, "case_type": case_type},
        "matches": matches,
    }


@app.post("/predict")
def predict(payload: dict):
    if not MODEL_FILE.is_file():
        raise HTTPException(
            status_code=404,
            detail="Experimental model not found. Run train_model.py first.",
        )

    category = str(payload.get("case_category", "")).strip() or "Unknown"
    case_type = str(payload.get("case_type", "")).strip() or "Unknown"
    category_type = f"{category.casefold()}|{case_type.casefold()}"

    import joblib

    model = joblib.load(MODEL_FILE)

    features = pd.DataFrame(
        [
            {
                "case_category": category,
                "case_type": case_type,
                "category_type": category_type,
            }
        ]
    )

    predicted_outcome = str(model.predict(features)[0])
    scores = model.predict_proba(features)[0]
    model_scores = {
        str(label): round(float(score), 4)
        for label, score in zip(model.classes_, scores)
    }

    return {
        "predicted_outcome": predicted_outcome,
        "model_scores": model_scores,
        "status": "experimental demo only",
        "warning": (
            "Experimental model: test accuracy was 39.5%, balanced accuracy "
            "was 46.4%, and macro F1 was 0.395 on one random test split. "
            "Scores are not calibrated confidence estimates. This is not "
            "legal advice."
        ),
    }