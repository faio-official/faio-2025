#!/usr/bin/env python3
"""FAIO 2025 Qualification P2 "Probability 101" — jury checker: evaluate.py submission.csv ground_truth.csv.

Single-answer CSV task. The submission is a CSV with a header `answer` and exactly one data row
holding the participant's probability. The ground truth has the same schema and holds the jury answer.
The answer is correct if it is within EPS of the jury value; a correct answer scores POINTS, otherwise 0.
Yandex-style scoring: there is NO public/private split — public_score == private_score.
"""
import csv
import io
import json
import sys
from pathlib import Path

MAX_BYTES = 1 * 1024 * 1024
POINTS = 10.0
EPS = 1e-4
COLUMN = "answer"

csv.field_size_limit(MAX_BYTES)


def read_csv(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"CSV exceeds {MAX_BYTES} bytes.")
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    rows = [row for row in reader if row]  # blank lines are skipped
    if len(rows) < 2:
        raise ValueError("CSV must contain a header row and exactly one answer row.")
    header = [name.strip() for name in rows[0]]
    if len(set(header)) != len(header):
        raise ValueError("CSV header has duplicate column names.")
    return header, rows[1:]


def read_answer(path):
    """The single float in the `answer` column, requiring exactly one data row."""
    header, rows = read_csv(path)
    if COLUMN not in header:
        raise ValueError(f"The header must contain the column '{COLUMN}'.")
    idx = header.index(COLUMN)
    if len(rows) != 1:
        raise ValueError("Submit exactly one answer row.")
    row = rows[0]
    if len(row) != len(header):
        raise ValueError("The answer row has the wrong number of fields.")
    cell = row[idx].strip()
    try:
        value = float(cell)
    except ValueError:
        raise ValueError(f"The answer {cell[:32]!r} is not a number.")
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError("The answer must be a finite number.")
    return value


def emit(verdict, public=0.0, private=0.0, message="Checker configuration error."):
    print(json.dumps({"public_score": round(public, 4),
                      "private_score": round(private, 4),
                      "verdict": verdict, "message": message}, allow_nan=False))


def evaluate(sub_path: str, gold_path: str) -> None:
    try:
        gold = read_answer(gold_path)
    except (OSError, ValueError, UnicodeError, csv.Error) as error:
        emit("PE", message=str(error))
        raise SystemExit(3) from None
    try:
        answer = read_answer(sub_path)
    except (OSError, ValueError, UnicodeError, csv.Error) as error:
        emit("PE", message=str(error))
        raise SystemExit(2) from None

    # Yandex-style: NO public/private split — the full score is always visible.
    correct = abs(answer - gold) <= EPS
    score = POINTS if correct else 0.0
    verdict_text = "Correct" if correct else "Incorrect"
    emit("OK", score, score, f"{verdict_text}: {score:.0f}/{POINTS:.0f} points.")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        emit("INTERNAL_ERROR", message="Usage: evaluate.py submission.csv ground_truth.csv")
        return 3
    evaluate(args[0], args[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
