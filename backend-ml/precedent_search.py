from pathlib import Path

import pandas as pd


project_dir = Path(__file__).parent
data_path = project_dir / "data" / "processed" / "cases_clean.csv"


def find_similar_cases(category: str, case_type: str, limit: int = 10) -> pd.DataFrame:
    data = pd.read_csv(
        data_path,
        usecols=["name", "case_category", "case_type", "label"],
        dtype="string",
    )

    category_query = category.strip().casefold()
    type_query = case_type.strip().casefold()

    category_matches = (
        data["case_category"].fillna("").str.strip().str.casefold()
        == category_query
    )
    type_matches = (
        data["case_type"].fillna("").str.strip().str.casefold()
        == type_query
    )

    scores = category_matches.astype(int) + type_matches.astype(int)
    results = data.loc[scores > 0].copy()
    results.insert(0, "match_score", scores.loc[scores > 0].to_numpy())

    results["match_basis"] = results["match_score"].map(
        {2: "same category and type", 1: "same category or type"}
    )

    results["name"] = results["name"].fillna("").replace("", "[name unavailable]")

    return (
        results.sort_values(
            ["match_score", "name"],
            ascending=[False, True],
            kind="stable",
        )
        .head(limit)
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    if not data_path.is_file():
        raise FileNotFoundError(f"Cleaned data not found: {data_path}")

    category = input("Enter case category (for example, Civil): ")
    case_type = input("Enter case type (for example, Appeal): ")

    matches = find_similar_cases(category, case_type)

    if matches.empty:
        print("No cases matched that category or type.")
    else:
        print("\nMatching historical cases:")
        print(matches.to_string(index=False))