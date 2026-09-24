"""
Phase 1 + Phase 3 smoke test: Verify the complete ML inference pipeline.
Runs against real HHGOA data — no mock transactions.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ml.transaction_loader import TransactionRecordLoader
from backend.ml.inference import FraudModelInference


def main() -> None:
    print("=== Phase 1 + 3: ML Pipeline Smoke Test ===\n")

    loader = TransactionRecordLoader(
        transactions_path="data/raw/transactions.csv",
        identity_path="data/raw/identity.csv",
    )

    inference = FraudModelInference(
        model_path="models/fraud_model.joblib",
        metadata_path="models/fraud_model_metadata.json",
        threshold=0.50,
    )

    # Load benchmark case IDs
    with open("data/raw/case_pack.csv", encoding="utf-8-sig") as f:
        cases = list(csv.DictReader(f))

    print(f"Benchmark cases: {len(cases)}")
    benchmark_ids = [c["flagged_txn_id"].strip() for c in cases[:5]]

    # Include required test transaction + benchmark samples
    test_ids = ["3514030"] + benchmark_ids
    print(f"Testing {len(test_ids)} transaction IDs\n")
    print(f"{'TXN_ID':<14} {'BANK_RISK':<12} {'ML_PROB':<10} {'IS_FRAUD':<10} {'MODEL_VERSION'}")
    print("-" * 72)

    successes = 0
    errors = 0

    for tid in test_ids:
        try:
            tx = loader.get_transaction(tid)
            pred = inference.predict(tx)
            bank_risk = tx.get("risk_score", "N/A")
            if bank_risk is None:
                bank_risk = "N/A"
            print(
                f"{pred.transaction_id:<14} "
                f"{str(bank_risk):<12} "
                f"{pred.probability:.4f}     "
                f"{'YES' if pred.is_fraud else 'NO':<10} "
                f"{pred.model_version or 'N/A'}"
            )
            successes += 1
        except KeyError:
            print(f"{tid:<14} NOT FOUND IN DATASET")
            errors += 1
        except Exception as e:
            print(f"{tid:<14} ERROR: {type(e).__name__}: {e}")
            errors += 1

    print("-" * 72)
    print(f"\nSuccessful: {successes}  |  Errors/Not Found: {errors}")
    print("\n=== Smoke test complete ===")


if __name__ == "__main__":
    main()
