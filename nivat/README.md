# nivat/ — an honest attack on Nivat's conjecture

**Nivat's conjecture (1997, open):** for a coloring `x : ℤ² → A` (finite `A`), if
the number of distinct `m×n` patterns satisfies `P_x(m,n) ≤ m·n` for some
`m,n ≥ 1`, then `x` has a nonzero period. It is the 2D analogue of Morse–Hedlund;
false in dimension `≥ 3`, so any proof must use planarity.

## Honest scorecard

| | status |
|---|---|
| Frontier record beaten (A/B/C)? | **No.** |
| `[PROVEN]` (Lean-checked) results? | **None** — the Lean toolchain is **uninstallable** here (see Constraints). |
| Reproducible `[EXPERIMENTAL]` results? | **Yes** — E1–E4 (below), all with tests + saved output. |
| Outcome | Honest **non-result** (safety-valve semantics). `RESULT.md`. |

## Constraints of this environment (the decisive fact)

This session runs behind an egress proxy whose **policy blocks the Lean
distribution hosts** — `github.com` releases and `release.lean-lang.org` both
return HTTP 403 (policy denial, not retryable). So `elan`/`lake`/`lean`/`mathlib`
cannot be installed and **no proof can be machine-checked**. Per the project's
Honesty Contract, `[PROVEN]` therefore cannot be earned and formal termination is
impossible here. Full-text scholarly sites (arxiv, springer, …) are likewise
blocked; `WebSearch` works, so citations rest on real retrieved search metadata
(see `LANDSCAPE.md`). z3 + Python work fully, and are used as the external checker.

To enable the Lean path, an operator would need to allowlist `github.com` (and
`release.lean-lang.org`, `objects.githubusercontent.com`) for this environment.

## What is actually established here (all `[EXPERIMENTAL]`, reproducible)

- **E1** 1D Morse–Hedlund is **sharp**: over all binary primitive necklaces
  `L ≤ 18`, `p(n) ≥ n+1` and `min p(n) = n+1`.  → `experiments/mh_1d.py`
- **E2** 2D threshold is **sharp on tori**: for windows strictly interior to a
  torus, primitive configs have `min P(m,n) = mn+1` (never `≤ mn`).
  → `experiments/torus_search.py`, `out/torus_search.json`
- **E3** caveat: full-wrap windows give a 1D-artifact `gap=0` (excluded from E2).
- **E4** z3 certifies non-existence of low-complexity primitive configs past
  brute force. → `experiments/sat_search.py`, `out/sat_search.txt`

## Reproduce

```bash
cd nivat/experiments
pip install z3-solver
python3 nivat_core_test.py      # correctness of the primitives
python3 mh_1d.py                # E1  (~1 min)
python3 torus_search.py         # E2/E3 (small tori exhaustive)
python3 sat_search.py           # E4  (z3 battery; some instances may time out -> UNKNOWN)
```

## Map of the folder

```
README.md      this file            JOURNAL.md    dated log
LANDSCAPE.md   cited state of art   SORRIES.md    every unproven assumption
CLAIMS.md      tagged claims        FRONTIER.md   3 target lines + records
RESULT.md      final outcome        attempts/     per-attempt verdicts + INDEX.md
lean/          UNVERIFIED statement (no toolchain) — not machine-checked
experiments/   Python + z3, with tests and saved outputs
```

## Resuming with Lean (once the hosts are allowlisted)

The operator opted to enable the Lean path. Network policy is fixed at
environment-creation time, so the change takes effect in a **new
environment/session**, not this running container (re-tested: still 403). To
resume: allowlist `github.com`, `objects.githubusercontent.com`,
`release.lean-lang.org` on the environment, start a fresh session on this branch,
then:

```bash
cd nivat/lean && bash setup.sh     # installs elan+mathlib, builds Nivat.lean
```

`setup.sh`, `lakefile.toml`, and `lean-toolchain` are committed but **untested**
here (no toolchain to test them). Once `lake build Nivat` succeeds, the three
sanity lemmas in `Nivat.lean` can be discharged (removing their `sorry`s and the
banner), and only then can any frontier attempt legitimately earn `[PROVEN]`.

## The honesty rules this project follows

No hidden `sorry`; no lemma that would (if true) prove Nivat unless itself
`[PROVEN]`; no hallucinated literature; "proved" appears only beside `[PROVEN]`
(and there are none). A slick result with a buried gap is worse than no result.
