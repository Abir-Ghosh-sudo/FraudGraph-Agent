from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from backend.ml.benchmark import FraudBenchmark
from backend.ml.inference import FraudModelInference
from backend.ml.transaction_loader import TransactionRecordLoader


def load_cases(path: Path) -> list[dict]:
    frame = pd.read_csv(path)

    required = {
        "case_id",
        "is_fraud",
    }

    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Missing benchmark columns: {sorted(missing)}"
        )

    transaction_column = next(
        (
            column
            for column in (
                "transaction_id",
                "flagged_txn_id",
                "TransactionID",
            )
            if column in frame.columns
        ),
        None,
    )

    if transaction_column is None:
        raise ValueError(
            "Benchmark file must contain transaction_id, "
            "flagged_txn_id, or TransactionID."
        )

    cases: list[dict] = []

    for row in frame.to_dict(orient="records"):
        cases.append(
            {
                "case_id": str(row["case_id"]),
                "transaction_id": str(row[transaction_column]),
                "is_fraud": row["is_fraud"],
            }
        )

    return cases


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the trained fraud model."
    )

    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("data/raw/case_pack.csv"),
    )

    parser.add_argument(
        "--transactions",
        type=Path,
        default=Path("data/raw/transactions.csv"),
    )

    parser.add_argument(
        "--identity",
        type=Path,
        default=Path("data/raw/identity.csv"),
    )

    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models/fraud/fraud_model.joblib"),
    )

    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path(
            "models/fraud/fraud_model_metadata.json"
        ),
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.50,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/ml/fraud_benchmark.json"
        ),
    )

    args = parser.parse_args()

    cases = load_cases(args.cases)

    inference = FraudModelInference(
        model_path=args.model,
        metadata_path=args.metadata,
        threshold=args.threshold,
    )

    loader = TransactionRecordLoader(
        transactions_path=args.transactions,
        identity_path=args.identity,
    )

    benchmark = FraudBenchmark(
        inference=inference,
        transaction_loader=loader,
    )

    metrics, results = benchmark.evaluate(cases)

    benchmark.save_report(
        args.output,
        metrics,
        results,
    )

    print("\n=== Fraud Model Benchmark ===")
    print(f"Cases      : {metrics.total}")
    print(f"Correct    : {metrics.correct}")
    print(f"Accuracy   : {metrics.accuracy:.4f}")
    print(f"Precision  : {metrics.precision:.4f}")
    print(f"Recall     : {metrics.recall:.4f}")
    print(f"F1         : {metrics.f1:.4f}")
    print()
    print(f"TP: {metrics.true_positive}")
    print(f"TN: {metrics.true_negative}")
    print(f"FP: {metrics.false_positive}")
    print(f"FN: {metrics.false_negative}")
    print()
    print(f"Report: {args.output}")


if __name__ == "__main__":
    main()