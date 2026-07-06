/-
  NivatTheory.lean — a GENERAL theorem proved by symbolic reasoning (no
  enumeration, no `native_decide`), mathlib-free, under the extracted Lean 4.10.0.

  Main result (`periodic_pair_PatternLE`): a configuration with periods (P,0) and
  (0,Q), P,Q ≥ 1, has block complexity  P_x(m,n) ≤ P·Q  for EVERY window — i.e.
  periodicity bounds complexity.  This is the provable converse direction of the
  complexity–periodicity correspondence that Nivat's conjecture is the hard side of.

  Idea (all proved below, from Lean core only — the environment has no mathlib and
  not even Batteries, so the algebra is built from `Int.mul_add`, `Int.ediv_add_emod`,
  `omega`, and `Int.rec`):
    * the window at an anchor is invariant under shifting the anchor by a period
      (`windowAt_add_period`) and by any INTEGER multiple of it (`windowAt_zmul`);
    * hence every anchor reduces mod (P,Q) to one in [0,P)×[0,Q) (`reduce_pair`);
    * those P·Q anchors form a covering template family, giving `P_x(m,n) ≤ P·Q`.

  Nothing here is Nivat's conjecture or beats a research record; it is a genuine
  general lemma with a genuine symbolic proof.
-/

namespace NivatTheory

abbrev Config (A : Type) := Int × Int → A

def windowAt {A : Type} (x : Config A) (m n : Nat) (p : Int × Int) :
    Fin m × Fin n → A :=
  fun q => x (p.1 + ((q.1 : Nat) : Int), p.2 + ((q.2 : Nat) : Int))

def HasPeriod {A : Type} (x : Config A) (w : Int × Int) : Prop :=
  ∀ p : Int × Int, x (p.1 + w.1, p.2 + w.2) = x p

def PatternLE {A : Type} (x : Config A) (m n K : Nat) : Prop :=
  ∃ T : Fin K → (Fin m × Fin n → A),
    ∀ p : Int × Int, ∃ k : Fin K, windowAt x m n p = T k

/-- Shifting the anchor by a period leaves the window unchanged. -/
theorem windowAt_add_period {A : Type} (x : Config A) (m n : Nat)
    (w p : Int × Int) (h : HasPeriod x w) :
    windowAt x m n (p.1 + w.1, p.2 + w.2) = windowAt x m n p := by
  funext q
  have hp := h (p.1 + ((q.1 : Nat) : Int), p.2 + ((q.2 : Nat) : Int))
  show x ((p.1 + w.1) + ((q.1 : Nat) : Int), (p.2 + w.2) + ((q.2 : Nat) : Int)) = _
  have e1 : (p.1 + w.1) + ((q.1 : Nat) : Int)
          = (p.1 + ((q.1 : Nat) : Int)) + w.1 := by omega
  have e2 : (p.2 + w.2) + ((q.2 : Nat) : Int)
          = (p.2 + ((q.2 : Nat) : Int)) + w.2 := by omega
  rw [e1, e2]; exact hp

/-- Invariance under a NATURAL-number multiple of a period. -/
theorem windowAt_nsmul {A : Type} (x : Config A) (m n : Nat)
    (w : Int × Int) (a b : Int) (h : HasPeriod x w) :
    ∀ t : Nat, windowAt x m n (a + w.1 * (t : Int), b + w.2 * (t : Int))
             = windowAt x m n (a, b) := by
  intro t
  induction t with
  | zero =>
      have h1 : a + w.1 * ((0 : Nat) : Int) = a := by simp
      have h2 : b + w.2 * ((0 : Nat) : Int) = b := by simp
      rw [h1, h2]
  | succ t ih =>
      -- peel one period off the top
      have key := windowAt_add_period x m n w
                    (a + w.1 * (t : Int), b + w.2 * (t : Int)) h
      -- rewrite anchors: a + w.1*(t+1) = (a + w.1*t) + w.1, etc.
      have c1 : a + w.1 * ((t + 1 : Nat) : Int) = (a + w.1 * (t : Int)) + w.1 := by
        have : ((t + 1 : Nat) : Int) = (t : Int) + 1 := by omega
        rw [this, Int.mul_add, Int.mul_one]; omega
      have c2 : b + w.2 * ((t + 1 : Nat) : Int) = (b + w.2 * (t : Int)) + w.2 := by
        have : ((t + 1 : Nat) : Int) = (t : Int) + 1 := by omega
        rw [this, Int.mul_add, Int.mul_one]; omega
      calc windowAt x m n (a + w.1 * ((t + 1 : Nat) : Int), b + w.2 * ((t + 1 : Nat) : Int))
          = windowAt x m n ((a + w.1 * (t : Int)) + w.1, (b + w.2 * (t : Int)) + w.2) := by
              rw [c1, c2]
        _ = windowAt x m n (a + w.1 * (t : Int), b + w.2 * (t : Int)) := key
        _ = windowAt x m n (a, b) := ih

/-- Invariance under any INTEGER multiple of a period. -/
theorem windowAt_zmul {A : Type} (x : Config A) (m n : Nat)
    (w : Int × Int) (a b : Int) (h : HasPeriod x w) :
    ∀ k : Int, windowAt x m n (a + w.1 * k, b + w.2 * k) = windowAt x m n (a, b) := by
  intro k
  -- also need invariance under NEGATIVE multiples: use the period at shifted anchor
  induction k using Int.rec with
  | ofNat t => simpa using windowAt_nsmul x m n w a b h t
  | negSucc t =>
      -- negSucc t = -(t+1).  Shift the base anchor by (t+1) periods and use nsmul:
      --   windowAt(a) = windowAt(a + w*negSucc t)   (the goal, reversed).
      have hb := windowAt_nsmul x m n w
                   (a + w.1 * (Int.negSucc t)) (b + w.2 * (Int.negSucc t)) h (t + 1)
      have hns : (Int.negSucc t : Int) = -((t : Int) + 1) := Int.negSucc_eq t
      have hz : (Int.negSucc t) + ((t + 1 : Nat) : Int) = 0 := by omega
      have e1 : (a + w.1 * (Int.negSucc t)) + w.1 * ((t + 1 : Nat) : Int) = a := by
        have hAB : w.1 * (Int.negSucc t) + w.1 * ((t + 1 : Nat) : Int) = 0 := by
          rw [← Int.mul_add, hz, Int.mul_zero]
        omega
      have e2 : (b + w.2 * (Int.negSucc t)) + w.2 * ((t + 1 : Nat) : Int) = b := by
        have hAB : w.2 * (Int.negSucc t) + w.2 * ((t + 1 : Nat) : Int) = 0 := by
          rw [← Int.mul_add, hz, Int.mul_zero]
        omega
      rw [e1, e2] at hb
      exact hb.symm

/-- **Horizontal reduction.** With period `(p,0)`, the window depends on the first
    coordinate only mod `p`. -/
theorem reduce_h {A : Type} (x : Config A) (m n : Nat) (p : Nat) (i j : Int)
    (h : HasPeriod x ((p : Int), 0)) :
    windowAt x m n (i, j) = windowAt x m n (i % (p : Int), j) := by
  have key := windowAt_zmul x m n ((p : Int), 0) (i % (p : Int)) j h (i / (p : Int))
  have ha : (i % (p : Int)) + ((p : Int), (0 : Int)).1 * (i / (p : Int)) = i := by
    have hd := Int.ediv_add_emod i (p : Int)
    simp only [] at hd ⊢
    omega
  have hb : j + ((p : Int), (0 : Int)).2 * (i / (p : Int)) = j := by simp
  rw [ha, hb] at key
  exact key

/-- **Vertical reduction.** With period `(0,q)`, the window depends on the second
    coordinate only mod `q`. -/
theorem reduce_v {A : Type} (x : Config A) (m n : Nat) (q : Nat) (i j : Int)
    (h : HasPeriod x (0, (q : Int))) :
    windowAt x m n (i, j) = windowAt x m n (i, j % (q : Int)) := by
  have key := windowAt_zmul x m n (0, (q : Int)) i (j % (q : Int)) h (j / (q : Int))
  have ha : i + ((0 : Int), (q : Int)).1 * (j / (q : Int)) = i := by simp
  have hb : (j % (q : Int)) + ((0 : Int), (q : Int)).2 * (j / (q : Int)) = j := by
    have hd := Int.ediv_add_emod j (q : Int)
    simp only [] at hd ⊢
    omega
  rw [ha, hb] at key
  exact key

/-- **Both directions.** With periods `(p,0)` and `(0,q)`, the window is determined
    by the anchor taken mod `(p,q)`. -/
theorem reduce_pair {A : Type} (x : Config A) (m n : Nat) (p q : Nat) (i j : Int)
    (hp : HasPeriod x ((p : Int), 0)) (hq : HasPeriod x (0, (q : Int))) :
    windowAt x m n (i, j) = windowAt x m n (i % (p : Int), j % (q : Int)) := by
  rw [reduce_h x m n p i j hp, reduce_v x m n q (i % (p : Int)) j hq]

/-- **Periodicity bounds complexity.** A configuration with periods `(p,0)` and
    `(0,q)` (`p,q ≥ 1`) satisfies `P_x(m,n) ≤ p·q` for every window `m,n`.
    Proved symbolically — the p·q reduced anchors in `[0,p)×[0,q)` cover all
    windows. -/
theorem periodic_pair_PatternLE {A : Type} (x : Config A) (m n : Nat)
    (p q : Nat) (hp0 : 0 < p) (hq0 : 0 < q)
    (hp : HasPeriod x ((p : Int), 0)) (hq : HasPeriod x (0, (q : Int))) :
    PatternLE x m n (p * q) := by
  refine ⟨fun k => windowAt x m n (((k.val / q : Nat) : Int), ((k.val % q : Nat) : Int)), ?_⟩
  intro P
  have hpi : (0 : Int) < (p : Int) := by exact_mod_cast hp0
  have hqi : (0 : Int) < (q : Int) := by exact_mod_cast hq0
  have hpz : (p : Int) ≠ 0 := by omega
  have hqz : (q : Int) ≠ 0 := by omega
  have hia_nn : 0 ≤ P.1 % (p : Int) := Int.emod_nonneg P.1 hpz
  have hia_lt : P.1 % (p : Int) < (p : Int) := Int.emod_lt_of_pos P.1 hpi
  have hjb_nn : 0 ≤ P.2 % (q : Int) := Int.emod_nonneg P.2 hqz
  have hjb_lt : P.2 % (q : Int) < (q : Int) := Int.emod_lt_of_pos P.2 hqi
  obtain ⟨a, hai⟩ : ∃ a : Nat, (a : Int) = P.1 % (p : Int) :=
    ⟨(P.1 % (p : Int)).toNat, Int.toNat_of_nonneg hia_nn⟩
  obtain ⟨b, hbi⟩ : ∃ b : Nat, (b : Int) = P.2 % (q : Int) :=
    ⟨(P.2 % (q : Int)).toNat, Int.toNat_of_nonneg hjb_nn⟩
  have hapI : (a : Int) < (p : Int) := by rw [hai]; exact hia_lt
  have hap : a < p := by exact_mod_cast hapI
  have hbqI : (b : Int) < (q : Int) := by rw [hbi]; exact hjb_lt
  have hbq : b < q := by exact_mod_cast hbqI
  -- index a*q+b is < p*q
  have h2 : a * q + q = (a + 1) * q := (Nat.succ_mul a q).symm
  have h3 : (a + 1) * q ≤ p * q := Nat.mul_le_mul_right q hap
  have hlt : a * q + b < p * q := by omega
  refine ⟨⟨a * q + b, hlt⟩, ?_⟩
  -- decode the index back to (a,b)
  have hdiv : (a * q + b) / q = a := by
    rw [Nat.add_comm, Nat.add_mul_div_right b a hq0, Nat.div_eq_of_lt hbq, Nat.zero_add]
  have hmod : (a * q + b) % q = b := by
    rw [Nat.add_comm, Nat.add_mul_mod_self_right]
    exact Nat.mod_eq_of_lt hbq
  show windowAt x m n (P.1, P.2)
     = windowAt x m n ((((a * q + b) / q : Nat) : Int), (((a * q + b) % q : Nat) : Int))
  rw [hdiv, hmod, hai, hbi]
  have hPP : (P.1, P.2) = P := rfl
  rw [hPP]
  exact reduce_pair x m n p q P.1 P.2 hp hq

end NivatTheory
