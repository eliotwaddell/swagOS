"""Oh Hell agents: bidding policies x play policies.

An Agent = (bidder, player). Every agent sees only legal information:
own hand, upcard, bids so far, cards played, inferred voids.
"""
import random
from .engine import legal_moves, beats, trick_winner, RoundState, score_hand

# ----------------------------------------------------------------------------- helpers

def unseen_cards(st, p):
    """Cards not in p's hand, not played, not the upcard."""
    known = set(st.hands[p]) | st.played
    if st.upcard is not None:
        known.add(st.upcard)
    return [c for c in range(52) if c not in known]


def is_master(c, unseen_set):
    """No unseen card of the same suit outranks c."""
    s, r = c // 13, c % 13
    for rr in range(r + 1, 13):
        if s * 13 + rr in unseen_set:
            return False
    return True


def current_best(trick, trump):
    if not trick:
        return None
    return trick[trick_winner(trick, trump)][1]


# ----------------------------------------------------------------------------- play policies

def play_random(st, p, rng, **kw):
    return rng.choice(legal_moves(st.hands[p], st.led_suit()))


def play_greedy(st, p, rng, **kw):
    """Human 'trick hog': always tries to win the trick (highest legal), leads highest card."""
    legal = legal_moves(st.hands[p], st.led_suit())
    trump = st.trump
    if not st.trick:
        return max(legal, key=lambda c: (c // 13 == trump, c % 13))
    best = current_best(st.trick, trump)
    led = st.led_suit()
    winners = [c for c in legal if beats(c, best, led, trump)]
    if winners:
        return min(winners, key=lambda c: (c // 13 == trump, c % 13))
    return min(legal, key=lambda c: (c // 13 == trump, c % 13))


def play_heuristic(st, p, rng, tracking=True, lead_pref="trump_first", discard="lowest_rank", dump="highest_loser",
                   second="high_if_honor", **kw):
    """Need-aware heuristic: tries to make the bid exactly.

    tracking=False models a player who does not count played cards (only knows Aces are top).
    """
    hand = st.hands[p]
    led = st.led_suit()
    legal = legal_moves(hand, led)
    if len(legal) == 1:
        return legal[0]
    trump = st.trump
    need = st.bids[p] - st.won[p]
    left = len(hand)
    unseen = set(unseen_cards(st, p)) if tracking else set(c for c in range(52) if c not in hand and c != st.upcard)
    want = need > 0
    n = st.n
    pos = len(st.trick)              # 0 = leading
    last = pos == n - 1
    after = [(p + k) % n for k in range(1, n - pos)]   # players still to play this trick

    def tval(c):  # sort key: trumps above all, then rank
        return (c // 13 == trump) * 13 + c % 13

    def safe_win(c):
        """c would win the trick against all unseen cards of players after us (approx)."""
        if last:
            return True
        s = c // 13
        if s == trump:
            return is_master(c, unseen)
        if not is_master(c, unseen):
            return False
        if trump is None:
            return True
        # danger if some later player is void in the suit and may still hold trump
        trumps_out = any(x // 13 == trump for x in unseen)
        if not trumps_out:
            return True
        suit_out = sum(1 for x in unseen if x // 13 == s)
        # rough: if many of the suit are out, ruff unlikely early
        if any(st.voids[q][s] for q in after):
            return False
        return suit_out >= len(after) + 1

    if pos > 0:
        best = current_best(st.trick, trump)
        winners = [c for c in legal if beats(c, best, led, trump)]
        losers = [c for c in legal if c not in winners]
        if want:
            if winners:
                safe = [c for c in winners if safe_win(c)]
                if safe:
                    return min(safe, key=tval)
                if need >= left:          # must win everything: go big
                    return max(winners, key=tval)
                # not safe: try with cheapest winner only if it's a high card, else duck low
                hi = max(winners, key=tval)
                if second == "always_high" or (second == "high_if_honor" and (hi % 13 >= 10 or hi // 13 == trump)):
                    return hi
                return min(legal, key=tval)
            # cannot win: discard lowest, prefer non-trump from shortest suit
            if discard == "lowest":
                return min(legal, key=tval)
            if discard == "short_suit":   # void-making: shortest side suit first
                return min(legal, key=lambda c: (c // 13 == trump, sum(1 for x in hand if x // 13 == c // 13), c % 13))
            return min(legal, key=lambda c: (c // 13 == trump, c % 13, sum(1 for x in hand if x // 13 == c // 13)))
        else:
            if losers:
                # shed the most dangerous card that still loses
                return max(losers, key=tval) if dump == "highest_loser" else min(losers, key=tval)
            # forced to (maybe) win
            if last:
                return max(winners, key=tval)
            return min(winners, key=tval)
    # ---------------- leading
    if want:
        masters = [c for c in legal if is_master(c, unseen)]
        trumps = [c for c in legal if c // 13 == trump]
        tm = [c for c in masters if c // 13 == trump]
        sm = [c for c in masters if c // 13 != trump and safe_win_lead(c, st, p, unseen)]
        if lead_pref == "trump_first" and tm and (len(trumps) >= 2 or not sm):
            return max(tm, key=tval)
        if sm:
            return max(sm, key=tval)
        if tm:
            return max(tm, key=tval)
        # no master: lead low from shortest side suit (create a void for ruffing) if holding trumps,
        # else lead highest from longest suit to establish
        side = [c for c in legal if c // 13 != trump]
        if side and trumps:
            short = min(set(c // 13 for c in side), key=lambda s: sum(1 for c in side if c // 13 == s))
            return min((c for c in side if c // 13 == short), key=tval)
        return max(legal, key=tval) if not side else max(side, key=tval)
    else:
        # lead a card unlikely to win: lowest rank, avoid trump; prefer suit with many unseen higher cards
        def risk(c):
            s = c // 13
            higher = sum(1 for x in unseen if x // 13 == s and x % 13 > c % 13)
            return ((s == trump) * 100) - higher * 3 + c % 13
        return min(legal, key=risk)


def safe_win_lead(c, st, p, unseen):
    s = c // 13
    if st.trump is None:
        return True
    if not any(x // 13 == st.trump for x in unseen):
        return True
    others = [(p + k) % st.n for k in range(1, st.n)]
    if any(st.voids[q][s] for q in others):
        return False
    suit_out = sum(1 for x in unseen if x // 13 == s)
    return suit_out >= st.n - 1


# ----------------------------------------------------------------------------- bidding policies

def legalize(b, st, p):
    b = max(0, min(st.h, b))
    fb = st.forbidden_bid(p)
    if b == fb:
        # move toward the side with smaller expected loss: default go down unless at 0
        b = b - 1 if b > 0 else b + 1
    return b


def bid_random(st, p, rng, **kw):
    return legalize(rng.randint(0, st.h), st, p)


def bid_naive(st, p, rng, **kw):
    """Typical overbidder: counts every Ace, every King, and trumps J+ as a trick."""
    t = st.trump
    b = 0
    for c in st.hands[p]:
        r = c % 13
        if r >= 11:
            b += 1
        elif c // 13 == t and r >= 9:
            b += 1
    return legalize(b, st, p)


def bid_rule_of_thumb(st, p, rng, **kw):
    """Competent club-player rule: Aces=1, side K with 2+ =0.5, trump K=1, trump Q (3+ trumps)=1,
    each trump beyond 3 = 1."""
    t = st.trump
    hand = st.hands[p]
    suits = [[c for c in hand if c // 13 == s] for s in range(4)]
    v = 0.0
    for s in range(4):
        ranks = sorted((c % 13 for c in suits[s]), reverse=True)
        if s == t:
            for r in ranks:
                if r >= 11:
                    v += 1
                elif r == 10 and len(ranks) >= 3:
                    v += 1
            v += max(0, len(ranks) - 3)
        else:
            for r in ranks:
                if r == 12:
                    v += 1
                elif r == 11 and len(ranks) >= 2:
                    v += 0.5
    return legalize(int(round(v)), st, p)


# Calibrated per-card trick values (filled in by experiments.calibrate; defaults are from that run).
CAL = None


def hand_features(hand, trump, h, n):
    """Feature vector used by the calibrated bidder / regression study."""
    suits = [[c % 13 for c in hand if c // 13 == s] for s in range(4)]
    f = {}
    nt = trump is None
    tr = [] if nt else suits[trump]
    f["trump_A"] = int(12 in tr)
    f["trump_K"] = int(11 in tr)
    f["trump_Q"] = int(10 in tr)
    f["trump_J"] = int(9 in tr)
    f["trump_low"] = sum(1 for r in tr if r < 9)
    side = [s for s in range(4) if s != trump]
    f["side_A"] = sum(1 for s in side if 12 in suits[s])
    f["side_K_guarded"] = sum(1 for s in side if 11 in suits[s] and len(suits[s]) >= 2)
    f["side_K_bare"] = sum(1 for s in side if 11 in suits[s] and len(suits[s]) == 1)
    f["side_Q"] = sum(1 for s in side if 10 in suits[s])
    f["voids_with_trump"] = sum(1 for s in side if len(suits[s]) == 0) if tr else 0
    f["singletons_with_trump"] = sum(1 for s in side if len(suits[s]) == 1) if tr else 0
    return f


def bid_calibrated(st, p, rng, **kw):
    """Linear trick estimate with coefficients fitted by simulation (see experiments.calibrate)."""
    coefs = CAL.get((st.n, min(st.h, 10), st.trump is None)) if CAL else None
    if coefs is None:
        return bid_rule_of_thumb(st, p, rng)
    f = hand_features(st.hands[p], st.trump, st.h, st.n)
    v = coefs["_int"] + sum(coefs[k] * f[k] for k in f)
    return legalize(int(round(v)), st, p)


def sample_hidden(st, p, rng, max_tries=50):
    """Random deal of unseen cards to the other players consistent with their hand sizes and voids."""
    pool = unseen_cards(st, p)
    sizes = {q: len(st.hands[q]) for q in range(st.n) if q != p}
    for _ in range(max_tries):
        rng.shuffle(pool)
        hands = [None] * st.n
        hands[p] = list(st.hands[p])
        rest = list(pool)
        ok = True
        # most-constrained first
        order = sorted(sizes, key=lambda q: -sum(st.voids[q]))
        for q in order:
            cand = [c for c in rest if not st.voids[q][c // 13]]
            if len(cand) < sizes[q]:
                ok = False
                break
            take = cand[:sizes[q]]
            hands[q] = take
            ts = set(take)
            rest = [c for c in rest if c not in ts]
        if ok:
            return hands
    # fallback ignoring voids
    rng.shuffle(pool)
    hands = [None] * st.n
    hands[p] = list(st.hands[p])
    i = 0
    for q in sizes:
        hands[q] = pool[i:i + sizes[q]]
        i += sizes[q]
    return hands


def rollout(st, rng, policy=play_heuristic):
    while not st.done():
        q = st.to_play()
        st.play(q, policy(st, q, rng))
    return st


def bid_montecarlo(st, p, rng, samples=40, others_bidder=None, **kw):
    """Probability-aware bidder: for each candidate bid b, sample hidden hands, let opponents bid
    (actual bids if already made, else calibrated estimate), roll out with heuristic play while
    p plays toward b. Picks argmax E[score | b] with hook constraint. Opponent-aware via actual bids."""
    others_bidder = others_bidder or bid_calibrated
    base = bid_calibrated(st, p, rng)
    cands = sorted(set(max(0, min(st.h, base + d)) for d in (-2, -1, 0, 1, 2)))
    fb = st.forbidden_bid(p)
    cands = [b for b in cands if b != fb]
    best, best_ev = base, -1e9
    deals = [sample_hidden(st, p, rng) for _ in range(samples)]
    for b in cands:
        tot = 0.0
        for hands in deals:
            s = st.clone_with_hands(hands)
            s.bids[p] = b
            # fill in bids of players after p using the estimate on their sampled hands
            for q in s.bid_order():
                if s.bids[q] is None:
                    s.bids[q] = others_bidder(s, q, rng)
            rollout(s, rng)
            tot += score_hand(b, s.won[p])
        ev = tot / samples
        if ev > best_ev:
            best, best_ev = b, ev
    return legalize(best, st, p)


# ----------------------------------------------------------------------------- PIMC player

def play_pimc(st, p, rng, samples=16, objective="relative", **kw):
    """Perfect-information Monte Carlo: for each legal card, sample consistent deals, roll out with
    the heuristic policy, average the objective.  objective='own' = own hand score,
    'relative' = own score - mean(opponents' scores) (spoils opponents when cheap)."""
    legal = legal_moves(st.hands[p], st.led_suit())
    if len(legal) == 1:
        return legal[0]
    deals = [sample_hidden(st, p, rng) for _ in range(samples)]
    best, best_v = legal[0], -1e9
    for c in legal:
        tot = 0.0
        for hands in deals:
            s = st.clone_with_hands(hands)
            s.play(p, c)
            rollout(s, rng)
            own = score_hand(s.bids[p], s.won[p])
            if objective == "own":
                tot += own
            else:
                opp = [score_hand(s.bids[q], s.won[q]) for q in range(s.n) if q != p]
                tot += own - 0.5 * sum(opp) / len(opp)
        if tot > best_v:
            best, best_v = c, tot
    return best


# ----------------------------------------------------------------------------- composition

def mental_points(hand, trump, h, prior=None, pos=None, n=4):
    """The 20-second mental count (distilled from the Monte Carlo bidder, 4 players).
    Each trump 3/4; trump Ace +3/4, King +1/2, Queen +1/4 (hands of 3+).
    Side Ace 3/4 (1/2 in hands of 3-5, 0 in hands of 1-2); side King 1/2 (hands of 6+ only).
    Minus 1/2 in hands of 6-8, minus 1 in hands of 9-10.
    If the bids already made exceed the 'fair share' (tricks * bidders_so_far / players) by 1 or more,
    shade down 1/4 per excess trick."""
    v = 0.0
    for c in hand:
        s, r = c // 13, c % 13
        if s == trump:
            v += 0.75
            if h >= 3:
                v += {12: 0.75, 11: 0.5, 10: 0.25}.get(r, 0.0)
        else:
            if r == 12:
                v += 0.0 if h <= 2 else (0.5 if h <= 5 else 0.75)
            elif r == 11 and h >= 6:
                v += 0.5
    if 6 <= h <= 8:
        v -= 0.5
    elif h >= 9:
        v -= 1.0
    if prior is not None and pos:
        excess = prior - h * pos / n
        if excess >= 1:
            v -= 0.25 * excess
    return v


def bid_mental(st, p, rng, tie="up", **kw):
    order = st.bid_order()
    pos = order.index(p)
    prior = sum(st.bids[q] for q in order[:pos])
    v = mental_points(st.hands[p], st.trump, st.h, prior, pos, st.n)
    b = int(v + 0.5) if tie == "up" else int(v + 0.5 - 1e-9) if v > 0 else 0
    return legalize(b, st, p)


PLAYERS = {
    "random": play_random,
    "greedy": play_greedy,
    "heur": play_heuristic,
    "heur_notrack": lambda st, p, rng, **kw: play_heuristic(st, p, rng, tracking=False),
    "pimc": play_pimc,
}
BIDDERS = {
    "random": bid_random,
    "naive": bid_naive,
    "thumb": bid_rule_of_thumb,
    "cal": bid_calibrated,
    "mc": bid_montecarlo,
    "mental": bid_mental,
}


class Agent:
    def __init__(self, bidder, player, name=None, seed=None, bid_shift=0, bid_kw=None, play_kw=None):
        self.bidder = BIDDERS[bidder] if isinstance(bidder, str) else bidder
        self.player = PLAYERS[player] if isinstance(player, str) else player
        self.name = name or f"{bidder}/{player}"
        self.rng = random.Random(seed)
        self.bid_shift = bid_shift
        self.bid_kw = bid_kw or {}
        self.play_kw = play_kw or {}

    def bid(self, st, p):
        b = self.bidder(st, p, self.rng, **self.bid_kw)
        if self.bid_shift:
            b = legalize(b + self.bid_shift, st, p)
        return b

    def play(self, st, p):
        return self.player(st, p, self.rng, **self.play_kw)
