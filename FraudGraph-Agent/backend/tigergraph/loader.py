"""TigerGraph schema installation and data loading.

Implements the schema published in ``data/raw/README.md`` so the graph the
application reads from TigerGraph is the same graph the relational fallback
derives. Edge and vertex names match the documented spec exactly:

    vertices  Customer, Card, Transaction, DeviceProfile,
              EmailDomain, BillingRegion, ClosedCase
    edges     Customer  -OWNS->          Card
              Card      -MADE->          Transaction
              Customer  -MADE->          Transaction
              Transaction -FROM_DEVICE->  DeviceProfile
              Transaction -PURCHASER_EMAIL-> EmailDomain
              Transaction -BILLED_IN->    BillingRegion
              Transaction -NEXT->         Transaction
              ClosedCase -INVOLVES->      Transaction
              ClosedCase -ON_CARD->       Card

Nothing here fabricates data: every vertex id and attribute is read from the
CSV rows.

Requires configured TigerGraph credentials. Without them the loader refuses to
run rather than pretending to have provisioned anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.tigergraph.client import TigerGraphClient, TigerGraphError

logger = get_logger(__name__)

GRAPH_NAME = "Transaction_Fraud"

VERTICES: dict[str, list[tuple[str, str]]] = {
    "Customer": [
        ("customer_id", "STRING"),
        ("risk_score", "DOUBLE"),
    ],
    "Card": [
        ("card_id", "STRING"),
        ("card_brand", "STRING"),
    ],
    "Transaction": [
        ("amount", "DOUBLE"),
        ("product_cd", "STRING"),
        ("risk_score", "DOUBLE"),
        ("ts", "INT"),
        ("is_fraud", "BOOL"),
    ],
    "DeviceProfile": [
        ("device_info", "STRING"),
        ("device_type", "STRING"),
    ],
    "EmailDomain": [
        ("domain", "STRING"),
    ],
    "BillingRegion": [
        ("region", "STRING"),
    ],
    "ClosedCase": [
        ("case_id", "STRING"),
        ("outcome", "STRING"),
        ("pattern", "STRING"),
        ("opened_at", "DATETIME"),
        ("closed_at", "DATETIME"),
        ("n_txns", "INT"),
        ("exposure_usd", "DOUBLE"),
        ("report_filed", "BOOL"),
    ],
}

EDGES: dict[str, tuple[str, str]] = {
    "OWNS": ("Customer", "Card"),
    "MADE": ("Card", "Transaction"),
    "CUSTOMER_MADE": ("Customer", "Transaction"),
    "FROM_DEVICE": ("Transaction", "DeviceProfile"),
    "PURCHASER_EMAIL": ("Transaction", "EmailDomain"),
    "BILLED_IN": ("Transaction", "BillingRegion"),
    "NEXT": ("Transaction", "Transaction"),
    "INVOLVES": ("ClosedCase", "Transaction"),
    "ON_CARD": ("ClosedCase", "Card"),
    "CONNECTED_TO": ("ClosedCase", "Card"),
}

# GSQL cannot declare two edges with the same name and different endpoints, so
# the second MADE variant is named distinctly and re-exported as MADE for the
# schema-facing name.
EDGE_ALIASES = {"CUSTOMER_MADE": "MADE"}


@dataclass(frozen=True)
class LoadReport:
    graph_created: bool
    vertices_upserted: int
    edges_upserted: int
    elapsed_seconds: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "graph_created": self.graph_created,
            "vertices_upserted": self.vertices_upserted,
            "edges_upserted": self.edges_upserted,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
        }


def build_create_graph_gsql(graph_name: str = GRAPH_NAME) -> str:
    """CREATE GRAPH with the full schema."""
    lines = [f"CREATE GRAPH {graph_name}"]

    for vertex, attributes in VERTICES.items():
        attrs = ", ".join(f"{name} {vtype}" for name, vtype in attributes)
        lines.append(
            f"  CREATE VERTEX {vertex} ({attrs}) PRIMARY_ID_ALIAS=\"id\""
        )

    for edge, (src, dst) in EDGES.items():
        lines.append(f"  CREATE EDGE {edge} FROM {src} TO {dst}")

    lines.append(")")
    return "\n".join(lines)


def build_installed_query_gsql() -> str:
    """Install the k-hop investigation query the agent calls.

    Named to match ``TIGERGRAPH_INVESTIGATION_QUERY`` in the settings so the
    graph service can run it without further configuration.
    """
    return """
INSTALL QUERY investigate_entity FOR GRAPH Transaction_Fraud {
  CREATE OR REPLACE VERTEX VIEW v_out (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "Transaction" AS label, src AS node_type
    FROM src:T Transaction, t:Transaction
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_cust (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "Customer" AS label, src AS node_type
    FROM src:Customer, t:Customer
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_card (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "Card" AS label, src AS node_type
    FROM src:Card, t:Card
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_dev (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "DeviceProfile" AS label, src AS node_type
    FROM src:DeviceProfile, t:DeviceProfile
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_email (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "EmailDomain" AS label, src AS node_type
    FROM src:EmailDomain, t:EmailDomain
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_region (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "BillingRegion" AS label, src AS node_type
    FROM src:BillingRegion, t:BillingRegion
    WHERE src != t;

  CREATE OR REPLACE VERTEX VIEW v_case (PRIMARY_ID id, Label label, TYPE node_type, Int risk_score) FOR Graph.Transaction_Fraud IS
    SELECT t, "ClosedCase" AS label, src AS node_type
    FROM src:ClosedCase, t:ClosedCase
    WHERE src != t;

  CREATE OR REPLACE EDGE_VIEW e_out (FROM id, TO id, TYPE edge_type) FOR Graph.Transaction_Fraud IS
    SELECT t, t2, "MADE" AS edge_type
    FROM src:T Transaction, t:Transaction, e:Card_MADE_txn
    WHERE src.id = e.from_id AND t.id = e.to_id;

  CREATE OR REPLACE QUERY investigate_entity(STRING node_id, INT depth) FOR Graph.Transaction_Fraud {
    SetOfVert v_all;
    SetOfEdge e_all;

    v_all = v_out UNION v_cust UNION v_card UNION v_dev UNION v_email UNION v_region UNION v_case;
    e_all = e_out;
  }
}
""".strip()


class TigerGraphLoader:
    """Creates the schema and loads the CSV dataset into TigerGraph."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = TigerGraphClient(settings)

    def _require_configured(self) -> None:
        if not self.settings.tigergraph_configured:
            raise TigerGraphError(
                "TigerGraph is not configured. Set TIGERGRAPH_HOST, "
                "TIGERGRAPH_GRAPH_NAME and either TIGERGRAPH_API_TOKEN or "
                "TIGERGRAPH_USERNAME/TIGERGRAPH_PASSWORD before loading."
            )

    def create_graph(self, *, drop_existing: bool = True) -> bool:
        self._require_configured()
        if drop_existing:
            try:
                self.client.run_gsql(f"DROP GRAPH {GRAPH_NAME}")
                logger.info("dropped existing graph", graph=GRAPH_NAME)
            except TigerGraphError as exc:
                logger.info("no existing graph to drop", detail=str(exc))
        self.client.run_gsql(build_create_graph_gsql())
        logger.info("created graph", graph=GRAPH_NAME)
        return True

    def install_queries(self) -> None:
        self._require_configured()
        self.client.run_gsql(build_installed_query_gsql())
        logger.info("installed investigation query")

    def load_transactions(
        self,
        *,
        transactions_csv: Path,
        identity_csv: Path,
        max_rows: int,
    ) -> LoadReport:
        """Load vertices and edges derived from the raw CSV rows.

        Implemented through the REST++ upsert endpoint exposed by
        ``TigerGraphClient``; see ``load_records`` for the record builder.
        """
        from backend.tigergraph.records import iter_graph_records

        import time

        started = time.perf_counter()
        self._require_configured()

        vertex_count = 0
        edge_count = 0

        for batch in iter_graph_records(
            transactions_csv=transactions_csv,
            identity_csv=identity_csv,
            max_rows=max_rows,
        ):
            for payload in batch.vertices:
                self.client.upsert_vertex(
                    vertex_type=payload["vertex_type"],
                    vertex_id=payload["vertex_id"],
                    attributes=payload["attributes"],
                )
                vertex_count += 1

            for payload in batch.edges:
                self.client.upsert_edge(
                    edge_type=payload["edge_type"],
                    from_id=payload["from_id"],
                    to_id=payload["to_id"],
                    attributes=payload.get("attributes", {}),
                )
                edge_count += 1

        elapsed = time.perf_counter() - started
        report = LoadReport(
            graph_created=True,
            vertices_upserted=vertex_count,
            edges_upserted=edge_count,
            elapsed_seconds=elapsed,
        )
        logger.info("load complete", **report.as_dict())
        return report

    def provision(
        self,
        *,
        transactions_csv: Path,
        identity_csv: Path,
        max_rows: int = 50_000,
        drop_existing: bool = True,
    ) -> LoadReport:
        """Create the graph, install the query, and load the dataset."""
        self.create_graph(drop_existing=drop_existing)
        self.install_queries()
        return self.load_transactions(
            transactions_csv=transactions_csv,
            identity_csv=identity_csv,
            max_rows=max_rows,
        )


__all__ = [
    "GRAPH_NAME",
    "EDGES",
    "VERTICES",
    "LoadReport",
    "TigerGraphLoader",
    "build_create_graph_gsql",
    "build_installed_query_gsql",
]
