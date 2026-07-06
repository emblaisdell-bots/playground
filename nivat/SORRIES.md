# SORRIES — ledger of every unproven assumption

Per the Honesty Contract: every `sorry` (and every uncompiled Lean declaration)
is logged with what it assumes, why it is unproven, and whether it hides the core
difficulty. A `sorry` whose statement is just the goal is BANNED.

## Update (toolchain acquired)

The earlier blanket claim "no Lean toolchain is available" is **no longer true**.
A mathlib-free **Lean 4.10.0** toolchain was obtained by pulling the community
Docker image `leanprovercommunity/lean4` through `mirror.gcr.io` (the official
hosts `github.com`/`release.lean-lang.org` remain egress-blocked) and extracting
the `lean`/`lake` binaries from the image layers — see `lean/pull_lean.sh`.

Consequence: **`lean/NivatFinite.lean` is fully machine-checked** — `lean
NivatFinite.lean` exits 0 with **zero `sorry`**. Its four theorems depend only on
the axiom `Lean.ofReduceBool` (the `native_decide` axiom); no `sorryAx`. Evidence:
`lean/out/verify.log`, reproduce with `lean/verify.sh`.

## Ledger

### `lean/NivatFinite.lean` — COMPILED, 0 sorry (all proofs `native_decide`, axiom `ofReduceBool`)

| decl | claim |
|------|-------|
| `floor_3x3`, `floor_4x4` | ∀ primitive config on 3×3 / 4×4 torus, `P(2,2) ≥ 5` (512 / 65536) |
| `floor_4x4_w23`, `floor_4x4_w33` | ∀ primitive 4×4 config, `P(2,3) ≥ 7`, `P(3,3) ≥ 10` |
| `sharp_3x3_w22`, `sharp_4x4_w22/w23/w33` | single-defect config attains each floor (5,7,10) — sharp |
| `mh_L6_n2`, `mh_L6_n3` | ∀ primitive length-6 necklace, `p(2) ≥ 3`, `p(3) ≥ 4` (all 64) |

**`native_decide` caveat (disclosed, not hidden).** These proofs run a compiled
decision procedure and trust the Lean compiler's Bool evaluation via
`Lean.ofReduceBool`, on top of the kernel. That is a strictly larger trusted base
than a pure-kernel `decide` proof — but `decide` overflows the kernel stack on the
`List.eraseDups` reduction here, so it is not available. This is standard practice
and is the honest trusted base for these `[PROVEN]` tags.

**What these do NOT do.** They are elementary *finite* instances (fixed torus
sizes). They are **not** Nivat's conjecture and beat **no** `[CITED]` record, so
they do **not** terminate the frontier loop. They upgrade experiment E2 for the
3×3/4×4 tori to `[PROVEN]` and validate the encoding — a checkpoint.

### `lean/Nivat.lean` — the INFINITE statement, still UNCOMPILED

This file states Nivat's conjecture over `ℤ²` using `Set.ncard` etc., which live
in **mathlib**. We deliberately stayed mathlib-free (per the user), so this file
is **not** compiled and its sanity lemmas remain `sorry`:

| decl | claim | strictly easier than Nivat? | hides core difficulty? | status |
|------|-------|------------------------------|------------------------|--------|
| `NivatConjecture` | the conjecture | — (target) | — | statement only |
| `const_periodic` | constant config periodic | yes | no | `sorry`, needs mathlib |
| `P_one_one_le` | `P(1,1) ≤ card A` | yes | no | `sorry`, needs mathlib |
| `periodic_bounded_complexity` | periodic ⇒ bounded complexity | yes | no | `sorry`, needs mathlib |

None restates the conjecture (no lemma-laundering). To compile these, pull mathlib
too (same Docker route can supply it) and align the toolchain; not done here.

## Termination status

Still an honest **non-result**: no `[PROVEN]` result strictly beats a `[CITED]`
record on lines (A)/(B)/(C). Having a verifier changes what is *provable in
principle*, not the difficulty of the frontier — the finite theorems proved here
are elementary, not record-beating.
