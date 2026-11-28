import Std

namespace FiniteAttainment
variable {Q A I : Type} (step : Q → A → I → Q) (optimal : Q → A → Prop) (zero : A)

/-- At a node with address w, a policy chooses its action from the full history. -/
abbrev Policy (I A : Type) := List I → A

def follow (p : Policy I A) (q : Q) : List I → Q
  | [] => q
  | i :: w => follow (fun v => p (i :: v)) (step q (p []) i) w

def valid (p : Policy I A) (q : Q) : Prop :=
  ∀ w, optimal (follow step p q w) (p w)

def bounded (p : Policy I A) (n : Nat) : Prop :=
  ∀ w, n ≤ w.length → p w = zero

/-- Every word of the subtree can legally use the zero action. -/
def zeroForever (q : Q) : Prop := valid step optimal (fun _ => zero) q

/-- One more level may use a nonzero optimal action; every child must qualify. -/
def layer : Nat → Q → Prop
  | 0, q => zeroForever step optimal zero q
  | n+1, q => ∃ a, optimal q a ∧ ∀ i, layer n (step q a i)

theorem zero_closed (q : Q) :
    zeroForever step optimal zero q ↔
    optimal q zero ∧ ∀ i, zeroForever step optimal zero (step q zero i) := by
  constructor
  · intro h
    exact ⟨h [], fun i w => h (i :: w)⟩
  · rintro ⟨h, hs⟩ (_ | ⟨i,w⟩)
    · exact h
    · exact hs i w

/-- Any set closed under optimal zero moves is contained in zeroForever. -/
theorem zero_greatest (Z : Q → Prop)
    (closed : ∀ q, Z q → optimal q zero ∧ ∀ i, Z (step q zero i))
    (q : Q) (hq : Z q) : zeroForever step optimal zero q := by
  intro w
  induction w generalizing q with
  | nil => exact (closed q hq).1
  | cons i w ih => exact ih _ ((closed q hq).2 i)

/-- The predecessor iteration is exact for policies using only zero at depth n
and beyond. A distinct policy may be selected for each child. -/
theorem layer_iff (n : Nat) (q : Q) :
    layer step optimal zero n q ↔
    ∃ p : Policy I A, valid step optimal p q ∧ bounded zero p n := by
  induction n generalizing q with
  | zero =>
    constructor
    · intro h
      exact ⟨fun _ => zero, h, fun _ _ => rfl⟩
    · rintro ⟨p, hp, tail⟩
      have eq : p = fun _ => zero := funext (fun w => tail w (Nat.zero_le _))
      subst p
      exact hp
  | succ n ih =>
    constructor
    · rintro ⟨a, ha, hs⟩
      have children := fun i => (ih (step q a i)).mp (hs i)
      let p : Policy I A := fun w => match w with
        | [] => a
        | i :: v => (children i).choose v
      refine ⟨p, ?_, ?_⟩
      · rintro (_ | ⟨i,w⟩)
        · exact ha
        · exact (children i).choose_spec.1 w
      · rintro (_ | ⟨i,w⟩) hw
        · simp at hw
        · exact (children i).choose_spec.2 w (Nat.le_of_succ_le_succ hw)
    · rintro ⟨p, hp, tail⟩
      refine ⟨p [], hp [], fun i => (ih _).mpr ?_⟩
      exact ⟨fun w => p (i :: w), fun w => hp (i :: w),
        fun w h => tail (i :: w) (Nat.succ_le_succ h)⟩

#print axioms zero_closed
#print axioms zero_greatest
#print axioms layer_iff
end FiniteAttainment
