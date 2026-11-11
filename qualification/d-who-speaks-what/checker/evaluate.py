#!/usr/bin/env python3
"""FAIO Qualification 2025 - Problem 4 "Who Speaks What?" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric (identical to the original Yandex checker): macro-averaged F1 over the language
labels, then mapped to 0-100 points: F1 < 0.6 -> 0, otherwise (F1-0.6)/0.4*100 (rounded).
Submission columns: `id`, `label`. Ground truth columns: `id`, `label`.

Rows are matched BY POSITION (row order), exactly like the original checker: the submission
must have the same number of rows as the ground truth, in the same order. (An order-independent
id-merge variant would be more robust but would rescore row-reordered submissions.)

ParticipantVisibleError -> verdict "PE"; other errors -> "INTERNAL_ERROR".
Prints one JSON line: {"public_score","private_score","verdict","message"}.
"""
import csv
import json
import sys

ID, LABEL = "id", "label"


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def macro_f1(y_true, y_pred):
    labels = sorted(set(y_true) | set(y_pred))
    f1s = []
    for label in labels:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp == label)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yp == label and yt != label)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == label and yp != label)
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * p * r / (p + r) if (p + r) else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def evaluate(sub_path, truth_path):
    try:
        truth = read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    if not truth or LABEL not in truth[0]:
        raise RuntimeError(f"ground truth must have a '{LABEL}' column")

    try:
        sub = read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    if not sub or LABEL not in sub[0]:
        cols = list(sub[0].keys()) if sub else []
        raise ParticipantVisibleError(
            f"Your submission must have a '{LABEL}' column; found {cols}.")
    if len(sub) != len(truth):
        raise ParticipantVisibleError(
            f"Your submission has {len(sub)} rows, but the test set has {len(truth)}.")

    y_true = [row[LABEL] for row in truth]
    y_pred = [row[LABEL] for row in sub]
    f1 = macro_f1(y_true, y_pred)
    score = 0.0 if f1 < 0.6 else round((f1 - 0.6) / 0.4 * 100)
    emit("OK", score, score, f"Score: {score} points (macro-F1 {f1:.4f})")


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
