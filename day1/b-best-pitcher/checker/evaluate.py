#!/usr/bin/env python3
"""FAIO 2025 Day 1 Task 2 "Who is the best pitcher?" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric: accuracy (exact match on the `ANSWER` value), on a 0-100 scale. This faithfully reproduces
the original Kaggle metric (sklearn.metrics.accuracy_score over pandas-read columns).

IMPORTANT - dtype fidelity: the gold `ANSWER` column is mixed (names, team codes, numbers, dates),
so pandas reads it as strings. Kaggle compares the submission's `ANSWER` column *as pandas infers
its dtype*. If a submission's `ANSWER` column is purely numeric, pandas reads it as numbers, and a
numeric value never equals the string gold (e.g. int 0 != "0") - so such submissions score ~0 on
Kaggle even when the string forms would match. We preserve that behaviour by reading both files with
pandas.read_csv (default dtype inference), exactly like the original checker.

Submission: columns `ID` and `ANSWER` (as in sample_submission.csv). Ground truth: columns `ID`,
`ANSWER`, `Usage` (Public/Private). Predictions are matched to the truth by `ID` (order-independent);
the public/private split is driven by the ground truth's `Usage` column.

Error handling follows Kaggle's convention: anything the participant can fix is raised as a
ParticipantVisibleError and surfaced in the result message (verdict "PE"); anything else is an
organizer/internal problem (verdict "INTERNAL_ERROR") and is not blamed on the submission.

Prints exactly one JSON line: {"public_score", "private_score", "verdict", "message"}.
Only the public score is shown in the message; the private score stays hidden there.
"""
import json
import sys

import pandas as pd

ID, ANSWER, USAGE = "ID", "ANSWER", "Usage"


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def evaluate(sub_path, truth_path):
    try:
        truth = pd.read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    for col in (ID, ANSWER, USAGE):
        if col not in truth.columns:
            raise RuntimeError(f"ground truth must have '{col}' column")

    # Read the submission with default dtype inference (like the original Kaggle checker), so a
    # purely-numeric ANSWER column stays numeric and will not match the string gold.
    try:
        sub = pd.read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    for col in (ID, ANSWER):
        if col not in sub.columns:
            raise ParticipantVisibleError(
                f"Your submission must have '{ID}' and '{ANSWER}' columns; found {list(sub.columns)}.")

    if sub[ID].duplicated().any():
        dup = sub.loc[sub[ID].duplicated(), ID].iloc[0]
        raise ParticipantVisibleError(f"Duplicate ID {dup!r} in your submission.")
    if len(sub) != len(truth):
        raise ParticipantVisibleError(
            f"Your submission has {len(sub)} rows, but the test set has {len(truth)}.")

    merged = truth.merge(sub[[ID, ANSWER]], on=ID, how="left", suffixes=("_true", "_pred"))
    if merged[f"{ANSWER}_pred"].isna().any() and not sub[ANSWER].isna().any():
        missing = merged.loc[merged[f"{ANSWER}_pred"].isna(), ID].iloc[0]
        raise ParticipantVisibleError(f"Missing prediction for ID {missing!r}.")

    # Elementwise equality, dtype-sensitive (int 0 != "0"), as sklearn.accuracy_score would do.
    correct = merged[f"{ANSWER}_true"].eq(merged[f"{ANSWER}_pred"])

    def acc(usage):
        mask = merged[USAGE] == usage
        n = int(mask.sum())
        return (float(correct[mask].sum()) / n * 100) if n else 0.0, n, int(correct[mask].sum())

    public, pub_n, pub_c = acc("Public")
    private, _, _ = acc("Private")
    emit("OK", public, private, f"Score: {round(public, 4)} (public accuracy {pub_c}/{pub_n})")


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
