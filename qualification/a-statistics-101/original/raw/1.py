import sys
import math

j_mean = 1.5
j_mode = 1
j_med  = 1.0
EPS = 1e-6

with open(sys.argv[2], 'r', encoding='utf-8') as f:
    line = f.readline()

parts = line.strip().split()
if len(parts) != 3:
    print("WA\n0")
    sys.exit(0)

p_mean = float(parts[0])
p_mode = float(parts[1])
p_med  = float(parts[2])

ok_mean = abs(p_mean - j_mean) <= EPS
ok_mode = (int(p_mode) == j_mode) and abs(p_mode - int(p_mode)) <= EPS
ok_med  = abs(p_med  - j_med ) <= EPS

if ok_mean and ok_mode and ok_med:
    print(10)
else:
    print(0)
