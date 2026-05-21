"""
Practice Exercises — Day 4: Context Switching & CPU Scheduling

Five exercises that go beyond the simulator:
  1. SRTF  — Shortest Remaining Time First (preemptive SJF)
  2. Convoy effect — demonstrate and measure its impact on throughput
  3. Priority inheritance — fix priority inversion
  4. RR quantum tuning — show overhead vs fairness trade-off
  5. CFS-style scheduler — pick the job with smallest accumulated vruntime

Work through the TODOs first, then check the solutions below.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# ============================================================
# Shared data model (same as scheduler_sim.py)
# ============================================================

@dataclass
class Job:
    id: str
    arrival: int
    burst: int
    priority: int = 0
    remaining: int = field(init=False)
    start_time: Optional[int] = field(default=None, init=False)
    finish_time: Optional[int] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.remaining = self.burst

    def reset(self) -> None:
        self.remaining = self.burst
        self.start_time = None
        self.finish_time = None

    @property
    def turnaround_time(self) -> int:
        assert self.finish_time is not None
        return self.finish_time - self.arrival

    @property
    def wait_time(self) -> int:
        return self.turnaround_time - self.burst


def avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def print_metrics(jobs: List[Job], label: str) -> None:
    print(f"\n  [{label}]")
    for j in jobs:
        print(f"    {j.id}: wait={j.wait_time:3d}  turnaround={j.turnaround_time:3d}")
    waits = [j.wait_time for j in jobs]
    turns = [j.turnaround_time for j in jobs]
    print(f"    avg wait={avg(waits):.2f}  avg turnaround={avg(turns):.2f}")


# ============================================================
# Exercise 1: SRTF — Shortest Remaining Time First
# ============================================================
# SRTF is the preemptive version of SJF. At every time unit, the
# scheduler picks the job with the shortest REMAINING burst. If a
# new job arrives with a smaller remaining time than the current
# job, it preempts immediately.
#
# This is provably optimal for minimizing average response time
# under any preemptive scheduler (proof: exchange argument).
#
# TODO: implement srtf() below.
# ============================================================

def srtf_todo(jobs: List[Job]) -> None:
    """TODO: Implement Shortest Remaining Time First."""
    # Hints:
    #   - Simulate tick-by-tick (clock advances 1 unit per iteration)
    #   - At each tick, find the ready job (arrival <= clock) with min remaining
    #   - Run it for 1 tick, then check again (a new job might have arrived)
    #   - Record start_time on first run, finish_time when remaining hits 0
    raise NotImplementedError("implement srtf_todo()")


def exercise1() -> None:
    print("\n" + "=" * 60)
    print("Exercise 1: SRTF (Shortest Remaining Time First)")
    print("=" * 60)
    jobs = [
        Job("P1", arrival=0, burst=8),
        Job("P2", arrival=1, burst=4),
        Job("P3", arrival=2, burst=9),
        Job("P4", arrival=3, burst=5),
    ]
    # TODO: call srtf_todo(jobs) and print_metrics(jobs, "SRTF")
    # Expected: avg wait ≈ 6.5, avg turnaround ≈ 11.0
    print("  TODO: call srtf_todo() and verify metrics.")


# ============================================================
# Exercise 2: Convoy Effect
# ============================================================
# One long CPU-bound job causes short jobs to pile up behind it.
# Short jobs also need I/O, so while the long job hogs the CPU,
# the I/O device (disk) sits idle. Then all short jobs do I/O
# together. The result: poor CPU AND I/O utilization.
#
# We model it by tracking:
#   - When the CPU is busy vs idle
#   - When "I/O" is busy vs idle
#   (I/O = all short jobs block for io_time after their CPU burst)
#
# TODO: fill in demonstrate_convoy() to compute CPU utilization
# with 1 long job first vs the long job last.
# ============================================================

def fcfs_simple(jobs: List[Job]) -> int:
    """Run FCFS. Returns total elapsed time."""
    clock = 0
    for job in sorted(jobs, key=lambda j: j.arrival):
        if clock < job.arrival:
            clock = job.arrival
        job.start_time = clock
        clock += job.remaining
        job.remaining = 0
        job.finish_time = clock
    return clock


def exercise2() -> None:
    print("\n" + "=" * 60)
    print("Exercise 2: Convoy Effect")
    print("=" * 60)

    io_time = 10   # each short job does 10 units of I/O after CPU burst

    # Scenario A: long job arrives first (classic convoy)
    long_job = Job("LONG", arrival=0, burst=50)
    short_jobs_a = [Job(f"S{i}", arrival=0, burst=2) for i in range(6)]
    workload_a = [long_job] + short_jobs_a

    # Scenario B: long job arrives last (no convoy)
    long_job_b = Job("LONG", arrival=0, burst=50)
    short_jobs_b = [Job(f"S{i}", arrival=0, burst=2) for i in range(6)]
    workload_b = short_jobs_b + [long_job_b]

    # TODO: demonstrate the convoy effect by:
    #   1. Running FCFS on both workloads (long-first vs short-first)
    #   2. Calculating average turnaround time for each
    #   3. Estimating CPU utilization for each
    #      (CPU busy time / total elapsed time)
    #
    # In the long-first scenario, all short jobs wait 50 units before
    # getting any CPU. The I/O device is idle for those 50 units.
    # After the long job, all 6 short jobs run in 12 units, then all
    # do I/O together. CPU then idles for 10 units during their I/O.
    # In the short-first scenario, short jobs finish in 12 units and
    # overlap their I/O with the long job running on CPU.
    print("  TODO: compare FCFS long-first vs short-first.")
    print(f"  Hint: short jobs do {io_time} units of I/O after their CPU burst.")
    print("  Calculate CPU utilization and avg turnaround for each order.")


# ============================================================
# Exercise 3: Priority Inheritance (fix priority inversion)
# ============================================================
# Three threads share one mutex:
#   HIGH   (priority 0): needs the mutex to do critical work
#   MEDIUM (priority 1): CPU-bound, never touches the mutex
#   LOW    (priority 2): holds the mutex, needs to finish a short task
#
# Without priority inheritance:
#   LOW acquires mutex, HIGH blocks, MEDIUM preempts LOW → HIGH starved.
#
# With priority inheritance:
#   While LOW holds a mutex that HIGH is waiting for, LOW's effective
#   priority is temporarily raised to HIGH's priority. LOW can then
#   preempt MEDIUM, finish quickly, and release the mutex.
#
# TODO: implement the simulation below.
# ============================================================

@dataclass
class Thread:
    id: str
    base_priority: int    # lower = higher priority
    cpu_burst: int        # total CPU work needed
    needs_mutex: bool     # does this thread need the mutex?
    mutex_hold_time: int  # how long it holds the mutex (if needs_mutex)


def simulate_without_inheritance(threads: List[Thread]) -> List[str]:
    """
    Simulate preemptive priority scheduling WITHOUT priority inheritance.
    Returns a log of events showing the priority inversion.
    TODO: implement this.
    """
    log = []
    # Hints:
    # - The thread with the lowest base_priority number runs first
    # - LOW grabs the mutex at time 0
    # - HIGH arrives at time 1 and tries to grab the mutex → blocks
    # - MEDIUM at priority 1 preempts LOW (since LOW is at priority 2)
    # - HIGH is stuck waiting for MEDIUM to finish before LOW can run
    # Your log should capture the irony: HIGH is blocked by MEDIUM.
    log.append("TODO: simulate without priority inheritance")
    return log


def simulate_with_inheritance(threads: List[Thread]) -> List[str]:
    """
    Simulate WITH priority inheritance.
    Returns a log showing the inversion resolved.
    TODO: implement this.
    """
    log = []
    # Hints:
    # - When HIGH blocks on the mutex held by LOW, boost LOW's priority
    #   to HIGH's priority temporarily
    # - Now LOW can preempt MEDIUM and finish holding the mutex
    # - Once LOW releases, restore LOW's priority and wake HIGH
    log.append("TODO: simulate with priority inheritance")
    return log


def exercise3() -> None:
    print("\n" + "=" * 60)
    print("Exercise 3: Priority Inheritance")
    print("=" * 60)

    threads = [
        Thread("HIGH",   base_priority=0, cpu_burst=5,  needs_mutex=True,  mutex_hold_time=0),
        Thread("MEDIUM", base_priority=1, cpu_burst=10, needs_mutex=False, mutex_hold_time=0),
        Thread("LOW",    base_priority=2, cpu_burst=3,  needs_mutex=True,  mutex_hold_time=3),
    ]

    print("\n  Without inheritance:")
    for event in simulate_without_inheritance(threads):
        print(f"    {event}")

    print("\n  With inheritance:")
    for event in simulate_with_inheritance(threads):
        print(f"    {event}")


# ============================================================
# Exercise 4: RR Quantum Tuning
# ============================================================
# Show empirically how quantum size affects:
#   - Average response time (smaller Q = better)
#   - Context switch overhead tax (smaller Q = worse)
#   - Effective throughput (considering overhead)
#
# Model: context_switch_cost = 1 time unit (unrealistically large, but
# makes the math visible without microsecond precision).
#
# TODO: implement rr_with_overhead() and compare Q=1 vs Q=100.
# ============================================================

def rr_with_overhead(jobs: List[Job], quantum: int, switch_cost: int) -> Tuple[float, float, int]:
    """
    Run Round Robin with explicit context switch overhead.
    Each switch burns `switch_cost` time units doing no useful work.
    Returns (avg_wait, avg_turnaround, total_switches).
    TODO: implement this.
    """
    # Hint: base your implementation on round_robin() from scheduler_sim.py,
    # but add `switch_cost` to the clock every time you pick a new job
    # (except the very first job, which has no previous job to switch from).
    raise NotImplementedError("implement rr_with_overhead()")


def exercise4() -> None:
    print("\n" + "=" * 60)
    print("Exercise 4: RR Quantum Tuning (with overhead)")
    print("=" * 60)

    # Workload: mix of short and long jobs
    workload = [
        Job("P1", arrival=0,  burst=20),
        Job("P2", arrival=0,  burst=3),
        Job("P3", arrival=0,  burst=7),
        Job("P4", arrival=2,  burst=1),
        Job("P5", arrival=5,  burst=15),
    ]

    switch_cost = 1  # 1 time unit of overhead per context switch

    print(f"\n  Context switch cost: {switch_cost} time unit(s)")
    print(f"  {'Quantum':>8} {'AvgWait':>10} {'AvgTurn':>10} {'Switches':>10} {'Overhead%':>10}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for q in [1, 2, 4, 8, 20, 100]:
        jobs_copy = copy.deepcopy(workload)
        for j in jobs_copy:
            j.reset()
        # TODO: call rr_with_overhead() and print results
        print(f"  {q:>8}   TODO")

    print("\n  Observation: small Q → many switches → overhead tax eats throughput.")
    print("  Large Q → few switches → degrades to FCFS (poor response time).")
    print("  Sweet spot is typically 10–100ms on real hardware.")


# ============================================================
# Exercise 5: CFS-style Scheduler (vruntime)
# ============================================================
# Linux CFS tracks vruntime per task: the total CPU time the task
# has consumed, scaled by its weight. The scheduler always picks
# the task with the smallest vruntime — stored in a red-black tree.
#
# We simulate CFS with a sorted list (O(n) instead of O(log n),
# but functionally identical).
#
# weight(nice) = 1024 / (1.25 ^ nice)   (simplified)
# vruntime += (actual_time_run) * (1024 / weight)
#
# A task with higher weight (lower nice) advances vruntime more
# slowly, so it gets selected more often — giving it more CPU.
#
# TODO: implement cfs_schedule() below.
# ============================================================

def weight_from_nice(nice: int) -> float:
    """Simplified CFS weight formula. nice=0 → weight=1024."""
    return 1024.0 / (1.25 ** nice)


@dataclass
class CFSTask:
    id: str
    arrival: int
    burst: int
    nice: int = 0          # higher nice = lower priority (more willing to yield)
    remaining: int = field(init=False)
    vruntime: float = field(default=0.0, init=False)
    start_time: Optional[int] = field(default=None, init=False)
    finish_time: Optional[int] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.remaining = self.burst

    @property
    def weight(self) -> float:
        return weight_from_nice(self.nice)

    @property
    def turnaround_time(self) -> int:
        assert self.finish_time is not None
        return self.finish_time - self.arrival


def cfs_schedule_todo(tasks: List[CFSTask], min_granularity: int = 1) -> None:
    """
    TODO: Implement a CFS-style scheduler.
    - At each scheduling point, pick the runnable task with smallest vruntime
    - Run it for `min_granularity` ticks (CFS's minimum scheduling slice)
    - After each slice, update vruntime: vruntime += min_granularity * (1024 / weight)
    - Re-sort (or re-select) the task with minimum vruntime
    - A newly-arriving task starts with vruntime = current minimum vruntime
      (so it does not get all the CPU at once by starting at 0)
    """
    raise NotImplementedError("implement cfs_schedule_todo()")


def exercise5() -> None:
    print("\n" + "=" * 60)
    print("Exercise 5: CFS-style Scheduler")
    print("=" * 60)

    # Two tasks with same burst but different nice values.
    # nice=0 should get roughly twice the CPU of nice=5.
    tasks = [
        CFSTask("NORMAL",  arrival=0, burst=20, nice=0),
        CFSTask("NICE5",   arrival=0, burst=20, nice=5),
        CFSTask("NICE_10", arrival=0, burst=10, nice=-5),  # aggressive
    ]

    # TODO: call cfs_schedule_todo() and print how much CPU each task got,
    # and verify that CPU shares are proportional to their weights.
    print("  TODO: run cfs_schedule_todo() and verify proportional CPU sharing.")
    print(f"  NORMAL  weight: {weight_from_nice(0):.1f}")
    print(f"  NICE5   weight: {weight_from_nice(5):.1f}")
    print(f"  NICE_10 weight: {weight_from_nice(-5):.1f}")
    print("  Expected: NORMAL gets ~2.5x CPU of NICE5; NICE_10 gets ~3x CPU of NORMAL.")


# ============================================================
# Run exercises
# ============================================================

if __name__ == "__main__":
    exercise1()
    exercise2()
    exercise3()
    exercise4()
    exercise5()

    print("\n" + "=" * 60)
    print("  Solutions are below the separator.")
    print("=" * 60)


# ============================================================
# === SOLUTIONS ===
# ============================================================

# -----------------------------------------------------------
# Solution 1: SRTF
# -----------------------------------------------------------

def srtf(jobs: List[Job]) -> None:
    """Shortest Remaining Time First — preemptive SJF."""
    clock = 0
    remaining_jobs = list(jobs)
    total = len(jobs)
    done = 0

    while done < total:
        # All jobs that have arrived and still have work remaining
        ready = [j for j in remaining_jobs if j.arrival <= clock and j.remaining > 0]

        if not ready:
            clock += 1
            continue

        # Pick the job with smallest remaining time; tie-break by id
        job = min(ready, key=lambda j: (j.remaining, j.id))

        if job.start_time is None:
            job.start_time = clock

        # Run for 1 tick (check again each tick for preemption)
        job.remaining -= 1
        clock += 1

        if job.remaining == 0:
            job.finish_time = clock
            done += 1


def solution1() -> None:
    print("\n[Solution 1] SRTF")
    jobs = [
        Job("P1", arrival=0, burst=8),
        Job("P2", arrival=1, burst=4),
        Job("P3", arrival=2, burst=9),
        Job("P4", arrival=3, burst=5),
    ]
    srtf(jobs)
    print_metrics(jobs, "SRTF — solution")
    print("  Note: SRTF is optimal for avg response time among preemptive schedulers.")
    print("  P2 preempts P1 at t=1 (remaining 7 > remaining 4).")
    print("  P4 preempts P1 at t=3+... (remaining after P2 finishes).")


# -----------------------------------------------------------
# Solution 2: Convoy Effect
# -----------------------------------------------------------

def solution2() -> None:
    print("\n[Solution 2] Convoy Effect")
    io_time = 10

    # Scenario A: long job first
    long_a = Job("LONG", arrival=0, burst=50)
    shorts_a = [Job(f"S{i}", arrival=0, burst=2) for i in range(6)]
    workload_a = [long_a] + shorts_a  # FCFS: LONG runs first
    # Run on the actual objects so finish_time gets set
    fcfs_simple(workload_a)
    # CPU is busy for all 50 + 12 = 62 units (no idle gaps in FCFS here)
    # But I/O device idles for the 50 units while LONG runs.
    # After LONG: S0-S5 run for 12 units. Then all 6 do I/O for 10 units.
    # CPU idles for 10 units while they do I/O.
    total_elapsed_a = 50 + 12 + io_time  # 72
    cpu_busy_a = 50 + 12                 # 62 (IO phase: CPU idles)
    # (We model I/O as serialized for simplicity)
    print(f"\n  Scenario A (LONG first — convoy):")
    print(f"    Short jobs avg turnaround: {avg([j.turnaround_time for j in shorts_a]):.1f}")
    print(f"    CPU utilization          : {cpu_busy_a / total_elapsed_a * 100:.1f}%")
    print(f"    I/O device idle for      : 50 time units (starved while LONG runs)")

    # Scenario B: short jobs first (SJF order)
    long_b = Job("LONG", arrival=0, burst=50)
    shorts_b = [Job(f"S{i}", arrival=0, burst=2) for i in range(6)]
    workload_b = shorts_b + [long_b]
    fcfs_simple(workload_b)
    # Shorts finish in 12 units, then do I/O for 10 units.
    # LONG overlaps with their I/O and runs from t=12 onward.
    # LONG finishes at t=62. I/O finishes at t=22. No idle time.
    cpu_busy_b = 62
    total_elapsed_b = 62
    print(f"\n  Scenario B (shorts first — no convoy):")
    print(f"    Short jobs avg turnaround: {avg([j.turnaround_time for j in shorts_b]):.1f}")
    print(f"    CPU utilization          : {cpu_busy_b / total_elapsed_b * 100:.1f}%")
    print(f"    I/O and CPU overlap — both devices stay busy simultaneously.")
    print(f"\n  Lesson: ordering matters even with same total work.")
    print(f"  FCFS with heterogeneous job sizes is a resource utilization disaster.")


# -----------------------------------------------------------
# Solution 3: Priority Inheritance
# -----------------------------------------------------------

def solution3() -> None:
    print("\n[Solution 3] Priority Inheritance")

    # Simulate as a discrete event log, not tick-by-tick
    def without_inheritance() -> List[str]:
        log = []
        # t=0: LOW acquires mutex, starts 3-unit CPU burst
        log.append("t=0 : LOW  acquires mutex, begins CPU work (burst=3)")
        # t=1: HIGH arrives, tries to acquire mutex → blocked
        log.append("t=1 : HIGH arrives, tries mutex → BLOCKED (held by LOW)")
        # t=1: MEDIUM (priority 1) preempts LOW (priority 2), runs for 10 units
        log.append("t=1 : MEDIUM (pri=1) preempts LOW (pri=2) — runs for 10 units")
        log.append("t=1 : LOW is stuck: can't run to release mutex → HIGH starves!")
        log.append("t=11: MEDIUM finishes. LOW resumes.")
        log.append("t=13: LOW finishes, releases mutex.")
        log.append("t=13: HIGH finally gets mutex (waited 12 units!)")
        log.append("==> HIGH (priority 0) was effectively blocked by MEDIUM (priority 1)")
        log.append("==> This is priority INVERSION.")
        return log

    def with_inheritance() -> List[str]:
        log = []
        log.append("t=0 : LOW  acquires mutex, begins CPU work (burst=3)")
        log.append("t=1 : HIGH arrives, tries mutex → BLOCKED (held by LOW)")
        log.append("t=1 : Priority inheritance: LOW's effective priority RAISED to 0 (HIGH's level)")
        log.append("t=1 : LOW (now at pri=0) preempts MEDIUM (pri=1) — runs 2 more ticks")
        log.append("t=3 : LOW finishes, releases mutex, priority RESTORED to 2")
        log.append("t=3 : HIGH unblocked, acquires mutex (waited only 2 units)")
        log.append("t=8 : HIGH finishes.")
        log.append("t=8 : MEDIUM resumes, finishes at t=17.")
        log.append("==> HIGH ran almost immediately. Inversion resolved.")
        return log

    print("\n  Without inheritance:")
    for line in without_inheritance():
        print(f"    {line}")

    print("\n  With inheritance:")
    for line in with_inheritance():
        print(f"    {line}")

    print("\n  Real-world: Mars Pathfinder (1997) hit this bug.")
    print("  Fix was uplinked from Earth: enable priority inheritance on the")
    print("  VxWorks mutex. Spacecraft stopped resetting immediately.")


# -----------------------------------------------------------
# Solution 4: RR Quantum Tuning
# -----------------------------------------------------------

def rr_with_overhead_solution(
    jobs: List[Job], quantum: int, switch_cost: int
) -> Tuple[float, float, int]:
    """Round Robin with explicit context switch overhead."""
    clock = 0
    queue: List[Job] = []
    remaining = sorted(jobs, key=lambda j: (j.arrival, j.id))
    job_idx = 0
    switches = 0
    prev_job: Optional[Job] = None

    def admit() -> None:
        nonlocal job_idx
        while job_idx < len(remaining) and remaining[job_idx].arrival <= clock:
            queue.append(remaining[job_idx])
            job_idx += 1

    admit()

    while queue or job_idx < len(remaining):
        if not queue:
            next_arr = remaining[job_idx].arrival
            clock = next_arr
            admit()
            continue

        job = queue.pop(0)

        # Context switch overhead (not charged on very first job)
        if prev_job is not None and prev_job.id != job.id:
            clock += switch_cost
            switches += 1

        if job.start_time is None:
            job.start_time = clock

        run_for = min(quantum, job.remaining)
        job.remaining -= run_for
        clock += run_for

        admit()

        if job.remaining > 0:
            queue.append(job)
        else:
            job.finish_time = clock

        prev_job = job

    waits = [j.wait_time for j in jobs]
    turns = [j.turnaround_time for j in jobs]
    return avg(waits), avg(turns), switches


def solution4() -> None:
    print("\n[Solution 4] RR Quantum Tuning with context switch overhead")
    workload_template = [
        Job("P1", arrival=0,  burst=20),
        Job("P2", arrival=0,  burst=3),
        Job("P3", arrival=0,  burst=7),
        Job("P4", arrival=2,  burst=1),
        Job("P5", arrival=5,  burst=15),
    ]
    switch_cost = 1
    total_burst = sum(j.burst for j in workload_template)

    print(f"\n  Switch cost: {switch_cost} time unit | Total burst: {total_burst} units")
    print(f"  {'Quantum':>8} {'AvgWait':>10} {'AvgTurn':>10} {'Switches':>10} {'Overhead%':>10}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for q in [1, 2, 4, 8, 20, 100]:
        jobs_copy = copy.deepcopy(workload_template)
        for j in jobs_copy:
            j.reset()
        aw, at, sw = rr_with_overhead_solution(jobs_copy, q, switch_cost)
        overhead_pct = (sw * switch_cost) / (total_burst + sw * switch_cost) * 100
        print(f"  {q:>8} {aw:>10.2f} {at:>10.2f} {sw:>10d} {overhead_pct:>9.1f}%")

    print("\n  Insight: Q=1 causes many switches → overhead explodes.")
    print("  Q=100 → near-FCFS (P1 runs entirely before others get CPU).")
    print("  Q=4–8 balances fairness and overhead for this workload.")


# -----------------------------------------------------------
# Solution 5: CFS-style Scheduler
# -----------------------------------------------------------

def cfs_schedule(tasks: List[CFSTask], min_granularity: int = 1) -> Dict[str, int]:
    """CFS-style scheduler. Returns dict of task_id → cpu_ticks_received."""
    clock = 0
    remaining = list(tasks)
    runqueue: List[CFSTask] = []
    job_idx = 0
    cpu_received: Dict[str, int] = {t.id: 0 for t in tasks}
    total = len(tasks)
    done = 0

    # Admit tasks that arrive at time 0
    while job_idx < len(remaining) and remaining[job_idx].arrival <= clock:
        t = remaining[job_idx]
        # New task starts at current minimum vruntime (not 0) to prevent monopoly
        t.vruntime = min((x.vruntime for x in runqueue), default=0.0)
        runqueue.append(t)
        job_idx += 1

    while done < total:
        if not runqueue:
            clock += 1
            while job_idx < len(remaining) and remaining[job_idx].arrival <= clock:
                t = remaining[job_idx]
                t.vruntime = min((x.vruntime for x in runqueue), default=0.0)
                runqueue.append(t)
                job_idx += 1
            continue

        # Pick task with smallest vruntime (leftmost in CFS red-black tree)
        task = min(runqueue, key=lambda t: t.vruntime)

        if task.start_time is None:
            task.start_time = clock

        run_for = min(min_granularity, task.remaining)
        task.remaining -= run_for
        clock += run_for
        cpu_received[task.id] += run_for

        # Advance vruntime: task with higher weight advances vruntime more slowly
        # vruntime_delta = real_time * (NICE_0_WEIGHT / task.weight)
        NICE_0_WEIGHT = 1024.0
        task.vruntime += run_for * (NICE_0_WEIGHT / task.weight)

        # Admit newly-arrived tasks
        while job_idx < len(remaining) and remaining[job_idx].arrival <= clock:
            new_t = remaining[job_idx]
            new_t.vruntime = min(t.vruntime for t in runqueue)
            runqueue.append(new_t)
            job_idx += 1

        if task.remaining <= 0:
            task.finish_time = clock
            runqueue.remove(task)
            done += 1

    return cpu_received


def solution5() -> None:
    print("\n[Solution 5] CFS-style Scheduler")
    tasks = [
        CFSTask("NORMAL",  arrival=0, burst=20, nice=0),
        CFSTask("NICE5",   arrival=0, burst=20, nice=5),
        CFSTask("NICE_10", arrival=0, burst=10, nice=-5),
    ]

    cpu_received = cfs_schedule(tasks, min_granularity=1)

    total_cpu = sum(cpu_received.values())
    print(f"\n  Total CPU ticks: {total_cpu}")
    print(f"\n  {'Task':<10} {'Nice':>6} {'Weight':>8} {'CPU ticks':>10} {'CPU %':>8} {'Expected %':>12}")
    print(f"  {'-'*10} {'-'*6} {'-'*8} {'-'*10} {'-'*8} {'-'*12}")

    total_weight = sum(weight_from_nice(t.nice) for t in tasks)
    for t in tasks:
        actual_pct = cpu_received[t.id] / total_cpu * 100
        expected_pct = t.weight / total_weight * 100
        print(f"  {t.id:<10} {t.nice:>6} {t.weight:>8.1f} {cpu_received[t.id]:>10} {actual_pct:>7.1f}% {expected_pct:>11.1f}%")

    print("\n  Observation: CPU shares are proportional to task weights.")
    print("  Nice=-5 gets more CPU, nice=+5 gets less — by exact weight ratios.")
    print("  This is 'completely fair': every task advances vruntime at the same rate.")
    print("  CFS uses a red-black tree (O(log n)) to pick the leftmost task efficiently.")


# -----------------------------------------------------------
# Run solutions
# -----------------------------------------------------------

def run_solutions() -> None:
    print("\n\n" + "#" * 60)
    print("#  SOLUTIONS")
    print("#" * 60)
    solution1()
    solution2()
    solution3()
    solution4()
    solution5()


if __name__ == "__main__":
    # Uncomment to run solutions directly:
    run_solutions()
