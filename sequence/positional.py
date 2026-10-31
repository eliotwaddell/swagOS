"""Positional value of Sequence squares. python -m sequence.positional [games]
1) combinatorial: # of 5-windows through each square (corner-adjacent windows need only 4 chips)
2) empirical (strong self-play): P(square is in a completed sequence); win-rate lift for the team
   occupying the square at turn T (early occupancy), with standard errors.
"""
import sys, json, math, random
from multiprocessing import Pool
import numpy as np
from .board import N, WINDOWS, WINDOWS_THROUGH, CORNER_IDX, BOARD, POS
from .engine import play_game
from .agents import Greedy

import os
SEQS = int(os.environ["SEQS"]) if "SEQS" in os.environ else None
T_SNAP = 16   # snapshot after 16 plies (4 cards per player)


def combinatorial():
    win = np.zeros((N, N))
    win_w = np.zeros((N, N))      # windows weighted by 1/(chips needed) -> corner windows are cheaper
    for w in WINDOWS:
        need = sum(1 for y in w if y not in CORNER_IDX)
        for y in w:
            win[y // N, y % N] += 1
            win_w[y // N, y % N] += 5.0 / need
    for y in CORNER_IDX:
        win[y // N, y % N] = 0; win_w[y // N, y % N] = 0
    return win, win_w


def _w(args):
    seeds, nt = args
    in_seq = np.zeros(N * N); occ_win = np.zeros((N * N, 2)); occ_n = np.zeros((N * N, 2)); games = 0
    for s in seeds:
        snap = {}
        def obs(g):
            if g.turn == T_SNAP:
                snap["cells"] = list(g.cells)
        np_ = 4 if nt == 2 else 6
        kw = {} if nt == 2 else dict(W=(0, 1, 3, 9, 27, 0), jack2=100, lam=0.75)
        g = play_game([Greedy(seed=s * np_ + i, **kw) for i in range(np_)], random.Random(s), observer=obs, n_teams=nt,
                      seqs_to_win=SEQS)
        if g.winner is None or "cells" not in snap:
            continue
        games += 1
        for t in range(nt):
            for sq in g.seqs[t]:
                for y in sq:
                    in_seq[y] += 1
        for y, v in enumerate(snap["cells"]):
            if 0 <= v < nt:
                # occupant v won?
                occ_n[y, 0] += 1
                occ_win[y, 0] += (g.winner == v)
    return in_seq, occ_win, occ_n, games


if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    NT = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    tag = ("" if NT == 2 else "3team_") + ("s2_" if (NT == 3 and SEQS == 2) else "")
    win, win_w = combinatorial()
    chunks = [list(range(k, G, 16)) for k in range(16)]
    with Pool(4) as p:
        parts = p.map(_w, [(c, NT) for c in chunks])
    in_seq = sum(x[0] for x in parts); occ_win = sum(x[1] for x in parts)[:, 0]; occ_n = sum(x[2] for x in parts)[:, 0]
    games = sum(x[3] for x in parts)
    p_in = (in_seq / games).reshape(N, N)
    lift = np.where(occ_n > 0, occ_win / np.maximum(occ_n, 1), np.nan).reshape(N, N)
    lift_se = np.sqrt(np.clip(lift * (1 - lift), 0, None) / np.maximum(occ_n.reshape(N, N), 1))
    # correlation between combinatorial and empirical
    mask = np.array([[(r * N + c) not in CORNER_IDX for c in range(N)] for r in range(N)])
    corr_w = float(np.corrcoef(win[mask], p_in[mask])[0, 1])
    corr_ww = float(np.corrcoef(win_w[mask], p_in[mask])[0, 1])
    # card values: a card's two squares
    cards = {}
    for card, cells in POS.items():
        cards[card] = dict(cells=[(c // N, c % N) for c in cells], p_in_seq=[float(p_in.flat[c]) for c in cells],
                       occupancy_winrate=[float(lift.flat[c]) for c in cells])
    res = dict(games=games, snapshot_ply=T_SNAP, windows=win.tolist(), windows_corner_weighted=win_w.tolist(),
               p_in_sequence=p_in.tolist(), occupancy_win_rate=lift.tolist(), occupancy_se=lift_se.tolist(),
               corr_windows_vs_pinseq=corr_w, corr_cornerweighted_vs_pinseq=corr_ww, cards=cards)
    json.dump(res, open(f"results/sequence_{tag}positional.json", "w"), indent=1)
    np.set_printoptions(precision=2, suppress=True, linewidth=150)
    print("games", games)
    print("windows through square:\n", win.astype(int))
    print("P(square in a completed sequence):\n", p_in)
    print(f"occupancy win rate at ply {T_SNAP} (avg se {np.nanmean(lift_se):.3f}):\n", lift)
    print("corr(windows, p_in_seq)=%.2f  corr(corner-weighted, p_in_seq)=%.2f" % (corr_w, corr_ww))
