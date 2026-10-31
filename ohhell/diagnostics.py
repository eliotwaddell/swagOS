"""Oh Hell diagnostics: bid bias, exact rates by bid/hand size, zero bids, dealer/hook effects,
distillation of the Monte Carlo bidder into a mental rule. python -m ohhell.diagnostics [games]"""
import sys, json, random
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
from . import agents as A
from .engine import play_round, RoundState, hand_sequence
from .experiments import load_cal, FEATS


def _w(args):
    seed, games, hero = args
    load_cal(4)
    rng = random.Random(seed)
    specs = {"mc": ("mc", "heur"), "thumb": ("thumb", "heur"), "cal": ("cal", "heur"), "naive": ("naive", "heur")}
    rows = []
    for g in range(games):
        seat = g % 4
        ags = [A.Agent(*specs[hero], seed=seed + i) if i == seat else A.Agent("thumb", "heur", seed=seed + 50 + i) for i in range(4)]
        dealer = rng.randrange(4)
        for h in hand_sequence(4):
            st = RoundState(4, h, dealer, rng)
            f = A.hand_features(st.hands[seat], st.trump, h, 4)
            hand = list(st.hands[seat])
            _, st = play_round(ags, 4, h, dealer, rng, state=st)
            pos = (seat - dealer - 1) % 4          # 0 = first to bid, 3 = dealer
            prior = sum(st.bids[(dealer + 1 + k) % 4] for k in range(pos))
            rows.append(dict(h=h, nt=st.trump is None, pos=pos, prior=prior, bid=st.bids[seat], won=st.won[seat],
                             f=[f[k] for k in FEATS], total=sum(st.bids), hand=hand, trump=st.trump))
            dealer = (dealer + 1) % 4
    return rows


def collect(hero, games):
    with Pool(4) as p:
        parts = p.map(_w, [(7000 + k * 997, games // 4, hero) for k in range(4)])
    return [r for x in parts for r in x]


def summarize(rows, name):
    out = {}
    b = np.array([r["bid"] for r in rows]); w = np.array([r["won"] for r in rows])
    out["n_hands"] = len(rows)
    out["mean_bid_minus_won"] = float((b - w).mean())
    out["exact_rate"] = float((b == w).mean())
    out["over_rate"] = float((b > w).mean()); out["under_rate"] = float((b < w).mean())
    by_bid = defaultdict(list)
    for r in rows:
        by_bid[min(r["bid"], 5)].append(r["bid"] == r["won"])
    out["exact_by_bid"] = {str(k): [float(np.mean(v)), len(v)] for k, v in sorted(by_bid.items())}
    by_h = defaultdict(list)
    for r in rows:
        by_h[r["h"]].append(r["bid"] == r["won"])
    out["exact_by_handsize"] = {str(k): [float(np.mean(v)), len(v)] for k, v in sorted(by_h.items())}
    by_pos = defaultdict(list)
    for r in rows:
        by_pos[r["pos"]].append(r["bid"] == r["won"])
    out["exact_by_bid_position(0=first,3=dealer)"] = {str(k): [float(np.mean(v)), len(v)] for k, v in sorted(by_pos.items())}
    zero = [r for r in rows if r["bid"] == 0]
    out["zero_bid_share"] = len(zero) / len(rows)
    out["zero_bid_exact_by_h"] = {str(h): [float(np.mean([r["won"] == 0 for r in zero if r["h"] == h])), sum(1 for r in zero if r["h"] == h)]
                                  for h in sorted(set(r["h"] for r in zero))}
    tot = defaultdict(list)
    for r in rows:
        tot["over" if r["total"] > r["h"] else "under"].append(r["bid"] == r["won"])
    out["exact_when_table_overbid_vs_underbid"] = {k: [float(np.mean(v)), len(v)] for k, v in tot.items()}
    print("==", name, json.dumps(out, indent=1))
    return out


def distill(rows):
    """Fit MC bids ~ features (per hand-size band) -> per-card bidding values usable mentally."""
    res = {}
    for band, hs in {"1-2": (1, 2), "3-5": (3, 4, 5), "6-8": (6, 7, 8), "9-10": (9, 10)}.items():
        sub = [r for r in rows if r["h"] in hs and not r["nt"]]
        X = np.array([[1.0] + r["f"] + [r["prior"] - (r["h"] / 4) * r["pos"]] for r in sub])
        y = np.array([r["bid"] for r in sub], float)
        coef = np.linalg.lstsq(X, y, rcond=None)[0]
        pred = np.round(X @ coef)
        res[band] = dict(n=len(sub), coefs=dict(zip(["intercept"] + FEATS + ["prior_bids_minus_par"], [round(float(c), 2) for c in coef])),
                         agree_with_mc=float((pred == y).mean()))
    print("== distillation", json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    out = {}
    for hero in ("thumb", "naive", "cal", "mc"):
        rows = collect(hero, G)
        out[hero] = summarize(rows, hero)
        if hero == "mc":
            out["distill"] = distill(rows)
            json.dump([{k: v for k, v in r.items()} for r in rows], open("results/ohhell_mc_bid_rows.json", "w"))
    json.dump(out, open("results/ohhell_diagnostics.json", "w"), indent=1)
