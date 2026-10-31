# Progress notes (resume here)

## Status (2026-10-31)
- [x] Rules established (Pagat for Oh Hell; Jax-rule summaries for Sequence). House-rule questions listed in Doc A §1 / Doc B §1.
- [x] Oh Hell engine + tests, 5 bidders, 5 players, calibration, ladder, diagnostics, exploitation, play ablations, worked examples.
- [x] Sequence engine (real board, validated) + tests, evaluator agents, flaw models, parameter sweeps, Monte Carlo lookahead (negative result), positional heatmap, analytic threat odds.
- [x] Docs A, B, C.
- [x] 2v2v2 Sequence (6 players, 3 teams, 1 sequence): engine generalized (n_teams), suite in sequence/three_team*.py, Doc B §11, cheat sheet box.

## Key numbers (see results/*.json)
Oh Hell (4p, vs club field, par 25%): MC bid + PIMC play 81.8% ± 2.4; mental count 49.4% ± 2.7 (round-half-up; round-down tested worse);
overbid +1 −14.6 pts/game vs underbid −1 −3.7; trick-hog play 2.9%.
Sequence (2v2, 2,000 games each): tuned (W 1:3:9:27, wild-jack only to complete, lam 0.75) vs strong 59.8%;
premature jacks −11.6 pts; individualist −8.6; hoarding one-eyed −8; over-defense −8; tuned vs human model 72.0%.

2v2v2: recommended agent (W 1:4:16:80, lam .5) 35.6% vs tuned-2v2 field, 52.0% vs human field (par 33.3%); premature wild jacks 23.3%; individualist 22.0%; lam 2.0 26.3%; seat 36/32/31%.

## Known limitations / caveats
- Opponents are bots modelling recreational players. Rankings are robust; absolute rates are illustrative.
- PIMC samples opponent hands uniformly (not conditioned on their bids).
- Sequence MC lookahead underperformed (42% ± 4%) because of short-horizon rollouts. Needs a better leaf evaluation or longer, cheaper rollouts.
- The Sequence heatmap's left/right asymmetry is a tie-break artifact; use the ring averages.

## Next experiments (if resumed)
1. Oh Hell: negative-miss scoring and "zero = 5 points" variants (bid_montecarlo accepts any scoring via score_hand).
2. Oh Hell: bid-conditioned hand sampling in PIMC; ISMCTS to bound the ceiling.
3. Sequence: 1-sequence-to-win variant (3 teams), 7-card variant; MC with longer rollouts using the tuned policy.
4. Sequence: learn W per game phase (early vs late).
