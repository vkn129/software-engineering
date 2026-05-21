"""
practice.py — Day 1: Kernel vs User Space — Five Exercises

Work through each exercise by replacing TODO with real code.
The solution for each exercise lives after the sentinel comment at the bottom.
Run with: python practice.py
"""

import os
import sys
import time
import signal

# ============================================================
# Exercise 1: Syscall vs Library Call Classification
#
# The goal: build the reflex of asking "does this cross the
# kernel boundary?" for every call you write.
#
# A syscall is a trap — it switches the CPU from ring 3 to
# ring 0. A library call is a regular function call that stays
# entirely in user space. Many libc functions ARE syscalls
# (os.read), others are NOT (math.sqrt), and some sometimes
# are (malloc — only when it needs more memory from the kernel).
# ============================================================

def exercise_1_classify():
    """
    For each operation below, decide: syscall, library call,
    or "sometimes a syscall". Print your classification with
    a one-line reason.

    Operations to classify:
      a) os.getpid()
      b) len("hello")
      c) open("file.txt", "r")       # Python built-in open
      d) os.read(0, 1)
      e) time.time()
      f) os.fork()
      g) [x*2 for x in range(10)]
      h) os.mmap / mmap.mmap(...)
      i) str.encode("utf-8")
      j) os.write(1, b"hi\n")
    """
    print("\n=== Exercise 1: Syscall vs Library Call ===")
    # TODO: print your classification for each of a-j above.
    # Example format:
    #   print("a) os.getpid() — SYSCALL: asks kernel for PID from task_struct")
    pass


# ============================================================
# Exercise 2: Measure Syscall Overhead
#
# The goal: make the kernel/user crossing cost *visible* in
# nanoseconds so it feels real, not theoretical.
#
# Strategy: run two tight loops — one that is pure arithmetic
# (never leaves ring 3), one that calls the cheapest possible
# syscall (getpid does almost no kernel work, so the delta is
# dominated by the mode-switch itself).
# ============================================================

def exercise_2_measure_overhead(n=50_000):
    """
    Time N iterations of:
      - Pure user-space: integer addition (stays in ring 3)
      - Syscall: os.getpid() (ring 3 -> 0 -> 3 each call)

    Compute and print the overhead in nanoseconds per crossing.
    """
    print(f"\n=== Exercise 2: Syscall Overhead (N={n:,}) ===")
    # TODO: time the user-space loop, time the syscall loop,
    # compute ns/iteration for each, print the difference.
    pass


# ============================================================
# Exercise 3: Fork — Kernel-Mediated Process Creation
#
# The goal: see that creating a new process is NOT a user-space
# operation. fork() is a syscall that asks the kernel to:
#   1. Duplicate the current process's page tables (copy-on-write)
#   2. Allocate a new PID from the kernel's PID namespace
#   3. Clone the file descriptor table
#   4. Schedule the child on a CPU
#
# The child and parent share no user-space state — any variable
# you modify in one is invisible to the other (until CoW triggers
# a page fault and the kernel hands the child a private copy).
# ============================================================

def exercise_3_fork():
    """
    Use os.fork() to create a child process. In the child:
      - Print the child's PID and parent's PID (os.getppid())
      - Modify a local variable and print it
    In the parent:
      - Wait for the child (os.wait())
      - Print the same variable to show it was not affected
    Skip gracefully on Windows.
    """
    print("\n=== Exercise 3: Fork — Process Creation via Kernel ===")

    if sys.platform == "win32":
        print("  os.fork() not available on Windows — skipping.")
        return

    # TODO: implement fork demo here.
    pass


# ============================================================
# Exercise 4: Signal Handling — Kernel Delivers, User Handles
#
# The goal: see the kernel/user interplay in signal delivery.
# When you press Ctrl+C, the terminal sends SIGINT to the
# foreground process group. The kernel:
#   1. Receives the interrupt from the keyboard driver (ring 0)
#   2. Sets a pending-signal flag in the process's task_struct
#   3. On the next return from kernel mode, checks for pending signals
#   4. Redirects execution to the user-space signal handler
#
# The handler runs in USER SPACE — the kernel just set up the
# stack frame and transferred control. Your handler is ring 3 code.
# ============================================================

def exercise_4_signals():
    """
    Register a SIGINT handler with signal.signal().
    Then raise SIGINT programmatically with os.kill(os.getpid(), signal.SIGINT).
    Verify the handler runs, then restore the default handler.

    Print:
      - A message when the handler is entered (proving it ran)
      - The signal number received
    """
    print("\n=== Exercise 4: Signal Delivery (Kernel -> User Space) ===")

    # TODO: implement signal handler registration and delivery.
    # Hint: signal.signal(signal.SIGINT, your_handler_function)
    #       os.kill(os.getpid(), signal.SIGINT)
    pass


# ============================================================
# Exercise 5: /proc/self/status — The Kernel's Ledger
#
# The goal: read what the kernel tracks about your process.
# /proc is a virtual filesystem — reading a file in it does NOT
# hit disk. The kernel generates the content on-the-fly from
# the process's task_struct (a C struct in kernel memory).
#
# This is one of the cleanest examples of the kernel/user boundary:
# you cannot directly read task_struct (it is kernel memory),
# but the kernel exposes a curated, safe view through /proc.
# ============================================================

def exercise_5_proc_status():
    """
    Read /proc/self/status and print these fields with a one-line
    explanation of what each means:
      - Name
      - Pid
      - PPid
      - VmRSS       (resident set size — physical RAM in use)
      - VmPeak      (peak virtual address space size)
      - Threads
      - voluntary_ctxt_switches
      - nonvoluntary_ctxt_switches

    Skip gracefully if /proc is not available (non-Linux).
    """
    print("\n=== Exercise 5: /proc/self/status — Kernel's Process Ledger ===")

    if not os.path.exists("/proc/self/status"):
        print("  /proc not available on this platform — skipping.")
        return

    # TODO: open and parse /proc/self/status, print the fields above
    # with explanations.
    pass


# ============================================================
# Run all exercises
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Day 1 Practice: Kernel vs User Space")
    print("=" * 60)

    exercise_1_classify()
    exercise_2_measure_overhead()
    exercise_3_fork()
    exercise_4_signals()
    exercise_5_proc_status()

    print("\n" + "=" * 60)
    print("  See solutions below the sentinel comment.")
    print("=" * 60)


# ============================================================
# SOLUTIONS — do not read until you have attempted each exercise
# ============================================================
# __SOLUTIONS_BELOW__


def _solution_1():
    """
    Classification answers (with kernel-boundary reasoning):

    a) os.getpid()
       SYSCALL — getpid(2). Reads task_struct->pid in ring 0.
       (Note: on Linux with vDSO, getpid may be served from user space
        by a kernel-mapped page to avoid the full crossing — but it is
        logically a syscall.)

    b) len("hello")
       LIBRARY CALL (no syscall). String length is computed in user space
       by reading the PyObject size field. Never leaves ring 3.

    c) open("file.txt", "r")
       SYSCALL — open(2) / openat(2). The kernel checks permissions,
       allocates a file descriptor in the fd table, and returns the integer.

    d) os.read(0, 1)
       SYSCALL — read(2). Kernel copies data from a kernel buffer (pipe,
       socket, or page cache) into user space. Always a ring crossing.

    e) time.time()
       SOMETIMES A SYSCALL. On Linux, gettimeofday/clock_gettime is
       served via vDSO — a kernel page mapped into every process's address
       space. The kernel updates a shared time value; user code reads it
       without a mode switch. The call *looks* like a syscall but avoids it.

    f) os.fork()
       SYSCALL — fork(2). The kernel duplicates the process: new PID,
       copy-on-write page tables, cloned fd table, new task_struct. Cannot
       be done in user space — requires kernel data structure manipulation.

    g) [x*2 for x in range(10)]
       LIBRARY CALL. Pure arithmetic and list allocation in user space.
       malloc underneath might call brk(2) if the heap is exhausted, but
       for 10 elements it will not.

    h) mmap.mmap(-1, 4096, ...)
       SYSCALL — mmap(2). The kernel modifies the process's page table
       to map new virtual address ranges. Cannot be done without ring 0
       access to page table structures.

    i) str.encode("utf-8")
       LIBRARY CALL. String encoding is a pure computation in user space
       (iterate characters, apply UTF-8 byte rules). No hardware or kernel
       state involved.

    j) os.write(1, b"hi\n")
       SYSCALL — write(2). Kernel copies bytes from user buffer into the
       page cache or socket buffer and schedules the I/O. Always ring 3->0.
    """


def _solution_2():
    print(f"\n=== Exercise 2: Syscall Overhead ===")
    n = 50_000

    # User-space baseline: integer addition, never leaves ring 3.
    # We sum into a variable so the optimizer cannot eliminate the loop.
    start = time.perf_counter()
    acc = 0
    for i in range(n):
        acc += i
    user_time = time.perf_counter() - start

    # Syscall loop: getpid() does minimal kernel work (reads one field from
    # task_struct). The time difference isolates the mode-switch cost itself.
    start = time.perf_counter()
    for _ in range(n):
        os.getpid()
    syscall_time = time.perf_counter() - start

    user_ns = user_time * 1e9 / n
    kernel_ns = syscall_time * 1e9 / n

    print(f"  User-space loop:   {user_ns:7.1f} ns/iter  (acc={acc})")
    print(f"  getpid() loop:     {kernel_ns:7.1f} ns/iter")
    print(f"  Mode-switch cost:  ~{max(0, kernel_ns - user_ns):.1f} ns per crossing")
    print()
    print("  Interpretation: the gap is the cost of saving registers,")
    print("  switching CPL bits, jumping to kernel entry, and returning.")
    print("  This is why io_uring exists: to batch many ops per crossing.")


def _solution_3():
    print("\n=== Exercise 3: Fork ===")

    if sys.platform == "win32":
        print("  os.fork() not available on Windows — skipping.")
        return

    # This variable lives in the parent's user-space memory.
    # After fork(), the child gets a copy-on-write copy.
    shared_var = 42

    pid = os.fork()

    if pid == 0:
        # We are in the child process. The kernel gave us a new PID and
        # copied the parent's page tables (copy-on-write). Modifying
        # shared_var here triggers a page fault — the kernel creates a
        # private physical page for the child. The parent's page is untouched.
        shared_var = 999
        child_pid = os.getpid()
        parent_pid = os.getppid()
        print(f"  [child]  PID={child_pid}  PPID={parent_pid}  shared_var={shared_var}")
        print(f"  [child]  I modified shared_var — this is MY private copy (CoW).")
        # Child must exit cleanly to avoid running the rest of __main__.
        os._exit(0)
    else:
        # We are in the parent. Wait for child to finish.
        child_pid, exit_status = os.wait()
        print(f"  [parent] PID={os.getpid()}  child was PID={child_pid}")
        print(f"  [parent] shared_var={shared_var}  (unchanged — CoW protected us)")
        print(f"  [parent] fork() cost: one syscall, new task_struct, cloned page tables.")


def _solution_4():
    print("\n=== Exercise 4: Signal Delivery ===")

    # Signal delivery flow:
    #   1. Sender (us, via os.kill) calls kill(2) — syscall, ring 3->0.
    #   2. Kernel sets SIGINT pending in our task_struct.
    #   3. On return from the kill() syscall, kernel checks pending signals.
    #   4. Kernel sets up a signal frame on our user-space stack and jumps
    #      to the handler — execution continues in ring 3, in our code.
    #   5. When handler returns, kernel cleans up the signal frame and
    #      resumes wherever we were interrupted.

    received = []

    def sigint_handler(signum, frame):
        # This runs in user space (ring 3). The kernel delivered control here
        # by manipulating our stack — we did not ask for it explicitly.
        received.append(signum)
        print(f"  [handler] SIGINT received! signum={signum}")
        print(f"  [handler] Running in user space (ring 3) after kernel delivery.")

    # Register our handler. signal.signal() calls sigaction(2) under the hood
    # to tell the kernel which user-space address to jump to on SIGINT.
    old_handler = signal.signal(signal.SIGINT, sigint_handler)

    print("  Sending SIGINT to ourselves via os.kill()...")
    # kill(2) is a syscall — kernel receives it, marks SIGINT pending,
    # then on syscall return detects the pending signal and fires the handler.
    os.kill(os.getpid(), signal.SIGINT)

    # Restore default handler so Ctrl+C works normally after this exercise.
    signal.signal(signal.SIGINT, old_handler)

    if received:
        print(f"  Handler ran correctly — signal {received[0]} was delivered.")
    else:
        print("  Handler did not run (unexpected).")


def _solution_5():
    print("\n=== Exercise 5: /proc/self/status ===")

    if not os.path.exists("/proc/self/status"):
        print("  /proc not available on this platform — skipping.")
        return

    # /proc/self/status is generated on-the-fly by the kernel's procfs
    # driver. Reading it does NOT hit disk — the kernel fills a buffer
    # from the current process's task_struct and returns it. It is a
    # controlled window from user space into kernel memory.
    with open("/proc/self/status") as f:
        status = {}
        for line in f:
            if ":" in line:
                key, _, value = line.partition(":")
                status[key.strip()] = value.strip()

    fields = {
        "Name":                      "Executable name (from exec syscall)",
        "Pid":                       "Process ID (kernel-assigned, unique system-wide)",
        "PPid":                      "Parent PID (set by fork — kernel tracks the tree)",
        "VmRSS":                     "Resident Set Size — physical RAM pages currently mapped",
        "VmPeak":                    "Peak virtual memory size (high-water mark)",
        "Threads":                   "Thread count (each thread has its own kernel task_struct)",
        "voluntary_ctxt_switches":   "Times process yielded CPU (blocking syscall, sleep)",
        "nonvoluntary_ctxt_switches":"Times kernel preempted process (time quantum expired)",
    }

    print("  Field                        Value              Meaning")
    print("  " + "-" * 72)
    for field, meaning in fields.items():
        val = status.get(field, "N/A")
        print(f"  {field:<28} {val:<18} {meaning}")

    print()
    print("  Key insight: voluntary switches = you called a blocking syscall.")
    print("  Nonvoluntary switches = the kernel's scheduler yanked the CPU away.")
    print("  High nonvoluntary count -> your process is competing for CPU time.")


# ============================================================
# Run solutions if invoked with --solutions flag
# ============================================================

if __name__ == "__main__" and "--solutions" in sys.argv:
    print("\n" + "=" * 60)
    print("  SOLUTIONS")
    print("=" * 60)
    _solution_1.__doc__ and print(_solution_1.__doc__)
    _solution_2()
    _solution_3()
    _solution_4()
    _solution_5()
