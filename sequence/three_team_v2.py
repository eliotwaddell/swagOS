"""2v2v2 round 2: combine best settings. python -m sequence.three_team_v2 [n]"""
import sys
from .three_team import match3, save, TUNED2, HUMAN
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
C = {
 "T3a: W 1:4:16:80, lam .5": dict(W=(0, 1, 4, 16, 80, 0), jack2=100, lam=0.5),
 "T3b: W 1:4:16:80, lam .5, hard-block 4s": dict(W=(0, 1, 4, 16, 80, 0), W_opp=(0, 1, 4, 16, 250, 0), jack2=100, lam=0.5),
 "T3c: W 1:3:9:27, lam_next .75 lam_far .25": dict(W=(0, 1, 3, 9, 27, 0), jack2=100, lam_next=0.75, lam_far=0.25),
 "T3d: W 1:4:16:80, lam_next .75 lam_far .35, hard-block 4s": dict(W=(0, 1, 4, 16, 80, 0), W_opp=(0, 1, 4, 16, 250, 0), jack2=100, lam_next=0.75, lam_far=0.35),
}
out = []
for k, v in C.items():
    out.append(match3(v, TUNED2, n, k + " vs tuned2v2"))
for k, v in C.items():
    out.append(match3(v, HUMAN, n, k + " vs human"))
save("v2", out)
