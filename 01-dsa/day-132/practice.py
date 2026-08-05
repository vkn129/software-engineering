"""
Day 132 Practice: Stable Matching (Gale-Shapley / Deferred Acceptance)

6 exercises. Implement TODOs, then run: python practice.py
"""

from collections import deque
from itertools import permutations


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
# Fixtures
# ---------------------------------------------------------------------------

MEN = {
    "al": ["xena", "yara", "zoe"],
    "bob": ["yara", "xena", "zoe"],
    "cal": ["xena", "yara", "zoe"],
}
WOMEN = {
    "xena": ["bob", "cal", "al"],
    "yara": ["cal", "al", "bob"],
    "zoe": ["al", "bob", "cal"],
}

# Smallest instance with TWO stable matchings.
SMALL_M = {"A": ["X", "Y"], "B": ["Y", "X"]}
SMALL_W = {"X": ["B", "A"], "Y": ["A", "B"]}


def _norm(matchings):
    """Canonical form so a list of dicts can be compared regardless of order."""
    return sorted(tuple(sorted(m.items())) for m in matchings)


# ---------------------------------------------------------------------------
# Exercise 1: Deferred acceptance
# ---------------------------------------------------------------------------

def gale_shapley(proposer_prefs, receiver_prefs):
    """Return {proposer: receiver}. Lists may be incomplete on either side."""
    # TODO: free queue + "receivers hold, never commit"
    pass


def _sol_gale_shapley(proposer_prefs, receiver_prefs):
    rank = {r: {p: i for i, p in enumerate(prefs)}
            for r, prefs in receiver_prefs.items()}
    free = deque(proposer_prefs)
    next_choice = {p: 0 for p in proposer_prefs}
    held = {}
    while free:
        p = free.popleft()
        prefs = proposer_prefs[p]
        if next_choice[p] >= len(prefs):
            continue  # asked everyone acceptable; stays unmatched
        r = prefs[next_choice[p]]
        next_choice[p] += 1
        if r not in rank or p not in rank[r]:
            free.append(p)
            continue
        current = held.get(r)
        if current is None:
            held[r] = p
        elif rank[r][p] < rank[r][current]:
            # A receiver's holding only ever improves. That monotonicity is
            # what makes the final matching stable.
            held[r] = p
            free.append(current)
        else:
            free.append(p)
    return {p: r for r, p in held.items()}


# ---------------------------------------------------------------------------
# Exercise 2: Blocking pairs
# ---------------------------------------------------------------------------

def find_blocking_pairs(matching, proposer_prefs, receiver_prefs):
    """
    Every (proposer, receiver) pair who each prefer the other to what they got.
    Return them sorted, so the result is comparable.
    """
    # TODO: for each proposer, scan only the receivers he ranks ABOVE his match
    pass


def _sol_find_blocking_pairs(matching, proposer_prefs, receiver_prefs):
    partner = {r: p for p, r in matching.items()}
    rank_r = {r: {p: i for i, p in enumerate(lst)}
              for r, lst in receiver_prefs.items()}
    rank_p = {p: {r: i for i, r in enumerate(lst)}
              for p, lst in proposer_prefs.items()}
    blocking = []
    for p, prefs in proposer_prefs.items():
        current = matching.get(p)
        for r in prefs:
            if r not in rank_r:
                continue
            if current is not None and rank_p[p][r] >= rank_p[p][current]:
                break  # list is ordered; nothing after this can be better
            if p not in rank_r[r]:
                continue
            other = partner.get(r)
            if other is None or rank_r[r][p] < rank_r[r][other]:
                blocking.append((p, r))
    return sorted(blocking)


# ---------------------------------------------------------------------------
# Exercise 3: Stability predicate
# ---------------------------------------------------------------------------

def is_stable(matching, proposer_prefs, receiver_prefs):
    """True iff the matching has no blocking pair."""
    # TODO: one line on top of exercise 2
    pass


def _sol_is_stable(matching, proposer_prefs, receiver_prefs):
    return not _sol_find_blocking_pairs(matching, proposer_prefs, receiver_prefs)


# ---------------------------------------------------------------------------
# Exercise 4: Enumerate every stable matching (small n)
# ---------------------------------------------------------------------------

def all_stable_matchings(proposer_prefs, receiver_prefs):
    """Every stable perfect matching. Brute force over n! pairings; n <= 7."""
    # TODO: permutations + the stability test
    pass


def _sol_all_stable_matchings(proposer_prefs, receiver_prefs):
    proposers = list(proposer_prefs)
    receivers = list(receiver_prefs)
    out = []
    for perm in permutations(receivers):
        candidate = dict(zip(proposers, perm))
        if _sol_is_stable(candidate, proposer_prefs, receiver_prefs):
            out.append(candidate)
    return out


# ---------------------------------------------------------------------------
# Exercise 5: Best partner across all stable matchings
# ---------------------------------------------------------------------------

def best_stable_partner(agent, prefs, stable_matchings, as_proposer=True):
    """
    The most-preferred partner `agent` receives in ANY stable matching.
    `prefs` is the dict for whichever side `agent` belongs to.
    """
    # TODO: scan the stable matchings, keep the best-ranked partner
    pass


def _sol_best_stable_partner(agent, prefs, stable_matchings, as_proposer=True):
    ranking = {name: i for i, name in enumerate(prefs[agent])}
    best = None
    for m in stable_matchings:
        got = m.get(agent) if as_proposer else {v: k for k, v in m.items()}.get(agent)
        if got is None:
            continue
        if best is None or ranking[got] < ranking[best]:
            best = got
    return best


def _worst_stable_partner(agent, prefs, stable_matchings, as_proposer=True):
    """Mirror of the above — used by the tests to show receiver-pessimality."""
    ranking = {name: i for i, name in enumerate(prefs[agent])}
    worst = None
    for m in stable_matchings:
        got = m.get(agent) if as_proposer else {v: k for k, v in m.items()}.get(agent)
        if got is None:
            continue
        if worst is None or ranking[got] > ranking[worst]:
            worst = got
    return worst


# ---------------------------------------------------------------------------
# Exercise 6: Many-to-one (hospitals / residents)
# ---------------------------------------------------------------------------

def hospital_residents(resident_prefs, hospital_prefs, capacities):
    """
    Deferred acceptance where hospital h holds up to capacities[h] offers.
    Return {hospital: [residents, best-ranked first]}.
    """
    # TODO: "keep the best one" becomes "keep the best k"
    pass


def _sol_hospital_residents(resident_prefs, hospital_prefs, capacities):
    rank = {h: {r: i for i, r in enumerate(lst)}
            for h, lst in hospital_prefs.items()}
    free = deque(resident_prefs)
    next_choice = {r: 0 for r in resident_prefs}
    held = {h: [] for h in hospital_prefs}
    while free:
        r = free.popleft()
        prefs = resident_prefs[r]
        if next_choice[r] >= len(prefs):
            continue
        h = prefs[next_choice[r]]
        next_choice[r] += 1
        if h not in rank or r not in rank[h]:
            free.append(r)
            continue
        held[h].append(r)
        held[h].sort(key=lambda x: rank[h][x])
        if len(held[h]) > capacities[h]:
            free.append(held[h].pop())  # worst-ranked loses the seat
    return held


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

    print("Exercise 1: gale_shapley")
    m = try_or_sol("gale_shapley", MEN, WOMEN)
    check("3x3 men-proposing", m,
          {"bob": "xena", "cal": "yara", "al": "zoe"})
    check("everyone matched", len(m), 3)
    check("2x2 men-proposing", try_or_sol("gale_shapley", SMALL_M, SMALL_W),
          {"A": "X", "B": "Y"})
    # Swap the argument dicts and the OTHER side wins. Same instance.
    check("2x2 women-proposing", try_or_sol("gale_shapley", SMALL_W, SMALL_M),
          {"X": "B", "Y": "A"})
    # Incomplete list: X refuses A outright, so A must settle for Y.
    truncated = {"X": ["B"], "Y": ["A", "B"]}
    check("truncated list re-routes A",
          try_or_sol("gale_shapley", SMALL_M, truncated),
          {"A": "Y", "B": "X"})

    print("\nExercise 2: find_blocking_pairs")
    check("GS output has none",
          try_or_sol("find_blocking_pairs", m, MEN, WOMEN), [])
    bad = {"al": "xena", "bob": "zoe", "cal": "yara"}
    # xena has al (her last choice); bob and cal both outrank him and both
    # prefer her to what they got.
    check("hand-picked unstable matching",
          try_or_sol("find_blocking_pairs", bad, MEN, WOMEN),
          [("bob", "xena"), ("cal", "xena")])
    check("2x2 other stable matching also has none",
          try_or_sol("find_blocking_pairs", {"A": "Y", "B": "X"}, SMALL_M, SMALL_W),
          [])

    print("\nExercise 3: is_stable")
    check("GS output is stable", try_or_sol("is_stable", m, MEN, WOMEN), True)
    check("hand-picked is not", try_or_sol("is_stable", bad, MEN, WOMEN), False)
    check("both 2x2 matchings are stable",
          [try_or_sol("is_stable", x, SMALL_M, SMALL_W)
           for x in ({"A": "X", "B": "Y"}, {"A": "Y", "B": "X"})],
          [True, True])

    print("\nExercise 4: all_stable_matchings")
    small_all = try_or_sol("all_stable_matchings", SMALL_M, SMALL_W)
    check("2x2 has exactly two", _norm(small_all),
          _norm([{"A": "X", "B": "Y"}, {"A": "Y", "B": "X"}]))
    big_all = try_or_sol("all_stable_matchings", MEN, WOMEN)
    check("3x3 has exactly one", len(big_all), 1)
    check("and it is what Gale-Shapley returned", big_all[0], m)

    print("\nExercise 5: best_stable_partner")
    check("A's best is X",
          try_or_sol("best_stable_partner", "A", SMALL_M, small_all, True), "X")
    check("X's best is B",
          try_or_sol("best_stable_partner", "X", SMALL_W, small_all, False), "B")
    # Proposer-optimality: proposing gives EVERY proposer his best stable partner.
    men_first = try_or_sol("gale_shapley", SMALL_M, SMALL_W)
    check("men-proposing is man-optimal",
          all(men_first[p] == try_or_sol("best_stable_partner", p, SMALL_M,
                                         small_all, True) for p in SMALL_M),
          True)
    # And the same run gives every receiver her WORST stable partner.
    inverted = {r: p for p, r in men_first.items()}
    check("men-proposing is woman-pessimal",
          all(inverted[w] == _worst_stable_partner(w, SMALL_W, small_all, False)
              for w in SMALL_W),
          True)

    print("\nExercise 6: hospital_residents")
    residents = {
        "r1": ["mercy", "general", "county"],
        "r2": ["mercy", "county", "general"],
        "r3": ["general", "mercy", "county"],
        "r4": ["mercy", "general", "county"],
        "r5": ["county", "mercy", "general"],
    }
    hospitals = {
        "mercy": ["r3", "r1", "r4", "r2", "r5"],
        "general": ["r1", "r2", "r3", "r4", "r5"],
        "county": ["r5", "r4", "r3", "r2", "r1"],
    }
    caps = {"mercy": 2, "general": 2, "county": 1}
    assignment = try_or_sol("hospital_residents", residents, hospitals, caps)
    check("assignment", assignment,
          {"mercy": ["r1", "r4"], "general": ["r2", "r3"], "county": ["r5"]})
    check("no capacity exceeded",
          all(len(v) <= caps[k] for k, v in assignment.items()), True)
    check("every resident placed exactly once",
          sorted(r for rs in assignment.values() for r in rs),
          ["r1", "r2", "r3", "r4", "r5"])
    # Capacity 1 everywhere must reproduce the one-to-one algorithm.
    ones = {h: 1 for h in hospitals}
    one_to_one = try_or_sol("hospital_residents", residents, hospitals, ones)
    check("capacity 1 degenerates to one-to-one",
          all(len(v) <= 1 for v in one_to_one.values()), True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
