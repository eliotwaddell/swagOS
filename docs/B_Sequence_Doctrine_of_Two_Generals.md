# Document B — Sequence: The Doctrine of Two Generals

*A technical analysis and 2v2 tactical guide (plus 2v2v2 in Part II, §11), built on a rules-checked simulator and about 140,000 simulated games.*

---

## 0. Executive summary

| # | Finding | Evidence (2v2, 6 cards each, need 2 sequences) |
|---|---|---|
| 1 | **Spending two-eyed (wild) jacks before they complete a sequence is the most expensive habit we measured.** Hold them to *finish* a five. | Same agent with jacks spent freely: **38.4% ± 1.7%** win vs the jack-holding version (2,000 games). Raising the "jack cost" monotonically improved results up to the point where wild jacks are only used to complete a sequence (cost 100 ≡ 200 ≡ 1000). |
| 2 | **One-eyed (removal) jacks are the opposite: use them.** Hoarding them loses. | One-eyed cost 0 / 30: 49.8% / 48.8% (≈ par). Cost 100 (hoarding): **42.0% ± 1.4%**. |
| 3 | **Play for the *team*, not for your own chips.** | "Individualist" valuation (ignores partner's chips): **41.4% ± 1.7%** vs team valuation. Second-largest single error measured. |
| 4 | **Defense matters, but over-defense also loses.** Optimal denial weight ≈ 0.75–1.0 × your own offense. | Pure offense: 42.8% ± 1.8%. Weight 3.0 (defense-heavy): 46.1% ± 1.8%. Blocking every three hard: **42.0% ± 1.6%**. |
| 5 | **Positional value is the number of five-in-a-row lines through a square.** Center ≫ edges; the corners do *not* make the edge squares good. | Correlation between lines-through-square and how often the square ends up in a completed sequence: **r = 0.96**. Center ring: in a finished sequence 37% of games; outer ring: 4%. |
| 6 | **Hearts in the middle are the best cards in the deck; spades are the worst.** | 4♥ 2♥ 5♥ 3♥ have a center square (≥35% sequence rate). Most spades sit on the rim (≤15%). |
| 7 | **Convex threat valuation (1 : 3 : 9 : 27 for 1-2-3-4 in a line) beat both flatter and steeper scales.** | 53.0% ± 1.7% vs the 1:4:16:80 baseline; 1:8:64:400 → 46.9%; "ignore 1s" → 42.2%. |
| 8 | Combining those principles, the tuned agent beats a "typical human" model **72.0% ± 1.7%** of 2v2 games. | 2,000 games, colors and move order swapped. |

**What did NOT work:** Monte Carlo lookahead (sampling hidden hands + 8-ply greedy rollouts) lost to the tuned one-ply evaluator: **42.0% ± 4.2%** (250 games). The first version, which did not value held jacks at the leaf, lost **30.0% ± 7.4%**. A shallow-horizon search misjudges the long-run option value of a wild jack. We do not claim the tuned agent is optimal, only that it is the strongest policy we found.

---

## 1. Rules baseline (official Jax rules) and house-rule questions

**Baseline we simulated** (verified against published rule summaries; confirm against your box's rulebook):

- 2 decks (104 cards); the board shows each non-Jack card **twice**. 4 corners are free spaces for everyone.
- Hand size by player count: 2→7, 3→6, **4→6**, 6→5, 8–9→4, 10–12→3.
- Two teams of two sit alternately: A1, B1, A2, B2.
- Turn: (optionally discard **one** dead card, meaning both its squares are occupied, and draw a replacement), play a card, place a chip on one of its two squares, draw. If you forget to draw before the next player draws, you lose the draw.
- **Two-eyed jacks (J♦, J♣)**: wild, place on any open square. **One-eyed jacks (J♠, J♥)**: remove one opponent chip, *not* from a completed sequence; you place nothing that turn.
- **Two teams need 2 sequences.** A second sequence may reuse **one** chip of the first, so nine in a row with a shared middle = two sequences. Six in a row ≠ two sequences.
- **No table talk / coaching between partners.**

**House-rule questions that change strategy materially** (ask before the first game):

1. *2 sequences or 1 to win?* With 1, defense value rises sharply (every open four is game-ending) and wild jacks lose some option value (no second sequence to save for).
2. *Can a one-eyed jack remove a chip from a completed sequence?* (Official: no.) If yes, the shared-chip second sequence becomes fragile.
3. *Hand size* (some tables play 7 with 4 players). Bigger hands → more outs → open threes become more dangerous.
4. *Dead-card rule*: one per turn (official) vs any number vs not allowed.
5. *Is "I'm stuck"/sighing considered table talk?* Decide before it matters.
6. *Corner variant* (a team may skip to claim a corner): rare; changes edge value.

---

## 2. The simulator

`sequence/board.py` encodes the real Jax board (validated: 48 distinct non-Jack cards × 2 squares + 4 corners; 192 five-square windows). `sequence/engine.py` implements the rules above. Validation tests are in `sequence/test_engine.py`: sequence detection with corners, the one-shared-chip rule, six-in-a-row ≠ two, chip conservation, random-legal-play games.

**Agents** (`sequence/agents.py`). Each candidate move is scored by the *exact change* in a window-based evaluation:

> value(team) = Σ over five-square windows with no enemy chip of W[k], where k = own chips + free corners in that window
> move score = Δvalue(us) − λ·Δvalue(them) − (jack option cost) + (sequence bonus)

Parameters (λ, W, jack costs) were swept. Human flaws are modeled by perturbing the strong agent:
- *premature jacks*: jack costs = 0
- *threat blindness*: enemy windows of 1–2 chips (or 1–3) valued at 0
- *individualist*: only one's own chips count, not the partner's
- *tunnel vision*: only plays near one's own existing chips
- *noise*: Gaussian jitter on move scores

The **human model** combines premature jacks, threat blindness below 3, individualism, and noise.

**Protocol.** Every match runs N deck seeds × 2 games. The same shuffle is replayed with the hero team moving first, then second, which cancels deal luck and first-move advantage. 95% CIs are computed over seed pairs. Default N = 1,000 seeds (2,000 games).

---

## 3. Board analysis — where to play

### 3.1 Positional value map

Each cell shows `card · % of games (tuned self-play, 6,000 games) in which that square ended up in a completed sequence`. ★ = free corner.

|   | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | ★ | 2S·4 | 3S·5 | 4S·6 | 5S·7 | 6S·6 | 7S·5 | 8S·5 | 9S·4 | ★ |
| 1 | 6C·2 | 5C·6 | 4C·5 | 3C·6 | 2C·9 | AH·8 | KH·6 | QH·6 | TH·8 | TS·3 |
| 2 | 7C·3 | AS·9 | 2D·17 | 3D·19 | 4D·23 | 5D·22 | 6D·16 | 7D·19 | 9H·5 | QS·4 |
| 3 | 8C·4 | KS·11 | 6C·19 | 5C·29 | 4C·30 | 3C·27 | 2C·28 | 8D·17 | 8H·7 | KS·5 |
| 4 | 9C·5 | QS·15 | 7C·24 | 6H·31 | **5H·37** | **4H·38** | AH·26 | 9D·22 | 7H·8 | AS·6 |
| 5 | TC·5 | TS·15 | 8C·23 | 7H·29 | **2H·37** | **3H·35** | KH·28 | TD·20 | 6H·9 | 2D·4 |
| 6 | QC·5 | 9S·13 | 9C·19 | 8H·31 | 9H·30 | TH·28 | QH·27 | QD·17 | 5H·5 | 3D·3 |
| 7 | KC·3 | 8S·8 | TC·18 | QC·19 | KC·23 | AC·22 | AD·18 | KD·14 | 4H·4 | 4D·2 |
| 8 | AC·3 | 7S·11 | 6S·9 | 5S·12 | 4S·13 | 3S·13 | 2S·10 | 2H·5 | 3H·5 | 5D·2 |
| 9 | ★ | AD·3 | KD·4 | QD·4 | TD·5 | 9D·5 | 8D·4 | 7D·3 | 6D·2 | ★ |

**By ring** (ring 0 = outer edge, ring 4 = central 2×2):

| Ring | Lines (windows) through square | % in a completed sequence | Team win rate when holding the square at ply 16 |
|---|---|---|---|
| 0 (edge) | 4–8 | 4% | 44.7% |
| 1 | 6–11 | 9% | 47.0% |
| 2 | 10–14 | 20% | 48.1% |
| 3 | 15–17 | 29% | 51.4% |
| 4 (center) | 20 | 37% | 54.0% |

*Caveats.* (a) "% in sequence" is measured under the agent's own policy, which favors the center, so it partly reflects policy. The window count (purely combinatorial) and the occupancy win rate (a different measure) agree on the ordering. (b) Per-square occupancy win rates have SE ≈ 0.03, so read the ring averages, not individual squares. (c) The slight left/right asymmetry in the map (e.g., column 1 vs column 8) is a tie-breaking artifact of the agent; the board's line structure is symmetric.

**Corners.** The free corner makes four edge windows need only 4 chips, but these squares still rank near the bottom (2–8%). An edge line is easy to see and block, and it connects to almost nothing. Do not chase corner lines early. Take them when they are *free* (you hold the card and nothing better exists) or as the second sequence's anchor.

### 3.2 Card values

Since every card has two squares, a card's value is that of its **better** square.

- **Premium (play/keep for the center):** 4♥, 5♥, 2♥, 3♥ (center 2×2), then 6♥, 7♥, 8♥, 9♥, T♥ and 2♣–6♣ (inner ring).
- **Weakest:** most spades (2♠–9♠ live on rows 0 and 8 / column 1), K♠, A♠, Q♠, K♦.
- *Practical use:* when you hold a weak card whose one decent square is contested, play it early. Hold a premium heart if its center square is still open and the opponents can't take it this round (only 2 copies exist; check the discard pile).

### 3.3 Intersections and multiple threats

The evaluation's convexity (1:3:9:27) is what produces *forks*. A chip that raises two different windows to 3 is worth 2×(9−3) = 12, versus 6 for one. The tuned weights beat both flatter scales (which ignore forks) and steeper ones (which tunnel on one line). Practical translation:

- **Prefer squares that extend two of your lines at once**, especially where a row and a diagonal cross.
- **The winning pattern is a double four:** two open fours that need *different* cards. The opponents can block only one per turn (or two with both their turns before you move again; see turn order below).

---

## 4. Threat arithmetic — how urgent is a threat?

`sequence/analytic.py`. The opponent holds 6 cards drawn from the U cards you can't see (≈ 90 early, ≈ 60 mid-game). **Outs** for an open four = unseen copies of the missing square's card (≤ 2) + unseen two-eyed jacks (≤ 4).

**P(the next opponent can complete)**

| unseen U | 1 out | 2 | 3 | 4 | 5 | 6 outs |
|---|---|---|---|---|---|---|
| 90 | 7% | 13% | 19% | 24% | 30% | 35% |
| 75 | 8% | 15% | 22% | 29% | 35% | 40% |
| 60 | 10% | 19% | 28% | 35% | 42% | 48% |

**P(either opponent can complete before it's blocked)** (12 hidden cards)

| U | 1 | 2 | 3 | 4 | 5 | 6 outs |
|---|---|---|---|---|---|---|
| 90 | 13% | 25% | 35% | 44% | 52% | 59% |
| 75 | 16% | 30% | 41% | 51% | 59% | 66% |
| 60 | 20% | 36% | 49% | 60% | 69% | 75% |

**Reading it:** an enemy open four early in the game with both copies and all wild jacks live is roughly a **coin flip to be completed** before your side moves twice. *Always* block a live open four if you can. Count outs: if both copies of the card are already in the discard pile and the wild jacks are gone, the four is dead and blocking it wastes a turn.

**Turn order (A1 → B1 → A2 → B2).** After you move, the opponent to your left moves before your partner. So:
- An enemy open four that **you** don't block will be completed with the probability in the first table before your partner can respond.
- A threat you create gets **two** enemy turns before you move again, but your partner moves between them. A *double* four you create usually needs both enemies to respond correctly, in order.

---

## 5. Jack doctrine

| Jack | Rule | Evidence |
|---|---|---|
| **Two-eyed (wild)** | **Use only to (1) complete a sequence, or (2) as the last resort against an enemy open four that you can't block with a natural card or a one-eyed jack *and* that has many outs.** Otherwise hold it. | Cost-100 (complete-only) vs cost-30: **+6 pts** (44.0% for cost-30, 2,000 games). Cost 0 vs 12: −2 pts; 25/50/100 vs 12: +1.4 / +2.7 / +3.7 pts. Adding an emergency block of fours with wilds: 48.6% ± 1.5% (no gain). |
| **One-eyed (remove)** | **Use it when it breaks an enemy window of 3–4, or a chip that sits at the intersection of two enemy lines.** Don't hoard. Prefer removing the chip that kills the most enemy windows (usually the center-most chip of their best line). | Hoarding (cost 100): 42.0% ± 1.4%. Costs 0–30 all within ±1.2 pts of par. |

**Why the asymmetry?** A wild jack is a guaranteed *completion* of whatever four you build later. With the card unknown, the probability of completing from your own draws is only what the outs table gives you. That conversion value is larger than any single extension. A removal jack's value is *destroying* something, and the best target usually exists now, while delaying lets the enemy's line grow around it.

**When holding is better than using (two-eyed):** any time the move would only make a 2→3 or 3→4. **Exceptions where you spend it:** it completes sequence #1 or #2; or the enemy has an open four with ≥ 4 outs that nothing else can stop.

**Endgame:** with one sequence made, a held wild jack turns *any* open four of yours into a sure win on your next turn. Build a four that shares the allowed one chip with your first sequence; the opponents must block it immediately.

**Dead cards:** turn in a dead card every turn you have one. It's a free card. (The engine does this automatically.)

---

## 6. Team coordination doctrine (no table talk)

1. **Value your partner's chips exactly as your own.** This is the second-largest effect we measured (−8.6 pts for individualism).
2. **Default: extend the team's strongest line, not your own newest line.** A chip that turns your partner's 3 into a 4 is worth as much as one on your own 3 (Δ 27−9).
3. **Create "either-of-us" finishes.** An open four whose missing card is not in your hand still has your partner as a second chance before your next turn, provided it survives one enemy move. Prefer fours whose completion square's card has *both copies unseen*: more outs for the team.
4. **Read your partner from their placements.** A partner who placed a weak edge card had no better card. A partner who *didn't* block an obvious enemy threat almost certainly lacks the card and a one-eyed jack, so the block is your job this turn. A partner who passed up an obvious completion holds neither the card nor a wild jack: don't wait for them.
5. **Don't duplicate.** If your partner just blocked a line, your block of the same line is wasted. Move to offense.
6. **Signal legally through play order only:** e.g., playing toward a square repeatedly tells your partner "this line is mine to finish." Never verbally.

---

## 7. Defensive emergency protocol

In priority order each turn:

1. **Can we complete a sequence now?** (natural card or wild jack) → do it.
2. **Enemy open four with live outs?** → block with a natural card on the empty square, or **one-eyed jack the most connected chip** in that four. Use a wild jack only if neither is available and outs ≥ 4.
3. **Enemy double three (fork)?** → remove/block the shared square.
4. **Our fork available?** (one chip making two threes, or a three+four) → take it.
5. Otherwise, the best positional placement: center rings first, intersections first, weakest card in hand first when values tie.

**Don't over-block:** pushing defense of single threes too hard cost **8 points** (42.0% ± 1.6%). A lone enemy three far from other enemy chips can wait. An enemy three that intersects another enemy line cannot.

---

## 8. Opening and late game

**Opening (first 2–3 turns each):**
- Play central-ring cards (hearts 2–9, clubs 2–6 inner, diamonds 3–5 row 2) to their inner square.
- Prefer squares adjacent to your partner's chip on a line, ideally a diagonal (diagonals through the center have the most windows).
- Weak spade/edge cards: dump them when you have nothing central; they still have small value as connectors toward a corner.

**Late game (one sequence each or close):**
- Count outs for every live four, ours and theirs.
- A held wild jack + any open four = forced win; make the opponents prove they have the block.
- Removal jacks: aim at the chip that would let the enemy reuse one chip of their first sequence.
- With 2 sequences required, **look for the overlap square**: a second sequence can share exactly one chip with the first. A line crossing your completed sequence at its end is often only 3–4 chips from done.

---

## 9. Human-opponent exploitation

From the flaw experiments (each isolated against the strong agent; 2,000 games each):

| Human habit | Cost to them | How to exploit |
|---|---|---|
| Spends wild jacks early | −11.6 pts (vs tuned) | Expect them to run out; their late-game open fours have only natural-card outs. Make *your* fours with both copies live. |
| Plays for self, not team | −8.6 pts | Their two players build two separate half-lines; block the one closer to four and let the duplication waste their turns. |
| Pure offense | −7.2 pts | Build forks: they won't block threes. |
| Over-defends every three | −8 pts | Spread decoy threes on weak edges; they spend natural cards blocking threats that were never going to finish. |
| Tunnel vision on one line | −4.6 pts | Block that one line early with a single chip at its *center*. A one-eyed jack on their center chip often kills 3–4 of their windows. |
| Hoards one-eyed jacks | −8 pts | Little to do. Just don't assume their removal isn't coming. |

**Against strong opponents** the same doctrine holds (sweeps were against the strong agent). Against weak ones, a slightly more offensive λ (0.75) is fine. Our tests showed λ in [0.75, 1.25] all within noise of each other.

---

## 10. Examples of strong and weak positions

(`A` = ours, `B` = theirs, `.` = empty, `★` = corner; a 7×7 window near the center, rows 2–8, columns 1–7.)

**Strong for A — row four plus diagonal four, sharing (4,4):**
```
      1 2 3 4 5 6 7
 r2   . A . . . . .      diagonal (2,2)(3,3)(4,4)(5,5)(6,6) = A A A . A  -> needs 3♥ at (5,5)
 r3   . . A . . . .
 r4   . A A A A . .      row 4: (4,2..5) = 7♣ 6♥ 5♥ 4♥ -> needs Q♠ at (4,1) or A♥ at (4,6)
 r5   . . . . . . .
 r6   . . . . . A .
```
Three completion squares on three different cards (Q♠, A♥, 3♥), each with 2 copies, plus 4 wild jacks: up to 10 outs, and B blocks one square per turn. The two lines share only (4,4), so completing both is legal: **two sequences.**

**Weak for A — edge line with a dead square:**
```
 r0   ★ A A A . . . . . ★     needs 5♠ at (0,4); if both 5♠ are discarded and the wild jacks are gone, it is dead.
```
Looks threatening; isn't. Check the discard pile before spending defense on it.

---

## 11. Part II — 2v2v2 (three teams of two)

### 11.1 Rules and setup
6 players seated A-B-C-A-B-C, 5 cards each. **Your table plays TWO sequences to win** (the printed rule for 3 teams is one; both were simulated, and the two-sequence results come first). A second sequence may share one chip with the first, as in 2v2. Jacks, corners, dead cards and no table talk are unchanged. The engine takes `n_teams=3, seqs_to_win=…` and passes its own rule tests; the 2v2 results reproduce exactly after the refactor.

**Protocol.** Every shuffle is played 3 times, with the hero team in seating slot 1, 2 and 3; two villain teams fill the other slots. **Par = 33.3%.** 1,000 shuffles = 3,000 games per comparison; CIs over shuffles. Opponents are the best 2v2 agent (line weights 1:3:9:27, denial 0.75, wild jacks only to complete) unless noted.
`SEQS=2 python -m sequence.three_team 1000 all` · `SEQS=2 python -m sequence.positional 3000 3` (omit `SEQS=2` for one sequence).

### 11.2 Headline results — TWO sequences (your rule)

Games average ~72 placements (≈12 turns per player), twice as long as one-sequence games.

| Change (vs a field of the 2v2-tuned agent) | Hero win rate (par 33.3%) |
|---|---|
| **2v2 doctrine as-is** (1:3:9:27, denial 0.5–0.75, wild jacks only to complete) | **par: no variant beat it** |
| Same agent vs a field of human-model teams | **56.4% ± 1.7** |
| Human model vs 2v2-tuned teams | 16.6% ± 1.3 |
| **Wild jacks spent freely** | **23.2% ± 1.4** (cost 0 alone: 24.8%; cost 12: 26.9%; cost 30: 30.8%) |
| One-eyed jacks hoarded (cost 100) | 27.0% ± 1.3 (using them freely: 31.3–32.9%, ≈ par) |
| **Individualist (ignores partner's chips)** | **24.0% ± 1.4** |
| Tunnel vision | 27.5% ± 1.4 |
| **Hard-block every enemy four** | **28.6% ± 1.4** (neutral with one sequence; costly with two) |
| Hard-block every three and four | 25.0% ± 1.4 |
| Line weights 1:2:4:8 / 1:4:16:80 / 1:5:25:125 | 28.1% / 30.7% / 28.6% (tripling stays best) |

**Denial weight λ vs both opponents (two sequences):**

| λ | 0 | 0.25 | 0.5 | 0.75 (tuned) | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|---|---|---|
| Win % | 31.1 | 34.0 | 33.5 | 33.3 | 31.3 | 28.9 | 26.4 |

The flat top (0.25–0.75) means a moderate-to-light defense is right; heavy defense clearly loses.

**Seat order (mirror match):** the team moving **first wins 41%**, second and third **30%** each. That's a bigger first-mover edge than with one sequence (36/32/31). Rotate who starts.

### 11.3 What's different from 2v2 — and from one-sequence 2v2v2

1. **Defense is a shared burden.** Your block helps the third team as much as you. Heavy defense costs 7 points (26.4%).
2. **Don't panic-block every enemy four.** With two sequences to win, an enemy's *first* sequence doesn't end the game. A block that costs you a good move often just delays them while the third team profits. Hard-blocking all fours: **28.6%** (vs 34.4% with one sequence). **Block a four when it would be that team's SECOND sequence (game-ending), or when blocking also builds your own line.** Otherwise keep building.
3. **Defend against whoever is closest to winning.** Splitting defense by turn order mostly changes *which* opponent wins (next team 23.6% vs far team 42.9% when you ignore the far team), not your own rate (32.4–33.4%).
4. **Jacks: identical doctrine.** Wild only to complete (each step toward free use costs you); one-eyed used freely, not hoarded.
5. **Partner's chips = yours** (24.0% if ignored).

### 11.4 Threat arithmetic with 5-card hands

| Unseen cards U | 1 out | 2 | 3 | 4 | 5 | 6 outs |
|---|---|---|---|---|---|---|
| **One specific enemy can complete**: U=95 | 5% | 10% | 15% | 20% | 24% | 28% |
| U=65 | 8% | 15% | 22% | 28% | 34% | 39% |
| **Either of the 2 enemies moving before your partner**: U=95 | 11% | 20% | 29% | 36% | 43% | 50% |
| U=65 | 15% | 29% | 40% | 50% | 58% | 65% |
| **Any of the 4 enemy turns before your own next turn**: U=95 | 21% | 38% | 51% | 62% | 70% | 77% |
| U=65 | 31% | 52% | 68% | 78% | 85% | 90% |

Turn order A1 → B1 → C1 → A2 → B2 → C2: **two enemy turns pass between you and your partner, four before you move again.** A *game-ending* four (a team's second sequence) with 3+ outs left for a round is completed more often than not. Block those. A team's *first* four is the one you may let the other team deal with: the team moving between you and them has its own reasons to block.

### 11.5 Board value in 2v2v2 (two sequences, 3,000 games)

| Ring | % in a winning team's sequence | Team win rate when holding the square at ply 16 |
|---|---|---|
| 0 (edge) | 10.7% | 34.3% |
| 1 | 12.2% | 33.4% |
| 2 | 20.1% | 33.3% |
| 3 | 24.5% | 33.4% |
| 4 (center) | 30.5% | 33.9% |

Lines-through-square still predicts which squares end up in sequences (r = 0.94). But **holding the center early doesn't predict winning**: every ring is 33–34%, which is par. With six players crowding the middle, central lines get blocked from all directions. Edges carry much more of the winning lines than in 2v2 (11% vs 4%), and second sequences in particular often run along the outside or through a corner. **Practical shift: choose the square with the most still-open lines through it, even off-center.** For your second sequence, look outward from the first one, including toward corners.

### 11.6 Two-sequence 2v2v2 doctrine (differences from 2v2 in bold)

1. Can we complete a sequence now? → do it, wild jack allowed.
2. **Enemy four that would be their SECOND (game-ending) sequence?** → block it: natural card → one-eyed jack on its best chip → wild jack if many outs.
3. **Enemy four that would only be their FIRST sequence?** → block it only if the block also builds our line or nothing better exists. Otherwise build.
4. **Skip blocking threes** unless they cross another enemy line.
5. Forks and team lines, toward **open** space (corners count for the second sequence).
6. Wild jacks only to complete. One-eyed jacks: use them. Partner's chips = yours.

### 11.7 If you ever play ONE sequence to win (printed 3-team rule)

3,000 games per row. Recommended agent (1:4:16:80, λ 0.5): 35.6% vs the 2v2-tuned field, 52.0% vs human-model teams. Seat 36/32/31%. Heavy defense λ 2: 26.3%. Wild jacks spent freely: 23.3%. Individualist: 22.0%. **Hard-blocking every enemy four is fine here (34.4%)**, because every four is game-ending. Blocking threes hard: 28.6%. Early center occupancy also doesn't predict winning (33–35% per ring). Raw data: `results/sequence3_log.txt`, `results/sequence3_v2_log.txt`.

---

## 12. Reproduce

```
python -m sequence.test_engine          # rules validation
python -m sequence.run_all 1000 ladder  # baseline + human flaws
python -m sequence.run_all 1000 sweep   # lambda, jack costs, window weights
python -m sequence.run_all 1000 human
python -m sequence.run_v2 1000          # tuned agent, Monte Carlo v2
python -m sequence.run_v3 1000          # jack doctrine details
python -m sequence.positional 6000      # heatmaps
python -m sequence.analytic             # threat odds
```
Raw outputs: `results/sequence_*.json`, logs in `results/sequence_*log.txt`.
