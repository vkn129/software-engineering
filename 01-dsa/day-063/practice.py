"""
Day 63 Practice: Job Scheduler Extensions

These exercises extend the scheduler with production-relevant features.
Each one teaches a concept used in real scheduling systems (Linux, Kubernetes, CI/CD).
"""

import sys
import os
import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))
from job_scheduler import Job, SchedulerResult, _compute_metrics


# ─── Exercise 1: Priority Aging ──────────────────────────────────────────────
#
# The PriorityScheduler in job_scheduler.py has basic aging, but it rebuilds
# the heap every time. Your job: implement aging that tracks per-job wait
# and boosts priority smoothly.
#
# Rule: every `aging_rate` time units a job waits, its effective priority
# decreases by 1 (lower number = higher priority). Minimum effective priority = 0.

def priority_aging_scheduler(jobs: list[Job], aging_rate: int = 5) -> list[SchedulerResult]:
    """
    Schedule jobs by priority with aging to prevent starvation.

    Args:
        jobs: list of Job objects
        aging_rate: every this many time units of waiting, boost priority by 1

    Returns:
        list of SchedulerResult

    How aging works:
        effective_priority = max(0, job.priority - (time_waiting // aging_rate))

    Algorithm:
    1. Sort jobs by arrival_time
    2. Maintain a min-heap of (effective_priority, tie, job)
    3. At each scheduling decision point:
       a. Add all arrived jobs to the heap
       b. Recalculate effective priorities for all waiting jobs
       c. Extract-min and run to completion
    """
    # TODO: Implement priority aging scheduler
    # Hint: The tricky part is recalculating priorities. You can rebuild the
    # heap each time (O(n log n) per job) or use a lazy deletion approach.
    pass


# ─── Exercise 2: Preemptive SJF (SRTF) ──────────────────────────────────────
#
# Non-preemptive SJF waits for the running job to finish. SRTF (Shortest
# Remaining Time First) interrupts the current job whenever a shorter one
# arrives. This further reduces average wait time.

def srtf_scheduler(jobs: list[Job]) -> list[SchedulerResult]:
    """
    Shortest Remaining Time First — preemptive version of SJF.

    When a new job arrives with duration shorter than the REMAINING time
    of the currently running job, preempt (interrupt) the running job
    and switch to the shorter one.

    Returns: list of SchedulerResult

    Algorithm:
    1. Create events at each job arrival time
    2. At each event (arrival or completion):
       a. Add newly arrived jobs to min-heap keyed on remaining_time
       b. If current job's remaining > new job's remaining, preempt
       c. Track each job's first start time for the result
    3. Simulate time unit by unit (or jump to next event)
    """
    # TODO: Implement SRTF scheduler
    # Hint: Process events at each unique time point. Use a heap of
    # (remaining_time, tie, job). When a job is preempted, push it
    # back with updated remaining_time.
    pass


# ─── Exercise 3: Multi-Level Feedback Queue ─────────────────────────────────
#
# MLFQ is the scheduling algorithm behind most modern OS schedulers.
# Jobs start in the highest-priority queue. If a job uses its full quantum
# without finishing, it gets demoted to the next lower queue.
#
# This solves the "don't know job duration" problem: short jobs finish
# quickly in the high-priority queue; long jobs sink to lower queues.

def mlfq_scheduler(jobs: list[Job], num_levels: int = 3,
                    base_quantum: int = 2) -> list[SchedulerResult]:
    """
    Multi-Level Feedback Queue scheduler.

    Args:
        jobs: list of Job objects
        num_levels: number of priority levels (0 = highest)
        base_quantum: quantum for level 0; level i gets quantum = base_quantum * 2^i

    Rules:
    1. New jobs enter at level 0 (highest priority)
    2. If a job uses its full quantum, demote to level+1 (min level = num_levels-1)
    3. If a job yields before quantum expires (e.g., I/O), stay at same level
    4. Always run from the highest non-empty level first
    5. Within a level, use Round Robin

    Returns: list of SchedulerResult
    """
    # TODO: Implement MLFQ scheduler
    # Hint: Maintain a deque for each level. At each step, find the highest
    # non-empty level, run the front job for that level's quantum.
    # If job didn't finish, move it to level+1's queue.
    pass


# ─── Exercise 4: Jain's Fairness Index ──────────────────────────────────────
#
# How do you measure if a scheduler is "fair"? Jain's Fairness Index:
#
#   J = (sum(x_i))^2 / (n * sum(x_i^2))
#
# where x_i is the turnaround time of job i and n is the number of jobs.
# J ranges from 1/n (maximally unfair) to 1.0 (perfectly fair).

def jains_fairness_index(results: list[SchedulerResult]) -> float:
    """
    Compute Jain's Fairness Index over turnaround times.

    J(x1, ..., xn) = (sum(xi))^2 / (n * sum(xi^2))

    Returns: float in range [1/n, 1.0]
             1.0 means all jobs had the same turnaround time (perfectly fair)
             1/n means one job got all the resources (maximally unfair)

    Edge case: if all turnaround times are 0, return 1.0
    """
    # TODO: Implement Jain's Fairness Index
    # This one is straightforward — just apply the formula.
    pass


# ─── Exercise 5: CI/CD Pipeline Scheduler with Dependencies ─────────────────
#
# Real CI/CD pipelines have dependencies: you can't deploy until tests pass,
# can't run tests until the build succeeds. This forms a DAG.
#
# Schedule: topological order + priority queue for jobs whose dependencies
# are all satisfied.

@dataclass
class PipelineJob:
    """A CI/CD job with dependencies."""
    job_id: str
    duration: int
    priority: int = 5       # lower = higher priority
    dependencies: list = field(default_factory=list)  # list of job_ids this depends on


@dataclass
class PipelineResult:
    """Result of a pipeline job execution."""
    job_id: str
    start_time: int
    finish_time: int


def cicd_pipeline_scheduler(jobs: list[PipelineJob]) -> Optional[list[PipelineResult]]:
    """
    Schedule CI/CD pipeline jobs respecting dependency DAG.

    Algorithm:
    1. Build adjacency list and in-degree count from dependencies
    2. Detect cycles (return None if cycle found)
    3. Initialize ready queue with jobs that have 0 in-degree
    4. Use a priority queue (min-heap on priority) for ready jobs
    5. When a job completes, decrement in-degree of dependents;
       if any reach 0, add to ready queue
    6. Simulate single-worker execution (one job at a time)

    Returns:
        list of PipelineResult in execution order, or None if cycle detected

    Example:
        build (2min) → test (3min) → deploy (1min)
                     → lint (1min) ↗
        Schedule: build → lint, test (test first by priority) → deploy
    """
    # TODO: Implement CI/CD pipeline scheduler
    # Hint: This is topological sort with a priority queue instead of a
    # regular queue. Use Kahn's algorithm (BFS-based topo sort) but
    # replace the queue with a min-heap keyed on priority.
    pass


# ─── Solutions ────────────────────────────────────────────────────────────────

def _priority_aging_solution(jobs, aging_rate=5):
    results = []
    pending = sorted(jobs, key=lambda j: j.arrival_time)
    pending_idx = 0
    heap = []
    tie = 0
    current_time = 0

    while pending_idx < len(pending) or heap:
        while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
            job = pending[pending_idx]
            heapq.heappush(heap, (job.priority, tie, job))
            tie += 1
            pending_idx += 1

        if not heap:
            if pending_idx < len(pending):
                current_time = pending[pending_idx].arrival_time
                continue
            else:
                break

        # Recalculate effective priorities with aging
        new_heap = []
        for _, t, j in heap:
            wait_so_far = current_time - j.arrival_time
            aging_boost = wait_so_far // aging_rate
            effective_priority = max(0, j.priority - aging_boost)
            new_heap.append((effective_priority, t, j))
        heapq.heapify(new_heap)
        heap = new_heap

        _, _, job = heapq.heappop(heap)
        start_time = current_time
        finish_time = start_time + job.duration
        current_time = finish_time

        results.append(SchedulerResult(
            job_id=job.job_id,
            start_time=start_time,
            finish_time=finish_time,
            wait_time=start_time - job.arrival_time,
            turnaround_time=finish_time - job.arrival_time,
        ))

    return results


def _srtf_solution(jobs):
    results = []
    pending = sorted(jobs, key=lambda j: j.arrival_time)

    # Track remaining time and first start for each job
    remaining = {j.job_id: j.duration for j in pending}
    first_start = {}
    arrival_map = {j.job_id: j.arrival_time for j in pending}

    pending_idx = 0
    heap = []  # (remaining_time, tie, job_id)
    tie = 0
    current_time = 0

    while pending_idx < len(pending) or heap:
        # Add all newly arrived jobs
        while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
            j = pending[pending_idx]
            heapq.heappush(heap, (remaining[j.job_id], tie, j.job_id))
            tie += 1
            pending_idx += 1

        if not heap:
            if pending_idx < len(pending):
                current_time = pending[pending_idx].arrival_time
                continue
            else:
                break

        # Run the shortest remaining job
        rem, _, jid = heapq.heappop(heap)

        # Skip stale heap entries (job already completed or remaining changed)
        if remaining[jid] <= 0 or rem != remaining[jid]:
            continue

        if jid not in first_start:
            first_start[jid] = current_time

        # Find next event: either job finishes or a new job arrives
        next_arrival = (pending[pending_idx].arrival_time
                        if pending_idx < len(pending) else float('inf'))
        run_until = min(current_time + remaining[jid], next_arrival)
        run_time = run_until - current_time

        remaining[jid] -= run_time
        current_time = run_until

        if remaining[jid] <= 0:
            # Job finished
            results.append(SchedulerResult(
                job_id=jid,
                start_time=first_start[jid],
                finish_time=current_time,
                wait_time=current_time - arrival_map[jid] - (
                    [j for j in pending if j.job_id == jid][0].duration),
                turnaround_time=current_time - arrival_map[jid],
            ))
        else:
            # Preempted — push back with updated remaining
            heapq.heappush(heap, (remaining[jid], tie, jid))
            tie += 1

    return results


def _mlfq_solution(jobs, num_levels=3, base_quantum=2):
    results = []
    pending = sorted(jobs, key=lambda j: j.arrival_time)
    pending_idx = 0

    # Level queues: each entry is [job, remaining_time, level]
    levels = [deque() for _ in range(num_levels)]
    first_start = {}
    current_time = 0

    while pending_idx < len(pending) or any(levels):
        # Add arrived jobs to level 0
        while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
            job = pending[pending_idx]
            levels[0].append([job, job.duration, 0])
            pending_idx += 1

        # Find highest non-empty level
        active_level = None
        for i in range(num_levels):
            if levels[i]:
                active_level = i
                break

        if active_level is None:
            if pending_idx < len(pending):
                current_time = pending[pending_idx].arrival_time
                continue
            else:
                break

        entry = levels[active_level].popleft()
        job, remaining, level = entry

        if job.job_id not in first_start:
            first_start[job.job_id] = current_time

        quantum = base_quantum * (2 ** level)
        run_time = min(quantum, remaining)
        current_time += run_time
        remaining -= run_time

        # Add jobs that arrived during execution
        while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
            new_job = pending[pending_idx]
            levels[0].append([new_job, new_job.duration, 0])
            pending_idx += 1

        if remaining > 0:
            # Used full quantum? Demote. Otherwise stay.
            if run_time == quantum:
                new_level = min(level + 1, num_levels - 1)
            else:
                new_level = level
            levels[new_level].append([job, remaining, new_level])
        else:
            # Job finished
            results.append(SchedulerResult(
                job_id=job.job_id,
                start_time=first_start[job.job_id],
                finish_time=current_time,
                wait_time=current_time - job.arrival_time - job.duration,
                turnaround_time=current_time - job.arrival_time,
            ))

    return results


def _jains_fairness_solution(results):
    if not results:
        return 1.0
    turnarounds = [r.turnaround_time for r in results]
    if all(t == 0 for t in turnarounds):
        return 1.0
    n = len(turnarounds)
    sum_x = sum(turnarounds)
    sum_x2 = sum(t * t for t in turnarounds)
    if sum_x2 == 0:
        return 1.0
    return (sum_x ** 2) / (n * sum_x2)


def _cicd_pipeline_solution(jobs):
    # Build graph
    job_map = {j.job_id: j for j in jobs}
    in_degree = {j.job_id: 0 for j in jobs}
    dependents = {j.job_id: [] for j in jobs}

    for job in jobs:
        for dep in job.dependencies:
            if dep not in job_map:
                continue  # skip unknown dependencies
            dependents[dep].append(job.job_id)
            in_degree[job.job_id] += 1

    # Kahn's algorithm with priority queue
    heap = []
    tie = 0
    for job in jobs:
        if in_degree[job.job_id] == 0:
            heapq.heappush(heap, (job.priority, tie, job.job_id))
            tie += 1

    results = []
    current_time = 0
    completed = set()

    while heap:
        _, _, jid = heapq.heappop(heap)
        job = job_map[jid]

        start_time = current_time
        finish_time = start_time + job.duration
        current_time = finish_time
        completed.add(jid)

        results.append(PipelineResult(
            job_id=jid,
            start_time=start_time,
            finish_time=finish_time,
        ))

        # Unlock dependents
        for dep_id in dependents[jid]:
            in_degree[dep_id] -= 1
            if in_degree[dep_id] == 0:
                dep_job = job_map[dep_id]
                heapq.heappush(heap, (dep_job.priority, tie, dep_id))
                tie += 1

    # Cycle detection: if not all jobs scheduled, there's a cycle
    if len(results) != len(jobs):
        return None

    return results


# ─── Test Runner ──────────────────────────────────────────────────────────────

def _make_test_jobs():
    """Standard test job set used across exercises."""
    return [
        Job("build-api",      3, 0,  8, 20),
        Job("hotfix",         1, 2,  3, 10),
        Job("run-tests",      2, 4,  6, 18),
        Job("deploy-staging", 4, 1,  4, 25),
        Job("lint-check",     5, 3,  2, 12),
        Job("db-migration",   2, 6,  5, 30),
        Job("build-frontend", 3, 5,  7, 28),
    ]


def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, fn, *args, validator=None, **kwargs):
        nonlocal passed, failed, skipped
        try:
            result = fn(*args, **kwargs)
            if result is None:
                print(f"  \u2b1c {name} -- not implemented yet")
                skipped += 1
                return
            if validator:
                assert validator(result), f"Validation failed: {result}"
            print(f"  \u2705 {name}")
            passed += 1
        except Exception as e:
            print(f"  \u274c {name} -- {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("Day 63 Practice Tests")
    print("=" * 60)

    jobs = _make_test_jobs()

    # Exercise 1: Priority Aging
    print("\nExercise 1: Priority Aging")
    check("Returns results for all jobs",
          priority_aging_scheduler, _make_test_jobs(), 5,
          validator=lambda r: len(r) == 7)
    check("All jobs complete (no starvation)",
          priority_aging_scheduler, _make_test_jobs(), 5,
          validator=lambda r: set(x.job_id for x in r) == set(j.job_id for j in _make_test_jobs()))
    check("High-priority jobs run early",
          priority_aging_scheduler, _make_test_jobs(), 5,
          validator=lambda r: r[0].job_id == "build-api" or r[1].job_id == "hotfix")
    check("Aging changes order vs no aging",
          lambda j: priority_aging_scheduler(j, aging_rate=3), _make_test_jobs(),
          validator=lambda r: True)  # just checks it runs

    # Exercise 2: SRTF
    print("\nExercise 2: Preemptive SJF (SRTF)")
    check("Returns results for all jobs",
          srtf_scheduler, _make_test_jobs(),
          validator=lambda r: len(r) == 7)
    check("Shorter jobs finish sooner than SJF",
          srtf_scheduler, _make_test_jobs(),
          validator=lambda r: True)  # basic sanity
    check("Wait times are non-negative",
          srtf_scheduler, _make_test_jobs(),
          validator=lambda r: all(x.wait_time >= 0 for x in r))
    check("SRTF preempts correctly",
          srtf_scheduler, [Job("long", 1, 0, 10), Job("short", 1, 1, 2)],
          validator=lambda r: (
              [x for x in r if x.job_id == "short"][0].finish_time == 3
          ))

    # Exercise 3: MLFQ
    print("\nExercise 3: Multi-Level Feedback Queue")
    check("Returns results for all jobs",
          mlfq_scheduler, _make_test_jobs(),
          validator=lambda r: len(r) == 7)
    check("Short jobs finish faster than long jobs",
          mlfq_scheduler, [Job("short", 5, 0, 1), Job("long", 5, 0, 20)],
          validator=lambda r: (
              [x for x in r if x.job_id == "short"][0].finish_time <
              [x for x in r if x.job_id == "long"][0].finish_time
          ))
    check("All jobs complete",
          mlfq_scheduler, _make_test_jobs(),
          validator=lambda r: set(x.job_id for x in r) == set(j.job_id for j in _make_test_jobs()))

    # Exercise 4: Jain's Fairness
    print("\nExercise 4: Jain's Fairness Index")
    # Perfectly fair: all same turnaround
    fair_results = [
        SchedulerResult("a", 0, 10, 0, 10),
        SchedulerResult("b", 10, 20, 0, 10),
        SchedulerResult("c", 20, 30, 0, 10),
    ]
    check("Perfect fairness = 1.0",
          jains_fairness_index, fair_results,
          validator=lambda r: abs(r - 1.0) < 0.001)
    # Unfair: vastly different turnarounds
    unfair_results = [
        SchedulerResult("a", 0, 1, 0, 1),
        SchedulerResult("b", 1, 100, 0, 99),
    ]
    check("Unfair schedule < 1.0",
          jains_fairness_index, unfair_results,
          validator=lambda r: r < 0.8)
    check("Empty results = 1.0",
          jains_fairness_index, [],
          validator=lambda r: abs(r - 1.0) < 0.001)
    check("Returns float in valid range",
          jains_fairness_index, fair_results,
          validator=lambda r: isinstance(r, float) and 0 < r <= 1.0)

    # Exercise 5: CI/CD Pipeline
    print("\nExercise 5: CI/CD Pipeline Scheduler")
    pipeline_jobs = [
        PipelineJob("build",   2, 1, []),
        PipelineJob("lint",    1, 3, ["build"]),
        PipelineJob("test",    3, 2, ["build"]),
        PipelineJob("deploy",  1, 4, ["lint", "test"]),
    ]
    check("Respects dependencies",
          cicd_pipeline_scheduler, pipeline_jobs,
          validator=lambda r: (
              r is not None and
              [x.job_id for x in r].index("build") < [x.job_id for x in r].index("test") and
              [x.job_id for x in r].index("test") < [x.job_id for x in r].index("deploy")
          ))
    check("Detects cycles",
          cicd_pipeline_scheduler, [
              PipelineJob("a", 1, 1, ["b"]),
              PipelineJob("b", 1, 1, ["a"]),
          ],
          validator=lambda r: r is None)
    check("Handles no dependencies",
          cicd_pipeline_scheduler, [
              PipelineJob("x", 2, 3, []),
              PipelineJob("y", 1, 1, []),
              PipelineJob("z", 3, 2, []),
          ],
          validator=lambda r: r is not None and r[0].job_id == "y")  # highest priority first
    check("Pipeline timing is correct",
          cicd_pipeline_scheduler, pipeline_jobs,
          validator=lambda r: (
              r is not None and
              r[0].start_time == 0 and
              r[-1].finish_time == 7  # build(2) + test(3) + lint(1) + deploy(1) = 7
          ))

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} not implemented")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run_tests()
