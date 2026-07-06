# Attempt 014 — get mathlib (couldn't) → compile the infinite statement mathlib-free

**Target.** User: "try to get mathlib." Goal behind it: make the *infinite* Nivat
statement (`lean/Nivat.lean`) machine-checked instead of an uncompiled mathlib-style
sketch.

**mathlib acquisition — FAILED (documented).** Every route is egress-blocked:
- olean build-cache: `lakecache.blob.core.windows.net`, `mathlib4.blob.core.windows.net` → 000.
- source: `codeload.github.com` → 403; `cdn.jsdelivr.net` (gh mirror) → 000;
  `reservoir.lean-lang.org` → 000.
- prebuilt-mathlib Docker image: `leanprovercommunity/mathlib` has only a `latest`
  tag whose layers are identical to the toolchain base (no mathlib); `.../mathlib4`,
  `.../lean4-mathlib`, `.../mathlib-dev` → 404.
- only `raw.githubusercontent.com/.../mathlib4/<tag>/<file>` (200) works — but
  file-by-file with no tree listing (api.github.com blocked) and no olean cache
  means an hours-long from-scratch build; not feasible.

**Workaround — SUCCEEDED.** Rewrote `lean/Nivat.lean` mathlib-free: the complexity
bound `P_x(m,n) ≤ K` is encoded as a **K-template covering** (`∃ K templates, every
m×n window equals one`) — the same encoding the z3 experiments use — so no
`Set.ncard`/cardinality library is needed. Result: the file **compiles** under the
extracted Lean 4.10.0.

**Findings — `[PROVEN]` (0 sorry, 0 axioms).**
- `NivatConjecture A : Prop` — a faithful mathlib-free statement of the conjecture
  (stated only; it is open, not asserted).
- `const_periodic`, `const_PatternLE_one`, `not_PatternLE_zero` — sanity lemmas
  proved with **no axioms at all** (pure kernel), validating the encoding
  (constant configs are periodic and low-complexity; complexity is never ≤ 0).
  Evidence: `lean/out/verify.log`.

**Verdict: checkpoint (formal), NOT termination.** The infinite statement is now
machine-checked mathlib-free, but the conjecture itself is unproved and no `[CITED]`
record on (A)/(B)/(C) is beaten. mathlib remains unobtainable in this environment;
the `setup.sh`/`lakefile.toml`/`lean-toolchain` scaffolding is kept only for an
environment where mathlib *is* reachable (not this one).
