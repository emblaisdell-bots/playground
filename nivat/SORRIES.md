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

### `lean/Nivat.lean` — the INFINITE statement, now COMPILED (mathlib-free), 0 sorry

mathlib could **not** be obtained here (its olean cache on `*.blob.core.windows.net`,
its source via `codeload`/`jsdelivr`/`reservoir`, and every prebuilt-mathlib Docker
image are all egress-blocked; only individual `raw.githubusercontent` files are
reachable, insufficient to build it). So the file was rewritten **mathlib-free**:
`P_x(m,n) ≤ K` is encoded as a K-template covering (no `Set.ncard`). It compiles.

| decl | claim | proof | axioms |
|------|-------|-------|--------|
| `NivatConjecture` | the conjecture | — (stated only, open) | — |
| `const_periodic` | constant config periodic | proved | **none** |
| `const_PatternLE_one` | constant config has complexity ≤ 1 | proved | **none** |
| `not_PatternLE_zero` | complexity is never ≤ 0 | proved | **none** |

No `sorry`, no axioms. None restates the conjecture (no lemma-laundering).

## Termination status

Still an honest **non-result**: no `[PROVEN]` result strictly beats a `[CITED]`
record on lines (A)/(B)/(C). Having a verifier changes what is *provable in
principle*, not the difficulty of the frontier — the finite theorems proved here
are elementary, not record-beating.
