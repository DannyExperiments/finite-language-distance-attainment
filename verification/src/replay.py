#!/usr/bin/env python3
"""Rational replay for finite attainment and the discounted word-tree compiler."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from random import Random
import subprocess
import sys
from pathlib import Path

F = Fraction
EPS = ""
EMPTY = ("const", ())
ALL = ("not", EMPTY)
SINGLETON = ("const", (EPS,))
X = ("var", 0)
Y = ("var", 1)


def lengths(expression):
    tag, *args = expression
    if tag == "const":
        return 0, max(map(len, args[0]), default=0)
    if tag == "var":
        return 0, 0
    if tag == "pre":
        depth, size = lengths(args[1])
        return depth + max(map(len, args[0]), default=0), size
    return tuple(map(max, zip(*(lengths(term) for term in args))))


def value(expression, word, labels):
    tag, *args = expression
    if tag == "const":
        return word in args[0]
    if tag == "var":
        return bool(labels.get(word, 0) & (1 << args[0]))
    if tag == "pre":
        prefixes, child = args
        return any(word.startswith(u) and value(child, word[len(u):], labels) for u in prefixes)
    if tag == "not":
        return not value(args[0], word, labels)
    if tag == "or":
        return any(value(term, word, labels) for term in args)
    if tag == "and":
        return all(value(term, word, labels) for term in args)
    raise ValueError(tag)


@dataclass
class Controller:
    alphabet: str
    left: tuple
    right: tuple
    variables: int

    def __post_init__(self):
        self.strip, self.standalone = map(max, zip(lengths(self.left), lengths(self.right)))
        self.head = self.strip + self.standalone
        self.actions = range(1 << self.variables)
        self.beta = F(1, 2 * len(self.alphabet))
        self.root = ("", 0, ())

    def child(self, state, action, letter):
        prefix, depth, history = state
        return ((letter + prefix)[:self.head], min(depth + 1, self.head + 1),
                ((action,) + history)[:self.strip])

    def charge(self, state, action):
        prefix, depth, history = state

        def get(term, offset=0):
            tag, *args = term
            if tag == "const":
                return any(depth == offset + len(u) and prefix[offset:offset + len(u)] == u
                           for u in args[0])
            if tag == "var":
                mask = history[offset - 1] if offset else action
                return bool(mask & (1 << args[0]))
            if tag == "pre":
                words, expr = args
                return any(depth >= offset + len(u) and prefix[offset:offset + len(u)] == u
                           and get(expr, offset + len(u)) for u in words)
            if tag == "not":
                return not get(args[0], offset)
            if tag == "or":
                return any(get(child, offset) for child in args)
            if tag == "and":
                return all(get(child, offset) for child in args)
            raise ValueError(tag)

        return F(get(self.left) != get(self.right), 2)

    def graph(self):
        states = [self.root]
        positions = {self.root: 0}
        rows = []
        for q in states:
            row = []
            for b in self.actions:
                successors = []
                for a in self.alphabet:
                    child = self.child(q, b, a)
                    if child not in positions:
                        positions[child] = len(states)
                        states.append(child)
                    successors.append(positions[child])
                row.append((self.charge(q, b), tuple(successors)))
            rows.append(tuple(row))
        return rows


def affine(pair, values, beta):
    cost, children = pair
    return cost + beta * sum(values[j] for j in children)


def policy_cost(graph, policy, beta):
    n = len(graph)
    matrix = []
    for i, b in enumerate(policy):
        cost, children = graph[i][b]
        row = [F(i == j) for j in range(n)] + [cost]
        for child in children:
            row[child] -= beta
        matrix.append(row)
    for j in range(n):
        k = next(i for i in range(j, n) if matrix[i][j])
        matrix[j], matrix[k] = matrix[k], matrix[j]
        pivot = matrix[j][j]
        matrix[j] = [v / pivot for v in matrix[j]]
        for i in range(n):
            if i != j and matrix[i][j]:
                factor = matrix[i][j]
                matrix[i] = [v - factor * w for v, w in zip(matrix[i], matrix[j])]
    return tuple(row[-1] for row in matrix)


def bellman(graph, values, beta):
    return tuple(min(affine(row, values, beta) for row in options) for options in graph)


def optimum(graph, beta):
    policy = (0,) * len(graph)
    seen = set()
    while policy not in seen:
        seen.add(policy)
        values = policy_cost(graph, policy, beta)
        new = tuple(min(range(len(row)), key=lambda j: affine(row[j], values, beta))
                    if min(affine(pair, values, beta) for pair in row) < values[i]
                    else policy[i] for i, row in enumerate(graph))
        if new == policy:
            assert values == bellman(graph, values, beta)
            return values
        policy = new
    raise AssertionError("strict policy improvement revisited a policy")


def finite_ranks(graph, values, beta):
    candidates = [tuple(b for b, row in enumerate(opts)
                        if affine(row, values, beta) == values[i]) for i, opts in enumerate(graph)]
    z = set(range(len(graph)))
    while True:
        update = {i for i in z if 0 in candidates[i] and set(graph[i][0][1]) <= z}
        if update == z:
            break
        z = update
    ranks = {i: (0, 0) for i in z}
    audit = policy_cost(graph, (0,) * len(graph), beta)
    for depth in range(len(graph) + 1):
        assert ranks.keys() == {i for i, v in enumerate(audit) if v == values[i]}
        new = {}
        for i, options in enumerate(candidates):
            if i in ranks:
                continue
            for b in options:
                if set(graph[i][b][1]) <= ranks.keys():
                    new[i] = (depth + 1, b)
                    break
        if not new:
            break
        ranks.update(new)
        audit = bellman(graph, audit, beta)
    return ranks


def witness(graph, alphabet, ranks):
    witnesses = {}
    pending = [(EPS, 0)]
    while pending:
        word, i = pending.pop()
        rank, action = ranks[i]
        if not rank:
            continue
        if action:
            witnesses[word] = action
        pending.extend((a + word, j) for a, j in zip(alphabet, graph[i][action][1]))
    return witnesses


def word_level(alphabet, depth):
    return ("".join(letters) for letters in product(alphabet, repeat=depth))


def direct_finite_distance(controller, labels):
    # Past depth D only the first strip letters can matter. No stripped
    # suffix can lie in a finite constant or in the supported variable images.
    end = max(controller.head, controller.strip + max(map(len, labels), default=-1)) + 1
    total = F(0)
    for depth in range(end + 1):
        mismatches = sum(value(controller.left, w, labels) != value(controller.right, w, labels)
                         for w in word_level(controller.alphabet, depth))
        charge = F(mismatches, 2) * controller.beta ** depth
        total += 2 * charge if depth == end else charge
    return total


def assert_context(controller, labels, max_depth):
    states = {EPS: controller.root}
    checked = 0
    for depth in range(max_depth + 1):
        for word in word_level(controller.alphabet, depth):
            q = states[word]
            b = labels.get(word, 0)
            assert controller.charge(q, b) == F(value(controller.left, word, labels)
                                                  != value(controller.right, word, labels), 2)
            for letter in controller.alphabet:
                states[letter + word] = controller.child(q, b, letter)
            checked += 1
    return checked


def fixtures():
    both = ("pre", ("a", "b"), X)
    fixtures = [
        ("a", X, ("or", SINGLETON, ("pre", ("a",), X)), 1, F(0), False),
        ("a", ("pre", ("a",), X), ALL, 1, F(1, 2), False),
        ("a", ("or", SINGLETON, X), EMPTY, 1, F(1, 2), True),
        ("a", X, SINGLETON, 1, F(0), True),
        ("ab", both, ALL, 1, F(1, 2), False),
        ("ab", both, ("const", ("", "a", "b")), 1, F(1, 2), True),
        ("a", ("pre", ("a",), ("pre", ("a",), X)), ("const", ("aa",)), 1, F(0), True),
        ("a", ("pre", ("", "a"), X), SINGLETON, 1, F(1, 4), True),
        ("ab", ("and", X, ("not", Y)), ("const", ("ba",)), 2, F(0), True),
        ("ab", ("pre", (), X), ALL, 1, F(1), True),
        ("a", SINGLETON, EMPTY, 0, F(1, 2), True),
        ("a", X, ALL, 1, F(0), False),
    ]
    for sigma, left, right, variables, v, attained in fixtures:
        controller = Controller(sigma, left, right, variables)
        graph = controller.graph()
        values = optimum(graph, controller.beta)
        ranks = finite_ranks(graph, values, controller.beta)
        assert values[0] == v and (0 in ranks) == attained
        if attained:
            assert direct_finite_distance(controller, witness(graph, sigma, ranks)) == v
    print(f"{len(fixtures)} exact infimum and finite-attainment fixtures passed.")


def cutoff_checks():
    both = ("pre", ("a", "b"), X)
    misses = Controller("ab", both, ALL, 1)
    hits = Controller("ab", both, ("const", ("", "a", "b")), 1)
    assert direct_finite_distance(hits, {EPS: 1}) == F(1, 2)
    for h in range(7):
        labels = {w: 1 for i in range(h + 1) for w in word_level("ab", i)}
        assert direct_finite_distance(misses, labels) == F(1, 2) + F(1, 2 ** (h + 2))
    print("Both positive-infimum teaching examples and seven finite cutoffs passed.")


def locality_checks():
    rng = Random(311)
    atoms = (X, Y, EMPTY, SINGLETON, ("const", ("aaa", "bba")))
    def random_term(depth):
        if depth == 0:
            return rng.choice(atoms)
        kind = rng.choice(("not", "and", "or", "pre", "plain"))
        if kind == "plain":
            return rng.choice(atoms)
        if kind == "pre":
            return kind, rng.choice(((), ("",), ("a", "b"), ("", "ab", "aab"))), random_term(depth - 1)
        if kind == "not":
            return kind, random_term(depth - 1)
        return kind, random_term(depth - 1), random_term(depth - 1)

    checked = 0
    for _ in range(80):
        sigma = rng.choice(("a", "ab"))
        labels = {w: rng.randrange(4) for d in range(6) for w in word_level(sigma, d)}
        controller = Controller(sigma, random_term(3), random_term(3), 2)
        checked += assert_context(controller, labels, 6)
    print(f"{checked:,} direct word-membership comparisons across 80 seeded expression pairs passed.")


if __name__ == "__main__":
    fixtures()
    cutoff_checks()
    locality_checks()
    subprocess.run([sys.executable, str(Path(__file__).with_name("controller_audit.py"))], check=True)
    print("PASS: exact rational values, finite witnesses, truncations and controller invariants.")
