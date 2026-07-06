# CLAIMS — every claim with an honest status tag

Tags: `[PROVEN]` (Lean, 0 sorry) · `[CITED]` (retrieved source) ·
`[EXPERIMENTAL]` (ran code + saved output) · `[CONJECTURED]`/`[HEURISTIC]` (ours).

## `[PROVEN]` — machine-checked in Lean 4.10.0 (mathlib-free), 0 sorry

A Lean toolchain was obtained via the Docker mirror route (`lean/pull_lean.sh`;
the official hosts stay egress-blocked). `lean/NivatFinite.lean` compiles (exit 0),
each proof depending only on `Lean.ofReduceBool` (the `native_decide` axiom — see
the caveat in `SORRIES.md`). Evidence `lean/out/verify.log`, reproduce `lean/verify.sh`.

2D sharp floor "primitive config ⇒ `P(wm,wn) ≥ wm·wn + 1`":
- **P1** `floor_3x3`, `floor_4x4` — 2×2 window on the 3×3 / 4×4 binary tori:
  `P(2,2) ≥ 5` (exhaustive over 512 / 65536).
- **P2** `floor_4x4_w23`, `floor_4x4_w33` — larger windows on the 4×4 torus:
  `P(2,3) ≥ 7` and `P(3,3) ≥ 10` (all 65536). [attempt 013]
- **P3** `sharp_*` — the single-defect config attains each floor exactly
  (`P=5,7,10`), so all the above floors are **sharp**.

1D Morse–Hedlund sharp floor "primitive necklace ⇒ `p(n) ≥ n+1`":
- **P4** `mh_L6_n2`, `mh_L6_n3` — length-6 binary necklaces: `p(2) ≥ 3`,
  `p(3) ≥ 4` (all 64). [attempt 013] Upgrades E1 to `[PROVEN]` for L=6.

These upgrade experiments E1/E2 (specific sizes/windows) from `[EXPERIMENTAL]` to
`[PROVEN]`. **They beat no `[CITED]` record** (elementary finite instances), so
they are checkpoints, not termination.

### `[PROVEN]` by genuine SYMBOLIC proof (not enumeration) — `lean/NivatTheory.lean`

Unlike the `native_decide` theorems above (which check finite cases by brute
force), this is a **general theorem proved by mathematical reasoning**, valid for
all configurations and all period sizes, depending only on the kernel logic axioms
`[propext, Quot.sound]` (no `native_decide`, no `sorry`), built from Lean core with
no mathlib/Batteries.

- **P5 `periodic_pair_PatternLE`** — *periodicity bounds complexity*: if a
  configuration `x` has periods `(p,0)` and `(0,q)` with `p,q ≥ 1`, then
  `P_x(m,n) ≤ p·q` for **every** window `(m,n)`. This is the provable converse
  direction of the complexity–periodicity correspondence that Nivat's conjecture
  is the hard side of. Supporting lemmas (also proved): `windowAt_add_period`,
  `windowAt_nsmul`, `windowAt_zmul` (window invariant under integer multiples of a
  period), `reduce_h`/`reduce_v`/`reduce_pair` (anchor reduces mod `(p,q)`).

  **Not** Nivat and **not** a `[CITED]` record beat — it is the elementary/tractable
  direction. But it is real symbolic mathematics, machine-checked. Checkpoint.

- **P6 `nivat_bound_sharp`** (sharpness — *fully general, symbolic*) — **Nivat's
  bound `m·n` is optimal: it cannot be relaxed to `m·n + 1`.** Proved as the
  conjunction of:
  - `sd_aperiodic` — the single-defect config `sd` (colour `1` at the origin, `0`
    elsewhere) is **aperiodic** (no nonzero period; a period would force the defect
    to repeat), and
  - `sd_PatternLE` — `P_sd(m,n) ≤ m·n + 1` for **every** window (every window is
    all-zero or has the defect in exactly one of its `m·n` cells; uses the
    cell-encoding injectivity lemma `encode_inj`).

  So there is an aperiodic configuration meeting `P ≤ m·n+1` — the honest reason
  the conjecture's hypothesis is `≤ m·n`, not `≤ m·n+1`. General ∀ m,n, proved by
  reasoning (no enumeration).

- **P7 `PatternLE_mono_K`, `PatternLE_restrict_row`, `PatternLE_restrict_col`** —
  block complexity is **monotone**: `P ≤ K ⇒ P ≤ K'` for `K ≤ K'`, and
  `P_x(m,n) ≤ P_x(m+1,n)`, `P_x(m,n) ≤ P_x(m,n+1)` (bigger windows have at least as
  many patterns). Symbolic proofs (template embedding / truncation).

  All of P5–P7 depend only on `[propext, Quot.sound]` (P6 only `[propext]`); no
  `native_decide`, no `sorry`. Genuine general lemmas — checkpoints, no record beaten.

The **infinite conjecture is now stated and COMPILED mathlib-free**
(`lean/Nivat.lean`, attempt 014): `P_x(m,n) ≤ K` is encoded as a K-template
covering (no `Set.ncard`), so no mathlib is needed. `NivatConjecture` is stated
(open, not asserted); the sanity lemmas `const_periodic`, `const_PatternLE_one`,
`not_PatternLE_zero` are **proved with zero axioms, zero `sorry`**. mathlib itself
could not be obtained (all routes egress-blocked — see `SORRIES.md`), so this is
the mathlib-free equivalent, not a mathlib build.

## `[EXPERIMENTAL]` — verified by code in `experiments/`, outputs in `experiments/out/`

- **E1 (1D Morse–Hedlund, sharp).** Over all binary primitive necklaces of
  length `L ≤ 18`, factor complexity satisfies `p(n) ≥ n+1` for every `1 ≤ n < L`,
  and this is sharp: `min p(n) = n+1` exactly. So the 1D threshold `p(n) ≤ n ⟹
  periodic` is tight. Script: `experiments/mh_1d.py`. Core primitives tested in
  `experiments/nivat_core_test.py`.

- **E2 (2D threshold on tori, sharp).** For every tested binary torus
  `Z_N × Z_M ∈ {3×3, 3×4, 4×4, 3×5}` and every window `(m,n)` **strictly smaller
  than the torus in both dimensions** (`m<N` and `n<M`), the minimum block
  complexity over *primitive* configurations (those with trivial period subgroup)
  is **exactly `mn + 1`** — i.e. `gap = min P(m,n) − mn = +1`, never `0` or
  negative. So on finite tori a genuinely-aperiodic configuration must spend
  `P(m,n) ≥ mn+1`, and the bound `mn` is exactly the sharp threshold, achieved.
  Script: `experiments/torus_search.py`, output `out/torus_search.json`.

- **E3 (finite-vs-infinite caveat).** Windows that fully wrap one torus dimension
  (`m=N` or `n=M`) can hit `gap = 0`; this is a 1D artifact of the wrap, not a
  Nivat statement, and is excluded from E2. Documented in `torus_search.py`.

- **E4 (z3 non-existence, scaling beyond brute force).** See
  `out/sat_search.txt`: for the tested `(N,M,a,m,n)`, z3 reports whether a
  *primitive* configuration with `P(m,n) ≤ mn` exists; every returned SAT witness
  is re-verified with `nivat_core` before being reported. (Verdicts recorded in
  `attempts/INDEX.md`.)

- **E5 (extremal structure, attempt 009).** The minimal-complexity aperiodic
  object is the **single-defect** config (one minority cell in a constant field):
  primitive with `P(m,n) = mn+1` on **every** torus tested up to `100×100` and for
  windows `2×2,2×3,3×3,3×4`. The `mn+1` floor is thus attained **uniformly in `N`**.
  Extremals are not unique (2–4-cell defects also attain it).
  → `experiments/extremal.py`, `out/extremal.{txt,json}`,
  `out/single_defect_uniform.txt`.

- **E6 (uniform-floor lower bound, attempt 010).** z3 confirms **no** primitive
  binary config with `P(2,2) ≤ 4 = mn` exists for `N = 5,6,7,8,9,10,11`
  (UNSAT); `N = 12` returns UNKNOWN (solver timeout, not a solution). Combined with
  E5 this pins the floor at exactly `mn+1` over the whole tested range.
  → `experiments/sat_nd.py` (leaner Bool encoding, validated against `sat_search`),
  `out/sat_nd.txt`.

## `[CITED]` — see `LANDSCAPE.md` for full entries and retrieval URLs

- Nivat's conjecture: Nivat, ICALP 1997 (via secondary sources).
- Morse–Hedlund 1938 (1D base case).
- Sander–Tijdeman: `P(2,n) ≤ 2n ⟹ periodic` (line A, `k=2`).
- arXiv:2606.10193 (2026): `P(4,n) ≤ 4n ⟹ periodic` (line A record `k=4`).
- Cyr–Kra, arXiv:1208.4090, Trans. AMS 2015: `P ≤ mn/2 ⟹ periodic` (line B, `c=1/2`).
- Quas–Zamboni `mn/16`, Epifanio–Koskas–Mignosi `mn/144` (line B, historical; summary-sourced).
- Kari–Szabados, arXiv:1510.00177: periodic decomposition + asymptotic Nivat.
- Szabados, arXiv:1710.05360: Nivat for sums of **two** periodic configs (line C, `t=2`).

## `[CONJECTURED]` / `[HEURISTIC]` — ours, unproven

- **H1.** The E2 pattern (`min P(m,n) = mn+1` for primitive configs, interior
  windows) persists for all `N,M` and alphabets — i.e. the *uniform finite form*
  "aperiodic-at-scale ⇒ `P(m,n) ≥ mn+1`" holds. This is a **strengthening** of
  Nivat's sharpness, tested only on small cases. NOT relied upon anywhere.
- **H2.** The extremal configs achieving `mn+1` are 2D analogues of Sturmian
  words (minimal-complexity aperiodic). Observed in witnesses; not characterized.
