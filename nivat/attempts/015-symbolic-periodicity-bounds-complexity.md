# Attempt 015 — a GENERAL theorem by symbolic proof (not enumeration)

**Target.** User: "try actual novel symbolic mathematics, not just trying
examples." Prove a *general* theorem about the complexity–periodicity relationship
by real reasoning — valid for all configurations and all period sizes — rather than
`native_decide` over finitely many cases.

**Result — `[PROVEN]` (`lean/NivatTheory.lean`, axioms `[propext, Quot.sound]`
only; no `native_decide`, no `sorry`).**

> **`periodic_pair_PatternLE`.** If a configuration `x : ℤ² → A` has periods
> `(p,0)` and `(0,q)` with `p,q ≥ 1`, then for **every** window `(m,n)`,
> `P_x(m,n) ≤ p·q`.  (Periodicity bounds complexity — the provable converse of the
> direction Nivat's conjecture asks about.)

**Proof structure (all lemmas proved from Lean core — no mathlib, not even
Batteries; algebra built from `Int.mul_add`, `Int.ediv_add_emod`, `Int.rec`,
`omega`):**
1. `windowAt_add_period` — the window at an anchor is unchanged when the anchor is
   shifted by a period `w` (unfold + rearrange with `omega`).
2. `windowAt_nsmul`, `windowAt_zmul` — invariance under any **integer** multiple of
   a period, by induction over ℕ and then over ℤ via `Int.rec` (the negative case
   handled by shifting the base anchor forward `t+1` times).
3. `reduce_h`, `reduce_v`, `reduce_pair` — using `Int.ediv_add_emod`, every anchor
   `(i,j)` satisfies `windowAt (i,j) = windowAt (i mod p, j mod q)`.
4. `periodic_pair_PatternLE` — the `p·q` reduced anchors in `[0,p)×[0,q)` form a
   covering template family (index `a·q+b`, with the `Int→Nat` casts and the Nat
   div/mod decoding proved explicitly), which is exactly `P_x(m,n) ≤ p·q`.

**Verdict: PROVEN, symbolic — checkpoint, NOT termination.** This is genuine
general mathematics, machine-checked by real reasoning rather than case
enumeration. It is the *tractable* direction and beats **no** `[CITED]` record on
(A)/(B)/(C); the hard direction (low complexity ⇒ periodic) is Nivat itself and
remains open. Reproduce: `lean/verify.sh`; evidence `lean/out/verify.log`.
