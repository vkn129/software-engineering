"""
Day 132: Stable Matching — Gale-Shapley / Deferred Acceptance

Two sides, each ranking the other. Find a pairing that no two people want to
abandon. "Want to abandon" has a precise name: a BLOCKING PAIR is a pair
(p, r) who are not matched to each other but each prefers the other to
whoever they got. A matching with no blocking pair is STABLE.

Preferences are dicts: name -> list of names, best first.
A matching is a dict: proposer -> receiver. Unmatched agents are simply absent.

Standard library only.
"""

from collections import deque
from itertools import permutations


# ---------------------------------------------------------------------------
# 1. Deferred acceptance
# ---------------------------------------------------------------------------

def gale_shapley(proposer_prefs, receiver_prefs):
    """
    One-to-one deferred acceptance. Returns {proposer: receiver}.

    The "deferred" in the name is the whole algorithm: a receiver holding an
    offer is ENGAGED, never committed. She keeps the best offer seen so far
    and stays free to trade up. That is why no one ever regrets an early
    acceptance, and why the process cannot cycle.

    Lists may be incomplete on either side; anyone a receiver did not rank is
    unacceptable to her and gets rejected outright.
    """
    rank = {r: {p: i for i, p in enumerate(prefs)}
            for r, prefs in receiver_prefs.items()}
    free = deque(proposer_prefs)
    next_choice = {p: 0 for p in proposer_prefs}
    held = {}  # receiver -> the proposer she is currently holding

    while free:
        p = free.popleft()
        prefs = proposer_prefs[p]
        if next_choice[p] >= len(prefs):
            continue  # p has proposed to everyone acceptable and stays unmatched
        r = prefs[next_choice[p]]
        next_choice[p] += 1

        # A proposer never proposes to the same receiver twice, so the total
        # number of proposals is bounded by the size of all preference lists.
        if r not in rank or p not in rank[r]:
            free.append(p)  # r does not exist or finds p unacceptable
            continue

        current = held.get(r)
        if current is None:
            held[r] = p
        elif rank[r][p] < rank[r][current]:
            held[r] = p
            free.append(current)  # traded up; the old holder is free again
        else:
            free.append(p)

    return {p: r for r, p in held.items()}


# ---------------------------------------------------------------------------
# 2. Stability check — the definition, executable
# ---------------------------------------------------------------------------

def find_blocking_pairs(matching, proposer_prefs, receiver_prefs):
    """
    Every (p, r) that would defect together. Empty list == stable.

    "Prefers" for an unmatched agent means "prefers anyone acceptable to
    nobody", which is why the unmatched cases short-circuit to True.
    """
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
                break  # prefs are ordered, so nothing further can be better
            if p not in rank_r[r]:
                continue  # r would not take p at any price
            other = partner.get(r)
            if other is None or rank_r[r][p] < rank_r[r][other]:
                blocking.append((p, r))
    return blocking


def is_stable(matching, proposer_prefs, receiver_prefs):
    return not find_blocking_pairs(matching, proposer_prefs, receiver_prefs)


# ---------------------------------------------------------------------------
# 3. Brute force over all matchings — ground truth for small instances
# ---------------------------------------------------------------------------

def all_stable_matchings(proposer_prefs, receiver_prefs):
    """
    Every stable matching, by testing all n! perfect matchings.
    For n <= 7 only. Used to prove proposer-optimality rather than assert it.
    """
    proposers = list(proposer_prefs)
    receivers = list(receiver_prefs)
    out = []
    for perm in permutations(receivers):
        candidate = dict(zip(proposers, perm))
        if is_stable(candidate, proposer_prefs, receiver_prefs):
            out.append(candidate)
    return out


def best_stable_partner(agent, prefs, stable_matchings, as_proposer=True):
    """The most-preferred partner `agent` gets in ANY stable matching."""
    ranking = {name: i for i, name in enumerate(prefs[agent])}
    best = None
    for m in stable_matchings:
        got = m.get(agent) if as_proposer else {v: k for k, v in m.items()}.get(agent)
        if got is None:
            continue
        if best is None or ranking[got] < ranking[best]:
            best = got
    return best


# ---------------------------------------------------------------------------
# 4. Many-to-one: the hospital/residents variant
# ---------------------------------------------------------------------------

def hospital_residents(resident_prefs, hospital_prefs, capacities):
    """
    Deferred acceptance where each hospital holds up to `capacities[h]` offers.
    Returns {hospital: [residents, best-ranked first]}.

    This is the real NRMP algorithm (US medical residency match), and it is
    the same three lines as the one-to-one version with "keep the best one"
    replaced by "keep the best k".
    """
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
            free.append(held[h].pop())  # the worst-ranked one loses the seat

    return held


def hospital_blocking_pairs(assignment, resident_prefs, hospital_prefs, capacities):
    """
    (resident, hospital) pairs that would defect. A hospital blocks if it has
    a free seat, or if it would rather have this resident than its worst hire.
    """
    placed = {r: h for h, rs in assignment.items() for r in rs}
    rank_h = {h: {r: i for i, r in enumerate(lst)}
              for h, lst in hospital_prefs.items()}
    rank_r = {r: {h: i for i, h in enumerate(lst)}
              for r, lst in resident_prefs.items()}

    blocking = []
    for r, prefs in resident_prefs.items():
        current = placed.get(r)
        for h in prefs:
            if h not in rank_h or r not in rank_h[h]:
                continue
            if current is not None and rank_r[r][h] >= rank_r[r][current]:
                break
            hires = assignment.get(h, [])
            if len(hires) < capacities[h]:
                blocking.append((r, h))
            elif hires and rank_h[h][r] < rank_h[h][hires[-1]]:
                blocking.append((r, h))
    return blocking


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Two men, two women, TWO distinct stable matchings — the smallest instance
# where "which side proposes" changes the outcome.
TWO_SIDED_MEN = {
    "A": ["X", "Y"],
    "B": ["Y", "X"],
}
TWO_SIDED_WOMEN = {
    "X": ["B", "A"],
    "Y": ["A", "B"],
}


def _invert(prefs_a, prefs_b):
    """Swap which side proposes by swapping the two argument dicts."""
    return prefs_b, prefs_a


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 66)
    print("DEMO 1: Deferred acceptance produces a stable matching")
    print("=" * 66)
    men = {
        "al": ["xena", "yara", "zoe"],
        "bob": ["yara", "xena", "zoe"],
        "cal": ["xena", "yara", "zoe"],
    }
    women = {
        "xena": ["bob", "cal", "al"],
        "yara": ["cal", "al", "bob"],
        "zoe": ["al", "bob", "cal"],
    }
    m = gale_shapley(men, women)
    print(f"\n  men-proposing: {m}")
    print(f"  blocking pairs: {find_blocking_pairs(m, men, women)}")
    assert is_stable(m, men, women)

    # An arbitrary matching is usually NOT stable — the contrast is the point.
    bad = {"al": "xena", "bob": "zoe", "cal": "yara"}
    bp = find_blocking_pairs(bad, men, women)
    print(f"\n  hand-picked matching: {bad}")
    print(f"  blocking pairs: {bp}")
    assert bp, "this matching was chosen to be unstable"


def demo_proposer_optimality():
    print("\n" + "=" * 66)
    print("DEMO 2: Proposer-optimality — the side that asks, wins")
    print("=" * 66)
    men, women = TWO_SIDED_MEN, TWO_SIDED_WOMEN
    stable = all_stable_matchings(men, women)
    print(f"\n  men   = {men}")
    print(f"  women = {women}")
    print(f"  all stable matchings ({len(stable)}): {stable}")

    m_prop = gale_shapley(men, women)
    w_prop = gale_shapley(*_invert(men, women))
    print(f"\n  men proposing:   {m_prop}")
    print(f"  women proposing: {w_prop}  (read as woman -> man)")

    for man in men:
        best = best_stable_partner(man, men, stable, as_proposer=True)
        print(f"    {man}: gets {m_prop[man]} when proposing; "
              f"best over all stable matchings = {best}")
        assert m_prop[man] == best, "men-proposing must be man-optimal"

    for woman in women:
        best = best_stable_partner(woman, women, stable, as_proposer=False)
        print(f"    {woman}: gets {w_prop[woman]} when proposing; "
              f"best over all stable matchings = {best}")
        assert w_prop[woman] == best, "women-proposing must be woman-optimal"

    print("\n  Same instance, same rules, opposite outcomes. Proposing is not")
    print("  a formality — it is the whole bargaining position.")


def demo_strategy():
    print("\n" + "=" * 66)
    print("DEMO 3: Mechanism design — the receiving side can gain by lying")
    print("=" * 66)
    men, women = TWO_SIDED_MEN, TWO_SIDED_WOMEN
    honest = gale_shapley(men, women)
    print(f"\n  X truly ranks {women['X']}")
    print(f"  men-proposing, everyone honest: {honest}")
    print("  X ends up with A, her LAST choice.")

    lying = dict(women)
    lying["X"] = ["B"]  # truncation: declare A unacceptable
    result = gale_shapley(men, lying)
    print(f"\n  X truncates her list to {lying['X']} (declares A unacceptable)")
    print(f"  men-proposing again: {result}")
    print("  X now gets B, her FIRST choice. Lying paid.")

    inverted = {r: p for p, r in result.items()}
    assert inverted["X"] == "B", "truncation should improve X's partner"
    print("\n  Gale-Shapley is strategy-proof for the PROPOSING side only.")
    print("  Roth (1982): no stable mechanism is strategy-proof for both sides.")


def demo_hospitals():
    print("\n" + "=" * 66)
    print("DEMO 4: Many-to-one — the residency match")
    print("=" * 66)
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
    capacities = {"mercy": 2, "general": 2, "county": 1}

    assignment = hospital_residents(residents, hospitals, capacities)
    print("\n  capacities:", capacities)
    for h, rs in assignment.items():
        print(f"    {h:8s} -> {rs}")
    bp = hospital_blocking_pairs(assignment, residents, hospitals, capacities)
    print(f"  blocking pairs: {bp}")
    assert not bp
    for h, rs in assignment.items():
        assert len(rs) <= capacities[h], "capacity violated"


if __name__ == "__main__":
    demo_basic()
    demo_proposer_optimality()
    demo_strategy()
    demo_hospitals()
    print("\nAll day-132 demos complete.")
