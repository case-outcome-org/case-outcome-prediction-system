from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Case Outcome Prediction System")

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "cases_clean.csv"
)


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

    outcomes_by_category = category_table.to_dict(orient="index")

    return {
        "total_cases": total_cases,
        "outcome_counts": outcome_counts,
        "outcome_percentages": outcome_percentages,
        "outcomes_by_category": outcomes_by_category,
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
        df["case_category"].fillna("").astype(str).str.strip().str.casefold()
        == requested_category
    )
    type_match = (
        df["case_type"].fillna("").astype(str).str.strip().str.casefold()
        == requested_type
    )

    df["match_score"] = category_match.astype(int) + type_match.astype(int)
    df = df[df["match_score"] > 0].copy()

    df["match_basis"] = "same case type"
    df.loc[category_match.loc[df.index] & ~type_match.loc[df.index], "match_basis"] = (
        "same category"
    )
    df.loc[category_match.loc[df.index] & type_match.loc[df.index], "match_basis"] = (
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
    model_file = (
        Path(__file__).resolve().parent
        / "models"
        / "outcome_model.joblib"
    )

    if not model_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="Trained model not found. Run train_model.py first.",
        )

    category = str(payload.get("case_category", "")).strip() or "Unknown"
    case_type = str(payload.get("case_type", "")).strip() or "Unknown"

    import joblib

    model = joblib.load(model_file)
    features = pd.DataFrame(
        [{"case_category": category, "case_type": case_type}]
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
            "This model had 40.2% test accuracy and did not identify any "
            "Accepted cases in its evaluation. Scores are not verified "
            "confidence estimates. This is not legal advice."
        ),
    }