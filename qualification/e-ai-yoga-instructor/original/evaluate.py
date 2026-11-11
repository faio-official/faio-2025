import sys
import csv

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


def extract_predicts(rows: list[dict[str, str]]) -> list[str]:
    return [row["label"] for row in rows]


def accuracy_score(y_true: list[str], y_pred: list[str]) -> float:
    """
    Pure Python accuracy score for binary classification
    """
    if len(y_true) == 0:
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if int(float(yt)) == int(float(yp)))
    return correct / len(y_true)


def score(y_true: list[str], y_pred: list[str]) -> float:
    """
    Final score is accuracy * 100 (0–100 scale).
    """
    acc = accuracy_score(y_true, y_pred)
    return round(acc * 100)


def main():
    student_ans = read_csv(sys.argv[2])
    ground_truth = read_csv(sys.argv[3])

    if len(student_ans) != len(ground_truth):
        print("PE")
        sys.exit(2)

    final_verdict = score(
        extract_predicts(ground_truth),
        extract_predicts(student_ans),
    )
    print(final_verdict)
    sys.exit(0)


if __name__ == '__main__':
    main()