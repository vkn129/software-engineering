"""
Practice: Memory Allocators
============================
Five exercises building on the allocator.py implementations.
Work through each TODO, then check your answers below the === SOLUTIONS === line.

Run with: python practice.py
"""

import struct
import math
import random
from typing import Optional


# ---------------------------------------------------------------------------
# Shared utilities (copied from allocator.py so this file is self-contained)
# ---------------------------------------------------------------------------

ALIGNMENT = 8
HEADER_SIZE = 8
NULL_PTR = 0xFFFFFFFF
HEADER_FMT = ">II"


def align_up(n: int, alignment: int = ALIGNMENT) -> int:
    return (n + alignment - 1) & ~(alignment - 1)


# ---------------------------------------------------------------------------
# Exercise 1: Best-Fit Free-List Allocator
# ---------------------------------------------------------------------------
# The FreeListAllocator in allocator.py uses first-fit (stop at first block
# that fits). Best-fit scans the *entire* free list and picks the *smallest*
# block that is still large enough.
#
# TODO: Complete BestFitAllocator.alloc() below.
# The __init__ and free() are identical to FreeListAllocator.

class BestFitAllocator:
    """Best-fit free-list allocator. Minimises internal fragmentation."""

    def __init__(self, size: int):
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        self._write_block(0, size, NULL_PTR)
        self.free_list_head = 0

    def _write_block(self, offset, size, next_ptr):
        struct.pack_into(HEADER_FMT, self.heap, offset, size, next_ptr)

    def _read_block(self, offset):
        return struct.unpack_from(HEADER_FMT, self.heap, offset)

    def _write_size(self, offset, size):
        struct.pack_into(">I", self.heap, offset, size)

    def _read_size(self, offset):
        return struct.unpack_from(">I", self.heap, offset)[0]

    def alloc(self, n: int) -> int:
        """
        TODO: implement best-fit allocation.

        Steps:
          1. Compute 'needed' bytes (4-byte size header + aligned payload).
          2. Walk the entire free list, tracking the block with the smallest
             size >= needed (and its predecessor).
          3. If found: split if remainder >= HEADER_SIZE + ALIGNMENT, remove
             from free list, write the size header, return offset + 4.
          4. Return -1 if no block fits.

        Hint: reuse the _write_block, _read_block, _write_size helpers.
        """
        # TODO: replace this stub
        return -1

    def free(self, ptr: int) -> None:
        if ptr <= 0:
            return
        block_offset = ptr - 4
        block_size = self._read_size(block_offset)
        prev_offset = -1
        cur_offset = self.free_list_head
        while cur_offset != NULL_PTR and cur_offset < block_offset:
            prev_offset = cur_offset
            _, next_ptr = self._read_block(cur_offset)
            cur_offset = next_ptr
        self._write_block(block_offset, block_size, cur_offset)
        if prev_offset == -1:
            self.free_list_head = block_offset
        else:
            prev_size = self._read_size(prev_offset)
            self._write_block(prev_offset, prev_size, block_offset)
        self._coalesce_with_next(block_offset)
        if prev_offset != -1:
            self._coalesce_with_next(prev_offset)

    def _coalesce_with_next(self, offset):
        size, next_ptr = self._read_block(offset)
        if offset + size == next_ptr and next_ptr != NULL_PTR:
            next_size, next_next = self._read_block(next_ptr)
            self._write_block(offset, size + next_size, next_next)


# ---------------------------------------------------------------------------
# Exercise 2: Double-Free Detection
# ---------------------------------------------------------------------------
# A double-free bug (calling free twice on the same pointer) silently
# corrupts the free list in a real allocator. Add detection to the
# FreeListAllocator below.
#
# TODO: Modify SafeFreeListAllocator.free() to raise ValueError on
# double-free. Use a set to track live (allocated) offsets.

class SafeFreeListAllocator:
    """Free-list allocator with double-free detection."""

    def __init__(self, size: int):
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        self._write_block(0, size, NULL_PTR)
        self.free_list_head = 0
        # TODO: add a data structure to track live pointers
        self._live: set = set()

    def _write_block(self, offset, size, next_ptr):
        struct.pack_into(HEADER_FMT, self.heap, offset, size, next_ptr)

    def _read_block(self, offset):
        return struct.unpack_from(HEADER_FMT, self.heap, offset)

    def _write_size(self, offset, size):
        struct.pack_into(">I", self.heap, offset, size)

    def _read_size(self, offset):
        return struct.unpack_from(">I", self.heap, offset)[0]

    def alloc(self, n: int) -> int:
        needed = align_up(4 + n)
        prev_offset = -1
        cur_offset = self.free_list_head
        while cur_offset != NULL_PTR:
            block_size, next_ptr = self._read_block(cur_offset)
            if block_size >= needed:
                remainder = block_size - needed
                if remainder >= HEADER_SIZE + ALIGNMENT:
                    new_free = cur_offset + needed
                    self._write_block(new_free, remainder, next_ptr)
                    next_ptr = new_free
                    block_size = needed
                if prev_offset == -1:
                    self.free_list_head = next_ptr
                else:
                    prev_size = self._read_size(prev_offset)
                    self._write_block(prev_offset, prev_size, next_ptr)
                self._write_size(cur_offset, block_size)
                ptr = cur_offset + 4
                # TODO: record this pointer as live
                return ptr
            prev_offset = cur_offset
            cur_offset = next_ptr
        return -1

    def free(self, ptr: int) -> None:
        """
        TODO: check if ptr is in _live. If not, raise ValueError("double-free").
        Otherwise remove it from _live, then proceed with normal free logic.
        """
        # TODO: add double-free check here

        if ptr <= 0:
            return
        block_offset = ptr - 4
        block_size = self._read_size(block_offset)
        prev_offset = -1
        cur_offset = self.free_list_head
        while cur_offset != NULL_PTR and cur_offset < block_offset:
            prev_offset = cur_offset
            _, next_ptr = self._read_block(cur_offset)
            cur_offset = next_ptr
        self._write_block(block_offset, block_size, cur_offset)
        if prev_offset == -1:
            self.free_list_head = block_offset
        else:
            prev_size = self._read_size(prev_offset)
            self._write_block(prev_offset, prev_size, block_offset)
        self._coalesce(block_offset)
        if prev_offset != -1:
            self._coalesce(prev_offset)

    def _coalesce(self, offset):
        size, next_ptr = self._read_block(offset)
        if offset + size == next_ptr and next_ptr != NULL_PTR:
            next_size, next_next = self._read_block(next_ptr)
            self._write_block(offset, size + next_size, next_next)


# ---------------------------------------------------------------------------
# Exercise 3: Alignment-Aware Allocator
# ---------------------------------------------------------------------------
# Some callers need specific alignment guarantees beyond ALIGNMENT=8.
# Implement alloc_aligned(n, align) that returns a pointer guaranteed to be
# divisible by `align` (where align is a power of 2).
#
# Strategy: allocate n + align - 1 extra bytes, then find the first aligned
# address within that region and return it. Store the original pointer before
# the aligned address so free_aligned can recover it.
#
# TODO: complete alloc_aligned and free_aligned.

class AlignedAllocator:
    """Wraps a bump allocator and provides alignment-aware allocation."""

    def __init__(self, size: int):
        self.heap = bytearray(size)
        self.size = size
        self.bump_ptr = 0
        # Maps aligned_ptr -> original_ptr for free_aligned
        self._align_map: dict[int, int] = {}

    def _raw_alloc(self, n: int) -> int:
        if self.bump_ptr + n > self.size:
            return -1
        ptr = self.bump_ptr
        self.bump_ptr += n
        return ptr

    def alloc_aligned(self, n: int, align: int) -> int:
        """
        TODO: allocate n bytes with the returned pointer divisible by align.

        Steps:
          1. Validate that align is a power of 2.
          2. Allocate n + align + 4 bytes raw (extra space for alignment slop
             and a 4-byte slot to store the original pointer).
          3. Compute the aligned address: smallest address >= raw_ptr+4 that
             is divisible by align. (The +4 reserves space for the stored ptr.)
          4. Store the raw_ptr at (aligned_ptr - 4) as a 4-byte integer.
          5. Record aligned_ptr -> raw_ptr in self._align_map.
          6. Return aligned_ptr.

        Hint: aligned = (raw + align - 1) & ~(align - 1)
        """
        # TODO: implement
        return -1

    def free_aligned(self, aligned_ptr: int) -> None:
        """
        TODO: look up the original pointer from _align_map and release it.
        For a bump allocator this is a no-op — just remove from _align_map
        to avoid double-free confusion.
        """
        # TODO: implement
        pass


# ---------------------------------------------------------------------------
# Exercise 4: Slab Allocator for Fixed-Size Objects
# ---------------------------------------------------------------------------
# A slab allocator pre-allocates a pool of fixed-size slots and uses a
# free-stack for O(1) alloc and free with zero fragmentation.
#
# TODO: complete SlabAllocator.__init__, alloc, and free.

class SlabAllocator:
    """
    Slab allocator for fixed-size objects.
    All allocations return a slot of exactly `obj_size` bytes.
    """

    def __init__(self, obj_size: int, num_objects: int):
        """
        TODO:
          1. Round obj_size up to ALIGNMENT.
          2. Allocate a bytearray of size obj_size * num_objects.
          3. Build a free_stack: a list of all slot offsets [0, obj_size,
             2*obj_size, ...] (in any order — it's a stack).
          4. Store obj_size and num_objects.
        """
        # TODO: implement
        self.obj_size = align_up(obj_size)
        self.num_objects = num_objects
        self.heap = bytearray(self.obj_size * num_objects)
        self.free_stack: list[int] = []
        # TODO: populate free_stack

    def alloc(self) -> int:
        """
        TODO: pop a slot offset from free_stack and return it.
        Return -1 if no slots remain.
        """
        # TODO: implement
        return -1

    def free(self, ptr: int) -> None:
        """
        TODO: push ptr back onto free_stack.
        Optionally validate that ptr is a valid slot offset.
        """
        # TODO: implement
        pass

    def stats(self) -> dict:
        used = self.num_objects - len(self.free_stack)
        return {
            "obj_size": self.obj_size,
            "num_objects": self.num_objects,
            "used": used,
            "free": len(self.free_stack),
            "utilization_pct": round(used / self.num_objects * 100, 1),
            "internal_frag_pct": 0.0,  # no fragmentation by design
            "external_frag_pct": 0.0,
        }


# ---------------------------------------------------------------------------
# Exercise 5: Measure External Fragmentation on a Random Workload
# ---------------------------------------------------------------------------
# External fragmentation = the percentage of free memory that is NOT in the
# largest single free block. High fragmentation means even though plenty of
# bytes are free, large allocations will fail.
#
# TODO: complete measure_fragmentation().

def measure_fragmentation(heap_size: int = 8192, seed: int = 0) -> dict:
    """
    TODO: run the following workload on a FreeListAllocator (import or
    copy the one from allocator.py — a minimal version is provided below)
    and return fragmentation stats.

    Workload:
      1. Allocate 100 objects with sizes drawn uniformly from [8, 256].
      2. Free a random 50% of them.
      3. Attempt to allocate one object of size heap_size // 4.
      4. Return: {
           "external_frag_pct": <float>,
           "large_alloc_succeeded": <bool>,
           "free_holes": <int>,
           "largest_hole": <int>,
           "free_bytes": <int>,
         }

    Use MinimalFreeList below (already implemented).
    """
    # TODO: implement
    return {}


# Minimal free-list for Exercise 5 (fully implemented — just use it)
class MinimalFreeList:
    def __init__(self, size):
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        struct.pack_into(HEADER_FMT, self.heap, 0, size, NULL_PTR)
        self.head = 0

    def _rb(self, o):
        return struct.unpack_from(HEADER_FMT, self.heap, o)

    def _wb(self, o, s, n):
        struct.pack_into(HEADER_FMT, self.heap, o, s, n)

    def _rs(self, o):
        return struct.unpack_from(">I", self.heap, o)[0]

    def _ws(self, o, s):
        struct.pack_into(">I", self.heap, o, s)

    def alloc(self, n):
        needed = align_up(4 + n)
        prev, cur = -1, self.head
        while cur != NULL_PTR:
            bs, nxt = self._rb(cur)
            if bs >= needed:
                rem = bs - needed
                if rem >= HEADER_SIZE + ALIGNMENT:
                    self._wb(cur + needed, rem, nxt)
                    nxt = cur + needed
                    bs = needed
                if prev == -1:
                    self.head = nxt
                else:
                    self._wb(prev, self._rs(prev), nxt)
                self._ws(cur, bs)
                return cur + 4
            prev, cur = cur, nxt
        return -1

    def free(self, ptr):
        if ptr <= 0:
            return
        bo = ptr - 4
        bs = self._rs(bo)
        prev, cur = -1, self.head
        while cur != NULL_PTR and cur < bo:
            prev, (_, nxt) = cur, self._rb(cur)
            cur = nxt
        self._wb(bo, bs, cur)
        if prev == -1:
            self.head = bo
        else:
            self._wb(prev, self._rs(prev), bo)
        self._coal(bo)
        if prev != -1:
            self._coal(prev)

    def _coal(self, o):
        s, n = self._rb(o)
        if o + s == n and n != NULL_PTR:
            ns, nn = self._rb(n)
            self._wb(o, s + ns, nn)

    def fragmentation(self):
        total, largest, holes = 0, 0, 0
        cur = self.head
        while cur != NULL_PTR:
            s, n = self._rb(cur)
            total += s
            largest = max(largest, s)
            holes += 1
            cur = n
        ext = (total - largest) / total * 100 if total else 0.0
        return {
            "external_frag_pct": round(ext, 1),
            "free_bytes": total,
            "largest_hole": largest,
            "free_holes": holes,
        }


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    print("=" * 60)
    print("Exercise 1: Best-Fit Allocator")
    print("=" * 60)
    bf = BestFitAllocator(512)
    # Allocate three blocks: 10, 50, 20 bytes
    p1 = bf.alloc(10)
    p2 = bf.alloc(50)
    p3 = bf.alloc(20)
    # Free the 50-byte block, creating a medium hole
    bf.free(p2)
    # Free the 10-byte block, creating a small hole
    bf.free(p1)
    # Best-fit for 12 bytes should pick the 10-byte hole's block (16 bytes
    # after alignment), not the larger 50-byte hole
    p4 = bf.alloc(12)
    if p4 == -1:
        print("  FAIL: alloc returned -1 (best-fit not implemented yet)")
    else:
        print(f"  alloc(12) -> offset {p4}  (expected <= {p1 + 4}, check best-fit picks small hole)")
    bf.free(p4)
    bf.free(p3)
    print()

    print("=" * 60)
    print("Exercise 2: Double-Free Detection")
    print("=" * 60)
    sf = SafeFreeListAllocator(256)
    px = sf.alloc(32)
    sf.free(px)
    try:
        sf.free(px)
        print("  FAIL: double-free not detected (not implemented yet)")
    except ValueError as e:
        print(f"  PASS: double-free raised ValueError: {e}")
    print()

    print("=" * 60)
    print("Exercise 3: Alignment-Aware Allocator")
    print("=" * 60)
    aa = AlignedAllocator(1024)
    for align in [16, 32, 64]:
        ptr = aa.alloc_aligned(100, align)
        if ptr == -1:
            print(f"  alloc_aligned(100, {align}) -> -1  (not implemented yet)")
        elif ptr % align == 0:
            print(f"  PASS: alloc_aligned(100, {align}) -> {ptr}  (divisible by {align})")
        else:
            print(f"  FAIL: alloc_aligned(100, {align}) -> {ptr}  (not divisible by {align})")
    print()

    print("=" * 60)
    print("Exercise 4: Slab Allocator")
    print("=" * 60)
    slab = SlabAllocator(obj_size=48, num_objects=10)
    slots = [slab.alloc() for _ in range(10)]
    if slots[0] == -1:
        print("  FAIL: slab alloc not implemented yet")
    else:
        full = slab.alloc()
        if full != -1:
            print("  FAIL: alloc should return -1 when slab is full")
        else:
            print(f"  PASS: 10 allocations succeeded, 11th returns -1")
        slab.free(slots[5])
        recycled = slab.alloc()
        if recycled == slots[5]:
            print(f"  PASS: freed slot recycled correctly (offset {recycled})")
        else:
            print(f"  FAIL or OK: recycled={recycled}, freed={slots[5]} (order may vary)")
    print(f"  Stats: {slab.stats()}")
    print()

    print("=" * 60)
    print("Exercise 5: External Fragmentation Measurement")
    print("=" * 60)
    result = measure_fragmentation(heap_size=4096, seed=7)
    if not result:
        print("  FAIL: measure_fragmentation not implemented yet (returned {})")
    else:
        print(f"  external_frag_pct:    {result.get('external_frag_pct', '?')}")
        print(f"  large_alloc_succeeded:{result.get('large_alloc_succeeded', '?')}")
        print(f"  free_holes:           {result.get('free_holes', '?')}")
        print(f"  largest_hole:         {result.get('largest_hole', '?')}")
        print(f"  free_bytes:           {result.get('free_bytes', '?')}")


if __name__ == "__main__":
    run_tests()
    print()
    print("Check your TODO implementations above, then compare with the")
    print("solutions below the === SOLUTIONS === marker.")


# ===========================================================================
# === SOLUTIONS ===
# ===========================================================================
# Study these after you have attempted each exercise yourself.


# ---------------------------------------------------------------------------
# Solution 1: Best-Fit Allocator
# ---------------------------------------------------------------------------

class BestFitAllocator_Solution:
    def __init__(self, size: int):
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        struct.pack_into(HEADER_FMT, self.heap, 0, size, NULL_PTR)
        self.free_list_head = 0

    def _wb(self, o, s, n): struct.pack_into(HEADER_FMT, self.heap, o, s, n)
    def _rb(self, o): return struct.unpack_from(HEADER_FMT, self.heap, o)
    def _ws(self, o, s): struct.pack_into(">I", self.heap, o, s)
    def _rs(self, o): return struct.unpack_from(">I", self.heap, o)[0]

    def alloc(self, n: int) -> int:
        needed = align_up(4 + n)

        # Track best block found so far
        best_offset = -1
        best_size = 10**18
        best_prev = -1

        prev_offset = -1
        cur_offset = self.free_list_head
        while cur_offset != NULL_PTR:
            block_size, next_ptr = self._rb(cur_offset)
            if block_size >= needed and block_size < best_size:
                best_size = block_size
                best_offset = cur_offset
                best_prev = prev_offset
            prev_offset = cur_offset
            cur_offset = next_ptr

        if best_offset == -1:
            return -1  # no block fits

        # Re-read the chosen block's next pointer
        block_size, next_ptr = self._rb(best_offset)
        remainder = block_size - needed
        if remainder >= HEADER_SIZE + ALIGNMENT:
            new_free = best_offset + needed
            self._wb(new_free, remainder, next_ptr)
            next_ptr = new_free
            block_size = needed

        # Remove best_offset from free list
        if best_prev == -1:
            self.free_list_head = next_ptr
        else:
            prev_size = self._rs(best_prev)
            self._wb(best_prev, prev_size, next_ptr)

        self._ws(best_offset, block_size)
        return best_offset + 4

    def free(self, ptr: int) -> None:
        if ptr <= 0:
            return
        bo = ptr - 4
        bs = self._rs(bo)
        prev, cur = -1, self.free_list_head
        while cur != NULL_PTR and cur < bo:
            prev = cur
            cur = self._rb(cur)[1]
        self._wb(bo, bs, cur)
        if prev == -1:
            self.free_list_head = bo
        else:
            self._wb(prev, self._rs(prev), bo)
        self._coal(bo)
        if prev != -1:
            self._coal(prev)

    def _coal(self, o):
        s, n = self._rb(o)
        if o + s == n and n != NULL_PTR:
            ns, nn = self._rb(n)
            self._wb(o, s + ns, nn)


# ---------------------------------------------------------------------------
# Solution 2: Double-Free Detection
# ---------------------------------------------------------------------------

class SafeFreeListAllocator_Solution:
    def __init__(self, size: int):
        size = align_up(size)
        self.heap = bytearray(size)
        self.size = size
        struct.pack_into(HEADER_FMT, self.heap, 0, size, NULL_PTR)
        self.free_list_head = 0
        self._live: set = set()  # set of currently allocated payload ptrs

    def _wb(self, o, s, n): struct.pack_into(HEADER_FMT, self.heap, o, s, n)
    def _rb(self, o): return struct.unpack_from(HEADER_FMT, self.heap, o)
    def _ws(self, o, s): struct.pack_into(">I", self.heap, o, s)
    def _rs(self, o): return struct.unpack_from(">I", self.heap, o)[0]

    def alloc(self, n: int) -> int:
        needed = align_up(4 + n)
        prev, cur = -1, self.free_list_head
        while cur != NULL_PTR:
            bs, nxt = self._rb(cur)
            if bs >= needed:
                rem = bs - needed
                if rem >= HEADER_SIZE + ALIGNMENT:
                    self._wb(cur + needed, rem, nxt)
                    nxt = cur + needed
                    bs = needed
                if prev == -1:
                    self.free_list_head = nxt
                else:
                    self._wb(prev, self._rs(prev), nxt)
                self._ws(cur, bs)
                ptr = cur + 4
                self._live.add(ptr)   # <-- record as live
                return ptr
            prev, cur = cur, nxt
        return -1

    def free(self, ptr: int) -> None:
        # Double-free check: ptr must be in _live
        if ptr not in self._live:
            raise ValueError(f"double-free or invalid pointer: {ptr}")
        self._live.discard(ptr)       # <-- remove from live set

        if ptr <= 0:
            return
        bo = ptr - 4
        bs = self._rs(bo)
        prev, cur = -1, self.free_list_head
        while cur != NULL_PTR and cur < bo:
            prev = cur
            cur = self._rb(cur)[1]
        self._wb(bo, bs, cur)
        if prev == -1:
            self.free_list_head = bo
        else:
            self._wb(prev, self._rs(prev), bo)
        self._coal(bo)
        if prev != -1:
            self._coal(prev)

    def _coal(self, o):
        s, n = self._rb(o)
        if o + s == n and n != NULL_PTR:
            ns, nn = self._rb(n)
            self._wb(o, s + ns, nn)


# ---------------------------------------------------------------------------
# Solution 3: Alignment-Aware Allocator
# ---------------------------------------------------------------------------

class AlignedAllocator_Solution:
    def __init__(self, size: int):
        self.heap = bytearray(size)
        self.size = size
        self.bump_ptr = 0
        self._align_map: dict[int, int] = {}

    def _raw_alloc(self, n: int) -> int:
        if self.bump_ptr + n > self.size:
            return -1
        ptr = self.bump_ptr
        self.bump_ptr += n
        return ptr

    def alloc_aligned(self, n: int, align: int) -> int:
        # Validate power-of-2
        assert align > 0 and (align & (align - 1)) == 0, "align must be power of 2"

        # Allocate extra space: n + align (for slop) + 4 (for stored raw ptr)
        raw_ptr = self._raw_alloc(n + align + 4)
        if raw_ptr == -1:
            return -1

        # Find first aligned address at least 4 bytes past raw_ptr
        # (we need 4 bytes before aligned_ptr to store raw_ptr)
        raw_plus_4 = raw_ptr + 4
        aligned_ptr = (raw_plus_4 + align - 1) & ~(align - 1)

        # Store original raw_ptr in the 4 bytes before aligned_ptr
        struct.pack_into(">I", self.heap, aligned_ptr - 4, raw_ptr)

        # Record in map for free_aligned
        self._align_map[aligned_ptr] = raw_ptr

        return aligned_ptr

    def free_aligned(self, aligned_ptr: int) -> None:
        if aligned_ptr not in self._align_map:
            raise ValueError(f"invalid or double-free of aligned pointer: {aligned_ptr}")
        self._align_map.pop(aligned_ptr)
        # For a bump allocator, we cannot individually reclaim — no-op.
        # A real aligned allocator would look up raw_ptr and call the underlying free.


# ---------------------------------------------------------------------------
# Solution 4: Slab Allocator
# ---------------------------------------------------------------------------

class SlabAllocator_Solution:
    def __init__(self, obj_size: int, num_objects: int):
        self.obj_size = align_up(obj_size)
        self.num_objects = num_objects
        self.heap = bytearray(self.obj_size * num_objects)
        # Populate free_stack with all slot offsets
        self.free_stack: list[int] = [
            i * self.obj_size for i in range(num_objects)
        ]

    def alloc(self) -> int:
        if not self.free_stack:
            return -1
        return self.free_stack.pop()

    def free(self, ptr: int) -> None:
        # Optional: validate ptr is a valid slot offset
        if ptr < 0 or ptr % self.obj_size != 0 or ptr >= self.obj_size * self.num_objects:
            raise ValueError(f"invalid slab pointer: {ptr}")
        if ptr in self.free_stack:
            raise ValueError(f"double-free of slab slot: {ptr}")
        self.free_stack.append(ptr)

    def stats(self) -> dict:
        used = self.num_objects - len(self.free_stack)
        return {
            "obj_size": self.obj_size,
            "num_objects": self.num_objects,
            "used": used,
            "free": len(self.free_stack),
            "utilization_pct": round(used / self.num_objects * 100, 1),
            "internal_frag_pct": 0.0,
            "external_frag_pct": 0.0,
        }


# ---------------------------------------------------------------------------
# Solution 5: External Fragmentation Measurement
# ---------------------------------------------------------------------------

def measure_fragmentation_solution(heap_size: int = 8192, seed: int = 0) -> dict:
    rng = random.Random(seed)
    fl = MinimalFreeList(heap_size)

    # Phase 1: allocate 100 objects of random sizes
    ptrs = []
    for _ in range(100):
        size = rng.randint(8, 256)
        ptr = fl.alloc(size)
        if ptr != -1:
            ptrs.append(ptr)

    # Phase 2: free a random 50% of them
    rng.shuffle(ptrs)
    to_free = ptrs[: len(ptrs) // 2]
    kept = ptrs[len(ptrs) // 2 :]
    for ptr in to_free:
        fl.free(ptr)

    # Measure fragmentation
    stats = fl.fragmentation()

    # Phase 3: attempt a large allocation
    large_ptr = fl.alloc(heap_size // 4)
    succeeded = large_ptr != -1

    return {
        "external_frag_pct": stats["external_frag_pct"],
        "large_alloc_succeeded": succeeded,
        "free_holes": stats["free_holes"],
        "largest_hole": stats["largest_hole"],
        "free_bytes": stats["free_bytes"],
    }


# ---------------------------------------------------------------------------
# Verify solutions (uncomment to run)
# ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     # Exercise 1 solution check
#     bf = BestFitAllocator_Solution(512)
#     p1 = bf.alloc(10); p2 = bf.alloc(50); p3 = bf.alloc(20)
#     bf.free(p2); bf.free(p1)
#     p4 = bf.alloc(12)
#     print("Best-fit alloc(12):", p4)
#     bf.free(p4); bf.free(p3)
#
#     # Exercise 2 solution check
#     sf = SafeFreeListAllocator_Solution(256)
#     px = sf.alloc(32); sf.free(px)
#     try: sf.free(px)
#     except ValueError as e: print("Double-free caught:", e)
#
#     # Exercise 3 solution check
#     aa = AlignedAllocator_Solution(1024)
#     for al in [16, 32, 64]:
#         p = aa.alloc_aligned(100, al)
#         print(f"alloc_aligned(100,{al})={p}, aligned={p % al == 0}")
#
#     # Exercise 4 solution check
#     slab = SlabAllocator_Solution(48, 10)
#     slots = [slab.alloc() for _ in range(10)]
#     print("Slab full, next alloc:", slab.alloc())
#     slab.free(slots[3]); print("Recycled:", slab.alloc())
#
#     # Exercise 5 solution check
#     result = measure_fragmentation_solution(4096, 7)
#     print("Fragmentation stats:", result)
