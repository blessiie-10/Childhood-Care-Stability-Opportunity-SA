"""Create weighted context profiles and adjusted education point estimates."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = ROOT / "data" / "processed" / "ghs_2025_children_analysis.csv"
TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"
GROUP_ORDER = ["Both parents", "Mother only", "Father only", "Neither parent"]
COLOURS = {
    "Both parents": "#6F4E7C",
    "Mother only": "#C45A83",
    "Father only": "#DD9A58",
    "Neither parent": "#4E8098",
}


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return float("nan")
    return float(np.average(values[mask].astype(float), weights=weights[mask]))


def weighted_median(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    values_array = values[mask].astype(float).to_numpy()
    weights_array = weights[mask].astype(float).to_numpy()
    if len(values_array) == 0:
        return float("nan")
    order = np.argsort(values_array)
    values_array = values_array[order]
    weights_array = weights_array[order]
    cutoff = weights_array.sum() / 2
    return float(values_array[np.searchsorted(np.cumsum(weights_array), cutoff)])


def weighted_rate(
    frame: pd.DataFrame,
    variable: str,
    yes_codes: tuple[int, ...] = (1,),
    valid_codes: tuple[int, ...] = (1, 2),
) -> float:
    valid = frame[frame[variable].isin(valid_codes) & frame["person_wgt"].notna()]
    if valid.empty:
        return float("nan")
    return weighted_mean(valid[variable].isin(yes_codes).astype(float), valid["person_wgt"]) * 100


def create_context_profiles(children: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group in GROUP_ORDER:
        subset = children[children["living_arrangement"] == group].copy()
        weights = subset["person_wgt"]
        rows.append(
            {
                "living_arrangement": group,
                "sample_n": len(subset),
                "weighted_children": weights.sum(),
                "mean_age": weighted_mean(subset["age"], weights),
                "female_percent": weighted_mean((subset["sex"] == 2).astype(float), weights) * 100,
                "rural_or_farm_percent": weighted_mean((subset["geotype"] != 1).astype(float), weights) * 100,
                "median_monthly_income_per_person": weighted_median(
                    subset["monthly_income_per_person"], weights
                ),
                "mean_household_size": weighted_mean(subset["hholdsz"], weights),
                "food_insufficiency_percent": weighted_rate(
                    subset,
                    "child_food_insufficient",
                    yes_codes=(1,),
                    valid_codes=(0, 1),
                ),
                "computer_access_percent": weighted_rate(subset, "hwl_assets_comp"),
                "fixed_internet_percent": weighted_rate(subset, "com_int_fixed"),
            }
        )
    return pd.DataFrame(rows)


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -35, 35)
    return 1.0 / (1.0 + np.exp(-values))


def fit_weighted_logistic(
    design: np.ndarray,
    outcome: np.ndarray,
    weights: np.ndarray,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
) -> tuple[np.ndarray, int, bool]:
    weights = weights / weights.mean()
    coefficients = np.zeros(design.shape[1], dtype=float)
    ridge = np.full(design.shape[1], 1e-8)
    ridge[0] = 0.0

    for iteration in range(1, max_iterations + 1):
        probabilities = sigmoid(design @ coefficients)
        variance = np.clip(probabilities * (1 - probabilities), 1e-9, None)
        gradient = design.T @ (weights * (outcome - probabilities)) - ridge * coefficients
        hessian = (design.T * (weights * variance)) @ design
        hessian += np.diag(ridge)
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(hessian) @ gradient
        coefficients += step
        if np.max(np.abs(step)) < tolerance:
            return coefficients, iteration, True
    return coefficients, max_iterations, False


def build_design(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    design = pd.DataFrame(index=frame.index)
    design["intercept"] = 1.0
    design["arr_mother_only"] = (frame["living_arrangement"] == "Mother only").astype(float)
    design["arr_father_only"] = (frame["living_arrangement"] == "Father only").astype(float)
    design["arr_neither_parent"] = (frame["living_arrangement"] == "Neither parent").astype(float)

    age_mean = float(frame["age"].mean())
    age_sd = float(frame["age"].std()) or 1.0
    age_standardised = (frame["age"] - age_mean) / age_sd
    design["age_standardised"] = age_standardised
    design["age_squared"] = age_standardised**2
    design["female"] = (frame["sex"] == 2).astype(float)

    for province in range(2, 10):
        design[f"province_{province}"] = (frame["prov"] == province).astype(float)
    design["traditional_area"] = (frame["geotype"] == 2).astype(float)
    design["farm_area"] = (frame["geotype"] == 3).astype(float)

    income = frame["monthly_income_per_person"].copy()
    income_missing = income.isna()
    income_fill = float(income.median())
    log_income = np.log1p(income.fillna(income_fill).clip(lower=0))
    log_income_mean = float(log_income.mean())
    log_income_sd = float(log_income.std()) or 1.0
    design["log_income_standardised"] = (log_income - log_income_mean) / log_income_sd
    design["income_missing"] = income_missing.astype(float)

    household_size_mean = float(frame["hholdsz"].mean())
    household_size_sd = float(frame["hholdsz"].std()) or 1.0
    design["household_size_standardised"] = (
        frame["hholdsz"] - household_size_mean
    ) / household_size_sd

    food_missing = frame["child_food_insufficient"].isna()
    design["food_insufficient"] = frame["child_food_insufficient"].fillna(0).astype(float)
    design["food_measure_missing"] = food_missing.astype(float)

    settings = {
        "age_mean": age_mean,
        "age_sd": age_sd,
        "income_fill": income_fill,
        "log_income_mean": log_income_mean,
        "log_income_sd": log_income_sd,
        "household_size_mean": household_size_mean,
        "household_size_sd": household_size_sd,
    }
    return design, settings


def adjusted_outcome(
    children: pd.DataFrame,
    variable: str,
    label: str,
    minimum_age: int = 5,
    maximum_age: int = 17,
) -> tuple[pd.DataFrame, dict[str, object]]:
    sample = children[
        children["age"].between(minimum_age, maximum_age, inclusive="both")
        & children[variable].isin([1, 2])
        & children["living_arrangement"].isin(GROUP_ORDER)
        & children["person_wgt"].notna()
        & (children["person_wgt"] > 0)
    ].copy()
    sample["outcome_binary"] = (sample[variable] == 1).astype(float)

    design_frame, settings = build_design(sample)
    design = design_frame.to_numpy(dtype=float)
    outcome = sample["outcome_binary"].to_numpy(dtype=float)
    weights = sample["person_wgt"].to_numpy(dtype=float)
    coefficients, iterations, converged = fit_weighted_logistic(design, outcome, weights)

    rows = []
    arrangement_columns = ["arr_mother_only", "arr_father_only", "arr_neither_parent"]
    for group in GROUP_ORDER:
        group_sample = sample[sample["living_arrangement"] == group]
        observed = weighted_mean(group_sample["outcome_binary"], group_sample["person_wgt"]) * 100

        counterfactual = design_frame.copy()
        counterfactual[arrangement_columns] = 0.0
        if group == "Mother only":
            counterfactual["arr_mother_only"] = 1.0
        elif group == "Father only":
            counterfactual["arr_father_only"] = 1.0
        elif group == "Neither parent":
            counterfactual["arr_neither_parent"] = 1.0
        predicted = sigmoid(counterfactual.to_numpy(dtype=float) @ coefficients)
        adjusted = float(np.average(predicted, weights=weights)) * 100
        rows.append(
            {
                "outcome": label,
                "living_arrangement": group,
                "observed_percent": observed,
                "adjusted_percent": adjusted,
                "sample_n": len(group_sample),
                "weighted_n": group_sample["person_wgt"].sum(),
            }
        )

    probabilities = sigmoid(design @ coefficients)
    epsilon = 1e-12
    weighted_log_loss = -float(
        np.average(
            outcome * np.log(probabilities + epsilon)
            + (1 - outcome) * np.log(1 - probabilities + epsilon),
            weights=weights,
        )
    )
    diagnostics = {
        "outcome": label,
        "sample_n": len(sample),
        "weighted_n": weights.sum(),
        "iterations": iterations,
        "converged": converged,
        "weighted_log_loss": weighted_log_loss,
        "number_of_parameters": design.shape[1],
        **settings,
    }
    return pd.DataFrame(rows), diagnostics


def save_adjusted_chart(results: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.8), sharey=True)
    specifications = [
        ("School attendance, ages 5-17", (90, 100), "Axis starts at 90%"),
        ("Grade repetition, applicable learners", (0, 10), ""),
    ]
    positions = np.arange(len(GROUP_ORDER))
    for axis, (outcome, limits, note) in zip(axes, specifications):
        subset = results[results["outcome"] == outcome].set_index("living_arrangement")
        observed = np.array([subset.loc[group, "observed_percent"] for group in GROUP_ORDER])
        adjusted = np.array([subset.loc[group, "adjusted_percent"] for group in GROUP_ORDER])
        axis.hlines(positions, observed, adjusted, color="#B8B0B5", linewidth=2)
        axis.scatter(observed, positions, marker="o", s=80, color="#A8A2A6", label="Observed")
        axis.scatter(
            adjusted,
            positions,
            marker="D",
            s=75,
            color=[COLOURS[group] for group in GROUP_ORDER],
            label="Adjusted",
            zorder=3,
        )
        for value, position in zip(adjusted, positions):
            axis.text(value + 0.12, position, f"{value:.1f}%", va="center", fontsize=9.5)
        axis.set_xlim(*limits)
        axis.set_yticks(positions, GROUP_ORDER)
        axis.set_xlabel("Weighted percentage")
        axis.set_title(outcome, fontsize=12)
        axis.grid(axis="x", alpha=0.25)
        axis.grid(axis="y", visible=False)
        if note:
            axis.text(0.0, -0.17, note, transform=axis.transAxes, fontsize=9, color="#666666")
    axes[0].invert_yaxis()
    axes[1].legend(loc="lower right", frameon=False)
    figure.suptitle(
        "Observed and model-adjusted education indicators, GHS 2025",
        fontsize=15,
    )
    figure.text(
        0.5,
        0.01,
        "Adjusted for age, sex, province, geography, income per person, household size and food insufficiency.",
        ha="center",
        fontsize=9,
        color="#666666",
    )
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    figure.savefig(FIGURE_DIR / "adjusted_education_indicators.png", dpi=200)
    plt.close(figure)


def main() -> int:
    if not DATA_PATH.exists():
        print("Processed child file not found. Run src/build_child_analysis.py first.")
        return 1

    children = pd.read_csv(DATA_PATH, low_memory=False)
    required = {
        "living_arrangement",
        "person_wgt",
        "age",
        "sex",
        "prov",
        "geotype",
        "monthly_income_per_person",
        "hholdsz",
        "child_food_insufficient",
        "hwl_assets_comp",
        "com_int_fixed",
        "edu_attend",
        "edu_same",
    }
    missing = sorted(required - set(children.columns))
    if missing:
        print(f"Processed child file is missing required columns: {missing}")
        return 1

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    profiles = create_context_profiles(children)
    profiles.to_csv(TABLE_DIR / "living_arrangement_context_profiles.csv", index=False)

    attendance, attendance_diagnostics = adjusted_outcome(
        children,
        "edu_attend",
        "School attendance, ages 5-17",
    )
    repetition, repetition_diagnostics = adjusted_outcome(
        children,
        "edu_same",
        "Grade repetition, applicable learners",
    )
    adjusted = pd.concat([attendance, repetition], ignore_index=True)
    adjusted.to_csv(TABLE_DIR / "adjusted_education_results.csv", index=False)
    pd.DataFrame([attendance_diagnostics, repetition_diagnostics]).to_csv(
        TABLE_DIR / "adjusted_model_diagnostics.csv", index=False
    )
    save_adjusted_chart(adjusted)

    print("Saved context profiles and adjusted education results.")
    print("\nCONTEXT PROFILES")
    print(profiles.to_string(index=False))
    print("\nADJUSTED EDUCATION RESULTS")
    print(adjusted.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

