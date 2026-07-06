/-
  Nivat.lean — formal STATEMENT of Nivat's conjecture (Phase 1).

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  !!!  UNVERIFIED  !!!                                                        │
  │  This file has NOT been compiled. The egress policy of this environment     │
  │  blocks the Lean toolchain distribution hosts (github.com releases and      │
  │  release.lean-lang.org both return HTTP 403 CONNECT — policy denial, not    │
  │  retryable), so `elan`/`lake`/`lean`/`mathlib` could not be installed.      │
  │  Therefore NOTHING here is `[PROVEN]`. This is a best-effort transcription   │
  │  of the statement in mathlib style, provided as scaffolding only. Do not    │
  │  treat any declaration below as machine-checked. See ../SORRIES.md.         │
  └───────────────────────────────────────────────────────────────────────────┘

  Conventions mirror the intent of DeepMind `formal-conjectures` issue #3907
  (Finset cardinality of the pattern set; period = nonzero vector in ℤ²), but
  the exact upstream file was not retrievable this session, so this is our own
  encoding and may differ from theirs.
-/

import Mathlib

open Finset

namespace Nivat

variable {A : Type*} [DecidableEq A]

/-- A configuration: a coloring of the integer plane. -/
abbrev Config (A : Type*) := ℤ × ℤ → A

/-- The `m × n` pattern of `x` anchored at `p` (offsets `0..m-1 × 0..n-1`),
    packaged as a function on `Fin m × Fin n`. -/
def patternAt (x : Config A) (m n : ℕ) (p : ℤ × ℤ) : Fin m × Fin n → A :=
  fun q => x (p.1 + (q.1 : ℤ), p.2 + (q.2 : ℤ))

/-- The set of `m × n` patterns occurring in `x`. -/
def patternSet (x : Config A) (m n : ℕ) : Set (Fin m × Fin n → A) :=
  Set.range (patternAt x m n)

/-- Block complexity `P_x(m,n)`: the number of distinct `m × n` patterns.
    (Uses `Set.ncard`; finite for finite `A`.) -/
noncomputable def P (x : Config A) (m n : ℕ) : ℕ := (patternSet x m n).ncard

/-- `x` is periodic: some NONZERO integer vector `v` is a period. -/
def Periodic (x : Config A) : Prop :=
  ∃ v : ℤ × ℤ, v ≠ 0 ∧ ∀ p, x (p + v) = x p

/-- **Nivat's conjecture.** UNVERIFIED STATEMENT ONLY (no proof; not compiled). -/
def NivatConjecture (A : Type*) [DecidableEq A] : Prop :=
  ∀ (x : Config A) (m n : ℕ), 1 ≤ m → 1 ≤ n → P x m n ≤ m * n → Periodic x

/-!
### Sanity lemmas that WOULD validate the encoding (all UNPROVEN here).

Each is stated as it should be proved once a toolchain is available. They are
logged in ../SORRIES.md. None is a paraphrase of the conjecture, so none is a
banned "goal = statement" sorry; they are genuine, strictly-easier facts.
-/

/-- A constant configuration is periodic (trivial). UNPROVEN. -/
theorem const_periodic (a : A) : Periodic (fun _ : ℤ × ℤ => a) := by
  sorry

/-- `P(1,1) ≤` (number of colors used) ≤ `card A` for `Fintype A`. UNPROVEN. -/
theorem P_one_one_le [Fintype A] (x : Config A) :
    P x 1 1 ≤ Fintype.card A := by
  sorry

/-- If `x` has a nonzero period then `P x m n` is bounded independent of the
    window growing along that period direction (a weak "periodic ⇒ low
    complexity" sanity check). UNPROVEN. -/
theorem periodic_bounded_complexity (x : Config A) (hx : Periodic x) :
    ∃ C, ∀ n, P x 1 n ≤ C := by
  sorry

end Nivat
