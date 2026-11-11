#!/usr/bin/env python3
"""FAIO 2025 Day 1 Task 3 "Missing Fundamental Puzzle" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric: accuracy (share of clips whose predicted `Pitch_ID` is correct), on a 0-100 scale. This
mirrors the original Kaggle metric (sklearn.metrics.accuracy_score) on the `Pitch_ID` column.

Submission: columns `Path` and `Pitch_ID` (as in sample_submission.csv). Ground truth: columns
`Path`, `Pitch_ID`, `Usage` (Public/Private). Predictions are matched to the truth by `Path`
(order-independent); the public/private split is driven by the ground truth's `Usage` column.

Error handling follows Kaggle's convention: anything the participant can fix is raised as a
ParticipantVisibleError and surfaced in the result message (verdict "PE"); anything else is an
organizer/internal problem (verdict "INTERNAL_ERROR") and is not blamed on the submission.

Prints exactly one JSON line: {"public_score", "private_score", "verdict", "message"}.
Only the public score is shown in the message; the private score stays hidden there.
"""
import csv
import json
import sys

PATH, PID, USAGE = "Path", "Pitch_ID", "Usage"


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(v):
    return (v if v is not None else "").strip()


def norm_pid(v):
    """Compare Pitch_ID as an integer when possible, else as a trimmed string."""
    s = norm(v)
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s


def evaluate(sub_path, truth_path):
    try:
        truth = read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    if not truth or PATH not in truth[0] or PID not in truth[0] or USAGE not in truth[0]:
        raise RuntimeError(f"ground truth must have '{PATH}', '{PID}', '{USAGE}' columns")

    try:
        sub = read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    if not sub or PATH not in sub[0] or PID not in sub[0]:
        cols = list(sub[0].keys()) if sub else []
        raise ParticipantVisibleError(
            f"Your submission must have '{PATH}' and '{PID}' columns; found {cols}.")

    sub_by_path = {}
    for row in sub:
        p = norm(row[PATH])
        if p in sub_by_path:
            raise ParticipantVisibleError(f"Duplicate Path {p!r} in your submission.")
        sub_by_path[p] = norm_pid(row[PID])

    if len(sub) != len(truth):
        raise ParticipantVisibleError(
            f"Your submission has {len(sub)} rows, but the test set has {len(truth)}.")

    splits = {"Public": [0, 0], "Private": [0, 0]}  # [correct, total]
    for row in truth:
        p = norm(row[PATH])
        if p not in sub_by_path:
            raise ParticipantVisibleError(f"Missing prediction for Path {p!r}.")
        usage = norm(row[USAGE])
        if usage not in splits:
            raise RuntimeError(f"unexpected Usage value {usage!r} in ground truth")
        splits[usage][1] += 1
        if sub_by_path[p] == norm_pid(row[PID]):
            splits[usage][0] += 1

    def acc(split):
        c, t = splits[split]
        return (c / t * 100) if t else 0.0

    public, private = acc("Public"), acc("Private")
    emit("OK", public, private,
         f"Score: {round(public, 4)} (public accuracy "
         f"{splits['Public'][0]}/{splits['Public'][1]})")


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
