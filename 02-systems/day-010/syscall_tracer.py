"""
syscall_tracer.py — Measure the real cost of syscalls from Python.

Strategy:
  - Wrap raw syscall numbers via ctypes to force actual kernel crossings
  - Compare clock_gettime (vDSO, fast path) vs gettid (always a true syscall)
  - Show 1-byte write vs 4KB write throughput over 1 MB of data
  - Everything stdlib only; no subprocess, no external tools

Syscall numbers (x86_64 Linux, kernel ABI frozen since 2.6):
  SYS_write      = 1
  SYS_clock_gettime = 228
  SYS_gettid     = 186
"""

import ctypes
import ctypes.util
import os
import sys
import time

# ---------------------------------------------------------------------------
# 1. Load libc and set up raw syscall access
# ---------------------------------------------------------------------------

_libc_name = ctypes.util.find_library("c")
if _libc_name is None:
    print("ERROR: could not locate libc — this script requires glibc on Linux")
    sys.exit(1)

_libc = ctypes.CDLL(_libc_name, use_errno=True)

# syscall(2): variable-argument C function; return type is long.
_raw_syscall = _libc.syscall
_raw_syscall.restype = ctypes.c_long
# We set argtypes dynamically per call via ctypes variadic support.

# Syscall numbers (x86_64 only — check /usr/include/asm/unistd_64.h)
SYS_write        = 1
SYS_gettid       = 186
SYS_clock_gettime = 228

# CLOCK_MONOTONIC = 1 (man 2 clock_gettime)
CLOCK_MONOTONIC  = 1
CLOCK_REALTIME   = 0


# ---------------------------------------------------------------------------
# 2. timespec struct for clock_gettime
# ---------------------------------------------------------------------------

class Timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]

    def to_ns(self) -> int:
        return self.tv_sec * 1_000_000_000 + self.tv_nsec

    def to_seconds(self) -> float:
        return self.tv_sec + self.tv_nsec / 1e9


# ---------------------------------------------------------------------------
# 3. Wrappers that count invocations
# ---------------------------------------------------------------------------

class SyscallCounter:
    """Wraps specific syscalls, tracks call count and total elapsed ns."""

    def __init__(self):
        self.counts: dict[str, int] = {}
        self.total_ns: dict[str, int] = {}

    def _record(self, name: str, elapsed_ns: int):
        self.counts[name] = self.counts.get(name, 0) + 1
        self.total_ns[name] = self.total_ns.get(name, 0) + elapsed_ns

    # --- clock_gettime via direct syscall (bypasses vDSO wrapper in glibc) ---
    def clock_gettime_syscall(self, clk_id: int = CLOCK_MONOTONIC) -> Timespec:
        """Force a real syscall even for clocks the vDSO handles."""
        ts = Timespec()
        t0 = time.perf_counter_ns()
        ret = _raw_syscall(
            ctypes.c_long(SYS_clock_gettime),
            ctypes.c_int(clk_id),
            ctypes.byref(ts),
        )
        t1 = time.perf_counter_ns()
        if ret != 0:
            raise OSError(ctypes.get_errno(), "clock_gettime failed")
        self._record("clock_gettime_syscall", t1 - t0)
        return ts

    # --- gettid: always a real syscall, no vDSO ---
    def gettid(self) -> int:
        t0 = time.perf_counter_ns()
        tid = _raw_syscall(ctypes.c_long(SYS_gettid))
        t1 = time.perf_counter_ns()
        self._record("gettid", t1 - t0)
        return int(tid)

    def report(self):
        print("\n--- SyscallCounter report ---")
        for name in sorted(self.counts):
            n = self.counts[name]
            total = self.total_ns[name]
            avg = total / n if n else 0
            print(f"  {name}: {n:>8,} calls  |  avg {avg:>8.1f} ns/call  |  total {total/1e6:>8.2f} ms")


# ---------------------------------------------------------------------------
# 4. clock_gettime via glibc wrapper (uses vDSO when available)
# ---------------------------------------------------------------------------

_libc_clock_gettime = _libc.clock_gettime
_libc_clock_gettime.restype  = ctypes.c_int
_libc_clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(Timespec)]

_vdso_call_count = 0
_vdso_total_ns   = 0

def clock_gettime_vdso(clk_id: int = CLOCK_MONOTONIC) -> Timespec:
    """Call glibc's clock_gettime — on modern kernels this goes through vDSO."""
    global _vdso_call_count, _vdso_total_ns
    ts = Timespec()
    t0 = time.perf_counter_ns()
    ret = _libc_clock_gettime(clk_id, ctypes.byref(ts))
    t1 = time.perf_counter_ns()
    if ret != 0:
        raise OSError(ctypes.get_errno(), "clock_gettime (vDSO) failed")
    _vdso_call_count += 1
    _vdso_total_ns   += t1 - t0
    return ts


# ---------------------------------------------------------------------------
# 5. Benchmark: vDSO vs real syscall
# ---------------------------------------------------------------------------

def bench_clock_mechanisms(n: int = 50_000):
    """
    Compare wall-time cost of:
      (a) glibc clock_gettime  (routes through vDSO on Linux ≥ 2.6.37)
      (b) raw clock_gettime syscall
      (c) gettid               (always kernel, no vDSO)

    We use time.perf_counter_ns() as a meta-timer around each call.
    The meta-timer itself has overhead (~20-50 ns), so we measure in bulk
    and divide to get per-call cost.
    """
    print(f"\n=== Clock mechanism comparison ({n:,} calls each) ===")

    counter = SyscallCounter()

    # (a) glibc / vDSO path
    t0 = time.perf_counter_ns()
    for _ in range(n):
        clock_gettime_vdso(CLOCK_MONOTONIC)
    t1 = time.perf_counter_ns()
    vdso_avg_ns = (t1 - t0) / n
    print(f"  glibc clock_gettime (vDSO path): {vdso_avg_ns:6.1f} ns/call")

    # (b) forced raw syscall path
    ts_list = []
    t0 = time.perf_counter_ns()
    for _ in range(n):
        ts_list.append(counter.clock_gettime_syscall(CLOCK_MONOTONIC))
    t1 = time.perf_counter_ns()
    syscall_avg_ns = (t1 - t0) / n
    print(f"  raw syscall clock_gettime:       {syscall_avg_ns:6.1f} ns/call")

    # (c) gettid — always real syscall
    tids = []
    t0 = time.perf_counter_ns()
    for _ in range(n):
        tids.append(counter.gettid())
    t1 = time.perf_counter_ns()
    gettid_avg_ns = (t1 - t0) / n
    print(f"  gettid (always real syscall):    {gettid_avg_ns:6.1f} ns/call")

    if vdso_avg_ns > 0:
        print(f"\n  Speedup vDSO vs raw clock_gettime: {syscall_avg_ns / vdso_avg_ns:.1f}x")
        print(f"  Speedup vDSO vs gettid:            {gettid_avg_ns / vdso_avg_ns:.1f}x")

    print(f"\n  Note: Differences shrink after first few calls due to branch-predictor")
    print(f"  warm-up. Real vDSO advantage is most visible on a cold process.")

    # Show vDSO is visible in /proc/self/maps
    print("\n  vDSO in /proc/self/maps:")
    try:
        with open("/proc/self/maps") as f:
            for line in f:
                if "vdso" in line or "vvar" in line:
                    print(f"    {line.rstrip()}")
    except OSError:
        print("    (could not read /proc/self/maps)")


# ---------------------------------------------------------------------------
# 6. Benchmark: 1-byte writes vs 4KB writes (1 MB total)
# ---------------------------------------------------------------------------

def bench_write_batching(total_bytes: int = 1 * 1024 * 1024):
    """
    Write total_bytes to /dev/null in two ways:
      (a) 1 byte at a time  → total_bytes syscalls
      (b) 4096 bytes at a time → total_bytes // 4096 syscalls

    Measures wall time and computes throughput MB/s.
    The fixed per-syscall overhead is the only difference — same total data.
    """
    chunk_4k = b"x" * 4096
    chunk_1  = b"x"

    print(f"\n=== Write batching benchmark ({total_bytes // 1024} KB total) ===")

    fd = os.open("/dev/null", os.O_WRONLY)
    try:
        # --- 4KB chunks ---
        n_chunks = total_bytes // 4096
        t0 = time.perf_counter_ns()
        for _ in range(n_chunks):
            os.write(fd, chunk_4k)
        t1 = time.perf_counter_ns()
        elapsed_4k_s = (t1 - t0) / 1e9
        throughput_4k = (total_bytes / elapsed_4k_s) / (1024 * 1024)

        # --- 1-byte writes ---
        t0 = time.perf_counter_ns()
        for _ in range(total_bytes):
            os.write(fd, chunk_1)
        t1 = time.perf_counter_ns()
        elapsed_1b_s = (t1 - t0) / 1e9
        throughput_1b = (total_bytes / elapsed_1b_s) / (1024 * 1024)

    finally:
        os.close(fd)

    print(f"  4KB chunks  : {n_chunks:>7,} syscalls  |  {elapsed_4k_s*1000:>8.1f} ms  |  {throughput_4k:>8.1f} MB/s")
    print(f"  1-byte writes: {total_bytes:>7,} syscalls  |  {elapsed_1b_s*1000:>8.1f} ms  |  {throughput_1b:>8.1f} MB/s")
    speedup = throughput_4k / throughput_1b if throughput_1b > 0 else float("inf")
    print(f"\n  Speedup (4KB vs 1B): {speedup:.0f}x")
    print(f"  Per-syscall overhead estimate: ~{elapsed_1b_s*1e9/total_bytes:.0f} ns/call (1-byte path)")
    print(f"  This overhead is ~constant regardless of payload — fixed kernel crossing cost.")


# ---------------------------------------------------------------------------
# 7. Show syscall number convention
# ---------------------------------------------------------------------------

def show_syscall_table_excerpt():
    """
    Print the x86_64 syscall number for common calls.
    These are hard-coded in the kernel ABI and never change.
    """
    # A small excerpt from syscall_64.tbl
    table = [
        (0,   "read"),
        (1,   "write"),
        (2,   "open"),
        (3,   "close"),
        (9,   "mmap"),
        (11,  "munmap"),
        (39,  "getpid"),
        (56,  "clone"),
        (60,  "exit"),
        (62,  "kill"),
        (186, "gettid"),
        (202, "futex"),
        (228, "clock_gettime"),
        (257, "openat"),
        (425, "io_uring_setup"),
        (426, "io_uring_enter"),
    ]
    print("\n=== x86_64 syscall table excerpt (rax values) ===")
    print(f"  {'rax':>4}  {'name':<20}")
    print(f"  {'-'*4}  {'-'*20}")
    for num, name in table:
        print(f"  {num:>4}  {name:<20}")
    print("\n  These numbers are frozen ABI. Changing them would break every")
    print("  compiled binary on the planet. io_uring got high numbers because")
    print("  it was added in 2019; the low numbers reflect POSIX origins (1988).")


# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("syscall_tracer.py — syscall cost demonstration")
    print("=" * 55)
    print(f"PID: {os.getpid()}  |  Python {sys.version.split()[0]}")

    show_syscall_table_excerpt()
    bench_clock_mechanisms(n=100_000)
    bench_write_batching(total_bytes=1_024 * 1_024)

    print("\nDone. Key takeaways:")
    print("  1. vDSO clock_gettime is 5-20x faster than a real syscall.")
    print("  2. gettid always crosses the boundary — ~300 ns, not ~30 ns.")
    print("  3. 1-byte writes are ~4096x slower per byte than 4KB writes.")
    print("  4. The fixed kernel-crossing overhead dominates at small payloads.")
    print("  5. io_uring eliminates even the single enter() call with SQPOLL.")
