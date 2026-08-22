# flakiness (SCORE)
- 5× `benchmarks/verify.py` per side: baseline (max_size=8) 5/5 green; candidate (full 0-30) 5/5 green.
- 0 nondeterministic results either side → subscore=100.
- Caveat: detection probability at n=5 for p=5% flake rate ≈ 23%.
