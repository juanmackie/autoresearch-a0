# functional (HARD)
- Baseline green-set: verify.py max_size=8 → 100/100 (bogo infeasible beyond ~size 10; full suite times out by design).
- Candidate: verify.py full suite → 100/100 incl. sizes 0-30, duplicates, empty/single/sorted/reversed.
- Matched tests (sizes ≤8): green→green, regression-eligible, 0 reds. Sizes >8: new-coverage, ungated.
- No green→red transition → HARD gate passes, subscore=100.
