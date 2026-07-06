# Attempt 009 — structure of minimal-complexity aperiodic configs (line: base/strengthen)

**Target.** Not a frontier record — a descriptive question sharpening E2: *what
do the extremal primitive configs (those attaining `P(2,2) = mn+1 = 5`) look
like?* Understanding the extremals is how one would guess the mechanism a proof
must exploit.

**Approach.** Exhaustive: for each binary torus up to `4×5`, enumerate all
primitive configs with `P(2,2)=5`, classify the "defect set" (minority cells).
Script `experiments/extremal.py`, output `out/extremal.{txt,json}`.

**Findings [EXPERIMENTAL].**
- The **single-defect** config — one minority cell in an otherwise constant field
  — is primitive and has `P(2,2) = mn+1 = 5` on **every** tested torus. Reason: the
  lone cell kills every nonzero period, and the 2×2 patterns are the all-constant
  one plus the 4 windows covering the defect = `1 + 4 = mn+1`. Crucially this holds
  for **all** `N,M` (defect density `→0`), so the sharp floor `mn+1` is attained
  *uniformly in torus size* — the achievability side of the uniform question H1.
- Extremals are **not unique**: 2-, 3-, and 4-minority-cell primitive extremals
  also occur (counts in `out/extremal.json`). So `P=mn+1` does not force a single
  defect; it forces only *bounded, concentrated* aperiodicity.

**Verdict: confirmed (checkpoint).** Descriptive `[EXPERIMENTAL]` result; not a
frontier improvement and not `[PROVEN]`. Feeds H1 (uniform `mn+1` floor) with an
explicit extremal family.

**Caveat.** The `defect_shape` classifier only tests axis/main-diagonal
alignment, so its "not-a-line" bucket for 2-cell defects just means "not
axis/diagonal aligned" (any two points are trivially collinear). Not
over-interpreted above.
