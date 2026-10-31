"""Card-play rule ablations (each vs club field, bidding fixed = calibrated). python -m ohhell.run_play [n]"""
import sys
from .experiments import tournament, save, load_cal
load_cal(4)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 600
CLUB = dict(bidder="thumb", player="heur")
base = dict(bidder="cal", player="heur")
V = {"baseline need-aware (trump masters first, discard lowest side card, shed highest loser, 2nd-hand high w/ honor)": {},
     "cash side masters before trump masters": dict(lead_pref="side_first"),
     "discard from SHORTEST side suit (void-making)": dict(discard="short_suit"),
     "discard lowest card incl. trumps": dict(discard="lowest"),
     "when ducking: play LOWEST loser (keep high cards)": dict(dump="lowest"),
     "2nd hand: always try highest winner": dict(second="always_high"),
     "2nd hand: always duck unless sure": dict(second="duck"),
     "no card tracking": dict(tracking=False)}
out = [tournament(dict(base, play_kw=kw), CLUB, N, label=k[:60]) for k, kw in V.items()]
save("play_ablations", out)
