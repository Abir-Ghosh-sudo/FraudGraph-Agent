from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from backend.ml.feature_builder import FeatureBuilder
from backend.ml.fraud_model import FraudModel


@dataclass(slots=True)
class FraudPrediction:
    transaction_id: str
    probability: float
    is_fraud: bool
    threshold: float
    model_version: str | None = None


class FraudModelInference:
    """Run fraud-model inference on a real transaction record."""

    def __init__(
        self,
        *,
        model_path: str | Path,
        metadata_path: str | Path,
        threshold: float = 0.50,
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")

        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.threshold = threshold

        self._model: FraudModel | None = None
        self._feature_builder: FeatureBuilder | None = None
        self._metadata: dict[str, Any] | None = None

    def _load(self) -> None:
        if self._model is not None and self._feature_builder is not None:
            return

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Fraud model metadata not found: {self.metadata_path}"
            )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Fraud model not found: {self.model_path}"
            )

        with self.metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        if not isinstance(metadata, dict):
            raise ValueError("Model metadata must contain a JSON object")

        feature_columns = metadata.get("feature_columns")

        if not isinstance(feature_columns, list) or not feature_columns:
            raise ValueError(
                "Model metadata does not contain valid feature_columns"
            )

        frequency_maps = metadata.get("frequency_maps") or {}

        if not isinstance(frequency_maps, dict):
            raise ValueError("frequency_maps must be a JSON object")

        self._metadata = metadata

        self._model = FraudModel(
            model_path=self.model_path,
            threshold=self.threshold,
        )

        self._feature_builder = FeatureBuilder(
            feature_columns=feature_columns,
            frequency_maps=frequency_maps,
        )

    @property
    def model(self) -> FraudModel:
        self._load()

        assert self._model is not None
        return self._model

    @property
    def feature_builder(self) -> FeatureBuilder:
        self._load()

        assert self._feature_builder is not None
        return self._feature_builder

    @property
    def metadata(self) -> dict[str, Any]:
        self._load()

        assert self._metadata is not None
        return self._metadata

    def predict(
        self,
        transaction: dict[str, Any],
    ) -> FraudPrediction:
        if not transaction:
            raise ValueError("transaction must not be empty")

        transaction_id = transaction.get("TransactionID")

        if transaction_id is None:
            transaction_id = transaction.get("transaction_id")

        if transaction_id is None:
            raise ValueError(
                "transaction must contain TransactionID or transaction_id"
            )

        transaction_id = str(transaction_id).strip()

        if not transaction_id:
            raise ValueError("transaction ID must not be empty")

        frame = pd.DataFrame([transaction])

        features = self.feature_builder.transform(frame)

        probability = self.model.predict_probability(features)

        model_version = self.metadata.get("model_version")

        return FraudPrediction(
            transaction_id=transaction_id,
            probability=probability,
            is_fraud=probability >= self.threshold,
            threshold=self.threshold,
            model_version=(
                str(model_version)
                if model_version is not None
                else None
            ),
        )

    def predict_probability(
        self,
        transaction: dict[str, Any],
    ) -> float:
        return self.predict(transaction).probability