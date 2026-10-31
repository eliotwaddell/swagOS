"""Sequence agents.

Evaluation = sum over 5-windows of W[k] where k = own chips (+free corners) in a window with no enemy chips,
minus lam * the same for the enemy. Moves are scored by the incremental change of the windows through
the affected cell (exact, fast). Parameters let us model strong play and typical human habits.
"""
import random
from .board import WINDOWS, WINDOWS_THROUGH, POS, CARDS, TWO_EYED, ONE_EYED, N
from .engine import EMPTY, CORNER, Game

DEFAULT_W = (0, 1, 4, 16, 80, 0)       # value of a live window holding k of our chips; k=5 handled as sequence


def window_value(g, wi, t, W, owner_seat=None):
    w = WINDOWS[wi]
    k = 0
    seqs = g.seqs[t]
    if seqs:
        ws = set(w)
        for s in seqs:
            if len(ws & s) >= 2:
                return 0.0
    for y in w:
        v = g.cells[y]
        if v == CORNER:
            k += 1
        elif v == t:
            if owner_seat is None or g.owner[y] == owner_seat:
                k += 1
        elif v != EMPTY:
            return 0.0
    return W[k] if k < 5 else 0.0


def local_value(g, x, t, W, owner_seat=None):
    return sum(window_value(g, wi, t, W, owner_seat) for wi in WINDOWS_THROUGH[x])


def total_value(g, t, W):
    return sum(window_value(g, wi, t, W) for wi in range(len(WINDOWS)))


class Greedy:
    """One-ply evaluator.
    lam      : weight on denying the enemy (defense)
    W, W_opp : window weights (own / enemy as perceived)
    jack2/jack1 : option-value cost charged for spending a two-eyed / one-eyed jack
    individualist : ignore teammate chips when valuing own windows (poor coordination model)
    tunnel   : only consider placements adjacent (within window) to own existing chips if any (tunnel vision)
    noise    : random jitter (models inconsistency)
    """

    def __init__(self, lam=1.0, W=DEFAULT_W, W_opp=None, jack2=12.0, jack1=12.0, individualist=False,
                 tunnel=False, noise=0.0, seed=None, name=None, lam_next=None, lam_far=None):
        self.lam, self.W, self.W_opp = lam, W, (W_opp or W)
        # 3-team games: separate denial weights for the team that moves right after us (next) and the other (far)
        self.lam_next = lam if lam_next is None else lam_next
        self.lam_far = lam if lam_far is None else lam_far
        self.jack2, self.jack1 = jack2, jack1
        self.individualist, self.tunnel, self.noise = individualist, tunnel, noise
        self.rng = random.Random(seed)
        self.name = name or "greedy"

    def score_move(self, g, seat, move):
        card, kind, x = move
        t = g.team_of[seat]
        nt = g.n_teams
        opps = [(t + k) % nt for k in range(1, nt)]          # in turn order: opps[0] moves next
        lams = [self.lam] if nt == 2 else [self.lam_next, self.lam_far]
        own_seat = seat if self.individualist else None
        before_t = local_value(g, x, t, self.W, own_seat)
        before_o = [local_value(g, x, o, self.W_opp) for o in opps]
        old = g.cells[x]
        old_owner = g.owner[x]
        bonus = 0.0
        if kind == "remove":
            g.cells[x] = EMPTY
        else:
            g.cells[x] = t
            g.owner[x] = seat
            ns = g.new_sequences(t, x)
            if ns:
                got = min(len(ns), g.seqs_to_win - len(g.seqs[t]))
                bonus += 1e6 if len(g.seqs[t]) + got >= g.seqs_to_win else 2000.0 * got
        after_t = local_value(g, x, t, self.W, own_seat)
        after_o = [local_value(g, x, o, self.W_opp) for o in opps]
        g.cells[x] = old
        g.owner[x] = old_owner
        s = (after_t - before_t) + bonus
        for lm, a, b in zip(lams, after_o, before_o):
            s -= lm * (a - b)
        if kind == "wild":
            s -= self.jack2
        elif kind == "remove":
            s -= self.jack1
        if self.noise:
            s += self.rng.gauss(0, self.noise)
        return s

    def candidate_filter(self, g, seat, moves):
        if not self.tunnel:
            return moves
        mine = [y for y in range(N * N) if g.owner[y] == seat]
        if not mine:
            return moves
        near = set()
        for y in mine:
            for wi in WINDOWS_THROUGH[y]:
                near.update(WINDOWS[wi])
        f = [m for m in moves if m[1] == "remove" or m[2] in near]
        return f or moves

    def choose(self, g, seat, moves):
        moves = self.candidate_filter(g, seat, moves)
        best, bs = None, -1e18
        for m in moves:
            s = self.score_move(g, seat, m)
            if s > bs:
                best, bs = m, s
        return best


class RandomAgent:
    name = "random"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose(self, g, seat, moves):
        return self.rng.choice(moves)


def unseen_multiset(g, seat):
    """Cards whose location is hidden from `seat`: both decks minus own hand minus discards."""
    from collections import Counter
    c = Counter(CARDS * 2)
    c.subtract(g.hands[seat])
    c.subtract(g.discard)
    out = []
    for k, v in c.items():
        out += [k] * max(0, v)
    return out


def clone_game(g):
    h = Game.__new__(Game)
    h.__dict__.update(g.__dict__)
    h.hands = [list(x) for x in g.hands]
    h.deck = list(g.deck)
    h.discard = list(g.discard)
    h.cells = list(g.cells)
    h.owner = list(g.owner)
    h.locked = list(g.locked)
    h.seqs = [list(s) for s in g.seqs]
    h.first_seq_turn = list(g.first_seq_turn)
    h.history = []
    h.rng = random.Random(g.rng.random())
    return h


class MonteCarlo:
    """Hidden-hand sampling + short rollouts. Takes the top-k moves of a Greedy evaluator, then for each
    runs R determinized rollouts of `depth` plies with Greedy policies for all four seats and scores the
    resulting position (win/loss, or static evaluation difference)."""

    def __init__(self, base=None, k=5, R=8, depth=8, seed=None, name="mc", jack_value=60.0, policy=None):
        self.base = base or Greedy(seed=seed)
        self.k, self.R, self.depth = k, R, depth
        self.rng = random.Random(seed)
        self.name = name
        self.policy = policy or Greedy(seed=seed)
        self.jack_value = jack_value   # leaf value of a two-eyed jack still held (option value)

    def choose(self, g, seat, moves):
        scored = sorted(moves, key=lambda m: -self.base.score_move(g, seat, m))
        top = scored[:self.k]
        # immediate win: take it
        if self.base.score_move(g, seat, top[0]) > 5e5:
            return top[0]
        t = g.team_of[seat]
        dets = []
        pool = unseen_multiset(g, seat)
        for _ in range(self.R):
            self.rng.shuffle(pool)
            hands = [None] * g.np
            i = 0
            for q in range(g.np):
                if q == seat:
                    hands[q] = list(g.hands[seat])
                else:
                    hands[q] = pool[i:i + len(g.hands[q])]
                    i += len(g.hands[q])
            dets.append((hands, pool[i:]))
        best, bv = top[0], -1e18
        for m in top:
            v = 0.0
            for hands, deck in dets:
                h = clone_game(g)
                h.hands = [list(x) for x in hands]
                h.deck = list(deck)
                h.rng.shuffle(h.deck)
                h.apply(seat, m)
                for _ in range(self.depth):
                    if h.winner is not None:
                        break
                    s = h.player
                    h.turn_in_dead(s)
                    mv = h.legal_moves(s)
                    if not mv:
                        break
                    h.apply(s, self.policy.choose(h, s, mv))
                if h.winner is not None:
                    v += 1e5 if h.winner == t else -1e5
                else:
                    jt = sum(1 for q in range(h.np) for c in h.hands[q] if c in TWO_EYED and h.team_of[q] == t)
                    jo = sum(1 for q in range(h.np) for c in h.hands[q] if c in TWO_EYED and h.team_of[q] != t)
                    others = [o for o in range(h.n_teams) if o != t]
                    v += (1000 * (len(h.seqs[t]) - max(len(h.seqs[o]) for o in others)) + total_value(h, t, self.base.W)
                          - sum(total_value(h, o, self.base.W) for o in others) + self.jack_value * (jt - jo))
            if v > bv:
                best, bv = m, v
        return best
