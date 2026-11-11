import sys
import json
import pandas as pd
from sklearn.metrics import accuracy_score

def evaluate(sub_path: str, truth_path: str) -> None:
    sub = pd.read_csv(sub_path)
    truth = pd.read_csv(truth_path)

    # Calculate metric score
    # Supports optional Public vs Private leaderboard split via 'usage' column
    if "usage" in truth.columns:
        pub_mask = truth["usage"].str.lower() == "public"
        priv_mask = truth["usage"].str.lower() == "private"

        pub_score = accuracy_score(
            truth.loc[pub_mask, "target"],
            sub.loc[pub_mask, "prediction"],
        ) * 100.0

        if priv_mask.any():
            priv_score = accuracy_score(
                truth.loc[priv_mask, "target"],
                sub.loc[priv_mask, "prediction"],
            ) * 100.0
        else:
            priv_score = pub_score

        # Output JSON format: {"public_score": ..., "private_score": ..., "verdict": "OK", "message": "..."}
        print(json.dumps({
            "public_score": round(float(pub_score), 4),
            "private_score": round(float(priv_score), 4),
            "verdict": "OK",
            "message": f"Public: {pub_score:.2f}%, Private: {priv_score:.2f}%"
        }))
    else:
        score = accuracy_score(truth["target"], sub["prediction"]) * 100.0
        # Output JSON format: {"public_score": ..., "private_score": ..., "verdict": "OK", "message": "..."}
        print(json.dumps({
            "public_score": round(float(score), 4),
            "private_score": round(float(score), 4),
            "verdict": "OK",
            "message": f"Accuracy: {score:.2f}%"
        }))

if __name__ == "__main__":
    # sys.argv: [1]=submission.csv, [2]=ground_truth.csv
    evaluate(sys.argv[1], sys.argv[2])