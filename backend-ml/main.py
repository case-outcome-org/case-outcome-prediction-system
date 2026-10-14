from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Case Outcome Prediction System")

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "cases_clean.csv"
MODEL_FILE = PROJECT_DIR / "models" / "outcome_model_v2.joblib"
DB_FILE = PROJECT_DIR / "data" / "cases.db"

WARNING = (
    "Experimental model: test accuracy was 39.5%, balanced accuracy "
    "was 46.4%, and macro F1 was 0.395 on one random test split. "
    "Scores are not calibrated confidence estimates. This is not legal advice."
)


def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                case_category TEXT NOT NULL,
                case_type TEXT NOT NULL,
                description TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'User',
                predicted_outcome TEXT,
                model_scores TEXT,
                prediction_status TEXT NOT NULL,
                warning TEXT,
                created_at TEXT NOT NULL
            )
        """)


initialize_database()


class CaseInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    case_category: str = Field(default="civil", max_length=100)
    case_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=10000)
    role: str = Field(default="User", max_length=30)


def predict_outcome(category: str, case_type: str):
    if not MODEL_FILE.is_file():
        raise HTTPException(
            status_code=404,
            detail="Experimental model not found. Run train_model.py first.",
        )

    import joblib

    model = joblib.load(MODEL_FILE)

    category_type = f"{category.casefold()}|{case_type.casefold()}"

    features = pd.DataFrame([{
        "case_category": category,
        "case_type": case_type,
        "category_type": category_type,
    }])

    predicted_outcome = str(model.predict(features)[0])
    scores = model.predict_proba(features)[0]

    model_scores = {
        str(label): round(float(score), 4)
        for label, score in zip(model.classes_, scores)
    }

    return predicted_outcome, model_scores


def row_to_dict(row):
    item = dict(row)
    item["model_scores"] = (
        json.loads(item["model_scores"])
        if item["model_scores"]
        else None
    )
    return item


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
        df["case_category"].fillna("").astype(str).str.strip().str.casefold()
        == requested_category
    )
    type_match = (
        df["case_type"].fillna("").astype(str).str.strip().str.casefold()
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
        "match_score", "name", "case_category", "case_type", "label",
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
    category = str(payload.get("case_category", "")).strip() or "Unknown"
    case_type = str(payload.get("case_type", "")).strip() or "Unknown"

    predicted_outcome, model_scores = predict_outcome(category, case_type)

    return {
        "predicted_outcome": predicted_outcome,
        "model_scores": model_scores,
        "status": "experimental demo only",
        "warning": WARNING,
    }


@app.post("/cases")
def create_case(payload: CaseInput):
    title = payload.title.strip()
    category = payload.case_category.strip() or "Unknown"
    case_type = payload.case_type.strip()
    description = payload.description.strip()
    role = payload.role.strip()

    if not title or not case_type or not description:
        raise HTTPException(
            status_code=422,
            detail="Title, case type, and description are required.",
        )

    # Generate the prediction before saving the case.
    # If prediction fails, no misleading successful case is stored.
    predicted_outcome, model_scores = predict_outcome(category, case_type)

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO cases (
                title, case_category, case_type, description, role,
                predicted_outcome, model_scores, prediction_status,
                warning, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                category,
                case_type,
                description,
                role,
                predicted_outcome,
                json.dumps(model_scores),
                "Prediction received",
                WARNING,
                created_at,
            ),
        )

        case_id = cursor.lastrowid
        row = connection.execute(
            "SELECT * FROM cases WHERE id = ?", (case_id,)
        ).fetchone()

    return row_to_dict(row)


@app.get("/cases")
def list_cases():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM cases ORDER BY id DESC"
        ).fetchall()

    return {"cases": [row_to_dict(row) for row in rows]}


@app.get("/cases/{case_id}")
def get_case(case_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM cases WHERE id = ?", (case_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    return row_to_dict(row)


@app.get("/case-analytics")
def case_analytics():
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM cases"
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT predicted_outcome, COUNT(*) AS count
            FROM cases
            WHERE predicted_outcome IS NOT NULL
            GROUP BY predicted_outcome
            """
        ).fetchall()

        status_rows = connection.execute(
            """
            SELECT prediction_status, COUNT(*) AS count
            FROM cases
            GROUP BY prediction_status
            """
        ).fetchall()

    outcome_counts = {
        row["predicted_outcome"]: row["count"]
        for row in rows
    }

    return {
        "total_cases": total,
        "outcome_counts": outcome_counts,
        "status_counts": {
            row["prediction_status"]: row["count"]
            for row in status_rows
        },
    }