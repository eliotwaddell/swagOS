"""Round 3: jack doctrine details. python -m sequence.run_v3 [n]"""
import sys
from .experiments import match, save
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
TUNED = dict(W=(0, 1, 3, 9, 27, 0), jack2=100, lam=0.75)
out = []
for j in (0, 30, 100):
    out.append(match(dict(TUNED, jack1=j), TUNED, N, f"tuned one-eyed cost={j} vs tuned(12)"))
out.append(match(dict(TUNED, W_opp=(0, 1, 3, 9, 200, 0)), TUNED, N, "tuned + emergency-block(4s) vs tuned"))
out.append(match(dict(TUNED, W_opp=(0, 1, 3, 40, 200, 0)), TUNED, N, "tuned + block 3s & 4s hard vs tuned"))
out.append(match(dict(TUNED, tunnel=True), TUNED, N, "tuned tunnel vision vs tuned"))
out.append(match(dict(TUNED, noise=3.0), TUNED, N, "tuned noisy vs tuned"))
save("v3", out)
