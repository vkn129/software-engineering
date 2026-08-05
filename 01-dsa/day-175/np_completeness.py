"""
Day 175: NP-Completeness & Reductions — From Scratch

The chain:   SAT -> 3-SAT -> CLIQUE -> VERTEX COVER -> INDEPENDENT SET

Every reduction here ships BOTH certificate maps and is round-tripped against a
brute-force oracle. A one-directional map is not a reduction — the constant
function sending everything to a satisfiable instance is one-directional too.

CNF encoding: a clause is a list of nonzero ints, `+v` means variable v, `-v`
means NOT v. Variables are numbered 1..nvars. An assignment is {var: bool}.

Graph encoding: (n, edges), vertices 0..n-1, `edges` a set of sorted 2-tuples.
Undirected, no self-loops.
"""

import random
from itertools import combinations, product


# ---------------------------------------------------------------------------
# 1. SAT — the verifier is the point
# ---------------------------------------------------------------------------

def verify_sat(clauses, assignment):
    """
    Check a certificate in O(total literals).

    THIS function is why SAT is in NP. Finding `assignment` looks exponential;
    checking it is a linear scan. That gap is the whole subject.
    """
    for clause in clauses:
        if not any(assignment.get(abs(l), False) == (l > 0) for l in clause):
            return False
    return True


def brute_force_sat(clauses, nvars):
    """
    Try all 2^nvars assignments. Returns a satisfying assignment or None.

    Exponential on purpose — this is the thing NP-completeness is a statement
    about. Only usable for nvars <= ~20.
    """
    for bits in product([False, True], repeat=nvars):
        assignment = {v + 1: bits[v] for v in range(nvars)}
        if verify_sat(clauses, assignment):
            return assignment
    return None


# ---------------------------------------------------------------------------
# 2. SAT <=p 3-SAT
# ---------------------------------------------------------------------------

def sat_to_3sat(clauses, nvars):
    """
    Rewrite every clause to exactly 3 literals. Returns (clauses3, nvars3).

    k=1: (l)     -> (l, +-y1, +-y2) x4   -- whatever y1,y2 are, l is forced
    k=2: (l1,l2) -> (l1,l2,y), (l1,l2,not y)
    k=3: unchanged
    k>3: chain with k-3 fresh carry variables
             (l1,l2,y1), (not y1,l3,y2), ..., (not y_{k-3}, l_{k-1}, l_k)

    The chain is the interesting case. If some l_t is true the carries can be
    set to satisfy everything. If NO l_t is true, the first clause forces y1,
    which forces y2, ... and the last clause has all three literals false. The
    fresh variables cannot rescue an unsatisfiable clause — that is the `<=`
    half of the equivalence, and the half people forget to check.

    Output size is O(total literals): polynomial, as a reduction must be.
    """
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
            # The empty clause is unsatisfiable. Encode that faithfully with a
            # contradiction on fresh variables, rather than dropping it — or
            # the map stops being an equivalence.
            y = fresh()
            fresh()          # keep the fresh-variable count in step with
            out.append([y, y, y])          # extend_assignment_to_3sat
            out.append([-y, -y, -y])
            continue
        if k == 1:
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


def restrict_assignment(assignment3, nvars):
    """
    3-SAT certificate -> SAT certificate: drop the fresh variables.

    The simplest backward map in the chain, which is exactly why this reduction
    is the one to learn first.
    """
    return {v: assignment3.get(v, False) for v in range(1, nvars + 1)}


def extend_assignment_to_3sat(clauses, assignment, nvars):
    """
    SAT certificate -> 3-SAT certificate: set the carry variables.

    For a clause whose first true literal is l_t (1-based), set y_1..y_{t-2}
    true and the rest false — the carries climb to the true literal and stop.
    Only meaningful when `assignment` actually satisfies `clauses`.
    """
    ext = dict(assignment)
    nxt = nvars + 1

    def fresh():
        nonlocal nxt
        v = nxt
        nxt += 1
        return v

    for clause in clauses:
        k = len(clause)
        if k == 0:
            ext[fresh()] = False
            fresh()
        elif k == 1:
            ext[fresh()] = False
            ext[fresh()] = False
        elif k == 2:
            ext[fresh()] = False
        elif k == 3:
            pass
        else:
            ys = [fresh() for _ in range(k - 3)]
            t = next((i for i, l in enumerate(clause)
                      if assignment.get(abs(l), False) == (l > 0)), None)
            # t is 0-based here; the README's l_t is 1-based, so cut = t - 1.
            cut = 0 if t is None else max(0, t - 1)
            for i, y in enumerate(ys):
                ext[y] = i < cut
    return ext


# ---------------------------------------------------------------------------
# 3. 3-SAT <=p CLIQUE
# ---------------------------------------------------------------------------

def three_sat_to_clique(clauses):
    """
    Build the literal-compatibility graph. Returns (n, edges, labels).

    Vertex per (clause, literal). Edge iff the two vertices are in DIFFERENT
    clauses AND their literals are not complementary. Then

        formula satisfiable  <=>  clique of size len(clauses) exists

    Edges encode "these two choices can both be true at once", and a clique is
    a set of pairwise-compatible choices. That is the reusable pattern.
    """
    labels = []                       # vertex -> (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for l in clause:
            labels.append((ci, l))
    n = len(labels)
    edges = set()
    for u, v in combinations(range(n), 2):
        cu, lu = labels[u]
        cv, lv = labels[v]
        # Same clause => no edge. That is what forces a size-m clique to pick
        # exactly one literal per clause, and it proves the (<=) direction.
        if cu != cv and lu != -lv:
            edges.add((u, v))
    return n, edges, labels


def clique_to_assignment(clique, labels, nvars):
    """
    CLIQUE certificate -> 3-SAT certificate.

    A size-m clique holds one vertex per clause with no two complementary
    literals, so setting every chosen literal true is consistent. Variables
    appearing in no chosen literal are free — default them to False.
    """
    assignment = {v: False for v in range(1, nvars + 1)}
    for u in clique:
        _, l = labels[u]
        assignment[abs(l)] = (l > 0)
    return assignment


def assignment_to_clique(clauses, assignment, labels):
    """
    3-SAT certificate -> CLIQUE certificate: one true literal per clause.
    Returns None if the assignment does not satisfy the formula.
    """
    chosen = []
    for ci, clause in enumerate(clauses):
        for l in clause:
            if assignment.get(abs(l), False) == (l > 0):
                chosen.append(labels.index((ci, l)))
                break
        else:
            return None
    return sorted(chosen)


# ---------------------------------------------------------------------------
# 4. CLIQUE <=p VERTEX COVER
# ---------------------------------------------------------------------------

def complement_graph(n, edges):
    """Gbar: same vertices, exactly the non-edges of G."""
    return n, {(u, v) for u, v in combinations(range(n), 2)
               if (u, v) not in edges}


def clique_to_vertex_cover(n, clique):
    """
    CLIQUE certificate -> VERTEX COVER certificate in the COMPLEMENT graph.

    C is a clique of size k in G  <=>  V\\C is a vertex cover of size n-k in
    Gbar. An edge of Gbar is a non-edge of G, so it cannot lie inside C;
    therefore every edge of Gbar has an endpoint outside C. Set complement.
    """
    return sorted(set(range(n)) - set(clique))


def vertex_cover_to_clique(n, cover):
    """VERTEX COVER certificate -> CLIQUE. The same complement, run backwards."""
    return sorted(set(range(n)) - set(cover))


def is_clique(edges, subset):
    return all((min(u, v), max(u, v)) in edges for u, v in combinations(subset, 2))


def is_vertex_cover(edges, subset):
    s = set(subset)
    return all(u in s or v in s for u, v in edges)


# ---------------------------------------------------------------------------
# 5. VERTEX COVER <=p INDEPENDENT SET
# ---------------------------------------------------------------------------

def vertex_cover_to_independent_set(n, cover):
    """
    Same graph, no transformation at all.

    S is a vertex cover  <=>  V\\S is an independent set. If S covers every
    edge, no edge has both endpoints outside S. Minimum vertex cover and
    maximum independent set are the same problem read twice.
    """
    return sorted(set(range(n)) - set(cover))


def independent_set_to_vertex_cover(n, indep):
    """The same complement, run backwards."""
    return sorted(set(range(n)) - set(indep))


def is_independent_set(edges, subset):
    s = set(subset)
    return all(not (u in s and v in s) for u, v in edges)


# ---------------------------------------------------------------------------
# 6. Brute-force oracles (exponential — reference only)
# ---------------------------------------------------------------------------

def max_clique_bruteforce(n, edges):
    """Largest clique, as a sorted vertex list. O(2^n n^2). n <= ~15."""
    for size in range(n, 0, -1):
        for sub in combinations(range(n), size):
            if is_clique(edges, sub):
                return list(sub)
    return []


def min_vertex_cover_bruteforce(n, edges):
    """Smallest vertex cover. O(2^n)."""
    for size in range(n + 1):
        for sub in combinations(range(n), size):
            if is_vertex_cover(edges, sub):
                return list(sub)
    return list(range(n))


def max_independent_set_bruteforce(n, edges):
    """Largest independent set. O(2^n)."""
    for size in range(n, -1, -1):
        for sub in combinations(range(n), size):
            if is_independent_set(edges, sub):
                return list(sub)
    return []


# ---------------------------------------------------------------------------
# Test instances
# ---------------------------------------------------------------------------

SAT_INSTANCES = [
    # (name, clauses, nvars, satisfiable)
    ("unit clause", [[1]], 1, True),
    ("x and not-x", [[1], [-1]], 1, False),
    ("2-literal", [[1, 2], [-1, 3]], 3, True),
    ("classic 3-SAT", [[1, 2, -3], [-1, 2, 3], [1, -2, 3]], 3, True),
    ("long clause k=5", [[1, 2, 3, 4, 5], [-1], [-2], [-3], [-4]], 5, True),
    ("long clause unsat", [[1, 2, 3, 4], [-1], [-2], [-3], [-4]], 4, False),
    ("all 8 triples", [list(c) for c in product(*[[v, -v] for v in (1, 2, 3)])],
     3, False),
    ("2-var contradiction", [[1, 2], [-1, -2], [1, -2], [-1, 2]], 2, False),
    ("empty clause", [[], [1]], 1, False),
]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_certificates():
    print("=" * 70)
    print("DEMO 1: NP is about CHECKING, not finding")
    print("=" * 70)
    clauses = [[1, 2, -3], [-1, 2, 3], [1, -2, 3], [-1, -2, -3]]
    print(f"\n  formula: {clauses}   (3 variables, 4 clauses)")
    a = brute_force_sat(clauses, 3)
    print(f"  brute force scanned up to 2^3 = 8 assignments -> {a}")
    print(f"  verify_sat(certificate) = {verify_sat(clauses, a)}   "
          f"(one linear scan)")
    bad = {1: True, 2: True, 3: True}
    print(f"  verify_sat({bad}) = {verify_sat(clauses, bad)}")
    print("\n  Finding: 2^n. Checking: O(total literals). SAT is in NP because")
    print("  the second number is small, not because the first one is.")


def demo_sat_to_3sat():
    print("\n" + "=" * 70)
    print("DEMO 2: SAT <=p 3-SAT, verified in BOTH directions")
    print("=" * 70)
    print("\n  name                | vars | 3SAT vars | clauses | sat? | "
          "3SAT sat? | agree")
    for name, clauses, nvars, expect in SAT_INSTANCES:
        c3, n3 = sat_to_3sat(clauses, nvars)
        assert all(len(c) == 3 for c in c3), "every clause must have 3 literals"
        a = brute_force_sat(clauses, nvars)
        a3 = brute_force_sat(c3, n3)
        agree = (a is not None) == (a3 is not None)
        assert agree and (a is not None) == expect, name
        # Forward: extend an original certificate, re-verify on the 3-SAT side.
        if a is not None:
            ext = extend_assignment_to_3sat(clauses, a, nvars)
            assert verify_sat(c3, ext), f"forward map failed on {name}"
        # Backward: restrict a 3-SAT certificate, re-verify on the original.
        if a3 is not None:
            assert verify_sat(clauses, restrict_assignment(a3, nvars)), name
        print(f"  {name:19s} | {nvars:4d} | {n3:9d} | {len(c3):7d} | "
              f"{str(expect):5s}| {str(a3 is not None):9s}| {agree}")
    print("\n  Both certificate maps verified on every instance, including the")
    print("  UNSAT ones — those are what catch a construction whose fresh")
    print("  variables can rescue an unsatisfiable clause.")


def demo_3sat_to_clique():
    print("\n" + "=" * 70)
    print("DEMO 3: 3-SAT <=p CLIQUE, verified in BOTH directions")
    print("=" * 70)
    small = [[1, 2, -3], [-1, 2, 3], [1, -2, 3]]
    n, edges, labels = three_sat_to_clique(small)
    print(f"\n  formula  : {small}")
    print(f"  vertices : {n} = 3 literals x {len(small)} clauses")
    print(f"  labels   : {labels}")
    print(f"  edges    : {len(edges)} of {n * (n - 1) // 2} possible")
    print("  (no edge inside a clause; no edge between x and NOT x)")

    clique = max_clique_bruteforce(n, edges)
    print(f"\n  max clique = {clique}, size {len(clique)}, m = {len(small)}")
    a = clique_to_assignment(clique, labels, 3)
    print(f"  clique -> assignment {a}, verifies: {verify_sat(small, a)}")
    back = assignment_to_clique(small, a, labels)
    print(f"  assignment -> clique {back}, is a clique: "
          f"{is_clique(edges, back)}, size {len(back)}")
    assert len(clique) == len(small) and verify_sat(small, a)
    assert is_clique(edges, back) and len(back) == len(small)

    print("\n  The equivalence across every instance:\n")
    print("  name                | m | vertices | max clique | sat? | agree")
    for name, clauses, nvars, expect in SAT_INSTANCES:
        c3, n3 = sat_to_3sat(clauses, nvars)
        if len(c3) > 9:                 # keep the 2^n oracle fast
            continue
        n, edges, labels = three_sat_to_clique(c3)
        clique = max_clique_bruteforce(n, edges)
        agree = (len(clique) == len(c3)) == expect
        assert agree, name
        if len(clique) == len(c3):
            a3 = clique_to_assignment(clique, labels, n3)
            assert verify_sat(c3, a3), name
            assert verify_sat(clauses, restrict_assignment(a3, nvars)), name
        print(f"  {name:19s} |{len(c3):2d} | {n:8d} | {len(clique):10d} | "
              f"{str(expect):5s}| {agree}")
    print("\n  Clique of size m <=> satisfiable. Verified, not asserted — and")
    print("  the whole chain SAT -> 3SAT -> clique round-trips back to a")
    print("  certificate for the ORIGINAL formula.")


def demo_clique_vc_is():
    print("\n" + "=" * 70)
    print("DEMO 4: CLIQUE <=p VERTEX COVER <=p INDEPENDENT SET")
    print("=" * 70)
    n = 6
    edges = {(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5)}
    print(f"\n  G: {n} vertices, edges {sorted(edges)}")
    clique = max_clique_bruteforce(n, edges)
    print(f"  max clique in G           : {clique} (size {len(clique)})")

    nc, cedges = complement_graph(n, edges)
    cover = clique_to_vertex_cover(n, clique)
    print(f"  complement graph edges    : {sorted(cedges)}")
    print(f"  -> vertex cover of Gbar   : {cover} (size {len(cover)}), "
          f"valid: {is_vertex_cover(cedges, cover)}")
    assert is_vertex_cover(cedges, cover) and len(cover) == n - len(clique)

    back = vertex_cover_to_clique(n, cover)
    print(f"  <- back to clique in G    : {back}, valid: "
          f"{is_clique(edges, back)}")
    assert back == sorted(clique) and is_clique(edges, back)

    indep = vertex_cover_to_independent_set(nc, cover)
    print(f"  -> independent set of Gbar: {indep} (size {len(indep)}), "
          f"valid: {is_independent_set(cedges, indep)}")
    assert is_independent_set(cedges, indep)
    back_vc = independent_set_to_vertex_cover(nc, indep)
    print(f"  <- back to vertex cover   : {back_vc}, valid: "
          f"{is_vertex_cover(cedges, back_vc)}")
    assert back_vc == cover

    print("\n  Optimality carries too (brute-force oracles agree):")
    mvc = min_vertex_cover_bruteforce(nc, cedges)
    mis = max_independent_set_bruteforce(nc, cedges)
    assert len(mvc) + len(mis) == n
    assert len(mis) == len(clique), "IS in Gbar must equal max clique in G"
    print(f"    |min VC| + |max IS| = {len(mvc)} + {len(mis)} = {n}   <- always")
    print(f"    max IS(Gbar) = max clique(G) = {len(clique)}   "
          f"<- the chain closes")


def demo_chain_sweep():
    print("\n" + "=" * 70)
    print("DEMO 5: the whole chain, swept over random graphs")
    print("=" * 70)
    random.seed(175)
    checked = 0
    for _ in range(120):
        n = random.randint(1, 7)
        edges = {(u, v) for u, v in combinations(range(n), 2)
                 if random.random() < 0.5}
        clique = max_clique_bruteforce(n, edges)
        nc, cedges = complement_graph(n, edges)
        cover = clique_to_vertex_cover(n, clique)
        indep = vertex_cover_to_independent_set(nc, cover)

        assert is_clique(edges, clique)
        assert is_vertex_cover(cedges, cover)
        assert is_independent_set(cedges, indep)
        assert vertex_cover_to_clique(n, cover) == sorted(clique)
        assert independent_set_to_vertex_cover(nc, indep) == cover
        # The identities that make steps 3 and 4 pure bookkeeping.
        assert len(min_vertex_cover_bruteforce(nc, cedges)) == n - len(clique)
        assert len(max_independent_set_bruteforce(nc, cedges)) == len(clique)
        checked += 1
    print(f"\n  {checked} random graphs (n <= 7): every certificate maps forward")
    print("  AND back, and both complement identities hold exactly.")
    print("\n    |min VC(Gbar)| = n - |max clique(G)|")
    print("    |max IS(Gbar)| = |max clique(G)|")


def demo_what_it_does_not_mean():
    print("\n" + "=" * 70)
    print("DEMO 6: NP-complete is a routing decision, not a wall")
    print("=" * 70)
    print("\n  Same problems, restricted inputs, polynomial algorithms:")
    print("    2-SAT           -> O(V+E) via SCC       day-087/scc.py:176")
    print("    vertex cover    -> Konig, bipartite     day-092/practice.py:189")
    print("    independent set -> n - max matching     day-092/practice.py:204")
    print("\n  And the direction that traps people:")
    print("    To prove B is HARD: reduce known-hard A -> B.")
    print("    Reducing B -> A proves B is EASY. Opposite conclusion.")
    print("\n  Handing off to day 176: vertex cover has a 2-approximation, and")
    print("  independent set — the SAME problem complemented — has no")
    print("  constant-factor approximation unless P = NP. Exact equivalence")
    print("  does not survive as approximation equivalence. That is why")
    print("  L-reductions exist and why 'reduction != approximation'.")


if __name__ == "__main__":
    demo_certificates()
    demo_sat_to_3sat()
    demo_3sat_to_clique()
    demo_clique_vc_is()
    demo_chain_sweep()
    demo_what_it_does_not_mean()
