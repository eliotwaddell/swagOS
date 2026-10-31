# Document A — Oh Hell: The Art of Exact Victory

*A technical analysis and field manual, built on a rules-checked simulator and about 60,000 simulated 19-hand games.*

---

## 0. Executive summary

All numbers are 4-player games (hands 10→1→10, 19 deals), standard scoring (exact bid = 10 + bid, miss = 0), hook rule on. The hero is played against 3 copies of a *club player* model: rule-of-thumb bidding (Aces, trump honors, length) plus sensible need-aware card play. Par win rate = 25%.

| Hero strategy | Win rate (95% CI) | Points/game vs avg opponent | Exact-bid rate |
|---|---|---|---|
| Random | 0.3% ± 0.3 | −54.4 | 19% |
| **"Trick hog"** (counts every A/K, always plays to win) | **2.9% ± 0.9** | −33.9 | 34% |
| Same bids, but plays *to the bid* | 33.6% ± 2.2 | +6.6 | 50% |
| Club player (mirror) | 25.0% | 0 | 47% |
| **Mental count (this manual)** + need-aware play | **49.4% ± 2.7** | +19.2 ± 1.4 | 55% |
| Calibrated linear bidder + need-aware play | 55.0% ± 2.8 | +23.8 ± 1.6 | 57% |
| Monte Carlo bidder + need-aware play | 63.0% ± 2.7 | +28.9 ± 1.5 | 59% |
| Club bidding + PIMC (simulation) card play | 51.2% ± 2.4 | +20.4 ± 1.1 | 54% |
| **Monte Carlo bidder + PIMC card play** | **81.8% ± 2.4** | **+45.2 ± 1.6** | **64%** |

(1,200 games per row = 300 deal sets × hero rotated through all 4 seats on the same deals.)

**The five findings that matter:**

1. **Playing to your bid instead of to win tricks is worth ≈ 40 points/game.** Same (bad) bids: trick-hog play 2.9% wins, need-aware play 33.6%. Every trick you take beyond your bid is a disaster, not a bonus.
2. **Bid accuracy is the biggest skill lever after that.** Fixing club players' systematic *underbidding* (−0.69 tricks/hand on average) is worth +24 points/game. A 20-second mental count captures ~80% of it.
3. **Errors are asymmetric: bidding one too many costs 4× as much as one too few.** Calibrated bidder shifted +1: −14.6 pts/game (12.7% wins). Shifted −1: −3.7 pts/game (19.9%). *When torn between two bids, take the lower.*
4. **Zero is the highest-EV bid when it's plausible.** Monte Carlo-chosen zero bids succeed 76% (EV 7.6) vs 59% for 1 (EV 6.5), 52% for 2 (EV 6.2), 44% for 3 (EV 5.7).
5. **Simulation-quality card play (inference of voids + "what happens if I play this?") adds another +16–20 pts/game** on top of good bidding. Section 4 compresses what it does into rules.

**What did not matter (measured, null):** remembering which cards are masters *inside a simple heuristic* (Δ ≈ 0); cashing side masters vs trump masters first (Δ ≈ 0); void-making discards vs lowest discards (Δ ≈ 0). These are not useless in general, but they did not change results at this level. The gains came from the bid, from ducking correctly, and from committing honors when you need tricks.

---

## 1. Rules baseline and house-rule questions

**Baseline** (Pagat, "Oh Hell"):
- 3–7 players (4–6 best); individual scoring; 52 cards, A high.
- Hand sizes: 10 cards with 3–5 players (8 with 6, 7 with 7), *down* by one to 1, then back *up*.
- After the deal the next card is turned up; its suit is trump. If the deck is exhausted, there is no trump.
- Bidding: left of dealer first, dealer last. Zero allowed, no passing. **Hook: dealer may not make total bids = tricks**, so every hand is over- or under-bid.
- Must follow suit; otherwise any card. Highest trump wins, else highest of the suit led. The winner leads.
- Score: exact = 10 + bid; miss = 0. (Common variant: 1/trick + 10 bonus for exact.)

**House-rule questions that materially change strategy:**

1. **Scoring for misses.** Zero (baseline, and **your table's rule**: exact = 10 + bid, miss = 0) vs negative per trick off. Negative scoring makes underbidding and zero bids much better and bold bids worse.
2. **Is the hook on?** With no hook the dealer's edge disappears and totals can be exact. That makes contested hands rarer and slightly overbidding safer.
3. **Exact zero worth 10 or 5?** At 5, the zero-bid advantage (finding 4) disappears; bid 1 on marginal hands instead.
4. **Hand pattern** (10→1→10, 1→10→1, or only up). **Your table plays 1→7→1: see §8.** It doesn't change per-hand play, but more big hands means more variance and more value from card play.
5. **Trump rotation / fixed trump / no-trump hands.** Our mental count assumes a turned-up trump.
6. **Must-trump rule** (must ruff if void). It removes the ducking-by-discard option, so zero bids get harder.
7. **Bid changes / simultaneous bidding.** Simultaneous bidding removes the position effects in §2.4.

---

## 2. The simulator and how strategies were tested

- `ohhell/engine.py` — rules engine, validated by `ohhell/test_engine.py` (trick winner with/without trump, follow-suit enforcement, hook enforcement on every hand, score formula, no-trump on full deals).
- `ohhell/agents.py` — bidders × players:
  - **Bidders:** random; *naive* (every A and K + trump J+ = a trick; typical overcounter); *thumb* (club rule: A=1, trump K=1, trump Q with 3+ trumps=1, guarded side K=½, each trump beyond 3 = 1); *calibrated* (linear model per hand size fitted by simulation); **Monte Carlo** (for each candidate bid, 40 sampled deals; opponents' actual bids are used and later bidders' bids are estimated; the hand is played out and the bid with max E[score] is chosen); **mental** (§3.1).
  - **Players:** random; *greedy* (always try to win); **need-aware heuristic** (§4); *no-tracking* variant; **PIMC** (perfect-information Monte Carlo: for each legal card, sample 16 deals consistent with known voids, roll out with need-aware play, and pick the best average outcome).
- **Protocol:** each deal set is played 4 times with the hero in each seat, which removes card luck. CIs are 1.96 × SE over deal sets.
- **Limits:** PIMC has known weaknesses ("strategy fusion": it assumes it will know everything later). Opponent hands are sampled uniformly, without conditioning on their bids. The heuristic opponents are a *model* of club players; real humans are noisier. So treat absolute win rates as illustrative and the *rankings and gaps* as the findings.

### 2.1 How hard is exactness? (Monte Carlo bidder, 7,600 hands)

| Hand size | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Exact rate | 77% | 70% | 66% | 60% | 60% | 60% | 53% | 54% | 51% | 49% |

| Bid | 0 | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|
| Exact rate | 76% | 59% | 52% | 44% | 42% | 39% |
| EV (10+b)·P | 7.6 | 6.5 | 6.2 | 5.7 | 5.9 | ≈ 5.8 |

When the Monte Carlo bidder misses, it is more often *over* (took extra tricks: 28% of hands) than *under* (13%). Extra tricks are forced on you; missing tricks you can usually fight for. **That is the mechanism behind "when in doubt, bid lower."**

### 2.2 Bias of common bidding styles

| Bidder | Mean (bid − tricks) | Exact | Over-bid misses | Under-bid misses |
|---|---|---|---|---|
| Club rule of thumb | −0.69 | 46.5% | 5% | 49% |
| Naive "count high cards" | −0.48 | 49.4% | 10% | 40% |
| Calibrated | −0.28 | 56.9% | 12% | 31% |
| Monte Carlo | −0.21 | 59.0% | 13% | 28% |

The common club rule *underbids*, mainly because it ignores how many tricks **small trumps** take (each trump ≈ ¾ trick in mid-size hands, regardless of rank). The "overcounter" is less biased than you'd think because it also ignores trump length. Its real disaster is trick-hog play (finding 1).

### 2.3 What do cards win? (bids of the Monte Carlo bidder regressed on hand features, 4 players)

| Feature | Hands 1–2 | 3–5 | 6–8 | 9–10 |
|---|---|---|---|---|
| Each trump (any rank) | 0.64 | 0.72 | 0.72 | 0.77 |
| + trump A (extra) | +0.24 | +0.56 | +0.78 | +0.84 |
| + trump K (extra) | +0.22 | +0.42 | +0.58 | +0.62 |
| + trump Q (extra) | +0.27 | +0.34 | +0.49 | +0.56 |
| + trump J (extra) | +0.12 | +0.30 | +0.38 | +0.47 |
| Side Ace | 0.06 | 0.48 | 0.73 | 0.78 |
| Side King | ≈0 | 0.26–0.31 | 0.40–0.47 | 0.37–0.55 |
| Side Queen | ≈0 | 0.18 | 0.32 | 0.34 |
| Constant | +0.08 | −0.14 | −0.38 | −0.82 |
| Per trick the earlier bids exceed "fair share" | +0.12 | −0.11 | −0.18 | −0.23 |

Lessons:
- **In 1–2 card hands, only trumps count.** A side Ace with 1 card wins about 40% of the time even when you lead it (someone usually holds a trump).
- **Long trumps are tricks**: 5 small trumps in a 10-card hand bid 3 (worked example 2).
- **Side Aces are only ~¾ of a trick**, even in big hands (they get ruffed).
- **When earlier bidders have bid a lot, shade down.** Contested hands lower everyone's exact rate (60% when underbid in total → 49% when overbid in total).

### 2.4 Seat effects (exact rate by bidding position, Monte Carlo bidder)

First bidder 56.9%, second 58.7%, **third 62.5%**, dealer 58.0% (≈ ±2.2% each). The third seat has most of the information and no hook. The dealer has full information but is sometimes forced off the best bid by the hook. A dealer forced off the best number should usually go *down* if that's legal (finding 3), unless going down means a hopeless zero.

---

## 3. Bidding

### 3.1 The 20-second mental count (4 players; validated at 3 and 5)

Count in quarters:

| Card | Hands of 1–2 | Hands of 3–5 | Hands of 6–10 |
|---|---|---|---|
| **Any trump** | ¾ | ¾ | ¾ |
| Trump **A** / **K** / **Q** (on top of the ¾) | — | +¾ / +½ / +¼ | +¾ / +½ / +¼ |
| **Side Ace** | 0 | ½ | ¾ |
| **Side King** | 0 | 0 | ½ |
| Everything else | 0 | 0 | 0 |
| **Adjustment** | — | — | −½ for 6–8 cards, −1 for 9–10 cards |

Then: **if the bids already made exceed the fair share** (tricks × bidders-so-far ÷ players) by 1 or more, subtract ¼ per extra trick. **Round to nearest, with x.5 rounding UP.** The −½/−1 big-hand adjustment already builds in the caution. Rounding x.5 down tested *worse*: 45.0% vs 48.4% wins at 4 players, 51.1% vs 56.5% at 3 (2,400 / 1,800 games); a wash at 5. If you're the dealer and hooked, move down unless that means a zero you can't survive.

**Validation:** this rule vs club field: **49.4% ± 2.7** wins (1,200 games), vs 25% par. At 3 players: 57.2% vs 33% par. At 5 players: 37.3% vs 20% par. It matches the Monte Carlo bid exactly 60% of the time and within one trick 95%. Against a field of calibrated bidders it is about break-even (22.6% ± 2.0, −1.8 pts), so it captures most but not all of the computer's bidding edge.

### 3.2 Rapid bidding decision tree

```
1. Hand of 1–2 cards?
   - Count trumps only. A trump A/K → bid 1. Any other single trump → bid 1 if you lead or are near the lead, else 0.
   - Side cards only → 0 (even a side Ace).
2. Otherwise: run the mental count (3.1) → X.
3. Contest check: earlier bids already ≥ the fair share + 1? → shade down (count does this).
4. Round (x.5 up). If your gut disagrees with the count, the gut's tie goes to the LOWER bid.
5. Is 0 within ½ of X and you hold no trump honor and ≤1 trump? → bid 0 (EV leader).
6. Dealer & hooked? → move down if legal and survivable; else up.
```

### 3.3 Why max expected tricks ≠ max expected score

Score is (10 + b)·P(exact = b). The +b part is small next to the 10, so **you are maximizing P(exact)**, not tricks. The best bid is the *mode* of your trick distribution, not the mean. Your control is also asymmetric: you can usually *lose* a trick you planned to win (discard, duck) more easily than you can shed one you didn't want. So choose the lower of two near-equal modes.

---

## 4. Card play

### 4.1 Trick-taking decision tree (need = bid − tricks won)

```
FOLLOWING (someone has led):
  need > 0 (want tricks):
     Can win safely (last to play, or a master that nobody after you can ruff)? -> win with the CHEAPEST safe winner.
     Need every remaining trick? -> play your biggest winner.
     Otherwise, holding a winner that is an honor (Q+) or a trump? -> play it now (committing beats ducking: +10 pts/game).
     Can't win -> throw your lowest side card (keep trumps).
  need <= 0 (made it, or bid 0):
     Have a card that LOSES to the current winner? -> play the HIGHEST such card
          (shed danger while it's free: +5.4 pts/game vs keeping it).
     Every card wins? -> if last: win with your HIGHEST card (unload it); if not last: play the LOWEST (hope to be overtaken).
LEADING:
  need > 0: lead a master (top trump first if you hold 2+ trumps); with no master, lead low from a short side suit when you hold trumps (to create a ruff).
  need <= 0: lead your lowest card in the suit with the most outstanding higher cards; never lead trumps.
```

### 4.2 What the search player (PIMC) does that the heuristic doesn't

Relative to identical bids, simulation-based play was worth **+16 to +20 points/game** (thumb/PIMC 51.2% vs 25%; cal/PIMC vs a calibrated field 43.0% vs 25%). Inspecting its choices shows three recurring patterns you can copy:

1. **Void inference.** Once a player shows out of a suit, PIMC never again counts on a master in that suit holding up against them. Track **who is void in what** (much more valuable than tracking every card).
2. **Timing of the forced trick.** If you need 1 more trick and hold one master plus losers, take the trick *when the most dangerous opponents have already played*. That is usually 4th seat, not 2nd.
3. **Spoiling.** When your own result is settled (made, or hopelessly busted), it plays to bust the leaders. That was worth +2 pts/game and +4% wins (79.9% ± 2.4 vs 76.0% ± 2.4), *suggestive but not significant* at this sample size.

### 4.3 Trump management

- **Trumps are length tricks.** Small trumps win late tricks once higher trumps are gone or when you're void in the led suit. Count each trump as ¾.
- **Lead trump only when you want tricks AND hold the top trump with 2+ trumps.** Otherwise let opponents spend theirs.
- **With a zero (or made) bid, never lead trump.** Ditch high trumps under someone else's higher trump when you can.
- **A lone small trump in a zero bid is the #1 zero-killer**: zero-bid success drops from 80% (no trumps) → 65% (1 trump) → 59% (2 trumps).

### 4.4 Zero-bid survival protocol

When to bid zero (MC data): no trump honors, at most 1 trump, at most 1 side honor. Success 79% with 0 high cards, 73% with 1, 65% with 2.

1. **Shed high cards early,** while others are still fighting for tricks: every time you can't follow, throw your *highest* side card or a trump that's lower than one already played.
2. **When following, play the highest card that still loses** (an Ace stays dangerous until it's gone).
3. **Never lead from your top.** Lead your lowest card in the suit with the most outstanding higher cards.
4. **Count your forced-win risk:** a singleton King or a bare Ace in a 3–5 card hand is a near-certain trick. Bid 1, not 0.
5. **Endgame:** with 2 cards left, keep the one that is more likely to be beaten; dump the other at the first chance.

### 4.5 When ahead of / behind your bid

- **Behind (need > 0) with few tricks left:** you must take risks: lead your best card, ruff aggressively, play honors second-hand.
- **Exactly made (need = 0):** you are a zero-bidder now. Follow 4.4.
- **Busted (took one too many):** your hand is worth 0 points. Switch to **spoiling**: win tricks the leader needs to lose, dump to the leader when they need to win.

---

## 5. Exploiting human opponents

| Field (3 opponents) | Calibrated (ignores bids) | Mental (shades vs prior bids) | Monte Carlo (uses bids) |
|---|---|---|---|
| Overbidders (+1 trick) | 96.5% ± 1.2 | 94.8% ± 1.3 | 98.3% ± 0.7 |
| Underbidders (−1 trick) | 60.7% ± 2.8 | 55.8% ± 2.8 | 67.5% ± 2.7 |
| Trick hogs (count A/K, always win) | 63.4% ± 2.9 | **72.6% ± 2.6** | 70.3% ± 2.7 |

(1,200 games each; par 25%.)

**Habitual overbidders** destroy themselves: an overbidding field makes contested hands, and your exact bids in contested hands are easy points. **Exploit:** bid your honest count. When the table is overbid, you will often get tricks *dumped* on you by people who had to win but couldn't. In a contested hand, the person who bid a lot will take your trick for you.

**Habitual underbidders / conservative players** are harder to exploit. They're *closer to correct* than overbidders (finding 3). Exploit by being the one who **takes the tricks they can't shed**: they'll be dumping high cards late, so your marginal Kings become tricks.

**Trick hogs** (play to win regardless of bid): **use their predictability.** They'll overtake anything, so your Q/K behind them are safe *losers*. Lead into them when you need to lose. Shading down when they've bid a lot (the mental rule's prior adjustment) is what makes the mental rule score best here.

**Poor suit trackers:** they'll lead masters into your voids. Save trumps for exactly those moments.

**Strong vs weak opponents.** Against strong opponents, only the honest count + correct ducking + void tracking survive. Against weak opponents, also: (a) bid zero more liberally (they won't punish you by leading into your one honor), and (b) spoil leaders more aggressively. They don't adjust.

---

## 6. Compact heuristics table

| Situation | Do this | Why / evidence |
|---|---|---|
| Gut torn between bids b and b+1 (no count) | Bid b | Over-misses cost 4× under (−14.6 vs −3.7 pts/game) |
| 1–2 card hand, no trump | Bid 0 | Side Ace ≈ 0.06 tricks of bid value at 1–2 cards |
| 1 card, lone low trump, you lead first | Bid 1 (52%) | MC: P(win)=0.52 |
| 1 card, side Ace, you're dealer after 0-0-0 | Bid 0 (forced by hook; 86% safe) | MC |
| Long weak trumps (5+) in a big hand | Count ¾ each | Worked example 2: bid 3 with no honors |
| Earlier bids exceed fair share | Shade down | contested hands: exact 49% vs 60% |
| Made your bid | Shed highest losers | +5.4 pts/game |
| Need a trick, 2nd seat with a Q+ winner | Play it | always-duck = −10 pts/game |
| Opponent showed void | Your masters in that suit are no longer safe | PIMC's main edge |
| You're busted | Spoil the leader | +2 pts/game (suggestive) |

---

## 7. Worked examples

(4 players, trump = suit of the upcard; 400 Monte Carlo deals per bid; `results/ohhell_examples.txt`.)

| # | Hand (trump) | Position | P(exact) for bid 0 / 1 / 2 / 3 / 4 | Best | Mental count |
|---|---|---|---|---|---|
| 1 | A♠ 7♠ 3♠ · A♥ 9♥ 4♥ · K♦ 8♦ · 6♣ 2♣ (♠) | 1st | .00 / .30 / .43 / **.49** / .42 | **3** | 3.25 → 3 ✔ |
| 2 | 9♠ 7♠ 5♠ 4♠ 2♠ · Q♥ 8♥ · 6♦ · 3♣ 2♣ (♠) | 1st | .01 / .04 / .19 / **.45** / .22 | **3** | 2.75 → 3 ✔ |
| 3 | A♥ 8♥ 5♥ · A♦ 9♦ 4♦ 2♦ · Q♣ 7♣ 3♣ (♠, none held) | 1st | .89 / **.96** / .78 / .06 / — | **1** | 0.5 → 1 ✔ |
| 4 | K♠ 6♠ · A♥ · 7♦ · 4♣ (♠), 5 cards | 1st | .04 / .27 / **.46** / .27 / .02 | **2** | 2.5 → 3 ✘ (one too high; the gut-check "take the lower" fixes it) |
| 5 | same hand, dealer after 2-2-1 (hook forbids 0) | dealer | — / .23 / **.52** / .26 / .01 | **2** | 2.19 → 2 |
| 6 | K♥ · Q♦ · J♣ (♠), 3 cards | 1st | .42 / **.41**(EV 4.5) / .14 / .01 | **1** (by EV; 0 is nearly equal) | 0 → 0 (EV 4.2 vs 4.5; near-tie) |
| 7 | A♥ alone (♠) | 1st | **.60** / .40 | **0** | 0 |
| 8 | A♥ alone, dealer after 0-0-0 | dealer | **.86** / (1 forbidden) | **0** | 0 |
| 9 | 4♠ alone (♠ trump) | 1st | .48 / **.52** | **1** | ¾ → 1 |

Notes:
- **#2:** five small trumps with no honors are worth 3 tricks. Club players bid 1–2 here.
- **#3:** two side Aces and no trumps in a 10-card hand is worth only **1**. A bid of 2 succeeds 78% but EV(1) = 10.5 > 9.3. Interestingly, a bid of 0 also works 89%: you can usually shed both Aces when void.
- **#6:** three side honors in a 3-card hand are worth ~½ a trick; 0 and 1 are nearly equal.
- **#7:** a lone side Ace, even on lead, wins only 40%: one of three opponents usually holds a trump (P(no trump among 3 cards) ≈ 0.43).

---

## 8. YOUR TABLE: 1 → 7 → 1, exact = 10 + bid, miss = 0

Your scoring is exactly the baseline used everywhere in this document (exact bid = 10 + bid, so 10 for a zero, 11 for 1, ...; any miss = 0). The only difference is the hand pattern: **1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1** (13 hands). Re-run with `python -m ohhell.run_171 400` and `python -m ohhell.diag_171`.

**Ladder vs club players (4 players, 1,600 games each, par 25%):**

| Hero | 1→7→1 win rate | pts/game vs avg | (10→1→10 for comparison) |
|---|---|---|---|
| Trick hog (count A/K, always win) | 9.6% ± 1.3 | −16.1 | 2.9% |
| Same bids, play to the bid | 31.4% ± 1.8 | +4.0 | 33.6% |
| **Mental count** (x.5 rounds up) | **50.0% ± 2.3** | **+14.8** | 49.4% |
| Mental count, x.5 rounds down | 45.7% ± 2.3 | +13.2 | 45.0% |
| Calibrated bidder | 52.3% ± 2.4 | +16.0 | 55.0% |
| Calibrated **+1** (overbid) | **5.2% ± 1.1** | **−20.5** | 12.7% |
| Calibrated −1 (underbid) | 18.6% ± 1.5 | −3.9 | 19.9% |
| Monte Carlo bidder | 54.4% ± 2.4 | +17.8 | 63.0% |
| Club bids + PIMC card play | 33.4% ± 1.7 | +6.8 | 51.2% |
| Monte Carlo bids + PIMC play | 64.2% ± 2.4 | +23.8 | 81.8% |

Mental count at other table sizes (1→7→1): 3 players 55.8% (par 33%), 5 players 37.9% (par 20%), 6 players 24.9% (par 17%).

**What changes with 1→7→1:**

1. **Bidding is now almost the whole game.** Card-play skill is worth much less: simulation-quality play adds +6.8 pts/game here vs +20.4 on 10→1→10. With ≤7 cards there are few tricks to maneuver in. *Spend your mental effort on the bid.*
2. **Overbidding is even deadlier**: one-too-many drops you to 5% wins (−20.5 pts/game) vs 19% for one-too-few. **When in doubt, go lower, always.**
3. **Zero is the workhorse bid.** The Monte Carlo bidder bid zero on **41%** of all hands (vs 28% on 10→1→10) and made it **77%** of the time. EV: zero 7.7 vs bid-1 6.4 (58%) vs bid-2 6.1 (51%) vs bid-3 6.1 (47%).
4. **Small hands are 6 of your 13 deals** (two each of 1, 2, 3 cards). The 1–2 card rule (count only trumps; side Aces are ~worthless) now covers 4 of 13 hands. Get it right every time.
5. **The mental count works unchanged.** At 6–7 cards apply the −½ tax; the −1 tax never comes up.
6. **Seat effect is larger:** exact rate by bidding position: 1st 61%, 2nd 65%, **3rd 69%**, dealer 60%. The dealer's hook costs most in small hands (with 1 card the hook often *forces* a specific bid). As dealer on a 1–2 card hand, compute what's forbidden *before* looking at your hand's details.

**Exact-bid rates by hand size (Monte Carlo bidder, 5,200 hands):** 1 card 77%, 2: 71%, 3: 67%, 4: 62%, 5: 59%, 6: 52%, 7: 54%.

---

## 9. Reproduce

```
python -m ohhell.test_engine
python -m ohhell.experiments calibrate 4    # ~2 s
python -m ohhell.run_ladder 300             # ~11 min on 4 cores
python -m ohhell.diagnostics 400
python -m ohhell.run_round2 300             # ~25 min
python -m ohhell.run_play 600
python -m ohhell.examples
```
Results JSON: `results/ohhell_*.json`; logs: `results/ohhell_*log.txt`.

**Untested / open:** negative-score variants (the MC bidder supports any scoring function; not run). 6–7 player tables. Bid-conditioned sampling of opponent hands in PIMC. A stronger search (ISMCTS) to check whether PIMC's +20 pts is near the ceiling.
