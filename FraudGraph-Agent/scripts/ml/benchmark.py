from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from backend.ml.inference import FraudModelInference
from backend.ml.transaction_loader import TransactionRecordLoader


@dataclass(slots=True)
class BenchmarkPrediction:
    case_id: str
    trigger_type: str
    customer_id: str
    card_id: str
    transaction_id: str
    bank_risk_score: float | None
    ml_probability: float
    ml_prediction: bool
    threshold: float


class FraudModelBenchmark:
    """Run the trained fraud model across all 20 benchmark cases."""

    def __init__(
        self,
        *,
        inference: FraudModelInference,
        transaction_loader: TransactionRecordLoader,
    ) -> None:
        self.inference = inference
        self.transaction_loader = transaction_loader

    def load_cases(
        self,
        case_pack_path: str | Path,
    ) -> list[dict[str, Any]]:
        path = Path(case_pack_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Case pack not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            rows = list(csv.DictReader(handle))

        if not rows:
            raise ValueError(
                "Case pack contains no benchmark cases."
            )

        required = {
            "case_id",
            "trigger_type",
            "flagged_txn_id",
            "card_id",
            "customer_id",
            "risk_score",
        }

        missing = required - set(rows[0].keys())

        if missing:
            raise ValueError(
                f"Case pack is missing columns: "
                f"{sorted(missing)}"
            )

        return rows

    def evaluate(
        self,
        cases: list[dict[str, Any]],
    ) -> list[BenchmarkPrediction]:
        predictions: list[BenchmarkPrediction] = []

        for case in cases:
            transaction_id = str(
                case["flagged_txn_id"]
            ).strip()

            if not transaction_id:
                raise ValueError(
                    f"Missing flagged transaction for "
                    f"case {case.get('case_id')}"
                )

            transaction = (
                self.transaction_loader.get_transaction(
                    transaction_id
                )
            )

            prediction = self.inference.predict(
                transaction
            )

            predictions.append(
                BenchmarkPrediction(
                    case_id=str(case["case_id"]),
                    trigger_type=str(
                        case["trigger_type"]
                    ),
                    customer_id=str(
                        case["customer_id"]
                    ),
                    card_id=str(case["card_id"]),
                    transaction_id=transaction_id,
                    bank_risk_score=self._float_or_none(
                        case.get("risk_score")
                    ),
                    ml_probability=prediction.probability,
                    ml_prediction=prediction.is_fraud,
                    threshold=prediction.threshold,
                )
            )

        return predictions

    @staticmethod
    def _float_or_none(
        value: Any,
    ) -> float | None:
        if value is None:
            return None

        text = str(value).strip()

        if not text or text in {"-", "—", "nan", "None"}:
            return None

        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def save_report(
        output_path: str | Path,
        predictions: list[BenchmarkPrediction],
    ) -> None:
        path = Path(output_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "benchmark_cases": len(predictions),
            "ground_truth_available": False,
            "note": (
                "The official benchmark answer key is hidden. "
                "These are model predictions only and must not "
                "be interpreted as benchmark accuracy."
            ),
            "cases": [
                asdict(prediction)
                for prediction in predictions
            ],
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
            ),
            encoding="utf-8",
        )