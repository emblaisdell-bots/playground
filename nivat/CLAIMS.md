# CLAIMS — every claim with an honest status tag

Tags: `[PROVEN]` (Lean, 0 sorry) · `[CITED]` (retrieved source) ·
`[EXPERIMENTAL]` (ran code + saved output) · `[CONJECTURED]`/`[HEURISTIC]` (ours).

There are **zero `[PROVEN]`** claims in this project: the Lean toolchain is
uninstallable here (see `SORRIES.md`), so nothing is machine-checked.

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
