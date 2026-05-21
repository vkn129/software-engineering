"""
practice.py — Day 2: Processes

5 exercises. Each has a TODO block.
Attempt each exercise yourself, then scroll to # === SOLUTIONS === to compare.

Linux only. Skips cleanly on Windows/platforms without os.fork().
"""

import os
import sys
import time
import signal

# ── Platform guard ────────────────────────────────────────────────────────────

if not hasattr(os, "fork"):
    print("SKIP: os.fork() is not available on this platform (requires Linux/macOS).")
    sys.exit(0)

# ═════════════════════════════════════════════════════════════════════════════
# Exercise 1: Print PIDs across fork
# ─────────────────────────────────────────────────────────────────────────────
# Goal: fork once and print, from BOTH parent and child:
#   - Your own PID
#   - Your parent's PID
#   - The value fork() returned
#   - Whether you are the parent or child
#
# Expected output (order of lines may vary):
#   [parent] My PID=<A>, My PPID=<B>, fork() returned <C>
#   [child]  My PID=<C>, My PPID=<A>, fork() returned 0
# ─────────────────────────────────────────────────────────────────────────────

def exercise_1():
    print("\n--- Exercise 1: Print PIDs across fork ---")
    # TODO: implement here
    pass


# ═════════════════════════════════════════════════════════════════════════════
# Exercise 2: Implement system("cmd") using fork + exec + wait
# ─────────────────────────────────────────────────────────────────────────────
# Goal: write a function my_system(cmd) that behaves like the C standard
# library system() function:
#   - Forks a child
#   - Child execs ["/bin/sh", "-c", cmd]
#   - Parent waits for child and returns its exit code
#
# Test it by calling: my_system("echo hello from my_system && ls /tmp | head -3")
# ─────────────────────────────────────────────────────────────────────────────

def exercise_2():
    print("\n--- Exercise 2: my_system() using fork+exec+wait ---")

    def my_system(cmd: str) -> int:
        # TODO: implement here
        pass

    # Uncomment to test once implemented:
    # exit_code = my_system("echo hello from my_system && ls /tmp | head -3")
    # print(f"exit code: {exit_code}")


# ═════════════════════════════════════════════════════════════════════════════
# Exercise 3: Demonstrate a zombie process, then reap it
# ─────────────────────────────────────────────────────────────────────────────
# Goal:
#   1. Fork a child that exits immediately.
#   2. Parent sleeps 2 seconds WITHOUT calling wait() so child is a zombie.
#      Print a message telling the user to check /proc/<pid>/status.
#   3. Parent then calls wait() to reap the zombie and prints the exit code.
#
# While the parent sleeps, open another terminal and run:
#   cat /proc/<pid>/status | grep State
# You should see "State: Z (zombie)".
# ─────────────────────────────────────────────────────────────────────────────

def exercise_3():
    print("\n--- Exercise 3: Zombie creation and reaping ---")
    # TODO: implement here
    pass


# ═════════════════════════════════════════════════════════════════════════════
# Exercise 4: Process tree visualizer (3 levels deep)
# ─────────────────────────────────────────────────────────────────────────────
# Goal: build a 3-level process tree by forking recursively.
#
# Structure:
#   Root (depth=0) forks 2 children (depth=1)
#   Each depth-1 child forks 2 children (depth=2)
#   Each depth-2 child just prints itself and exits
#
# Each process should print:
#   [depth=<D>] PID=<P>, PPID=<PP>
#
# Root must reap all its direct children (which reap their children first).
# Hint: use a recursive function that takes the current depth.
#       When depth == max_depth, print and exit.
#       Otherwise, fork twice, wait for both children, then print self.
# ─────────────────────────────────────────────────────────────────────────────

def exercise_4():
    print("\n--- Exercise 4: 3-level process tree ---")

    MAX_DEPTH = 2
    BRANCH = 2   # children per node

    def build_tree(depth: int):
        # TODO: implement here
        pass

    build_tree(0)
    print("[root] tree complete")


# ═════════════════════════════════════════════════════════════════════════════
# Exercise 5: Process group — put children in a group, signal them all
# ─────────────────────────────────────────────────────────────────────────────
# Goal: demonstrate os.setpgid() and os.killpg().
#
#   1. Fork 3 children.
#   2. Each child calls os.setpgid(0, 0) to create its own process group
#      (group ID = its own PID). Actually, put ALL children in a single
#      shared group: use the PID of the FIRST child as the PGID for all.
#      Hint: pass the first child's PID to the other children via a shared
#      variable before forking them.
#   3. Children install a SIGTERM handler that prints "PID=<pid> got SIGTERM"
#      and exits cleanly.
#   4. Parent sleeps 0.5s, then sends SIGTERM to the entire process group
#      using os.killpg(pgid, signal.SIGTERM).
#   5. Parent reaps all children and prints exit codes.
#
# Key syscalls:
#   os.setpgid(pid, pgid) — set process group of pid to pgid
#   os.killpg(pgid, sig)  — send sig to all processes in group pgid
# ─────────────────────────────────────────────────────────────────────────────

def exercise_5():
    print("\n--- Exercise 5: Process groups and killpg ---")
    # TODO: implement here
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Uncomment any exercise to run it. All exercises are independent.
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # exercise_1()
    # exercise_2()
    # exercise_3()
    # exercise_4()
    # exercise_5()
    print("Uncomment the exercise you want to run in __main__.")
    print("Then scroll down to # === SOLUTIONS === to compare your answer.")


# =============================================================================
# === SOLUTIONS ===
# =============================================================================

# ── Solution 1 ────────────────────────────────────────────────────────────────

def solution_1():
    print("\n--- Solution 1: Print PIDs across fork ---")

    pid = os.fork()

    if pid == 0:
        # We are the child; fork() returned 0 to us
        print(f"[child]  My PID={os.getpid()}, My PPID={os.getppid()}, fork() returned {pid}")
        sys.stdout.flush()
        os._exit(0)
    else:
        # We are the parent; fork() returned child PID to us
        print(f"[parent] My PID={os.getpid()}, My PPID={os.getppid()}, fork() returned {pid}")
        os.waitpid(pid, 0)  # reap child

# ── Solution 2 ────────────────────────────────────────────────────────────────

def solution_2():
    print("\n--- Solution 2: my_system() using fork+exec+wait ---")

    def my_system(cmd: str) -> int:
        """
        Equivalent to C's system(3): runs cmd via /bin/sh -c.
        Returns the shell's exit code (0 = success).
        """
        pid = os.fork()

        if pid == 0:
            # Child: exec the shell with the command
            sys.stdout.flush()
            os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
            # execv only returns on error
            os._exit(127)   # 127 is the conventional "command not found" code

        # Parent: wait for child
        _, status = os.waitpid(pid, 0)
        # WIFEXITED checks normal exit; WEXITSTATUS extracts the code
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        # If killed by signal, return 128 + signal number (shell convention)
        if os.WIFSIGNALED(status):
            return 128 + os.WTERMSIG(status)
        return -1

    result = my_system("echo hello from my_system && ls /tmp | head -3")
    print(f"exit code: {result}")

# ── Solution 3 ────────────────────────────────────────────────────────────────

def solution_3():
    print("\n--- Solution 3: Zombie creation and reaping ---")

    pid = os.fork()

    if pid == 0:
        # Child exits immediately with a recognisable code
        print(f"[child]  PID={os.getpid()} exiting now")
        sys.stdout.flush()
        os._exit(77)

    # Parent: do NOT call wait() yet — child is now a zombie
    print(f"[parent] child PID={pid} has exited. Sleeping 2s WITHOUT wait().")
    print(f"[parent] In another terminal: cat /proc/{pid}/status | grep State")
    print(f"[parent] You should see 'State: Z (zombie)'")
    sys.stdout.flush()
    time.sleep(2)

    # Now reap: zombie entry removed from process table
    _, status = os.waitpid(pid, 0)
    code = os.WEXITSTATUS(status)
    print(f"[parent] Zombie reaped. Exit code={code}. PID {pid} is gone.")

# ── Solution 4 ────────────────────────────────────────────────────────────────

def solution_4():
    print("\n--- Solution 4: 3-level process tree ---")

    MAX_DEPTH = 2
    BRANCH = 2

    def build_tree(depth: int):
        if depth == MAX_DEPTH:
            # Leaf: just announce ourselves and exit
            print(f"  [depth={depth}] PID={os.getpid()}, PPID={os.getppid()} (leaf)")
            sys.stdout.flush()
            os._exit(0)

        # Internal node: fork BRANCH children, wait for each
        children = []
        for _ in range(BRANCH):
            pid = os.fork()
            if pid == 0:
                # We are a child — recurse deeper
                build_tree(depth + 1)
                os._exit(0)   # safety exit (build_tree exits at leaves)
            children.append(pid)

        # Wait for all children before printing ourselves
        for child_pid in children:
            os.waitpid(child_pid, 0)

        print(f"  [depth={depth}] PID={os.getpid()}, PPID={os.getppid()}")
        sys.stdout.flush()

    build_tree(0)
    print("[root] process tree complete")

# ── Solution 5 ────────────────────────────────────────────────────────────────

def solution_5():
    print("\n--- Solution 5: Process groups and killpg ---")

    N = 3
    child_pids = []
    pgid = None  # will be set to first child's PID

    for i in range(N):
        pid = os.fork()

        if pid == 0:
            # Determine our process group ID:
            # First child creates a new group (PGID = own PID).
            # Subsequent children join that group.
            # The parent passes pgid via the variable — but since we fork
            # sequentially, the child inherits the pgid value at fork time.
            my_pgid = pgid if pgid is not None else os.getpid()
            os.setpgid(0, my_pgid)   # 0 means "this process"

            # Install SIGTERM handler
            def on_sigterm(signum, frame):
                print(f"  [child {i}] PID={os.getpid()} got SIGTERM, exiting")
                sys.stdout.flush()
                os._exit(0)

            signal.signal(signal.SIGTERM, on_sigterm)

            # Wait to be signalled
            print(f"  [child {i}] PID={os.getpid()}, PGID={os.getpgrp()}, waiting...")
            sys.stdout.flush()
            # sleep longer than parent's 0.5s signal delay
            time.sleep(5)
            # If we reach here, signal was not received (shouldn't happen)
            os._exit(1)

        # Parent side: record PID, set pgid for subsequent children
        child_pids.append(pid)
        if pgid is None:
            pgid = pid          # first child's PID becomes the group ID
            # Also move first child into the group immediately
            # (race-free: parent sets it before forking next child)
            try:
                os.setpgid(pid, pgid)
            except ProcessLookupError:
                pass  # child already called setpgid itself — that is fine

    print(f"[parent] spawned {N} children in PGID={pgid}")
    print(f"[parent] sleeping 0.5s, then sending SIGTERM to group...")
    sys.stdout.flush()
    time.sleep(0.5)

    # Signal the entire process group
    os.killpg(pgid, signal.SIGTERM)

    # Reap all children
    for child_pid in child_pids:
        _, status = os.waitpid(child_pid, 0)
        code = os.WEXITSTATUS(status)
        print(f"[parent] reaped PID={child_pid}, exit_code={code}")

    print("[parent] all children signalled and reaped")
