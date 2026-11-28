# Optimal policies with a depth cutoff

[Q311Cutoff.lean](Q311Cutoff.lean) formalizes the subtree argument in Section 4 of the paper. A controller gives the next state for each state, action and letter. At each word address, a policy chooses an action; different branches may use different policies.

- `zero_closed` proves that the everywhere-zero policy is optimal from a state exactly when zero is optimal there and the everywhere-zero policy is optimal from every child.
- `zero_greatest` proves that every set of states closed under optimal zero moves is contained in this zero-only region.
- `layer_iff` proves, for every depth n, that a state belongs to the nth predecessor layer exactly when it admits an optimal policy that uses zero at all addresses of length at least n. The forward proof selects compatible subpolicies for all children, and the converse restricts one policy to each child.

The controller transition and local optimality predicate are explicit parameters. Finite alphabets make bounded-depth support finite. The language-expression compiler, Bellman minimization, positive-weight gap identity, termination of the finite-state iterations and the full decision procedure remain in the paper.

To replay with Lean 4.30.0, run `lean -DwarningAsError=true formalization/Q311Cutoff.lean` from the repository root. The source uses the standard library and reports axiom dependencies. [Workflow](../.github/workflows/lean.yml)
