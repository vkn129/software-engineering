"""
process_demo.py — Day 2: Processes (fork, exec, wait, zombies)

Demonstrates:
  1. os.fork() basics: parent/child PID identification
  2. exec() from child: replace child image with /bin/ls
  3. Fork bomb defuser: spawn N children, print PIDs, reap all
  4. Zombie creation and reaping
  5. Summary table of what was demonstrated

Linux only. On Windows, prints a clear skip message and exits.
"""

import os
import sys
import time
import signal

# ── Platform guard ────────────────────────────────────────────────────────────

def check_platform():
    if not hasattr(os, "fork"):
        print("=" * 60)
        print("SKIP: os.fork() is not available on this platform.")
        print("This demo requires Linux or macOS.")
        print("=" * 60)
        sys.exit(0)

# ── Section 1: fork() basics ──────────────────────────────────────────────────

def demo_fork_basics():
    """
    Show that fork() duplicates the process and returns different
    values in parent vs child.
    """
    print("\n" + "=" * 60)
    print("DEMO 1: fork() basics — parent vs child PID")
    print("=" * 60)

    parent_pid = os.getpid()
    print(f"[parent] PID={parent_pid}, about to fork...")

    pid = os.fork()

    if pid == 0:
        # Child: fork() returned 0
        # os.getppid() is the parent's PID — proves the PCB PPID field
        print(f"[child]  PID={os.getpid()}, PPID={os.getppid()}, fork() returned {pid}")
        # Exit child cleanly so parent's wait() below succeeds
        os._exit(0)
    else:
        # Parent: fork() returned child's PID
        print(f"[parent] PID={os.getpid()}, fork() returned child PID={pid}")
        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status)
        print(f"[parent] child exited with code {exit_code}")

# ── Section 2: fork + exec ────────────────────────────────────────────────────

def demo_fork_exec():
    """
    Fork a child, then exec /bin/ls in the child.
    The child's process image is replaced entirely.
    The PID stays the same but the code, memory, and registers are new.
    """
    print("\n" + "=" * 60)
    print("DEMO 2: fork() + exec() — replace child image with /bin/ls")
    print("=" * 60)

    # List the current directory so output is predictable
    target_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[parent] Will exec: /bin/ls {target_dir}")

    pid = os.fork()

    if pid == 0:
        # Child: replace our image with /bin/ls
        # execv(path, args): args[0] is argv[0] by convention
        print(f"[child]  PID={os.getpid()}, calling exec('/bin/ls')...")
        sys.stdout.flush()          # flush before exec wipes our buffers
        os.execv("/bin/ls", ["/bin/ls", target_dir])
        # If execv returns, something went wrong
        print("[child]  ERROR: exec failed", file=sys.stderr)
        os._exit(1)
    else:
        # Parent waits for child
        _, status = os.waitpid(pid, 0)
        print(f"[parent] child (exec'd ls) exited with code {os.WEXITSTATUS(status)}")

# ── Section 3: Fork bomb defuser ──────────────────────────────────────────────

def demo_fork_bomb_defuser(n: int = 5):
    """
    Safely spawn N children, print each PID, and reap them all.
    This is the *controlled* version of a fork bomb: we track every
    child PID so we can wait for each one.

    A real fork bomb does NOT track PIDs and each child forks again,
    producing 2^k processes at depth k. We never do that here.
    """
    print("\n" + "=" * 60)
    print(f"DEMO 3: Fork bomb defuser — spawn {n} children and reap all")
    print("=" * 60)

    child_pids = []

    for i in range(n):
        pid = os.fork()
        if pid == 0:
            # Child: do some "work" then exit with its index as exit code
            time.sleep(0.05)    # simulate brief work
            print(f"  [child {i}] PID={os.getpid()}, done")
            sys.stdout.flush()
            os._exit(i)         # exit code = child index
        else:
            child_pids.append(pid)
            print(f"[parent] spawned child {i}, PID={pid}")

    print(f"[parent] spawned {n} children, now reaping...")

    # Reap all children — order may differ from spawn order
    results = {}
    for _ in range(n):
        pid, status = os.wait()     # wait for any child
        code = os.WEXITSTATUS(status)
        results[pid] = code
        print(f"[parent] reaped PID={pid}, exit_code={code}")

    print(f"[parent] all {n} children reaped. Results: {results}")

# ── Section 4: Zombie creation and reaping ────────────────────────────────────

def demo_zombie():
    """
    Demonstrate zombie state:
      1. Fork a child that exits immediately.
      2. Parent sleeps briefly WITHOUT calling wait() — child is now a zombie.
         In /proc/<pid>/status you would see State: Z (zombie).
      3. Parent then calls wait() — zombie is reaped, PCB entry freed.

    We cannot easily show /proc state from within the same process without
    a second process, so we print the timing to make the window visible.
    """
    print("\n" + "=" * 60)
    print("DEMO 4: Zombie creation and reaping")
    print("=" * 60)

    pid = os.fork()

    if pid == 0:
        # Child exits immediately
        print(f"[child]  PID={os.getpid()} exiting now (will become zombie)")
        sys.stdout.flush()
        os._exit(42)
    else:
        # Parent intentionally does NOT wait yet
        print(f"[parent] child PID={pid} has exited.")
        print(f"[parent] sleeping 1s WITHOUT calling wait()...")
        print(f"[parent] During this window, child is a zombie (State: Z).")
        print(f"[parent] Run: cat /proc/{pid}/status  in another terminal to see it.")
        sys.stdout.flush()
        time.sleep(1)

        # Now reap the zombie
        _, status = os.waitpid(pid, 0)
        code = os.WEXITSTATUS(status)
        print(f"[parent] wait() called — zombie reaped. Exit code was {code}.")
        print(f"[parent] PID {pid} is no longer in the process table.")

# ── Summary table ─────────────────────────────────────────────────────────────

def print_summary():
    print("\n" + "=" * 60)
    print("SUMMARY: What was demonstrated")
    print("=" * 60)
    rows = [
        ("Demo 1", "fork() basics",        "Parent/child PID, fork return values"),
        ("Demo 2", "fork() + exec()",       "Child image replaced by /bin/ls"),
        ("Demo 3", "Fork bomb defuser",     "N children spawned & reaped safely"),
        ("Demo 4", "Zombie & reaping",      "1s zombie window, then wait() clears it"),
    ]
    fmt = "  {:<8} {:<25} {}"
    print(fmt.format("Section", "Concept", "Key observation"))
    print("  " + "-" * 56)
    for demo, concept, obs in rows:
        print(fmt.format(demo, concept, obs))
    print()
    print("Key syscalls covered:")
    print("  os.fork()      — duplicate the calling process")
    print("  os.execv()     — replace process image (exec family)")
    print("  os.wait()      — wait for any child, reap zombie")
    print("  os.waitpid()   — wait for specific child")
    print("  os._exit()     — exit without Python cleanup (safe in child)")
    print("  os.getpid()    — read PID from PCB")
    print("  os.getppid()   — read parent PID from PCB")

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    check_platform()

    demo_fork_basics()
    demo_fork_exec()
    demo_fork_bomb_defuser(n=5)
    demo_zombie()
    print_summary()
