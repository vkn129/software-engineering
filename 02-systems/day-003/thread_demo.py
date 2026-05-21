"""
thread_demo.py — Threads: race conditions, GIL effects, I/O vs CPU

Demonstrates:
  1. Race condition on a shared counter (no lock)
  2. Fixed counter with threading.Lock
  3. GIL effect: CPU-bound work with N threads is NOT faster than 1
  4. GIL release: I/O-bound work with N threads IS faster
  5. Comparison table

Run:  python thread_demo.py
"""

import threading
import time
import sys


# ─────────────────────────────────────────────────────────────────────────────
# PART 1: The Race Condition
# ─────────────────────────────────────────────────────────────────────────────
# counter += 1  compiles to three bytecode instructions:
#   LOAD_FAST counter      ← read current value into the eval stack
#   LOAD_CONST 1
#   BINARY_ADD             ← compute result
#   STORE_FAST counter     ← write result back
#
# Between LOAD and STORE the OS can preempt this thread and let another thread
# run its own LOAD. Both load the same old value, both add 1, both store.
# One increment is silently lost.
# With 100 threads × 100_000 increments we expect 10_000_000; we will see less.

def race_demo(n_threads: int = 100, increments_per_thread: int = 100_000) -> int:
    # Use a list so threads share a mutable container — clearer than nonlocal.
    # The race: LOAD counter[0], ADD 1, STORE counter[0].
    # Between LOAD and STORE another thread can do the same — one write is lost.
    # We use sys.setswitchinterval(0) to force the GIL to yield as often as
    # possible, making the race observable. (Default is 5ms — sometimes the
    # entire inner loop finishes before a switch, masking the race.)
    counter = [0]
    original_interval = sys.getswitchinterval()
    sys.setswitchinterval(1e-9)  # near-zero: switch after every bytecode check

    def worker():
        for _ in range(increments_per_thread):
            counter[0] += 1  # ← NOT thread-safe: LOAD, ADD, STORE can interleave

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    sys.setswitchinterval(original_interval)  # restore
    return counter[0]


# ─────────────────────────────────────────────────────────────────────────────
# PART 2: Lock-protected Counter
# ─────────────────────────────────────────────────────────────────────────────
# threading.Lock() is a mutual-exclusion lock (mutex).
# acquire() blocks until the lock is free; release() frees it.
# With "with lock:" we guarantee release even if an exception occurs.
#
# The lock makes the read–modify–write atomic from the perspective of other
# threads: only one thread executes the body at a time, so no interleaving
# can corrupt the counter. Cost: threads spend most of their time waiting
# on the lock rather than doing work — which is why this is slower than
# single-threaded code for a pure-CPU task.

def locked_demo(n_threads: int = 100, increments_per_thread: int = 100_000) -> int:
    counter = 0
    lock = threading.Lock()

    def worker():
        nonlocal counter
        for _ in range(increments_per_thread):
            with lock:
                counter += 1  # ← now atomic w.r.t. other threads

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return counter


# ─────────────────────────────────────────────────────────────────────────────
# PART 3: GIL Effect — CPU-Bound Work
# ─────────────────────────────────────────────────────────────────────────────
# The GIL ensures only one thread executes Python bytecode at a time.
# For CPU-bound work (no I/O, no C extension releasing the GIL) N threads
# produce the same throughput as 1 thread — but with added context-switch
# overhead. More threads = MORE total time, not less.
#
# We hash a block of bytes repeatedly. hashlib's hash functions are pure Python
# digest computation — the GIL is held throughout. (For large data, hashlib's
# C implementation CAN release the GIL, so we keep blocks small to stay in
# Python bytecode land as much as possible.)

def cpu_bound_task(iterations: int) -> None:
    """Deliberately inefficient pure-Python CPU work."""
    x = 0
    for i in range(iterations):
        # Pure Python arithmetic — GIL held the entire time
        x = (x * 1_000_003 + i) % (2**32)


def measure_cpu_bound(n_threads: int, iterations_per_thread: int = 2_000_000) -> float:
    """Return wall-clock seconds for n_threads doing CPU work."""
    threads = [
        threading.Thread(target=cpu_bound_task, args=(iterations_per_thread,))
        for _ in range(n_threads)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start


# ─────────────────────────────────────────────────────────────────────────────
# PART 4: GIL Release — I/O-Bound Work
# ─────────────────────────────────────────────────────────────────────────────
# During blocking I/O (socket read/write, file read, time.sleep), CPython
# releases the GIL so other threads can run Python bytecode. This is why
# threading genuinely helps for I/O-bound programs: while one thread waits
# for the network, other threads can process their own data.
#
# We simulate I/O with time.sleep(). In production this is a network call,
# a disk read, or a database query — the principle is identical.

def io_bound_task(sleep_seconds: float) -> None:
    """Simulate blocking I/O (network request, disk read, etc.)"""
    # time.sleep releases the GIL: other threads run while we wait
    time.sleep(sleep_seconds)


def measure_io_bound(n_threads: int, sleep_per_thread: float = 0.1) -> float:
    """Return wall-clock seconds for n_threads each sleeping sleep_per_thread."""
    threads = [
        threading.Thread(target=io_bound_task, args=(sleep_per_thread,))
        for _ in range(n_threads)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("THREAD DEMO: Race Conditions, Locks, and the GIL")
    print("=" * 65)

    N_THREADS = 100
    INCREMENTS = 100_000
    EXPECTED = N_THREADS * INCREMENTS

    # ── Part 1: Race Condition ────────────────────────────────────────────
    print(f"\n[1] RACE CONDITION  ({N_THREADS} threads × {INCREMENTS:,} increments)")
    print(f"    Expected: {EXPECTED:,}")

    results = []
    for run in range(3):
        result = race_demo(N_THREADS, INCREMENTS)
        results.append(result)
        lost = EXPECTED - result
        pct = lost / EXPECTED * 100
        print(f"    Run {run + 1}: {result:,}  (lost {lost:,} increments = {pct:.1f}% loss)")

    print(f"\n    Note: results differ between runs (non-deterministic)")
    print(f"    Note: result is always LESS than expected (never more)")
    print(f"    Why: STORE from one thread overwrites STORE from another,")
    print(f"    so some increments are silently dropped — never doubled.")

    # ── Part 2: Lock Fix ─────────────────────────────────────────────────
    print(f"\n[2] LOCK-PROTECTED COUNTER  ({N_THREADS} threads × {INCREMENTS:,} increments)")
    result = locked_demo(N_THREADS, INCREMENTS // 10)  # fewer iterations for speed
    locked_expected = N_THREADS * (INCREMENTS // 10)
    print(f"    Result:   {result:,}")
    print(f"    Expected: {locked_expected:,}")
    print(f"    Correct:  {result == locked_expected}")
    print(f"    Cost:     each increment now serializes all {N_THREADS} threads")

    # ── Part 3: CPU-Bound GIL Effect ────────────────────────────────────
    print(f"\n[3] GIL EFFECT — CPU-BOUND WORK")
    print(f"    (pure Python arithmetic, GIL held throughout)")
    print()

    cpu_configs = [1, 2, 4]
    cpu_times = {}
    for n in cpu_configs:
        elapsed = measure_cpu_bound(n)
        cpu_times[n] = elapsed
        # Total work is the same regardless of thread count (GIL serializes it)
        # so time should stay flat or increase with more threads
        print(f"    {n:2d} thread(s): {elapsed:.2f}s")

    baseline = cpu_times[1]
    print()
    print(f"    Speedup vs 1 thread:")
    for n in cpu_configs:
        speedup = baseline / cpu_times[n]
        verdict = "(~expected: GIL prevents parallelism)" if n == 1 else \
                  "(slower! GIL + context-switch overhead)" if speedup < 0.95 else \
                  "(about the same — GIL serializes CPU work)"
        print(f"      {n:2d} threads: {speedup:.2f}x  {verdict}")

    # ── Part 4: I/O-Bound Threading Wins ─────────────────────────────────
    print(f"\n[4] GIL RELEASE — I/O-BOUND WORK")
    SLEEP = 0.2   # simulate 200ms I/O per task
    io_configs = [1, 4, 8, 16]
    io_times = {}

    print(f"    Each thread sleeps {SLEEP}s (simulating blocking I/O)")
    print(f"    Serial expected: n_threads × {SLEEP}s")
    print()

    for n in io_configs:
        elapsed = measure_io_bound(n, SLEEP)
        io_times[n] = elapsed
        serial_time = n * SLEEP
        speedup = serial_time / elapsed
        print(f"    {n:2d} thread(s): {elapsed:.2f}s  "
              f"(serial would be {serial_time:.1f}s → {speedup:.1f}x speedup)")

    # ── Summary Table ─────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print()
    print(f"  {'Scenario':<40} {'Threads help?'}")
    print(f"  {'-'*40} {'-'*20}")
    print(f"  {'Shared counter, no lock':<40} NO  — race condition")
    print(f"  {'Shared counter, with Lock':<40} YES — correct, but slower")
    print(f"  {'CPU-bound Python (pure arithmetic)':<40} NO  — GIL serializes")
    print(f"  {'I/O-bound (sleep/network/disk)':<40} YES — GIL released during I/O")
    print()
    print("  Rule of thumb:")
    print("    Python threads → use for I/O-bound work")
    print("    Python threads → avoid for CPU-bound work (use multiprocessing)")
    print("    Always protect shared mutable state with locks")
    print()


if __name__ == "__main__":
    main()
