from __future__ import annotations

import argparse
from pathlib import Path

from backend.ml.benchmark import FraudModelBenchmark
from backend.ml.inference import FraudModelInference
from backend.ml.transaction_loader import TransactionRecordLoader


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the fraud model against the 20 HHGO benchmark cases."
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
        default=Path("models/fraud_model.joblib"),
    )

    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("models/fraud_model_metadata.json"),
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.50,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/ml/fraud_benchmark.json"),
    )

    args = parser.parse_args()

    inference = FraudModelInference(
        model_path=args.model,
        metadata_path=args.metadata,
        threshold=args.threshold,
    )

    loader = TransactionRecordLoader(
        transactions_path=args.transactions,
        identity_path=args.identity,
    )

    benchmark = FraudModelBenchmark(
        inference=inference,
        transaction_loader=loader,
    )

    cases = benchmark.load_cases(args.cases)
    predictions = benchmark.evaluate(cases)

    benchmark.save_report(
        args.output,
        predictions,
    )

    print()
    print("=== HHGO Fraud Model Benchmark ===")
    print(f"Cases: {len(predictions)}")
    print()

    for prediction in predictions:
        bank_score = (
            f"{prediction.bank_risk_score:.2f}"
            if prediction.bank_risk_score is not None
            else "N/A"
        )

        print(
            f"{prediction.case_id}: "
            f"txn={prediction.transaction_id} "
            f"bank_risk={bank_score} "
            f"ml_probability={prediction.ml_probability:.4f} "
            f"prediction={prediction.ml_prediction}"
        )

    print()
    print(f"Report: {args.output}")
    print()
    print(
        "NOTE: The official benchmark answer key is hidden. "
        "No accuracy/precision/recall is calculated here."
    )


if __name__ == "__main__":
    main()