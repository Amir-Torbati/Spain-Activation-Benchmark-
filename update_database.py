from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "hour",
    "activated_up",
    "activated_dn",
    "reserve_up",
    "reserve_dn",
    "act_pct_up",
    "act_pct_dn",
    "price_up_eur_mwh",
    "price_dn_eur_mwh",
    "spot_eur_mwh",
]

NUMERIC_COLUMNS = [col for col in REQUIRED_COLUMNS if col != "hour"]


def load_activation_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS].copy()
    df["hour"] = pd.to_datetime(df["hour"], errors="coerce")

    if df["hour"].isna().any():
        bad_rows = df.index[df["hour"].isna()].tolist()[:10]
        raise ValueError(f"{path} has invalid hour values at rows: {bad_rows}")

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[NUMERIC_COLUMNS].isna().any().any():
        null_counts = df[NUMERIC_COLUMNS].isna().sum()
        bad_cols = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"{path} has invalid numeric values: {bad_cols}")

    return df


def write_database(df: pd.DataFrame, path: Path) -> None:
    output = df.copy()
    output["hour"] = output["hour"].dt.strftime("%Y-%m-%dT%H:%M")
    output.to_csv(path, index=False)


def summarize_missing_hours(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []

    expected = pd.date_range(df["hour"].min(), df["hour"].max(), freq="h")
    missing = expected.difference(pd.DatetimeIndex(df["hour"]))
    return [ts.strftime("%Y-%m-%dT%H:%M") for ts in missing[:20]]


def update_database(database_path: Path, new_csv_path: Path, dry_run: bool = False) -> dict[str, object]:
    incoming = load_activation_csv(new_csv_path)

    if database_path.exists():
        existing = load_activation_csv(database_path)
    else:
        existing = pd.DataFrame(columns=REQUIRED_COLUMNS)
        existing["hour"] = pd.to_datetime(existing["hour"])

    existing_hours = set(existing["hour"])
    incoming_hours = set(incoming["hour"])

    combined = pd.concat([existing, incoming], ignore_index=True)
    combined = combined.sort_values("hour")
    combined = combined.drop_duplicates(subset=["hour"], keep="last")
    combined = combined.sort_values("hour").reset_index(drop=True)

    summary = {
        "database": str(database_path),
        "source": str(new_csv_path),
        "existing_rows": len(existing),
        "incoming_rows": len(incoming),
        "added_hours": len(incoming_hours - existing_hours),
        "replaced_hours": len(incoming_hours & existing_hours),
        "final_rows": len(combined),
        "min_hour": combined["hour"].min().strftime("%Y-%m-%dT%H:%M") if not combined.empty else None,
        "max_hour": combined["hour"].max().strftime("%Y-%m-%dT%H:%M") if not combined.empty else None,
        "missing_hours_sample": summarize_missing_hours(combined),
    }

    if not dry_run:
        write_database(combined, database_path)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a new activation CSV into database.csv.")
    parser.add_argument("new_csv", type=Path, help="New activation CSV exported from the API workflow.")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("database.csv"),
        help="Database CSV to create or update. Defaults to database.csv.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = update_database(args.database, args.new_csv, args.dry_run)

    if args.dry_run:
        print("Dry run complete. No files were changed.")
    else:
        print("Database updated.")

    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
