# Attempt 010 — the uniform `mn+1` floor (line: strengthen / toward B)

**Target (strengthening H1, NOT a cited record).** Is the sharp finite floor
"primitive ⇒ `P(m,n) ≥ mn+1`" **uniform in torus size `N`**? Uniformity is exactly
the bridge a finite→infinite argument would need; if it held for all `N` it would
essentially give Nivat's sharpness — so H1 is treated as a `[CONJECTURED]`
strengthening, never used as a lemma (no laundering).

**Approach — both sides of the floor.**
- *Achievability (upper side).* Direct construction: the single-defect config
  (one `1` in a field of `0`). `experiments/out/single_defect_uniform.txt`.
- *Lower bound.* z3 non-existence of a primitive config with `P(2,2) ≤ 4 = mn`,
  swept over torus sizes. `experiments/sat_nd.py` → `out/sat_nd.txt`.

**Findings [EXPERIMENTAL].**
- **Achievability holds uniformly.** The single-defect config is primitive with
  `P(m,n) = mn+1` for every size tested up to `100×100`, and for windows `2×2,
  2×3, 3×3, 3×4` (all give exactly `mn+1`). Elementary reason (informal, not
  `[PROVEN]`): the patterns are the all-constant one plus the `mn` windows each
  covering the lone defect at a distinct offset, `= mn+1`; and any nonzero shift
  moves the unique defect, so there is no nonzero period.
- **Lower bound holds up to `11×11`.** `P(2,2) ≤ 4` is **UNSAT** for
  `N = 5,6,7,8` (from attempt 003 / `sat_search.py`) and `N = 9,10,11`
  (`sat_nd.py`). At `N = 12` z3 returns **UNKNOWN** (90 s timeout on 144 Bool
  cells) — a solver limit, *not* evidence of a low-complexity primitive config.

**Verdict: partial support (checkpoint).** Both sides agree: the floor is exactly
`mn+1` and is attained for all tested `N` with no counterexample found. This is
consistent `[EXPERIMENTAL]` evidence for H1, **not** a proof and **not** a beat of
any `[CITED]` record. It does not terminate the loop. The honest gap: the lower
bound is only machine-confirmed to `N=11`; a uniform statement needs a proof
(hence a verifier), which this environment cannot provide.
