"""
Day 155: Parallel Prefix Sum — Hillis-Steele and Blelloch Scans

Two foundational parallel-scan algorithms with different work/depth profiles.
GIL note: Python threads serialize on pure-Python bytecode, so we measure
logical operation counts as well as wall-clock time.
"""

import threading
import time
import random
from typing import Callable, List


# ---------------------------------------------------------------------------
# 1. Sequential baseline
# ---------------------------------------------------------------------------

def sequential_scan_inclusive(a: List[int]) -> List[int]:
    """O(n) work, O(n) depth — the single-threaded loop."""
    out = a[:]
    for i in range(1, len(out)):
        out[i] += out[i - 1]
    return out


def sequential_scan_exclusive(a: List[int]) -> List[int]:
    """out[0] = 0, out[i] = a[0] + ... + a[i-1]."""
    out = [0] * len(a)
    for i in range(1, len(a)):
        out[i] = out[i - 1] + a[i - 1]
    return out


# ---------------------------------------------------------------------------
# 2. Hillis-Steele — step-efficient, O(n log n) work, O(log n) depth
# ---------------------------------------------------------------------------

def hillis_steele_scan(a: List[int]) -> List[int]:
    """
    Inclusive scan via log n sync rounds.
    Each round, in parallel: a[i] += a[i - offset] if i >= offset, doubling
    the offset each round.

    We simulate the "parallel for" with a snapshot of the previous round —
    the actual parallelism is logical, not threaded (GIL would kill it).
    """
    n = len(a)
    cur = a[:]
    offset = 1
    rounds = 0
    while offset < n:
        # Snapshot prevents read-after-write hazards across "parallel" lanes
        prev = cur[:]
        for i in range(n):
            if i >= offset:
                cur[i] = prev[i] + prev[i - offset]
        offset *= 2
        rounds += 1
    return cur, rounds


def hillis_steele_scan_threaded(a: List[int], num_workers: int = 4):
    """
    Same algorithm, but each round is split across worker threads.
    Demonstrates GIL serialization on pure-Python work.
    """
    n = len(a)
    cur = a[:]
    offset = 1
    rounds = 0

    def worker(prev, start, end, off):
        for i in range(start, end):
            if i >= off:
                cur[i] = prev[i] + prev[i - off]

    while offset < n:
        prev = cur[:]
        threads = []
        chunk = (n + num_workers - 1) // num_workers
        for w in range(num_workers):
            s = w * chunk
            e = min(n, s + chunk)
            if s >= e:
                break
            t = threading.Thread(target=worker, args=(prev, s, e, offset))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        offset *= 2
        rounds += 1
    return cur, rounds


# ---------------------------------------------------------------------------
# 3. Blelloch — work-efficient, O(n) work, O(log n) depth
# ---------------------------------------------------------------------------

def blelloch_scan(a: List[int], op: Callable[[int, int], int] = lambda x, y: x + y,
                  identity: int = 0):
    """
    Exclusive scan over an associative operator `op` with `identity`.
    Two passes:
      - up-sweep: build segment sums (reduce tree)
      - down-sweep: distribute partial sums
    Requires len(a) to be a power of two — we pad and trim.
    """
    n = len(a)
    # Pad to next power of two
    size = 1
    while size < n:
        size *= 2
    buf = a[:] + [identity] * (size - n)

    # Up-sweep
    d = 1
    while d < size:
        for i in range(0, size, 2 * d):
            buf[i + 2 * d - 1] = op(buf[i + d - 1], buf[i + 2 * d - 1])
        d *= 2

    # Set root to identity for exclusive scan
    buf[size - 1] = identity

    # Down-sweep
    d = size // 2
    while d >= 1:
        for i in range(0, size, 2 * d):
            t = buf[i + d - 1]
            buf[i + d - 1] = buf[i + 2 * d - 1]
            buf[i + 2 * d - 1] = op(t, buf[i + 2 * d - 1])
        d //= 2

    return buf[:n]


def blelloch_scan_threaded(a: List[int], num_workers: int = 4) -> List[int]:
    """Same as blelloch_scan but parallelizes each level across threads."""
    n = len(a)
    size = 1
    while size < n:
        size *= 2
    buf = a[:] + [0] * (size - n)

    def parallel_for(tasks, fn):
        threads = []
        chunk = max(1, (len(tasks) + num_workers - 1) // num_workers)
        for w in range(num_workers):
            s = w * chunk
            e = min(len(tasks), s + chunk)
            if s >= e:
                break

            def run(s=s, e=e):
                for k in range(s, e):
                    fn(tasks[k])
            t = threading.Thread(target=run)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    # Up-sweep
    d = 1
    while d < size:
        indices = list(range(0, size, 2 * d))
        parallel_for(indices, lambda i, d=d: buf.__setitem__(
            i + 2 * d - 1, buf[i + d - 1] + buf[i + 2 * d - 1]))
        d *= 2

    buf[size - 1] = 0

    # Down-sweep
    d = size // 2
    while d >= 1:
        indices = list(range(0, size, 2 * d))

        def step(i, d=d):
            t = buf[i + d - 1]
            buf[i + d - 1] = buf[i + 2 * d - 1]
            buf[i + 2 * d - 1] = t + buf[i + 2 * d - 1]
        parallel_for(indices, step)
        d //= 2

    return buf[:n]


# ---------------------------------------------------------------------------
# 4. Monoid scan — same skeleton, any associative op
# ---------------------------------------------------------------------------

def monoid_scan_max(a: List[int]) -> List[int]:
    """Exclusive scan with max; identity is -inf."""
    NEG_INF = float("-inf")
    res = blelloch_scan(a, op=max, identity=NEG_INF)
    return res


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_correctness():
    print("=" * 60)
    print("DEMO 1: Correctness — all four implementations agree")
    print("=" * 60)
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"\ninput:                {a}")
    seq_inc = sequential_scan_inclusive(a)
    seq_exc = sequential_scan_exclusive(a)
    hs, rounds = hillis_steele_scan(a)
    bl = blelloch_scan(a)
    print(f"sequential inclusive: {seq_inc}")
    print(f"sequential exclusive: {seq_exc}")
    print(f"Hillis-Steele incl.:  {hs}  ({rounds} sync rounds)")
    print(f"Blelloch exclusive:   {bl}")
    assert hs == seq_inc
    assert bl == seq_exc


def demo_work_vs_depth():
    print("\n" + "=" * 60)
    print("DEMO 2: Work vs Depth")
    print("=" * 60)
    for n in [8, 64, 1024, 8192]:
        import math
        depth = math.ceil(math.log2(n))
        hs_work = n * depth
        bl_work = 2 * n - 2  # exact for power of two
        print(f"  n={n:6d}: depth={depth:2d}  HS work={hs_work:8d}  Blelloch work={bl_work:6d}")
    print("  → Blelloch matches sequential O(n); Hillis-Steele pays an extra log n factor")


def demo_threaded_timing():
    print("\n" + "=" * 60)
    print("DEMO 3: Threaded timing (expect GIL anti-speedup)")
    print("=" * 60)
    random.seed(0)
    n = 1 << 14  # 16384
    a = [random.randint(0, 100) for _ in range(n)]

    t0 = time.perf_counter()
    sequential_scan_inclusive(a)
    t_seq = time.perf_counter() - t0

    t0 = time.perf_counter()
    hillis_steele_scan(a)
    t_hs = time.perf_counter() - t0

    t0 = time.perf_counter()
    hillis_steele_scan_threaded(a, num_workers=4)
    t_hs_par = time.perf_counter() - t0

    t0 = time.perf_counter()
    blelloch_scan(a)
    t_bl = time.perf_counter() - t0

    t0 = time.perf_counter()
    blelloch_scan_threaded(a, num_workers=4)
    t_bl_par = time.perf_counter() - t0

    print(f"\nn={n}")
    print(f"  sequential:           {t_seq:.4f}s")
    print(f"  Hillis-Steele 1T:     {t_hs:.4f}s")
    print(f"  Hillis-Steele 4T:     {t_hs_par:.4f}s   (speedup {t_hs / t_hs_par:.2f}x)")
    print(f"  Blelloch 1T:          {t_bl:.4f}s")
    print(f"  Blelloch 4T:          {t_bl_par:.4f}s   (speedup {t_bl / t_bl_par:.2f}x)")
    print("  → GIL serializes pure-Python; threads add overhead. Same algorithm")
    print("    on a GPU would scale linearly with cores until memory-bound.")


def demo_monoid_max():
    print("\n" + "=" * 60)
    print("DEMO 4: Monoid scan with max")
    print("=" * 60)
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"input:                   {a}")
    print(f"exclusive max-scan:      {monoid_scan_max(a)}")
    print("  (each position = max of all strictly-prior elements)")


if __name__ == "__main__":
    demo_correctness()
    demo_work_vs_depth()
    demo_threaded_timing()
    demo_monoid_max()
