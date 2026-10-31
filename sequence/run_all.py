"""Full Sequence experiment suite. python -m sequence.run_all [n_seeds]"""
import sys, json, math, random
from .experiments import match, save
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
which = sys.argv[2] if len(sys.argv) > 2 else "all"
STRONG = dict()                                  # Greedy defaults: lam=1, W=(0,1,4,16,80), jack costs 12
HUMAN = dict(jack2=0, jack1=0, W_opp=(0, 0, 0, 4, 80, 0), individualist=True, noise=3.0)
out = {}
if which in ("all", "ladder"):
    out["ladder_vs_strong"] = [
        match(dict(kind="random"), STRONG, N, "random vs strong"),
        match(HUMAN, STRONG, N, "human-model vs strong"),
        match(STRONG, STRONG, N, "strong mirror (sanity, expect .5)"),
    ]
    flaws = {
        "premature jacks (cost 0)": dict(jack2=0, jack1=0),
        "ignores developing threats (blocks only 3+)": dict(W_opp=(0, 0, 0, 4, 80, 0)),
        "ignores threats below 4": dict(W_opp=(0, 0, 0, 0, 80, 0)),
        "individualist (ignores teammate chips)": dict(individualist=True),
        "tunnel vision (only near own chips)": dict(tunnel=True),
        "pure offense (lam=0)": dict(lam=0.0),
        "noisy (sd 3)": dict(noise=3.0),
    }
    out["flaws_vs_strong"] = [match(v, STRONG, N, "flaw: " + k) for k, v in flaws.items()]
if which in ("all", "sweep"):
    out["lam_sweep"] = [match(dict(lam=l), STRONG, N, f"lam={l}") for l in (0.25, 0.5, 0.75, 1.25, 1.5, 2.0, 3.0)]
    out["jack2_sweep"] = [match(dict(jack2=j), STRONG, N, f"two-eyed cost={j}") for j in (0, 4, 25, 50, 100)]
    out["jack1_sweep"] = [match(dict(jack1=j), STRONG, N, f"one-eyed cost={j}") for j in (0, 4, 25, 50, 100)]
    out["W_sweep"] = [match(dict(W=w, W_opp=w), STRONG, N, f"W={w}") for w in
                      [(0, 1, 2, 4, 8, 0), (0, 1, 3, 9, 27, 0), (0, 1, 5, 25, 125, 0), (0, 1, 8, 64, 400, 0), (0, 0, 1, 10, 100, 0)]]
if which in ("all", "human"):
    out["vs_human"] = [match(STRONG, HUMAN, N, "strong vs human-model"),
                       match(dict(lam=1.5), HUMAN, N, "lam1.5 vs human-model"),
                       match(dict(lam=0.5), HUMAN, N, "lam0.5 vs human-model"),
                       match(dict(jack2=50, jack1=50), HUMAN, N, "jack-hoarder vs human-model")]
if which in ("all", "mc"):
    n = max(40, N // 5)
    out["mc_vs_strong"] = [match(dict(kind="mc", k=5, R=8, depth=8), STRONG, n, "MC lookahead vs strong")]
for k, v in out.items():
    save(f"{which}_{k}", v)
