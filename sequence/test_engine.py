"""Rule validation for the Sequence engine: python -m sequence.test_engine"""
import random
from .board import validate, POS, N
from .engine import Game, play_game, EMPTY, CORNER
from .agents import RandomAgent, Greedy

def rc(r, c): return r * N + c

def test_sequences():
    g = Game(random.Random(0))
    # row 0: corner + 4 chips -> sequence using the corner
    for c in range(1, 5):
        g.cells[rc(0, c)] = 0
    assert len(g.new_sequences(0, rc(0, 4))) == 1
    # a second sequence sharing exactly one chip is legal; sharing two is not
    g.seqs[0].append(frozenset([rc(0, c) for c in range(0, 5)]))
    for r in range(1, 5):
        g.cells[rc(r, 4)] = 0          # vertical through (0,4): shares 1 chip
    assert len(g.new_sequences(0, rc(4, 4))) == 1
    g2 = Game(random.Random(0))
    for c in range(0, 6): g2.cells[rc(5, c)] = 1
    g2.seqs[1].append(frozenset(rc(5, c) for c in range(0, 5)))
    assert g2.new_sequences(1, rc(5, 5)) == []   # 6 in a row is not two sequences
    for c in range(6, 9): g2.cells[rc(5, c)] = 1
    assert len(g2.new_sequences(1, rc(5, 8))) == 1  # 9 in a row = two (shared middle)

def test_games():
    for s in range(20):
        g = play_game([RandomAgent(s), RandomAgent(s + 1), RandomAgent(s + 2), RandomAgent(s + 3)], random.Random(s))
        assert sum(1 for x in g.cells if x == CORNER) == 4
        # chip conservation: every non-remove move placed a chip; removes took one
        placed = sum(1 for h in g.history if h[2] != "remove")
        removed = sum(1 for h in g.history if h[2] == "remove")
        assert placed - removed == sum(1 for x in g.cells if 0 <= x < 3)
    wins = [0, 0, 0]
    for s in range(40):
        g = play_game([Greedy(seed=s), RandomAgent(s), Greedy(seed=s + 9), RandomAgent(s + 1)], random.Random(s))
        wins[2 if g.winner is None else g.winner] += 1
    assert wins[0] > wins[1], wins

def test_three_teams():
    g = Game(random.Random(0), n_players=6, n_teams=3)
    assert g.seqs_to_win == 1 and all(len(h) == 5 for h in g.hands) and g.team_of == [0, 1, 2, 0, 1, 2]
    wins = [0, 0, 0, 0]
    for s in range(30):
        g = play_game([RandomAgent(s * 6 + i) for i in range(6)], random.Random(s), n_teams=3)
        for t in range(3):
            for sq in g.seqs[t]:
                assert all(g.cells[y] in (t, CORNER) for y in sq)
        if g.winner is not None:
            assert len(g.seqs[g.winner]) == 1
        wins[3 if g.winner is None else g.winner] += 1
        placed = sum(1 for h in g.history if h[2] != "remove")
        removed = sum(1 for h in g.history if h[2] == "remove")
        assert placed - removed == sum(1 for x in g.cells if 0 <= x < 3)
    # greedy team 0 vs two random teams should dominate
    w = [0, 0, 0, 0]
    for s in range(30):
        ags = [Greedy(seed=s * 6 + i) if i % 3 == 0 else RandomAgent(s * 6 + i) for i in range(6)]
        g = play_game(ags, random.Random(s), n_teams=3)
        w[3 if g.winner is None else g.winner] += 1
    assert w[0] > 20, w

if __name__ == "__main__":
    validate(); test_sequences(); test_games(); test_three_teams(); print("all Sequence engine tests passed")
