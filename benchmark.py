#!/usr/bin/env python3
"""Train and measure a LightGBM credit-card fraud classifier."""
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

DATA = Path.home() / "ml-benchmark" / "creditcard.csv"
OUT = Path("benchmark_result.json")

start = time.perf_counter()
df = pd.read_csv(DATA)
load_seconds = time.perf_counter() - start
X = df.drop(columns="Class")
y = df["Class"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
model = lgb.LGBMClassifier(
    objective="binary", n_estimators=500, learning_rate=0.05,
    num_leaves=31, class_weight="balanced", random_state=42, n_jobs=-1,
    verbosity=-1,
)
start = time.perf_counter()
model.fit(X_train, y_train)
training_seconds = time.perf_counter() - start

start = time.perf_counter()
probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)
one_row_start = time.perf_counter()
model.predict_proba(X_test.iloc[[0]])
latency_ms = (time.perf_counter() - one_row_start) * 1000
batch = X_test.iloc[: min(1000, len(X_test))]
batch_start = time.perf_counter()
model.predict_proba(batch)
batch_seconds = time.perf_counter() - batch_start
inference_seconds = time.perf_counter() - start

result = {
    "dataset": str(DATA), "rows": int(len(df)), "features": int(X.shape[1]),
    "load_data_seconds": round(load_seconds, 3),
    "training_seconds": round(training_seconds, 3),
    "best_iteration": int(getattr(model, "best_iteration_", 0) or model.n_estimators),
    "metrics": {
        "auc_roc": float(roc_auc_score(y_test, probabilities)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
    },
    "inference_latency_one_row_ms": round(latency_ms, 3),
    "inference_throughput_1000_rows_per_second": round(len(batch) / batch_seconds, 2),
    "inference_evaluation_seconds": round(inference_seconds, 3),
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
print(f"Saved {OUT.resolve()}")
