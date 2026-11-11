#!/usr/bin/env python3
"""FAIO 2025 Day 2 Task 2 "Lost in the Museum" - platform checker.

    python evaluate.py <submission.csv> <ground_truth.csv>

Metric: Hit@3 image retrieval, on a 0-100 scale. This reproduces the original Kaggle metric.

The submission provides an embedding for every one of the 20,000 images:
    columns `image_name`, `feature_0`, `feature_1`, ... `feature_{D-1}`.
Each embedding is L2-normalized, so a dot product is the cosine similarity. For each query image we
rank all *gallery* images (every image that is not itself a query in this split) by cosine similarity
and check whether the correct answer is among the top 3. The score is the fraction of queries whose
answer is in the top 3.

Ground truth: columns `ID`, `Usage`, `query`, `answer` (Usage is Public/Private). As on Kaggle, the
public and private scores are computed independently: each split's gallery excludes only that split's
own query images.

Error handling follows Kaggle's convention: anything the participant can fix is raised as a
ParticipantVisibleError and surfaced in the result message (verdict "PE"); anything else is an
organizer/internal problem (verdict "INTERNAL_ERROR").

Prints exactly one JSON line: {"public_score", "private_score", "verdict", "message"}.
Only the public score is shown in the message; the private score stays hidden there.

Note on reproducibility: Hit@3 is sensitive to ties in cosine similarity. The original Kaggle checker
iterated its gallery in Python set order (non-deterministic), so a submission with tied similarities at
the top-3 boundary can differ by a query or two between runs. This port iterates the gallery in
submission row order (deterministic); results match the original exactly except on such borderline ties.
"""
import json
import sys

import numpy as np
import pandas as pd

IMG, TOPK, N_IMAGES = "image_name", 3, 20000


class ParticipantVisibleError(Exception):
    """A problem the participant can fix; its message is shown to them (verdict PE)."""


def emit(verdict, public=0.0, private=0.0, message=""):
    print(json.dumps({"public_score": round(float(public), 4),
                      "private_score": round(float(private), 4),
                      "verdict": verdict, "message": message}))


def hit_at_k(sol_split, emb, names, idx):
    """Hit@3 over one Usage split; gallery = all images except this split's queries."""
    qids = set(sol_split["query"].values)
    gmask = np.array([n not in qids for n in names])
    gemb = emb[gmask]
    gnames = names[gmask]
    hits = total = 0
    for q, ans in zip(sol_split["query"].values, sol_split["answer"].values):
        i = idx.get(q)
        if i is None:
            continue  # query image not in submission -> cannot be scored (counts as miss-by-omission)
        sims = gemb @ emb[i]
        top = np.argpartition(sims, -TOPK)[-TOPK:]
        top = top[np.argsort(sims[top])[::-1]]
        if ans in {gnames[j] for j in top}:
            hits += 1
        total += 1
    return (hits / total * 100) if total else 0.0, hits, total


def evaluate(sub_path, truth_path):
    try:
        truth = pd.read_csv(truth_path)
    except Exception as e:
        raise RuntimeError(f"cannot read ground truth: {e}")
    for col in ("Usage", "query", "answer"):
        if col not in truth.columns:
            raise RuntimeError(f"ground truth must have a '{col}' column")

    try:
        sub = pd.read_csv(sub_path)
    except Exception as e:
        raise ParticipantVisibleError(f"Could not read your submission as a CSV: {e}")
    if IMG not in sub.columns:
        raise ParticipantVisibleError(f"Your submission must have an '{IMG}' column.")
    feat_cols = [c for c in sub.columns if c.startswith("feature_")]
    if not feat_cols:
        raise ParticipantVisibleError("Your submission has no 'feature_*' embedding columns.")

    names = sub[IMG].to_numpy()
    if sub[IMG].duplicated().any():
        dup = sub.loc[sub[IMG].duplicated(), IMG].iloc[0]
        raise ParticipantVisibleError(f"Duplicate image_name {dup!r} in your submission.")
    if len(names) != N_IMAGES:
        raise ParticipantVisibleError(
            f"Your submission must have embeddings for all {N_IMAGES} images; found {len(names)}.")

    try:
        emb = sub[feat_cols].to_numpy(np.float32)
    except Exception:
        raise ParticipantVisibleError("The 'feature_*' columns must all be numeric.")
    if not np.isfinite(emb).all():
        raise ParticipantVisibleError("Your embedding contains NaN or infinite values.")
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    idx = {n: i for i, n in enumerate(names)}

    public, pub_h, pub_t = hit_at_k(truth[truth.Usage == "Public"], emb, names, idx)
    private, _, _ = hit_at_k(truth[truth.Usage == "Private"], emb, names, idx)
    emit("OK", public, private,
         f"Score: {round(public, 4)} (public Hit@3 {pub_h}/{pub_t})")


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
