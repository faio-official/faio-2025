import sys
import csv
from collections import Counter

def read_csv(filename) -> list[dict[str, str]]:
    try:
        rows = []
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    except:
        print("PE")
        sys.exit(2)


def extract_predicts(rows: list[dict[str, str]]) -> list[int]:
    return [row["label"] for row in rows]



def precision_recall_f1(y_true: list[str], y_pred: list[str], labels: list[str]) -> dict:
    """
    Compute precision, recall, f1 for each label
    """
    results = {}
    for label in labels:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp == label)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yp == label and yt != label)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == label and yp != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        results[label] = (precision, recall, f1)
    return results


def macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    labels = sorted(set(y_true) | set(y_pred))
    metrics = precision_recall_f1(y_true, y_pred, labels)
    f1s = [f1 for _, _, f1 in metrics.values()]
    return sum(f1s) / len(f1s) if f1s else 0.0


def score(y_true: list[str], y_pred: list[str]) -> float:
    f1 = macro_f1(y_true, y_pred)

    # map F1 (0.6 → 0, 1.0 → 100)
    if f1 < 0.6:
        return 0.0
    else:
        mapped = (f1 - 0.6) / (1.0 - 0.6) * 100
        return round(mapped)



def main():
    student_ans = read_csv(sys.argv[2])
    ground_truth = read_csv(sys.argv[3])

    if len(student_ans)!=len(ground_truth):
        print("PE")
        sys.exit(2)
        
    final_verdict = score(extract_predicts(ground_truth), extract_predicts(student_ans), )
    print(final_verdict)
    sys.exit(0)


if __name__ == '__main__':
    main()
