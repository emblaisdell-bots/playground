# attempts/INDEX.md — (target, approach) → verdict cache

Consulted before every attempt; re-running a listed (target, approach) is banned.

**Environment caveat:** no Lean toolchain (egress-blocked), so every attempt is
an *experimental* probe or a *proof-route assessment*, never a machine-checked
proof. No attempt can reach `[PROVEN]`, hence none can terminate the loop. Walls
are recorded where they were actually hit — this is an honest, un-padded list, not
a march to 300.

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
| 010 | strengthen | H1 uniformity at larger N | z3 sweep `P(2,2)≤4`, N=9..14 | see `attempts/010` | `experiments/sat_nd.py` |
| 011 | context (planarity) | 2D vs 3D dimensional gap | z3: primitive `P(2,2,2)≤8`? | see `attempts/011` | why `d≥3` differs; `experiments/sat_nd.py` |

**Why the list stops here.** The binding wall is environmental and was hit at
setup: with no verifier, no (target, approach) on (A)/(B)/(C) can be carried to a
`[PROVEN]` verdict. The three frontier targets (005/006/007) each also sit behind
a genuine mathematical wall (expert machinery), independently confirmed by the
fact that finite computation cannot express their universal implications.
Padding to `MAX_ATTEMPTS=300` with throwaway stabs is explicitly banned by the
prompt; the honest count is what is above.
