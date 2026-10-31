"""The standard Jax Sequence board (10x10). 'XX' = free corner. Each non-Jack card appears twice."""
from collections import Counter

LAYOUT = """
XX 2S 3S 4S 5S 6S 7S 8S 9S XX
6C 5C 4C 3C 2C AH KH QH TH TS
7C AS 2D 3D 4D 5D 6D 7D 9H QS
8C KS 6C 5C 4C 3C 2C 8D 8H KS
9C QS 7C 6H 5H 4H AH 9D 7H AS
TC TS 8C 7H 2H 3H KH TD 6H 2D
QC 9S 9C 8H 9H TH QH QD 5H 3D
KC 8S TC QC KC AC AD KD 4H 4D
AC 7S 6S 5S 4S 3S 2S 2H 3H 5D
XX AD KD QD TD 9D 8D 7D 6D XX
"""
BOARD = [row.split() for row in LAYOUT.strip().splitlines()]
N = 10
CORNERS = {(0, 0), (0, 9), (9, 0), (9, 9)}
RANKS = "23456789TJQKA"
SUITS = "CDHS"
CARDS = [r + s for s in SUITS for r in RANKS]               # 52 card names
TWO_EYED = {"JD", "JC"}     # wild: place anywhere empty
ONE_EYED = {"JS", "JH"}     # remove an opponent chip (not in a completed sequence)

POS = {}
for r in range(N):
    for c in range(N):
        if BOARD[r][c] != "XX":
            POS.setdefault(BOARD[r][c], []).append(r * N + c)

# all 5-windows (lines) on the board, as tuples of cell indices
WINDOWS = []
for r in range(N):
    for c in range(N):
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            cells = [(r + k * dr, c + k * dc) for k in range(5)]
            if all(0 <= a < N and 0 <= b < N for a, b in cells):
                WINDOWS.append(tuple(a * N + b for a, b in cells))
WINDOWS_THROUGH = [[] for _ in range(N * N)]
for wi, w in enumerate(WINDOWS):
    for x in w:
        WINDOWS_THROUGH[x].append(wi)
CORNER_IDX = {r * N + c for r, c in CORNERS}


def validate():
    cnt = Counter(x for row in BOARD for x in row)
    assert cnt["XX"] == 4
    for card in CARDS:
        if card[0] == "J":
            assert cnt[card] == 0, card
        else:
            assert cnt[card] == 2, (card, cnt[card])
    assert len(WINDOWS) == 192
    return True


if __name__ == "__main__":
    validate()
    print("board OK: 48 cards x2 + 4 corners; windows:", len(WINDOWS))
