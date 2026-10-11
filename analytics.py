from pathlib import Path

import pandas as pd


project_dir = Path(__file__).parent
data_path = project_dir / "data" / "processed" / "cases_clean.csv"

if not data_path.is_file():
    raise FileNotFoundError(f"Cleaned data not found: {data_path}")

data = pd.read_csv(
    data_path,
    usecols=["case_category", "case_type", "label"],
    dtype="string",
)

print(f"Total cases: {len(data)}")
print("\nOutcome counts:")
print(data["label"].value_counts().to_string())

print("\nOutcome percentages:")
percentages = data["label"].value_counts(normalize=True).mul(100).round(1)
print(percentages.astype(str).add("%").to_string())

print("\nOutcomes by case category:")
print(pd.crosstab(data["case_category"], data["label"]).to_string())

top_types = data["case_type"].value_counts().head(10).index
common_types = data[data["case_type"].isin(top_types)]

print("\nOutcomes for the 10 most common case types:")
print(pd.crosstab(common_types["case_type"], common_types["label"]).to_string())