/-
  Nivat.lean — formal STATEMENT of Nivat's conjecture, MATHLIB-FREE and COMPILED.

  Compile:  lean Nivat.lean   (exit 0).  Verified under the Lean 4.10.0 toolchain
  extracted via lean/pull_lean.sh.  mathlib itself could not be obtained in this
  environment (its olean cache on *.blob.core.windows.net, its source via
  codeload/jsdelivr/reservoir, and every prebuilt-mathlib Docker image are all
  egress-blocked; only individual raw.githubusercontent files are reachable, which
  is insufficient to build it).  So instead of mathlib's `Set.ncard`, we encode the
  complexity bound "P_x(m,n) ≤ K" by a **K-template covering** — exactly the
  encoding used by the z3 experiments — which needs no cardinality library:

      P_x(m,n) ≤ K   ⟺   ∃ K templates such that every m×n window equals one of them.

  This is a faithful statement of the conjecture using only Lean core.  The
  conjecture itself is stated as a `def : Prop` (NOT asserted/proved — it is open);
  the accompanying sanity lemmas ARE proved (no `sorry`), validating the encoding.
-/

namespace Nivat

/-- A configuration: a coloring of the integer plane by a finite alphabet `A`. -/
abbrev Config (A : Type) := Int × Int → A

/-- The `m × n` window of `x` anchored at `p`, as a function on `Fin m × Fin n`. -/
def windowAt {A : Type} (x : Config A) (m n : Nat) (p : Int × Int) :
    Fin m × Fin n → A :=
  fun q => x (p.1 + ((q.1 : Nat) : Int), p.2 + ((q.2 : Nat) : Int))

/-- Block-complexity bound, cardinality-free: `P_x(m,n) ≤ K` means there is a family
    of `K` template patterns covering every window of `x`. -/
def PatternLE {A : Type} (x : Config A) (m n K : Nat) : Prop :=
  ∃ T : Fin K → (Fin m × Fin n → A), ∀ p : Int × Int, ∃ k : Fin K, windowAt x m n p = T k

/-- `x` is periodic: some NONZERO integer vector `v` is a period. -/
def Periodic {A : Type} (x : Config A) : Prop :=
  ∃ v : Int × Int, v ≠ (0, 0) ∧ ∀ p : Int × Int, x (p.1 + v.1, p.2 + v.2) = x p

/-- **Nivat's conjecture** (open). If some `m,n ≥ 1` give `P_x(m,n) ≤ m·n`, then `x`
    is periodic. Stated only — not asserted here. -/
def NivatConjecture (A : Type) : Prop :=
  ∀ (x : Config A) (m n : Nat), 1 ≤ m → 1 ≤ n → PatternLE x m n (m * n) → Periodic x

/-! ### Sanity lemmas (PROVED, no `sorry`) — they validate the encoding.
     None is close to the conjecture, so there is no lemma-laundering. -/

/-- A constant configuration is periodic (period `(1,0)`). -/
theorem const_periodic {A : Type} (a : A) : Periodic (fun _ => a) := by
  refine ⟨(1, 0), ?_, ?_⟩
  · decide
  · intro p; rfl

/-- A constant configuration has complexity `≤ 1` for every window: the single
    constant pattern covers all windows. (A "periodic ⇒ low complexity" check.) -/
theorem const_PatternLE_one {A : Type} (a : A) (m n : Nat) :
    PatternLE (fun _ => a) m n 1 := by
  refine ⟨fun _ => (fun _ => a), ?_⟩
  intro p; exact ⟨0, rfl⟩

/-- Complexity is never `≤ 0`: there is always a window (at the origin), but `Fin 0`
    is empty. So the hypothesis of Nivat with `K = 0` (i.e. `m·n = 0`) is vacuous,
    matching the side condition `m,n ≥ 1`. -/
theorem not_PatternLE_zero {A : Type} (x : Config A) (m n : Nat) :
    ¬ PatternLE x m n 0 := by
  rintro ⟨_, hT⟩
  obtain ⟨k, _⟩ := hT (0, 0)
  exact k.elim0

end Nivat
