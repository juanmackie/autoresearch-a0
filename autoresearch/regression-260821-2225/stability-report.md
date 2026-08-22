# Regression Stability Report — autoresearch-a0

- **Run:** autoresearch/regression-260821-2225
- **Base ref:** 347cfa0 (detached worktree `baseline/347cfa0ae…`)
- **Candidate:** working tree — bogo_sort.py final incumbent (in-place `list.sort()`, classic-loop iteration 6)
- **Scope:** `bogo_sort.py`
- **Probe:** auto-skipped (non-interactive session); inferred config: functional = `benchmarks/verify.py`, performance = `benchmarks/bench.py`, flakiness = repeat-5x verify
- **Samples:** 7/side (performance, independent processes) · 5/side (flakiness) · noise band 5%

## Classification

| Unit | State | Gated |
|---|---|---|
| verify cases, sizes 0–8 (green on baseline, green on candidate) | regression-eligible, green→green | yes — no red |
| verify cases, sizes 9–30 (infeasible on bogo baseline, green on candidate) | new-coverage | no |
| flakiness 5× both sides all green | regression-eligible, 0 flakes | yes — clean |
| performance 7× both sides | regression-eligible | yes — improvement |

**Core invariant held:** zero green→red transitions.

## Dimension results

| Dim | Tier | Baseline | Candidate | Δ | Regressed | Subscore |
|---|---|---|---|---|---|---|
| functional | HARD | 100/100 green (sizes 0–8) | 100/100 green (sizes 0–30) | 0 new reds | false | 100 |
| flakiness | SCORE | 0/5 nondeterministic | 0/5 nondeterministic | 0 | false | 100 |
| performance | SCORE | median 7750.560 ms | median 0.001 ms | −100.0000% | false | 100 |

**Performance statistics:** Mann-Whitney U = 0.0 (max 49), one-sided p = 1.000 for "candidate slower"; median delta −100.0000% — effect magnitude 100% ≫ 5% noise band. Both Mann-Whitney AND effect-size conditions satisfied; regression = false.

**Flakiness caveat:** 5/5 green ≠ non-flaky; at n=5 a p=5% flake rate is detected with only ≈23% probability (1−(1−p)ⁿ).

## Score math

| Dim | Subscore | Weight |
|---|---|---|
| performance | 100.00 | 0.30 |
| flakiness | 100.00 | 0.30 |
| **stability_score** | **100.00** | threshold 95 |

## Verdict

**STABLE** (exit 0, `score-regression.sh verdict`) — blocking: none.

Dims ran: functional, flakiness, performance.
Dims UNAVAILABLE (not applicable to this repo — no schemas, migrations, e2e, size budgets, or UI): api-contract, data-migration, integration-e2e, resource, visual-ui. Listed, not silently passed.

## Conclusion

The classic-loop optimization (bogo → in-place Timsort) introduces **no functional, flakiness, or performance regression**. The candidate is strictly faster and strictly more capable (passes the full 0–30 verification suite the baseline could not). Ship-safe with respect to this gate (no deploy/push performed).
