"""2v2v2 Sequence (6 players, 3 teams of 2, 5 cards each). Sequences to win: env SEQS (default 1 = official;
set SEQS=2 for the common house rule). python -m sequence.three_team [n_seeds] [part]
Each seed is played 3 times with the hero team in seating slot 0, 1, 2 (same shuffle); villains fill the
other two teams. Par win rate = 1/3. CIs are over seeds (the 3 rotated games averaged)."""
import sys, json, math, random, time
from multiprocessing import Pool
import os
import numpy as np
SEQS = int(os.environ.get("SEQS", "1"))
TAG = "" if SEQS == 1 else "s2_"
from .engine import play_game
from .experiments import build
from .board import N, CORNER_IDX

TUNED2 = dict(W=(0, 1, 3, 9, 27, 0), jack2=100, lam=0.75)       # best 2v2 agent
STRONG2 = dict()                                                 # 2v2 baseline evaluator
HUMAN = dict(jack2=0, jack1=0, W_opp=(0, 0, 0, 4, 80, 0), individualist=True, noise=3.0)


def _worker(args):
    hero, villain, seeds = args
    out = []
    for s in seeds:
        res = []
        for slot in range(3):
            ags = [build(hero if seat % 3 == slot else villain, s * 11 + seat) for seat in range(6)]
            g = play_game(ags, random.Random(s), n_teams=3, seqs_to_win=SEQS)
            w = g.winner
            # who won relative to hero: 0 hero, 1 team moving right after hero, 2 team moving after that, 3 draw
            rel = 3 if w is None else (w - slot) % 3
            res.append((rel, g.turn, w))
        out.append(res)
    return out


def match3(hero, villain, n_seeds=600, label=""):
    t0 = time.time()
    chunks = [list(range(k, n_seeds, 16)) for k in range(16)]
    with Pool(4) as p:
        parts = p.map(_worker, [(hero, villain, [20000 + x for x in c]) for c in chunks])
    seeds = [r for part in parts for r in part]
    hero_w = np.array([np.mean([g[0] == 0 for g in r]) for r in seeds])
    nxt = np.mean([g[0] == 1 for r in seeds for g in r])
    far = np.mean([g[0] == 2 for r in seeds for g in r])
    draws = np.mean([g[0] == 3 for r in seeds for g in r])
    slot_win = [float(np.mean([r[k][2] == k for r in seeds])) for k in range(3)]  # hero win when hero in slot k
    wr, ci = hero_w.mean(), 1.96 * hero_w.std(ddof=1) / math.sqrt(len(hero_w))
    turns = np.mean([g[1] for r in seeds for g in r])
    res = dict(label=label, hero=hero, villain=villain, games=3 * len(seeds), win_rate=float(wr), ci95=float(ci),
               next_team_win=float(nxt), far_team_win=float(far), draws=float(draws), hero_win_by_slot=slot_win,
               mean_turns=float(turns), secs=round(time.time() - t0, 1))
    print(f"{label:52s} hero {wr:.3f}±{ci:.3f} (par .333) | next-team {nxt:.3f} far-team {far:.3f} draw {draws:.3f} "
          f"| by slot {slot_win[0]:.2f}/{slot_win[1]:.2f}/{slot_win[2]:.2f} | turns {turns:.0f} [{3*len(seeds)} g, {res['secs']}s]",
          flush=True)
    return res


def save(name, obj):
    json.dump(obj, open(f"results/sequence3_{TAG}{name}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    part = sys.argv[2] if len(sys.argv) > 2 else "all"
    T = TUNED2
    out = {}
    if part in ("all", "base"):
        out["base"] = [
            match3(T, T, n, "mirror tuned (seat advantage check)"),
            match3(dict(kind="random"), T, n, "random vs tuned"),
            match3(STRONG2, T, n, "2v2-baseline evaluator vs tuned"),
            match3(HUMAN, T, n, "human-model vs tuned"),
            match3(T, HUMAN, n, "tuned vs human-model"),
        ]
    if part in ("all", "defense"):
        out["defense"] = [match3(dict(T, lam=l), T, n, f"lam={l} (both opponents)") for l in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0)]
        out["defense_asym"] = [match3(dict(T, lam_next=a, lam_far=b), T, n, f"lam_next={a} lam_far={b}")
                               for a, b in ((1.0, 0.5), (1.25, 0.5), (1.0, 0.25), (0.5, 1.0), (0.75, 0.25), (1.5, 1.0))]
    if part in ("all", "jacks"):
        out["jacks"] = ([match3(dict(T, jack2=j), T, n, f"two-eyed cost={j}") for j in (0, 12, 30, 200)] +
                        [match3(dict(T, jack1=j), T, n, f"one-eyed cost={j}") for j in (0, 30, 100)])
    if part in ("all", "style"):
        out["style"] = ([match3(dict(T, W=w, W_opp=w), T, n, f"W={w[:5]}") for w in
                         [(0, 1, 2, 4, 8, 0), (0, 1, 4, 16, 80, 0), (0, 1, 5, 25, 125, 0)]] +
                        [match3(dict(T, W_opp=(0, 1, 3, 9, 200, 0)), T, n, "hard-block every enemy four"),
                         match3(dict(T, W_opp=(0, 1, 3, 40, 200, 0)), T, n, "hard-block threes and fours"),
                         match3(dict(T, individualist=True), T, n, "individualist (ignores partner)"),
                         match3(dict(T, tunnel=True), T, n, "tunnel vision"),
                         match3(dict(T, jack2=0, jack1=0), T, n, "premature jacks")])
    for k, v in out.items():
        save(f"{part}_{k}", v)
