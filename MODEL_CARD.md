# CreditLens credit-risk model

## Purpose

Estimate probability of a borrower falling into the dataset's high-credit-risk class. The model supports analyst review; it must not make an automated approval, pricing, or adverse-action decision.

## Training data

Default source: Kaggle `programmer3/credit-risk-dataset`, described as a 5,000-row synthetic, CC0 credit-risk dataset. Data and artifacts are deliberately excluded from Git.

## Method

Median/mode imputation, standard scaling for numerics, one-hot encoding for categoricals, class-balanced logistic regression, and five-fold sigmoid calibration. Metrics include holdout ROC-AUC, average precision, Brier score, and default rate.

## Controls required before production use

- Replace the demonstration data with lawfully sourced, representative portfolio performance data.
- Complete feature, leakage, drift, calibration, discrimination, and stability testing.
- Perform fairness testing on protected-class proxies and obtain legal/compliance approval.
- Establish human review, adverse-action reason codes, model monitoring, retraining, rollback, access control, and audit logging.
