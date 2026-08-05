"""
Day 175 Practice: NP-Completeness & Reductions

6 exercises. Implement TODOs, then run: python practice.py

Exercise 1 is the certificate verifier — the definition of NP. Exercise 2 is
the exponential search it contrasts with. Exercises 3-6 walk the chain:
SAT -> 3-SAT -> CLIQUE -> VERTEX COVER -> INDEPENDENT SET.

Every reduction is tested in BOTH directions. A map that only sends yes to yes
is not a reduction — the constant function does that too.
"""

from itertools import combinations, product


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: verify_sat — why SAT is in NP
# ---------------------------------------------------------------------------

def verify_sat(clauses, assignment):
    """
    True iff `assignment` satisfies every clause. O(total literals).

    A clause is a list of nonzero ints: +v means v, -v means NOT v. A literal l
    is true iff assignment[abs(l)] == (l > 0). Missing variables default to
    False. The empty clause is unsatisfiable — do not accidentally accept it.

    This is the certificate check. Its cheapness is the definition of NP.
    """
    # TODO: implement
    pass


def _sol_verify_sat(clauses, assignment):
    for clause in clauses:
        if not any(assignment.get(abs(l), False) == (l > 0) for l in clause):
            return False
    return True


# ---------------------------------------------------------------------------
# Exercise 2: brute_force_sat — the exponential search
# ---------------------------------------------------------------------------

def brute_force_sat(clauses, nvars):
    """
    Try all 2^nvars assignments; return one that satisfies, else None.

    Return the dict {1: bool, ..., nvars: bool}. Only usable for small nvars —
    that is the point.
    """
    # TODO: implement
    pass


def _sol_brute_force_sat(clauses, nvars):
    for bits in product([False, True], repeat=nvars):
        a = {v + 1: bits[v] for v in range(nvars)}
        if _sol_verify_sat(clauses, a):
            return a
    return None


# ---------------------------------------------------------------------------
# Exercise 3: SAT <=p 3-SAT
# ---------------------------------------------------------------------------

def sat_to_3sat(clauses, nvars):
    """
    Return (clauses3, nvars3) where every clause has exactly 3 literals.

    k=1: (l)     -> (l, +-y1, +-y2) for all 4 sign combinations
    k=2: (l1,l2) -> (l1,l2,y), (l1,l2,-y)
    k=3: unchanged
    k>3: (l1,l2,y1), (-y1,l3,y2), ..., (-y_{k-3}, l_{k-1}, l_k)

    Fresh variables start at nvars+1, allocated in clause order.
    Satisfiability must be PRESERVED, not merely implied — if the original is
    unsatisfiable the result must be too, which is what the chain guarantees.
    """
    # TODO: implement
    pass


def _sol_sat_to_3sat(clauses, nvars):
    out = []
    nxt = nvars + 1

    def fresh():
        nonlocal nxt
        v = nxt
        nxt += 1
        return v

    for clause in clauses:
        k = len(clause)
        if k == 0:
            # Keep the empty clause unsatisfiable, else the map is not an
            # equivalence.
            y = fresh()
            fresh()
            out.append([y, y, y])
            out.append([-y, -y, -y])
        elif k == 1:
            l = clause[0]
            y1, y2 = fresh(), fresh()
            for s1, s2 in product([1, -1], repeat=2):
                out.append([l, s1 * y1, s2 * y2])
        elif k == 2:
            y = fresh()
            out.append([clause[0], clause[1], y])
            out.append([clause[0], clause[1], -y])
        elif k == 3:
            out.append(list(clause))
        else:
            ys = [fresh() for _ in range(k - 3)]
            out.append([clause[0], clause[1], ys[0]])
            for i in range(k - 4):
                out.append([-ys[i], clause[i + 2], ys[i + 1]])
            out.append([-ys[-1], clause[k - 2], clause[k - 1]])
    return out, nxt - 1


# ---------------------------------------------------------------------------
# Exercise 4: 3-SAT <=p CLIQUE
# ---------------------------------------------------------------------------

def three_sat_to_clique(clauses):
    """
    Return (n, edges, labels).

    labels[v] = (clause_index, literal), one vertex per (clause, literal) in
    reading order. `edges` is a set of sorted 2-tuples (u, v) with u < v.

    Edge iff the vertices are in DIFFERENT clauses and their literals are not
    complementary. No edge inside a clause — that is what forces a size-m
    clique to pick exactly one literal per clause.
    """
    # TODO: implement
    pass


def _sol_three_sat_to_clique(clauses):
    labels = [(ci, l) for ci, clause in enumerate(clauses) for l in clause]
    n = len(labels)
    edges = set()
    for u, v in combinations(range(n), 2):
        cu, lu = labels[u]
        cv, lv = labels[v]
        if cu != cv and lu != -lv:
            edges.add((u, v))
    return n, edges, labels


def _sol_clique_to_assignment(clique, labels, nvars):
    a = {v: False for v in range(1, nvars + 1)}
    for u in clique:
        _, l = labels[u]
        a[abs(l)] = (l > 0)
    return a


def _sol_max_clique_bruteforce(n, edges):
    for size in range(n, 0, -1):
        for sub in combinations(range(n), size):
            if all((min(x, y), max(x, y)) in edges
                   for x, y in combinations(sub, 2)):
                return list(sub)
    return []


# ---------------------------------------------------------------------------
# Exercise 5: CLIQUE <=p VERTEX COVER (complement the graph AND the set)
# ---------------------------------------------------------------------------

def complement_graph(n, edges):
    """
    Return (n, complement_edges): every pair (u, v) with u < v that is NOT an
    edge of G. No self-loops.

    C is a clique of size k in G  <=>  V\\C is a vertex cover of size n-k in
    this graph. Both halves hold, which is what makes it a reduction.
    """
    # TODO: implement
    pass


def _sol_complement_graph(n, edges):
    return n, {(u, v) for u, v in combinations(range(n), 2)
               if (u, v) not in edges}


def _sol_is_vertex_cover(edges, subset):
    s = set(subset)
    return all(u in s or v in s for u, v in edges)


def _sol_is_clique(edges, subset):
    return all((min(u, v), max(u, v)) in edges for u, v in combinations(subset, 2))


# ---------------------------------------------------------------------------
# Exercise 6: VERTEX COVER <=p INDEPENDENT SET
# ---------------------------------------------------------------------------

def is_independent_set(edges, subset):
    """
    True iff no edge has BOTH endpoints in `subset`.

    S is a vertex cover of G  <=>  V\\S is an independent set of G. Same graph,
    no transformation — the two problems are one problem read twice.
    """
    # TODO: implement
    pass


def _sol_is_independent_set(edges, subset):
    s = set(subset)
    return all(not (u in s and v in s) for u, v in edges)


def _sol_complement_set(n, subset):
    return sorted(set(range(n)) - set(subset))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: verify_sat")
    check("satisfied", try_or_sol("verify_sat", [[1, 2]], {1: True, 2: False}), True)
    check("unsatisfied", try_or_sol("verify_sat", [[1, 2]], {1: False, 2: False}),
          False)
    check("negative literal", try_or_sol("verify_sat", [[-1]], {1: False}), True)
    check("missing var defaults False", try_or_sol("verify_sat", [[1]], {}), False)
    check("empty clause is unsatisfiable",
          try_or_sol("verify_sat", [[]], {1: True}), False)
    check("no clauses is vacuously true", try_or_sol("verify_sat", [], {}), True)

    print("\nExercise 2: brute_force_sat")
    check("classic 3-SAT is sat",
          try_or_sol("brute_force_sat", [[1, 2, -3], [-1, 2, 3], [1, -2, 3]], 3)
          is not None, True)
    check("x AND not-x is unsat",
          try_or_sol("brute_force_sat", [[1], [-1]], 1), None)
    all8 = [list(c) for c in product(*[[v, -v] for v in (1, 2, 3)])]
    check("all 8 sign-triples unsat", try_or_sol("brute_force_sat", all8, 3), None)
    got = try_or_sol("brute_force_sat", [[1, 2], [-1, 3]], 3)
    check("returned certificate actually verifies",
          _sol_verify_sat([[1, 2], [-1, 3]], got), True)

    print("\nExercise 3: sat_to_3sat")
    cases = [
        ("unit", [[1]], 1, True),
        ("x and not-x", [[1], [-1]], 1, False),
        ("two literals", [[1, 2], [-1, 3]], 3, True),
        ("already 3", [[1, 2, -3]], 3, True),
        ("k=5 sat", [[1, 2, 3, 4, 5], [-1], [-2], [-3], [-4]], 5, True),
        ("k=4 unsat", [[1, 2, 3, 4], [-1], [-2], [-3], [-4]], 4, False),
        ("empty clause", [[], [1]], 1, False),
    ]
    for name, cl, nv, expect in cases:
        c3, n3 = try_or_sol("sat_to_3sat", cl, nv)
        check(f"{name}: every clause has 3 literals",
              all(len(c) == 3 for c in c3), True)
        # BOTH directions: satisfiability preserved, not merely implied.
        a3 = _sol_brute_force_sat(c3, n3)
        check(f"{name}: satisfiability preserved", a3 is not None, expect)
        if a3 is not None:
            back = {v: a3.get(v, False) for v in range(1, nv + 1)}
            check(f"{name}: certificate maps BACK to the original",
                  _sol_verify_sat(cl, back), True)

    print("\nExercise 4: three_sat_to_clique")
    f = [[1, 2], [-1, 3]]
    n, edges, labels = try_or_sol("three_sat_to_clique", f)
    check("vertex count", n, 4)
    check("labels", labels, [(0, 1), (0, 2), (1, -1), (1, 3)])
    # (0,1) same clause -> no edge. (0,2) is 1 vs -1 -> complementary, no edge.
    check("edges", sorted(edges), [(0, 3), (1, 2), (1, 3)])
    f3 = [[1, 2, -3], [-1, 2, 3], [1, -2, 3]]
    n3, e3, lab3 = try_or_sol("three_sat_to_clique", f3)
    check("no edge inside a clause",
          any((u, v) in e3 for u, v in [(0, 1), (0, 2), (1, 2)]), False)
    clique = _sol_max_clique_bruteforce(n3, e3)
    check("max clique size == number of clauses", len(clique), len(f3))
    check("clique maps back to a satisfying assignment",
          _sol_verify_sat(f3, _sol_clique_to_assignment(clique, lab3, 3)), True)
    # And an UNSAT formula must have no size-m clique.
    unsat3 = _sol_sat_to_3sat([[1], [-1]], 1)[0]
    nu, eu, _ = try_or_sol("three_sat_to_clique", unsat3)
    check("unsat formula has no size-m clique",
          len(_sol_max_clique_bruteforce(nu, eu)) < len(unsat3), True)

    print("\nExercise 5: complement_graph")
    cn, cedges = try_or_sol("complement_graph", 3, {(0, 1), (1, 2)})
    check("n unchanged", cn, 3)
    check("complement edges", sorted(cedges), [(0, 2)])
    check("complete graph -> empty",
          try_or_sol("complement_graph", 3, {(0, 1), (0, 2), (1, 2)})[1], set())
    check("empty graph -> complete",
          sorted(try_or_sol("complement_graph", 3, set())[1]),
          [(0, 1), (0, 2), (1, 2)])
    n5 = 6
    e5 = {(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5)}
    _, ce5 = try_or_sol("complement_graph", n5, e5)
    cl5 = _sol_max_clique_bruteforce(n5, e5)
    cover = _sol_complement_set(n5, cl5)
    check("clique complement is a cover of Gbar",
          _sol_is_vertex_cover(ce5, cover), True)
    check("cover size is n - k", len(cover), n5 - len(cl5))
    check("cover complement is the clique again",
          _sol_complement_set(n5, cover), sorted(cl5))
    check("...and it is still a clique in G", _sol_is_clique(e5, cl5), True)

    print("\nExercise 6: is_independent_set")
    check("empty set", try_or_sol("is_independent_set", e5, []), True)
    check("single vertex", try_or_sol("is_independent_set", e5, [0]), True)
    check("adjacent pair", try_or_sol("is_independent_set", e5, [0, 1]), False)
    check("non-adjacent pair", try_or_sol("is_independent_set", e5, [0, 3]), True)
    indep = _sol_complement_set(n5, cover)
    check("cover complement is independent in Gbar",
          try_or_sol("is_independent_set", ce5, indep), True)
    check("independent-set complement is a cover again",
          _sol_complement_set(n5, indep), cover)
    check("|VC| + |IS| == n", len(cover) + len(indep), n5)
    check("max IS(Gbar) == max clique(G) — the chain closes",
          len(indep), len(cl5))

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    print('=' * 50)


if __name__ == "__main__":
    run_tests()
