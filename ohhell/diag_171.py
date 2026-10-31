"""Exact rates / bias by hand size under 1-7-1 for the MC bidder (4p). python -m ohhell.diag_171"""
import random, json
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
from . import agents as A
from .engine import play_round, RoundState, hand_sequence
from .experiments import load_cal

def _w(seed):
    load_cal(4); rng = random.Random(seed); rows = []
    for g in range(100):
        seat = g % 4
        ags = [A.Agent("mc", "heur", seed=seed + i) if i == seat else A.Agent("thumb", "heur", seed=seed + 9 + i) for i in range(4)]
        dealer = rng.randrange(4)
        for h in hand_sequence(4, max_cards=7, pattern="up_down"):
            _, st = play_round(ags, 4, h, dealer, rng)
            rows.append((h, st.bids[seat], st.won[seat], (seat - dealer - 1) % 4))
            dealer = (dealer + 1) % 4
    return rows

if __name__ == "__main__":
    with Pool(4) as p:
        rows = [r for part in p.map(_w, [31, 32, 33, 34]) for r in part]
    out = {"n_hands": len(rows)}
    by = defaultdict(list)
    for h, b, w, pos in rows: by[h].append(b == w)
    out["exact_by_handsize"] = {h: round(float(np.mean(v)), 3) for h, v in sorted(by.items())}
    bb = defaultdict(list)
    for h, b, w, pos in rows: bb[min(b, 4)].append(b == w)
    out["exact_by_bid"] = {b: [round(float(np.mean(v)), 3), len(v)] for b, v in sorted(bb.items())}
    out["zero_share"] = round(sum(1 for r in rows if r[1] == 0) / len(rows), 3)
    out["bias_bid_minus_won"] = round(float(np.mean([b - w for h, b, w, p in rows])), 3)
    pp = defaultdict(list)
    for h, b, w, pos in rows: pp[pos].append(b == w)
    out["exact_by_position"] = {k: round(float(np.mean(v)), 3) for k, v in sorted(pp.items())}
    print(json.dumps(out, indent=1))
    json.dump(out, open("results/ohhell_171_diagnostics.json", "w"), indent=1)
