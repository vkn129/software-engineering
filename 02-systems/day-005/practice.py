"""
practice.py — Day 5: Virtual Memory & Paging
Five exercises with TODOs.  Work through each TODO, then check the solutions
below the === SOLUTIONS === marker.

Run with: python practice.py
"""

from collections import OrderedDict
import sys

print("=" * 62)
print("Day 5 Practice — Virtual Memory & Paging")
print("=" * 62)


# ──────────────────────────────────────────────────────────────────
# Exercise 1: Why single-level page tables fail on 64-bit systems
# ──────────────────────────────────────────────────────────────────
print("\n── Exercise 1: Single-level page table size ──")
print("""
A 64-bit CPU uses 48-bit virtual addresses (x86-64 canonical form).
Pages are 4 KB (2^12 bytes).  Each page table entry (PTE) is 8 bytes.

TODO 1a: Compute the number of virtual pages in a 48-bit address space.
TODO 1b: Compute the total size in bytes of a single-level page table.
TODO 1c: Convert to GB and explain why this is untenable per-process.
TODO 1d: How does x86-64's 4-level table fix this? Estimate the memory
         needed for a process that only uses 1 MB of virtual space.
""")

# ── your work here ──
num_virtual_pages_48bit = None     # TODO 1a
page_table_bytes        = None     # TODO 1b
page_table_gb           = None     # TODO 1c

print("[your answers here]")


# ──────────────────────────────────────────────────────────────────
# Exercise 2: LRU cache using OrderedDict
# ──────────────────────────────────────────────────────────────────
print("\n── Exercise 2: LRU page replacement with OrderedDict ──")
print("""
Implement LRUCache with:
  - get(key)       → return value or -1 if not present; mark as recently used
  - put(key, value)→ insert/update; evict LRU entry if over capacity

This is the canonical data-structure interview problem, but here we
use it to understand how OS LRU page eviction would work logically.
""")

class LRUCache:
    def __init__(self, capacity: int):
        # TODO: store capacity and ordered data structure
        pass

    def get(self, key: int) -> int:
        # TODO: return value if present, move to MRU position; else -1
        pass

    def put(self, key: int, value: int):
        # TODO: insert/update; move to MRU; evict LRU if over capacity
        pass


# Smoke test (do not modify)
def test_lru(cls):
    c = cls(3)
    c.put(1, 10); c.put(2, 20); c.put(3, 30)
    assert c.get(1) == 10,   "get existing"
    c.put(4, 40)             # should evict key 2 (LRU after get(1))
    assert c.get(2) == -1,   "evicted key should return -1"
    assert c.get(3) == 30,   "non-evicted key still present"
    assert c.get(4) == 40,   "newly inserted key present"
    c.put(5, 50)             # should evict key 1 (LRU now)
    assert c.get(1) == -1,   "key 1 should now be evicted"
    print("  LRU tests passed!")

try:
    test_lru(LRUCache)
except Exception as e:
    print(f"  LRU test failed (expected until you implement it): {e}")


# ──────────────────────────────────────────────────────────────────
# Exercise 3: Belady's anomaly with FIFO
# ──────────────────────────────────────────────────────────────────
print("\n── Exercise 3: Belady's anomaly ──")
print("""
Reference string: 3 2 1 0 3 2 4 3 2 1 0 4

TODO: implement simulate_fifo(reference, num_frames) -> fault_count
      using a plain list as the frame set.
      Then call it for num_frames = 1..6 and print the results.
      Identify where the anomaly occurs (more frames → more faults).
""")

def simulate_fifo(reference: list, num_frames: int) -> int:
    """
    TODO: simulate FIFO page replacement.
    - Maintain a list of currently resident pages (FIFO order).
    - On each access: if page not resident, increment fault count,
      add page; if frames full, remove the oldest (front of list).
    """
    fault_count = 0
    # TODO: implement
    return fault_count


reference_string = [3, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0, 4]
print(f"  Reference string: {reference_string}")
print(f"  {'Frames':>6}  {'FIFO Faults':>12}  {'Note':}")
for nf in range(1, 7):
    faults = simulate_fifo(reference_string, nf)
    print(f"  {nf:>6}  {faults:>12}  [your output]")


# ──────────────────────────────────────────────────────────────────
# Exercise 4: Copy-on-write fork simulator
# ──────────────────────────────────────────────────────────────────
print("\n── Exercise 4: Copy-on-write (COW) fork simulator ──")
print("""
Model a parent process with N pages.  fork() creates a child that shares
all parent pages read-only.  On the first write to a shared page, the OS
copies the frame and gives the writer its own private copy.

TODO: implement class COWProcess and fork() function so that:
  - After fork, parent and child share the same physical frame IDs.
  - A write by either process to a shared page triggers a copy
    (new_frame_id = max_frame_id + 1) for the writer only.
  - The other process still sees the original frame ID.
""")

class COWProcess:
    def __init__(self, name: str, pages: dict):
        """
        pages: dict mapping virtual_page → physical_frame_id
        shared: set of virtual pages that are copy-on-write shared
        """
        self.name   = name
        self.pages  = dict(pages)   # vpn → frame_id
        self.shared : set = set()   # vpns currently shared with another process

    def read(self, vpn: int) -> int:
        # TODO: return the physical frame id for vpn (no copy needed)
        pass

    def write(self, vpn: int, next_frame_id: int) -> int:
        """
        TODO: if vpn is shared, copy the frame:
          - assign next_frame_id to this process's mapping
          - remove vpn from self.shared (this copy is now private)
          - return next_frame_id  (caller increments its counter)
        If not shared, no copy needed; return the existing frame_id.
        """
        pass


def fork(parent: COWProcess, next_frame_id: int) -> COWProcess:
    """
    TODO: create child sharing all parent pages.
    - Child gets same page→frame mappings as parent.
    - Mark all current pages as shared in both parent and child.
    - Return the child COWProcess.
    """
    pass


# Smoke test
def test_cow():
    pages = {0: 10, 1: 11, 2: 12}
    parent = COWProcess("parent", pages)
    next_frame = [13]   # mutable counter

    child = fork(parent, next_frame[0])
    if child is None:
        print("  COW not implemented yet")
        return

    # Both should see same frames before any write
    assert parent.read(0) == 10
    assert child.read(0)  == 10

    # Parent writes to page 0 → gets a new frame; child still has 10
    new_frame = parent.write(0, next_frame[0])
    next_frame[0] += 1
    assert new_frame == 13,             f"expected frame 13, got {new_frame}"
    assert parent.pages[0] == 13,       "parent should have new frame"
    assert child.pages[0]  == 10,       "child still has original frame"
    assert 0 not in parent.shared,      "page 0 no longer shared in parent"

    # Child writes to page 1 → gets its own copy; parent still has 11
    new_frame = child.write(1, next_frame[0])
    next_frame[0] += 1
    assert new_frame == 14,             f"expected frame 14, got {new_frame}"
    assert child.pages[1]  == 14
    assert parent.pages[1] == 11

    print("  COW tests passed!")

try:
    test_cow()
except Exception as e:
    print(f"  COW test failed (expected until implemented): {e}")


# ──────────────────────────────────────────────────────────────────
# Exercise 5: Thrashing detector
# ──────────────────────────────────────────────────────────────────
print("\n── Exercise 5: Thrashing detection and reaction ──")
print("""
Given a stream of (timestamp, is_fault) events, detect thrashing:
  fault_rate = faults_in_window / window_size  > threshold

TODO: implement ThrashingDetector.record(timestamp, is_fault) that:
  - Maintains a sliding window of the last `window_size` events.
  - After each record(), computes the fault rate in the window.
  - If fault_rate > threshold: set self.thrashing = True and
    append timestamp to self.thrash_events.
  - If fault_rate <= threshold: set self.thrashing = False.

Then: react() prints recommended action (reduce multiprogramming).
""")

class ThrashingDetector:
    def __init__(self, window_size: int = 10, threshold: float = 0.7):
        self.window_size  = window_size
        self.threshold    = threshold
        self.thrashing    = False
        self.thrash_events: list = []
        # TODO: storage for recent events

    def record(self, timestamp: int, is_fault: bool):
        # TODO: add event to window, trim old events, compute fault rate
        pass

    def react(self):
        if self.thrashing:
            print("  [ThrashingDetector] THRASHING detected!")
            print("  → Recommended action: suspend lowest-priority process")
            print("  → Reduce degree of multiprogramming until fault rate drops")
        else:
            print("  [ThrashingDetector] System healthy.")


# Demo with a fabricated event stream
def test_thrashing():
    det = ThrashingDetector(window_size=10, threshold=0.6)
    # First 20 events: mostly hits
    for t in range(20):
        det.record(t, is_fault=(t % 5 == 0))

    healthy_state = not det.thrashing
    det.react()

    # Next 20 events: heavy faults (simulating thrashing)
    for t in range(20, 40):
        det.record(t, is_fault=(t % 10 != 0))  # 90% fault rate

    det.react()
    print(f"  Thrash events recorded: {len(det.thrash_events)}")

try:
    test_thrashing()
except Exception as e:
    print(f"  Thrashing test error (expected until implemented): {e}")


# ══════════════════════════════════════════════════════════════════
# === SOLUTIONS ===
# ══════════════════════════════════════════════════════════════════

print("\n\n" + "=" * 62)
print("SOLUTIONS")
print("=" * 62)


# ── Solution 1 ────────────────────────────────────────────────────
print("\n── Solution 1: Single-level page table size ──")

VADDR_BITS   = 48
PAGE_BITS    = 12
PTE_SIZE     = 8  # bytes on 64-bit

num_vpages    = 2 ** (VADDR_BITS - PAGE_BITS)          # 2^36
table_bytes   = num_vpages * PTE_SIZE                   # 2^36 * 8 = 512 GB
table_gb      = table_bytes / (1024 ** 3)

print(f"  Virtual address bits : {VADDR_BITS}")
print(f"  Page size            : {2**PAGE_BITS} bytes (2^{PAGE_BITS})")
print(f"  Number of virtual pages: 2^{VADDR_BITS-PAGE_BITS} = {num_vpages:,}")
print(f"  PTE size             : {PTE_SIZE} bytes")
print(f"  Single-level table   : {num_vpages:,} × {PTE_SIZE} = {table_bytes:,} bytes = {table_gb:.0f} GB")
print()
print("  This is 512 GB *per process* — untenable.  x86-64 uses 4 levels:")
print("  PGD[9] → PUD[9] → PMD[9] → PTE[9] → offset[12]  (9+9+9+9+12 = 48)")
print()
print("  For a process using only 1 MB (256 pages = 1 L2 table):")
print("  Pages allocated: 1 PGD + 1 PUD + 1 PMD + 1 PTE table = 4 × 4KB = 16 KB")
print("  (vs 512 GB for the flat table)")


# ── Solution 2 ────────────────────────────────────────────────────
print("\n── Solution 2: LRU Cache (OrderedDict) ──")

class LRUCacheSolution:
    def __init__(self, capacity: int):
        self.cap  = capacity
        self._od  = OrderedDict()   # key → value, LRU at front, MRU at back

    def get(self, key: int) -> int:
        if key not in self._od:
            return -1
        self._od.move_to_end(key)   # mark as most recently used
        return self._od[key]

    def put(self, key: int, value: int):
        if key in self._od:
            self._od.move_to_end(key)
        self._od[key] = value
        if len(self._od) > self.cap:
            self._od.popitem(last=False)   # evict LRU (front)

test_lru(LRUCacheSolution)
print("  Key insight: move_to_end() on every access maintains MRU order.")
print("  OS LRU approximations (Clock) avoid the cost of this on every")
print("  memory access — true LRU would require a pointer update per access.")


# ── Solution 3 ────────────────────────────────────────────────────
print("\n── Solution 3: Belady's anomaly ──")

def simulate_fifo_solution(reference: list, num_frames: int) -> int:
    frames: list  = []          # FIFO queue (front = oldest)
    fault_count   = 0
    for page in reference:
        if page not in frames:
            fault_count += 1
            if len(frames) == num_frames:
                frames.pop(0)   # evict oldest
            frames.append(page)
    return fault_count

ref = [3, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0, 4]
print(f"  Reference: {ref}")
prev_faults = None
for nf in range(1, 7):
    f = simulate_fifo_solution(ref, nf)
    anomaly = ""
    if prev_faults is not None and f > prev_faults:
        anomaly = " ← BELADY'S ANOMALY (more frames, more faults!)"
    print(f"  {nf} frames → {f:2d} faults{anomaly}")
    prev_faults = f

print()
print("  Anomaly at 3→4 frames: 9 faults → 10 faults.")
print("  LRU and Clock do NOT exhibit Belady's anomaly because they belong")
print("  to the 'stack algorithm' family: the set of pages in memory for n+1")
print("  frames always contains the set for n frames.")


# ── Solution 4 ────────────────────────────────────────────────────
print("\n── Solution 4: Copy-on-write fork simulator ──")

class COWProcessSolution:
    def __init__(self, name: str, pages: dict):
        self.name   = name
        self.pages  = dict(pages)
        self.shared : set = set()

    def read(self, vpn: int) -> int:
        return self.pages[vpn]

    def write(self, vpn: int, next_frame_id: int) -> int:
        if vpn in self.shared:
            # Fault: copy the frame
            self.pages[vpn] = next_frame_id
            self.shared.discard(vpn)
            return next_frame_id
        # Private page — write in place, no copy
        return self.pages[vpn]


def fork_solution(parent: COWProcessSolution, next_frame_id: int) -> COWProcessSolution:
    child = COWProcessSolution(f"{parent.name}_child", parent.pages)
    # Mark all current pages shared in both
    all_pages = set(parent.pages.keys())
    parent.shared |= all_pages
    child.shared   = set(all_pages)
    return child

# Verify
pages  = {0: 10, 1: 11, 2: 12}
parent = COWProcessSolution("parent", pages)
nf     = [13]
child  = fork_solution(parent, nf[0])
assert parent.read(0) == child.read(0) == 10
new_f = parent.write(0, nf[0]); nf[0] += 1
assert new_f == 13 and child.read(0) == 10
new_f = child.write(1, nf[0]); nf[0] += 1
assert new_f == 14 and parent.read(1) == 11
print("  COW solution verified.")
print()
print("  fork() cost: O(pages) to mark shared — no frame copying.")
print("  Actual copy only happens on the first write (protection fault).")
print("  On Linux: vfork() goes further — child even shares the stack,")
print("  and the parent is suspended until exec() or _exit() is called.")


# ── Solution 5 ────────────────────────────────────────────────────
print("\n── Solution 5: Thrashing detector ──")

class ThrashingDetectorSolution:
    def __init__(self, window_size: int = 10, threshold: float = 0.7):
        self.window_size  = window_size
        self.threshold    = threshold
        self.thrashing    = False
        self.thrash_events: list = []
        self._window: list = []   # list of (timestamp, is_fault)

    def record(self, timestamp: int, is_fault: bool):
        self._window.append((timestamp, is_fault))
        # Trim to sliding window
        if len(self._window) > self.window_size:
            self._window.pop(0)
        fault_rate = sum(1 for _, f in self._window if f) / len(self._window)
        if fault_rate > self.threshold:
            if not self.thrashing:
                self.thrash_events.append(timestamp)
            self.thrashing = True
        else:
            self.thrashing = False

    def react(self):
        if self.thrashing:
            print("  [ThrashingDetector] THRASHING detected!")
            print("  → Suspend lowest-priority process to free frames")
        else:
            print("  [ThrashingDetector] System healthy.")

det2 = ThrashingDetectorSolution(window_size=10, threshold=0.6)
for t in range(20):
    det2.record(t, is_fault=(t % 5 == 0))
print(f"  After low-fault period (thrashing={det2.thrashing}):")
det2.react()

for t in range(20, 40):
    det2.record(t, is_fault=(t % 10 != 0))
print(f"  After high-fault period (thrashing={det2.thrashing}):")
det2.react()
print(f"  Thrash onset events: {det2.thrash_events}")
print()
print("  Real fix: Working Set Model — only keep processes whose working")
print("  sets fit in RAM.  Linux uses kswapd to reclaim pages under pressure")
print("  and the OOM killer as a last resort.")

print("\n" + "=" * 62)
print("All solutions complete.  Run page_table_sim.py for the full")
print("replacement-policy comparison and Belady's anomaly demo.")
print("=" * 62)
