"""Inspect downloaded GHS 2025 files before analysis."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "outputs" / "tables"

SUPPORTED_SUFFIXES = {".csv", ".dta", ".sav"}

PERSON_EXPECTED = {
    "uqnr",
    "personnr",
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

HOUSEHOLD_EXPECTED = {
    "uqnr",
    "fsd_hung_child",
    "fsd_worried",
    "fsd_healthy",
    "totmhinc",
    "hholdsz",
    "house_wgt",
}


def discover_files() -> tuple[Path, Path]:
    candidates = sorted(
        path for path in RAW_DIR.iterdir() if path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    person = [path for path in candidates if "person" in path.name.lower()]
    household = [
        path
        for path in candidates
        if any(token in path.name.lower() for token in ("household", "hhold"))
        and "person" not in path.name.lower()
    ]

    if len(person) != 1 or len(household) != 1:
        raise FileNotFoundError(
            "Expected exactly one person file and one household file in data/raw. "
            "See data/raw/README.md for download and naming guidance."
        )
    return person[0], household[0]


def read_data(path: Path, sample_rows: int | None = None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(
                path, nrows=sample_rows, low_memory=False, encoding="utf-8"
            )
        except UnicodeDecodeError:
            # Stats SA CSV exports may contain Windows-1252 punctuation.
            return pd.read_csv(
                path, nrows=sample_rows, low_memory=False, encoding="cp1252"
            )
    if suffix == ".dta":
        return pd.read_stata(path, convert_categoricals=False)
    if suffix == ".sav":
        return pd.read_spss(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Lowercase columns while preserving duplicate DataFirst label columns."""
    result = frame.copy()
    seen: dict[str, int] = {}
    normalised = []
    for column in result.columns:
        base = str(column).strip().lower()
        occurrence = seen.get(base, 0)
        if occurrence == 0:
            name = base
        elif occurrence == 1:
            name = f"{base}_label"
        else:
            name = f"{base}_duplicate_{occurrence}"
        normalised.append(name)
        seen[base] = occurrence + 1
    result.columns = normalised
    return result


def audit_file(path: Path, expected: set[str], role: str) -> pd.DataFrame:
    frame = read_data(path, sample_rows=500 if path.suffix.lower() == ".csv" else None)
    frame = normalise_columns(frame)

    rows = []
    for variable in sorted(expected):
        rows.append(
            {
                "file_role": role,
                "file_name": path.name,
                "variable": variable,
                "present": variable in frame.columns,
                "dtype": str(frame[variable].dtype) if variable in frame.columns else "",
                "sample_non_null": int(frame[variable].notna().sum())
                if variable in frame.columns
                else 0,
            }
        )

    print(f"\n{role.upper()}: {path.name}")
    print(f"Rows inspected: {len(frame):,}")
    print(f"Columns: {len(frame.columns):,}")
    missing = sorted(expected - set(frame.columns))
    print("Missing expected variables:", missing or "None")
    return pd.DataFrame(rows)


def main() -> int:
    try:
        person_path, household_path = discover_files()
    except FileNotFoundError as error:
        print(error)
        return 1

    audits = [
        audit_file(person_path, PERSON_EXPECTED, "person"),
        audit_file(household_path, HOUSEHOLD_EXPECTED, "household"),
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "column_audit.csv"
    pd.concat(audits, ignore_index=True).to_csv(output_path, index=False)
    print(f"\nSaved audit: {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
