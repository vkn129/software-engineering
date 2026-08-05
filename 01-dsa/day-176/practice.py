"""
Day 176 Practice: Approximation Algorithms

5 exercises: matchings, vertex cover, MST shortcut, set cover greedy,
knapsack FPTAS-style scaling.
"""

import math
import itertools


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Maximal Matching (greedy)
# ===================================================================
# Walk edges in input order, take any edge whose endpoints are unused.

def maximal_matching(n, edges):
    """Returns list of edges forming a maximal matching."""
    # TODO: implement
    pass


def _sol_maximal_matching(n, edges):
    used = [False] * n
    m = []
    for u, v in edges:
        if not used[u] and not used[v]:
            used[u] = used[v] = True
            m.append((u, v))
    return m


# ===================================================================
# Exercise 2: Vertex Cover from Matching
# ===================================================================
# Given a maximal matching, return the 2-approx vertex cover.

def cover_from_matching(matching):
    """Return set of all endpoints of matched edges."""
    # TODO: implement
    pass


def _sol_cover_from_matching(matching):
    s = set()
    for u, v in matching:
        s.add(u)
        s.add(v)
    return s


# ===================================================================
# Exercise 3: Greedy Set Cover (H_n approximation)
# ===================================================================
# Repeatedly pick the set covering the most uncovered elements.

def greedy_set_cover(universe, sets):
    """
    universe: set of elements to cover
    sets: list of sets
    Returns: list of indices of chosen sets that cover everything.
    """
    # TODO: implement
    pass


def _sol_greedy_set_cover(universe, sets):
    remaining = set(universe)
    chosen = []
    while remaining:
        best_i = -1
        best_gain = -1
        for i, s in enumerate(sets):
            if i in chosen:
                continue
            gain = len(s & remaining)
            if gain > best_gain:
                best_gain = gain
                best_i = i
        if best_i == -1 or best_gain == 0:
            break
        chosen.append(best_i)
        remaining -= sets[best_i]
    return chosen


# ===================================================================
# Exercise 4: Nearest-Neighbor TSP cost
# ===================================================================
# Compute nearest-neighbor tour cost from a distance matrix.

def nn_tour_cost(dist, start=0):
    """
    dist: n x n symmetric matrix, dist[i][i] = 0.
    Returns cost of nearest-neighbor tour starting at `start` and returning to start.
    """
    # TODO: implement
    pass


def _sol_nn_tour_cost(dist, start=0):
    n = len(dist)
    if n == 0:
        return 0.0
    visited = [False] * n
    visited[start] = True
    cur = start
    total = 0.0
    for _ in range(n - 1):
        best = -1
        best_d = math.inf
        for v in range(n):
            if not visited[v] and dist[cur][v] < best_d:
                best_d = dist[cur][v]
                best = v
        total += best_d
        visited[best] = True
        cur = best
    total += dist[cur][start]
    return total


# ===================================================================
# Exercise 5: Knapsack greedy (2-approximation by ratio)
# ===================================================================
# Sort items by value/weight, take greedily; also try the single best
# item alone. Return max of the two — this is a 2-approx for 0/1 knapsack.

def knapsack_greedy_2approx(weights, values, capacity):
    """
    Returns best achievable value: max(greedy_by_ratio, best_single_item).
    """
    # TODO: implement
    pass


def _sol_knapsack_greedy_2approx(weights, values, capacity):
    n = len(weights)
    # Greedy by value/weight
    order = sorted(range(n), key=lambda i: -values[i] / max(weights[i], 1e-9))
    greedy_v = 0
    rem = capacity
    for i in order:
        if weights[i] <= rem:
            rem -= weights[i]
            greedy_v += values[i]
    # Single best item that fits
    best_single = 0
    for i in range(n):
        if weights[i] <= capacity and values[i] > best_single:
            best_single = values[i]
    return max(greedy_v, best_single)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected={expected}  got={got}")
            failed += 1

    # Ex 1
    print("Exercise 1: Maximal Matching")
    m = try_or_sol("maximal_matching", 4, [(0, 1), (1, 2), (2, 3)])
    # greedy: (0,1) taken, (1,2) blocked, (2,3) taken → 2 edges
    check("path 0-1-2-3 matches 2 edges", len(m), 2)
    m = try_or_sol("maximal_matching", 4, [(0, 1), (2, 3)])
    check("disjoint edges both taken", len(m), 2)

    # Ex 2
    print("\nExercise 2: Cover From Matching")
    check("two edges 4 endpoints",
          try_or_sol("cover_from_matching", [(0, 1), (2, 3)]),
          {0, 1, 2, 3})
    check("single edge 2 endpoints",
          try_or_sol("cover_from_matching", [(5, 7)]),
          {5, 7})

    # Ex 3
    print("\nExercise 3: Greedy Set Cover")
    universe = {1, 2, 3, 4, 5}
    sets = [{1, 2, 3}, {2, 4}, {3, 4}, {4, 5}]
    chosen = try_or_sol("greedy_set_cover", universe, sets)
    covered = set()
    for i in chosen:
        covered |= sets[i]
    check("covers universe", covered, universe)
    check("uses at most 3 sets", len(chosen) <= 3, True)

    # Ex 4
    print("\nExercise 4: Nearest-Neighbor TSP")
    # 3 vertices on a line; NN from 0 = 0->1->2->0
    dist = [[0, 1, 2], [1, 0, 1], [2, 1, 0]]
    check("triangle on a line", try_or_sol("nn_tour_cost", dist, 0), 4)

    # Ex 5
    print("\nExercise 5: Knapsack 2-Approx")
    # capacity 10. Best single item = 60. Greedy by ratio takes (w=6,v=60) only.
    weights = [6, 5, 5]
    values = [60, 40, 40]
    # OPT = take items 1 and 2: weight 10, value 80
    # Greedy by ratio: item 0 (ratio 10), then nothing fits in 4 remaining → 60
    # Single best: 60
    # max → 60. Within factor 2 of OPT (80).
    got = try_or_sol("knapsack_greedy_2approx", weights, values, 10)
    check("greedy result <= 80", got <= 80, True)
    check("greedy result >= 80/2", got >= 40, True)
    # Trivial case
    check("empty knapsack",
          try_or_sol("knapsack_greedy_2approx", [], [], 5), 0)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
