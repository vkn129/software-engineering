# Day 63: Job Scheduler Mini-Project — Heaps, Priority Queues, and Scheduling Theory

## Why This Exists

Every time your OS decides which process runs next, every time a CI/CD pipeline queues builds, every time a database engine picks which query to execute, a **job scheduler** is making decisions. This project builds five schedulers from scratch, each backed by the data structures we implemented in Week 9: heaps and priority queues.

Job scheduling is where theory meets production:
- **OS process scheduling**: Linux decides among thousands of runnable processes 100+ times per second
- **CI/CD pipelines**: GitHub Actions, Jenkins, and GitLab CI decide build order when runners are limited
- **Database query execution**: PostgreSQL's query planner decides execution order of concurrent queries
- **Cloud task queues**: AWS SQS, Celery, and Sidekiq route millions of tasks to worker pools
- **Real-time systems**: Embedded controllers in aircraft must guarantee deadlines are never missed

The core insight: **every priority-based scheduler is just "extract-min from a heap" on repeat.** The only difference is *what* you use as the key.

## Theory (45 min)

### Scheduling Algorithms and Their Trade-Offs

| Algorithm | Heap Key | Strengths | Weaknesses |
|-----------|----------|-----------|------------|
| FIFO | arrival_time | Simple, fair, predictable | No priority support; short jobs stuck behind long ones |
| Priority | priority value | Urgent jobs first | **Starvation**: low-priority jobs may never run |
| SJF | duration | Minimizes avg wait time (provably optimal) | Requires knowing duration upfront; starvation of long jobs |
| Round Robin | N/A (circular queue) | Time-sliced fairness; good for interactive systems | Context switch overhead; poor for batch workloads |
| EDF | deadline | Optimal for real-time deadline systems | Requires deadline knowledge; cascade failure if overloaded |

### FIFO (First In, First Out)

The simplest scheduler: jobs run in arrival order. Used when fairness matters more than efficiency.

```
Job Queue: [A:10ms] → [B:2ms] → [C:5ms]
Execution: AAAAAAAAAA BB CCCCC
A waits: 0ms, B waits: 10ms, C waits: 12ms
Average wait: 7.3ms
```

Problem: **convoy effect** — short jobs pile up behind a long job.

### Priority Scheduling

Each job has a priority. The heap extracts the highest-priority job (lowest number = highest priority). This is what hospital ERs and network packet schedulers do.

```
Jobs: A(priority=3), B(priority=1), C(priority=2)
Execution: B → C → A  (by priority)
```

**Critical flaw — starvation**: if high-priority jobs keep arriving, low-priority jobs never run. The fix is **priority aging**: gradually boost the priority of waiting jobs.

```
Priority aging: every N time units, decrease priority number by 1
Job D (priority=10) after waiting 50 units at rate 1/5: effective priority = 0
```

### Shortest Job First (SJF)

Provably optimal for minimizing average wait time. Proof sketch: swapping a shorter job to run before a longer one always reduces total wait time (exchange argument).

```
Without SJF: [10ms] [2ms] [5ms] → avg wait = (0 + 10 + 12) / 3 = 7.3ms
With SJF:    [2ms] [5ms] [10ms] → avg wait = (0 + 2 + 7) / 3 = 3.0ms
```

Problem: requires knowing job duration upfront. In practice, schedulers estimate from history.

### Round Robin

Each job gets a fixed **time quantum** (e.g., 10ms). If it doesn't finish, it goes to the back of the queue. This is the foundation of interactive OS scheduling — no single process can hog the CPU.

```
Quantum = 3ms, Jobs: A(8ms), B(4ms), C(2ms)
Time: [AAA][BBB][CC][AAA][B][AA]
        A    B   C   A   B  A
```

Trade-off: smaller quantum = better responsiveness but more context switch overhead.

### Earliest Deadline First (EDF)

For real-time systems where missing a deadline is a failure. The heap key is the deadline. Provably optimal: if any scheduler can meet all deadlines, EDF can too.

```
Jobs: A(deadline=10), B(deadline=5), C(deadline=8)
EDF order: B → C → A
```

If the system is overloaded (total work > available time), EDF degrades badly — it may miss *all* deadlines instead of strategically dropping some.

### The Heap Connection

All priority-based schedulers reduce to the same pattern:

```python
heap = MinHeap()
for job in jobs:
    heap.insert(job, key=scheduling_criterion)

while heap:
    next_job = heap.extract_min()  # O(log n) — this is why heaps matter
    execute(next_job)
```

- Priority scheduler: key = priority value
- SJF: key = duration
- EDF: key = deadline
- Even FIFO is a degenerate case: key = arrival_time

Without a heap, finding the next job is O(n). With a heap, it's O(log n). For an OS scheduling among 10,000 processes, that's the difference between 10,000 comparisons and 14.

### Preemption

Non-preemptive: once a job starts, it runs to completion.
Preemptive: a running job can be **interrupted** when a higher-priority job arrives.

```
Non-preemptive SJF:
  Time 0: Job A (8ms) starts
  Time 3: Job B (2ms) arrives — waits until A finishes
  Timeline: [AAAAAAAA][BB]

Preemptive SJF (= Shortest Remaining Time First):
  Time 0: Job A (8ms) starts
  Time 3: Job B (2ms) arrives — A interrupted (5ms remaining)
  Timeline: [AAA][BB][AAAAA]
  B finishes sooner, A finishes at same total time
```

Preemption requires re-inserting the interrupted job with its remaining time.

### Real Systems

- **Linux CFS (Completely Fair Scheduler)**: Uses a red-black tree keyed on "virtual runtime." Processes that have run less get priority. O(log n) selection among all runnable processes.
- **Kubernetes scheduler**: Scores nodes by resource fit, affinity rules, and priorities. Multi-dimensional scheduling problem.
- **AWS SQS**: FIFO queues guarantee ordering; standard queues prioritize throughput over order.
- **Database query schedulers**: PostgreSQL uses cost-based priority. Long analytical queries yield to short transactional queries.

## Complexity

| Operation | Time | Why |
|-----------|------|-----|
| Add job to heap-based scheduler | O(log n) | Heap insert |
| Get next job (priority/SJF/EDF) | O(log n) | Heap extract-min |
| Add job to FIFO | O(1) | Queue append |
| Get next job (FIFO) | O(1) | Queue pop |
| Add job to Round Robin | O(1) | Queue append |
| Round Robin quantum tick | O(1) | Dequeue + re-enqueue |
| Priority aging (per tick) | O(n) | Must update all waiting jobs |

## Checkpoint Questions

1. Why is SJF provably optimal for average wait time? Sketch the exchange argument: if job A is shorter than job B, what happens to total wait time when you swap their order?
2. Priority aging solves starvation, but what new problem does it introduce? (Hint: what happens when all jobs reach priority 0?)
3. Round Robin with quantum = infinity degenerates to which other scheduler? What about quantum = 1?
4. Why does EDF fail catastrophically under overload while priority scheduling degrades more gracefully?
5. Linux CFS uses a red-black tree instead of a binary heap. What property of red-black trees makes them better for this use case? (Hint: think about what CFS needs besides extract-min.)
6. In a preemptive SJF scheduler, a newly arriving 1ms job always preempts a running 100ms job with 99ms remaining. Is this always the right call? When might you NOT want to preempt?
