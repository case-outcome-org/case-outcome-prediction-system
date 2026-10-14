from pathlib import Path

import pandas as pd


zip_path = Path.home() / "Downloads" / "archive.zip"
output_path = Path(__file__).parent / "data" / "processed" / "cases_clean.csv"

if not zip_path.is_file():
    raise FileNotFoundError(f"Dataset ZIP not found: {zip_path}")

if output_path.exists():
    raise FileExistsError(
        f"Refusing to overwrite existing file: {output_path}"
    )

columns = ["name", "case_category", "case_type", "label"]

df = pd.read_csv(
    zip_path,
    compression="zip",
    usecols=columns,
    dtype="string",
)

rows_before = len(df)

df["label"] = df["label"].str.strip()
has_label = df["label"].notna() & df["label"].ne("")
dropped_rows = int((~has_label).sum())
df = df.loc[has_label].copy()

for column in ("case_category", "case_type"):
    df[column] = df[column].fillna("").str.strip()
    df[column] = df[column].replace("", "Unknown")

df["name"] = df["name"].fillna("").str.strip()

output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Rows read: {rows_before}")
print(f"Rows skipped because label was blank: {dropped_rows}")
print(f"Rows saved: {len(df)}")
print("\nOutcome counts:")
print(df["label"].value_counts().sort_index().to_string())
print("\nRows with Unknown category:", int((df["case_category"] == "Unknown").sum()))
print("Rows with Unknown type:", int((df["case_type"] == "Unknown").sum()))
print(f"\nCleaned file saved to: {output_path}")