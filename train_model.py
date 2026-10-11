from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


project_dir = Path(__file__).parent
data_path = project_dir / "data" / "processed" / "cases_clean.csv"
model_path = project_dir / "models" / "outcome_model.joblib"

if not data_path.is_file():
    raise FileNotFoundError(f"Cleaned data not found: {data_path}")

if model_path.exists():
    raise FileExistsError(f"Refusing to overwrite existing model: {model_path}")

features = ["case_category", "case_type"]
data = pd.read_csv(
    data_path,
    usecols=features + ["label"],
    dtype="string",
)

X = data[features].fillna("Unknown")
y = data["label"].str.strip()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = Pipeline(
    steps=[
        (
            "encode",
            ColumnTransformer(
                [
                    (
                        "categories",
                        OneHotEncoder(handle_unknown="ignore"),
                        features,
                    )
                ]
            ),
        ),
        (
            "classifier",
            LogisticRegression(max_iter=1000, class_weight="balanced"),
        ),
    ]
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)
labels = sorted(y.unique())

print(f"Training rows: {len(X_train)}")
print(f"Test rows: {len(X_test)}")
print(f"Accuracy: {accuracy_score(y_test, predictions):.3f}")
print("\nClass report:")
print(classification_report(y_test, predictions, zero_division=0))
print("Confusion matrix (actual rows, predicted columns):")
print(
    pd.DataFrame(
        confusion_matrix(y_test, predictions, labels=labels),
        index=labels,
        columns=labels,
    )
)

model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_path)
print(f"\nBaseline model saved to: {model_path}")