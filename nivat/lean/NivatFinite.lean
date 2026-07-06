/-
  NivatFinite.lean — MACHINE-CHECKED finite instances of the Nivat threshold.

  Mathlib-free (Lean 4 core only), so it compiles under a bare toolchain:
      lean NivatFinite.lean      (exit 0 = all theorems checked)

  What is proved here is NOT Nivat's conjecture and beats no research record.
  It is the *finite* sharp-threshold fact from experiment E2 — "a primitive
  (totally aperiodic at scale) configuration on a torus needs block complexity
  P(2,2) >= 5 = mn+1, and 5 is attained" — verified exhaustively for the 3x3
  and 4x4 binary tori. This upgrades those specific experimental findings to
  genuine [PROVEN], and validates that our combinatorial encoding is correct.

  Configurations are indexed by a natural number k whose bit (N*i+j) is the
  color of cell (i,j) on Z_N x Z_N; quantifying k over `Fin (2^(N*N))` keeps
  everything decidable in core Lean (no Finset, no mathlib).
-/

namespace NivatFinite

/-- color of cell (i,j) of the N x N binary torus encoded by `k`. -/
def cell (N k i j : Nat) : Nat := (k / 2 ^ (N * i + j)) % 2

/-- the 2x2 window (with torus wrap) anchored at (i,j), as a 4-element list. -/
def win22 (N k i j : Nat) : List Nat :=
  [cell N k i j,
   cell N k i ((j + 1) % N),
   cell N k ((i + 1) % N) j,
   cell N k ((i + 1) % N) ((j + 1) % N)]

/-- the list of all 2x2 windows occurring in the torus. -/
def patterns22 (N k : Nat) : List (List Nat) :=
  (List.range N).bind (fun i => (List.range N).map (fun j => win22 N k i j))

/-- block complexity P(2,2): number of DISTINCT 2x2 windows. -/
def P22 (N k : Nat) : Nat := (patterns22 N k).eraseDups.length

/-- `(a,b)` is a period of `k`: every cell equals its (a,b)-shift (mod N). -/
def isPeriod (N k a b : Nat) : Bool :=
  (List.range N).all (fun i =>
    (List.range N).all (fun j =>
      cell N k i j == cell N k ((i + a) % N) ((j + b) % N)))

/-- primitive: no NONZERO vector (a,b) in [0,N)x[0,N) is a period. -/
def primitive (N k : Nat) : Bool :=
  (List.range N).all (fun a =>
    (List.range N).all (fun b =>
      (a == 0 && b == 0) || (! isPeriod N k a b)))

/-! ### Proofs by `native_decide`.

    `native_decide` compiles the decision procedure to native code and runs it;
    it is a legitimate proof but it enlarges the trusted base to include the
    Lean compiler and the compiled `cell/P22/primitive` (kernel `decide`
    overflows on the `List.eraseDups` reduction here, so it is not usable).
    Disclosed honestly; noted again in ../SORRIES.md and ../CLAIMS.md. -/

/-- Exhaustive floor check as a tail-recursive Bool over `k = 0 .. cnt-1`:
    "every primitive config has `P(2,2) ≥ fl`".  Using `List.all` (iterative)
    instead of a `∀ k : Fin cnt` instance avoids a depth-`cnt` decidability
    recursion that overflows the stack for large `cnt`. -/
def allPrimHaveFloor (N cnt fl : Nat) : Bool :=
  (List.range cnt).all (fun k => (! primitive N k) || Nat.ble fl (P22 N k))

/-! #### 3x3 torus (2^9 = 512 configurations). -/

/-- The single-defect config (only cell (0,0) = 1) is primitive with P(2,2)=5. -/
theorem single_defect_3x3 : primitive 3 1 = true ∧ P22 3 1 = 5 := by
  native_decide

/-- **Sharp floor, 3x3**, in readable quantified form. Every primitive 3x3 binary
    config has P(2,2) ≥ 5 = mn+1. Exhaustive over all 512 configs. -/
theorem floor_3x3 : ∀ k : Fin 512, primitive 3 k.val = true → 5 ≤ P22 3 k.val := by
  native_decide

/-! #### 4x4 torus (2^16 = 65536 configurations). -/

/-- The single-defect config on 4x4 is primitive with P(2,2)=5. -/
theorem single_defect_4x4 : primitive 4 1 = true ∧ P22 4 1 = 5 := by
  native_decide

/-- **Sharp floor, 4x4.** `allPrimHaveFloor 4 65536 5 = true` says: for every one
    of the 2^16 configs `k`, if `primitive 4 k` then `P22 4 k ≥ 5`. Same content
    as `floor_3x3`, one torus size up. -/
theorem floor_4x4 : allPrimHaveFloor 4 65536 5 = true := by
  native_decide

end NivatFinite
