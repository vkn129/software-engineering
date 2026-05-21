"""
practice.py — Day 10: System Calls

Five exercises with solutions.  Read the TODO, attempt it, then scroll to
the SOLUTION block below each one.  Run with:

    python practice.py

Each exercise runs automatically and prints results so you can compare
your mental model against measured reality.
"""

import os
import sys
import time

SEPARATOR = "-" * 60


# ===========================================================================
# Exercise 1: Measure syscall cost with os.times()
#
# os.times() returns (utime, stime, cutime, cstime, elapsed).
# utime = user CPU seconds, stime = kernel CPU seconds for this process.
#
# TODO: Write a loop that makes 100,000 calls to os.getpid() (a cheap
# syscall) and 100,000 calls to sum(range(1000)) (CPU-bound, no syscalls).
# Use os.times() before and after each block. What fraction of total
# CPU time is spent in kernel mode for each workload?
# ===========================================================================

def exercise_1_ostimes():
    print(f"\n{SEPARATOR}")
    print("Exercise 1: os.times() — user vs kernel time split")
    print(SEPARATOR)

    # --- TODO: try it yourself first ---
    # t_before = os.times()
    # for _ in range(100_000):
    #     os.getpid()
    # t_after = os.times()
    # user_delta   = t_after[0] - t_before[0]
    # kernel_delta = t_after[1] - t_before[1]
    # ...

    # SOLUTION ---------------------------------------------------------------
    N = 100_000

    # Block A: syscall-heavy (getpid)
    t0 = os.times()
    for _ in range(N):
        os.getpid()
    t1 = os.times()
    user_a   = t1[0] - t0[0]
    kernel_a = t1[1] - t0[1]
    total_a  = user_a + kernel_a
    kernel_pct_a = (kernel_a / total_a * 100) if total_a > 0 else 0

    # Block B: CPU-bound (pure math)
    t0 = os.times()
    for _ in range(N):
        sum(range(100))
    t1 = os.times()
    user_b   = t1[0] - t0[0]
    kernel_b = t1[1] - t0[1]
    total_b  = user_b + kernel_b
    kernel_pct_b = (kernel_b / total_b * 100) if total_b > 0 else 0

    print(f"  getpid x{N:,}:       user={user_a:.3f}s  kernel={kernel_a:.3f}s  => {kernel_pct_a:.0f}% kernel")
    print(f"  sum(range) x{N:,}: user={user_b:.3f}s  kernel={kernel_b:.3f}s  => {kernel_pct_b:.0f}% kernel")
    print()
    print("  Insight: getpid() should push non-trivial time into kernel (stime).")
    print("  sum(range) is almost entirely user-space math — kernel% ≈ 0.")
    print("  os.times() granularity is low (10ms clock ticks); visible with N=1M.")


# ===========================================================================
# Exercise 2: print() is a hidden syscall machine
#
# TODO: Time printing 10,000 lines to stdout in two ways:
#   (a) print(str(i)) inside a loop (one write() syscall per line)
#   (b) build a single large string, then one print() at the end
# Measure with time.perf_counter_ns(). How much faster is (b)?
#
# Then explain: why does this matter for logging libraries?
# ===========================================================================

def exercise_2_print_cost():
    print(f"\n{SEPARATOR}")
    print("Exercise 2: print() overhead — each call can be a syscall")
    print(SEPARATOR)

    N = 5_000
    devnull = open(os.devnull, "w")

    # SOLUTION ---------------------------------------------------------------

    # (a) One print per line → one write() per call
    t0 = time.perf_counter_ns()
    for i in range(N):
        print(i, file=devnull)
    t1 = time.perf_counter_ns()
    time_a_ms = (t1 - t0) / 1e6

    # (b) Build string, single print
    t0 = time.perf_counter_ns()
    out = "\n".join(str(i) for i in range(N))
    print(out, file=devnull)
    t1 = time.perf_counter_ns()
    time_b_ms = (t1 - t0) / 1e6

    devnull.close()

    speedup = time_a_ms / time_b_ms if time_b_ms > 0 else float("inf")
    print(f"  {N:,} individual print()s:    {time_a_ms:.2f} ms")
    print(f"  one joined print():         {time_b_ms:.2f} ms")
    print(f"  Speedup (batch):            {speedup:.1f}x")
    print()
    print("  Insight: Python's print() is not buffered by default when stdout")
    print("  is a terminal (line-buffered) or a pipe (block-buffered at 8KB).")
    print("  Each print() to a terminal triggers a write() syscall.")
    print("  Logging libraries batch records for exactly this reason.")


# ===========================================================================
# Exercise 3: Syscall-bound vs CPU-bound benchmark
#
# TODO: Write two benchmarks that run for approximately the same wall time:
#   (a) syscall-bound: call os.write() to /dev/null in a tight loop
#   (b) CPU-bound: compute Fibonacci numbers in a tight loop
# Use os.times() to show the user/kernel split for each.
#
# Goal: see that (a) has high stime, (b) has high utime.
# ===========================================================================

def exercise_3_syscall_vs_cpu_bound():
    print(f"\n{SEPARATOR}")
    print("Exercise 3: Syscall-bound vs CPU-bound — user/kernel time split")
    print(SEPARATOR)

    DURATION_S = 0.5   # run each workload for 0.5 seconds
    buf = b"x"

    # SOLUTION ---------------------------------------------------------------

    # (a) Syscall-bound: write() to /dev/null
    fd = os.open("/dev/null", os.O_WRONLY)
    t0_os = os.times()
    deadline = time.perf_counter() + DURATION_S
    syscall_count = 0
    while time.perf_counter() < deadline:
        os.write(fd, buf)
        syscall_count += 1
    t1_os = os.times()
    os.close(fd)

    user_sc   = t1_os[0] - t0_os[0]
    kernel_sc = t1_os[1] - t0_os[1]
    total_sc  = user_sc + kernel_sc
    pct_kernel_sc = (kernel_sc / total_sc * 100) if total_sc > 0 else 0

    # (b) CPU-bound: Fibonacci
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    t0_os = os.times()
    deadline = time.perf_counter() + DURATION_S
    cpu_count = 0
    while time.perf_counter() < deadline:
        fib(50)
        cpu_count += 1
    t1_os = os.times()

    user_cpu   = t1_os[0] - t0_os[0]
    kernel_cpu = t1_os[1] - t0_os[1]
    total_cpu  = user_cpu + kernel_cpu
    pct_kernel_cpu = (kernel_cpu / total_cpu * 100) if total_cpu > 0 else 0

    print(f"  Syscall-bound (write /dev/null):")
    print(f"    iterations={syscall_count:,}  user={user_sc:.3f}s  kernel={kernel_sc:.3f}s  kernel%={pct_kernel_sc:.0f}%")
    print(f"  CPU-bound (fib(50)):")
    print(f"    iterations={cpu_count:,}  user={user_cpu:.3f}s  kernel={kernel_cpu:.3f}s  kernel%={pct_kernel_cpu:.0f}%")
    print()
    print("  Insight: syscall-bound workloads move ~50% of CPU time into kernel")
    print("  mode. CPU-bound workloads stay almost entirely in user mode (< 1%).")
    print("  This is the os.times() signal that tells you 'reduce syscalls'.")


# ===========================================================================
# Exercise 4: Implement a syscall-batching write wrapper
#
# TODO: Write a class BufferedWriter that:
#   - Has a write(data: bytes) method
#   - Buffers data internally until buffer >= CHUNK_SIZE bytes
#   - Flushes to os.write() only when full or close() is called
#   - Tracks how many syscalls were made
#
# Then benchmark it against unbuffered os.write() for 1 MB of 1-byte writes.
# ===========================================================================

class BufferedWriter:
    """
    Minimal syscall-batching write wrapper.

    Real buffered I/O in Python: use io.BufferedWriter or simply open() in
    binary mode ('wb') — Python's built-in file objects buffer at 8KB by
    default.  This class re-implements the core idea from scratch so you
    can see exactly how it works.
    """

    CHUNK_SIZE = 4096   # flush when internal buffer reaches this size

    def __init__(self, fd: int):
        self.fd = fd
        self._buf = bytearray()
        self.syscall_count = 0

    def write(self, data: bytes):
        self._buf += data
        if len(self._buf) >= self.CHUNK_SIZE:
            self._flush()

    def _flush(self):
        if self._buf:
            os.write(self.fd, bytes(self._buf))
            self._buf.clear()
            self.syscall_count += 1

    def close(self):
        self._flush()   # flush remainder


def exercise_4_batching_wrapper():
    print(f"\n{SEPARATOR}")
    print("Exercise 4: BufferedWriter — manual syscall batching")
    print(SEPARATOR)

    TOTAL = 256 * 1024   # 256 KB in 1-byte writes

    # (a) Unbuffered: one syscall per byte
    fd = os.open("/dev/null", os.O_WRONLY)
    t0 = time.perf_counter_ns()
    for _ in range(TOTAL):
        os.write(fd, b"x")
    t1 = time.perf_counter_ns()
    os.close(fd)
    unbuffered_ms = (t1 - t0) / 1e6
    unbuffered_calls = TOTAL

    # (b) Buffered via our wrapper
    fd = os.open("/dev/null", os.O_WRONLY)
    bw = BufferedWriter(fd)
    t0 = time.perf_counter_ns()
    for _ in range(TOTAL):
        bw.write(b"x")
    bw.close()
    t1 = time.perf_counter_ns()
    os.close(fd)
    buffered_ms = (t1 - t0) / 1e6
    buffered_calls = bw.syscall_count

    speedup = unbuffered_ms / buffered_ms if buffered_ms > 0 else float("inf")
    reduction = unbuffered_calls / buffered_calls if buffered_calls > 0 else float("inf")

    print(f"  {TOTAL // 1024} KB via 1-byte os.write():    {unbuffered_ms:>8.1f} ms  ({unbuffered_calls:,} syscalls)")
    print(f"  {TOTAL // 1024} KB via BufferedWriter:       {buffered_ms:>8.1f} ms  ({buffered_calls:,} syscalls)")
    print(f"  Speedup: {speedup:.0f}x   |   Syscall reduction: {reduction:.0f}x")
    print()
    print("  Insight: the speedup matches the syscall reduction ratio.")
    print("  Buffering trades memory (4KB buffer) for CPU time (fewer crossings).")
    print("  This is exactly what stdio fwrite(), Python's io.BufferedWriter,")
    print("  and every logging library with 'flush interval' settings do.")


# ===========================================================================
# Exercise 5: strace-style timing without strace
#
# strace uses ptrace(2) which has its own overhead. A lighter approach:
# monkey-patch os.write to count calls and measure elapsed time.
#
# TODO: Wrap os.write in a counting decorator that records:
#   - total calls
#   - total bytes written
#   - total elapsed time in ns
# Then run a workload through it and print a summary like strace -c.
# ===========================================================================

class SyscallInterceptor:
    """
    Intercept os.write by replacing it with a counting wrapper.

    This is the user-space equivalent of strace -e write -c — it cannot
    catch C-level writes (e.g., from ctypes or inside the interpreter itself)
    but captures every call made via os.write() from Python code.
    """

    def __init__(self):
        self._original_write = os.write
        self.call_count  = 0
        self.total_bytes = 0
        self.total_ns    = 0

    def __enter__(self):
        interceptor = self

        def patched_write(fd: int, data: bytes) -> int:
            t0 = time.perf_counter_ns()
            result = interceptor._original_write(fd, data)
            t1 = time.perf_counter_ns()
            interceptor.call_count  += 1
            interceptor.total_bytes += len(data)
            interceptor.total_ns    += (t1 - t0)
            return result

        os.write = patched_write
        return self

    def __exit__(self, *_):
        os.write = self._original_write   # restore

    def report(self, label: str = ""):
        avg_ns = self.total_ns / self.call_count if self.call_count else 0
        print(f"  {label}")
        print(f"    calls:       {self.call_count:>10,}")
        print(f"    bytes:       {self.total_bytes:>10,}")
        print(f"    total time:  {self.total_ns/1e6:>10.2f} ms")
        print(f"    avg/call:    {avg_ns:>10.1f} ns")


def exercise_5_strace_style():
    print(f"\n{SEPARATOR}")
    print("Exercise 5: strace-style syscall counter without strace")
    print(SEPARATOR)

    N = 10_000

    # Workload A: many tiny writes
    with SyscallInterceptor() as si_a:
        fd = os.open("/dev/null", os.O_WRONLY)
        for _ in range(N):
            os.write(fd, b"hello\n")
        os.close(fd)
    si_a.report(f"Workload A: {N:,} x 6-byte writes")

    print()

    # Workload B: same data, fewer large writes
    chunk = b"hello\n" * 100
    with SyscallInterceptor() as si_b:
        fd = os.open("/dev/null", os.O_WRONLY)
        for _ in range(N // 100):
            os.write(fd, chunk)
        os.close(fd)
    si_b.report(f"Workload B: {N // 100:,} x 600-byte writes (same total bytes)")

    speedup = (si_a.total_ns / si_b.total_ns) if si_b.total_ns > 0 else float("inf")
    print()
    print(f"  Speedup B vs A: {speedup:.1f}x")
    print()
    print("  Insight: SyscallInterceptor is a lightweight profiler for Python-")
    print("  level I/O. Real strace uses ptrace(2) and captures ALL syscalls")
    print("  including those from C extensions — at ~5x runtime overhead.")
    print("  This wrapper costs almost nothing because it stays in Python land.")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print("practice.py — Day 10: System Calls")
    print("=" * 60)

    exercise_1_ostimes()
    exercise_2_print_cost()
    exercise_3_syscall_vs_cpu_bound()
    exercise_4_batching_wrapper()
    exercise_5_strace_style()

    print(f"\n{SEPARATOR}")
    print("All exercises complete.")
    print()
    print("Summary of mental models:")
    print("  1. os.times() splits CPU time into user/kernel — the ratio tells")
    print("     you if you're syscall-bound.")
    print("  2. print() to a terminal = a write() syscall per call.")
    print("  3. Syscall-bound code shows high stime; CPU-bound shows high utime.")
    print("  4. Buffering reduces syscalls by chunk_size/1 — matching speedup.")
    print("  5. Monkey-patching os.write gives lightweight tracing without ptrace.")
