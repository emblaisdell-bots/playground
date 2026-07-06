# Attempt 013 — broaden the machine-checked coverage (more windows + 1D)

**Target.** Not a frontier record: generalize the Lean formalization from the
single 2×2 window to arbitrary windows, and formally verify the sharp-floor
phenomenon across more of the E1/E2 tables, so the `[PROVEN]` set reflects the
experimental findings more fully.

**Approach.** Refactored `lean/NivatFinite.lean` to a generic `window/P wm wn`.
Added `native_decide` theorems (mathlib-free, axiom `ofReduceBool` only).

**Findings — `[PROVEN]` (0 sorry).**
- 2D sharp floor `primitive ⇒ P(wm,wn) ≥ wm·wn+1`:
  `floor_4x4_w23` (`P(2,3) ≥ 7`), `floor_4x4_w33` (`P(3,3) ≥ 10`) — exhaustive over
  all 65536 4×4 configs — in addition to the earlier 2×2 cases.
- Sharpness: `sharp_4x4_w23/w33` — the single-defect config attains `P=7,10`.
- 1D Morse–Hedlund sharp floor `primitive necklace ⇒ p(n) ≥ n+1`:
  `mh_L6_n2` (`p(2) ≥ 3`), `mh_L6_n3` (`p(3) ≥ 4`) over all 64 length-6 necklaces.
  This puts the 1D base case (experiment E1) into `[PROVEN]`.

**Verdict: PROVEN checkpoint — NOT termination.** Broader formal coverage of the
finite sharp-threshold, machine-checked. Still elementary finite instances; beats
**no** `[CITED]` record on (A)/(B)/(C). Evidence `lean/out/verify.log`.

**Honest limit reached.** With `native_decide` I can only settle *finite* facts.
Every frontier target (A `k=5`, B `c>1/2`, C `t=3`) is a universal implication
over all `n` / all configurations that no finite computation can decide, and I
have no new mathematical idea to prove one by hand. So the frontier lines remain
**not beaten**, and further finite formalization would be padding, not progress.
