# SORRIES — ledger of every unproven assumption

Per the Honesty Contract: every `sorry` (and, here, every uncompiled Lean
declaration) is logged with what it assumes, why it is unproven, and whether it
hides the core difficulty. A `sorry` whose statement is just the goal is BANNED.

## Environment-level `sorry` (the big one)

**No Lean toolchain is available in this environment.** `elan`/`lake`/`lean`/
`mathlib` cannot be installed: the egress policy returns HTTP 403 (policy denial,
not retryable) for both `github.com` releases and `release.lean-lang.org`. Verified
this session:

```
403  https://github.com/leanprover/elan/releases/latest/download/elan-...tar.gz
403  https://github.com/leanprover/lean4/releases
403  (CONNECT) release.lean-lang.org:443
```

Consequence: **no declaration in `lean/` has been compiled.** Nothing in this
project may carry the `[PROVEN]` tag. Every Lean `theorem ... := by sorry` below
is unproven *and* unchecked-for-typo. This is disclosed at the top of
`lean/Nivat.lean`.

## Per-declaration ledger (`lean/Nivat.lean`)

| decl | what it claims | strictly easier than Nivat? | hides core difficulty? | status |
|------|----------------|------------------------------|------------------------|--------|
| `NivatConjecture` | the conjecture itself | — (it IS the target) | — | statement only, no proof attempted |
| `const_periodic` | a constant config is periodic | yes (trivial) | no | `sorry`, uncompiled |
| `P_one_one_le` | `P(1,1) ≤ card A` | yes (trivial) | no | `sorry`, uncompiled |
| `periodic_bounded_complexity` | periodic ⇒ complexity bounded in one direction | yes | no | `sorry`, uncompiled |

None of these sorries restates the goal `NivatConjecture` (no lemma-laundering).
They are genuine, strictly-weaker sanity checks whose only reason for being
`sorry` is the absence of a compiler — not a hidden difficulty.

## What this means for termination

Formal TERMINATION (a `[PROVEN]` strict improvement over a `[CITED]` record) is
**impossible in this environment** because the verifier cannot be installed.
All positive results here are `[EXPERIMENTAL]`. See `RESULT.md`.
