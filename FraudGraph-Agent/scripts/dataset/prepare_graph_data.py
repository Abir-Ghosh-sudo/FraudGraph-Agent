"""
Prepare normalized HHGOA records for TigerGraph loading.

Input:
    graph_records.json

Output:
    customers.jsonl
    devices.jsonl
    connections.jsonl
    transactions.jsonl
    edges.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_graph_records(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load graph records produced by preprocess.py."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Graph data must be a JSON object.")

    return data


def write_jsonl(
    path: Path,
    records: list[dict[str, Any]],
) -> int:
    """Write records as JSON Lines."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )

    return len(records)


def prepare_graph_data(
    input_path: Path,
    output_dir: Path,
) -> dict[str, int]:
    """Split graph records into TigerGraph-oriented datasets."""
    graph = load_graph_records(input_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    customers = graph.get("customers", [])
    devices = graph.get("devices", [])
    connections = graph.get("connections", [])
    transactions = graph.get("transactions", [])
    edges = graph.get("edges", [])

    counts = {
        "customers": write_jsonl(
            output_dir / "customers.jsonl",
            customers,
        ),
        "devices": write_jsonl(
            output_dir / "devices.jsonl",
            devices,
        ),
        "connections": write_jsonl(
            output_dir / "connections.jsonl",
            connections,
        ),
        "transactions": write_jsonl(
            output_dir / "transactions.jsonl",
            transactions,
        ),
        "edges": write_jsonl(
            output_dir / "edges.jsonl",
            edges,
        ),
    }

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare HHGOA data for TigerGraph loading."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to graph_records.json.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for TigerGraph-ready JSONL files.",
    )

    args = parser.parse_args()

    counts = prepare_graph_data(
        input_path=args.input,
        output_dir=args.output_dir,
    )

    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()