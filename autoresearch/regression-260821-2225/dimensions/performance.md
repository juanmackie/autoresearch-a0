# performance (SCORE)
- 7 independent-process samples/side of `python3 benchmarks/bench.py` (median of 3 in-process runs each).
- Baseline (bogo, worktree 347cfa0): medians [7835.883, 7510.760, 7503.200, 7869.014, 7403.095, 8938.848, 7750.560] ms → median 7750.560 ms
- Candidate (list.sort): [0.001]×7 ms → median 0.001 ms
- Mann-Whitney U = 0.0 / 49, one-sided p = 1.000 ("candidate slower"); effect −100.0000% ≫ 5% band → regressed=false, subscore=100.
