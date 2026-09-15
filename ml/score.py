"""Score a CSV of borrower records with a trained CreditLens model."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="CSV containing borrower records")
    parser.add_argument("--model", type=Path, default=Path("artifacts/credit_risk_model.joblib"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/scored_borrowers.csv"))
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    if not 0 < args.threshold < 1:
        raise ValueError("--threshold must be between 0 and 1")
    bundle = joblib.load(args.model)
    frame = pd.read_csv(args.input)
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    missing = sorted(set(bundle["features"]) - set(frame.columns))
    if missing:
        raise ValueError(f"Input is missing required features: {missing}")
    probability = bundle["pipeline"].predict_proba(frame[bundle["features"]])[:, 1]
    result = frame.copy()
    result["probability_of_default"] = probability.round(6)
    result["risk_decision"] = (probability >= args.threshold).astype(int)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} scored records to {args.output}")


if __name__ == "__main__":
    main()

