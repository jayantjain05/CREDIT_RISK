"""Reproducible training pipeline for the CreditLens risk model.

The default source is Kaggle's programmer3/credit-risk-dataset (CC0).  The
dataset is synthetic and is suitable for demonstration only, not live lending
decisions.  The pipeline deliberately excludes IDs and returns calibrated PDs.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = "programmer3/credit-risk-dataset"
TARGET_CANDIDATES = ("credit_risk", "loan_default", "default", "target", "label")


def download_dataset(destination: Path, dataset: str = DEFAULT_DATASET) -> Path:
    """Download a Kaggle dataset into the project data directory."""
    import kagglehub

    destination.mkdir(parents=True, exist_ok=True)
    cache_path = Path(kagglehub.dataset_download(dataset))
    for source in cache_path.rglob("*"):
        if source.is_file() and source.suffix.lower() in {".csv", ".xlsx", ".xls"}:
            target = destination / source.name
            shutil.copy2(source, target)
    return destination


def find_data_file(data_dir: Path) -> Path:
    candidates = sorted([*data_dir.glob("*.csv"), *data_dir.glob("*.xlsx"), *data_dir.glob("*.xls")])
    if not candidates:
        raise FileNotFoundError(f"No CSV/XLSX data file found in {data_dir}. Run with --download first.")
    return candidates[0]


def load_data(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    if frame.empty:
        raise ValueError("The selected dataset is empty.")
    frame.columns = [str(name).strip().lower() for name in frame.columns]
    return frame


def locate_target(frame: pd.DataFrame, requested: str | None) -> str:
    if requested:
        requested = requested.lower()
        if requested in frame.columns:
            return requested
        raise ValueError(f"Target '{requested}' is not in the dataset columns: {list(frame.columns)}")
    for candidate in TARGET_CANDIDATES:
        if candidate in frame.columns:
            return candidate
    raise ValueError("No recognized binary target column. Use --target to specify one.")


def normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        values = sorted(series.dropna().unique())
        if len(values) != 2:
            raise ValueError("The target must have exactly two non-null classes.")
        target = series.map({values[0]: 0, values[1]: 1})
    else:
        normalized = series.astype(str).str.strip().str.lower()
        if normalized.nunique() != 2:
            raise ValueError("The target must have exactly two non-null classes.")
        positive = {"1", "yes", "y", "true", "default", "high", "high risk", "risky", "bad"}
        target = normalized.isin(positive)
    return target.astype("int8")


def build_pipeline(numeric: list[str], categorical: list[str]) -> Pipeline:
    numeric_pipe = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ], remainder="drop")
    base = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=5)
    return Pipeline([("preprocess", preprocessor), ("model", calibrated)])


def train(data_path: Path, target_name: str | None, artifact_dir: Path) -> dict:
    frame = load_data(data_path)
    target = locate_target(frame, target_name)
    y = normalize_target(frame[target])
    # Identifiers and target-derived columns must not be model features.
    excluded = [target, *[column for column in frame.columns if column == "id" or column.endswith("_id")]]
    features = frame.drop(columns=excluded)
    if features.shape[1] == 0:
        raise ValueError("No usable feature columns remain after excluding IDs and target.")
    numeric = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical = [column for column in features.columns if column not in numeric]
    x_train, x_test, y_train, y_test = train_test_split(
        features, y, test_size=0.2, random_state=42, stratify=y
    )
    pipeline = build_pipeline(numeric, categorical)
    pipeline.fit(x_train, y_train)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "average_precision": round(float(average_precision_score(y_test, probabilities)), 4),
        "brier_score": round(float(brier_score_loss(y_test, probabilities)), 4),
        "default_rate": round(float(y.mean()), 4),
        "training_rows": int(len(x_train)),
        "holdout_rows": int(len(x_test)),
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    bundle = {"pipeline": pipeline, "features": list(features.columns), "target": target, "metrics": metrics}
    joblib.dump(bundle, artifact_dir / "credit_risk_model.joblib")
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the CreditLens credit-risk model.")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data/raw")
    parser.add_argument("--target", help="Binary target column (auto-detected if omitted).")
    parser.add_argument("--artifacts", type=Path, default=PROJECT_ROOT / "artifacts")
    parser.add_argument("--download", action="store_true", help="Download the default Kaggle dataset first.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Kaggle dataset slug for --download.")
    args = parser.parse_args()
    if args.download:
        download_dataset(args.data, args.dataset)
    metrics = train(find_data_file(args.data), args.target, args.artifacts)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
