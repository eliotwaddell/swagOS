# Document C — The Cabin Conquest Cheat Sheet

*10 minutes. Every rule here is backed by a simulation result in Doc A or Doc B (numbers in brackets).*

---

## ♠ OH HELL

### Before the first deal, ask
Misses = 0 or negative? · Hook on? · Zero worth 10? · Must-trump rule? *(Any "no" changes the count; see Doc A §1.)*

### The count (20 seconds, in quarters)
| | 1–2 cards | 3–5 cards | 6–10 cards |
|---|---|---|---|
| **Each trump** | ¾ | ¾ | ¾ |
| Trump A / K / Q bonus | — | +¾ / +½ / +¼ | +¾ / +½ / +¼ |
| **Side Ace** | 0 | ½ | ¾ |
| Side King | 0 | 0 | ½ |
| Big-hand tax | — | — | −½ (6–8), −1 (9–10) |

Earlier bids already over their fair share? Subtract ¼ per extra trick. **Round, x.5 up.**
*[This count alone: 49% wins vs 25% par against club players; 57% at 3 players, 37% at 5.]*

### Top 10 rules
1. **Play to your bid, never to "win tricks."** An extra trick is a zero. *[Same bids: hog play 3% wins, bid-play 34%.]*
2. **When unsure, bid lower.** One-too-high costs 4× one-too-low. *[−14.6 vs −3.7 pts/game.]*
3. **Small trumps are tricks.** ¾ each. Five small trumps in a 10-card hand = bid 3.
4. **Side Aces are only ¾ of a trick, and worth nothing in 1–2 card hands.**
5. **Zero is the best-paying bid when plausible** (no trump honor, ≤1 trump). *[76% success → EV 7.6, beats every other bid.]*
6. **Made your bid? Shed your HIGHEST losing card every trick.** *[+5.4 pts/game.]*
7. **Need a trick, 2nd seat, holding Q+ or a trump that wins? Play it now.** *[Always ducking: −10 pts/game.]*
8. **Track voids, not every card.** Once someone shows out, your "master" in that suit is no longer safe.
9. **Never lead trump unless you want tricks AND hold the top trump with 2+ trumps.**
10. **Busted? Become a spoiler.** Wreck the leader's bid. *[Suggestive: +4% wins.]*

### Decision hierarchy: every card you play
```
need = bid − tricks won
need > 0 : safe winner? → cheapest one.  Honor/trump winner? → play it.  Can't win → lowest side card.
need ≤ 0 : have a loser? → play the HIGHEST loser.  All win? → last seat: biggest; else: lowest.
leading  : want tricks → master (trump master first if 2+ trumps), else low from short side suit.
           don't want  → lowest card where most higher cards are still out. Never trump.
```

### Catastrophic mistakes
- Taking "free" tricks after making your bid.
- Bidding a side Ace in a 1–2 card hand.
- Bidding zero holding a trump honor or 2+ trumps. *[Zero success: 80% → 65% → 59% with 0/1/2 trumps.]*
- Dealer forcing a bid UP to dodge the hook when down was survivable.
- Saving a high card "for later" when you want to lose. Later it wins.

### Exploit list
- **Overbidders:** do nothing special; bid honestly and collect. *[You win 95–98% vs a +1 field.]*
- **Trick hogs:** they'll overtake everything, so your Q/K behind them are safe losers. When they bid big, shade your count down. *[73% wins.]*
- **Conservative players:** they dump high cards late, so your marginal Kings become tricks.
- **Non-trackers:** they'll lead into your voids. Keep a small trump for exactly that.

### Endgame (last 2–3 tricks)
Count your sure winners vs need. Keep the card most likely to be *beaten* if you're done; lead your master *after* the void-holder has played if you need one.

---

## ♦ SEQUENCE (2v2)

### Before the first game, ask
2 sequences to win (official, 2 teams)? · Can one-eyed jacks break a finished sequence (official: no)? · Hand size (official: 6 for 4 players)? · Dead-card rule?

### Top 10 rules
1. **Two-eyed (wild) jacks: hold them. Spend one only to *complete* a sequence.** *[Spending freely: 38% wins vs the disciplined version.]*
2. **One-eyed jacks: use them.** Remove the chip that kills the most enemy lines, usually the center-most chip of their best line or a crossing chip. *[Hoarding them: 42%.]*
3. **Your partner's chips are your chips.** Extend the *team's* best line. *[Ignoring teammate: 41%.]*
4. **Center beats edge. Value = how many 5-lines pass through the square.** The center 2×2 (2♥ 3♥ 4♥ 5♥) ends up in finished sequences 37% of the time; edges ~4%. *[r = 0.96.]*
5. **Best cards: middle hearts (2♥–9♥) and inner clubs (2♣–6♣). Worst: spades.** Dump edge cards when nothing central is playable.
6. **Build forks:** a chip that makes two threes (or a three and a four) on different lines. Value lines 1 : 3 : 9 : 27 for 1–2–3–4 chips. *[Beat flatter and steeper scales.]*
7. **Always block a live enemy open four.** Early on, ~1 in 3 chance the next opponent can finish it; ~1 in 2 that one of them can. Count outs first: no copies left and no wild jacks → it's dead, ignore it.
8. **Don't over-defend.** A lone enemy three can wait; a three crossing another enemy line cannot. *[Blocking all threes hard: 42%.]*
9. **Second sequence: reuse one chip.** Look for a line through an *end* chip of your first sequence.
10. **Turn in dead cards every turn you have one.** Free card.

### Decision hierarchy: every turn
```
1. Can we complete a sequence now?           → do it (wild jack allowed).
2. Enemy open four with live outs?           → block with the card, else one-eyed jack its best chip;
                                                wild jack only if nothing else AND ≥4 outs.
3. Enemy fork (crossing threes / three+four)? → remove/block the crossing square.
4. Our fork available?                        → take it.
5. Extend the team's longest live line, center first, with your WEAKEST card that does the job.
```

### Catastrophic mistakes
- Using a wild jack to make a 3 or 4.
- Building a line your partner already blocked or already owns.
- Chasing corner/edge lines early (corners look free but edge lines connect to nothing).
- Letting an enemy open four live because "they probably don't have it". The odds above say they often do.
- Spending a turn blocking a four that is already dead (both copies discarded, wild jacks gone).

### Exploit list
- **They burn wild jacks early** → late-game, their fours rely only on natural cards. Make your fours with both copies unseen.
- **They play for themselves** → two half-lines; block the one nearer to four, and let them duplicate.
- **They only attack** → build forks; they won't block threes.
- **They block every three** → plant decoy threes on the edges; they waste turns.
- **Tunnel vision** → one chip in the *middle* of their line (or a one-eyed jack there) kills several windows.

### Endgame
- One sequence up + a wild jack in hand = any open four is a forced win. Build one.
- One-eyed jack target: the chip that would let them reuse a chip from their first sequence.
- Turn order A1→B1→A2→B2: a four you leave alive gets **one** enemy shot before your partner moves.

---

## ✅ 5-second checklist before every move

**Oh Hell:** *What's my need? Do I want this trick? If not, what's my highest card that still loses? Who's void?*

**Sequence:** *Can we win? Can they win next turn (count outs)? Can I make a fork? Am I about to waste a wild jack? Is my partner's line better than mine?*

---

*Evidence: Oh Hell results are 1,200–3,000 simulated 19-hand games per comparison. Sequence results are 2,000 simulated 2v2 games per comparison (fewer for the lookahead tests), deck-paired and with colors swapped. Opponent models are simplified recreational-player bots; rankings and gaps are the findings, absolute percentages are illustrative.*
