"""
Day 127: Greedy Strategy — Activity Selection & Friends
Sort, sweep, commit. No backtracking. O(n log n).

Includes:
  - Activity selection (sort by finish time)
  - Wrong strategies (sort by start, by duration) with counterexamples
  - Minimum platforms (interval partitioning)
  - Maximum meetings in a single room
"""

from math import inf


# ---------------------------------------------------------------------------
# 1. Activity Selection — correct greedy
# ---------------------------------------------------------------------------

def activity_selection(intervals):
    """
    Pick the maximum number of non-overlapping intervals.
    Strategy: sort by finish time, take greedily.
    Exchange argument: any optimal solution can be transformed to start with
    the earliest-finishing activity without losing any picks.

    Time: O(n log n)   Space: O(k) for the chosen list
    """
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[1])
    chosen = []
    last_end = -inf
    for start, finish in sorted_iv:
        if start >= last_end:
            chosen.append((start, finish))
            last_end = finish
    return chosen


# ---------------------------------------------------------------------------
# 2. Wrong strategies — illustrate why other sorts fail
# ---------------------------------------------------------------------------

def activity_selection_by_start(intervals):
    """WRONG: sort by start time. A long early interval blocks many shorter ones."""
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    chosen = []
    last_end = -inf
    for start, finish in sorted_iv:
        if start >= last_end:
            chosen.append((start, finish))
            last_end = finish
    return chosen


def activity_selection_by_duration(intervals):
    """WRONG: shortest first. A short interval can split two longer compatible ones."""
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[1] - x[0])
    chosen = []
    used = []  # list of (start, finish) accepted
    for start, finish in sorted_iv:
        if all(finish <= s or start >= f for s, f in used):
            used.append((start, finish))
            chosen.append((start, finish))
    return chosen


# ---------------------------------------------------------------------------
# 3. Minimum Platforms (Interval Partitioning)
# ---------------------------------------------------------------------------

def min_platforms(intervals):
    """
    Minimum number of rooms/platforms so that all intervals can be scheduled
    (overlapping intervals need separate rooms).

    Strategy: sort arrivals and departures separately. Sweep timeline,
    increment counter on arrival, decrement on departure. Max = answer.

    This is also the chromatic number of the interval graph (greedy gives it).

    Time: O(n log n)
    """
    if not intervals:
        return 0
    arrivals = sorted(s for s, _ in intervals)
    departures = sorted(f for _, f in intervals)
    i = j = 0
    cur = peak = 0
    while i < len(arrivals):
        if arrivals[i] < departures[j]:
            cur += 1
            peak = max(peak, cur)
            i += 1
        else:
            cur -= 1
            j += 1
    return peak


# ---------------------------------------------------------------------------
# 4. Maximum Meetings — count only
# ---------------------------------------------------------------------------

def max_meetings(intervals):
    """Just the count of activity_selection. Standard interview phrasing."""
    return len(activity_selection(intervals))


# ---------------------------------------------------------------------------
# 5. Exchange-argument trace (didactic)
# ---------------------------------------------------------------------------

def explain_exchange(intervals):
    """
    Print a sketch of the exchange argument on a concrete instance.
    Shows: greedy choice g vs first pick of an arbitrary optimal O.
    """
    if not intervals:
        return
    sorted_iv = sorted(intervals, key=lambda x: x[1])
    greedy = activity_selection(intervals)
    print(f"  Greedy pick first: {greedy[0]} (earliest finish)")
    print(f"  Claim: some optimal schedule also starts with {greedy[0]}")
    print(f"  Proof: any optimal's first activity finishes >= {greedy[0][1]}")
    print(f"         swap it with {greedy[0]} → still compatible with rest")
    print(f"         → swapped schedule is optimal too")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("=" * 65)
    print("Day 127 — Greedy: Activity Selection")
    print("=" * 65)

    print("\n--- Example 1: classic ---")
    intervals = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
                 (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
    print(f"  Intervals: {intervals}")
    print(f"  Greedy (by finish): {activity_selection(intervals)}")
    print(f"  Wrong (by start):   {activity_selection_by_start(intervals)}")
    print(f"  Wrong (by duration):{activity_selection_by_duration(intervals)}")

    print("\n--- Example 2: counterexample for sort-by-start ---")
    # One giant interval starts first, blocks 3 small ones
    intervals = [(0, 100), (1, 2), (3, 4), (5, 6)]
    print(f"  Intervals: {intervals}")
    print(f"  Correct (by finish): {activity_selection(intervals)}  → 3 picks")
    print(f"  Wrong (by start):    {activity_selection_by_start(intervals)}  → 1 pick")

    print("\n--- Example 3: counterexample for sort-by-duration ---")
    # Short middle interval splits two long compatible ones
    intervals = [(0, 5), (4, 6), (5, 10)]
    print(f"  Intervals: {intervals}")
    print(f"  Correct (by finish):  {activity_selection(intervals)}  → 2 picks")
    print(f"  Wrong (by duration):  {activity_selection_by_duration(intervals)}  → 1 pick")

    print("\n--- Minimum platforms ---")
    trains = [(900, 910), (905, 920), (915, 930), (925, 940), (935, 945)]
    print(f"  Train schedule: {trains}")
    print(f"  Platforms needed: {min_platforms(trains)}")

    print("\n--- Exchange argument trace ---")
    explain_exchange([(1, 4), (3, 5), (0, 6), (5, 7)])

    print("\n" + "=" * 65)
    print("Greedy works when exchange argument holds. Always try it.")


if __name__ == "__main__":
    demo()
