# FRONTIER — the three target lines, current records, best attempt

> A result terminates the loop only if it is `[PROVEN]` (Lean, 0 sorry) AND
> strictly beats a `[CITED]` record. **In this environment no Lean toolchain is
> installable (egress-blocked), so no line can be terminated.** Below: the record
> on each line, the exact target to beat it, and how close the *experimental*
> probes here could get (they cannot prove; they filter/confirm).

## (A) Window width `k` — `P(k,n) ≤ k·n ⟹ periodic`

- **Record `[CITED]`:** `k = 4` — arXiv:2606.10193 (2026), `P(4,n) ≤ 4n ⟹
  periodic`. (Sander–Tijdeman established `k=2`.)
- **Target to beat:** `k = 5`, `P(5,n) ≤ 5n ⟹ periodic`, for **all** `n` and all
  alphabets — an infinite statement.
- **Best attempt here (experimental):** reproduced `k=2` on tori (E2/E4:
  primitive configs need `P(2,n) ≥ 2n+1`, consistent with Sander–Tijdeman) and
  confirmed `min P(2,2)=5` up to `7×7` via z3. A finite computation **cannot**
  establish the `k=5` universal implication, and no prover is available to.
  **Verdict: obstacle — out of reach without a verifier; not attempted as a proof.**

## (B) Complexity threshold `c` — `P(m,n) ≤ c·m·n ⟹ periodic`

- **Record `[CITED]`:** `c = 1/2` — Cyr–Kra, arXiv:1208.4090 (Trans. AMS 2015).
- **Target to beat:** any fixed `c > 1/2` (toward the full `c=1`).
- **Best attempt here (experimental):** E2 shows the *sharp finite* fact `min
  P(m,n) = mn+1` for primitive interior windows — i.e. below `mn+1` forces a
  period on tori. That is about `c` near `1`, but as a **finite/torus** statement
  it does not contradict-or-prove the infinite conjecture, and it is not a proof
  of any `c`. Closing the gap `1/2 → 1` requires the expansive-subdynamics or
  algebraic machinery plus a prover. **Verdict: obstacle — no proof route without
  Lean; experiments only bound the finite picture.**

## (C) Kari–Szabados components `t` — Nivat for sums of `t` periodic configs

- **Record `[CITED]`:** `t = 2` — Szabados, arXiv:1710.05360 (LATA 2018).
- **Target to beat:** `t = 3`.
- **Best attempt here (experimental):** one can *build* sums of 2 or 3 periodic
  configs and measure complexity, but the theorem is a universal implication over
  the algebraic structure (annihilator/Nullstellensatz), not a finite check.
  **Verdict: obstacle — needs the algebraic proof + a verifier.**

## Standing

No line beaten. A mathlib-free Lean verifier was obtained (via Docker mirror,
`lean/pull_lean.sh`), so the finite sharp-threshold facts are now **`[PROVEN]`**
(`lean/NivatFinite.lean`: `floor_3x3`, `floor_4x4`) — but these are elementary
finite instances that beat **no** record. The frontier lines are universal/infinite
implications a `native_decide` cannot settle; no new mathematical idea was found.
Together with the `[EXPERIMENTAL]` theory (E1–E6: 1D/2D thresholds sharp, extremal
configs, z3 non-existence), this is a checkpoint, not termination.
