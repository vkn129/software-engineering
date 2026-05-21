"""
Memory Allocator Simulation — malloc from Scratch
==================================================
Simulates a heap as a Python bytearray and implements three allocators:
  1. BumpAllocator  — O(1) alloc, no free
  2. FreeListAllocator — first-fit with coalescing
  3. BuddyAllocator  — power-of-2 buddy system

Each exposes alloc(n) -> int (byte offset into heap, or -1 on failure)
and free(ptr) -> None.

Run with: python allocator.py
"""

import struct
import math
import random
from typing import Optional


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

ALIGNMENT = 8  # bytes; every allocation is rounded up to a multiple of this


def align_up(n: int, alignment: int = ALIGNMENT) -> int:
    """Round n up to the next multiple of alignment."""
    return (n + alignment - 1) & ~(alignment - 1)


# ---------------------------------------------------------------------------
# 1. Bump Allocator
# ---------------------------------------------------------------------------
# The simplest allocator possible. A pointer advances through the heap.
# Allocation is a single addition. Free does nothing.
# Suitable for arenas where all objects are freed together.

class BumpAllocator:
    """
    Heap layout: flat bytearray. bump_ptr marks next free byte.

    [  used  |  used  |  used  | . . . FREE . . . ]
                                ^
                              bump_ptr
    """

    def __init__(self, size: int):
        self.heap = bytearray(size)
        self.size = size
        self.bump_ptr = 0
        self.total_allocated = 0   # bytes actually returned to callers
        self.alloc_count = 0

    def alloc(self, n: int) -> int:
        """
        Return offset of a new n-byte block, or -1 if out of memory.
        Rounds n up to ALIGNMENT to ensure aligned returns.
        """
        n = align_up(n)
        if self.bump_ptr + n > self.size:
            return -1
        ptr = self.bump_ptr
        self.bump_ptr += n
        self.total_allocated += n
        self.alloc_count += 1
        return ptr

    def free(self, ptr: int) -> None:
        """Bump allocator never frees individual blocks — no-op."""
        pass  # intentional: reclaim only by resetting the whole arena

    def reset(self) -> None:
        """Reclaim the entire arena at once."""
        self.bump_ptr = 0
        self.total_allocated = 0
        self.alloc_count = 0

    def fragmentation(self) -> dict:
        """
        Bump allocator has zero external fragmentation (no holes) but some
        internal fragmentation from alignment padding.
        """
        used = self.bump_ptr
        free_bytes = self.size - used
        return {
            "heap_size": self.size,
            "used": used,
            "free": free_bytes,
            "external_frag_pct": 0.0,  # no holes, ever
        }


# ---------------------------------------------------------------------------
# 2. Free-List Allocator
# ---------------------------------------------------------------------------
# Maintains a linked list of free blocks embedded inside the heap itself.
# Each free block starts with a header: [size: 4 bytes][next_ptr: 4 bytes]
# (offsets into the heap, using 0xFFFFFFFF as a null sentinel).
#
# Allocation: first-fit search of free list.
# If the found block is larger than needed, split it.
# Free: insert at head of free list, then coalesce adjacent blocks.

HEADER_SIZE = 8          # 4 bytes size + 4 bytes next_ptr
NULL_PTR = 0xFFFFFFFF   # sentinel for "no next block"
HEADER_FMT = ">II"       # big-endian unsigned int, unsigned int


class FreeListAllocator:
    """
    Heap layout — each block (free or allocated) begins with a 4-byte size
    field so we can navigate the heap. Free blocks additionally store a
    next_ptr to chain the free list.

    Allocated block: [size(4)] [  payload ... ]
    Free block:      [size(4)] [next(4)] [  unused ... ]

    The pointer returned to the caller points PAST the size field, i.e.,
    to the start of the payload. The caller sees an opaque integer offset.
    """

    def __init__(self, size: int):
        # Ensure size is aligned
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        self.alloc_count = 0
        self.free_count = 0

        # Initialise the entire heap as one large free block
        # Block header: size=size, next=NULL_PTR
        self._write_block(0, size, NULL_PTR)
        self.free_list_head = 0  # offset of first free block

    # ---- low-level heap read/write ----

    def _write_block(self, offset: int, size: int, next_ptr: int) -> None:
        """Write a free-block header at offset."""
        struct.pack_into(HEADER_FMT, self.heap, offset, size, next_ptr)

    def _read_block(self, offset: int):
        """Return (size, next_ptr) of the block header at offset."""
        return struct.unpack_from(HEADER_FMT, self.heap, offset)

    def _write_size(self, offset: int, size: int) -> None:
        struct.pack_into(">I", self.heap, offset, size)

    def _read_size(self, offset: int) -> int:
        return struct.unpack_from(">I", self.heap, offset)[0]

    # ---- allocation ----

    def alloc(self, n: int) -> int:
        """
        First-fit: scan free list, take the first block >= n bytes.
        Split the block if leftover space is large enough for a new free block.
        Returns offset of payload (after the 4-byte size header), or -1.
        """
        # Total bytes needed: size header + payload (aligned)
        needed = align_up(HEADER_SIZE // 2 + n)  # 4 bytes for size + payload
        # More precisely: we store a 4-byte size prefix before the payload.
        needed = align_up(4 + n)

        prev_offset: int = -1
        cur_offset: int = self.free_list_head

        while cur_offset != NULL_PTR:
            block_size, next_ptr = self._read_block(cur_offset)

            if block_size >= needed:
                # Found a fit. Split if remainder is large enough.
                remainder = block_size - needed
                if remainder >= HEADER_SIZE + ALIGNMENT:
                    # Split: shrink this block, create a new free block after.
                    new_free_offset = cur_offset + needed
                    new_next = next_ptr
                    # If there is already a next free block past the new split,
                    # chain it correctly.
                    self._write_block(new_free_offset, remainder, new_next)
                    next_ptr = new_free_offset
                    block_size = needed

                # Remove cur_offset from free list
                if prev_offset == -1:
                    self.free_list_head = next_ptr
                else:
                    _, prev_next = self._read_block(prev_offset)
                    prev_size = self._read_size(prev_offset)
                    self._write_block(prev_offset, prev_size, next_ptr)

                # Write allocated block header (size only; next field unused)
                self._write_size(cur_offset, block_size)
                self.alloc_count += 1
                return cur_offset + 4  # payload starts after 4-byte size field

            prev_offset = cur_offset
            cur_offset = next_ptr

        return -1  # out of memory

    # ---- free ----

    def free(self, ptr: int) -> None:
        """
        Free the block whose payload starts at ptr.
        Insert at the correct sorted position in the free list (sorted by
        address), then coalesce with adjacent free blocks.
        """
        if ptr <= 0:
            return
        block_offset = ptr - 4  # step back to the size header
        block_size = self._read_size(block_offset)

        # Insert into free list in sorted order (by address) so coalescing works
        prev_offset: int = -1
        cur_offset: int = self.free_list_head

        while cur_offset != NULL_PTR and cur_offset < block_offset:
            prev_offset = cur_offset
            _, next_ptr = self._read_block(cur_offset)
            cur_offset = next_ptr

        # cur_offset is now the first free block >= block_offset
        # Insert block between prev and cur
        self._write_block(block_offset, block_size, cur_offset)

        if prev_offset == -1:
            self.free_list_head = block_offset
        else:
            prev_size = self._read_size(prev_offset)
            self._write_block(prev_offset, prev_size, block_offset)

        # Coalesce with successor
        self._coalesce_with_next(block_offset)

        # Coalesce predecessor with this block
        if prev_offset != -1:
            self._coalesce_with_next(prev_offset)

        self.free_count += 1

    def _coalesce_with_next(self, offset: int) -> None:
        """
        If the block immediately following 'offset' is also free, merge them.
        """
        size, next_ptr = self._read_block(offset)
        next_block = offset + size
        if next_block == next_ptr and next_ptr != NULL_PTR:
            # The physically adjacent block IS the next free block — merge.
            next_size, next_next = self._read_block(next_ptr)
            self._write_block(offset, size + next_size, next_next)

    # ---- stats ----

    def fragmentation(self) -> dict:
        """
        Walk the entire heap to measure fragmentation.
        External fragmentation = free bytes that exist but may be unusable.
        We report it as (total free bytes that are NOT in the largest free block)
        / total free bytes.
        """
        total_free = 0
        largest_free = 0
        hole_count = 0

        cur = self.free_list_head
        while cur != NULL_PTR:
            size, next_ptr = self._read_block(cur)
            total_free += size
            if size > largest_free:
                largest_free = size
            hole_count += 1
            cur = next_ptr

        if total_free == 0:
            ext_frag = 0.0
        else:
            ext_frag = (total_free - largest_free) / total_free * 100

        return {
            "heap_size": self.size,
            "free_bytes": total_free,
            "used_bytes": self.size - total_free,
            "free_holes": hole_count,
            "largest_hole": largest_free,
            "external_frag_pct": round(ext_frag, 1),
        }


# ---------------------------------------------------------------------------
# 3. Buddy Allocator
# ---------------------------------------------------------------------------
# Heap size must be a power of 2. All block sizes are powers of 2.
# A free list exists per size class (size_class 0 = min_block_size,
# size_class k = min_block_size * 2^k).
#
# alloc(n): round n up to power-of-2, find or split a block.
# free(ptr): find buddy address via XOR, merge if buddy is free.

class BuddyAllocator:
    """
    Buddy system allocator.

    min_block: minimum allocation size (must be power of 2, >= 8 for header).
    heap_size: total heap size (must be power of 2).

    Each free block stores a 4-byte size prefix so free() can determine
    the original allocated size.
    """

    def __init__(self, heap_size: int, min_block: int = 16):
        assert heap_size & (heap_size - 1) == 0, "heap_size must be power of 2"
        assert min_block & (min_block - 1) == 0, "min_block must be power of 2"
        assert heap_size >= min_block

        self.heap = bytearray(heap_size)
        self.heap_size = heap_size
        self.min_block = min_block

        # Number of size classes: log2(heap_size/min_block) + 1
        self.levels = int(math.log2(heap_size // min_block)) + 1
        # free_lists[k] = set of offsets of free blocks of size min_block*2^k
        self.free_lists: list[set] = [set() for _ in range(self.levels)]

        # Entire heap starts as one free block at level (levels-1)
        self.free_lists[self.levels - 1].add(0)

        self.alloc_count = 0
        self.free_count = 0
        # Track allocated blocks: offset -> level
        self._alloc_map: dict[int, int] = {}

    def _level_for_size(self, size: int) -> int:
        """Return the size-class level for a block of given size."""
        return int(math.log2(size // self.min_block))

    def _size_at_level(self, level: int) -> int:
        return self.min_block * (2 ** level)

    def _buddy_offset(self, offset: int, level: int) -> int:
        """XOR trick: buddy is at offset XOR block_size."""
        return offset ^ self._size_at_level(level)

    def alloc(self, n: int) -> int:
        """
        Round n up to next power-of-2 (min min_block), find a free block,
        split down to the right level. Returns payload offset (after 4-byte
        header), or -1 on failure.
        """
        # Account for 4-byte size prefix
        needed = max(self.min_block, self._next_pow2(n + 4))
        if needed > self.heap_size:
            return -1

        target_level = self._level_for_size(needed)

        # Find the smallest level >= target_level that has a free block
        found_level = -1
        for lvl in range(target_level, self.levels):
            if self.free_lists[lvl]:
                found_level = lvl
                break

        if found_level == -1:
            return -1  # out of memory

        # Split down from found_level to target_level
        offset = self.free_lists[found_level].pop()
        for lvl in range(found_level, target_level, -1):
            # Split: the right buddy becomes free at lvl-1
            half_size = self._size_at_level(lvl - 1)
            buddy = offset + half_size
            self.free_lists[lvl - 1].add(buddy)

        # Write size prefix and record allocation
        struct.pack_into(">I", self.heap, offset, needed)
        self._alloc_map[offset] = target_level
        self.alloc_count += 1
        return offset + 4  # return payload start

    def free(self, ptr: int) -> None:
        """
        Restore block to free list. Merge with buddy if buddy is free.
        """
        if ptr <= 0:
            return
        offset = ptr - 4
        if offset not in self._alloc_map:
            raise ValueError(f"double-free or invalid pointer: {ptr}")

        level = self._alloc_map.pop(offset)
        self._merge(offset, level)
        self.free_count += 1

    def _merge(self, offset: int, level: int) -> None:
        """Recursively merge with buddy if possible."""
        if level == self.levels - 1:
            # Already at the top level
            self.free_lists[level].add(offset)
            return

        buddy = self._buddy_offset(offset, level)
        if buddy in self.free_lists[level]:
            # Buddy is free — merge
            self.free_lists[level].remove(buddy)
            parent = min(offset, buddy)  # parent block starts at lower address
            self._merge(parent, level + 1)
        else:
            self.free_lists[level].add(offset)

    @staticmethod
    def _next_pow2(n: int) -> int:
        if n <= 1:
            return 1
        return 1 << (n - 1).bit_length()

    def fragmentation(self) -> dict:
        total_free = sum(
            len(self.free_lists[lvl]) * self._size_at_level(lvl)
            for lvl in range(self.levels)
        )
        largest_free = 0
        for lvl in range(self.levels - 1, -1, -1):
            if self.free_lists[lvl]:
                largest_free = self._size_at_level(lvl)
                break

        hole_count = sum(len(fl) for fl in self.free_lists)

        if total_free == 0:
            ext_frag = 0.0
        else:
            ext_frag = (total_free - largest_free) / total_free * 100

        # Internal fragmentation: bytes wasted inside allocated blocks
        # (rounded-up allocation - requested size). We can't know the original
        # request, so we report the worst-case: up to 50% per block (a block
        # of size 2^k serving a request of 2^(k-1)+1 bytes).
        return {
            "heap_size": self.heap_size,
            "free_bytes": total_free,
            "used_bytes": self.heap_size - total_free,
            "free_holes": hole_count,
            "largest_hole": largest_free,
            "external_frag_pct": round(ext_frag, 1),
            "note": "internal frag up to 50% per block (power-of-2 rounding)",
        }


# ---------------------------------------------------------------------------
# Workload Runner
# ---------------------------------------------------------------------------

def run_workload(allocator, name: str, heap_size: int) -> None:
    """
    Run a mixed allocation/free workload and print fragmentation stats.
    Pattern: allocate many small objects, free half of them (creating holes),
    allocate a large object.
    """
    print(f"\n{'='*60}")
    print(f"  Allocator: {name}")
    print(f"{'='*60}")

    rng = random.Random(42)  # deterministic
    live_ptrs = []

    # Phase 1: allocate 30 small objects (8–64 bytes)
    print("Phase 1: allocate 30 small objects (8-64 bytes)...")
    for _ in range(30):
        size = rng.randint(8, 64)
        ptr = allocator.alloc(size)
        if ptr != -1:
            live_ptrs.append(ptr)
            # Write a canary byte to verify the pointer is usable
            allocator.heap[ptr] = 0xAB

    print(f"  Live pointers: {len(live_ptrs)}")

    # Phase 2: free every other pointer (create holes)
    print("Phase 2: free every-other pointer (create external fragmentation)...")
    freed = []
    for i in range(0, len(live_ptrs), 2):
        allocator.free(live_ptrs[i])
        freed.append(live_ptrs[i])
    for p in freed:
        live_ptrs.remove(p)

    stats = allocator.fragmentation()
    print(f"  After freeing alternating blocks:")
    for k, v in stats.items():
        print(f"    {k}: {v}")

    # Phase 3: try to allocate a large object
    large_size = heap_size // 8
    print(f"Phase 3: allocate one large object ({large_size} bytes)...")
    ptr = allocator.alloc(large_size)
    if ptr == -1:
        print("  FAILED — fragmented heap could not satisfy large request")
    else:
        print(f"  SUCCESS — allocated at offset {ptr}")
        live_ptrs.append(ptr)

    # Phase 4: free everything
    print("Phase 4: free all remaining live pointers...")
    for ptr in live_ptrs:
        allocator.free(ptr)

    stats = allocator.fragmentation()
    print(f"  After freeing all:")
    for k, v in stats.items():
        print(f"    {k}: {v}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    HEAP_SIZE = 4096

    print("Memory Allocator Simulation")
    print("Heap size:", HEAP_SIZE, "bytes")

    # --- Bump Allocator ---
    bump = BumpAllocator(HEAP_SIZE)

    print(f"\n{'='*60}")
    print(f"  Allocator: Bump Allocator")
    print(f"{'='*60}")
    print("Phase 1: allocate 30 small objects...")
    rng = random.Random(42)
    ptrs = []
    for _ in range(30):
        size = rng.randint(8, 64)
        ptr = bump.alloc(size)
        if ptr != -1:
            ptrs.append(ptr)
    print(f"  Allocated: {len(ptrs)} objects, bump_ptr={bump.bump_ptr}")
    print("Phase 2: 'free' every-other (no-op for bump allocator)...")
    for i in range(0, len(ptrs), 2):
        bump.free(ptrs[i])  # no-op
    stats = bump.fragmentation()
    print(f"  Stats after 'free':")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    print("Phase 3: reset arena (bulk free)...")
    bump.reset()
    stats = bump.fragmentation()
    for k, v in stats.items():
        print(f"    {k}: {v}")

    # --- Free List Allocator ---
    fl = FreeListAllocator(HEAP_SIZE)
    run_workload(fl, "Free-List Allocator (first-fit + coalescing)", HEAP_SIZE)

    # --- Buddy Allocator ---
    # Heap must be power of 2
    buddy_size = 4096
    buddy = BuddyAllocator(buddy_size, min_block=16)
    run_workload(buddy, "Buddy Allocator (power-of-2 blocks)", buddy_size)

    print("\nDone.")
