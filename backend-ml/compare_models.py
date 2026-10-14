from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


project_dir = Path(__file__).parent
data_path = project_dir / "data" / "processed" / "cases_clean.csv"
base_features = ["case_category", "case_type"]
features = base_features + ["category_type"]

data = pd.read_csv(data_path, usecols=base_features + ["label"], dtype="string")
data["label"] = data["label"].str.strip()
data = data[data["label"].notna() & data["label"].ne("")].copy()

X = data[base_features].fillna("Unknown")
X["category_type"] = (
    X["case_category"].str.casefold() + "|" + X["case_type"].str.casefold()
)
y = data["label"]
labels = sorted(y.unique())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


def make_logistic_model(class_weight):
    return Pipeline(
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
                LogisticRegression(
                    max_iter=1000,
                    class_weight=class_weight,
                ),
            ),
        ]
    )


models = [
    ("Most-common baseline", DummyClassifier(strategy="most_frequent")),
    ("Logistic regression, balanced", make_logistic_model("balanced")),
    ("Logistic regression, unweighted", make_logistic_model(None)),
]

for name, model in models:
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print(f"\n--- {name} ---")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.3f}")
    print(f"Balanced accuracy: {balanced_accuracy_score(y_test, predictions):.3f}")
    print(f"Macro F1: {f1_score(y_test, predictions, average='macro', zero_division=0):.3f}")
    print(classification_report(y_test, predictions, labels=labels, zero_division=0))