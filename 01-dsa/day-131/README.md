# Day 131: Job Scheduling — EDF, Weighted, and the DP Crossover

## The Family of Scheduling Problems

"Schedule N jobs on M machines to optimize X" is a vast problem family
where the right algorithm depends entirely on the constraints:

| Problem | Optimum | Algorithm |
|---------|---------|-----------|
| Minimize total wait time, single machine | Greedy: SJF (shortest job first) | O(n log n) |
| Maximize jobs done by their deadlines | Greedy: deadline + Union-Find | O(n α(n)) |
| Earliest Deadline First (real-time) | Greedy: EDF (with preemption) | O(n log n) |
| Weighted job scheduling (max profit, no overlap) | DP | O(n log n) |
| Multi-machine makespan minimization | NP-hard; greedy LPT 4/3-approx | depends |

Today: **EDF**, **deadline-greedy**, and the **weighted DP variant**.

## Earliest Deadline First (EDF)

### Setup
- Single processor. Jobs arrive over time.
- Each job has a **deadline** and a **processing time**.
- A schedule is **feasible** if every job finishes by its deadline.
- With **preemption** allowed (interrupt + resume).

### EDF rule
> At every moment, run the job with the **earliest deadline** among those
> currently available.

### Optimality (Liu & Layland, 1973)
EDF is **optimal** for single-processor preemptive scheduling: if any
feasible schedule exists, EDF finds one.

### Proof (exchange argument)
Suppose schedule `O` is feasible but at time `t` it runs job `j` while
job `i` is available and has an earlier deadline `d_i < d_j`. Swap:
run `i` for one time unit at `t`, push `j`'s unit to a later slot before
`d_j`. The swap is feasible (`d_i < d_j` and `j`'s slot existed before
`d_j` either way). After finitely many swaps `O` becomes EDF. ∎

### Where EDF fails
- **Multi-processor non-preemptive**: NP-hard. EDF is no longer optimal.
- **Overload**: if no feasible schedule exists, EDF may cause cascading
  deadline misses ("domino effect"). Rate-monotonic + admission control
  is preferred in such hard real-time systems.

## Deadline-Greedy (Unit Jobs, Maximize Count)

### Setup
- `n` unit-length jobs. Job `i` has deadline `d_i`.
- Goal: schedule the **maximum number** that meet their deadlines.

### Greedy algorithm
```
sort jobs by deadline ascending
slots = empty time slots {0, 1, ..., n-1}
for each job in order:
    if there's a free slot s with s <= deadline - 1:
        schedule job at slot s (use the largest such s)
        mark s used
```

The "largest such s" rule is implemented efficiently with **Union-Find**:
each slot points to the next free slot ≤ itself.

Or, equivalently with a **min-heap** of currently scheduled job
processing times:
```
for job in sorted-by-deadline:
    push job onto heap
    if heap size > deadline: pop the longest job in heap (drop it)
```

The heap variant generalizes to **weighted** (max-profit) when all jobs
have unit length: pop the **least profitable** job. (See `LC 1834`.)

## Weighted Job Scheduling — DP, not Greedy

### Setup
- Each job has `(start, finish, profit)`.
- Jobs may overlap. Pick a non-overlapping subset to **maximize total profit**.

### Why greedy fails
"Sort by profit desc, take if compatible" can be tricked by a few medium-
profit jobs that together exceed a single high-profit one. Example:

```
Job A: (0, 10, 100)
Job B: (0, 5,  60)
Job C: (5, 10, 60)
```

Greedy by profit picks A (100). Optimal picks B+C (120).

"Sort by finish, take if compatible" fails too — you might lock yourself
out of higher-profit choices.

### DP solution
Sort by finish time. Define `dp[i]` = max profit using first `i` jobs.

```
dp[0] = 0
for i in 1..n:
    p = profit[i] + dp[latest j < i where finish[j] <= start[i]]
    dp[i] = max(dp[i-1], p)
```

Find `j` by binary search → `O(n log n)`.

### Why this is DP, not greedy
The choice "include job i?" requires knowing the optimal solution of the
**remaining** subproblem (jobs ending before `start[i]`). That's optimal
substructure, but **without** the greedy choice property — there's no
locally optimal choice that doesn't require looking back at all prior
subproblems.

## The Decision: Greedy vs DP for Scheduling

Ask:
1. **Does the value of a choice depend on later choices?**
   - No: greedy.
   - Yes: DP.
2. **Is there a sort order that decouples choices?**
   - Yes (deadline, finish time, density): greedy or DP works trivially.
   - No: DP with state.
3. **Are weights involved?**
   - Unit weights / count-only: usually greedy.
   - General weights: usually DP (unless matroid structure).

## A Worked EDF Trace

Jobs (release_time, processing, deadline):
- J1: (0, 2, 5)
- J2: (1, 3, 4)
- J3: (3, 1, 6)

Timeline (preemptive EDF, pick earliest deadline among available):
```
t=0: only J1 available (d=5). Run J1.        elapsed: J1=1
t=1: J2 arrives (d=4). EDF picks J2.         elapsed: J1=1, J2=1
t=2: J2 still earliest deadline. Run J2.     elapsed: J1=1, J2=2
t=3: J3 arrives (d=6). Deadlines: J1=5, J2=4, J3=6. Pick J2.
                                              elapsed: J1=1, J2=3 ✓
t=4: J1(d=5) vs J3(d=6). Pick J1.            elapsed: J1=2 ✓
t=5: only J3 remains.                         elapsed: J3=1 ✓
All finish by deadlines.
```

## Real-World Use

- **Linux SCHED_DEADLINE** (CONFIG_RT_DEADLINE): runs EDF for real-time
  tasks alongside CFS.
- **Apache Mesos / Kubernetes**: weighted scheduling with bin-packing
  approximations.
- **Industrial scheduling (job-shop)**: large LP/IP solvers, not greedy.
- **Compiler instruction scheduling**: list scheduling (greedy by
  priority) for register pressure + latency.

## Failure Modes

1. **EDF without admission control**: overload causes domino effect.
2. **Greedy on weighted intervals**: produces suboptimal profit.
3. **Mistaking unit-job greedy for general weighted**: identical-looking
   code gives wrong answers when weights differ.
4. **Tie-breaking in EDF**: matters for deterministic systems but not for
   feasibility. Liu-Layland proof is independent of tie-break choice.

## Checkpoint

1. State the EDF rule. Why is it optimal for single-processor preemptive?
2. Give a 3-job instance where deadline-greedy (max count) succeeds but
   sorting by processing time fails.
3. Why does the weighted job scheduling problem require DP rather than
   greedy? Give a 3-job counterexample.
4. In the weighted DP, why must you sort by finish time, not start time?
5. Describe how Union-Find speeds up the unit-job deadline greedy.
6. Name a real OS that uses EDF and a real workload where you'd reach for
   list scheduling.
