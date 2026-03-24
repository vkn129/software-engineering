"""
Day 63: Job Scheduler Mini-Project
Week 9 Capstone — Heaps, Priority Queues, and Scheduling Theory

Five scheduling algorithms from scratch, all built on the same insight:
priority-based scheduling is just "extract-min from a heap" with different keys.
"""

import heapq
from dataclasses import dataclass, field
from typing import Optional, Protocol
from collections import deque


# ─── Data Types ───────────────────────────────────────────────────────────────

@dataclass
class Job:
    """A unit of work to be scheduled."""
    job_id: str
    priority: int          # lower number = higher priority
    arrival_time: int      # when the job enters the system
    duration: int          # total CPU time needed
    deadline: Optional[int] = None  # optional deadline (for EDF)
    remaining_time: int = -1        # tracks progress for preemptive schedulers

    def __post_init__(self):
        if self.remaining_time == -1:
            self.remaining_time = self.duration


@dataclass
class SchedulerResult:
    """Outcome of scheduling a single job."""
    job_id: str
    start_time: int        # when the job first started running
    finish_time: int       # when the job completed
    wait_time: int         # finish_time - arrival_time - duration
    turnaround_time: int   # finish_time - arrival_time


@dataclass
class SchedulerMetrics:
    """Aggregate metrics across all scheduled jobs."""
    avg_wait_time: float
    avg_turnaround_time: float
    throughput: float          # jobs completed / total time
    missed_deadlines: int = 0
    total_time: int = 0

    def __str__(self):
        s = (f"  Avg wait: {self.avg_wait_time:.1f}  |  "
             f"Avg turnaround: {self.avg_turnaround_time:.1f}  |  "
             f"Throughput: {self.throughput:.2f} jobs/unit")
        if self.missed_deadlines > 0:
            s += f"  |  Missed deadlines: {self.missed_deadlines}"
        return s


# ─── Scheduler Protocol ──────────────────────────────────────────────────────

class Scheduler(Protocol):
    """Interface that all schedulers implement."""

    def add_job(self, job: Job) -> None: ...
    def run(self) -> list[SchedulerResult]: ...
    def metrics(self) -> SchedulerMetrics: ...


# ─── Helper: compute metrics from results ────────────────────────────────────

def _compute_metrics(results: list[SchedulerResult], missed: int = 0) -> SchedulerMetrics:
    """Compute aggregate metrics from a list of scheduler results."""
    if not results:
        return SchedulerMetrics(0, 0, 0, missed, 0)

    total_time = max(r.finish_time for r in results)
    avg_wait = sum(r.wait_time for r in results) / len(results)
    avg_turn = sum(r.turnaround_time for r in results) / len(results)
    throughput = len(results) / total_time if total_time > 0 else 0

    return SchedulerMetrics(
        avg_wait_time=avg_wait,
        avg_turnaround_time=avg_turn,
        throughput=throughput,
        missed_deadlines=missed,
        total_time=total_time,
    )


# ─── FIFO Scheduler ──────────────────────────────────────────────────────────

class FIFOScheduler:
    """
    First In, First Out — jobs run in arrival order.

    Simple and fair, but suffers from the convoy effect: short jobs
    stuck behind long ones inflate average wait time.
    """

    def __init__(self):
        self._jobs: list[Job] = []
        self._results: list[SchedulerResult] = []

    def add_job(self, job: Job) -> None:
        self._jobs.append(job)

    def run(self) -> list[SchedulerResult]:
        self._results = []
        # Sort by arrival time, then by insertion order (stable sort)
        queue = sorted(self._jobs, key=lambda j: j.arrival_time)
        current_time = 0

        for job in queue:
            # If CPU is idle, fast-forward to the job's arrival
            start_time = max(current_time, job.arrival_time)
            finish_time = start_time + job.duration
            current_time = finish_time

            self._results.append(SchedulerResult(
                job_id=job.job_id,
                start_time=start_time,
                finish_time=finish_time,
                wait_time=start_time - job.arrival_time,
                turnaround_time=finish_time - job.arrival_time,
            ))

        return self._results

    def metrics(self) -> SchedulerMetrics:
        if not self._results:
            self.run()
        return _compute_metrics(self._results)


# ─── Priority Scheduler ──────────────────────────────────────────────────────

class PriorityScheduler:
    """
    Priority-based scheduling using a min-heap on priority value.
    Lower number = higher priority.

    Optional aging: waiting jobs get their effective priority boosted
    by 1 for every `aging_interval` time units they wait, preventing
    starvation of low-priority jobs.
    """

    def __init__(self, aging_interval: int = 0):
        self._jobs: list[Job] = []
        self._results: list[SchedulerResult] = []
        self._aging_interval = aging_interval  # 0 = no aging

    def add_job(self, job: Job) -> None:
        self._jobs.append(job)

    def run(self) -> list[SchedulerResult]:
        self._results = []
        # Sort jobs by arrival time for feeding into the system
        pending = sorted(self._jobs, key=lambda j: j.arrival_time)
        pending_idx = 0
        # Heap entries: (effective_priority, tie_breaker, job, original_arrival)
        heap: list[tuple[int, int, Job]] = []
        tie = 0
        current_time = 0

        while pending_idx < len(pending) or heap:
            # Add all jobs that have arrived by current_time
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
                job = pending[pending_idx]
                heapq.heappush(heap, (job.priority, tie, job))
                tie += 1
                pending_idx += 1

            if not heap:
                # CPU idle — skip to next arrival
                if pending_idx < len(pending):
                    current_time = pending[pending_idx].arrival_time
                    continue
                else:
                    break

            # Apply aging: recalculate effective priorities
            if self._aging_interval > 0:
                new_heap = []
                for _, t, j in heap:
                    wait_so_far = current_time - j.arrival_time
                    aging_boost = wait_so_far // self._aging_interval
                    effective_priority = max(0, j.priority - aging_boost)
                    new_heap.append((effective_priority, t, j))
                heapq.heapify(new_heap)
                heap = new_heap

            _, _, job = heapq.heappop(heap)
            start_time = current_time
            finish_time = start_time + job.duration
            current_time = finish_time

            self._results.append(SchedulerResult(
                job_id=job.job_id,
                start_time=start_time,
                finish_time=finish_time,
                wait_time=start_time - job.arrival_time,
                turnaround_time=finish_time - job.arrival_time,
            ))

        return self._results

    def metrics(self) -> SchedulerMetrics:
        if not self._results:
            self.run()
        return _compute_metrics(self._results)


# ─── Shortest Job First Scheduler ────────────────────────────────────────────

class SJFScheduler:
    """
    Shortest Job First — min-heap keyed on duration.
    Non-preemptive: once a job starts, it runs to completion.

    Provably optimal for minimizing average wait time (exchange argument):
    swapping a shorter job ahead of a longer one always reduces total wait.
    """

    def __init__(self):
        self._jobs: list[Job] = []
        self._results: list[SchedulerResult] = []

    def add_job(self, job: Job) -> None:
        self._jobs.append(job)

    def run(self) -> list[SchedulerResult]:
        self._results = []
        pending = sorted(self._jobs, key=lambda j: j.arrival_time)
        pending_idx = 0
        # Heap: (duration, tie, job)
        heap: list[tuple[int, int, Job]] = []
        tie = 0
        current_time = 0

        while pending_idx < len(pending) or heap:
            # Feed arrived jobs into the heap
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
                job = pending[pending_idx]
                heapq.heappush(heap, (job.duration, tie, job))
                tie += 1
                pending_idx += 1

            if not heap:
                if pending_idx < len(pending):
                    current_time = pending[pending_idx].arrival_time
                    continue
                else:
                    break

            _, _, job = heapq.heappop(heap)
            start_time = current_time
            finish_time = start_time + job.duration
            current_time = finish_time

            self._results.append(SchedulerResult(
                job_id=job.job_id,
                start_time=start_time,
                finish_time=finish_time,
                wait_time=start_time - job.arrival_time,
                turnaround_time=finish_time - job.arrival_time,
            ))

        return self._results

    def metrics(self) -> SchedulerMetrics:
        if not self._results:
            self.run()
        return _compute_metrics(self._results)


# ─── Round Robin Scheduler ───────────────────────────────────────────────────

class RoundRobinScheduler:
    """
    Round Robin — each job gets a fixed time quantum, then yields.
    Circular queue: unfinished jobs go to the back of the line.

    Trade-off: smaller quantum = better responsiveness, more context switches.
    Quantum = infinity degenerates to FIFO.
    """

    def __init__(self, quantum: int = 4):
        self._jobs: list[Job] = []
        self._results: list[SchedulerResult] = []
        self._quantum = quantum

    def add_job(self, job: Job) -> None:
        self._jobs.append(job)

    def run(self) -> list[SchedulerResult]:
        self._results = []
        pending = sorted(self._jobs, key=lambda j: j.arrival_time)
        pending_idx = 0

        # Queue of (job, remaining_time, first_start_time_or_None)
        rq: deque[list] = deque()
        current_time = 0
        # Track first start time per job
        first_start: dict[str, int] = {}

        while pending_idx < len(pending) or rq:
            # Add newly arrived jobs
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
                job = pending[pending_idx]
                rq.append([job, job.duration])
                pending_idx += 1

            if not rq:
                if pending_idx < len(pending):
                    current_time = pending[pending_idx].arrival_time
                    continue
                else:
                    break

            entry = rq.popleft()
            job, remaining = entry[0], entry[1]

            if job.job_id not in first_start:
                first_start[job.job_id] = current_time

            run_time = min(self._quantum, remaining)
            current_time += run_time
            remaining -= run_time

            # Add jobs that arrived during this quantum BEFORE re-enqueueing
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
                new_job = pending[pending_idx]
                rq.append([new_job, new_job.duration])
                pending_idx += 1

            if remaining > 0:
                rq.append([job, remaining])
            else:
                # Job finished
                finish_time = current_time
                self._results.append(SchedulerResult(
                    job_id=job.job_id,
                    start_time=first_start[job.job_id],
                    finish_time=finish_time,
                    wait_time=finish_time - job.arrival_time - job.duration,
                    turnaround_time=finish_time - job.arrival_time,
                ))

        return self._results

    def metrics(self) -> SchedulerMetrics:
        if not self._results:
            self.run()
        return _compute_metrics(self._results)


# ─── Earliest Deadline First Scheduler ───────────────────────────────────────

class EDFScheduler:
    """
    Earliest Deadline First — min-heap keyed on deadline.
    Non-preemptive. Tracks missed deadlines.

    Optimal for real-time systems: if any scheduler can meet all deadlines,
    EDF can too. But under overload, it fails catastrophically — it may
    miss ALL deadlines because it keeps picking the most urgent one even
    when it's already too late.
    """

    def __init__(self):
        self._jobs: list[Job] = []
        self._results: list[SchedulerResult] = []
        self._missed: int = 0

    def add_job(self, job: Job) -> None:
        if job.deadline is None:
            # Jobs without deadlines get a very large deadline
            job.deadline = 10**9
        self._jobs.append(job)

    def run(self) -> list[SchedulerResult]:
        self._results = []
        self._missed = 0
        pending = sorted(self._jobs, key=lambda j: j.arrival_time)
        pending_idx = 0
        # Heap: (deadline, tie, job)
        heap: list[tuple[int, int, Job]] = []
        tie = 0
        current_time = 0

        while pending_idx < len(pending) or heap:
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= current_time:
                job = pending[pending_idx]
                heapq.heappush(heap, (job.deadline, tie, job))
                tie += 1
                pending_idx += 1

            if not heap:
                if pending_idx < len(pending):
                    current_time = pending[pending_idx].arrival_time
                    continue
                else:
                    break

            _, _, job = heapq.heappop(heap)
            start_time = current_time
            finish_time = start_time + job.duration
            current_time = finish_time

            # Check if deadline was missed
            if job.deadline is not None and finish_time > job.deadline:
                self._missed += 1

            self._results.append(SchedulerResult(
                job_id=job.job_id,
                start_time=start_time,
                finish_time=finish_time,
                wait_time=start_time - job.arrival_time,
                turnaround_time=finish_time - job.arrival_time,
            ))

        return self._results

    def metrics(self) -> SchedulerMetrics:
        if not self._results:
            self.run()
        return _compute_metrics(self._results, self._missed)


# ─── Demo ─────────────────────────────────────────────────────────────────────

def demo():
    """Compare all five schedulers on the same job set."""

    # A realistic-ish workload: mixed priorities, durations, and arrival times
    job_specs = [
        # (job_id, priority, arrival_time, duration, deadline)
        ("build-api",     3, 0,  8,  20),
        ("hotfix",        1, 2,  3,  10),
        ("run-tests",     2, 4,  6,  18),
        ("deploy-staging",4, 1,  4,  25),
        ("lint-check",    5, 3,  2,  12),
        ("db-migration",  2, 6,  5,  30),
        ("build-frontend",3, 5,  7,  28),
    ]

    def make_jobs():
        return [Job(jid, pri, arr, dur, dl) for jid, pri, arr, dur, dl in job_specs]

    schedulers = [
        ("FIFO",             FIFOScheduler()),
        ("Priority",         PriorityScheduler()),
        ("Priority+Aging",   PriorityScheduler(aging_interval=5)),
        ("SJF",              SJFScheduler()),
        ("Round Robin (q=3)",RoundRobinScheduler(quantum=3)),
        ("EDF",              EDFScheduler()),
    ]

    print("=" * 78)
    print("JOB SCHEDULER — Comparing 6 Scheduling Algorithms")
    print("=" * 78)

    # Print the job set
    print(f"\n{'Job':<18} {'Prio':>4} {'Arrive':>7} {'Duration':>8} {'Deadline':>8}")
    print("-" * 50)
    for jid, pri, arr, dur, dl in job_specs:
        print(f"{jid:<18} {pri:>4} {arr:>7} {dur:>8} {dl:>8}")

    # Run each scheduler
    all_metrics = []
    for name, scheduler in schedulers:
        for job in make_jobs():
            scheduler.add_job(job)
        results = scheduler.run()
        m = scheduler.metrics()
        all_metrics.append((name, m, results))

    # ── Per-scheduler detail ──
    for name, m, results in all_metrics:
        print(f"\n{'─' * 78}")
        print(f"  {name}")
        print(f"{'─' * 78}")
        print(f"  {'Job':<18} {'Start':>6} {'Finish':>7} {'Wait':>6} {'Turnaround':>11}")
        print(f"  {'-'*50}")
        for r in sorted(results, key=lambda x: x.start_time):
            print(f"  {r.job_id:<18} {r.start_time:>6} {r.finish_time:>7} "
                  f"{r.wait_time:>6} {r.turnaround_time:>11}")
        print(f"\n{m}")

    # ── Comparison table ──
    print(f"\n{'=' * 78}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 78}")
    print(f"{'Scheduler':<22} {'Avg Wait':>9} {'Avg Turn':>9} {'Throughput':>11} {'Missed DL':>10}")
    print("-" * 65)
    for name, m, _ in all_metrics:
        print(f"{name:<22} {m.avg_wait_time:>9.1f} {m.avg_turnaround_time:>9.1f} "
              f"{m.throughput:>11.3f} {m.missed_deadlines:>10}")

    # ── Key observations ──
    print(f"\n{'─' * 78}")
    print("KEY OBSERVATIONS:")
    print("─" * 78)

    # Find best avg wait
    best_wait = min(all_metrics, key=lambda x: x[1].avg_wait_time)
    print(f"  - Lowest avg wait time: {best_wait[0]} ({best_wait[1].avg_wait_time:.1f})")
    print(f"    SJF is provably optimal for this metric.")

    # Find EDF missed deadlines
    edf = [x for x in all_metrics if x[0] == "EDF"][0]
    print(f"  - EDF missed {edf[1].missed_deadlines} deadline(s).")

    # Aging effect
    no_aging = [x for x in all_metrics if x[0] == "Priority"][0]
    with_aging = [x for x in all_metrics if x[0] == "Priority+Aging"][0]
    print(f"  - Priority aging changes avg wait: "
          f"{no_aging[1].avg_wait_time:.1f} -> {with_aging[1].avg_wait_time:.1f}")
    print(f"    Aging prevents starvation at the cost of slightly different ordering.")

    print()


if __name__ == "__main__":
    demo()
