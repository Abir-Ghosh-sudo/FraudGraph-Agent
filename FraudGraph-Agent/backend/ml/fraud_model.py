from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


class FraudModel:
    """Lazy-loaded wrapper around the trained fraud model."""

    def __init__(
        self,
        model_path: str | Path,
        *,
        threshold: float = 0.50,
    ) -> None:
        self.model_path = Path(model_path)
        self.threshold = threshold
        self._model: Any | None = None

    def load(self) -> None:
        """Load the trained model into memory."""
        if self._model is not None:
            return

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Fraud model not found: {self.model_path}"
            )

        self._model = joblib.load(self.model_path)

    @property
    def model(self) -> Any:
        """Return the loaded model."""
        self.load()
        return self._model

    def predict_probability(self, features: Any) -> float:
        """Return the probability that a transaction is fraudulent."""
        probability = float(
            self.model.predict_proba(features)[0][1]
        )

        return max(0.0, min(1.0, probability))

    def predict(self, features: Any) -> bool:
        """Return the binary fraud decision."""
        return self.predict_probability(features) >= self.threshold

    def predict_with_probability(
        self,
        features: Any,
    ) -> dict[str, float | bool]:
        """Return both fraud probability and binary prediction."""
        probability = self.predict_probability(features)

        return {
            "probability": probability,
            "is_fraud": probability >= self.threshold,
        }
