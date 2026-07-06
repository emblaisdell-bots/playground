# Attempt 016 — novel directions: a block-complexity theory + Nivat-bound sharpness

**Target.** User: "try novel research directions and prove whatever you can." Build
out genuine, general theorems (symbolic proofs, not enumeration) around block
complexity, in mathlib-free Lean.

**Results — all `[PROVEN]`, axioms `[propext(, Quot.sound)]` only, 0 `sorry`,
`lean/NivatTheory.lean`.**

*Direction — sharpness of the Nivat threshold.*
- **`sd_aperiodic`**: the single-defect configuration `sd` (colour `1` at the
  origin, `0` elsewhere) is **aperiodic** — no nonzero vector is a period. Proof: a
  period `v` would give `sd v = sd 0 = 1`, forcing `v = 0`. This is the honest
  reason Nivat's hypothesis cannot be weakened from `P ≤ m·n` to `P ≤ m·n+1`: `sd`
  is aperiodic yet (as the finite `sharp_*` results show) has complexity exactly
  `m·n+1`. So `m·n` is the sharp threshold.

*Direction — monotonicity of complexity.*
- **`PatternLE_mono_K`**: `P ≤ K` and `K ≤ K'` give `P ≤ K'` (embed the covering,
  padding with a default template extracted from the always-present origin window).
- **`PatternLE_restrict_row` / `PatternLE_restrict_col`**: `P_x(m,n) ≤ P_x(m+1,n)`
  and `P_x(m,n) ≤ P_x(m,n+1)` — a covering of taller/wider windows truncates to a
  covering of smaller ones. So block complexity is monotone in the window
  dimensions.

*(Prior, same file:* `periodic_pair_PatternLE` — periodicity ⇒ `P ≤ p·q`.)*

**Verdict: PROVEN (symbolic) — checkpoints, NOT termination.** These form a small
but genuine machine-checked theory of block complexity (monotonicity, a periodic
upper bound, and a sharpness witness). None beats a `[CITED]` record on (A)/(B)/(C);
the hard direction remains Nivat itself. Reproduce `lean/verify.sh`.

## Follow-up: sharpness completed (general, symbolic)

`sd_PatternLE` and the capstone `nivat_bound_sharp` are now proved (axioms
`[propext, Quot.sound]`, 0 sorry):

- **`sd_PatternLE (m n)`**: `P_sd(m,n) ≤ m·n + 1` for every window — the `m·n+1`
  templates (all-zero, plus one per cell) cover all windows. Uses `encode_inj`
  (injectivity of the cell encoding `(x,y) ↦ x·n+y`, proved via `%`/`/`).
- **`nivat_bound_sharp`**: `sd` is aperiodic AND `P_sd(m,n) ≤ m·n+1` for all `m,n`.
  Hence **Nivat's threshold `m·n` is optimal** — relaxing the hypothesis to
  `P ≤ m·n+1` would make the conjecture false (this witness). General, symbolic.

This upgrades the earlier finite `[EXPERIMENTAL]`/`native_decide` sharpness evidence
to a fully general machine-checked theorem. Still a checkpoint (it does not settle
Nivat); beats no `[CITED]` record.
