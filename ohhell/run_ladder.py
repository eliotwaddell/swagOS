"""Main Oh Hell ladder. python -m ohhell.run_ladder"""
from .experiments import tournament, save, load_cal
load_cal(4)
CLUB = dict(bidder="thumb", player="heur")
HEROES = {
    "random bid / random play": dict(bidder="random", player="random"),
    "naive bid / greedy play (trick hog)": dict(bidder="naive", player="greedy"),
    "naive bid / need-aware play": dict(bidder="naive", player="heur"),
    "thumb bid / no card tracking": dict(bidder="thumb", player="heur_notrack"),
    "thumb bid / need-aware (mirror)": dict(bidder="thumb", player="heur"),
    "calibrated bid / need-aware": dict(bidder="cal", player="heur"),
    "MC bid / need-aware": dict(bidder="mc", player="heur"),
    "thumb bid / PIMC play": dict(bidder="thumb", player="pimc"),
    "MC bid / PIMC play": dict(bidder="mc", player="pimc"),
}
import sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
out = [tournament(h, CLUB, n_seeds=N, label=k) for k, h in HEROES.items()]
save("ladder_vs_club", out)
