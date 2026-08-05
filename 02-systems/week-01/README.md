# Week 1: Process Fundamentals

Goal: understand what a process **is** at the kernel level — not as a Docker
container or a `python script.py`, but as a `task_struct` with a PID, a
virtual address space, file descriptors, and signal handlers.

## Day Plan

| Day | Topic | File | What you'll build |
|-----|-------|------|-------------------|
| 1 | What is a process | `process_basics.py` | `fork()` demo, PID/PPID inspection, syscall trace |
| 2 | Threads vs processes | `threads_vs_procs.py` | Side-by-side benchmark, GIL contention demo |
| 3 | Scheduling | `scheduler_sim.py` | Round-robin, priority, MLFQ, CFS-lite simulators |
| 4 | Context switches | `context_switch.py` | Microbenchmark — measure CS cost in microseconds |
| 5 | Inter-process communication | `ipc.py` | Pipes, signals, shared memory, message queues |
| 6 | **Capstone**: process supervisor | `supervisor.py` | supervisord-lite with restart policies + signals |

## Why This Week First

Every other systems topic — threading, memory, I/O, networking — sits inside
a process. Get the process model wrong and nothing else makes sense. By Friday
you should be able to draw the lifecycle from `fork()` through `exec()` through
`wait()` and explain why zombies exist.

## Failure Modes You'll See

- **Zombie processes** — child exited, parent didn't `wait()`. PID table fills, eventually `fork: Resource temporarily unavailable`.
- **Fork bombs** — `:(){ :|:& };:` exhausts the PID space. `ulimit -u` is the fence.
- **Orphan processes** — parent died first; child reparented to PID 1 (init/systemd/launchd).
- **Priority inversion** — low-priority task holds lock a high-priority task needs (Mars Pathfinder 1997).
- **Scheduler thrashing** — load average > #cores; context switches dominate useful work.

## Real Systems

- Linux: `task_struct` in `include/linux/sched.h`, CFS in `kernel/sched/fair.c`
- macOS XNU: Mach tasks + BSD processes layered (`task_t` vs `proc_t`)
- systemd / launchd / supervisord — production process supervisors
