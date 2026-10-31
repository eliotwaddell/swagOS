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
        assert placed - removed == sum(1 for x in g.cells if x in (0, 1))
    wins = [0, 0, 0]
    for s in range(40):
        g = play_game([Greedy(seed=s), RandomAgent(s), Greedy(seed=s + 9), RandomAgent(s + 1)], random.Random(s))
        wins[2 if g.winner is None else g.winner] += 1
    assert wins[0] > wins[1], wins

if __name__ == "__main__":
    validate(); test_sequences(); test_games(); print("all Sequence engine tests passed")
