"""
Validate the HHGOA fraud-investigation dataset.

The validator intentionally performs structural/data-quality validation only.
It does not infer fraud labels from the data.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "transactions": (
        "TransactionID",
    ),
    "customers": (
        "CustomerID",
    ),
    "devices": (
        "DeviceID",
    ),
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV file using UTF-8 with BOM support."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    return fieldnames, rows


def validate_required_columns(
    name: str,
    columns: list[str],
    required: tuple[str, ...],
) -> list[str]:
    """Validate that required columns are present."""
    return [
        f"{name}: missing required column '{column}'"
        for column in required
        if column not in columns
    ]


def validate_duplicate_ids(
    name: str,
    rows: list[dict[str, str]],
    id_column: str,
) -> list[str]:
    """Detect duplicate non-empty identifiers."""
    if id_column not in (rows[0].keys() if rows else {id_column}):
        return []

    seen: set[str] = set()
    duplicates: set[str] = set()

    for row in rows:
        value = (row.get(id_column) or "").strip()

        if not value:
            continue

        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    if not duplicates:
        return []

    sample = sorted(duplicates)[:10]

    return [
        (
            f"{name}: duplicate {id_column} values found "
            f"({len(duplicates)} unique duplicates); sample={sample}"
        )
    ]


def validate_null_ids(
    name: str,
    rows: list[dict[str, str]],
    id_column: str,
) -> list[str]:
    """Detect rows with missing primary identifiers."""
    missing = sum(
        1 for row in rows if not (row.get(id_column) or "").strip()
    )

    if missing == 0:
        return []

    return [
        f"{name}: {missing} rows have a missing {id_column}"
    ]


def validate_references(
    source_name: str,
    source_rows: list[dict[str, str]],
    source_column: str,
    target_name: str,
    target_rows: list[dict[str, str]],
    target_column: str,
) -> list[str]:
    """Check that populated foreign-key references resolve."""
    if not source_rows or not target_rows:
        return []

    target_values = {
        (row.get(target_column) or "").strip()
        for row in target_rows
        if (row.get(target_column) or "").strip()
    }

    if not target_values:
        return []

    missing: set[str] = set()

    for row in source_rows:
        value = (row.get(source_column) or "").strip()

        if value and value not in target_values:
            missing.add(value)

    if not missing:
        return []

    sample = sorted(missing)[:10]

    return [
        (
            f"{source_name}: {len(missing)} {source_column} references "
            f"do not exist in {target_name}.{target_column}; "
            f"sample={sample}"
        )
    ]


def validate_file(
    path: Path,
    *,
    required_columns: tuple[str, ...] = (),
    id_column: str | None = None,
) -> dict[str, Any]:
    """Validate one CSV file."""
    result: dict[str, Any] = {
        "file": str(path),
        "exists": path.exists(),
        "rows": 0,
        "columns": [],
        "errors": [],
        "warnings": [],
    }

    if not path.exists():
        result["errors"].append("file does not exist")
        return result

    if path.suffix.lower() != ".csv":
        result["errors"].append("expected a CSV file")
        return result

    try:
        columns, rows = read_csv(path)
    except (OSError, UnicodeError, csv.Error) as exc:
        result["errors"].append(f"unable to read CSV: {exc}")
        return result

    result["rows"] = len(rows)
    result["columns"] = columns

    result["errors"].extend(
        validate_required_columns(
            path.stem,
            columns,
            required_columns,
        )
    )

    if id_column:
        result["errors"].extend(
            validate_null_ids(
                path.stem,
                rows,
                id_column,
            )
        )
        result["errors"].extend(
            validate_duplicate_ids(
                path.stem,
                rows,
                id_column,
            )
        )

    if not rows:
        result["warnings"].append("file contains no data rows")

    return result


def discover_csv_files(data_dir: Path) -> list[Path]:
    """Discover CSV files recursively under the dataset directory."""
    if not data_dir.exists():
        return []

    return sorted(
        path
        for path in data_dir.rglob("*.csv")
        if path.is_file()
    )


def validate_dataset(data_dir: Path) -> dict[str, Any]:
    """Validate the complete available CSV dataset."""
    files = discover_csv_files(data_dir)

    report: dict[str, Any] = {
        "dataset_dir": str(data_dir),
        "files_found": len(files),
        "files": [],
        "errors": [],
        "warnings": [],
        "valid": True,
    }

    if not files:
        report["errors"].append(
            f"No CSV files found under '{data_dir}'."
        )
        report["valid"] = False
        return report

    loaded: dict[str, tuple[list[str], list[dict[str, str]]]] = {}

    for path in files:
        key = path.stem.lower()

        try:
            columns, rows = read_csv(path)
            loaded[key] = (columns, rows)
        except (OSError, UnicodeError, csv.Error) as exc:
            report["errors"].append(
                f"{path}: unable to read CSV: {exc}"
            )
            continue

        required = DEFAULT_REQUIRED_COLUMNS.get(key, ())
        id_column = required[0] if required else None

        result = validate_file(
            path,
            required_columns=required,
            id_column=id_column,
        )

        report["files"].append(result)

    # Referential checks are only applied when the expected datasets and
    # columns are actually present. This avoids assuming undocumented files.
    transactions = loaded.get("transactions")
    customers = loaded.get("customers")
    devices = loaded.get("devices")

    if transactions and customers:
        transaction_columns, transaction_rows = transactions
        customer_columns, customer_rows = customers

        if "CustomerID" in transaction_columns and "CustomerID" in customer_columns:
            report["errors"].extend(
                validate_references(
                    "transactions",
                    transaction_rows,
                    "CustomerID",
                    "customers",
                    customer_rows,
                    "CustomerID",
                )
            )

    if transactions and devices:
        transaction_columns, transaction_rows = transactions
        device_columns, device_rows = devices

        if "DeviceID" in transaction_columns and "DeviceID" in device_columns:
            report["errors"].extend(
                validate_references(
                    "transactions",
                    transaction_rows,
                    "DeviceID",
                    "devices",
                    device_rows,
                    "DeviceID",
                )
            )

    for result in report["files"]:
        report["errors"].extend(result["errors"])
        report["warnings"].extend(result["warnings"])

    report["valid"] = not report["errors"]

    return report


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate the HHGOA fraud-investigation dataset."
    )
    parser.add_argument(
        "data_dir",
        nargs="?",
        type=Path,
        default=Path("data"),
        help="Dataset directory. Defaults to ./data",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete validation report as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()

    report = validate_dataset(args.data_dir)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Dataset: {args.data_dir}")
        print(f"CSV files found: {report['files_found']}")
        print(f"Status: {'VALID' if report['valid'] else 'INVALID'}")

        for result in report["files"]:
            print(
                f"  {result['file']}: "
                f"{result['rows']} rows"
            )

        if report["errors"]:
            print("\nErrors:")
            for error in report["errors"]:
                print(f"  - {error}")

        if report["warnings"]:
            print("\nWarnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())