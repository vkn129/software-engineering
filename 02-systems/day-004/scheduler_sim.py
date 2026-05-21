"""
CPU Scheduler Simulation — Day 4: Context Switching & CPU Scheduling

Implements four schedulers on the same workload:
  1. FCFS  — First Come First Served
  2. SJF   — Shortest Job First (non-preemptive)
  3. RR    — Round Robin (configurable quantum)
  4. MLFQ  — Multi-Level Feedback Queue (3 queues, priority boost)

Outputs a text Gantt chart and a metrics table for each scheduler.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Job:
    """Represents a process/job submitted to the scheduler."""
    id: str
    arrival: int          # time unit when the job arrives
    burst: int            # total CPU time required
    priority: int = 0     # lower number = higher priority (used by MLFQ boost)

    # Runtime state — mutated during simulation
    remaining: int = field(init=False)
    start_time: Optional[int] = field(default=None, init=False)
    finish_time: Optional[int] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.remaining = self.burst

    def reset(self) -> None:
        """Restore to pre-simulation state (allows reuse across schedulers)."""
        self.remaining = self.burst
        self.start_time = None
        self.finish_time = None

    @property
    def wait_time(self) -> int:
        assert self.finish_time is not None and self.start_time is not None
        return self.turnaround_time - self.burst

    @property
    def turnaround_time(self) -> int:
        assert self.finish_time is not None
        return self.finish_time - self.arrival


# ---------------------------------------------------------------------------
# Gantt chart helpers
# ---------------------------------------------------------------------------

GanttSlot = Tuple[str, int, int]   # (job_id | "IDLE", start, end)


def render_gantt(slots: List[GanttSlot], title: str) -> None:
    """Print a compact text Gantt chart."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")

    # Merge consecutive slots for the same job
    merged: List[GanttSlot] = []
    for slot in slots:
        if merged and merged[-1][0] == slot[0]:
            merged[-1] = (merged[-1][0], merged[-1][1], slot[2])
        else:
            merged.append(list(slot))  # type: ignore[arg-type]

    bar = ""
    timeline = ""
    prev_end = -1
    for job_id, start, end in merged:
        width = max(end - start, len(job_id) + 2)
        bar += f"|{job_id:^{width}}"
        if prev_end != start:
            timeline += f"{start:<{width + 1}}"
        else:
            timeline += f"{start:<{width + 1}}"
        prev_end = end

    bar += "|"
    timeline += f"{merged[-1][2]}"

    print(bar)
    print(timeline)


def print_metrics(jobs: List[Job], scheduler_name: str, total_time: int) -> None:
    """Print a metrics table for the completed simulation."""
    print(f"\n  Metrics — {scheduler_name}")
    print(f"  {'Job':<8} {'Arrival':>7} {'Burst':>6} {'Start':>6} {'Finish':>7} {'Wait':>6} {'Turn':>6}")
    print(f"  {'-'*8} {'-'*7} {'-'*6} {'-'*6} {'-'*7} {'-'*6} {'-'*6}")
    total_wait = 0
    total_turn = 0
    for j in jobs:
        w = j.wait_time
        t = j.turnaround_time
        total_wait += w
        total_turn += t
        print(f"  {j.id:<8} {j.arrival:>7} {j.burst:>6} {j.start_time!s:>6} {j.finish_time!s:>7} {w:>6} {t:>6}")

    n = len(jobs)
    throughput = n / total_time
    print(f"\n  Avg wait      : {total_wait / n:.2f}")
    print(f"  Avg turnaround: {total_turn / n:.2f}")
    print(f"  Throughput    : {throughput:.4f} jobs/time-unit")


# ---------------------------------------------------------------------------
# Scheduler 1: FCFS
# ---------------------------------------------------------------------------

def fcfs(jobs: List[Job]) -> Tuple[List[GanttSlot], int]:
    """
    First Come First Served — non-preemptive, arrival-order queue.
    Pathological for short jobs that arrive behind a long one (convoy effect).
    """
    clock = 0
    slots: List[GanttSlot] = []
    # Sort by arrival, break ties by id
    queue = sorted(jobs, key=lambda j: (j.arrival, j.id))

    for job in queue:
        if clock < job.arrival:
            # CPU is idle until this job arrives
            slots.append(("IDLE", clock, job.arrival))
            clock = job.arrival

        job.start_time = clock
        slots.append((job.id, clock, clock + job.remaining))
        clock += job.remaining
        job.remaining = 0
        job.finish_time = clock

    return slots, clock


# ---------------------------------------------------------------------------
# Scheduler 2: SJF (non-preemptive)
# ---------------------------------------------------------------------------

def sjf(jobs: List[Job]) -> Tuple[List[GanttSlot], int]:
    """
    Shortest Job First — non-preemptive.
    Among all jobs that have arrived, picks the one with shortest burst.
    Minimizes average wait time. Requires knowing burst times in advance.
    """
    clock = 0
    slots: List[GanttSlot] = []
    remaining_jobs = list(jobs)
    done = 0

    while done < len(jobs):
        # All jobs that have arrived and are not yet finished
        ready = [j for j in remaining_jobs if j.arrival <= clock]

        if not ready:
            # No job ready — jump clock to next arrival
            next_arrival = min(j.arrival for j in remaining_jobs)
            slots.append(("IDLE", clock, next_arrival))
            clock = next_arrival
            continue

        # Pick job with shortest burst; tie-break by id
        job = min(ready, key=lambda j: (j.burst, j.id))
        remaining_jobs.remove(job)

        job.start_time = clock
        slots.append((job.id, clock, clock + job.remaining))
        clock += job.remaining
        job.remaining = 0
        job.finish_time = clock
        done += 1

    return slots, clock


# ---------------------------------------------------------------------------
# Scheduler 3: Round Robin
# ---------------------------------------------------------------------------

def round_robin(jobs: List[Job], quantum: int = 4) -> Tuple[List[GanttSlot], int]:
    """
    Round Robin — preemptive, each job gets at most `quantum` time units per turn.
    Fair: no starvation. Quantum is the critical tuning parameter.
    Small quantum → more context switches; large quantum → degrades to FCFS.
    """
    clock = 0
    slots: List[GanttSlot] = []
    queue: List[Job] = []
    remaining_jobs = sorted(jobs, key=lambda j: (j.arrival, j.id))
    job_idx = 0  # pointer into sorted remaining_jobs

    # Seed queue with jobs that arrive at time 0
    while job_idx < len(remaining_jobs) and remaining_jobs[job_idx].arrival <= clock:
        queue.append(remaining_jobs[job_idx])
        job_idx += 1

    while queue or job_idx < len(remaining_jobs):
        if not queue:
            # Nothing ready — jump to next arrival
            next_arrival = remaining_jobs[job_idx].arrival
            slots.append(("IDLE", clock, next_arrival))
            clock = next_arrival
            while job_idx < len(remaining_jobs) and remaining_jobs[job_idx].arrival <= clock:
                queue.append(remaining_jobs[job_idx])
                job_idx += 1
            continue

        job = queue.pop(0)

        if job.start_time is None:
            job.start_time = clock

        run_for = min(quantum, job.remaining)
        slots.append((job.id, clock, clock + run_for))
        job.remaining -= run_for
        clock += run_for

        # Admit newly-arrived jobs before re-queuing current job
        new_arrivals: List[Job] = []
        while job_idx < len(remaining_jobs) and remaining_jobs[job_idx].arrival <= clock:
            new_arrivals.append(remaining_jobs[job_idx])
            job_idx += 1
        queue.extend(new_arrivals)

        if job.remaining > 0:
            queue.append(job)   # not done — go to back of queue
        else:
            job.finish_time = clock

    return slots, clock


# ---------------------------------------------------------------------------
# Scheduler 4: MLFQ
# ---------------------------------------------------------------------------

def mlfq(
    jobs: List[Job],
    quantums: Tuple[int, int, int] = (2, 4, 8),
    boost_interval: int = 20,
) -> Tuple[List[GanttSlot], int]:
    """
    Multi-Level Feedback Queue — 3 priority levels.
    - Level 0 (highest): quantum = quantums[0]
    - Level 1 (medium):  quantum = quantums[1]
    - Level 2 (lowest):  quantum = quantums[2]

    New jobs enter level 0.
    A job that exhausts its quantum is demoted to the next level.
    A job that voluntarily yields (remaining < quantum) stays at same level.
    Every `boost_interval` time units, ALL jobs are boosted back to level 0.
    """
    clock = 0
    slots: List[GanttSlot] = []
    queues: List[List[Job]] = [[], [], []]   # index = priority level
    job_levels: dict[str, int] = {}
    remaining_jobs = sorted(jobs, key=lambda j: (j.arrival, j.id))
    job_idx = 0
    last_boost = 0

    def admit_arrivals() -> None:
        nonlocal job_idx
        while job_idx < len(remaining_jobs) and remaining_jobs[job_idx].arrival <= clock:
            j = remaining_jobs[job_idx]
            job_levels[j.id] = 0
            queues[0].append(j)
            job_idx += 1

    admit_arrivals()

    total_jobs = len(jobs)
    finished = 0

    while finished < total_jobs:
        # Priority boost: move all jobs in levels 1 and 2 back to level 0
        if clock - last_boost >= boost_interval:
            for level in (1, 2):
                for j in queues[level]:
                    job_levels[j.id] = 0
                queues[0].extend(queues[1])
                queues[0].extend(queues[2])
                queues[1].clear()
                queues[2].clear()
            last_boost = clock

        # Find the highest-priority non-empty queue
        current_queue_idx = None
        for qi in range(3):
            if queues[qi]:
                current_queue_idx = qi
                break

        if current_queue_idx is None:
            # All queues empty — jump to next arrival
            if job_idx < len(remaining_jobs):
                next_arr = remaining_jobs[job_idx].arrival
                slots.append(("IDLE", clock, next_arr))
                clock = next_arr
                admit_arrivals()
            continue

        job = queues[current_queue_idx].pop(0)
        q = quantums[current_queue_idx]

        if job.start_time is None:
            job.start_time = clock

        run_for = min(q, job.remaining)
        slots.append((job.id, clock, clock + run_for))
        job.remaining -= run_for
        clock += run_for

        admit_arrivals()

        # Trigger boost check after clock advance
        if clock - last_boost >= boost_interval:
            # Will be handled at top of next loop iteration
            pass

        if job.remaining <= 0:
            job.finish_time = clock
            finished += 1
        else:
            # Demote if it used its full quantum (assumed CPU-bound)
            if run_for == q:
                new_level = min(current_queue_idx + 1, 2)
            else:
                new_level = current_queue_idx  # yielded early — I/O-bound, keep priority
            job_levels[job.id] = new_level
            queues[new_level].append(job)

    return slots, clock


# ---------------------------------------------------------------------------
# Run all schedulers on the same workload
# ---------------------------------------------------------------------------

def deep_copy_jobs(jobs: List[Job]) -> List[Job]:
    """Return fresh copies of jobs with runtime state reset."""
    copies = copy.deepcopy(jobs)
    for j in copies:
        j.reset()
    return copies


def run_all(jobs: List[Job], rr_quantum: int = 4) -> None:
    """Run FCFS, SJF, RR, and MLFQ on the same workload and print results."""
    print("\n" + "=" * 60)
    print("  WORKLOAD")
    print("=" * 60)
    print(f"  {'ID':<8} {'Arrival':>7} {'Burst':>6} {'Priority':>9}")
    print(f"  {'-'*8} {'-'*7} {'-'*6} {'-'*9}")
    for j in jobs:
        print(f"  {j.id:<8} {j.arrival:>7} {j.burst:>6} {j.priority:>9}")

    schedulers = [
        ("FCFS",                    lambda js: fcfs(js)),
        ("SJF (non-preemptive)",    lambda js: sjf(js)),
        (f"Round Robin (Q={rr_quantum})",
                                    lambda js: round_robin(js, rr_quantum)),
        ("MLFQ (Q=2/4/8, boost=20)", lambda js: mlfq(js)),
    ]

    for name, scheduler_fn in schedulers:
        job_copies = deep_copy_jobs(jobs)
        slots, total_time = scheduler_fn(job_copies)
        render_gantt(slots, f"Gantt — {name}")
        print_metrics(job_copies, name, total_time)

    # Observations
    print("\n" + "=" * 60)
    print("  TRADE-OFF SUMMARY")
    print("=" * 60)
    print("""
  FCFS:  Simplest. Convoy effect makes short jobs wait behind long ones.
         Average wait time is worst when job lengths are heterogeneous.

  SJF:   Optimal average wait time (non-preemptive). Requires knowing
         burst durations in advance — impossible in production. Starves
         long jobs if short jobs keep arriving.

  RR:    Fair and responsive. No starvation. Quantum choice is critical:
         too small → overhead dominates; too large → degrades to FCFS.
         Context switch overhead (not modeled here) penalizes small Q.

  MLFQ:  Best practical algorithm. Approximates SJF without burst time
         knowledge. Adapts: I/O-bound jobs stay in high-priority queues
         (short quanta, fast response); CPU-bound jobs sink to low queues
         (long quanta, high throughput). Boost prevents starvation.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Representative workload:
    # P1: long CPU-bound job (arrives first → tests convoy effect under FCFS)
    # P2–P4: short interactive-style jobs
    # P5: medium-length job arriving late
    # P6–P7: very short jobs arriving mid-simulation
    workload = [
        Job("P1", arrival=0,  burst=20, priority=2),   # long CPU-bound
        Job("P2", arrival=0,  burst=3,  priority=0),   # short, high priority
        Job("P3", arrival=1,  burst=5,  priority=1),   # short
        Job("P4", arrival=2,  burst=2,  priority=0),   # very short
        Job("P5", arrival=5,  burst=10, priority=1),   # medium, late arrival
        Job("P6", arrival=10, burst=1,  priority=0),   # tiny, arrives mid-sim
        Job("P7", arrival=12, burst=4,  priority=1),   # short, arrives mid-sim
    ]

    run_all(workload, rr_quantum=4)
