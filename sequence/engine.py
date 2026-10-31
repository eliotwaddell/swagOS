"""Sequence engine, official Jax rules for 2 or 3 teams (3 teams: 6 players A,B,C,A,B,C, 5 cards, 1 sequence wins):
 * 4 players, seats alternate teams (A,B,A,B); 6 cards each; two 52-card decks (104 cards).
 * Turn: (optionally turn in ONE dead card and draw a replacement), play a card, place/remove chip, draw.
 * Two-eyed jacks (JD, JC): place a chip on any empty space. One-eyed jacks (JS, JH): remove one
   opponent chip that is not part of a completed sequence (you do not place a chip that turn).
 * Corners are free spaces counting for every team.
 * 2 teams need 2 sequences. A second sequence may share at most one space with the first.
 * Deck exhausted -> discard pile reshuffled (house convention; rarely triggered). Turn cap -> draw.
"""
import random
from .board import BOARD, POS, WINDOWS, WINDOWS_THROUGH, CORNER_IDX, CARDS, TWO_EYED, ONE_EYED, N

EMPTY, CORNER = -1, 9


class Game:
    def __init__(self, rng, n_players=4, hand_size=None, seqs_to_win=None, n_teams=2):
        self.rng = rng
        self.np = n_players
        assert n_players % n_teams == 0
        self.n_teams = n_teams
        self.team_of = [i % n_teams for i in range(n_players)]
        if seqs_to_win is None:
            seqs_to_win = 2 if n_teams == 2 else 1   # official: 2 teams need 2, 3 teams need 1
        hs = hand_size or {2: 7, 3: 6, 4: 6, 6: 5, 8: 4, 9: 4, 10: 3, 12: 3}[n_players]
        self.deck = CARDS * 2
        rng.shuffle(self.deck)
        self.hands = [[self.deck.pop() for _ in range(hs)] for _ in range(n_players)]
        self.discard = []
        self.cells = [EMPTY] * (N * N)
        self.owner = [-1] * (N * N)          # seat that placed the chip (for analysis only)
        for x in CORNER_IDX:
            self.cells[x] = CORNER
        self.locked = [False] * (N * N)
        self.seqs = [[] for _ in range(n_teams)]                 # list of frozenset windows per team
        self.seqs_to_win = seqs_to_win
        self.turn = 0
        self.player = 0
        self.winner = None
        self.history = []                    # (seat, card, kind, cell)
        self.first_seq_turn = [None] * n_teams

    # ---------------------------------------------------------------- queries
    def is_dead(self, card):
        if card[0] == "J":
            return False
        return all(self.cells[x] != EMPTY for x in POS[card])

    def legal_moves(self, seat, hand=None):
        """List of (card, kind, cell). kind in {'place','wild','remove'}."""
        hand = self.hands[seat] if hand is None else hand
        t = self.team_of[seat]
        mv = []
        seen = set()
        for card in hand:
            if card in seen:
                continue
            seen.add(card)
            if card in TWO_EYED:
                for x in range(N * N):
                    if self.cells[x] == EMPTY:
                        mv.append((card, "wild", x))
            elif card in ONE_EYED:
                for x in range(N * N):
                    v = self.cells[x]
                    if 0 <= v < self.n_teams and v != t and not self.locked[x]:
                        mv.append((card, "remove", x))
            else:
                for x in POS[card]:
                    if self.cells[x] == EMPTY:
                        mv.append((card, "place", x))
        return mv

    # ---------------------------------------------------------------- mechanics
    def draw(self):
        if not self.deck:
            if not self.discard:
                return None
            self.deck = self.discard
            self.discard = []
            self.rng.shuffle(self.deck)
        return self.deck.pop()

    def turn_in_dead(self, seat):
        for card in self.hands[seat]:
            if self.is_dead(card):
                self.hands[seat].remove(card)
                self.discard.append(card)
                c = self.draw()
                if c is not None:
                    self.hands[seat].append(c)
                return card
        return None

    def new_sequences(self, t, x):
        """Windows through x that are complete for team t and legal as new sequences."""
        found = []
        for wi in WINDOWS_THROUGH[x]:
            w = WINDOWS[wi]
            if all(self.cells[y] == t or self.cells[y] == CORNER for y in w):
                ws = frozenset(w)
                if all(len(ws & s) <= 1 for s in self.seqs[t] + found):
                    found.append(ws)
        return found

    def apply(self, seat, move):
        card, kind, x = move
        t = self.team_of[seat]
        assert seat == self.player and self.winner is None
        assert card in self.hands[seat]
        if kind == "remove":
            v = self.cells[x]
            assert card in ONE_EYED and 0 <= v < self.n_teams and v != t and not self.locked[x]
            self.cells[x] = EMPTY
            self.owner[x] = -1
        else:
            assert self.cells[x] == EMPTY
            assert (kind == "wild" and card in TWO_EYED) or (kind == "place" and x in POS[card])
            self.cells[x] = t
            self.owner[x] = seat
            for s in self.new_sequences(t, x):
                if len(self.seqs[t]) >= self.seqs_to_win:
                    break
                self.seqs[t].append(s)
                for y in s:
                    self.locked[y] = True
                if self.first_seq_turn[t] is None:
                    self.first_seq_turn[t] = self.turn
            if len(self.seqs[t]) >= self.seqs_to_win:
                self.winner = t
        self.hands[seat].remove(card)
        self.discard.append(card)
        c = self.draw()
        if c is not None:
            self.hands[seat].append(c)
        self.history.append((seat, card, kind, x))
        self.turn += 1
        self.player = (self.player + 1) % self.np


def play_game(agents, rng, max_turns=400, observer=None, n_teams=2, seqs_to_win=None):
    g = Game(rng, n_players=len(agents), n_teams=n_teams, seqs_to_win=seqs_to_win)
    for a in agents:
        if hasattr(a, "reset"):
            a.reset()
    while g.winner is None and g.turn < max_turns:
        s = g.player
        g.turn_in_dead(s)
        mv = g.legal_moves(s)
        if not mv:                       # only possible with an all-one-eyed hand and no targets
            card = g.hands[s][0]
            g.hands[s].remove(card); g.discard.append(card)
            c = g.draw()
            if c is not None:
                g.hands[s].append(c)
            g.turn += 1; g.player = (s + 1) % g.np
            continue
        m = agents[s].choose(g, s, mv)
        g.apply(s, m)
        if observer:
            observer(g)
    return g
