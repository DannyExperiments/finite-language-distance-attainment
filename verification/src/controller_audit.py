"""Exhaustive equality/attainment check on unordered binary, two-state controllers."""
from fractions import Fraction as F
from itertools import product

# Row (cost, number of children at state 1). Each of the two children carries weight 1/4.
def affine(row, values):
    cost,k=row
    return F(cost,2)+((2-k)*values[0]+k*values[1])/4

def stationary(rows):
    (v,i),(w,j)=rows
    # Multiply the two discounted policy equations by 4.
    a,b,c,d=2+i,-i,j-2,4-j
    det=a*d-b*c
    return F(2*v*d-2*w*b,det),F(2*w*a-2*v*c,det)

def bellman(rows, values):
    return tuple(min(affine(row,values) for row in opts) for opts in rows)

def children_in(row, allowed):
    _,k=row
    return (k==2 or 0 in allowed) and (k==0 or 1 in allowed)

mix=0
for row_tuple in product(product(range(2),range(3)),repeat=4):
    rows=[row_tuple[:2],row_tuple[2:]]
    policies=list(product(*rows))
    values=next(v for p in policies for v in [stationary(p)] if bellman(rows,v)==v)
    costs=stationary((rows[0][0],rows[1][0]))
    options=[tuple(r for r in rows[i] if affine(r,values)==values[i]) for i in range(2)]
    allowed={0,1}
    for i in range(3):
        allowed={j for j in allowed if rows[j][0] in options[j] and children_in(rows[j][0],allowed)}
    for i in range(4):
        assert allowed=={j for j in range(2) if costs[j]==values[j]}
        costs=bellman(rows,costs)
        allowed|={j for j in range(2) if any(children_in(r,allowed) for r in options[j])}
    if allowed=={0} or allowed=={1}: mix+=1
print('1296 controllers checked; finite-support optimum depends on initial state in',mix,'cases.')
