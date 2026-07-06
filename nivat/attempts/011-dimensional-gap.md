# Attempt 011 — does the 2D→3D gap show up on finite tori? (line: context / planarity)

**Target (context, not a record).** Nivat holds in 2D but its analogue is FALSE
for `d ≥ 3` (`[CITED]`, `LANDSCAPE.md`). Question: can that dimensional difference
be exhibited **computationally** on finite tori — i.e. does a *primitive* 3D torus
config with box-complexity `P(2,2,2) ≤ 8 = mnk` exist, where the 2D analogue
`P(2,2) ≤ 4` is impossible (UNSAT)?

**Approach.** z3 existence (`experiments/sat_nd.py`, `d`-dimensional encoding):
forbid every nonzero period vector and force `≤ K` template boxes. Re-verify any
SAT witness in pure Python.

**Findings [EXPERIMENTAL].**
- 2D baseline reproduced: `Z_5×5` primitive with `P(2,2) ≤ 4` is **UNSAT**.
- 3D: `Z_3×3×3` and `Z_3×4×4` primitive with `P(2,2,2) ≤ 8` both return
  **UNKNOWN** — z3 could not decide even the smallest case with a **280 s** budget.
  A `3×3×3` torus has 26 nonzero period vectors, each contributing a large
  disjunction, on top of 8-template matching over 27 cells; the instance is out of
  z3's reach here.

**Verdict: obstacle / inconclusive.** No finite dimensional gap was demonstrated.
Two honest reasons, and I am not claiming otherwise:
1. **Solver limit.** The 3D encoding is too hard for z3 at reachable sizes
   (UNKNOWN, not SAT/UNSAT), so the finite question is simply undecided here.
2. **Conceptual mismatch (why this probe may be the wrong tool).** The genuine
   `d ≥ 3` counterexamples are **infinite** aperiodic low-complexity configs. On a
   finite torus every config is triply-periodic, so a "primitive finite torus"
   need not witness the infinite phenomenon at all — the dimensional gap may live
   only in the infinite regime and be invisible to any finite-torus search,
   independent of solver strength.

This is a `[CONJECTURED]`/open note, not a result: it neither beats a record nor is
`[PROVEN]`. The planarity-necessity fact itself remains `[CITED]` (it does not
depend on this probe). Logged so the dead end is not re-attempted with the same
encoding (see caching rule).
