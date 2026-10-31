"""Closed-form odds for Sequence threats. python -m sequence.analytic
P(a specific opponent holds >=1 of m 'outs') with a 6-card hand drawn from U unseen cards:
    1 - C(U-m, 6) / C(U, 6)
Outs for an open four (one empty square, card X): copies of X not yet seen (<=2) + two-eyed jacks unseen (<=4).
"""
from math import comb


def p_hold(U, m, hand=6):
    if m <= 0:
        return 0.0
    return 1 - comb(U - m, hand) / comb(U, hand)


if __name__ == "__main__":
    print("P(next opponent can complete an open four), hand=6")
    print("unseen U | outs: 1     2     3     4     5     6")
    for U in (90, 75, 60, 45):
        print(f"  U={U:3d}  | " + "  ".join(f"{p_hold(U, m):.2f}" for m in range(1, 7)))
    print("\nTwo open fours (different squares), both must be blocked: you can block one per turn;")
    print("P(opponent completes) >= P(holds an out for the unblocked one).")
    print("\nP(either of 2 opponents holds >=1 of m outs) (approx, 12 hidden cards):")
    for U in (90, 75, 60):
        print(f"  U={U:3d}  | " + "  ".join(f"{1 - comb(U - m, 12) / comb(U, 12):.2f}" for m in range(1, 7)))

    print("\n=== 2v2v2 (5-card hands) ===")
    print("P(one specific opponent holds >=1 of m outs), hand=5")
    for U in (95, 80, 65, 50):
        print(f"  U={U:3d}  | " + "  ".join(f"{p_hold(U, m, 5):.2f}" for m in range(1, 7)))
    print("Between your turn and your partner's, TWO enemies move (next team, then far team): 10 hidden cards")
    for U in (95, 80, 65, 50):
        print(f"  U={U:3d}  | " + "  ".join(f"{1 - comb(U - m, 10) / comb(U, 10):.2f}" for m in range(1, 7)))
    print("Until your own next turn, FOUR enemy turns pass (20 hidden cards, ignoring draws)")
    for U in (95, 80, 65):
        print(f"  U={U:3d}  | " + "  ".join(f"{1 - comb(U - m, 20) / comb(U, 20):.2f}" for m in range(1, 7)))
