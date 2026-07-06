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
