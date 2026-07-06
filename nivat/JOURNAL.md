# JOURNAL — dated log

## 2026-07-06

### Phase 0 — setup & environment reconnaissance

- `git` repo already present with the target branch
  `claude/nivat-conjecture-research-rbd8w1` and remote configured. Created the
  `nivat/` tree and `.gitignore`.
- **Toolchain reconnaissance (decisive).** Attempted to install Lean via `elan`.
  Both distribution routes are **blocked by the egress policy** (HTTP 403 CONNECT,
  policy denial — not retryable per proxy rules):
  - `github.com/leanprover/elan/releases/...` → 403
  - `release.lean-lang.org` → 403
  z3 (`pip install z3-solver`) and Python **do** work; package registries and
  `raw.githubusercontent.com` are reachable.
- **Literature access.** `WebSearch` (Anthropic-proxied) works and returns real
  results. Direct fetches of arxiv/wikipedia/springer/etc. are **403-blocked**, so
  full PDFs could not be retrieved. `LANDSCAPE.md` cites what search actually
  returned and flags summary-vs-verified numbers.
- **Decision.** The prescribed "verifier-first / Lean" method is not executable
  here. Rather than fake proofs (the worst outcome per the Prime Directive), the
  plan is: (i) honest cited landscape, (ii) a rigorous **experimental** program in
  Python + z3 as the only available external checker, (iii) Lean *statements* as
  clearly-marked UNVERIFIED scaffolding, (iv) an honest non-result, since
  `[PROVEN]` termination is impossible without a compiler. The Lean blocker is
  surfaced to the user with a recommendation.

### Phase 1 — formal statement (scaffolding only)

- Wrote `lean/Nivat.lean`: `Config`, `patternAt`, `patternSet`, `P` (via
  `Set.ncard`), `Periodic`, `NivatConjecture`, plus three strictly-easier sanity
  lemmas. **Not compiled** (no toolchain); all bodies are `sorry`. Logged in
  `SORRIES.md`. No lemma-laundering: no sorry restates the conjecture.

### Phase 2 — reproduce a known base case (computationally)

- Built and unit-tested the core primitives (`nivat_core.py`,
  `nivat_core_test.py`, all pass): pattern counting `P(m,n)`, period-vector /
  primitivity detection, 1D factor complexity.
- **E1**: reproduced Morse–Hedlund (the 1D base case) exhaustively and found it
  **sharp** — primitive binary necklaces up to length 18 all satisfy
  `p(n) ≥ n+1`, with `min p(n) = n+1`. Machinery certifies a true statement. ✓

### Phase 3 — experimental frontier

- **E2**: exhaustive torus enumeration (`torus_search.py`) over binary
  `3×3, 3×4, 4×4, 3×5`. Finding: for every window strictly interior to the torus,
  the minimum complexity of a *primitive* config is exactly `mn+1`. The `mn`
  threshold is sharp in 2D exactly as in 1D. Windows wrapping a full torus
  dimension give a 1D-artifact `gap=0` (excluded).
- **E4**: z3 (`sat_search.py`) confirms non-existence of low-complexity primitive
  configs at sizes past brute force (`5×5, 6×6, 7×7`, `P(2,2)≤4` → UNSAT …).

### Phase 4 — frontier loop

- See `FRONTIER.md` and `attempts/INDEX.md`. Binding constraint hit at setup: with
  no Lean, no attempt can produce a `[PROVEN]` improvement, so none can terminate.
  Each frontier target was probed *experimentally* (the cheap filter the method
  prescribes); records on (A)/(B)/(C) are set by expert proofs using
  expansive-subdynamics/algebraic machinery and are not reachable by finite
  computation. Attempts logged with honest verdicts. No record beaten.

### Outcome

- Honest **non-result** (safety-valve semantics), driven primarily by the
  environmental blocker (no verifier) and secondarily by the genuine difficulty of
  the frontier. Full write-up in `RESULT.md`. Real, reproducible experimental
  contributions recorded as `[EXPERIMENTAL]` (E1–E4).

### 2026-07-06 (later) — operator chose to enable Lean

- Operator selected "allowlist Lean hosts". Re-tested egress: still 403 for
  `github.com` releases, `release.lean-lang.org` unreachable — the policy change
  has not taken effect in this live container (network policy is set at
  environment creation; it applies to a NEW session). Did not retry the denial.
- Committed Lean bring-up scaffolding for a future allowlisted session:
  `lean/setup.sh`, `lean/lakefile.toml`, `lean/lean-toolchain` (all UNTESTED here
  — no toolchain to test them; versions may need the usual mathlib alignment).
- Resume path documented in README §"Resuming with Lean". All work pushed, so a
  fresh session on this branch can install Lean and continue with a real verifier.

### 2026-07-06 (later) — frontier-push: experimental deepening (attempts 009-011)

Directive "push the research frontier". With no verifier, "frontier" here means
the *experimental* frontier (no [PROVEN] beat is possible). Three attempts:
- 009 extremal structure: single-defect config is the universal minimal aperiodic
  object; attains mn+1 uniformly in N (to 100x100). [EXPERIMENTAL], checkpoint.
- 010 uniform mn+1 floor (H1): achievability (single defect, all N) + z3 lower
  bound UNSAT for N=5..11 (UNKNOWN at 12). Partial support; CONJECTURED, not used
  as a lemma. checkpoint.
- 011 dimensional gap on finite tori: z3 3D probe INCONCLUSIVE (UNKNOWN even at
  280s); noted the gap is likely infinite-only, so finite tori may never show it.
  obstacle. No record beaten; nothing PROVEN. All committed and pushed per attempt.

### 2026-07-06 (later) — got Lean anyway (Docker mirror), formal finite proofs (attempt 012)

User: "try elsewhere to pull Lean; ok to skip mathlib". Mapped egress: official
Lean hosts (github releases, api.github.com, release.lean-lang.org) blocked; Docker
Hub API reachable but its cloudfront blob CDN blocked; **mirror.gcr.io reachable
with GCS-backed blobs**. Pulled leanprovercommunity/lean4 via mirror.gcr.io,
extracted lean+lake from image layers -> working Lean 4.10.0, mathlib-free
(lean/pull_lean.sh, lean/env.sh).
Wrote lean/NivatFinite.lean (core-only): encodes N×N binary torus as bits of a Nat,
defines P22/isPeriod/primitive, proves by native_decide:
  floor_3x3, floor_4x4 (∀ primitive config, P(2,2) >= 5 = mn+1; exhaustive over
  512 / 65536), single_defect_3x3/4x4 (bound attained). Compiles exit 0, zero sorry,
  axioms = [Lean.ofReduceBool] only (native_decide; disclosed). Evidence
  lean/out/verify.log; reproduce lean/verify.sh.
Honest status: E2 for 3×3/4×4 upgraded EXPERIMENTAL -> PROVEN. Beats NO cited
record (elementary finite instances) -> checkpoint, NOT termination. A verifier
makes finite facts provable, not the frontier reachable. Ledgers (SORRIES, CLAIMS,
README, RESULT, FRONTIER, INDEX) updated accordingly.

### 2026-07-06 (later) — broaden formal coverage (attempt 013)

Generalized lean/NivatFinite.lean to arbitrary windows; added PROVEN
(native_decide, axiom ofReduceBool, 0 sorry): 2D sharp floors P(2,3)>=7 and
P(3,3)>=10 on the 4x4 torus (all 65536), their sharpness witnesses, and the 1D
Morse-Hedlund floors p(2)>=3, p(3)>=4 for length-6 necklaces (upgrades E1 to
PROVEN). Compiles exit 0 (~60s). Still elementary finite instances -> checkpoint,
NOT termination; beats no cited record. Honest limit: native_decide settles only
finite facts; the frontier targets (A k=5, B c>1/2, C t=3) are universal/infinite
and need a mathematical idea I don't have. Further finite formalization would be
padding.

### 2026-07-06 (later) — mathlib unobtainable; infinite statement compiled mathlib-free (attempt 014)

User: "try to get mathlib." Probed every route: olean cache
(*.blob.core.windows.net) 000; source via codeload 403, jsdelivr/reservoir 000;
prebuilt-mathlib Docker images 404 (leanprovercommunity/mathlib :latest == toolchain
base, no mathlib). Only raw.githubusercontent single files reachable (200) —
insufficient (no tree listing; no olean cache; hours-long build). Conclusion:
mathlib not practically obtainable here.
Workaround: rewrote lean/Nivat.lean MATHLIB-FREE — encode "P_x(m,n) <= K" as a
K-template covering (same trick as the z3 experiments), no Set.ncard needed. It
COMPILES under the extracted Lean 4.10.0: NivatConjecture stated (open); sanity
lemmas const_periodic/const_PatternLE_one/not_PatternLE_zero proved with 0 axioms,
0 sorry. So the infinite statement is now machine-checked without mathlib.
Still a checkpoint (statement compiled, conjecture unproved, no record beaten).

### 2026-07-06 (later) — actual symbolic mathematics (attempt 015)

User: "try actual novel symbolic mathematics, not just trying examples."
Proved a GENERAL theorem by real reasoning (not native_decide enumeration):
lean/NivatTheory.lean, periodic_pair_PatternLE — a config with periods (p,0),(0,q),
p,q>=1, has P_x(m,n) <= p*q for every window (periodicity bounds complexity; the
provable converse of Nivat's direction). Built entirely from Lean core (no mathlib,
no Batteries): windowAt_add_period -> windowAt_nsmul/windowAt_zmul (invariance under
integer multiples of a period, induction via Int.rec) -> reduce_h/v/pair (anchor mod
(p,q) via Int.ediv_add_emod) -> covering by the p*q reduced anchors. Axioms:
[propext, Quot.sound] only (kernel logic; NO native_decide, NO sorry). Genuine
symbolic math; still the tractable/converse direction, beats NO cited record ->
checkpoint, not termination. verify.sh now checks all three Lean files.
