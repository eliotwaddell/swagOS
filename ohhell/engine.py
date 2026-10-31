"""Oh Hell game engine.

Cards are ints 0..51: suit = c // 13 (0=C,1=D,2=H,3=S), rank = c % 13 (0='2' ... 12='A').
Baseline rules (Pagat "Oh Hell"):
  * n players, individual scoring, hand sizes go down from max to 1 then back up (configurable).
  * After the deal the next card is turned; its suit is trump. If the deck is exhausted -> no trump.
  * Bidding starts left of dealer; dealer bids last and may NOT make total bids == tricks (the "hook").
  * Must follow suit if able; otherwise any card. Highest trump wins, else highest of suit led.
  * Score: exact bid -> 10 + bid, otherwise 0  (variants supported via `scoring`).
"""
import random

SUITS = "CDHS"
RANKS = "23456789TJQKA"


def suit(c):
    return c // 13


def rank(c):
    return c % 13


def cstr(c):
    return RANKS[rank(c)] + SUITS[suit(c)]


def parse(s):
    return SUITS.index(s[1]) * 13 + RANKS.index(s[0])


def legal_moves(hand, led):
    if led is None:
        return list(hand)
    f = [c for c in hand if c // 13 == led]
    return f if f else list(hand)


def beats(a, b, led, trump):
    """True if card a beats current best card b in a trick with suit `led`."""
    sa, sb = a // 13, b // 13
    if sa == sb:
        return a % 13 > b % 13
    if trump is not None and sa == trump:
        return True
    return False


def trick_winner(cards, trump):
    """cards: list of (player, card) in play order. Returns index into list of winning entry."""
    led = cards[0][1] // 13
    best = 0
    for i in range(1, len(cards)):
        if beats(cards[i][1], cards[best][1], led, trump):
            best = i
    return best


def score_hand(bid, won, scoring="standard"):
    if scoring == "standard":          # 10 + bid if exact else 0
        return 10 + bid if bid == won else 0
    if scoring == "trick_plus_bonus":  # 1/trick + 10 bonus for exact
        return won + (10 if bid == won else 0)
    if scoring == "penalty":           # 10+bid exact, else -|diff| * 10 ... (common house rule: lose 10/trick off)
        return 10 + bid if bid == won else -10 * abs(bid - won)
    raise ValueError(scoring)


def hand_sequence(n_players, max_cards=None, pattern="down_up"):
    if max_cards is None:
        max_cards = {3: 10, 4: 10, 5: 10, 6: 8, 7: 7}.get(n_players, 52 // n_players)
    down = list(range(max_cards, 0, -1))
    if pattern == "down_up":
        return down + list(range(2, max_cards + 1))
    if pattern == "up_down":
        return list(range(1, max_cards + 1)) + list(range(max_cards - 1, 0, -1))
    if pattern == "down":
        return down
    raise ValueError(pattern)


class RoundState:
    """Public + private state of one hand (deal)."""

    def __init__(self, n, h, dealer, rng, hands=None, upcard=None):
        self.n, self.h, self.dealer = n, h, dealer
        if hands is None:
            deck = list(range(52))
            rng.shuffle(deck)
            hands = [sorted(deck[i * h:(i + 1) * h]) for i in range(n)]
            upcard = deck[n * h] if n * h < 52 else None
        self.hands = [list(x) for x in hands]
        self.upcard = upcard
        self.trump = None if upcard is None else upcard // 13
        self.bids = [None] * n
        self.won = [0] * n
        self.played = set()              # cards already played in completed or current tricks
        self.voids = [[False] * 4 for _ in range(n)]
        self.trick = []                  # list of (player, card)
        self.leader = (dealer + 1) % n
        self.history = []                # list of completed tricks
        self.n_tricks_done = 0

    def bid_order(self):
        return [(self.dealer + 1 + i) % self.n for i in range(self.n)]

    def forbidden_bid(self, p):
        """Bid the dealer may not make (hook rule)."""
        if p != self.dealer:
            return None
        s = sum(b for b in self.bids if b is not None)
        f = self.h - s
        return f if f >= 0 else None

    def to_play(self):
        return (self.leader + len(self.trick)) % self.n

    def led_suit(self):
        return self.trick[0][1] // 13 if self.trick else None

    def play(self, p, c):
        assert p == self.to_play()
        led = self.led_suit()
        assert c in self.hands[p], (p, c)
        assert c in legal_moves(self.hands[p], led), "illegal: must follow suit"
        if led is not None and c // 13 != led:
            self.voids[p][led] = True
        self.hands[p].remove(c)
        self.played.add(c)
        self.trick.append((p, c))
        if len(self.trick) == self.n:
            w = self.trick[trick_winner(self.trick, self.trump)][0]
            self.won[w] += 1
            self.history.append(self.trick)
            self.trick = []
            self.leader = w
            self.n_tricks_done += 1
            return w
        return None

    def done(self):
        return self.n_tricks_done == self.h

    def clone_with_hands(self, hands):
        s = RoundState.__new__(RoundState)
        s.n, s.h, s.dealer = self.n, self.h, self.dealer
        s.hands = [list(x) for x in hands]
        s.upcard, s.trump = self.upcard, self.trump
        s.bids = list(self.bids)
        s.won = list(self.won)
        s.played = set(self.played)
        s.voids = [list(v) for v in self.voids]
        s.trick = list(self.trick)
        s.leader = self.leader
        s.history = self.history  # shared, read-only
        s.n_tricks_done = self.n_tricks_done
        return s


def play_round(agents, n, h, dealer, rng, scoring="standard", state=None, log=None):
    st = state or RoundState(n, h, dealer, rng)
    for p in st.bid_order():
        b = agents[p].bid(st, p)
        fb = st.forbidden_bid(p)
        assert 0 <= b <= h and b != fb, f"illegal bid {b} (forbidden {fb})"
        st.bids[p] = b
    for _ in range(h * n):
        p = st.to_play()
        c = agents[p].play(st, p)
        st.play(p, c)
    assert st.done() and sum(st.won) == h
    pts = [score_hand(st.bids[i], st.won[i], scoring) for i in range(n)]
    if log is not None:
        log.append(dict(h=h, dealer=dealer, trump=st.trump, bids=list(st.bids), won=list(st.won), pts=pts))
    return pts, st


def play_game(agents, rng, scoring="standard", seq=None, log=None, first_dealer=None):
    n = len(agents)
    seq = seq or hand_sequence(n)
    totals = [0] * n
    dealer = rng.randrange(n) if first_dealer is None else first_dealer
    for h in seq:
        for a in agents:
            if hasattr(a, "new_round"):
                a.new_round()
        pts, st = play_round(agents, n, h, dealer, rng, scoring, log=log)
        for a in agents:
            if hasattr(a, "observe_round"):
                a.observe_round(st)
        totals = [t + q for t, q in zip(totals, pts)]
        dealer = (dealer + 1) % n
    return totals
