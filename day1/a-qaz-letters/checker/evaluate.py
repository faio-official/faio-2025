#!/usr/bin/env python3
"""FAIO 2025 Day 1 Task 1 "Qaz-letters" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric: accuracy (share of letters classified correctly), on a 0-100 scale.

Submission: columns `ID` and `label` (one predicted integer class per test row, as in
sample_submission.csv). Ground truth: columns `ID`, `target`, `usage` (Public/Private).
Predictions are matched to the truth by `ID` (order-independent), so the public/private split
is driven by the ground truth's `usage` column.

Error handling follows Kaggle's convention: anything the participant can fix is raised as a
ParticipantVisibleError and surfaced in the result message (verdict "PE"); anything else is an
organizer/internal problem (verdict "INTERNAL_ERROR") and is not blamed on the submission.

Prints exactly one JSON line: {"public_score", "private_score", "verdict", "message"}.
Only the public score is shown in the message; the private score stays hidden there.
"""
import json
import sys

import pandas as pd

ID = "ID"
TRUTH_COL = "target"
USAGE_COL = "usage"


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def evaluate(sub_path, truth_path):
    # --- ground truth (organizer-side; a problem here is INTERNAL_ERROR, not the participant's) ---
    try:
        truth = pd.read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    for col in (ID, TRUTH_COL):
        if col not in truth.columns:
            raise RuntimeError(f"ground truth is missing the '{col}' column")

    # --- submission (everything the participant could get wrong raises ParticipantVisibleError) ---
    try:
        sub = pd.read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    pred_col = next((c for c in ("label", "prediction") if c in sub.columns), None)
    if ID not in sub.columns or pred_col is None:
        raise ParticipantVisibleError(
            f"Your submission must have the columns '{ID}' and 'label'; found {list(sub.columns)}.")
    if sub[ID].duplicated().any():
        dup = sub.loc[sub[ID].duplicated(), ID].iloc[0]
        raise ParticipantVisibleError(f"Your submission has duplicate ID values (e.g. {dup}).")

    merged = truth.merge(sub[[ID, pred_col]], on=ID, how="left")
    missing = int(merged[pred_col].isna().sum())
    if missing:
        raise ParticipantVisibleError(
            f"Your submission is missing predictions for {missing} of {len(truth)} test IDs.")
    extra = len(sub) - len(sub[sub[ID].isin(set(truth[ID]))])
    if extra:
        raise ParticipantVisibleError(
            f"Your submission has {extra} row(s) whose ID is not in the test set.")
    try:
        y_pred = pd.to_numeric(merged[pred_col]).astype("int64")
    except Exception:
        raise ParticipantVisibleError("The 'label' column must contain integer class values.")
    y_true = merged[TRUTH_COL].astype("int64")

    def acc(mask):
        yt, yp = y_true[mask].to_numpy(), y_pred[mask].to_numpy()
        return round(float((yt == yp).mean()) * 100.0, 4)  # accuracy = mean exact match

    if USAGE_COL in merged.columns:
        usage = merged[USAGE_COL].astype(str).str.lower()
        pub, prv = usage == "public", usage == "private"
        public_score = acc(pub) if pub.any() else 0.0
        private_score = acc(prv) if prv.any() else public_score
    else:
        public_score = private_score = acc(y_true.index == y_true.index)

    emit("OK", public_score, private_score, f"Public accuracy: {public_score:.2f}%")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        emit("INTERNAL_ERROR", message="usage: evaluate.py <submission.csv> <ground_truth.csv>")
        return 3
    try:
        evaluate(args[0], args[1])
        return 0
    except ParticipantVisibleError as e:
        emit("PE", message=str(e))
        return 2
    except Exception as e:
        emit("INTERNAL_ERROR", message=f"{type(e).__name__}: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
