# Week 2: Threading & Synchronization

Goal: understand why shared mutable state is the hardest problem in computing,
and learn the primitives that make it survivable.

## Day Plan

| Day | Topic | File | What you'll build |
|-----|-------|------|-------------------|
| 1 | Race conditions & atomicity | `races.py` | Demonstrate lost updates, torn reads |
| 2 | Mutexes & spinlocks | `mutex_spinlock.py` | Build a spinlock with `threading.Lock` and CAS |
| 3 | Semaphores & condition variables | `sem_condvar.py` | Producer/consumer with `Condition` |
| 4 | Deadlock — detect, prevent, recover | `deadlock.py` | Coffman conditions, lock ordering, banker's algorithm |
| 5 | Lock-free data structures | `lockfree.py` | Treiber stack, CAS loops, ABA problem |
| 6 | **Capstone**: bounded-buffer | `bounded_buffer.py` | Thread-safe ring buffer, benchmarked vs `queue.Queue` |

## Failure Modes
- Lost updates, torn reads/writes, deadlock, livelock, starvation, priority inversion, ABA in lock-free code.

## Real Systems
- Linux futex, Java `synchronized`, Go channels, Rust `Send`/`Sync`, Java `j.u.c.atomic`.
