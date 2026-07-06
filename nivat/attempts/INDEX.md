# attempts/INDEX.md — (target, approach) → verdict cache

Consulted before every attempt; re-running a listed (target, approach) is banned.

**Environment caveat (updated at #012):** the official Lean hosts are
egress-blocked, but a mathlib-free Lean 4.10.0 toolchain was pulled via the Docker
mirror (`lean/pull_lean.sh`), so `[PROVEN]` **is** now reachable for *finite*
facts (see #012). It is **not** reachable for the frontier lines (A)/(B)/(C):
those are universal/infinite statements no `native_decide` can settle, and no new
mathematical idea was found — so none can terminate the loop. Walls are recorded
where actually hit — an honest, un-padded list, not a march to 300.

| # | line | target | approach | verdict | note |
|---|------|--------|----------|---------|------|
| 001 | base | 1D Morse–Hedlund sharpness | exhaustive necklaces `L≤18` | **confirmed (checkpoint)** | E1: `min p(n)=n+1`; reproduces base case, no improvement |
| 002 | base | 2D threshold sharp on tori | exhaustive enum `≤4×5` binary | **confirmed (checkpoint)** | E2: `min P(m,n)=mn+1` interior windows |
| 003 | base | scale E2 past brute force | z3 non-existence `5×5…7×7` | **confirmed (checkpoint)** | E4: `P(2,2)≤4` UNSAT, etc. |
| 004 | A | `k=2` Sander–Tijdeman | reproduce on tori | **reproduced (checkpoint)** | not an improvement; record is `k=4` |
| 005 | A | `k=5` (`P(5,n)≤5n⟹periodic`) | finite computational filter | **obstacle** | infinite implication; finite tori can't establish it; no prover |
| 006 | B | `c>1/2` (beat Cyr–Kra) | near-counterexample search on tori | **obstacle** | finite search bounds only the finite picture; proof needs subdynamics + Lean |
| 007 | C | `t=3` components | build sums of 3 periodics, measure | **obstacle** | universal algebraic statement; needs Nullstellensatz proof + Lean |
| 008 | strengthen | H1: uniform `min P=mn+1` all sizes | z3 sweep over sizes | **partial support** | holds on all tested sizes; not a frontier record (a new strengthening, unproven) |
| 009 | base/strengthen | structure of `P=mn+1` extremals | exhaustive enum `≤4×5` | **confirmed (checkpoint)** | single-defect config attains `mn+1` for ALL N (uniform achievability); extremals not unique. `experiments/extremal.py` |
| 010 | strengthen | H1 uniformity at larger N | z3 sweep `P(2,2)≤4`, N=9..14 | **partial support** | UNSAT to N=11, UNKNOWN at 12; `attempts/010`, `experiments/sat_nd.py` |
| 011 | context (planarity) | 2D vs 3D dimensional gap on finite tori | z3: primitive `P(2,2,2)≤8`? | **obstacle / inconclusive** | 3D UNKNOWN even at 280s; gap may be infinite-only; `attempts/011` |
| 012 | base (formal) | machine-check E2 finite instances | pull Lean via Docker mirror; `native_decide` | **PROVEN (checkpoint)** | `floor_3x3`/`floor_4x4` etc., 0 sorry, axioms=`ofReduceBool`; beats NO record; `attempts/012`, `lean/NivatFinite.lean` |
| 013 | base (formal) | broaden proven coverage: more windows + 1D | generic window; `native_decide` | **PROVEN (checkpoint)** | `floor_4x4_w23/w33` (P≥7,10), `mh_L6_*` (1D E1); still beats NO record; `attempts/013` |
| 014 | base (formal) | get mathlib → compile infinite statement | mathlib unobtainable; mathlib-free K-template encoding | **PROVEN (checkpoint)** | mathlib all-routes-blocked; `Nivat.lean` compiles mathlib-free, sanity lemmas 0 axioms/0 sorry; beats NO record; `attempts/014` |
| 015 | converse (symbolic) | periodicity ⇒ complexity ≤ p·q, GENERAL | real proof: shift-invariance + ℤ-induction + mod reduction | **PROVEN, symbolic (checkpoint)** | `periodic_pair_PatternLE`, axioms `[propext,Quot.sound]` (NO native_decide), 0 sorry; not enumeration; beats NO record; `attempts/015`, `lean/NivatTheory.lean` |
| 016 | complexity theory + sharpness | monotonicity + aperiodic witness | symbolic proofs (embedding/truncation; defect argument) | **PROVEN, symbolic (checkpoint)** | `sd_aperiodic`, `PatternLE_mono_K`, `PatternLE_restrict_row/col`; `[propext(,Quot.sound)]`, 0 sorry; beats NO record; `attempts/016` |

**Standing.** A mathlib-free Lean verifier was obtained (Docker mirror, #012), so
`[PROVEN]` is reachable and used — for finite facts by `native_decide` (#012–014)
and for GENERAL theorems by genuine symbolic proof (#015–016: a small block-complexity
theory). None of these beats a `[CITED]` record: the frontier targets (005/006/007)
are the universal/infinite statements at the research frontier (`k=5`, `c>1/2`,
`t=3`), each behind expert machinery, and no new mathematical idea was found to
settle one. So the loop does not terminate. Padding to `MAX_ATTEMPTS=300` with
throwaway stabs is banned; the honest count is what is above.
