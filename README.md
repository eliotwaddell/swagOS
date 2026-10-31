# Operation Cabin Hegemony

Computational strategy for **Oh Hell** and **2v2 Sequence**: rules-checked simulators, agent tournaments, and field manuals.

## Deliverables
| Doc | What |
|---|---|
| [docs/A_OhHell_Art_of_Exact_Victory.md](docs/A_OhHell_Art_of_Exact_Victory.md) | Oh Hell technical analysis + field manual |
| [docs/B_Sequence_Doctrine_of_Two_Generals.md](docs/B_Sequence_Doctrine_of_Two_Generals.md) | Sequence technical analysis + 2v2 tactical guide |
| [docs/C_Cabin_Conquest_Cheat_Sheet.md](docs/C_Cabin_Conquest_Cheat_Sheet.md) | **The 10-minute cheat sheet** |
| [NOTES.md](NOTES.md) | Progress notes, open questions, next experiments |

## Layout
```
ohhell/    engine.py (rules), agents.py (bidders/players incl. Monte Carlo + PIMC), experiments.py (harness),
           run_ladder.py, run_round2.py, diagnostics.py, examples.py, test_engine.py
sequence/  board.py (real Jax board), engine.py (rules), agents.py (evaluators, Monte Carlo), experiments.py,
           run_all.py, run_v2.py, run_v3.py, positional.py, analytic.py, test_engine.py
results/   raw JSON + logs of every experiment cited in the docs
```

## Reproduce (Python 3.10+, numpy; 4 cores ≈ 1.5 h for everything)
```
python -m ohhell.test_engine && python -m sequence.test_engine
python -m ohhell.experiments calibrate 4      # fits the calibrated bidder (results/ohhell_cal_table_n4.json)
python -m ohhell.run_ladder 300
python -m ohhell.diagnostics 400
python -m ohhell.run_round2 300
python -m ohhell.examples
python -m sequence.run_all 1000 ladder; python -m sequence.run_all 1000 sweep; python -m sequence.run_all 1000 human
python -m sequence.run_all 300 mc; python -m sequence.run_v2 1000; python -m sequence.run_v3 1000
python -m sequence.positional 6000; python -m sequence.analytic
```
All experiments are seeded; re-running reproduces the numbers exactly.
