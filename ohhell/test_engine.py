"""Rule-validation tests for the Oh Hell engine (run: python -m ohhell.test_engine)."""
import random
from .engine import *
from .agents import Agent

def test_winner():
    T = parse
    assert trick_winner([(0, T("2H")), (1, T("AH")), (2, T("3S"))], trump=None) == 1
    assert trick_winner([(0, T("2H")), (1, T("AH")), (2, T("3S"))], trump=3) == 2   # spade trump
    assert trick_winner([(0, T("2H")), (1, T("AD")), (2, T("3H"))], trump=None) == 2  # off-suit ace loses
    assert trick_winner([(0, T("2H")), (1, T("4S")), (2, T("KS"))], trump=3) == 2

def test_follow():
    T = parse
    assert legal_moves([T("2H"), T("AS")], 2) == [T("2H")]
    assert set(legal_moves([T("2D"), T("AS")], 2)) == {T("2D"), T("AS")}

def test_hook_and_games():
    rng = random.Random(1)
    for pl in ["random", "greedy", "heur", "heur_notrack"]:
        for b in ["random", "naive", "thumb"]:
            ags = [Agent(b, pl, seed=i) for i in range(4)]
            log = []
            play_game(ags, rng, log=log)
            for r in log:
                assert sum(r["bids"]) != r["h"], "hook violated"
                assert sum(r["won"]) == r["h"]
                for i in range(4):
                    assert r["pts"][i] == (10 + r["bids"][i] if r["bids"][i] == r["won"][i] else 0)
            assert len(log) == 19

def test_no_trump_full_deal():
    st = RoundState(4, 13, 0, random.Random(0))
    assert st.trump is None and st.upcard is None

if __name__ == "__main__":
    test_winner(); test_follow(); test_hook_and_games(); test_no_trump_full_deal()
    print("all Oh Hell engine tests passed")
