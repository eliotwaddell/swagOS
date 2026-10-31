"""Oh Hell experiments. Usage: python -m ohhell.experiments <name> [args]
Results are written to results/ohhell_*.json and printed."""
import json, math, random, sys, time
from multiprocessing import Pool
import numpy as np
from . import agents as A
from .engine import play_game, play_round, RoundState, hand_sequence, score_hand

N_WORKERS = 4

# ------------------------------------------------------------------ calibration
FEATS = list(A.hand_features([0], 0, 1, 4).keys())


def _calib_worker(args):
    seed, n, games, bidder = args
    rng = random.Random(seed)
    ags = [A.Agent(bidder, "heur", seed=seed * 10 + i) for i in range(n)]
    rows = []
    for g in range(games):
        dealer = rng.randrange(n)
        for h in hand_sequence(n):
            st = RoundState(n, h, dealer, rng)
            feats = [A.hand_features(st.hands[p], st.trump, h, n) for p in range(n)]
            _, st = play_round(ags, n, h, dealer, rng, state=st)
            for p in range(n):
                rows.append((h, st.trump is None, [feats[p][k] for k in FEATS], st.won[p], st.bids[p]))
            dealer = (dealer + 1) % n
    return rows


def calibrate(n=4, games=400, iters=2):
    """Fixed-point fit: tricks ~ linear(features), separately per (hand size, trump/no-trump).
    Players bid with the current calibration and play the need-aware heuristic."""
    out = {}
    for it in range(iters):
        bidder = "thumb" if it == 0 else "cal"
        with Pool(N_WORKERS) as pool:
            parts = pool.map(_calib_worker, [(1000 + it * 100 + k, n, games // N_WORKERS, bidder) for k in range(N_WORKERS)])
        rows = [r for part in parts for r in part]
        cal = {}
        report = {}
        for h in sorted(set(r[0] for r in rows)):
            for nt in (False, True):
                sub = [r for r in rows if r[0] == h and r[1] == nt]
                if len(sub) < 200:
                    continue
                X = np.array([[1.0] + r[2] for r in sub])
                y = np.array([r[3] for r in sub], float)
                # ridge for stability
                lam = 1.0
                coef = np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)
                pred = X @ coef
                rmse = float(np.sqrt(np.mean((pred - y) ** 2)))
                exact = float(np.mean(np.round(pred) == y))
                d = {"_int": float(coef[0])}
                d.update({k: float(c) for k, c in zip(FEATS, coef[1:])})
                cal[(n, h, nt)] = d
                report[f"h={h},{'NT' if nt else 'T'}"] = dict(n_obs=len(sub), rmse=rmse, round_pred_exact=exact,
                                                             coefs={k: round(v, 3) for k, v in d.items()})
        A.CAL = cal
        print(f"calibration iter {it}: {len(rows)} hand observations")
    json.dump({"n": n, "report": report}, open(f"results/ohhell_calibration_n{n}.json", "w"), indent=1)
    json.dump([[list(map(str, k)), v] for k, v in cal.items()], open(f"results/ohhell_cal_table_n{n}.json", "w"))
    for k, v in report.items():
        print(k, v["n_obs"], "rmse=%.2f" % v["rmse"], "exact=%.2f" % v["round_pred_exact"], v["coefs"])
    return cal


def load_cal(n=4):
    try:
        tab = json.load(open(f"results/ohhell_cal_table_n{n}.json"))
    except FileNotFoundError:
        return
    A.CAL = {(int(k[0]), int(k[1]), k[2] == "True"): v for k, v in tab}


# ------------------------------------------------------------------ tournament

def make(spec, seed):
    """spec: dict(bidder, player, shift, bid_kw, play_kw)"""
    return A.Agent(spec["bidder"], spec["player"], seed=seed, bid_shift=spec.get("shift", 0),
                   bid_kw=spec.get("bid_kw"), play_kw=spec.get("play_kw"))


def _tourn_worker(args):
    hero, villain, seeds, n, scoring, seq = args
    load_cal(n)
    res = []
    for s in seeds:
        block = []
        for seat in range(n):            # same deals, hero rotates through every seat
            ags = [make(hero if i == seat else villain, s * 31 + i) for i in range(n)]
            log = []
            tot = play_game(ags, random.Random(s), scoring=scoring, seq=seq, log=log, first_dealer=0)
            best = max(tot)
            winners = [i for i in range(n) if tot[i] == best]
            win = (1.0 / len(winners)) if seat in winners else 0.0
            ex = sum(1 for r in log if r["bids"][seat] == r["won"][seat]) / len(log)
            others = [tot[i] for i in range(n) if i != seat]
            block.append((win, tot[seat], tot[seat] - sum(others) / len(others), ex))
        res.append(tuple(sum(x[k] for x in block) / n for k in range(4)))
    return res


def tournament(hero, villain, n_seeds=200, n=4, scoring="standard", seq=None, label=""):
    t0 = time.time()
    chunks = [list(range(k, n_seeds, N_WORKERS * 4)) for k in range(N_WORKERS * 4)]
    with Pool(N_WORKERS) as pool:
        parts = pool.map(_tourn_worker, [(hero, villain, [5000 + x for x in c], n, scoring, seq) for c in chunks])
    rows = np.array([r for p in parts for r in p])
    m = rows.mean(0)
    se = rows.std(0, ddof=1) / math.sqrt(len(rows))
    out = dict(label=label, hero=hero, villain=villain, n_players=n, scoring=scoring, deal_blocks=len(rows),
               games=len(rows) * n, win_rate=m[0], win_ci95=1.96 * se[0], mean_score=m[1], score_ci95=1.96 * se[1],
               score_diff=m[2], diff_ci95=1.96 * se[2], exact_rate=m[3], exact_ci95=1.96 * se[3],
               secs=round(time.time() - t0, 1))
    print(f"{label:40s} win {m[0]:.3f}±{1.96*se[0]:.3f} (fair {1/n:.3f})  score {m[1]:.1f}±{1.96*se[1]:.1f}  "
          f"diff {m[2]:+.1f}±{1.96*se[2]:.1f}  exact {m[3]:.3f}  [{len(rows)*n} games, {out['secs']}s]", flush=True)
    return out


def save(name, obj):
    json.dump(obj, open(f"results/ohhell_{name}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "calibrate":
        calibrate(n=int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif cmd == "time":
        load_cal()
        for spec in [dict(bidder="cal", player="heur"), dict(bidder="mc", player="heur"), dict(bidder="cal", player="pimc")]:
            t = time.time()
            ags = [make(spec, 1)] + [make(dict(bidder="cal", player="heur"), i) for i in range(2, 5)]
            play_game(ags, random.Random(3))
            print(spec, time.time() - t)
