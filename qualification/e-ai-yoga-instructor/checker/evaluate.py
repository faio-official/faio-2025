#!/usr/bin/env python3
"""FAIO Qualification 2025 - Problem 5 "Can You Become AI Yoga Instructor?" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric (identical to the original Yandex checker): classification accuracy, as round(accuracy*100)
on a 0-100 scale. Labels are compared as int(float(label)). Submission columns: `id`, `label`.
Ground truth columns: `id`, `label`.

Rows are matched BY POSITION (row order), exactly like the original checker: the submission must
have the same number of rows as the ground truth, in the same order.

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
        raise ParticipantVisibleError(f"Your submission must have a '{LABEL}' column; found {cols}.")
    if len(sub) != len(truth):
        raise ParticipantVisibleError(
            f"Your submission has {len(sub)} rows, but the test set has {len(truth)}.")

    try:
        y_true = [int(float(row[LABEL])) for row in truth]
        y_pred = [int(float(row[LABEL])) for row in sub]
    except Exception:
        raise ParticipantVisibleError("The 'label' column must contain numeric class values (0 or 1).")

    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    score = round(correct / len(y_true) * 100) if y_true else 0.0
    emit("OK", score, score, f"Score: {score} points (accuracy {correct}/{len(y_true)})")


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
