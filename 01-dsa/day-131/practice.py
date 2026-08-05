"""
Day 131 Practice: Job Scheduling — EDF, Deadline-Greedy, Weighted DP

Targets the functions in job_scheduling.py:
  schedule_max_jobs, schedule_max_profit_unit, edf_simulate,
  weighted_job_scheduling

6 exercises. Implement TODOs, then run: python practice.py
"""

import heapq
from bisect import bisect_right


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
# Exercise 1: Unit jobs, maximise the COUNT finished by their deadline
# ---------------------------------------------------------------------------

def schedule_max_jobs(jobs):
    """
    jobs: list of (id, deadline). Every job takes one time unit.
    Return (count, ids in deadline order).

    Greedy: sort by deadline. A job with deadline d can only ever occupy one
    of slots 0..d-1, so if d slots are already committed, no schedule can fit
    this job as well.
    """
    # TODO: sort by deadline, keep a heap of what is scheduled
    pass


def _sol_schedule_max_jobs(jobs):
    sorted_jobs = sorted(jobs, key=lambda x: x[1])
    scheduled = []
    for jid, d in sorted_jobs:
        if len(scheduled) < d:
            heapq.heappush(scheduled, (d, jid))
        # else: every slot before d is taken, and by an equally urgent job
    ordered = sorted((d, jid) for d, jid in scheduled)
    return len(ordered), [jid for _, jid in ordered]


# ---------------------------------------------------------------------------
# Exercise 2: Unit jobs, maximise PROFIT
# ---------------------------------------------------------------------------

def schedule_max_profit_unit(jobs):
    """
    jobs: list of (id, deadline, profit). Every job takes one time unit.
    Return (total_profit, ids in deadline order).

    Same sweep, but now a full slot window is not the end of the story: evict
    the least profitable job already chosen if this one pays more. The heap is
    keyed on profit precisely so that eviction is O(log n).
    """
    # TODO: min-heap on profit, evict when it pays
    pass


def _sol_schedule_max_profit_unit(jobs):
    sorted_jobs = sorted(jobs, key=lambda x: x[1])
    selected = []  # min-heap of (profit, id, deadline)
    for jid, d, p in sorted_jobs:
        if len(selected) < d:
            heapq.heappush(selected, (p, jid, d))
        elif selected and selected[0][0] < p:
            heapq.heappop(selected)
            heapq.heappush(selected, (p, jid, d))
    total = sum(p for p, _, _ in selected)
    ordered = sorted(selected, key=lambda x: x[2])
    return total, [jid for _, jid, _ in ordered]


# ---------------------------------------------------------------------------
# Exercise 3: Earliest Deadline First, preemptive
# ---------------------------------------------------------------------------

def edf_simulate(jobs, total_time):
    """
    jobs: list of (id, release_time, processing_time, deadline).
    Simulate slots t = 0 .. total_time-1, one unit each, preemptive.

    Return (timeline, finished) where timeline[t] is the id running in slot t
    (or None if nothing is available) and finished maps id -> completion time,
    or (completion_or_None, "MISS") when the deadline was missed.

    EDF is optimal for preemptive single-processor scheduling: if ANY schedule
    meets all deadlines, EDF does.
    """
    # TODO: each slot, run the released unfinished job with the nearest deadline
    pass


def _sol_edf_simulate(jobs, total_time):
    remaining, release, deadline = {}, {}, {}
    for jid, r, p, d in jobs:
        remaining[jid] = p
        release[jid] = r
        deadline[jid] = d

    timeline = []
    finished = {jid: None for jid, _, _, _ in jobs}

    for t in range(total_time):
        candidates = [jid for jid in remaining
                      if release[jid] <= t and remaining[jid] > 0]
        if not candidates:
            timeline.append(None)   # an idle slot is information, not a gap
            continue
        candidates.sort(key=lambda jid: (deadline[jid], jid))
        chosen = candidates[0]
        timeline.append(chosen)
        remaining[chosen] -= 1
        if remaining[chosen] == 0:
            finished[chosen] = t + 1

    for jid in finished:
        if finished[jid] is None or finished[jid] > deadline[jid]:
            finished[jid] = (finished[jid], "MISS")
    return timeline, finished


# ---------------------------------------------------------------------------
# Exercise 4: The predecessor lookup that makes the DP O(n log n)
# ---------------------------------------------------------------------------

def latest_compatible(finishes, start, hi):
    """
    `finishes` is sorted ascending. Return the number of jobs among the first
    `hi` whose finish time is <= start — i.e. the DP index p(i).

    Linear scanning here is what turns an O(n log n) algorithm into O(n^2).
    """
    # TODO: binary search, bounded by hi
    pass


def _sol_latest_compatible(finishes, start, hi):
    # bisect_right gives the insertion point, which is exactly the count of
    # entries <= start — already the index the DP wants.
    return bisect_right(finishes, start, hi=hi)


# ---------------------------------------------------------------------------
# Exercise 5: Weighted interval scheduling — DP, not greedy
# ---------------------------------------------------------------------------

def weighted_job_scheduling(jobs):
    """
    jobs: list of (start, finish, profit). Intervals may overlap.
    Return the maximum total profit over a non-overlapping subset.

    dp[i] = max(dp[i-1], profit[i-1] + dp[p(i)]) after sorting by finish time.
    Sorting by finish is what makes p(i) a prefix, and therefore searchable.
    """
    # TODO: sort by finish, then the include/exclude recurrence
    pass


def _sol_weighted_job_scheduling(jobs):
    if not jobs:
        return 0
    sorted_jobs = sorted(jobs, key=lambda x: x[1])
    n = len(sorted_jobs)
    starts = [s for s, _, _ in sorted_jobs]
    finishes = [f for _, f, _ in sorted_jobs]
    profits = [p for _, _, p in sorted_jobs]

    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        j = _sol_latest_compatible(finishes, starts[i - 1], i - 1)
        include = profits[i - 1] + dp[j]
        exclude = dp[i - 1]
        dp[i] = max(include, exclude)
    return dp[n]


# ---------------------------------------------------------------------------
# Exercise 6: The greedy trap — why exercise 5 has to be a DP
# ---------------------------------------------------------------------------

def greedy_by_profit(jobs):
    """
    Take the most profitable job that still fits, repeatedly.
    Return the total profit. This is NOT optimal — that is the point.
    """
    # TODO: sort by profit descending, keep what does not overlap
    pass


def _sol_greedy_by_profit(jobs):
    chosen = []
    total = 0
    for s, f, p in sorted(jobs, key=lambda x: -x[2]):
        # Half-open intervals: [s, f) and [s2, f2) overlap iff s < f2 and s2 < f.
        if all(not (s < f2 and s2 < f) for s2, f2 in chosen):
            chosen.append((s, f))
            total += p
    return total


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

    print("Exercise 1: schedule_max_jobs")
    check("five jobs, four fit",
          try_or_sol("schedule_max_jobs",
                     [("a", 4), ("b", 1), ("c", 1), ("d", 2), ("e", 3)]),
          (4, ["b", "d", "e", "a"]))
    # b and c both need slot 0; only one of them can run.
    check("two jobs share deadline 1",
          try_or_sol("schedule_max_jobs",
                     [("a", 2), ("b", 1), ("c", 2), ("d", 1), ("e", 3)]),
          (3, ["b", "a", "e"]))
    # Four jobs all due by t=3: the deadline itself caps the count at 3.
    check("deadline caps the count",
          try_or_sol("schedule_max_jobs",
                     [("a", 3), ("b", 3), ("c", 3), ("d", 3)]),
          (3, ["a", "b", "c"]))
    check("empty", try_or_sol("schedule_max_jobs", []), (0, []))

    print("\nExercise 2: schedule_max_profit_unit")
    check("classic five",
          try_or_sol("schedule_max_profit_unit",
                     [("a", 2, 100), ("b", 1, 19), ("c", 2, 27),
                      ("d", 1, 25), ("e", 3, 15)]),
          (142, ["a", "c", "e"]))
    # c(40) must evict b(10) from the single slot before deadline 1.
    check("eviction beats first-come",
          try_or_sol("schedule_max_profit_unit",
                     [("a", 4, 20), ("b", 1, 10), ("c", 1, 40), ("d", 1, 30)]),
          (60, ["c", "a"]))
    check("one slot, take the richer",
          try_or_sol("schedule_max_profit_unit", [("a", 1, 10), ("b", 1, 20)]),
          (20, ["b"]))

    print("\nExercise 3: edf_simulate")
    # J2 preempts J1 at t=1 because its deadline (4) is nearer than J1's (5).
    check("three jobs, all on time",
          try_or_sol("edf_simulate",
                     [("J1", 0, 2, 5), ("J2", 1, 3, 4), ("J3", 3, 1, 6)], 6),
          (["J1", "J2", "J2", "J2", "J1", "J3"],
           {"J1": 5, "J2": 4, "J3": 6}))
    check("a missed deadline is reported, not hidden",
          try_or_sol("edf_simulate", [("A", 0, 3, 2)], 4),
          (["A", "A", "A", None], {"A": (3, "MISS")}))
    check("idle slots before release",
          try_or_sol("edf_simulate", [("A", 2, 1, 4)], 4),
          ([None, None, "A", None], {"A": 3}))
    check("nearest deadline goes first",
          try_or_sol("edf_simulate", [("A", 0, 1, 1), ("B", 0, 1, 2)], 3),
          (["A", "B", None], {"A": 1, "B": 2}))

    print("\nExercise 4: latest_compatible")
    finishes = [3, 5, 19, 100]
    check("start 6 clears the first two",
          try_or_sol("latest_compatible", finishes, 6, 2), 2)
    check("start 2 clears nothing",
          try_or_sol("latest_compatible", finishes, 2, 3), 0)
    # A job finishing exactly at `start` IS compatible with a half-open model.
    check("finish == start is compatible",
          try_or_sol("latest_compatible", finishes, 3, 4), 1)
    check("hi bounds the search",
          try_or_sol("latest_compatible", finishes, 100, 2), 2)

    print("\nExercise 5: weighted_job_scheduling")
    check("two halves beat one whole",
          try_or_sol("weighted_job_scheduling",
                     [(0, 10, 100), (0, 5, 60), (5, 10, 60)]), 120)
    check("one long job wins here",
          try_or_sol("weighted_job_scheduling",
                     [(1, 3, 50), (3, 5, 20), (6, 19, 100), (2, 100, 200)]), 200)
    check("non-overlapping chain",
          try_or_sol("weighted_job_scheduling",
                     [(0, 3, 5), (3, 6, 5), (6, 9, 5)]), 15)
    check("empty", try_or_sol("weighted_job_scheduling", []), 0)
    check("single job", try_or_sol("weighted_job_scheduling", [(1, 2, 5)]), 5)

    print("\nExercise 6: greedy_by_profit (the trap)")
    trap = [(0, 10, 100), (0, 5, 60), (5, 10, 60)]
    check("greedy grabs the fat job", try_or_sol("greedy_by_profit", trap), 100)
    # This gap is the whole reason exercise 5 is a DP: a locally best choice
    # blocks two choices that together pay more.
    check("and loses to the DP",
          try_or_sol("greedy_by_profit", trap)
          < try_or_sol("weighted_job_scheduling", trap), True)
    # When nothing overlaps, greedy has no chance to go wrong.
    chain = [(0, 3, 5), (3, 6, 5), (6, 9, 5)]
    check("greedy is fine when nothing overlaps",
          try_or_sol("greedy_by_profit", chain),
          try_or_sol("weighted_job_scheduling", chain))
    # Greedy is a feasible schedule, so it is a lower bound on the optimum.
    cases = [trap, chain, [(1, 3, 50), (3, 5, 20), (6, 19, 100), (2, 100, 200)],
             [(1, 2, 50), (2, 100, 200), (3, 5, 20), (6, 19, 100)]]
    check("greedy never beats the DP",
          all(try_or_sol("greedy_by_profit", c)
              <= try_or_sol("weighted_job_scheduling", c) for c in cases), True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
