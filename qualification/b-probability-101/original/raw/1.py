import sys

jury_answer = 0.4213
EPS = 0.0001

with open(sys.argv[2], 'r', encoding='utf-8') as f:
    participant_line = f.readline()

participant_answer = float(participant_line)

if abs(participant_answer - jury_answer) <= EPS:
    print(10)
else:
    print(0)