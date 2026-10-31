"""Oh Hell with the 1 -> 7 -> 1 hand pattern (13 hands). python -m ohhell.run_171 [n]"""
import sys
from .experiments import tournament, save, load_cal
from .engine import hand_sequence
load_cal(4)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SEQ = hand_sequence(4, max_cards=7, pattern="up_down")          # 1..7..1
CLUB = dict(bidder="thumb", player="heur")
H = {
    "naive bid / greedy play (trick hog)": dict(bidder="naive", player="greedy"),
    "naive bid / need-aware play": dict(bidder="naive", player="heur"),
    "mental count (tie up) / need-aware": dict(bidder="mental", player="heur"),
    "mental count (tie down) / need-aware": dict(bidder="mental", player="heur", bid_kw=dict(tie="down")),
    "calibrated / need-aware": dict(bidder="cal", player="heur"),
    "calibrated shift -1": dict(bidder="cal", player="heur", shift=-1),
    "calibrated shift +1": dict(bidder="cal", player="heur", shift=1),
    "MC bid / need-aware": dict(bidder="mc", player="heur"),
    "thumb / PIMC play": dict(bidder="thumb", player="pimc"),
    "MC bid / PIMC play": dict(bidder="mc", player="pimc"),
}
out = [tournament(h, CLUB, N, seq=SEQ, label="[1-7-1, 4p] " + k) for k, h in H.items()]
for n in (3, 5, 6):
    seq = hand_sequence(n, max_cards=7, pattern="up_down")
    out.append(tournament(dict(bidder="mental", player="heur"), CLUB, N, n=n, seq=seq, label=f"[1-7-1, {n}p] mental count"))
    out.append(tournament(dict(bidder="naive", player="greedy"), CLUB, N, n=n, seq=seq, label=f"[1-7-1, {n}p] trick hog"))
save("pattern_171", out)
