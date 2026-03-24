"""
Day 28: Memory Allocator — Mini-project

Three allocators built from scratch:
  1. SimpleAllocator  — first-fit with splitting and coalescing
  2. BestFitAllocator — best-fit variant
  3. BuddyAllocator  — power-of-2 splitting with buddy merging

All operate on a simulated contiguous memory region (a list of Block objects).
No external libraries.
"""

import random


# ---------------------------------------------------------------------------
# Block: the fundamental unit of our simulated heap
# ---------------------------------------------------------------------------

class Block:
    """Represents a contiguous region of memory."""

    __slots__ = ("start", "size", "is_free")

    def __init__(self, start: int, size: int, is_free: bool = True):
        self.start = start
        self.size = size
        self.is_free = is_free

    def __repr__(self):
        state = "FREE" if self.is_free else "USED"
        return f"[{state} start={self.start} size={self.size}]"


# ---------------------------------------------------------------------------
# SimpleAllocator — first-fit, splitting, coalescing
# ---------------------------------------------------------------------------

class SimpleAllocator:
    """
    First-fit allocator.

    malloc: scan blocks left-to-right, pick the first free block >= requested size.
    free:   mark block as free, then coalesce with adjacent free neighbors.
    """

    MIN_SPLIT_REMAINDER = 4  # don't create fragments smaller than this

    def __init__(self, total_size: int):
        self.total_size = total_size
        # Start with one big free block
        self.blocks: list[Block] = [Block(start=0, size=total_size, is_free=True)]
        # Map from start address -> allocation name (for visualization)
        self.alloc_names: dict[int, str] = {}
        self._name_counter = 0

    # -- public API ---------------------------------------------------------

    def malloc(self, size: int, name: str | None = None) -> int | None:
        """Allocate *size* bytes.  Returns start address or None on failure."""
        if size <= 0:
            return None

        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return self._allocate_block(i, size, name)
        return None  # no suitable block

    def free(self, address: int) -> bool:
        """Free the block that starts at *address*.  Returns True on success."""
        for i, block in enumerate(self.blocks):
            if block.start == address and not block.is_free:
                block.is_free = True
                self.alloc_names.pop(address, None)
                self._coalesce(i)
                return True
        return False

    # -- internals ----------------------------------------------------------

    def _allocate_block(self, index: int, size: int, name: str | None) -> int:
        block = self.blocks[index]
        remainder = block.size - size

        if remainder >= self.MIN_SPLIT_REMAINDER:
            # Split: shrink current block, insert new free block after it
            new_free = Block(start=block.start + size, size=remainder, is_free=True)
            block.size = size
            self.blocks.insert(index + 1, new_free)

        block.is_free = False

        if name is None:
            self._name_counter += 1
            name = f"A{self._name_counter}"
        self.alloc_names[block.start] = name

        return block.start

    def _coalesce(self, index: int):
        """Merge block at *index* with adjacent free neighbors."""
        # Merge with next block first (so index stays valid for prev merge)
        while index + 1 < len(self.blocks) and self.blocks[index + 1].is_free:
            nxt = self.blocks.pop(index + 1)
            self.blocks[index].size += nxt.size

        # Merge with previous block
        while index > 0 and self.blocks[index - 1].is_free:
            prev = self.blocks[index - 1]
            cur = self.blocks.pop(index)
            prev.size += cur.size
            index -= 1

    # -- diagnostics --------------------------------------------------------

    def memory_map(self, width: int = 60) -> str:
        """Return an ASCII visualization of memory."""
        lines = []
        bar = []
        for block in self.blocks:
            # Number of chars proportional to block size
            chars = max(1, round(block.size / self.total_size * width))
            if block.is_free:
                bar.append("." * chars)
            else:
                label = self.alloc_names.get(block.start, "?")
                segment = label * chars
                bar.append(segment[:chars])
        lines.append("|" + "".join(bar)[:width].ljust(width) + "|")

        # Block details
        for block in self.blocks:
            state = "FREE" if block.is_free else f"USED ({self.alloc_names.get(block.start, '?')})"
            lines.append(f"  @{block.start:>5}  size={block.size:<6} {state}")

        return "\n".join(lines)

    def fragmentation_metrics(self) -> dict:
        """Compute fragmentation statistics."""
        free_blocks = [b for b in self.blocks if b.is_free]
        used_blocks = [b for b in self.blocks if not b.is_free]

        total_free = sum(b.size for b in free_blocks)
        largest_free = max((b.size for b in free_blocks), default=0)
        total_used = sum(b.size for b in used_blocks)

        # External fragmentation: 1 - (largest_free / total_free)
        # 0 = no fragmentation (all free memory in one block)
        # 1 = fully fragmented (free memory in many tiny pieces)
        if total_free > 0:
            external_frag = 1.0 - (largest_free / total_free)
        else:
            external_frag = 0.0

        return {
            "total_size": self.total_size,
            "total_used": total_used,
            "total_free": total_free,
            "num_free_blocks": len(free_blocks),
            "num_used_blocks": len(used_blocks),
            "largest_free_block": largest_free,
            "external_fragmentation": round(external_frag, 4),
        }


# ---------------------------------------------------------------------------
# BestFitAllocator — scans entire list, picks smallest sufficient block
# ---------------------------------------------------------------------------

class BestFitAllocator(SimpleAllocator):
    """
    Identical to SimpleAllocator except malloc uses best-fit strategy:
    scan all free blocks, pick the smallest one that fits.
    """

    def malloc(self, size: int, name: str | None = None) -> int | None:
        if size <= 0:
            return None

        best_index = None
        best_size = float("inf")

        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_index = i

        if best_index is not None:
            return self._allocate_block(best_index, size, name)
        return None


# ---------------------------------------------------------------------------
# BuddyAllocator — power-of-2 blocks, fast split/merge via buddy pairing
# ---------------------------------------------------------------------------

class BuddyAllocator:
    """
    Buddy-system allocator.

    - Total size must be a power of 2.
    - All blocks are power-of-2 sized.
    - free_lists[k] holds start addresses of free blocks of size 2^k.
    - Splitting: break a 2^k block into two 2^(k-1) buddies.
    - Merging: if a block's buddy is also free at the same level, merge them.
    """

    def __init__(self, total_size: int):
        # Round up to next power of 2
        self.order = (total_size - 1).bit_length()
        self.total_size = 1 << self.order  # actual size (power of 2)

        # free_lists[k] = set of start addresses of free blocks of size 2^k
        self.free_lists: list[set[int]] = [set() for _ in range(self.order + 1)]
        self.free_lists[self.order].add(0)  # one big free block

        # Track allocations: address -> (actual_size, requested_size, name)
        self.allocations: dict[int, tuple[int, int, str]] = {}
        self._name_counter = 0

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _next_power_of_2(n: int) -> int:
        """Smallest power of 2 >= n (minimum 1)."""
        if n <= 1:
            return 1
        return 1 << (n - 1).bit_length()

    @staticmethod
    def _log2(n: int) -> int:
        return n.bit_length() - 1

    def _buddy_address(self, address: int, order: int) -> int:
        """XOR trick: flip the bit at position *order* to find the buddy."""
        return address ^ (1 << order)

    # -- public API ---------------------------------------------------------

    def malloc(self, size: int, name: str | None = None) -> int | None:
        """Allocate at least *size* bytes (rounded up to power of 2)."""
        if size <= 0:
            return None

        needed = self._next_power_of_2(size)
        needed_order = self._log2(needed)

        if needed_order > self.order:
            return None  # request larger than total memory

        # Find the smallest available order >= needed_order
        for k in range(needed_order, self.order + 1):
            if self.free_lists[k]:
                return self._allocate_from_order(k, needed_order, size, name)

        return None  # out of memory

    def free(self, address: int) -> bool:
        """Free the allocation at *address*."""
        if address not in self.allocations:
            return False

        actual_size, _requested, _name = self.allocations.pop(address)
        order = self._log2(actual_size)

        # Return block to free list, then try to merge with buddy
        self._merge_up(address, order)
        return True

    # -- internals ----------------------------------------------------------

    def _allocate_from_order(self, avail_order: int, needed_order: int,
                              requested_size: int, name: str | None) -> int:
        # Take a block from avail_order
        address = self.free_lists[avail_order].pop()

        # Split down to needed_order
        while avail_order > needed_order:
            avail_order -= 1
            # The "right buddy" at the new smaller order becomes free
            buddy = address + (1 << avail_order)
            self.free_lists[avail_order].add(buddy)

        # Mark as allocated
        actual_size = 1 << needed_order
        if name is None:
            self._name_counter += 1
            name = f"A{self._name_counter}"
        self.allocations[address] = (actual_size, requested_size, name)

        return address

    def _merge_up(self, address: int, order: int):
        """Recursively merge a freed block with its buddy if the buddy is free."""
        while order < self.order:
            buddy = self._buddy_address(address, order)
            if buddy in self.free_lists[order]:
                # Buddy is free — merge
                self.free_lists[order].remove(buddy)
                # The merged block starts at the lower address
                address = min(address, buddy)
                order += 1
            else:
                break

        # Add the (possibly merged) block to the free list
        self.free_lists[order].add(address)

    # -- diagnostics --------------------------------------------------------

    def memory_map(self, width: int = 60) -> str:
        """ASCII visualization of the buddy allocator's memory."""
        # Build a sorted list of all blocks (allocated and free)
        events = []  # (start, size, is_free, label)

        for addr, (actual, requested, nm) in self.allocations.items():
            events.append((addr, actual, False, nm))

        for order, addrs in enumerate(self.free_lists):
            sz = 1 << order
            for addr in addrs:
                events.append((addr, sz, True, ""))

        events.sort(key=lambda e: e[0])

        lines = []
        bar = []
        for start, size, is_free, label in events:
            chars = max(1, round(size / self.total_size * width))
            if is_free:
                bar.append("." * chars)
            else:
                bar.append((label * chars)[:chars])
        lines.append("|" + "".join(bar)[:width].ljust(width) + "|")

        for start, size, is_free, label in events:
            state = "FREE" if is_free else f"USED ({label}, req={self.allocations[start][1]})"
            lines.append(f"  @{start:>5}  size={size:<6} {state}")

        return "\n".join(lines)

    def fragmentation_metrics(self) -> dict:
        """Compute fragmentation statistics for the buddy allocator."""
        total_allocated_actual = 0
        total_requested = 0

        for actual, requested, _ in self.allocations.values():
            total_allocated_actual += actual
            total_requested += requested

        total_free = self.total_size - total_allocated_actual

        # Internal fragmentation: wasted space inside allocated blocks
        if total_allocated_actual > 0:
            internal_frag = 1.0 - (total_requested / total_allocated_actual)
        else:
            internal_frag = 0.0

        # Largest free block
        largest_free = 0
        for order, addrs in enumerate(self.free_lists):
            if addrs:
                largest_free = max(largest_free, 1 << order)

        # External fragmentation
        if total_free > 0:
            external_frag = 1.0 - (largest_free / total_free)
        else:
            external_frag = 0.0

        free_block_count = sum(len(s) for s in self.free_lists)

        return {
            "total_size": self.total_size,
            "total_allocated_actual": total_allocated_actual,
            "total_requested": total_requested,
            "total_free": total_free,
            "internal_fragmentation": round(internal_frag, 4),
            "external_fragmentation": round(external_frag, 4),
            "num_free_blocks": free_block_count,
            "num_allocations": len(self.allocations),
            "largest_free_block": largest_free,
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_simple_allocator():
    print("=" * 70)
    print("SIMPLE ALLOCATOR (First-Fit)")
    print("=" * 70)

    alloc = SimpleAllocator(256)
    print("\nInitial state:")
    print(alloc.memory_map())

    # Make some allocations
    a = alloc.malloc(40, "A")
    b = alloc.malloc(60, "B")
    c = alloc.malloc(30, "C")
    d = alloc.malloc(50, "D")
    print(f"\nAfter malloc(40)=@{a}, malloc(60)=@{b}, malloc(30)=@{c}, malloc(50)=@{d}:")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")

    # Free B and D — creates holes
    alloc.free(b)
    alloc.free(d)
    print(f"\nAfter free(B=@{b}), free(D=@{d}):")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")

    # Allocate something that fits in B's old spot
    e = alloc.malloc(25, "E")
    print(f"\nAfter malloc(25)=@{e} (should reuse B's old hole):")
    print(alloc.memory_map())

    # Free A and E — should coalesce with the gap between them
    alloc.free(a)
    alloc.free(e)
    print(f"\nAfter free(A=@{a}), free(E=@{e}) — watch coalescing:")
    print(alloc.memory_map())

    # Free C — should coalesce into one big block at the front
    alloc.free(c)
    print(f"\nAfter free(C=@{c}) — everything before D's old spot merges:")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")


def demo_best_fit_allocator():
    print("\n" + "=" * 70)
    print("BEST-FIT ALLOCATOR")
    print("=" * 70)

    alloc = BestFitAllocator(256)

    # Create some holes of different sizes
    a = alloc.malloc(30, "A")
    b = alloc.malloc(80, "B")
    c = alloc.malloc(20, "C")
    d = alloc.malloc(60, "D")
    alloc.free(b)   # 80-byte hole
    alloc.free(d)   # 60-byte hole (and trailing free merges)

    print("\nMemory with two holes (80 and 60+trailing):")
    print(alloc.memory_map())

    # Best-fit should pick the 80-byte hole for a 70-byte request
    # (it is the smallest hole that fits)
    e = alloc.malloc(70, "E")
    print(f"\nAfter malloc(70)=@{e} — best-fit picks the 80-byte hole:")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")


def demo_buddy_allocator():
    print("\n" + "=" * 70)
    print("BUDDY ALLOCATOR")
    print("=" * 70)

    alloc = BuddyAllocator(256)
    print(f"\nInitial state (total_size rounded to {alloc.total_size}):")
    print(alloc.memory_map())

    a = alloc.malloc(30, "A")
    b = alloc.malloc(50, "B")
    c = alloc.malloc(10, "C")
    print(f"\nAfter malloc(30)=@{a}, malloc(50)=@{b}, malloc(10)=@{c}:")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")

    # Free B — buddy may merge
    alloc.free(b)
    print(f"\nAfter free(B=@{b}):")
    print(alloc.memory_map())

    # Free A — should trigger buddy merges
    alloc.free(a)
    print(f"\nAfter free(A=@{a}) — buddy merges cascade:")
    print(alloc.memory_map())

    # Free C — everything merges back to one big block
    alloc.free(c)
    print(f"\nAfter free(C=@{c}) — back to one block:")
    print(alloc.memory_map())
    print(f"Metrics: {alloc.fragmentation_metrics()}")


def demo_fragmentation_comparison():
    """Compare fragmentation across allocators under the same random workload."""
    print("\n" + "=" * 70)
    print("FRAGMENTATION COMPARISON — Random Workload")
    print("=" * 70)

    SIZE = 1024
    NUM_OPS = 200

    random.seed(42)

    # Generate a reproducible workload
    workload = []
    live_ids = []
    next_id = 0
    for _ in range(NUM_OPS):
        if not live_ids or random.random() < 0.6:
            # allocate
            sz = random.randint(4, 64)
            workload.append(("alloc", next_id, sz))
            live_ids.append(next_id)
            next_id += 1
        else:
            # free a random live allocation
            idx = random.randint(0, len(live_ids) - 1)
            aid = live_ids.pop(idx)
            workload.append(("free", aid, 0))

    for label, AllocClass in [("First-Fit", SimpleAllocator),
                               ("Best-Fit", BestFitAllocator)]:
        alloc = AllocClass(SIZE)
        addr_map = {}
        alloc_ok = 0
        alloc_fail = 0

        for op, aid, sz in workload:
            if op == "alloc":
                addr = alloc.malloc(sz, f"a{aid}")
                if addr is not None:
                    addr_map[aid] = addr
                    alloc_ok += 1
                else:
                    alloc_fail += 1
            else:
                if aid in addr_map:
                    alloc.free(addr_map.pop(aid))

        metrics = alloc.fragmentation_metrics()
        print(f"\n{label}:")
        print(f"  Successful allocs: {alloc_ok}, Failed: {alloc_fail}")
        for k, v in metrics.items():
            print(f"  {k}: {v}")

    # Buddy allocator (same workload)
    alloc = BuddyAllocator(SIZE)
    addr_map = {}
    alloc_ok = 0
    alloc_fail = 0

    for op, aid, sz in workload:
        if op == "alloc":
            addr = alloc.malloc(sz, f"a{aid}")
            if addr is not None:
                addr_map[aid] = addr
                alloc_ok += 1
            else:
                alloc_fail += 1
        else:
            if aid in addr_map:
                alloc.free(addr_map.pop(aid))

    metrics = alloc.fragmentation_metrics()
    print(f"\nBuddy System:")
    print(f"  Successful allocs: {alloc_ok}, Failed: {alloc_fail}")
    for k, v in metrics.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    demo_simple_allocator()
    demo_best_fit_allocator()
    demo_buddy_allocator()
    demo_fragmentation_comparison()
