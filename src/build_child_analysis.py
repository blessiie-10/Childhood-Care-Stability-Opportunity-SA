"""Build the child-level GHS 2025 analysis file and first weighted summaries."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from inspect_ghs import discover_files, normalise_columns, read_data


PROCESSED_DIR = ROOT / "data" / "processed"
TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"

GROUP_ORDER = ["Both parents", "Mother only", "Father only", "Neither parent"]


def extract_leading_number(series: pd.Series) -> pd.Series:
    """Extract the numeric code from DataFirst labels such as '1. Yes'."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    extracted = series.astype("string").str.extract(
        r"^\s*(-?\d+(?:\.\d+)?)\.", expand=False
    )
    return pd.to_numeric(extracted, errors="coerce")


def convert_analysis_codes(person: pd.DataFrame, household: pd.DataFrame) -> None:
    person_columns = {
        "age",
        "sex",
        "prov",
        "hhc_moth_parthh",
        "hhc_fath_parthh",
        "edu_attend",
        "edu_same",
        "soc_grant",
        "soc_grant_csg",
        "soc_grant_csg_topup",
        "soc_grant_fos",
        "person_wgt",
    }
    household_columns = {
        "fsd_hung_child",
        "fsd_worried",
        "fsd_healthy",
        "totmhinc",
        "hholdsz",
        "house_wgt",
        "hwl_assets_comp",
        "com_int_fixed",
    }
    for column in person_columns & set(person.columns):
        person[column] = extract_leading_number(person[column])
    for column in household_columns & set(household.columns):
        household[column] = extract_leading_number(household[column])

    # DataFirst uses 9,999,999 as the unspecified household-income code.
    if "totmhinc" in household.columns:
        household.loc[household["totmhinc"] == 9_999_999, "totmhinc"] = pd.NA


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise KeyError(f"{label} file is missing required columns: {missing}")


def derive_living_arrangement(frame: pd.DataFrame) -> pd.Series:
    # For children whose parent is deceased, DataFirst exports co-residence as
    # 8 (not applicable). Stats SA's published living-arrangement measure treats
    # that parent as not resident, so map 8 to 2 (No) for this derivation.
    mother = frame["hhc_moth_parthh"].replace(8, 2)
    father = frame["hhc_fath_parthh"].replace(8, 2)
    result = pd.Series(pd.NA, index=frame.index, dtype="string")
    result.loc[(mother == 1) & (father == 1)] = "Both parents"
    result.loc[(mother == 1) & (father == 2)] = "Mother only"
    result.loc[(mother == 2) & (father == 1)] = "Father only"
    result.loc[(mother == 2) & (father == 2)] = "Neither parent"
    return result


def weighted_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    valid = frame.dropna(subset=["living_arrangement", "person_wgt"]).copy()
    totals = valid.groupby("living_arrangement", observed=True)["person_wgt"].sum()
    result = (totals / totals.sum() * 100).rename("weighted_percent").reset_index()
    counts = valid.groupby("living_arrangement", observed=True).size().rename("sample_n")
    result = result.merge(counts.reset_index(), on="living_arrangement", how="left")
    result["living_arrangement"] = pd.Categorical(
        result["living_arrangement"], categories=GROUP_ORDER, ordered=True
    )
    return result.sort_values("living_arrangement")


def weighted_yes_rate(
    frame: pd.DataFrame,
    variable: str,
    yes_codes: tuple[int, ...] = (1,),
    valid_codes: tuple[int, ...] = (1, 2),
) -> pd.DataFrame:
    valid = frame[
        frame["living_arrangement"].notna()
        & frame[variable].isin(valid_codes)
        & frame["person_wgt"].notna()
    ].copy()
    valid["weighted_yes"] = valid[variable].isin(yes_codes) * valid["person_wgt"]
    grouped = valid.groupby("living_arrangement", observed=True)
    result = grouped.agg(
        weighted_yes=("weighted_yes", "sum"),
        weighted_total=("person_wgt", "sum"),
        sample_n=(variable, "size"),
    ).reset_index()
    result["weighted_percent_yes"] = (
        result["weighted_yes"] / result["weighted_total"] * 100
    )
    result["outcome"] = variable
    return result[
        ["outcome", "living_arrangement", "weighted_percent_yes", "sample_n"]
    ]


def save_distribution_chart(distribution: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    figure, axis = plt.subplots(figsize=(9, 5.5))
    sns.barplot(
        data=distribution,
        x="living_arrangement",
        y="weighted_percent",
        hue="living_arrangement",
        order=GROUP_ORDER,
        hue_order=GROUP_ORDER,
        palette=["#6F4E7C", "#C45A83", "#DD9A58", "#4E8098"],
        legend=False,
        ax=axis,
    )
    axis.set_title("Children's parent co-residence in South Africa, GHS 2025")
    axis.set_xlabel("")
    axis.set_ylabel("Weighted percentage of children")
    axis.set_ylim(0, max(55, distribution["weighted_percent"].max() + 5))
    for container in axis.containers:
        axis.bar_label(container, fmt="%.1f%%", padding=3)
    figure.tight_layout()
    figure.savefig(FIGURE_DIR / "living_arrangement_distribution.png", dpi=200)
    plt.close(figure)


def save_initial_outcome_charts(outcomes: pd.DataFrame) -> None:
    colours = {
        "Both parents": "#6F4E7C",
        "Mother only": "#C45A83",
        "Father only": "#DD9A58",
        "Neither parent": "#4E8098",
    }

    education = outcomes[outcomes["outcome"].isin(["edu_attend", "edu_same"])].copy()
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    chart_specs = [
        ("edu_attend", "Currently attending education, ages 5-17", (90, 100), "Axis starts at 90%"),
        ("edu_same", "Repeated a grade, applicable learners", (0, 10), ""),
    ]
    for axis, (outcome, title, limits, note) in zip(axes, chart_specs):
        subset = education[education["outcome"] == outcome].set_index("living_arrangement")
        values = [subset.loc[group, "weighted_percent_yes"] for group in GROUP_ORDER]
        positions = list(range(len(GROUP_ORDER)))
        axis.hlines(positions, limits[0], values, color="#D9D2D7", linewidth=2)
        axis.scatter(
            values,
            positions,
            s=95,
            color=[colours[group] for group in GROUP_ORDER],
            zorder=3,
        )
        for value, position in zip(values, positions):
            axis.text(value + 0.12, position, f"{value:.1f}%", va="center", fontsize=10)
        axis.set_xlim(*limits)
        axis.set_title(title, fontsize=12)
        axis.set_xlabel("Weighted percentage")
        axis.set_yticks(positions, GROUP_ORDER)
        axis.grid(axis="x", alpha=0.25)
        axis.grid(axis="y", visible=False)
        if note:
            axis.text(0.0, -0.17, note, transform=axis.transAxes, fontsize=9, color="#666666")
    axes[0].invert_yaxis()
    figure.suptitle("Unadjusted education indicators by parent co-residence, GHS 2025", fontsize=15)
    figure.tight_layout()
    figure.savefig(FIGURE_DIR / "education_indicators_by_arrangement.png", dpi=200)
    plt.close(figure)

    food = outcomes[outcomes["outcome"] == "child_food_insufficient"].copy()
    food["living_arrangement"] = pd.Categorical(
        food["living_arrangement"], categories=GROUP_ORDER, ordered=True
    )
    food = food.sort_values("living_arrangement")
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.bar(
        food["living_arrangement"].astype("string"),
        food["weighted_percent_yes"],
        color=[colours[group] for group in GROUP_ORDER],
    )
    axis.set_title("Child food insufficiency by parent co-residence, GHS 2025")
    axis.set_xlabel("")
    axis.set_ylabel("Weighted percentage of children")
    axis.set_ylim(0, 30)
    for position, value in enumerate(food["weighted_percent_yes"]):
        axis.text(position, value + 0.6, f"{value:.1f}%", ha="center", fontsize=11)
    axis.text(
        0.0,
        -0.17,
        "Unadjusted household measure: food was insufficient seldom, sometimes, often or always.",
        transform=axis.transAxes,
        fontsize=9,
        color="#666666",
    )
    figure.tight_layout()
    figure.savefig(FIGURE_DIR / "food_insufficiency_by_arrangement.png", dpi=200)
    plt.close(figure)


def main() -> int:
    try:
        person_path, household_path = discover_files()
        person = normalise_columns(read_data(person_path))
        household = normalise_columns(read_data(household_path))
        convert_analysis_codes(person, household)

        require_columns(
            person,
            {
                "uqnr",
                "age",
                "hhc_moth_parthh",
                "hhc_fath_parthh",
                "edu_attend",
                "edu_same",
                "soc_grant",
                "soc_grant_csg",
                "soc_grant_fos",
                "person_wgt",
            },
            "Person",
        )
        require_columns(
            household,
            {"uqnr", "fsd_hung_child", "totmhinc", "hholdsz"},
            "Household",
        )

        if household["uqnr"].duplicated().any():
            raise ValueError("Household file contains duplicate uqnr values; inspect before merging.")

        household_keep = [
            column
            for column in (
                "uqnr",
                "fsd_hung_child",
                "fsd_worried",
                "fsd_healthy",
                "totmhinc",
                "hholdsz",
                "hwl_assets_comp",
                "com_int_fixed",
            )
            if column in household.columns
        ]
        merged = person.merge(
            household[household_keep], on="uqnr", how="left", validate="many_to_one"
        )
        children = merged.loc[merged["age"].between(0, 17, inclusive="both")].copy()
        children["living_arrangement"] = derive_living_arrangement(children)
        children["monthly_income_per_person"] = (
            children["totmhinc"] / children["hholdsz"].replace(0, pd.NA)
        )
        children["child_food_insufficient"] = pd.NA
        children.loc[children["fsd_hung_child"] == 1, "child_food_insufficient"] = 0
        children.loc[
            children["fsd_hung_child"].isin([2, 3, 4, 5]),
            "child_food_insufficient",
        ] = 1

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        TABLE_DIR.mkdir(parents=True, exist_ok=True)
        FIGURE_DIR.mkdir(parents=True, exist_ok=True)

        children.to_csv(PROCESSED_DIR / "ghs_2025_children_analysis.csv", index=False)

        distribution = weighted_distribution(children)
        distribution.to_csv(TABLE_DIR / "living_arrangement_distribution.csv", index=False)
        save_distribution_chart(distribution)

        outcomes = []
        school_age = children.loc[children["age"].between(5, 17, inclusive="both")]
        outcomes.append(weighted_yes_rate(school_age, "edu_attend"))
        outcomes.append(weighted_yes_rate(school_age, "edu_same"))
        outcomes.append(weighted_yes_rate(children, "soc_grant"))
        outcomes.append(
            weighted_yes_rate(children, "soc_grant_csg", valid_codes=(1, 2, 8))
        )
        if "soc_grant_csg_topup" in children.columns:
            outcomes.append(
                weighted_yes_rate(
                    children, "soc_grant_csg_topup", valid_codes=(1, 2, 8)
                )
            )
        outcomes.append(
            weighted_yes_rate(children, "soc_grant_fos", valid_codes=(1, 2, 8))
        )
        outcomes.append(
            weighted_yes_rate(
                children,
                "child_food_insufficient",
                yes_codes=(1,),
                valid_codes=(0, 1),
            )
        )
        outcome_table = pd.concat(outcomes, ignore_index=True)
        outcome_table.to_csv(TABLE_DIR / "first_weighted_outcomes.csv", index=False)
        save_initial_outcome_charts(outcome_table)

        print("Built child-level analysis file and first weighted outputs.")
        print(distribution.to_string(index=False))
        print("\nValidation target: 31.4% both, 45.9% mother only, 4.2% father only, 18.5% neither.")
        return 0
    except (FileNotFoundError, KeyError, ValueError) as error:
        print(f"Analysis stopped: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
