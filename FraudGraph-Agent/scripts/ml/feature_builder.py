from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class FeatureBuilder:
    """Build inference features compatible with the trained fraud model."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        frequency_maps: dict[str, dict[str, int]] | None = None,
    ) -> None:
        self.feature_columns = list(feature_columns)
        self.frequency_maps = frequency_maps or {}

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            raise ValueError(
                "Cannot build features from an empty dataframe."
            )

        data = frame.copy()

        self._add_temporal_features(data)
        self._add_frequency_features(data)

        for column in self.feature_columns:
            if column not in data.columns:
                data[column] = np.nan

        features = data[self.feature_columns].copy()

        for column in features.columns:
            if not pd.api.types.is_numeric_dtype(
                features[column]
            ):
                features[column] = pd.to_numeric(
                    features[column],
                    errors="coerce",
                )

        features = features.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        return features

    def _add_temporal_features(
        self,
        data: pd.DataFrame,
    ) -> None:
        if "ts" not in data.columns:
            return

        timestamps = pd.to_datetime(
            data["ts"],
            errors="coerce",
        )

        data["year"] = timestamps.dt.year
        data["month"] = timestamps.dt.month
        data["day"] = timestamps.dt.day
        data["dayofweek"] = timestamps.dt.dayofweek
        data["hour"] = timestamps.dt.hour
        data["minute"] = timestamps.dt.minute
        data["weekend"] = (
            timestamps.dt.dayofweek >= 5
        ).astype("float64")

    def _add_frequency_features(
        self,
        data: pd.DataFrame,
    ) -> None:
        for column, mapping in self.frequency_maps.items():
            output_column = f"{column}__freq"

            if column not in data.columns:
                data[output_column] = 0.0
                continue

            values = data[column].astype(str)

            normalized_mapping = {
                str(key): value
                for key, value in mapping.items()
            }

            data[output_column] = (
                values.map(normalized_mapping)
                .fillna(0.0)
            )