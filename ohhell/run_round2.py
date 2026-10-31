"""Oh Hell round 2: mental rule validation, bias, exploitation, spoiling. python -m ohhell.run_round2 [n]"""
import sys
from .experiments import tournament, save, load_cal
load_cal(4)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
CLUB = dict(bidder="thumb", player="heur")
CAL = dict(bidder="cal", player="heur")
out = {}
out["mental"] = [
    tournament(dict(bidder="mental", player="heur"), CLUB, N, label="mental / heur vs club"),
    tournament(dict(bidder="mental", player="heur"), CAL, N, label="mental / heur vs cal field"),
    tournament(dict(bidder="mc", player="heur"), CAL, N, label="MC / heur vs cal field"),
    tournament(dict(bidder="cal", player="pimc"), CAL, N, label="cal / PIMC vs cal field"),
]
out["shift"] = [tournament(dict(bidder="cal", player="heur", shift=d), CLUB, N, label=f"cal shift {d:+d} vs club") for d in (-1, 1)]
OVER = dict(bidder="cal", player="heur", shift=1)
UNDER = dict(bidder="cal", player="heur", shift=-1)
HOG = dict(bidder="naive", player="greedy")
out["exploit"] = []
for fname, field in (("overbidders(+1)", OVER), ("underbidders(-1)", UNDER), ("trick hogs", HOG)):
    for hname, hero in (("cal(unaware)", CAL), ("mental(prior-aware)", dict(bidder="mental", player="heur")),
                        ("MC(bid-aware)", dict(bidder="mc", player="heur"))):
        out["exploit"].append(tournament(hero, field, N, label=f"{hname} vs {fname}"))
out["spoil"] = [
    tournament(dict(bidder="cal", player="pimc", play_kw=dict(objective="own")), CLUB, N, label="cal/PIMC own-score vs club"),
    tournament(dict(bidder="cal", player="pimc", play_kw=dict(objective="relative")), CLUB, N, label="cal/PIMC spoiling vs club"),
]
for k, v in out.items():
    save("round2_" + k, v)
