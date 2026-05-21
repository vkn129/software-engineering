"""
syscall_demo.py — Kernel vs User Space: measuring the mode-switch cost.

Every syscall forces the CPU to swap from ring 3 (user) to ring 0 (kernel)
and back. This demo makes that cost visible by timing syscall-heavy loops
against equivalent pure-user-space loops. The gap IS the kernel crossing tax.

Run:
    python syscall_demo.py
"""

import os
import sys
import ctypes
import ctypes.util
import mmap
import time
import tempfile


# ---------------------------------------------------------------------------
# Section 1: Direct syscall numbers via ctypes
# This is what libc wraps — we are going one layer below libc to show
# what the CPU actually executes.
# ---------------------------------------------------------------------------

def get_libc():
    """Load libc so we can call syscalls by number directly."""
    name = ctypes.util.find_library("c")
    if name is None:
        # Linux fallback — libc is always present, just named differently
        name = "libc.so.6"
    return ctypes.CDLL(name, use_errno=True)


libc = get_libc()

# syscall(2) is the raw gateway: takes a syscall number + args, executes
# the 'syscall' instruction, returns the result. We use it to bypass Python
# and libc entirely for demonstration.
_syscall = libc.syscall
_syscall.restype = ctypes.c_long


# Linux x86_64 syscall numbers (from /usr/include/asm/unistd_64.h)
# These are the literal numbers loaded into rax before 'syscall' fires.
SYS_getpid  = 39
SYS_write   = 1
SYS_read    = 0
SYS_open    = 2
SYS_close   = 3

# ---------------------------------------------------------------------------
# Demo 1: getpid — simplest possible syscall, no arguments, pure ring switch
# ---------------------------------------------------------------------------

def demo_getpid():
    print("\n=== Demo 1: getpid() — the cheapest syscall ===")

    # Python's os.getpid() calls getpid(2) internally via libc
    pid_via_os = os.getpid()

    # We can also invoke it directly through ctypes to bypass Python overhead
    if sys.platform.startswith("linux"):
        pid_via_raw = _syscall(SYS_getpid)
        print(f"  os.getpid()       = {pid_via_os}")
        print(f"  raw syscall(39)   = {pid_via_raw}")
        assert pid_via_os == pid_via_raw, "They must agree — same kernel call"
    else:
        print(f"  os.getpid()       = {pid_via_os}")
        print("  (raw syscall demo skipped on non-Linux)")

    print("  Both cross the ring 0 boundary exactly once.")


# ---------------------------------------------------------------------------
# Demo 2: open / write / close — file I/O as a sequence of syscalls
# ---------------------------------------------------------------------------

def demo_file_syscalls():
    print("\n=== Demo 2: open/write/close — three separate ring crossings ===")

    # Each of these is one syscall: one mode switch in, kernel work, mode
    # switch out. The file descriptor returned by open() is a kernel-managed
    # integer — it is an index into the per-process file descriptor table
    # that lives in kernel memory, not user memory.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".demo") as f:
        path = f.name

    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    # os.write issues the write(2) syscall — kernel copies buf from user space
    # into page cache (kernel memory), queues a write-back to disk.
    n = os.write(fd, b"kernel boundary crossed\n")
    os.close(fd)

    fd = os.open(path, os.O_RDONLY)
    data = os.read(fd, 64)
    os.close(fd)
    os.unlink(path)

    print(f"  Wrote {n} bytes, read back: {data.rstrip()}")
    print("  Each os.* call above was exactly one syscall (ring 3 -> 0 -> 3).")


# ---------------------------------------------------------------------------
# Demo 3: mmap — the kernel gives user space a window into kernel page cache
# ---------------------------------------------------------------------------

def demo_mmap():
    print("\n=== Demo 3: mmap — kernel maps pages into user address space ===")

    # mmap(2) asks the kernel to insert entries into our page table so that
    # a range of our virtual addresses points at physical pages. After this
    # syscall returns, we can read/write those addresses without any further
    # syscalls — the MMU handles it transparently.
    size = 4096  # one page
    buf = mmap.mmap(-1, size, mmap.MAP_SHARED | mmap.MAP_ANONYMOUS,
                    mmap.PROT_READ | mmap.PROT_WRITE)

    buf.write(b"written without a syscall after mmap")
    buf.seek(0)
    result = buf.read(36)
    buf.close()

    print(f"  Data read from mmap'd region: {result}")
    print("  The write above did NOT cross the kernel boundary — MMU handled it.")
    print("  Only mmap() and munmap() (close) are syscalls; the accesses are not.")


# ---------------------------------------------------------------------------
# Demo 4: Timing — user-space loop vs syscall loop
# The visible gap is the cost of the ring 0 crossing.
# ---------------------------------------------------------------------------

def demo_timing():
    print("\n=== Demo 4: Timing the kernel boundary crossing ===")

    N = 100_000

    # Pure user-space: arithmetic only, never leaves ring 3.
    # The CPU runs this at full speed with no mode switches.
    start = time.perf_counter()
    acc = 0
    for i in range(N):
        acc += i  # ring 3 only
    user_time = time.perf_counter() - start

    # Syscall-heavy: getpid() is the cheapest syscall available.
    # It does almost no kernel work — it just reads task_struct->pid and
    # returns. So the time difference is almost purely mode-switch overhead.
    start = time.perf_counter()
    for _ in range(N):
        os.getpid()  # ring 3 -> 0 -> 3 each iteration
    syscall_time = time.perf_counter() - start

    user_ns   = user_time   * 1e9 / N
    kernel_ns = syscall_time * 1e9 / N

    print(f"  Pure user-space loop:  {user_ns:6.1f} ns / iteration")
    print(f"  getpid() syscall loop: {kernel_ns:6.1f} ns / iteration")
    print(f"  Mode-switch overhead:  ~{kernel_ns - user_ns:.1f} ns per crossing")
    print()
    print("  This gap (typically 100-300 ns) is why high-performance systems")
    print("  batch syscalls (io_uring) or eliminate them (mmap, vDSO).")


# ---------------------------------------------------------------------------
# Demo 5: File descriptor lifecycle — what the kernel tracks on your behalf
# ---------------------------------------------------------------------------

def demo_fd_lifecycle():
    print("\n=== Demo 5: File descriptors — handles into kernel-managed state ===")

    # stdin/stdout/stderr are fd 0/1/2 — the kernel opens these before
    # exec() and they are inherited. They are not pointers; they are indices
    # into the kernel's file descriptor table for this process.
    print(f"  stdin  fd={sys.stdin.fileno()}  (kernel-allocated)")
    print(f"  stdout fd={sys.stdout.fileno()} (kernel-allocated)")
    print(f"  stderr fd={sys.stderr.fileno()} (kernel-allocated)")

    # Open a new fd — kernel picks the lowest unused integer
    with tempfile.NamedTemporaryFile(delete=True) as f:
        new_fd = f.fileno()
        print(f"  tempfile fd={new_fd} (next available slot in kernel fd table)")
        print(f"  /proc/self/fd/{new_fd} -> kernel tracks the file position,")
        print(f"  flags, and inode reference for this fd in kernel memory.")

    # After context manager closes, fd is gone — kernel freed the slot.
    print("  After close: fd slot is freed, kernel decrements inode refcount.")


# ---------------------------------------------------------------------------
# Demo 6: /proc — the kernel exposing its own state as a filesystem
# ---------------------------------------------------------------------------

def demo_proc():
    print("\n=== Demo 6: /proc/self/status — kernel's view of this process ===")

    if not os.path.exists("/proc/self/status"):
        print("  /proc not available on this platform.")
        return

    with open("/proc/self/status") as f:
        lines = f.readlines()

    # Print a curated subset — these are all values the kernel maintains
    # in the process's task_struct (kernel data structure, not user memory).
    keys_of_interest = {"Name", "Pid", "PPid", "VmRSS", "VmPeak",
                        "Threads", "voluntary_ctxt_switches",
                        "nonvoluntary_ctxt_switches"}
    print("  Fields from kernel's task_struct for this process:")
    for line in lines:
        key = line.split(":")[0].strip()
        if key in keys_of_interest:
            print(f"    {line.rstrip()}")

    print()
    print("  voluntary_ctxt_switches   = process called a blocking syscall")
    print("  nonvoluntary_ctxt_switches = kernel preempted the process (scheduler)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  Kernel vs User Space — syscall boundary demonstration")
    print(f"  PID: {os.getpid()}  |  Platform: {sys.platform}")
    print("=" * 60)

    demo_getpid()
    demo_file_syscalls()
    demo_mmap()
    demo_timing()
    demo_fd_lifecycle()
    demo_proc()

    print("\n" + "=" * 60)
    print("  Key takeaway: every os.* call above was a kernel crossing.")
    print("  Every arithmetic operation, list access, or function call was not.")
    print("  The hardware CPL bit is the only thing that separates them.")
    print("=" * 60)
