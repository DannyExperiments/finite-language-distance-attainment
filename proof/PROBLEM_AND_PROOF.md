# Problem and proof outline

For a finite nonempty alphabet $\Sigma$ and two expressions with finite language constants, Boolean operations, and left concatenation by finite constants, decide whether a finite language assignment has $d_2$ distance at most a supplied rational $p\ge0$. [Full proof](../paper/manuscript.pdf) · [Original question](https://lat.inf.tu-dresden.de/research/theses/2019/Marantidis-Diss-2019.pdf#page=117)

1. Label words by vectors of variable-membership bits. At word $w$, membership in an expression depends only on a bounded prefix of $w$, its capped length, and the action bits at $w$ and a bounded suffix history. These data form a finite controller.
2. Discounted Bellman minimization gives exact rational values. The weight of each child of a node is $(2|\Sigma|)^{-1}$ times that of the node. The sum of relative child weights is $1/2$. A weighted telescoping identity expresses the excess cost over the root value as a sum of nonnegative local gaps. Every summand has positive weight.
3. A finite optimal assignment exists exactly when one can choose optimal actions that are all zero beyond one common depth. Find the greatest set $Z$ that allows an optimal zero-only subtree. Starting from $Z$, repeatedly add a state when some optimal action has all children already included. The root is eventually added exactly when a finite optimal assignment exists.
4. For a threshold above the infimum, truncate a minimizing unrestricted assignment at sufficient depth. Below the infimum no assignment works. At equality apply the finite cutoff test.
