"""Calculate design-aware confidence intervals for key weighted proportions."""

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
ADJUSTED_PATH = ROOT / "outputs" / "tables" / "adjusted_education_results.csv"
TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"
GROUP_ORDER = ["Both parents", "Mother only", "Father only", "Neither parent"]
COLOURS = {
    "Both parents": "#A93673",
    "Mother only": "#F06FAE",
    "Father only": "#35C9C2",
    "Neither parent": "#087F83",
}


def logistic(value: float) -> float:
    return 1.0 / (1.0 + np.exp(-value))


def ratio_with_design_ci(
    frame: pd.DataFrame,
    numerator: pd.Series,
    denominator: pd.Series,
) -> dict[str, float]:
    """Taylor-linearised ratio with stratified PSU variance estimation.

    The few strata containing a single observed PSU are centred at zero, a
    conservative lonely-PSU adjustment for these ratio linearised totals.
    """

    usable = frame[
        frame["stratum"].notna()
        & frame["psu"].notna()
        & frame["person_wgt"].notna()
        & (frame["person_wgt"] > 0)
    ].copy()
    num = numerator.reindex(usable.index).fillna(False).astype(float)
    den = denominator.reindex(usable.index).fillna(False).astype(float)
    weights = usable["person_wgt"].astype(float)
    denominator_total = float((weights * den).sum())
    if denominator_total <= 0:
        raise ValueError("The weighted denominator is zero.")

    estimate = float((weights * num).sum() / denominator_total)
    usable["linearised"] = weights * (num - estimate * den) / denominator_total
    cluster_totals = (
        usable.groupby(["stratum", "psu"], observed=True)["linearised"]
        .sum()
        .reset_index()
    )

    variance = 0.0
    singleton_strata = 0
    for _, stratum in cluster_totals.groupby("stratum", observed=True):
        totals = stratum["linearised"].to_numpy(dtype=float)
        psu_count = len(totals)
        if psu_count > 1:
            variance += psu_count / (psu_count - 1) * float(
                np.square(totals - totals.mean()).sum()
            )
        else:
            singleton_strata += 1
            variance += float(np.square(totals).sum())

    standard_error = float(np.sqrt(max(variance, 0.0)))
    if 0 < estimate < 1 and standard_error > 0:
        logit_estimate = np.log(estimate / (1 - estimate))
        logit_se = standard_error / (estimate * (1 - estimate))
        lower = logistic(logit_estimate - 1.96 * logit_se)
        upper = logistic(logit_estimate + 1.96 * logit_se)
    else:
        lower = max(0.0, estimate - 1.96 * standard_error)
        upper = min(1.0, estimate + 1.96 * standard_error)

    return {
        "estimate_percent": estimate * 100,
        "standard_error_percentage_points": standard_error * 100,
        "ci95_lower_percent": lower * 100,
        "ci95_upper_percent": upper * 100,
        "sample_n": int(den.sum()),
        "weighted_n": denominator_total,
        "strata_n": int(cluster_totals["stratum"].nunique()),
        "psu_n": int(len(cluster_totals)),
        "singleton_strata_n": singleton_strata,
    }


def living_arrangement_intervals(children: pd.DataFrame) -> pd.DataFrame:
    base = children[children["age"].between(0, 17) & children["living_arrangement"].isin(GROUP_ORDER)]
    rows = []
    denominator = pd.Series(True, index=base.index)
    for group in GROUP_ORDER:
        result = ratio_with_design_ci(
            base,
            base["living_arrangement"].eq(group),
            denominator,
        )
        rows.append({"living_arrangement": group, **result})
    return pd.DataFrame(rows)


def education_intervals(children: pd.DataFrame) -> pd.DataFrame:
    specifications = [
        ("School attendance, ages 5-17", "edu_attend", (1, 2)),
        ("Grade repetition, applicable learners", "edu_same", (1, 2)),
    ]
    base = children[
        children["age"].between(5, 17)
        & children["living_arrangement"].isin(GROUP_ORDER)
    ].copy()
    rows = []
    for outcome_label, variable, valid_codes in specifications:
        for group in GROUP_ORDER:
            group_member = base["living_arrangement"].eq(group)
            valid = base[variable].isin(valid_codes)
            denominator = group_member & valid
            numerator = denominator & base[variable].eq(1)
            result = ratio_with_design_ci(base, numerator, denominator)
            rows.append(
                {
                    "outcome": outcome_label,
                    "living_arrangement": group,
                    **result,
                }
            )
    return pd.DataFrame(rows)


def save_uncertainty_chart(intervals: pd.DataFrame, adjusted: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    figure.patch.set_facecolor("#FFF9FC")
    specifications = [
        ("School attendance, ages 5-17", (90, 100), "Axis starts at 90%"),
        ("Grade repetition, applicable learners", (0, 10), ""),
    ]
    positions = np.arange(len(GROUP_ORDER))
    for axis, (outcome, limits, note) in zip(axes, specifications):
        interval = intervals[intervals["outcome"] == outcome].set_index("living_arrangement")
        model = adjusted[adjusted["outcome"] == outcome].set_index("living_arrangement")
        observed = np.array([interval.loc[group, "estimate_percent"] for group in GROUP_ORDER])
        lower = np.array([interval.loc[group, "ci95_lower_percent"] for group in GROUP_ORDER])
        upper = np.array([interval.loc[group, "ci95_upper_percent"] for group in GROUP_ORDER])
        adjusted_values = np.array([model.loc[group, "adjusted_percent"] for group in GROUP_ORDER])
        colours = [COLOURS[group] for group in GROUP_ORDER]

        axis.set_facecolor("#FFFFFF")
        axis.errorbar(
            observed,
            positions,
            xerr=np.vstack([observed - lower, upper - observed]),
            fmt="o",
            markersize=7,
            color="#705967",
            ecolor="#C8A8B8",
            elinewidth=2,
            capsize=4,
            label="Observed (95% CI)",
            zorder=2,
        )
        axis.scatter(
            adjusted_values,
            positions,
            marker="D",
            s=70,
            color=colours,
            edgecolor="white",
            linewidth=0.8,
            label="Adjusted point estimate",
            zorder=3,
        )
        for value, position, colour in zip(adjusted_values, positions, colours):
            axis.text(value + 0.14, position, f"{value:.1f}%", va="center", fontsize=9.5, color=colour)
        axis.set_xlim(*limits)
        axis.set_yticks(positions, GROUP_ORDER)
        axis.set_xlabel("Weighted percentage")
        axis.set_title(outcome, fontsize=12, color="#36212E")
        axis.grid(axis="x", color="#F0DDE6", linewidth=0.8)
        axis.grid(axis="y", visible=False)
        for spine in axis.spines.values():
            spine.set_color("#E8D5DF")
        if note:
            axis.text(0, -0.18, note, transform=axis.transAxes, fontsize=9, color="#806C77")

    axes[0].invert_yaxis()
    axes[1].legend(loc="upper right", frameon=False)
    figure.suptitle(
        "Education indicators: observed uncertainty and adjusted estimates",
        fontsize=15,
        color="#A93673",
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "Observed intervals account for stratification and PSU clustering. Adjusted values remain point estimates.",
        ha="center",
        fontsize=9,
        color="#705967",
    )
    figure.tight_layout(rect=(0, 0.04, 1, 0.98))
    figure.savefig(FIGURE_DIR / "education_indicators_with_uncertainty.png", dpi=200, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> int:
    if not DATA_PATH.exists():
        print("Processed child file not found. Run src/build_child_analysis.py first.")
        return 1
    if not ADJUSTED_PATH.exists():
        print("Adjusted results not found. Run src/adjusted_analysis.py first.")
        return 1

    children = pd.read_csv(DATA_PATH, low_memory=False)
    required = {"stratum", "psu", "person_wgt", "age", "living_arrangement", "edu_attend", "edu_same"}
    missing = sorted(required - set(children.columns))
    if missing:
        print(f"Processed child file is missing required columns: {missing}")
        return 1

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    living = living_arrangement_intervals(children)
    education = education_intervals(children)
    living.to_csv(TABLE_DIR / "living_arrangement_confidence_intervals.csv", index=False)
    education.to_csv(TABLE_DIR / "education_observed_confidence_intervals.csv", index=False)

    adjusted = pd.read_csv(ADJUSTED_PATH)
    save_uncertainty_chart(education, adjusted)
    print("Saved design-aware confidence intervals and uncertainty chart.")
    print(education.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
