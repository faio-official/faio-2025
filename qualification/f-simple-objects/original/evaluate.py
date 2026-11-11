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

def to_int_safe(s: str) -> int:
    try:
        return int(float(s))
    except ValueError:
        print("PE")
        sys.exit(2)

def extract_predicts(rows: list[dict[str, str]]) -> list[int]:
    try:
        return [to_int_safe(row["counts"]) for row in rows]
    except ValueError:
        print("PE")
        sys.exit(2)


def custom_acc(ground_truth: int, prediction: int) -> float:
    error = abs(prediction - ground_truth) / ground_truth
    return 1 - min(error, 1)

def score(ground_truths: list[int], predictions: list[int]) -> int:
    accuracy = 0
    for ground_truth, prediction in zip(ground_truths, predictions):
        accuracy += custom_acc(ground_truth, prediction)
    verdict = accuracy / len(ground_truths)
    theshold = 0.55
    if verdict < theshold:
        return 0
    else:
        verdict = (verdict - theshold) / (1 - theshold)
    return round(100 * verdict)



def main():
    student_ans = read_csv(sys.argv[2])
    ground_truth = read_csv(sys.argv[3])
    if len(student_ans) != len(ground_truth):
        print("PE")
        sys.exit(2)
    final_verdict = score(extract_predicts(ground_truth), extract_predicts(student_ans), )
    print(final_verdict)


if __name__ == '__main__':
    main()
