# LANDSCAPE — Nivat's conjecture, state of the art (Phase 0)

> Every literature line carries a status tag per the Honesty Contract.
> **Sourcing note (important):** this session runs behind an egress proxy whose
> policy **blocks arxiv.org, Wikipedia, Springer, ScienceDirect, semanticscholar,
> combinatorics.org, and github.com web** (all return 403 CONNECT). Package
> registries and `raw.githubusercontent.com` are reachable, and `WebSearch`
> (Anthropic-proxied) works. So each `[CITED]` entry below is grounded in a
> **search result actually returned this session** — authors, title, and arXiv
> id/URL are real and retrieved — but I could **not** fetch the full PDFs.
> Exact constants/theorem numbers are as reported by the search summaries and
> standard attribution, not verified against the paper body. Where a number is
> summary-derived rather than PDF-verified, it is marked "(summary)".

## The statement

A configuration is `x : ℤ² → A`, `A` finite. For `m,n ≥ 1` the rectangular
(block) complexity `P_x(m,n)` is the number of distinct `m×n` patterns occurring
in `x`. `x` is periodic if `∃ v ∈ ℤ²\{0}` with `x(p+v)=x(p)` for all `p`.

**Nivat's conjecture (1997):** if `P_x(m,n) ≤ m·n` for some `m,n ≥ 1`, then `x`
is periodic.

- `[CITED]` Origin: M. Nivat, invited address, ICALP 1997. Standard attribution;
  restated in essentially every source below (e.g. Cyr–Kra arXiv:1208.4090,
  Kari–Szabados arXiv:1510.00177). Full 1997 text not retrieved.
- `[CITED]` Tracked as **DeepMind `formal-conjectures` issue #3907** ("Nivat
  conjecture", status research-open). Retrieved:
  https://github.com/google-deepmind/formal-conjectures/issues/3907

## Why dimension matters (planarity is essential)

- `[CITED]` The 1D base case is **Morse–Hedlund (1938)**: a bi-infinite word with
  `p(n) ≤ n` for some `n` is periodic; equivalently it has period `≤ n` iff
  `p(n) ≤ n`. Universally cited; see any of the sources below.
- `[EXPERIMENTAL]` Verified computationally in `experiments/mh_1d.py`: over **all**
  binary primitive necklaces up to length 18, `p(n) ≥ n+1` for every `n<L`, and
  the bound is sharp (`min p(n) = n+1`). This is the exact 1D shadow of Nivat.
- `[CITED]` For `d ≥ 3` the analogue is **FALSE** — low-complexity aperiodic
  configurations exist — so any correct proof must use a genuinely 2D
  (planarity) argument. Stated in the algebraic-approach literature
  (Kari–Szabados, arXiv:1510.00177) and the surveys returned by search.
  `[CONJECTURED-for-us]` the precise 3D counterexample construction was not
  retrieved this session; do not rely on a specific construction until cited.

## The three frontier lines and their current records

### (A) Window width `k`: `P(k,n) ≤ k·n ⟹ periodic` for fixed small `k`

- `[CITED]` `k = 2` — **Sander & Tijdeman**, "The complexity of functions on
  lattices" (Theoret. Comput. Sci.). `P_x(2,n) ≤ 2n ⟹` periodic. Retrieved:
  https://www.semanticscholar.org/paper/The-complexity-of-functions-on-lattices-Sander-Tijdeman/1d3092fb55a8520752d82f14e4bfa91569ad9200
  Related: "Complexity of short rectangles and periodicity", arXiv:1307.0098.
- `[CITED]` **Current record `k = 4`** — "A Modular Structure Theorem for Minimal
  Periodic Decompositions and Periodicity of Configurations with `P_η(4,n) ≤ 4n`",
  arXiv:2606.10193 (2026). Retrieved: https://arxiv.org/html/2606.10193
  (title/abstract via search; PDF not fetched). This supersedes `k=2,3`.
- **To beat line A:** prove the `k = 5` case (`P(5,n) ≤ 5n ⟹ periodic`).

### (B) Complexity threshold `c`: `P(m,n) ≤ c·m·n ⟹ periodic`

- `[CITED]` `c = 1/144` (summary) — **Epifanio, Koskas, Mignosi**. Reported by
  the search summary of the algebraic-subshifts survey (arXiv:1806.07107) and
  others; PDF not fetched.
- `[CITED]` `c = 1/16` (summary) — **Quas & Zamboni**. Same sourcing as above.
- `[CITED]` **Current record `c = 1/2`** — **Cyr & Kra**, "Nonexpansive ℤ²
  subdynamics and Nivat's conjecture", arXiv:1208.4090, Trans. AMS (2015).
  `P_x(n,k) ≤ nk/2 ⟹` periodic. Retrieved:
  https://arxiv.org/abs/1208.4090 and
  https://sites.math.northwestern.edu/~kra/papers/nivat.pdf (search snippet gave
  the `nk/2` statement).
- `[CITED]` The **algebraic route** (Kari–Szabados, arXiv:1510.00177,
  Inf. Comput. 2019) gives an *asymptotic* Nivat: any non-periodic `x` satisfies
  the low-complexity bound for only finitely many shapes `D`. Retrieved:
  https://arxiv.org/pdf/1510.00177
- **To beat line B:** prove periodicity under `P(m,n) ≤ c·mn` for some fixed
  `c > 1/2` (equivalently `P ≤ mn/K` with `K < 2`), full conjecture is `c = 1`.

### (C) Kari–Szabados components `t`: Nivat for sums of `t` periodic configurations

- `[CITED]` Low-complexity configurations decompose as a **sum of finitely many
  periodic** configurations over ℤ (Kari–Szabados, arXiv:1510.00177).
- `[CITED]` **Current record `t = 2`** — **Szabados**, "Nivat's conjecture holds
  for sums of two periodic configurations", arXiv:1710.05360 (LATA 2018 /
  Springer LNCS). Combines the algebraic approach with Cyr–Kra balanced sets.
  Retrieved: https://arxiv.org/abs/1710.05360
- **To beat line C:** prove Nivat for `t = 3` (sum of three periodic components).

## Adjacent tools worth knowing (all `[CITED]`, search-retrieved)

- Boyle–Lind **expansive subdynamics** — the engine behind Cyr–Kra
  (arXiv:1208.4090).
- **Periodic decompositions / nonexpansive directions**: arXiv:1909.08195,
  arXiv:2204.06658, and the 2023 DCDS paper (aimsciences doi 10.3934/dcds.2023088).
- **Algebraic subshifts / annihilators via Nullstellensatz**: arXiv:1806.07107,
  arXiv:2301.06868.
- "An alphabetical approach to Nivat's conjecture" (researchgate 341844099).

## Where a proof-free agent can actually push

Honest appraisal for this environment (no Lean toolchain available — see
`README.md` §Constraints):

- Lines (A)/(B)/(C) are all active research frontiers whose records were set by
  domain experts using expansive-subdynamics and algebraic (Nullstellensatz)
  machinery. A **machine-checked** strict improvement is not realistically
  reachable here, and without Lean it cannot be `[PROVEN]` even if found.
- The reachable, genuine contribution is **`[EXPERIMENTAL]`**: exact finite
  computation of the threshold, its sharpness, the extremal (Sturmian-like)
  configurations, and z3-certified non-existence of low-complexity primitive
  configs at each tested torus size. That is what `experiments/` delivers.
