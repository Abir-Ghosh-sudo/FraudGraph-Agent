from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd


class FeatureBuilder:
    """
    Builds inference features compatible with the fraud-model training pipeline.

    The builder intentionally follows the training-time feature contract:
    - temporal features from `ts`
    - training-only frequency maps
    - exact feature-column ordering from model metadata
    - numeric coercion with NaN for values that cannot be converted
    """

    def __init__(
        self,
        *,
        feature_columns: Sequence[str],
        frequency_maps: Mapping[str, Mapping[str, float | int]] | None = None,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns must not be empty")

        self.feature_columns = list(feature_columns)
        self.frequency_maps = {
            str(column): {
                str(key): float(value)
                for key, value in mapping.items()
            }
            for column, mapping in (frequency_maps or {}).items()
        }

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw transaction records into model-ready features.

        The returned DataFrame:
        - contains exactly the columns requested by feature_columns
        - preserves feature-column order
        - contains numeric values only
        - uses NaN for unavailable/non-numeric values
        """

        if not isinstance(frame, pd.DataFrame):
            raise TypeError("frame must be a pandas DataFrame")

        if frame.empty:
            raise ValueError("Cannot build features from an empty DataFrame")

        data = frame.copy()

        self._add_temporal_features(data)
        self._add_frequency_features(data)

        # Guarantee that every model feature exists.
        for column in self.feature_columns:
            if column not in data.columns:
                data[column] = np.nan

        # Exact training/model feature ordering.
        features = data.loc[:, self.feature_columns].copy()

        # The trained pipeline expects a numeric feature matrix.
        for column in features.columns:
            if not pd.api.types.is_numeric_dtype(features[column]):
                features[column] = pd.to_numeric(
                    features[column],
                    errors="coerce",
                )

        # Normalise infinite values exactly as missing values.
        features = features.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        return features.reset_index(drop=True)

    @staticmethod
    def _add_temporal_features(data: pd.DataFrame) -> None:
        """Create the temporal features used during model training."""

        if "ts" not in data.columns:
            return

        timestamps = pd.to_datetime(
            data["ts"],
            errors="coerce",
        )

        data["year"] = timestamps.dt.year.astype("float64")
        data["month"] = timestamps.dt.month.astype("float64")
        data["day"] = timestamps.dt.day.astype("float64")
        data["dayofweek"] = timestamps.dt.dayofweek.astype("float64")
        data["hour"] = timestamps.dt.hour.astype("float64")
        data["minute"] = timestamps.dt.minute.astype("float64")
        data["weekend"] = (
            timestamps.dt.dayofweek >= 5
        ).astype("float64")

        # Invalid timestamps produce NaN for datetime components.
        invalid_timestamp = timestamps.isna()

        if invalid_timestamp.any():
            temporal_columns = (
                "year",
                "month",
                "day",
                "dayofweek",
                "hour",
                "minute",
            )

            for column in temporal_columns:
                data.loc[invalid_timestamp, column] = np.nan

            data.loc[invalid_timestamp, "weekend"] = np.nan

    def _add_frequency_features(
        self,
        data: pd.DataFrame,
    ) -> None:
        """
        Apply frequency maps generated during training.

        Frequency maps MUST come from training data only.
        Unknown inference values receive 0.0 rather than being
        assigned a value derived from the inference dataset.
        """

        for column, mapping in self.frequency_maps.items():
            output_column = f"{column}__freq"

            if column not in data.columns:
                data[output_column] = 0.0
                continue

            values = data[column].astype("string")

            normalized_mapping = {
                str(key): float(value)
                for key, value in mapping.items()
            }

            data[output_column] = (
                values.map(normalized_mapping)
                .fillna(0.0)
                .astype("float64")
            )