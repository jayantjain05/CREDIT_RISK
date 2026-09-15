# CreditLens

An interactive commercial-credit review workspace for underwriting teams. It presents a borrower overview, financial trajectory, covenant monitoring, stress testing, and a concise credit memo.

## Run locally

Open `index.html` in a browser, or serve the folder:

```bash
npm start
```

## Product behavior

- Adjust the revenue-decline slider to recalculate DSCR, credit score, probability of default, risk grade, and guidance.
- Open the credit memo from the header, recommendation card, or analyst-view panel.
- Print the memo from the modal dialog.

## Deployment

This is a static application. Deploy the repository root to any static host (Netlify, Vercel, GitHub Pages, S3/CloudFront, etc.). No build command or server-side environment variables are required.

## Credit-risk ML pipeline

The project includes a reproducible binary-classification pipeline using Kaggle's CC0 `programmer3/credit-risk-dataset`. It downloads the data, removes identifier fields, trains a class-balanced calibrated logistic-regression model, and saves holdout metrics plus a model bundle.

```bash
python3 -m pip install --user -r requirements.txt
python3 ml/train.py --download
```

Score a new, schema-compatible CSV:

```bash
python3 ml/score.py path/to/borrowers.csv --threshold 0.50
```

See [MODEL_CARD.md](MODEL_CARD.md) for validation, model-risk, and responsible-use requirements. The supplied dataset is synthetic; do not use the resulting model for actual lending decisions.

## Production integration notes

The UI uses illustrative borrower data. In a production deployment, source financials and covenant data from an authenticated API, calculate scores on the server, retain versioned decision/audit records, and enforce role-based access control before presenting any customer information.
