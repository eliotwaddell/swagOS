"""Round 2: tuned agent and corrected Monte Carlo. python -m sequence.run_v2 [n]"""
import sys
from .experiments import match, save
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
STRONG = dict()
TUNED = dict(W=(0, 1, 3, 9, 27, 0), jack2=100, lam=0.75)
HUMAN = dict(jack2=0, jack1=0, W_opp=(0, 0, 0, 4, 80, 0), individualist=True, noise=3.0)
out = []
out.append(match(TUNED, STRONG, N, "tuned vs strong"))
for j in (30, 200, 1000):
    out.append(match(dict(TUNED, jack2=j), TUNED, N, f"tuned jack2={j} vs tuned(100)"))
for l in (0.5, 1.0, 1.25):
    out.append(match(dict(TUNED, lam=l), TUNED, N, f"tuned lam={l} vs tuned(0.75)"))
out.append(match(dict(TUNED, individualist=True), TUNED, N, "tuned individualist vs tuned"))
out.append(match(dict(TUNED, jack2=0, jack1=0), TUNED, N, "tuned w/ premature jacks vs tuned"))
out.append(match(TUNED, HUMAN, N, "tuned vs human-model"))
n = max(40, N // 8)
out.append(match(dict(kind="mc", k=5, R=10, depth=8, base=TUNED, policy=TUNED), TUNED, n, "MC(v2) vs tuned"))
save("v2", out)
