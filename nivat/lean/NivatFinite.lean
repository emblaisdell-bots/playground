/-
  NivatFinite.lean — MACHINE-CHECKED finite instances of the Nivat / Morse–Hedlund
  sharp threshold.  Mathlib-free (Lean 4 core only):  `lean NivatFinite.lean`.

  Proved here (all by `native_decide`; trusted base = kernel + `Lean.ofReduceBool`,
  disclosed in ../SORRIES.md; zero `sorry`):

    2D, for the sharp floor  "primitive config ⇒ P(wm,wn) ≥ wm·wn + 1":
      * 2×2 window on the 3×3 and 4×4 binary tori   (floor 5)
      * 2×3 window on the 4×4 torus                 (floor 7)
      * 3×3 window on the 4×4 torus                 (floor 10)
      and that each floor is ATTAINED by the single-defect config (sharpness).
    1D Morse–Hedlund sharp floor  "primitive necklace ⇒ p(n) ≥ n+1":
      * length-6 binary necklaces, n = 2 and n = 3.

  None of this is Nivat's conjecture and none beats a [CITED] record — these are
  elementary finite instances that upgrade experiments E1/E2 to [PROVEN] and
  validate the encoding.  A verifier makes finite facts provable; it does not make
  the (infinite) frontier reachable.  See ../RESULT.md.

  A config on the N×N binary torus is encoded by a Nat `k`: bit (N*i+j) = color of
  cell (i,j).  Quantifying `k` over a range with a tail-recursive `List.all`
  (not a `∀ k : Fin _` instance) keeps the decidability shallow enough to compile.
-/

namespace NivatFinite

/-! ## 2D torus -/

/-- color of cell (i,j) of the N×N binary torus encoded by `k`. -/
def cell (N k i j : Nat) : Nat := (k / 2 ^ (N * i + j)) % 2

/-- the `wm × wn` window (torus wrap) anchored at (i,j), flattened to a list. -/
def window (N k wm wn i j : Nat) : List Nat :=
  (List.range wm).bind (fun di =>
    (List.range wn).map (fun dj => cell N k ((i + di) % N) ((j + dj) % N)))

/-- all `wm × wn` windows occurring in the torus. -/
def patterns (N k wm wn : Nat) : List (List Nat) :=
  (List.range N).bind (fun i => (List.range N).map (fun j => window N k wm wn i j))

/-- block complexity `P(wm,wn)`: number of DISTINCT windows. -/
def P (N k wm wn : Nat) : Nat := (patterns N k wm wn).eraseDups.length

/-- `(a,b)` is a period of `k`: every cell equals its (a,b)-shift (mod N). -/
def isPeriod (N k a b : Nat) : Bool :=
  (List.range N).all (fun i =>
    (List.range N).all (fun j =>
      cell N k i j == cell N k ((i + a) % N) ((j + b) % N)))

/-- primitive: no NONZERO vector (a,b) in [0,N)×[0,N) is a period. -/
def primitive (N k : Nat) : Bool :=
  (List.range N).all (fun a =>
    (List.range N).all (fun b =>
      (a == 0 && b == 0) || (! isPeriod N k a b)))

/-- exhaustive sharp-floor check over `k = 0 .. cnt-1` (tail-recursive):
    "every primitive config has `P(wm,wn) ≥ fl`". -/
def allPrimFloor (N wm wn cnt fl : Nat) : Bool :=
  (List.range cnt).all (fun k => (! primitive N k) || Nat.ble fl (P N k wm wn))

/-! ### Sharp floor, 2×2 window. -/

/-- 3×3 torus, readable quantified form (2^9 = 512 configs). -/
theorem floor_3x3_readable :
    ∀ k : Fin 512, primitive 3 k.val = true → 5 ≤ P 3 k.val 2 2 := by
  native_decide

/-- 3×3 torus, Bool form. -/
theorem floor_3x3 : allPrimFloor 3 2 2 512 5 = true := by native_decide

/-- 4×4 torus (2^16 = 65536 configs). -/
theorem floor_4x4 : allPrimFloor 4 2 2 65536 5 = true := by native_decide

/-! ### Sharp floor, larger windows on the 4×4 torus (more of the E2 table). -/

/-- 2×3 window: every primitive 4×4 config has P(2,3) ≥ 7 = 2·3+1. -/
theorem floor_4x4_w23 : allPrimFloor 4 2 3 65536 7 = true := by native_decide

/-- 3×3 window: every primitive 4×4 config has P(3,3) ≥ 10 = 3·3+1. -/
theorem floor_4x4_w33 : allPrimFloor 4 3 3 65536 10 = true := by native_decide

/-! ### The floors are ATTAINED (single-defect config), i.e. sharp. -/

theorem sharp_3x3_w22 : primitive 3 1 = true ∧ P 3 1 2 2 = 5 := by native_decide
theorem sharp_4x4_w22 : primitive 4 1 = true ∧ P 4 1 2 2 = 5 := by native_decide
theorem sharp_4x4_w23 : primitive 4 1 = true ∧ P 4 1 2 3 = 7 := by native_decide
theorem sharp_4x4_w33 : primitive 4 1 = true ∧ P 4 1 3 3 = 10 := by native_decide

/-! ## 1D Morse–Hedlund (the base case Nivat generalizes).

    A cyclic binary word of length L is encoded by `k` (bit i = letter i).
    `primitive1d` = no nonzero rotation is a period (= least period is L). -/

def bit (k p : Nat) : Nat := (k / 2 ^ p) % 2

def factorsAt (L k n i : Nat) : List Nat :=
  (List.range n).map (fun t => bit k ((i + t) % L))

def factors (L k n : Nat) : List (List Nat) :=
  (List.range L).map (fun i => factorsAt L k n i)

/-- factor complexity `p(n)`: number of distinct length-`n` cyclic factors. -/
def p1d (L k n : Nat) : Nat := (factors L k n).eraseDups.length

def isRot (L k s : Nat) : Bool :=
  (List.range L).all (fun i => bit k i == bit k ((i + s) % L))

def primitive1d (L k : Nat) : Bool :=
  (List.range L).all (fun s => (s == 0) || (! isRot L k s))

/-- exhaustive Morse–Hedlund floor: "every primitive necklace has `p(n) ≥ fl`". -/
def mhFloor (L cnt n fl : Nat) : Bool :=
  (List.range cnt).all (fun k => (! primitive1d L k) || Nat.ble fl (p1d L k n))

/-- Length-6 necklaces: every primitive one has p(2) ≥ 3 = 2+1. -/
theorem mh_L6_n2 : mhFloor 6 64 2 3 = true := by native_decide

/-- Length-6 necklaces: every primitive one has p(3) ≥ 4 = 3+1. -/
theorem mh_L6_n3 : mhFloor 6 64 3 4 = true := by native_decide

end NivatFinite
