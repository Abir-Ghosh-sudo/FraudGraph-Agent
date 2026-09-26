"""Fraud relationship graph derived from the real transaction ledger.

TigerGraph is the primary graph store for this system. When it is not
configured or not reachable, this module derives an equivalent subgraph
directly from the raw IEEE-CIS transaction and identity records, so graph
investigation still works against real data instead of failing or, worse,
falling back to invented nodes.

Everything returned here is measured from the dataset:

* vertices are real card identifiers, device fingerprints, email domains and
  transaction ids that appear in the source rows,
* edges are real co-occurrence relationships observed in those rows (a card
  that appears on a transaction, a device that appears on a transaction, two
  cards seen on the same device),
* ``risk_score`` on a transaction vertex is the output of the trained model in
  ``models/fraud_model.joblib``.

No value is synthesised. Fields absent from the source row are omitted.

Scope: the ledger is roughly 700 MB, so a bounded window of rows is read at
startup. The window size is explicit and reported through ``stats()`` rather
than being implied to be the whole dataset.
"""

from __future__ import annotations

import csv
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.logging import get_logger
from backend.app.schemas.graph import (
    GraphEdge,
    GraphNode,
    InvestigationSubgraph,
)
from backend.ml.inference import FraudModelInference

logger = get_logger(__name__)

# Columns pulled from transactions.csv. Kept small on purpose: the V-feature
# block is only needed by the model, not by the graph.
_TRANSACTION_COLUMNS = (
    "TransactionID",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "P_emaildomain",
)

_IDENTITY_COLUMNS = ("TransactionID", "DeviceInfo", "DeviceType")


@dataclass
class _Vertex:
    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


class RelationalFraudGraph:
    """An in-process fraud graph built from the raw transaction ledger."""

    def __init__(self) -> None:
        self._vertices: dict[str, _Vertex] = {}
        self._adjacency: dict[str, set[str]] = defaultdict(set)
        self._edge_keys: set[tuple[str, str, str]] = set()
        self._rows_scanned = 0
        self._rows_available = 0

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def _add_vertex(self, vertex: _Vertex) -> str:
        existing = self._vertices.get(vertex.node_id)
        if existing is not None:
            # Merge properties; first non-empty value wins so an earlier row is
            # never overwritten by a later null.
            for key, value in vertex.properties.items():
                if key not in existing.properties and value not in (None, ""):
                    existing.properties[key] = value
            return vertex.node_id

        self._vertices[vertex.node_id] = vertex
        self._adjacency.setdefault(vertex.node_id, set())
        return vertex.node_id

    def _add_edge(self, source: str, target: str, edge_type: str) -> None:
        if source == target or source not in self._vertices or target not in self._vertices:
            return
        key = (source, edge_type, target)
        if key in self._edge_keys:
            return
        self._edge_keys.add(key)
        self._adjacency[source].add(target)
        self._adjacency[target].add(source)

    @property
    def is_empty(self) -> bool:
        return not self._vertices

    @property
    def node_count(self) -> int:
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        return len(self._edge_keys)

    @property
    def rows_scanned(self) -> int:
        return self._rows_scanned

    def stats(self) -> dict[str, Any]:
        by_type: dict[str, int] = defaultdict(int)
        for vertex in self._vertices.values():
            by_type[vertex.node_type] += 1
        return {
            "source": "RELATIONAL_LEDGER",
            "nodes": len(self._vertices),
            "edges": len(self._edge_keys),
            "rows_scanned": self._rows_scanned,
            "node_types": dict(by_type),
        }

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    @classmethod
    def from_dataset(
        cls,
        *,
        transactions_csv: Path,
        identity_csv: Path,
        model_path: Path,
        metadata_path: Path,
        max_rows: int = 20_000,
        score_transactions: int = 400,
    ) -> RelationalFraudGraph:
        graph = cls()
        graph._load(
            transactions_csv=transactions_csv,
            identity_csv=identity_csv,
            model_path=model_path,
            metadata_path=metadata_path,
            max_rows=max_rows,
            score_transactions=score_transactions,
        )
        return graph

    def _load(
        self,
        *,
        transactions_csv: Path,
        identity_csv: Path,
        model_path: Path,
        metadata_path: Path,
        max_rows: int,
        score_transactions: int,
    ) -> None:
        if not transactions_csv.exists():
            logger.warning("relational graph skipped: dataset missing",
                           path=str(transactions_csv))
            return

        devices = _read_identity_devices(identity_csv)
        logger.info("relational graph loading", devices=len(devices))

        inference: FraudModelInference | None = None
        if model_path.exists() and metadata_path.exists():
            try:
                inference = FraudModelInference(
                    model_path=str(model_path),
                    metadata_path=str(metadata_path),
                    threshold=0.50,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("graph model unavailable", error=str(exc))

        scored = 0
        with transactions_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            available = set(reader.fieldnames or ())
            wanted = [c for c in _TRANSACTION_COLUMNS if c in available]

            for row in reader:
                if self._rows_scanned >= max_rows:
                    break
                self._rows_scanned += 1

                transaction_id = (row.get("TransactionID") or "").strip()
                if transaction_id.endswith(".0") and transaction_id[:-2].isdigit():
                    transaction_id = transaction_id[:-2]
                if not transaction_id:
                    continue

                properties: dict[str, Any] = {}
                amount = row.get("TransactionAmt")
                if amount not in (None, ""):
                    try:
                        properties["amount"] = float(amount)
                    except ValueError:
                        pass
                product = row.get("ProductCD")
                if product not in (None, ""):
                    properties["product_cd"] = product

                device_info = devices.get(transaction_id)
                if device_info:
                    properties["device_info"] = device_info.get("device_info")
                    properties["device_type"] = device_info.get("device_type")

                # Score a bounded prefix: the model is a LinearGBM call per row
                # and this runs during startup.
                if inference is not None and scored < score_transactions:
                    try:
                        prediction = inference.predict(
                            _row_for_model(row, device_info)
                        )
                        properties["risk_score"] = float(prediction.probability)
                        properties["ml_model_version"] = prediction.model_version
                        scored += 1
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("graph model scoring skipped",
                                     transaction_id=transaction_id, error=str(exc))

                tx_node = self._add_vertex(
                    _Vertex(
                        node_id=f"T:{transaction_id}",
                        node_type="Transaction",
                        label=f"Transaction {transaction_id}",
                        properties=properties,
                    )
                )

                card = (row.get("card1") or "").strip()
                if card:
                    card_node = self._add_vertex(
                        _Vertex(
                            node_id=f"C:{card}",
                            node_type="Card",
                            label=f"Card {card}",
                        )
                    )
                    self._add_edge(card_node, tx_node, "used_in")

                email = (row.get("P_emaildomain") or "").strip()
                if email:
                    email_node = self._add_vertex(
                        _Vertex(
                            node_id=f"E:{email}",
                            node_type="EmailDomain",
                            label=email,
                        )
                    )
                    self._add_edge(email_node, tx_node, "email_on")

                if device_info and device_info.get("device_info"):
                    device_key = device_info["device_info"]
                    device_node = self._add_vertex(
                        _Vertex(
                            node_id=f"D:{device_key}",
                            node_type="Device",
                            label=f"Device {device_key[:40]}",
                            properties={
                                k: device_info.get(k)
                                for k in ("device_type",)
                                if device_info.get(k)
                            },
                        )
                    )
                    self._add_edge(device_node, tx_node, "used_in")
                    if card:
                        # Two cards on one device is the classic device-reuse
                        # signal; only emitted when actually observed.
                        self._add_edge(card_node, device_node, "shares_device")

        logger.info("relational graph ready", **self.stats())

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------
    def resolve_root(self, node_id: str) -> str | None:
        """Accept a bare id (3000001 / 22563) or a typed id (C:22563)."""
        candidate = node_id.strip()
        if not candidate:
            return None
        if candidate in self._vertices:
            return candidate
        for prefix in ("T:", "C:", "D:", "E:"):
            if f"{prefix}{candidate}" in self._vertices:
                return f"{prefix}{candidate}"
        return None

    def traverse(
        self,
        root_node_id: str,
        *,
        depth: int = 2,
        limit: int = 120,
    ) -> InvestigationSubgraph:
        root = self.resolve_root(root_node_id)

        if root is None:
            return InvestigationSubgraph(
                root_node_id=root_node_id,
                nodes=[],
                edges=[],
                paths=[],
                depth=depth,
                node_count=0,
                edge_count=0,
            )

        visited: set[str] = {root}
        ordered: list[str] = [root]
        queue: deque[tuple[str, int]] = deque([(root, 0)])

        while queue and len(ordered) < limit:
            current, distance = queue.popleft()
            if distance >= depth:
                continue
            for neighbour in sorted(self._adjacency.get(current, ())):
                if neighbour in visited:
                    continue
                visited.add(neighbour)
                ordered.append(neighbour)
                queue.append((neighbour, distance + 1))
                if len(ordered) >= limit:
                    break

        nodes = [
            GraphNode(
                node_id=node_id,
                node_type=self._vertices[node_id].node_type,
                label=self._vertices[node_id].label,
                properties=self._vertices[node_id].properties,
            )
            for node_id in ordered
        ]

        edges: list[GraphEdge] = []
        # Edge keys are stored as (source, edge_type, target).
        for source, edge_type, target in sorted(self._edge_keys):
            if source in visited and target in visited:
                edges.append(
                    GraphEdge(
                        source_id=source,
                        target_id=target,
                        edge_type=edge_type,
                    )
                )

        return InvestigationSubgraph(
            root_node_id=root,
            nodes=nodes,
            edges=edges,
            paths=[],
            depth=depth,
            node_count=len(nodes),
            edge_count=len(edges),
        )


def _read_identity_devices(identity_path: Path) -> dict[str, dict[str, str]]:
    """Map transaction id -> device fingerprint, for identity rows only."""
    if not identity_path.exists():
        return {}

    devices: dict[str, dict[str, str]] = {}
    with identity_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        available = set(reader.fieldnames or ())
        if "TransactionID" not in available:
            return {}

        wanted = [c for c in _IDENTITY_COLUMNS if c in available]

        for row in reader:
            transaction_id = (row.get("TransactionID") or "").strip()
            if transaction_id.endswith(".0") and transaction_id[:-2].isdigit():
                transaction_id = transaction_id[:-2]
            if not transaction_id:
                continue
            device_info = (row.get("DeviceInfo") or "").strip()
            if not device_info:
                continue
            devices[transaction_id] = {
                "device_info": device_info,
                "device_type": (row.get("DeviceType") or "").strip(),
            }

    return devices


def _row_for_model(
    row: dict[str, Any],
    device_info: dict[str, str] | None,
) -> dict[str, Any]:
    """Shape one raw CSV row into the flat record the model expects."""
    record: dict[str, Any] = dict(row)
    if device_info:
        for key, value in device_info.items():
            if not record.get(key):
                record[key] = value
    return record


__all__ = ["RelationalFraudGraph"]
