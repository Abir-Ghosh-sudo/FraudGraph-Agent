"""
Train the supervised fraud-risk model from HHGOA closed-case history.

The training target is derived only from transactions explicitly referenced
by closed investigations:

    confirmed_fraud -> 1
    cleared        -> 0

Transactions that are not referenced by a closed case are treated as
unlabeled and are excluded from supervised training. The benchmark case pack
is never used for training.

The resulting LightGBM model is intended to provide a predictive signal to
the FraudGraph Agent; it is not treated as the investigation ground truth.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)


DEFAULT_DATA_DIR = Path("data/raw")
DEFAULT_MODEL_DIR = Path("models")

TRANSACTION_ID = "TransactionID"

# Fields with useful fraud/entity information and manageable cardinality.
CATEGORICAL_COLUMNS = [
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "addr2",
    "P_emaildomain",
    "R_emaildomain",
    "DeviceType",
    "DeviceInfo",
]

# Core numeric transaction / behavioral features.
NUMERIC_COLUMNS = [
    "TransactionAmt",
    "TransactionDT",
    "dist1",
    "dist2",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "C8",
    "C9",
    "C10",
    "C11",
    "C12",
    "C13",
    "C14",
]

# Identity-side numeric signals.
IDENTITY_NUMERIC_COLUMNS = [
    f"id_{index:02d}" for index in range(1, 39)
]

# M columns are categorical-ish indicator fields.
MATCH_COLUMNS = [
    f"M{index}" for index in range(1, 10)
]

# Selected Vesta behavioral variables. These are deliberately limited rather
# than blindly feeding all V-columns into the first production benchmark.
V_COLUMNS = [
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8",
    "V9",
    "V10",
    "V11",
    "V12",
    "V13",
    "V14",
    "V15",
    "V16",
    "V17",
    "V18",
    "V19",
    "V20",
    "V21",
    "V22",
    "V23",
    "V24",
    "V25",
    "V26",
    "V27",
    "V28",
    "V29",
    "V30",
    "V31",
    "V32",
    "V33",
    "V34",
    "V35",
    "V36",
    "V37",
    "V38",
    "V39",
    "V40",
    "V41",
    "V42",
    "V43",
    "V44",
    "V45",
    "V46",
    "V47",
    "V48",
    "V49",
    "V50",
]


def normalize_transaction_id(value: Any) -> str | None:
    """Normalize transaction identifiers without changing their meaning."""
    if value is None:
        return None

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]

    return text


def parse_transaction_ids(value: Any) -> list[str]:
    """Parse pipe-separated transaction IDs from a closed case."""
    if value is None or pd.isna(value):
        return []

    result: list[str] = []

    for item in str(value).split("|"):
        transaction_id = normalize_transaction_id(item)

        if transaction_id:
            result.append(transaction_id)

    return result


def build_transaction_labels(
    cases_path: Path,
) -> dict[str, int]:
    """
    Build transaction-level labels from closed investigations.

    A transaction can theoretically occur in more than one historical case.
    If conflicting outcomes are encountered, confirmed fraud takes precedence
    because it is the stronger explicit case outcome.
    """
    cases = pd.read_csv(
        cases_path,
        usecols=["outcome", "txn_ids"],
        low_memory=False,
    )

    labels: dict[str, int] = {}

    for row in cases.itertuples(index=False):
        outcome = str(row.outcome).strip().lower()
        transaction_ids = parse_transaction_ids(row.txn_ids)

        if outcome not in {"confirmed_fraud", "cleared"}:
            continue

        label = 1 if outcome == "confirmed_fraud" else 0

        for transaction_id in transaction_ids:
            previous = labels.get(transaction_id)

            if previous is None:
                labels[transaction_id] = label
            elif previous == 0 and label == 1:
                labels[transaction_id] = 1

    return labels


def select_existing(
    requested: list[str],
    available: set[str],
) -> list[str]:
    """Return requested columns that actually exist in the dataset."""
    return [column for column in requested if column in available]


def load_labeled_transactions(
    transactions_path: Path,
    labels: dict[str, int],
    chunksize: int = 50_000,
) -> pd.DataFrame:
    """
    Read transactions in chunks and retain only transactions with explicit
    closed-case labels.
    """
    if not labels:
        raise RuntimeError(
            "No transaction labels were produced from closed cases."
        )

    available_columns = pd.read_csv(
        transactions_path,
        nrows=0,
    ).columns.tolist()

    available = set(available_columns)

    requested = [
        TRANSACTION_ID,
        "customer_id",
        "ts",
        "channel",
        "risk_score",
        *CATEGORICAL_COLUMNS,
        *NUMERIC_COLUMNS,
        *MATCH_COLUMNS,
        *V_COLUMNS,
    ]

    requested = list(dict.fromkeys(requested))
    usecols = select_existing(requested, available)

    if TRANSACTION_ID not in usecols:
        raise RuntimeError(
            f"{TRANSACTION_ID!r} was not found in transactions.csv."
        )

    chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        transactions_path,
        usecols=usecols,
        chunksize=chunksize,
        low_memory=False,
    ):
        normalized_ids = chunk[TRANSACTION_ID].map(
            normalize_transaction_id
        )

        mask = normalized_ids.isin(labels.keys())

        if not mask.any():
            continue

        selected = chunk.loc[mask].copy()

        selected[TRANSACTION_ID] = normalized_ids.loc[mask]
        selected["target"] = selected[TRANSACTION_ID].map(labels)

        chunks.append(selected)

    if not chunks:
        raise RuntimeError(
            "No closed-case transaction IDs matched transactions.csv."
        )

    dataframe = pd.concat(
        chunks,
        ignore_index=True,
    )

    dataframe = dataframe.drop_duplicates(
        subset=[TRANSACTION_ID],
        keep="first",
    )

    return dataframe


def load_identity(
    identity_path: Path,
    transaction_ids: set[str],
) -> pd.DataFrame:
    """Load only identity rows relevant to the supervised transactions."""
    header = pd.read_csv(
        identity_path,
        nrows=0,
    ).columns.tolist()

    requested = [
        TRANSACTION_ID,
        *IDENTITY_NUMERIC_COLUMNS,
        "DeviceType",
        "DeviceInfo",
    ]

    usecols = select_existing(
        requested,
        set(header),
    )

    if TRANSACTION_ID not in usecols:
        return pd.DataFrame()

    chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        identity_path,
        usecols=usecols,
        chunksize=50_000,
        low_memory=False,
    ):
        chunk[TRANSACTION_ID] = chunk[TRANSACTION_ID].map(
            normalize_transaction_id
        )

        chunk = chunk[
            chunk[TRANSACTION_ID].isin(transaction_ids)
        ]

        if not chunk.empty:
            chunks.append(chunk)

    if not chunks:
        return pd.DataFrame()

    identity = pd.concat(
        chunks,
        ignore_index=True,
    )

    return identity.drop_duplicates(
        subset=[TRANSACTION_ID],
        keep="first",
    )


def add_temporal_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Add calendar/time-of-day features from the supplied transaction time."""
    dataframe = dataframe.copy()

    if "ts" not in dataframe.columns:
        return dataframe

    timestamps = pd.to_datetime(
        dataframe["ts"],
        errors="coerce",
    )

    dataframe["txn_year"] = timestamps.dt.year
    dataframe["txn_month"] = timestamps.dt.month
    dataframe["txn_day"] = timestamps.dt.day
    dataframe["txn_dayofweek"] = timestamps.dt.dayofweek
    dataframe["txn_hour"] = timestamps.dt.hour
    dataframe["txn_minute"] = timestamps.dt.minute

    dataframe["txn_is_weekend"] = (
        timestamps.dt.dayofweek >= 5
    ).astype("int8")

    return dataframe


def add_frequency_features(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, int]]]:
    """
    Frequency encode categorical/entity fields using TRAIN data only.

    This prevents validation information from influencing the feature
    statistics.
    """
    train = train.copy()
    validation = validation.copy()

    mappings: dict[str, dict[str, int]] = {}

    for column in columns:
        if column not in train.columns:
            continue

        train_values = (
            train[column]
            .astype("string")
            .fillna("__MISSING__")
        )

        validation_values = (
            validation[column]
            .astype("string")
            .fillna("__MISSING__")
        )

        counts = train_values.value_counts(
            dropna=False,
        )

        mapping = {
            str(key): int(value)
            for key, value in counts.items()
        }

        mappings[column] = mapping

        train[f"{column}__freq"] = (
            train_values.map(mapping)
            .fillna(0)
            .astype("float32")
        )

        validation[f"{column}__freq"] = (
            validation_values.map(mapping)
            .fillna(0)
            .astype("float32")
        )

    return train, validation, mappings


def prepare_features(
    train: pd.DataFrame,
    validation: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    list[str],
    dict[str, dict[str, int]],
]:
    """Build the final numeric feature matrices."""
    train = add_temporal_features(train)
    validation = add_temporal_features(validation)

    frequency_columns = [
        *CATEGORICAL_COLUMNS,
        "customer_id",
        "channel",
        *MATCH_COLUMNS,
    ]

    train, validation, frequency_maps = add_frequency_features(
        train,
        validation,
        frequency_columns,
    )

    feature_columns: list[str] = []

    requested_numeric = [
        "TransactionAmt",
        "TransactionDT",
        "risk_score",
        "dist1",
        "dist2",
        *NUMERIC_COLUMNS,
        *MATCH_COLUMNS,
        *V_COLUMNS,
        *IDENTITY_NUMERIC_COLUMNS,
        "txn_year",
        "txn_month",
        "txn_day",
        "txn_dayofweek",
        "txn_hour",
        "txn_minute",
        "txn_is_weekend",
    ]

    requested_numeric = list(
        dict.fromkeys(requested_numeric)
    )

    for column in requested_numeric:
        if column in train.columns:
            feature_columns.append(column)

    for column in frequency_columns:
        encoded = f"{column}__freq"

        if encoded in train.columns:
            feature_columns.append(encoded)

    feature_columns = list(
        dict.fromkeys(feature_columns)
    )

    if not feature_columns:
        raise RuntimeError(
            "No usable ML features were found."
        )

    X_train = train[feature_columns].copy()
    X_validation = validation[feature_columns].copy()

    for dataframe in (X_train, X_validation):
        for column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

        dataframe.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True,
        )

    return (
        X_train,
        X_validation,
        feature_columns,
        frequency_maps,
    )


def chronological_split(
    dataframe: pd.DataFrame,
    validation_fraction: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split labeled transactions chronologically."""
    if "ts" not in dataframe.columns:
        raise RuntimeError(
            "transactions.csv must contain the ts column."
        )

    dataframe = dataframe.copy()

    dataframe["__timestamp"] = pd.to_datetime(
        dataframe["ts"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=["__timestamp"],
    )

    dataframe = dataframe.sort_values(
        "__timestamp",
    ).reset_index(drop=True)

    split_index = int(
        len(dataframe) * (1.0 - validation_fraction)
    )

    split_index = max(
        1,
        min(split_index, len(dataframe) - 1),
    )

    train = dataframe.iloc[:split_index].copy()
    validation = dataframe.iloc[split_index:].copy()

    train.drop(
        columns=["__timestamp"],
        inplace=True,
    )

    validation.drop(
        columns=["__timestamp"],
        inplace=True,
    )

    return train, validation


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
) -> lgb.LGBMClassifier:
    """Train the LightGBM fraud classifier."""
    model = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=600,
        learning_rate=0.04,
        num_leaves=63,
        max_depth=-1,
        min_child_samples=40,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.5,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (X_validation, y_validation),
        ],
        eval_metric="auc",
        callbacks=[
            lgb.early_stopping(
                stopping_rounds=60,
                verbose=True,
            ),
        ],
    )

    return model


def evaluate_model(
    model: lgb.LGBMClassifier,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
) -> dict[str, Any]:
    """Calculate validation metrics."""
    probabilities = model.predict_proba(
        X_validation,
    )[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype("int8")

    metrics: dict[str, Any] = {
        "roc_auc": float(
            roc_auc_score(
                y_validation,
                probabilities,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_validation,
                probabilities,
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_validation,
            predictions,
        ).tolist(),
        "classification_report": classification_report(
            y_validation,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "validation_rows": int(len(y_validation)),
        "validation_positive": int(y_validation.sum()),
        "validation_negative": int(
            (y_validation == 0).sum()
        ),
    }

    return metrics


def save_artifacts(
    model: lgb.LGBMClassifier,
    feature_columns: list[str],
    frequency_maps: dict[str, dict[str, int]],
    metrics: dict[str, Any],
    train_rows: int,
    validation_rows: int,
    model_dir: Path,
) -> None:
    """Persist the trained model and reproducibility metadata."""
    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = model_dir / "fraud_model.joblib"
    metadata_path = model_dir / "fraud_model_metadata.json"

    joblib.dump(
        model,
        model_path,
    )

    from datetime import datetime, timezone

    metadata = {
        "model_version": "v1.0.0",
        "model_type": "lightgbm.LGBMClassifier",
        "model_path": str(model_path),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "threshold": 0.50,
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "frequency_maps": frequency_maps,
        "metrics": metrics,
        "train_rows": train_rows,
        "validation_rows": validation_rows,
        "target_definition": {
            "confirmed_fraud": 1,
            "cleared": 0,
            "unreferenced_transactions": "excluded",
        },
        "benchmark_excluded": True,
        "random_state": 42,
        "random_seed": 42,
    }

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the HHGOA fraud-risk model.",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
    )

    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
    )

    parser.add_argument(
        "--validation-fraction",
        type=float,
        default=0.20,
    )

    parser.add_argument(
        "--chunksize",
        type=int,
        default=50_000,
    )

    args = parser.parse_args()

    if not 0.05 <= args.validation_fraction <= 0.50:
        raise ValueError(
            "--validation-fraction must be between 0.05 and 0.50."
        )

    transactions_path = (
        args.data_dir / "transactions.csv"
    )

    identity_path = (
        args.data_dir / "identity.csv"
    )

    cases_path = (
        args.data_dir / "closed_cases_history.csv"
    )

    required_files = [
        transactions_path,
        identity_path,
        cases_path,
    ]

    missing = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing required dataset files:\n"
            + "\n".join(missing)
        )

    print("Building transaction labels from closed cases...")

    labels = build_transaction_labels(
        cases_path,
    )

    positive_labels = sum(
        value == 1
        for value in labels.values()
    )

    negative_labels = sum(
        value == 0
        for value in labels.values()
    )

    print(
        f"Labeled transactions: {len(labels):,}"
    )

    print(
        f"Confirmed fraud labels: {positive_labels:,}"
    )

    print(
        f"Cleared labels: {negative_labels:,}"
    )

    print(
        "\nLoading labeled transactions..."
    )

    transactions = load_labeled_transactions(
        transactions_path=transactions_path,
        labels=labels,
        chunksize=args.chunksize,
    )

    print(
        f"Matched transaction rows: {len(transactions):,}"
    )

    print(
        "\nLoading relevant identity records..."
    )

    identity = load_identity(
        identity_path=identity_path,
        transaction_ids=set(
            transactions[TRANSACTION_ID]
        ),
    )

    if not identity.empty:
        transactions = transactions.merge(
            identity,
            on=TRANSACTION_ID,
            how="left",
            suffixes=("", "_identity"),
        )

        print(
            f"Identity rows joined: {len(identity):,}"
        )
    else:
        print(
            "No matching identity records found."
        )

    train, validation = chronological_split(
        transactions,
        validation_fraction=args.validation_fraction,
    )

    print(
        "\nChronological split:"
    )

    print(
        f"Train rows: {len(train):,}"
    )

    print(
        f"Validation rows: {len(validation):,}"
    )

    if train["target"].nunique() < 2:
        raise RuntimeError(
            "Training split contains only one target class."
        )

    if validation["target"].nunique() < 2:
        raise RuntimeError(
            "Validation split contains only one target class."
        )

    X_train, X_validation, feature_columns, frequency_maps = (
        prepare_features(
            train,
            validation,
        )
    )

    y_train = train["target"].astype("int8")
    y_validation = validation["target"].astype("int8")

    print(
        f"\nML features: {len(feature_columns)}"
    )

    print(
        "Training LightGBM..."
    )

    model = train_model(
        X_train,
        y_train,
        X_validation,
        y_validation,
    )

    metrics = evaluate_model(
        model,
        X_validation,
        y_validation,
    )

    print(
        "\nValidation metrics:"
    )

    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )

    save_artifacts(
        model=model,
        feature_columns=feature_columns,
        frequency_maps=frequency_maps,
        metrics=metrics,
        train_rows=len(train),
        validation_rows=len(validation),
        model_dir=args.model_dir,
    )

    print(
        "\nSaved:"
    )

    print(
        args.model_dir / "fraud_model.joblib"
    )

    print(
        args.model_dir / "fraud_model_metadata.json"
    )


if __name__ == "__main__":
    main()