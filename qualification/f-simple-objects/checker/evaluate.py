#!/usr/bin/env python3
"""FAIO Qualification 2025 - Problem 6 "Simple Objects" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric (identical to the original Yandex checker): per-row relative-error accuracy
    acc_i = 1 - min(|pred_i - gt_i| / gt_i, 1)
averaged over rows, then thresholded at 0.55 and remapped to 0-100 points:
    score = 0 if mean < 0.55 else round(100 * (mean - 0.55) / (1 - 0.55)).
Submission columns: `id`, `counts`. Ground truth columns: `id`, `counts`; counts parsed as int(float(.)).

Rows are matched BY POSITION (row order), exactly like the original checker: the submission must
have the same number of rows as the ground truth, in the same order.

ParticipantVisibleError -> verdict "PE"; other errors -> "INTERNAL_ERROR".
Prints one JSON line: {"public_score","private_score","verdict","message"}.
"""
import csv
import json
import sys

COUNTS, THRESHOLD = "counts", 0.55


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
    if not truth or COUNTS not in truth[0]:
        raise RuntimeError(f"ground truth must have a '{COUNTS}' column")

    try:
        sub = read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    if not sub or COUNTS not in sub[0]:
        cols = list(sub[0].keys()) if sub else []
        raise ParticipantVisibleError(f"Your submission must have a '{COUNTS}' column; found {cols}.")
    if len(sub) != len(truth):
        raise ParticipantVisibleError(
            f"Your submission has {len(sub)} rows, but the test set has {len(truth)}.")

    try:
        gts = [int(float(row[COUNTS])) for row in truth]
        preds = [int(float(row[COUNTS])) for row in sub]
    except Exception:
        raise ParticipantVisibleError("The 'counts' column must contain integer values.")

    acc = 0.0
    for gt, pr in zip(gts, preds):
        acc += 1 - min(abs(pr - gt) / gt, 1)
    mean = acc / len(gts) if gts else 0.0
    score = 0 if mean < THRESHOLD else round(100 * (mean - THRESHOLD) / (1 - THRESHOLD))
    emit("OK", score, score, f"Score: {score} points (mean rel-acc {mean:.4f})")


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
