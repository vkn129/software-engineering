"""
practice.py — Thread exercises with solutions

Five exercises covering the core threading primitives.
Try each TODO yourself, then compare with the solution section.

Run:  python practice.py
"""

import threading
import queue
import time
import random


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Producer-Consumer with queue.Queue
# ─────────────────────────────────────────────────────────────────────────────
# queue.Queue is a thread-safe FIFO queue built on threading.Lock and
# threading.Condition internally. You do not need a lock of your own.
#
# Pattern: producers put() items, consumers get() items. A sentinel value
# (None here) signals consumers to stop. queue.Queue blocks on get() when
# empty and on put() when full — no busy-waiting needed.

def exercise_1():
    print("\n[Exercise 1] Producer-Consumer with queue.Queue")

    # TODO: Implement two producers and three consumers.
    # Producers should each produce 5 items (just integers).
    # Consumers should print each item they consume and exit when they see None.
    # Use a bounded queue (maxsize=3) to observe backpressure.
    # Signal consumers to stop with one None sentinel per consumer.

    pass  # replace with your implementation

    # ── Solution is at the bottom of the file ──


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Thread-Safe Singleton with Double-Checked Locking
# ─────────────────────────────────────────────────────────────────────────────
# Double-Checked Locking (DCL) attempts to avoid acquiring the lock on every
# call by checking _instance first (fast path), and only locking if it is None.
#
# Why DCL is fragile in languages without a strong memory model:
#   Without memory barriers, the CPU or compiler may reorder the writes inside
#   the constructor so that another thread sees a non-None _instance pointer
#   BEFORE the object's fields are fully initialized. The second thread skips
#   the lock (because _instance is not None) and uses a partially-constructed
#   object. This is a classic Java pre-1.5 bug.
#
# In Python, DCL is safe because:
#   (a) The GIL prevents true simultaneous bytecode execution.
#   (b) The GIL acts as a memory barrier on acquisition/release.
# But you should still use a lock because CPython's GIL behavior is an
# implementation detail, not a language guarantee.

class SingletonTODO:
    """TODO: make this thread-safe using double-checked locking."""
    _instance = None

    @classmethod
    def get_instance(cls):
        # TODO: implement DCL here
        # 1. Check _instance without the lock (fast path)
        # 2. If None, acquire the lock
        # 3. Check again inside the lock (in case another thread beat you)
        # 4. If still None, create the instance
        # 5. Return _instance
        pass


def exercise_2():
    print("\n[Exercise 2] Thread-Safe Singleton (Double-Checked Locking)")

    # TODO: Spawn 10 threads, each calling SingletonTODO.get_instance().
    # Verify all threads receive the same object (same id()).
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Demonstrate a Deadlock
# ─────────────────────────────────────────────────────────────────────────────
# Deadlock occurs when:
#   Thread A holds Lock 1, waits for Lock 2
#   Thread B holds Lock 2, waits for Lock 1
# Neither can proceed. The program hangs.
#
# Fix: always acquire locks in the same order. If every thread acquires
# Lock 1 before Lock 2, no circular wait is possible.
# Alternative fix: use a timeout on acquire() and retry or abort.

def exercise_3():
    print("\n[Exercise 3] Deadlock with Two Locks")

    lock_a = threading.Lock()
    lock_b = threading.Lock()

    # TODO: Write two functions that deadlock when run concurrently.
    # task_1: acquire lock_a, sleep briefly, then try to acquire lock_b
    # task_2: acquire lock_b, sleep briefly, then try to acquire lock_a
    # Run them as threads and observe the hang (use a timeout to detect it).
    # Then fix the deadlock by changing the lock acquisition order.

    # Hint for detection: use lock.acquire(timeout=2.0) which returns False
    # if it cannot acquire within 2 seconds — this lets you detect a deadlock
    # without hanging forever.

    pass


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 4: threading.Event for Signaling
# ─────────────────────────────────────────────────────────────────────────────
# threading.Event is a simple flag with built-in waiting.
# event.wait() blocks until event.set() is called.
# event.clear() resets it so wait() will block again.
# event.is_set() checks without blocking.
#
# Use case: one thread signals another that something is ready.
# Cleaner than busy-polling (while not ready: sleep(0.01)) because
# wait() uses a Condition variable internally — no CPU wasted.

def exercise_4():
    print("\n[Exercise 4] threading.Event for Signaling")

    # TODO: Implement a "ready" event pattern.
    # - A "loader" thread does slow work (sleep 1s) then sets an event.
    # - A "processor" thread waits on the event, then does its work.
    # - A "monitor" thread prints "still waiting..." every 0.3s until the event fires.
    # All three run concurrently. Use threading.Event to coordinate.

    pass


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 5: threading.local — Per-Thread State
# ─────────────────────────────────────────────────────────────────────────────
# threading.local() creates an object whose attributes are per-thread.
# Thread A setting local.x = 1 does not affect Thread B's local.x.
#
# Use cases: per-request database connections in a web server, per-thread
# random number generators, per-thread logging context.
#
# Misconception: threading.local does NOT protect shared objects — it gives
# each thread its own COPY. If the attribute itself is a shared mutable object
# (e.g., a global list), pointing local.data at it does not protect it.

local_storage = threading.local()


def exercise_5():
    print("\n[Exercise 5] threading.local — Per-Thread State")

    # TODO: Spawn 5 threads. Each thread should:
    # 1. Store its own random value in local_storage.value
    # 2. Sleep a random short duration (to interleave with other threads)
    # 3. Read back local_storage.value and verify it is still its own value
    # 4. Print "Thread {name}: stored {stored}, read back {readback}, match={match}"
    #
    # The point: even though threads interleave, each thread's local_storage.value
    # is independent — they cannot overwrite each other's value.

    pass


# ─────────────────────────────────────────────────────────────────────────────
# === SOLUTIONS ===
# ─────────────────────────────────────────────────────────────────────────────

def solution_1():
    print("\n[Solution 1] Producer-Consumer with queue.Queue")

    N_PRODUCERS = 2
    N_CONSUMERS = 3
    ITEMS_PER_PRODUCER = 5
    # Bounded queue: producers block when full, demonstrating backpressure
    q: queue.Queue = queue.Queue(maxsize=3)
    results = []
    lock = threading.Lock()

    def producer(pid: int) -> None:
        for i in range(ITEMS_PER_PRODUCER):
            item = pid * 100 + i
            q.put(item)  # blocks if queue is full (backpressure)
            print(f"  Producer {pid}: put {item}  (queue size ~{q.qsize()})")
            time.sleep(0.01)

    def consumer(cid: int) -> None:
        while True:
            item = q.get()  # blocks if queue is empty
            if item is None:
                print(f"  Consumer {cid}: received sentinel, stopping")
                q.task_done()
                break
            print(f"  Consumer {cid}: got {item}")
            with lock:
                results.append(item)
            q.task_done()
            time.sleep(0.02)  # consumers slightly slower to show backpressure

    producers = [threading.Thread(target=producer, args=(i,)) for i in range(N_PRODUCERS)]
    consumers = [threading.Thread(target=consumer, args=(i,)) for i in range(N_CONSUMERS)]

    for t in consumers:
        t.start()
    for t in producers:
        t.start()

    # Wait for all producers to finish
    for t in producers:
        t.join()

    # Send one sentinel per consumer to stop them
    for _ in range(N_CONSUMERS):
        q.put(None)

    for t in consumers:
        t.join()

    expected = N_PRODUCERS * ITEMS_PER_PRODUCER
    print(f"  Produced: {expected} items, consumed: {len(results)} items — match: {len(results) == expected}")


class SingletonSolution:
    """Thread-safe singleton using double-checked locking."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.created_by = threading.current_thread().name

    @classmethod
    def get_instance(cls):
        # Fast path: no lock needed if already initialized.
        # In Python this is safe because the GIL makes the attribute read atomic.
        if cls._instance is None:
            with cls._lock:
                # Slow path: re-check inside the lock.
                # Between our first check and acquiring the lock, another thread
                # may have already created the instance.
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


def solution_2():
    print("\n[Solution 2] Thread-Safe Singleton (Double-Checked Locking)")

    SingletonSolution._instance = None  # reset for demo
    ids = []
    id_lock = threading.Lock()

    def get_singleton():
        instance = SingletonSolution.get_instance()
        with id_lock:
            ids.append(id(instance))

    threads = [threading.Thread(target=get_singleton) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique_ids = set(ids)
    print(f"  10 threads got {len(unique_ids)} unique instance id(s) — all same: {len(unique_ids) == 1}")
    print(f"  Singleton created by: {SingletonSolution._instance.created_by}")
    print()
    print("  Why DCL is fragile in C++/Java without volatile/memory fences:")
    print("  The CPU may reorder 'write pointer' before 'initialize object'.")
    print("  Thread B sees non-None pointer but reads uninitialized fields.")
    print("  Fix in C++: use std::atomic with sequential consistency.")
    print("  Fix in Java: declare _instance as volatile (Java 5+).")
    print("  In Python: GIL makes DCL safe, but use a lock anyway for clarity.")


def solution_3():
    print("\n[Solution 3] Deadlock Detection and Fix")

    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()

    def task_deadlock_1():
        """Acquires A then tries B — will deadlock with task_deadlock_2."""
        with lock_a:
            print("  Thread 1: acquired lock_a, waiting for lock_b...")
            time.sleep(0.1)  # give Thread 2 time to grab lock_b
            acquired = lock_b.acquire(timeout=1.5)
            if not acquired:
                print("  Thread 1: DEADLOCK DETECTED — could not acquire lock_b")
                deadlock_detected.set()
            else:
                print("  Thread 1: acquired lock_b (unexpected — no deadlock?)")
                lock_b.release()

    def task_deadlock_2():
        """Acquires B then tries A — will deadlock with task_deadlock_1."""
        with lock_b:
            print("  Thread 2: acquired lock_b, waiting for lock_a...")
            time.sleep(0.1)
            acquired = lock_a.acquire(timeout=1.5)
            if not acquired:
                print("  Thread 2: DEADLOCK DETECTED — could not acquire lock_a")
                deadlock_detected.set()
            else:
                print("  Thread 2: acquired lock_a (unexpected — no deadlock?)")
                lock_a.release()

    print("  --- Deadlock scenario (different acquisition order) ---")
    t1 = threading.Thread(target=task_deadlock_1, name="Thread-1")
    t2 = threading.Thread(target=task_deadlock_2, name="Thread-2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"  Deadlock detected: {deadlock_detected.is_set()}")

    # Fix: always acquire locks in the same canonical order (e.g., by id)
    lock_a2 = threading.Lock()
    lock_b2 = threading.Lock()
    # Establish a total order: always acquire the lock with the lower id() first
    ordered = sorted([lock_a2, lock_b2], key=id)

    def task_fixed():
        """Both threads acquire locks in the same order — no deadlock possible."""
        with ordered[0]:
            time.sleep(0.05)
            with ordered[1]:
                pass  # both locks held safely

    print()
    print("  --- Fixed scenario (same acquisition order for all threads) ---")
    threads = [threading.Thread(target=task_fixed) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("  Both threads completed without deadlock.")


def solution_4():
    print("\n[Solution 4] threading.Event for Signaling")

    ready_event = threading.Event()
    stop_monitor = threading.Event()

    def loader():
        print("  Loader: starting slow work...")
        time.sleep(1.0)  # simulate slow initialization
        print("  Loader: work complete, setting ready event")
        ready_event.set()

    def processor():
        print("  Processor: waiting for ready signal...")
        ready_event.wait()  # blocks here until loader calls set()
        stop_monitor.set()  # tell monitor to stop
        print("  Processor: ready! doing processing work now")

    def monitor():
        while not stop_monitor.wait(timeout=0.3):
            # wait() returns False on timeout, True when event is set
            print("  Monitor: still waiting for ready...")
        print("  Monitor: done (ready event fired)")

    threads = [
        threading.Thread(target=loader, name="loader"),
        threading.Thread(target=processor, name="processor"),
        threading.Thread(target=monitor, name="monitor"),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def solution_5():
    print("\n[Solution 5] threading.local — Per-Thread State")

    thread_local = threading.local()

    def thread_worker(name: str) -> None:
        # Each thread sets its own .value — other threads cannot see this
        my_value = random.randint(1000, 9999)
        thread_local.value = my_value

        # Simulate interleaving: yield to other threads
        time.sleep(random.uniform(0.01, 0.05))

        # Read back — must still be our value, not modified by another thread
        readback = thread_local.value
        match = readback == my_value
        print(f"  Thread {name}: stored {my_value}, read back {readback}, match={match}")

    threads = [
        threading.Thread(target=thread_worker, args=(str(i),), name=f"T{i}")
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print()
    print("  Key insight: thread_local.value does not exist in the main thread")
    print("  (each thread has its own namespace for threading.local attributes)")
    try:
        _ = thread_local.value
        print("  Main thread: value =", _)
    except AttributeError:
        print("  Main thread: AttributeError — thread_local.value not set here")

    print()
    print("  When threading.local is NOT enough:")
    print("  If local.data = some_shared_list, you haven't protected the list —")
    print("  you've just stored a reference to it. Mutating the list is still")
    print("  a race condition. threading.local protects the binding, not the object.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("PRACTICE: Thread Primitives — Solutions")
    print("=" * 65)
    print("(Running solution implementations directly)")

    solution_1()
    solution_2()
    solution_3()
    solution_4()
    solution_5()

    print()
    print("=" * 65)
    print("Done. Study the TODO sections above, implement them yourself,")
    print("then compare your output to the solutions.")
    print("=" * 65)


if __name__ == "__main__":
    main()
