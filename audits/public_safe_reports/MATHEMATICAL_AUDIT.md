# Internal mathematical review

An independent reconstruction checked the exact finite-assignment threshold and the equality argument. For the explicit finite controller let $U_0(q)$ be the value of always choosing zero, found by an exact policy linear solve. Define $U_{h+1}=T(U_h)$ using the Bellman operator. The value $U_h(q)$ is the least cost among assignments whose actions are zero at all nodes of depth at least $h$ below $q$. Because the child coefficients are positive, $U_{h+1}(q)=V(q)$ precisely when some minimizing action sends all children to states with $U_h=V$.

The equality sets increase and thus stabilize. This independently yields the same condition as the paper's zero-invariant set and finite reachability iterations. The [controller replay](../../verification/src/controller_audit.py) checks all 1,296 two-state, two-action, binary-child controllers with unordered child pairs and binary disagreement costs. In 102 controllers the existence of a finite optimal witness depends on the starting state.

Separate tests compare the expression compiler against direct membership and verify the example distances. Exact rational arithmetic suffices for this algorithm. The paper distinguishes the finite support of variables from the potential infinitude of a closed expression, and handles the strict threshold by the already-known equality of infima.
