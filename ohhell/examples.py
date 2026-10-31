"""Worked bidding examples: exact-bid probability and EV for each candidate bid via Monte Carlo
(400 sampled deals each; opponents bid calibrated + play need-aware). python -m ohhell.examples"""
import random, json
from . import agents as A
from .engine import RoundState, parse, score_hand, cstr
from .experiments import load_cal

load_cal(4)
EXAMPLES = [
    # (description, hand, upcard, hand size, my seat relative to dealer: pos 0=first bidder, 3=dealer, prior bids)
    ("10 cards, 3 trumps incl. A, side A+K", "AS 7S 3S AH 9H 4H KD 8D 6C 2C", "5S", 0, []),
    ("10 cards, long weak trumps (5 small)", "9S 7S 5S 4S 2S QH 8H 6D 3C 2C", "TS", 0, []),
    ("10 cards, no trumps, two side Aces", "AH 8H 5H AD 9D 4D 2D QC 7C 3C", "KS", 0, []),
    ("5 cards, trump K + side A, first to bid", "KS 6S AH 7D 4C", "2S", 0, []),
    ("5 cards, same hand, dealer after bids 2,2,1 (hook forbids 0)", "KS 6S AH 7D 4C", "2S", 3, [2, 2, 1]),
    ("3 cards, side K-Q-J (no trump)", "KH QD JC", "5S", 0, []),
    ("1 card: a side Ace, first to lead", "AH", "5S", 0, []),
    ("1 card: a side Ace, dealer (leads last)", "AH", "5S", 3, [0, 0, 0]),
    ("1 card: low trump (4 of trumps), first to lead", "4S", "5S", 0, []),
]


def analyze(desc, hand_s, up_s, pos, prior, samples=400, seed=1):
    rng = random.Random(seed)
    hand = [parse(x) for x in hand_s.split()]
    up = parse(up_s)
    h = len(hand)
    n = 4
    dealer = 0
    me = (dealer + 1 + pos) % n
    deck = [c for c in range(52) if c not in hand and c != up]
    rng.shuffle(deck)
    hands = [None] * n
    hands[me] = hand
    i = 0
    for q in range(n):
        if q != me:
            hands[q] = deck[i:i + h]; i += h
    st = RoundState(n, h, dealer, rng, hands=hands, upcard=up)
    for k, b in enumerate(prior):
        st.bids[(dealer + 1 + k) % n] = b
    fb = st.forbidden_bid(me)
    res = {}
    deals = [A.sample_hidden(st, me, rng) for _ in range(samples)]
    for b in range(0, min(h, 5) + 1):
        if b == fb:
            continue
        dist = [0] * (h + 1)
        for hs in deals:
            s = st.clone_with_hands(hs)
            s.bids[me] = b
            for q in s.bid_order():
                if s.bids[q] is None:
                    s.bids[q] = A.bid_calibrated(s, q, rng)
            A.rollout(s, rng)
            dist[s.won[me]] += 1
        pe = dist[b] / samples
        res[b] = dict(p_exact=round(pe, 3), ev=round(pe * (10 + b), 2))
    best = max(res, key=lambda b: res[b]["ev"])
    mp = A.mental_points(hand, up // 13, h, sum(prior), pos, n)
    line = f"{desc}\n  hand {hand_s} | trump {'CDHS'[up // 13]} | bid position {pos} prior {prior} forbidden {fb}\n"
    line += "  " + "  ".join(f"bid {b}: P={v['p_exact']:.2f} EV={v['ev']:.1f}" for b, v in res.items())
    line += f"\n  -> best bid {best}; mental count {mp:.2f} -> {int(mp + 0.5)}\n"
    print(line, flush=True)
    return dict(desc=desc, hand=hand_s, upcard=up_s, pos=pos, prior=prior, forbidden=fb, results=res, best=best,
                mental=mp)


if __name__ == "__main__":
    out = [analyze(*e) for e in EXAMPLES]
    json.dump(out, open("results/ohhell_examples.json", "w"), indent=1)
