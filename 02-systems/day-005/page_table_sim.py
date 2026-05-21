"""
page_table_sim.py — 2-level page table simulator for a 32-bit address space.

Address layout (32 bits, 4 KB pages):
  [ 10 bits: L1 index | 10 bits: L2 index | 12 bits: page offset ]

Physical memory is a fixed number of frames.  When all frames are occupied and
a fault occurs, one frame is evicted according to the chosen replacement policy.

Replacement policies implemented:
  - FIFO  : evict the frame that has been in memory the longest
  - LRU   : evict the least-recently-used frame
  - Clock : second-chance approximation of LRU (used by Linux)
"""

import random
from collections import deque, OrderedDict


# ──────────────────────────────────────────────────────────────────────────────
# Constants for a 32-bit / 4 KB page address space
# ──────────────────────────────────────────────────────────────────────────────
PAGE_SIZE     = 4096          # 4 KB
L1_BITS       = 10            # top 10 bits → L1 directory index
L2_BITS       = 10            # next 10 bits → L2 table index
OFFSET_BITS   = 12            # bottom 12 bits → byte offset within page
L1_ENTRIES    = 1 << L1_BITS  # 1024
L2_ENTRIES    = 1 << L2_BITS  # 1024

def split_va(va: int):
    """Decompose a 32-bit virtual address into (l1_idx, l2_idx, offset)."""
    offset = va & 0xFFF
    l2_idx = (va >> OFFSET_BITS) & 0x3FF
    l1_idx = (va >> (OFFSET_BITS + L2_BITS)) & 0x3FF
    return l1_idx, l2_idx, offset


# ──────────────────────────────────────────────────────────────────────────────
# Page Table Entry and 2-level Page Table
# ──────────────────────────────────────────────────────────────────────────────
class PTE:
    """Page Table Entry — maps one virtual page to a physical frame."""
    __slots__ = ("present", "frame", "dirty", "referenced")

    def __init__(self):
        self.present    = False
        self.frame      = -1
        self.dirty      = False
        self.referenced = False   # used by Clock algorithm


class PageTable:
    """
    2-level page table for a single process.
    L1 directory → array of L2 tables (allocated lazily).
    L2 table     → array of PTEs.
    """
    def __init__(self):
        # L1 directory: list of (L2 table | None)
        self._l1: list = [None] * L1_ENTRIES

    def _ensure_l2(self, l1_idx: int) -> list:
        if self._l1[l1_idx] is None:
            self._l1[l1_idx] = [PTE() for _ in range(L2_ENTRIES)]
        return self._l1[l1_idx]

    def get_pte(self, l1_idx: int, l2_idx: int) -> PTE:
        l2 = self._ensure_l2(l1_idx)
        return l2[l2_idx]

    def translate(self, va: int):
        """
        Return (physical_address, pte) if page is present, else raise PageFault.
        Also sets the 'referenced' bit (for Clock) on a hit.
        """
        l1_idx, l2_idx, offset = split_va(va)
        pte = self.get_pte(l1_idx, l2_idx)
        if not pte.present:
            raise PageFault(va, pte)
        pte.referenced = True
        pa = (pte.frame << OFFSET_BITS) | offset
        return pa, pte

    def map_page(self, va: int, frame: int):
        """Install a mapping: virtual page containing va → physical frame."""
        l1_idx, l2_idx, _ = split_va(va)
        pte = self.get_pte(l1_idx, l2_idx)
        pte.present    = True
        pte.frame      = frame
        pte.referenced = True
        pte.dirty      = False

    def unmap_page(self, va: int):
        """Remove a mapping (called by eviction)."""
        l1_idx, l2_idx, _ = split_va(va)
        l2 = self._l1[l1_idx]
        if l2 is None:
            return
        pte = l2[l2_idx]
        pte.present    = False
        pte.frame      = -1
        pte.referenced = False

    def page_base(self, va: int) -> int:
        """Return the virtual page base address (zero offset) for va."""
        return va & ~0xFFF


class PageFault(Exception):
    def __init__(self, va: int, pte: PTE):
        self.va  = va
        self.pte = pte


# ──────────────────────────────────────────────────────────────────────────────
# Physical Frame Pool
# ──────────────────────────────────────────────────────────────────────────────
class FramePool:
    """Manages a fixed set of physical frames."""
    def __init__(self, num_frames: int):
        self._free: deque = deque(range(num_frames))
        self._total = num_frames

    def allocate(self):
        """Return a free frame number, or None if all frames are occupied."""
        if self._free:
            return self._free.popleft()
        return None

    def release(self, frame: int):
        self._free.append(frame)

    @property
    def total(self):
        return self._total


# ──────────────────────────────────────────────────────────────────────────────
# Replacement Policies
# ──────────────────────────────────────────────────────────────────────────────
class FIFOPolicy:
    """Evict the frame that has been resident the longest."""
    def __init__(self):
        self._order: deque = deque()          # (frame, vpage_base)
        self._resident: dict = {}             # frame → vpage_base

    def on_load(self, frame: int, vpage: int):
        self._order.append((frame, vpage))
        self._resident[frame] = vpage

    def on_access(self, frame: int):
        pass  # FIFO ignores subsequent accesses

    def evict(self):
        """Return (frame, vpage_base) of victim."""
        while True:
            frame, vpage = self._order.popleft()
            if self._resident.get(frame) == vpage:
                del self._resident[frame]
                return frame, vpage

    def remove(self, frame: int):
        """Called if a frame is explicitly freed (not needed here, but kept for API parity)."""
        self._resident.pop(frame, None)


class LRUPolicy:
    """Evict the least-recently-used frame using an OrderedDict."""
    def __init__(self):
        # frame → vpage_base, ordered from LRU (front) to MRU (back)
        self._od: OrderedDict = OrderedDict()

    def on_load(self, frame: int, vpage: int):
        self._od[frame] = vpage
        self._od.move_to_end(frame)

    def on_access(self, frame: int):
        if frame in self._od:
            self._od.move_to_end(frame)

    def evict(self):
        frame, vpage = self._od.popitem(last=False)
        return frame, vpage

    def remove(self, frame: int):
        self._od.pop(frame, None)


class ClockPolicy:
    """
    Second-chance (Clock) algorithm.
    Maintains a circular list of (frame, vpage) tuples and a hand pointer.
    On eviction, if the referenced bit is set → clear it, advance; else evict.
    The referenced bit lives in the PTE; we read it through a callback.
    """
    def __init__(self, get_pte_fn):
        """
        get_pte_fn(vpage_base) → PTE  (so we can read/clear referenced bits)
        """
        self._get_pte = get_pte_fn
        self._slots: list = []    # list of [frame, vpage_base]
        self._hand  = 0

    def on_load(self, frame: int, vpage: int):
        self._slots.append([frame, vpage])

    def on_access(self, frame: int):
        pass  # referenced bit is set by PageTable.translate

    def evict(self):
        """Sweep the clock hand until we find a frame with referenced=False."""
        n = len(self._slots)
        if n == 0:
            raise RuntimeError("No frames to evict")

        while True:
            if self._hand >= n:
                self._hand = 0
            slot = self._slots[self._hand]
            frame, vpage = slot
            pte = self._get_pte(vpage)
            if pte.referenced:
                pte.referenced = False           # give a second chance
                self._hand += 1
            else:
                # evict this slot
                self._slots.pop(self._hand)
                if self._hand >= len(self._slots):
                    self._hand = 0
                return frame, vpage

    def remove(self, frame: int):
        self._slots = [s for s in self._slots if s[0] != frame]
        if self._hand >= len(self._slots):
            self._hand = 0


# ──────────────────────────────────────────────────────────────────────────────
# Demand-Paging Memory Manager
# ──────────────────────────────────────────────────────────────────────────────
class MemoryManager:
    """
    Simulates demand paging for a single process.
    Handles page faults by allocating or evicting frames according to a policy.
    """
    def __init__(self, num_frames: int, policy: str = "lru"):
        self.page_table  = PageTable()
        self.frames      = FramePool(num_frames)
        self.num_frames  = num_frames

        # Statistics
        self.accesses    = 0
        self.faults      = 0      # total faults (minor + major)
        self.major_faults= 0      # faults requiring "disk I/O" (page not in memory)
        self.evictions   = 0

        # frame → vpage_base (reverse map for eviction)
        self._frame_to_vpage: dict = {}

        policy = policy.lower()
        if policy == "fifo":
            self._policy = FIFOPolicy()
        elif policy == "lru":
            self._policy = LRUPolicy()
        elif policy == "clock":
            self._policy = ClockPolicy(self._get_pte_for_vpage)
        else:
            raise ValueError(f"Unknown policy: {policy!r}")

    def _get_pte_for_vpage(self, vpage_base: int) -> PTE:
        l1_idx, l2_idx, _ = split_va(vpage_base)
        return self.page_table.get_pte(l1_idx, l2_idx)

    def access(self, va: int, write: bool = False):
        """Simulate a memory access.  Handles faults transparently."""
        self.accesses += 1
        try:
            pa, pte = self.page_table.translate(va)
            # TLB hit simulation: inform policy of access
            self._policy.on_access(pte.frame)
            if write:
                pte.dirty = True
            return pa
        except PageFault as fault:
            return self._handle_fault(fault.va, write)

    def _handle_fault(self, va: int, write: bool) -> int:
        self.faults      += 1
        self.major_faults += 1   # in this simulation every fault is "major"

        vpage_base = self.page_table.page_base(va)

        # Try to get a free frame first
        frame = self.frames.allocate()
        if frame is None:
            # All frames occupied — must evict
            frame, evicted_vpage = self._policy.evict()
            self.page_table.unmap_page(evicted_vpage)
            self._frame_to_vpage.pop(frame, None)
            self.evictions += 1

        # Map the new page
        self.page_table.map_page(va, frame)
        self._frame_to_vpage[frame] = vpage_base
        self._policy.on_load(frame, vpage_base)

        pte = self._get_pte_for_vpage(vpage_base)
        if write:
            pte.dirty = True

        offset = va & 0xFFF
        return (frame << OFFSET_BITS) | offset

    def miss_rate(self) -> float:
        return self.faults / self.accesses if self.accesses else 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Workload generators
# ──────────────────────────────────────────────────────────────────────────────
def sequential_trace(n_pages: int, passes: int = 2) -> list:
    """Scan all pages sequentially, multiple times."""
    trace = []
    for _ in range(passes):
        for p in range(n_pages):
            trace.append(p * PAGE_SIZE)
    return trace


def random_trace(n_pages: int, n_accesses: int) -> list:
    """Uniformly random accesses across n_pages."""
    return [random.randint(0, n_pages - 1) * PAGE_SIZE for _ in range(n_accesses)]


def locality_trace(n_pages: int, n_accesses: int, hotset_ratio: float = 0.2) -> list:
    """80/20 locality: 80% of accesses go to hotset_ratio of pages."""
    hot_pages = max(1, int(n_pages * hotset_ratio))
    trace = []
    for _ in range(n_accesses):
        if random.random() < 0.8:
            p = random.randint(0, hot_pages - 1)
        else:
            p = random.randint(0, n_pages - 1)
        trace.append(p * PAGE_SIZE)
    return trace


def strided_trace(n_pages: int, stride: int, n_accesses: int) -> list:
    """Access pages with a fixed stride (cache-unfriendly pattern)."""
    trace = []
    p = 0
    for _ in range(n_accesses):
        trace.append((p % n_pages) * PAGE_SIZE)
        p += stride
    return trace


# ──────────────────────────────────────────────────────────────────────────────
# Simulation runner
# ──────────────────────────────────────────────────────────────────────────────
def run_simulation(trace: list, num_frames: int, policy: str) -> dict:
    mm = MemoryManager(num_frames, policy)
    for va in trace:
        mm.access(va)
    return {
        "policy":      policy.upper(),
        "frames":      num_frames,
        "accesses":    mm.accesses,
        "faults":      mm.faults,
        "evictions":   mm.evictions,
        "miss_rate":   mm.miss_rate(),
    }


def compare_policies(trace: list, num_frames: int, label: str):
    print(f"\n{'─'*60}")
    print(f"Workload : {label}")
    print(f"Frames   : {num_frames}   |   Trace length: {len(trace)}")
    print(f"{'─'*60}")
    print(f"{'Policy':<8}  {'Faults':>8}  {'Evictions':>10}  {'Miss Rate':>10}")
    print(f"{'─'*8}  {'─'*8}  {'─'*10}  {'─'*10}")
    for policy in ("fifo", "lru", "clock"):
        r = run_simulation(trace, num_frames, policy)
        print(f"{r['policy']:<8}  {r['faults']:>8}  {r['evictions']:>10}  {r['miss_rate']:>9.1%}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Belady's anomaly demonstration (FIFO only)
# ──────────────────────────────────────────────────────────────────────────────
def beladys_anomaly_demo():
    """
    Classic sequence that exhibits Belady's anomaly with FIFO:
    3, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0, 4
    3 frames → 9 faults, 4 frames → 10 faults (more frames = more faults!)
    """
    reference_string = [3, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0, 4]
    trace = [p * PAGE_SIZE for p in reference_string]

    print(f"\n{'─'*60}")
    print("Belady's Anomaly (FIFO)")
    print(f"Reference string: {reference_string}")
    print(f"{'─'*60}")
    print(f"{'Frames':>8}  {'FIFO Faults':>12}")
    print(f"{'─'*8}  {'─'*12}")
    for nf in range(1, 7):
        r = run_simulation(trace, nf, "fifo")
        anomaly = " ← MORE faults with more frames!" if nf == 4 else ""
        print(f"{nf:>8}  {r['faults']:>12}{anomaly}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Main: run all experiments and print a comparison table
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    random.seed(42)

    N_PAGES  = 20    # virtual pages available (only PAGE_SIZE apart)
    N_FRAMES = 8     # physical frames (less than N_PAGES to force evictions)
    N_ACC    = 200   # accesses per trace

    print("=" * 60)
    print("Virtual Memory & Paging — Replacement Policy Comparison")
    print("=" * 60)
    print(f"Virtual pages : {N_PAGES}")
    print(f"Physical frames: {N_FRAMES}")
    print(f"Page size      : {PAGE_SIZE} bytes")

    # ── Workload 1: Sequential scan (bad for FIFO/LRU, mediocre for Clock) ──
    compare_policies(
        sequential_trace(N_PAGES, passes=3),
        N_FRAMES,
        "Sequential scan (3 passes over 20 pages)",
    )

    # ── Workload 2: Pure random (all policies roughly equal) ──
    compare_policies(
        random_trace(N_PAGES, N_ACC),
        N_FRAMES,
        "Uniform random accesses",
    )

    # ── Workload 3: 80/20 locality (LRU and Clock win) ──
    compare_policies(
        locality_trace(N_PAGES, N_ACC, hotset_ratio=0.25),
        N_FRAMES,
        "80/20 locality (25% hot pages)",
    )

    # ── Workload 4: Strided access (defeats LRU, Clock does better) ──
    compare_policies(
        strided_trace(N_PAGES, stride=3, n_accesses=N_ACC),
        N_FRAMES,
        "Strided access (stride=3)",
    )

    # ── Belady's anomaly ──
    beladys_anomaly_demo()

    # ── Quick TLB-size intuition ──
    print("─" * 60)
    print("TLB Coverage Intuition")
    print("─" * 60)
    for tlb_entries in (64, 256, 1024, 4096):
        coverage_4k  = tlb_entries * 4096
        coverage_2m  = tlb_entries * 2 * 1024 * 1024
        print(
            f"  {tlb_entries:>5} TLB entries: "
            f"{coverage_4k / (1024**2):>6.1f} MB (4K pages)  |  "
            f"{coverage_2m / (1024**3):>5.1f} GB (2M huge pages)"
        )
    print()
    print("Observation: huge pages give 512x more coverage per TLB entry.")
    print("That is why databases and JVMs use them for large working sets.")
