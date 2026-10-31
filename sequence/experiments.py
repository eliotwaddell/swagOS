"""Sequence experiments: python -m sequence.experiments <cmd>"""
import json, math, random, sys, time
from multiprocessing import Pool
import numpy as np
from .engine import play_game, Game
from .agents import Greedy, RandomAgent, MonteCarlo, DEFAULT_W
from .board import N, WINDOWS_THROUGH, CORNER_IDX, BOARD, POS

N_WORKERS = 4


def build(spec, seed):
    kind = spec.get("kind", "greedy")
    kw = {k: v for k, v in spec.items() if k != "kind"}
    if kind == "random":
        return RandomAgent(seed)
    if kind == "mc":
        base = kw.pop("base", {})
        pol = kw.pop("policy", {})
        return MonteCarlo(base=Greedy(seed=seed, **base), policy=Greedy(seed=seed + 1, **pol), seed=seed, **kw)
    return Greedy(seed=seed, **kw)


def _worker(args):
    a, b, seeds = args
    out = []
    for s in seeds:
        for swap in (0, 1):     # hero team moves first in one game, second in the other; same shuffle
            hero_team = swap
            ags = []
            for seat in range(4):
                spec = a if seat % 2 == hero_team else b
                ags.append(build(spec, s * 7 + seat))
            g = play_game(ags, random.Random(s))
            r = 0.5 if g.winner is None else (1.0 if g.winner == hero_team else 0.0)
            out.append((r, g.turn, g.winner is None))
    return out


def match(a, b, n_seeds=500, label=""):
    t0 = time.time()
    chunks = [list(range(k, n_seeds, N_WORKERS * 4)) for k in range(N_WORKERS * 4)]
    with Pool(N_WORKERS) as pool:
        parts = pool.map(_worker, [(a, b, [9000 + x for x in c]) for c in chunks])
    rows = np.array([r for p in parts for r in p], float)
    # pair the two games of each seed for the SE (shared deck)
    pairs = rows[:, 0].reshape(-1, 2).mean(1)
    wr = pairs.mean()
    ci = 1.96 * pairs.std(ddof=1) / math.sqrt(len(pairs))
    res = dict(label=label, hero=a, villain=b, games=len(rows), win_rate=wr, ci95=ci,
               draws=float(rows[:, 2].mean()), mean_turns=float(rows[:, 1].mean()), secs=round(time.time() - t0, 1))
    print(f"{label:45s} hero win {wr:.3f}±{ci:.3f}  draws {res['draws']:.3f}  turns {res['mean_turns']:.0f}  "
          f"[{len(rows)} games {res['secs']}s]", flush=True)
    return res


def save(name, obj):
    json.dump(obj, open(f"results/sequence_{name}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    if sys.argv[1] == "time":
        for spec in [dict(kind="random"), dict(), dict(kind="mc", k=4, R=6, depth=8)]:
            t = time.time()
            g = play_game([build(spec, i) if i % 2 == 0 else build({}, i) for i in range(4)], random.Random(1))
            print(spec, g.turn, g.winner, round(time.time() - t, 2))
