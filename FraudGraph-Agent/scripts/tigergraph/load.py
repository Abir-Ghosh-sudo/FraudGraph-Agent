"""Provision TigerGraph with the fraud graph schema and dataset.

Usage (from the repository root):

    .venv\\Scripts\\python.exe -m scripts.tigergraph.load

    # or with an explicit row cap
    .venv\\Scripts\\python.exe -m scripts.tigergraph.load --max-rows 50000

Requires working TigerGraph credentials in .env:

    TIGERGRAPH_HOST=https://<workspace>.tgcloud.io
    TIGERGRAPH_GRAPH_NAME=Transaction_Fraud
    TIGERGRAPH_API_TOKEN=<token>          # or USERNAME + PASSWORD

The script refuses to run when the instance is not configured, and it will not
report success unless TigerGraph accepted every batch.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import get_settings  # noqa: E402
from backend.tigergraph.loader import TigerGraphLoader  # noqa: E402
from backend.tigergraph.records import (  # noqa: E402
    iter_closed_case_records,
    iter_graph_records,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the TigerGraph fraud schema and load the dataset.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50_000,
        help="Transactions to load from transactions.csv.",
    )
    parser.add_argument(
        "--keep-graph",
        action="store_true",
        help="Do not drop an existing graph before creating the schema.",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Create the graph and install the query, but load no data.",
    )
    args = parser.parse_args()

    settings = get_settings()

    if not settings.tigergraph_configured:
        print(
            "TigerGraph is not configured.\n"
            "Set these in .env before running the loader:\n"
            "  TIGERGRAPH_HOST\n"
            "  TIGERGRAPH_GRAPH_NAME\n"
            "  TIGERGRAPH_API_TOKEN   (or TIGERGRAPH_USERNAME + TIGERGRAPH_PASSWORD)\n"
            "\nAlso make sure this machine's outbound IP is allowlisted by the "
            "TigerGraph instance, otherwise GSQL connections are refused with "
            "HTTP 403.",
            file=sys.stderr,
        )
        return 2

    loader = TigerGraphLoader(settings)
    started = time.perf_counter()

    try:
        loader.create_graph(drop_existing=not args.keep_graph)
        loader.install_queries()
    except Exception as exc:  # noqa: BLE001
        print(f"Schema creation failed: {exc}", file=sys.stderr)
        return 1

    if args.schema_only:
        print(json.dumps({"schema": "created", "data": "skipped"}, indent=2))
        return 0

    transactions_csv = args.data_dir / "transactions.csv"
    identity_csv = args.data_dir / "identity.csv"
    closed_cases_csv = args.data_dir / "closed_cases_history.csv"

    vertices = 0
    edges = 0

    try:
        for batch in iter_graph_records(
            transactions_csv=transactions_csv,
            identity_csv=identity_csv,
            max_rows=args.max_rows,
        ):
            for payload in batch.vertices:
                loader.client.upsert_vertex(
                    vertex_type=payload["vertex_type"],
                    vertex_id=payload["vertex_id"],
                    attributes=payload["attributes"],
                )
                vertices += 1
            for payload in batch.edges:
                loader.client.upsert_edge(
                    edge_type=payload["edge_type"],
                    from_id=payload["from_id"],
                    to_id=payload["to_id"],
                    attributes=payload.get("attributes", {}),
                )
                edges += 1

        for batch in iter_closed_case_records(
            closed_cases_csv=closed_cases_csv,
        ):
            for payload in batch.vertices:
                loader.client.upsert_vertex(
                    vertex_type=payload["vertex_type"],
                    vertex_id=payload["vertex_id"],
                    attributes=payload["attributes"],
                )
                vertices += 1
            for payload in batch.edges:
                loader.client.upsert_edge(
                    edge_type=payload["edge_type"],
                    from_id=payload["from_id"],
                    to_id=payload["to_id"],
                    attributes=payload.get("attributes", {}),
                )
                edges += 1
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "vertices_upserted": vertices,
                    "edges_upserted": edges,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "graph": settings.tigergraph_graph_name,
                "vertices_upserted": vertices,
                "edges_upserted": edges,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
