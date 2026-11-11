#!/usr/bin/env python3
"""FAIO 2025 Day 2 Task 1 "Hear Me: Personalized Music Recommender" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric (reproduces the original Kaggle scorer, original/evaluate.py): for each of the 1500 users we
take their 50 recommended tracks; for every recommended track that the user actually listened to we
add that track's listening `share` (0..1, from the ground truth), 0 if it was not listened to. The
score is the mean over users of (sum of shares over their 50 tracks) / 50, i.e. the mean listening
share per recommended slot. Reported on a 0-100 scale.

Submission: columns `user_id`, `item_id`, `rank` (an optional leading `id` row-index column is
ignored) - exactly 1500 users, 50 rows per user, ranks 1..50.
Ground truth: columns `user_id`, `item_id`, `share` (the listened tracks and their shares).

Yandex/Kaggle-style for this task: there is NO public/private split - the leaderboard reported the
same number for public and private (the validation gold is entirely "Public"), so the score is
computed over all rows and public_score == private_score.

Error handling follows Kaggle's convention: anything the participant can fix is a
ParticipantVisibleError (verdict "PE"); anything else is an organizer/internal problem
("INTERNAL_ERROR"). Prints exactly one JSON line: {"public_score","private_score","verdict","message"}.
"""
import json
import sys

import pandas as pd

N_USERS = 1500
N_RECS = 50
ROW_ID_COLS = ("id", "Id", "ID", "row_id", "index", "Unnamed: 0")


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def _drop_row_id(df):
    for col in ROW_ID_COLS:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df


def evaluate(sub_path, truth_path):
    # --- ground truth (organizer-side; a problem here is INTERNAL_ERROR, not the participant's) ---
    try:
        solution = pd.read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    solution = _drop_row_id(solution)
    if not {"user_id", "item_id", "share"}.issubset(solution.columns):
        raise RuntimeError("ground truth must have columns user_id, item_id, share")

    # --- submission (everything the participant could get wrong raises ParticipantVisibleError) ---
    try:
        submission = pd.read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    submission = _drop_row_id(submission)

    if set(submission.columns) != {"user_id", "item_id", "rank"}:
        raise ParticipantVisibleError(
            f"Your submission must have the columns user_id, item_id, rank; found {list(submission.columns)}.")

    num_users = submission["user_id"].nunique()
    if num_users != N_USERS:
        raise ParticipantVisibleError(
            f"Your submission must cover exactly {N_USERS} users, found {num_users}.")

    user_counts = submission.groupby("user_id").size()
    if not (user_counts == N_RECS).all():
        bad = int((user_counts != N_RECS).sum())
        raise ParticipantVisibleError(
            f"Each user must have exactly {N_RECS} recommendations ({bad} user(s) do not).")

    want_ranks = set(range(1, N_RECS + 1))
    for user_id, user_df in submission.groupby("user_id"):
        if set(user_df["rank"]) != want_ranks:
            raise ParticipantVisibleError(f"Invalid rank values for user {user_id} (must be 1..{N_RECS}).")

    # --- score: sum listened share per user over their 50 recs, mean over users, / 50 ---
    final = pd.merge(submission, solution[["user_id", "item_id", "share"]],
                     on=["user_id", "item_id"], how="left")
    final["share"] = final["share"].fillna(0)
    user_scores = final.groupby("user_id")["share"].sum()
    metric = float(user_scores.mean()) / N_RECS   # 0..1

    if not (metric >= 0):   # catches NaN too
        raise RuntimeError("metric computation returned an invalid value")

    score = round(metric * 100.0, 4)              # 0..100
    # No public/private split for this task: report the same score as both.
    emit("OK", score, score, f"Score: {score:.4f} (mean listening share per recommended track x100)")


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
