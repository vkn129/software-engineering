"""
Day 28: Memory Allocator — Practice Exercises

4 exercises with TODO stubs and _sol_ solutions.
Run: python practice.py
"""

import random


# ===================================================================
# Shared Block class (same as memory_allocator.py)
# ===================================================================

class Block:
    __slots__ = ("start", "size", "is_free")

    def __init__(self, start: int, size: int, is_free: bool = True):
        self.start = start
        self.size = size
        self.is_free = is_free

    def __repr__(self):
        state = "FREE" if self.is_free else "USED"
        return f"[{state} @{self.start} sz={self.size}]"


# ===================================================================
# Exercise 1: Worst-Fit Allocation
# ===================================================================
# Implement a worst-fit allocator: always pick the LARGEST free block.
# If multiple blocks tie for largest, pick the first one.
# Support splitting (if remainder >= min_split=4).

def worst_fit_malloc(blocks: list[Block], size: int, min_split: int = 4) -> int | None:
    """
    Allocate *size* bytes using worst-fit strategy.
    Modify *blocks* in place (mark used, split if needed).
    Return the start address of the allocated block, or None if no fit.

    Steps:
    1. Scan all blocks, find the LARGEST free block that is >= size.
    2. If found, allocate from it (split if remainder >= min_split).
    3. Return start address.
    """
    # TODO: Implement worst-fit allocation
    pass


def _sol_worst_fit_malloc(blocks: list[Block], size: int, min_split: int = 4) -> int | None:
    """Reference solution for worst-fit."""
    worst_idx = None
    worst_size = -1

    for i, block in enumerate(blocks):
        if block.is_free and block.size >= size:
            if block.size > worst_size:
                worst_size = block.size
                worst_idx = i

    if worst_idx is None:
        return None

    block = blocks[worst_idx]
    remainder = block.size - size

    if remainder >= min_split:
        new_free = Block(start=block.start + size, size=remainder, is_free=True)
        block.size = size
        blocks.insert(worst_idx + 1, new_free)

    block.is_free = False
    return block.start


# ===================================================================
# Exercise 2: Block Coalescing
# ===================================================================
# Given a list of blocks where some adjacent blocks are both free,
# merge all adjacent free blocks into single larger blocks.

def coalesce_free_blocks(blocks: list[Block]) -> list[Block]:
    """
    Merge all adjacent free blocks into single blocks.
    Return a new list of blocks (or modify in place and return it).

    Example:
      Input:  [USED@0 sz=32] [FREE@32 sz=16] [FREE@48 sz=16] [USED@64 sz=32] [FREE@96 sz=64] [FREE@160 sz=96]
      Output: [USED@0 sz=32] [FREE@32 sz=32] [USED@64 sz=32] [FREE@96 sz=160]

    The two FREE blocks at 32 and 48 merge into one FREE block at 32 with size 32.
    The two FREE blocks at 96 and 160 merge into one FREE block at 96 with size 160.
    """
    # TODO: Implement coalescing
    pass


def _sol_coalesce_free_blocks(blocks: list[Block]) -> list[Block]:
    """Reference solution for coalescing."""
    if not blocks:
        return []

    result = [Block(blocks[0].start, blocks[0].size, blocks[0].is_free)]

    for i in range(1, len(blocks)):
        current = blocks[i]
        prev = result[-1]

        if prev.is_free and current.is_free:
            # Merge: extend previous block
            prev.size += current.size
        else:
            result.append(Block(current.start, current.size, current.is_free))

    return result


# ===================================================================
# Exercise 3: Fragmentation Measurement
# ===================================================================
# Perform a random alloc/free workload on a simple first-fit allocator,
# then measure external fragmentation.

class MiniAllocator:
    """Minimal first-fit allocator (provided — do NOT modify)."""

    def __init__(self, total_size: int):
        self.total_size = total_size
        self.blocks = [Block(0, total_size, True)]

    def malloc(self, size: int) -> int | None:
        for i, b in enumerate(self.blocks):
            if b.is_free and b.size >= size:
                remainder = b.size - size
                if remainder >= 4:
                    self.blocks.insert(i + 1, Block(b.start + size, remainder, True))
                    b.size = size
                b.is_free = False
                return b.start
        return None

    def free(self, address: int) -> bool:
        for i, b in enumerate(self.blocks):
            if b.start == address and not b.is_free:
                b.is_free = True
                # Coalesce forward
                while i + 1 < len(self.blocks) and self.blocks[i + 1].is_free:
                    nxt = self.blocks.pop(i + 1)
                    self.blocks[i].size += nxt.size
                # Coalesce backward
                while i > 0 and self.blocks[i - 1].is_free:
                    prev = self.blocks[i - 1]
                    cur = self.blocks.pop(i)
                    prev.size += cur.size
                    i -= 1
                return True
        return False


def measure_fragmentation(allocator: MiniAllocator) -> dict:
    """
    Given an allocator that has been used (has a mix of free and used blocks),
    compute and return:
      - "total_free": total bytes in free blocks
      - "largest_free": size of the largest free block
      - "num_free_blocks": count of free blocks
      - "external_fragmentation": 1 - (largest_free / total_free), or 0.0 if total_free == 0

    Examine allocator.blocks to compute these.
    """
    # TODO: Implement fragmentation measurement
    pass


def _sol_measure_fragmentation(allocator: MiniAllocator) -> dict:
    """Reference solution for fragmentation measurement."""
    free_blocks = [b for b in allocator.blocks if b.is_free]
    total_free = sum(b.size for b in free_blocks)
    largest_free = max((b.size for b in free_blocks), default=0)
    num_free = len(free_blocks)

    if total_free > 0:
        ext_frag = 1.0 - (largest_free / total_free)
    else:
        ext_frag = 0.0

    return {
        "total_free": total_free,
        "largest_free": largest_free,
        "num_free_blocks": num_free,
        "external_fragmentation": round(ext_frag, 4),
    }


# ===================================================================
# Exercise 4: Simple Mark-and-Sweep Garbage Collector
# ===================================================================
# Simulated heap objects with references. Implement mark-and-sweep.

class HeapObject:
    """A simulated object on the heap."""

    def __init__(self, obj_id: int, size: int):
        self.obj_id = obj_id
        self.size = size
        self.references: list[int] = []  # obj_ids this object points to
        self.marked = False

    def __repr__(self):
        return f"Obj({self.obj_id}, size={self.size}, refs={self.references})"


def mark_and_sweep(heap: dict[int, HeapObject], roots: list[int]) -> list[int]:
    """
    Perform mark-and-sweep garbage collection.

    Args:
        heap: dict mapping obj_id -> HeapObject (all objects on the heap)
        roots: list of obj_ids that are directly reachable (e.g., on the stack)

    Returns:
        List of obj_ids that are GARBAGE (unreachable from roots).

    Steps:
    1. MARK phase: starting from roots, recursively mark all reachable objects.
       - Set obj.marked = True for each reachable object.
       - Follow obj.references to find more reachable objects.
       - Watch out for cycles — don't revisit already-marked objects.
    2. SWEEP phase: iterate over all objects in the heap.
       - Any object with marked=False is garbage — collect its obj_id.
       - Reset marked=False on all objects (for next GC cycle).
    3. Return the list of garbage obj_ids (sorted for deterministic output).
    """
    # TODO: Implement mark-and-sweep GC
    pass


def _sol_mark_and_sweep(heap: dict[int, HeapObject], roots: list[int]) -> list[int]:
    """Reference solution for mark-and-sweep."""
    # MARK phase: BFS from roots
    stack = list(roots)
    while stack:
        obj_id = stack.pop()
        if obj_id not in heap:
            continue
        obj = heap[obj_id]
        if obj.marked:
            continue
        obj.marked = True
        for ref_id in obj.references:
            if ref_id in heap and not heap[ref_id].marked:
                stack.append(ref_id)

    # SWEEP phase
    garbage = []
    for obj_id, obj in heap.items():
        if not obj.marked:
            garbage.append(obj_id)
        obj.marked = False  # reset for next cycle

    return sorted(garbage)


# ===================================================================
# Test runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")
            failed += 1

    # --- Exercise 1: Worst-Fit ---
    print("\nExercise 1: Worst-Fit Allocation")
    print("-" * 40)

    # Use student impl if available, else solution
    wf_fn = worst_fit_malloc if worst_fit_malloc.__code__.co_code != (lambda: None).__code__.co_code else _sol_worst_fit_malloc
    if wf_fn is _sol_worst_fit_malloc:
        print("  (Using reference solution — implement worst_fit_malloc to test yours)")

    # Test 1a: picks largest block
    blocks = [
        Block(0, 30, False),
        Block(30, 20, True),   # hole 20
        Block(50, 40, False),
        Block(90, 50, True),   # hole 50
        Block(140, 60, True),  # hole 60 <-- worst-fit should pick this
    ]
    addr = wf_fn(blocks, 30)
    check("picks largest free block", addr, 140)

    # Test 1b: splits correctly
    blocks = [
        Block(0, 100, True),   # hole 100
        Block(100, 50, False),
        Block(150, 200, True), # hole 200 <-- picked, should split
    ]
    addr = wf_fn(blocks, 40)
    check("picks 200-byte block for 40-byte request", addr, 150)
    check("splits: allocated block size", blocks[2].size, 40)
    check("splits: remainder block exists", blocks[3].size, 160)
    check("splits: remainder is free", blocks[3].is_free, True)

    # Test 1c: returns None when nothing fits
    blocks = [Block(0, 10, True), Block(10, 20, False)]
    addr = wf_fn(blocks, 15)
    check("returns None when no block fits", addr, None)

    # --- Exercise 2: Coalescing ---
    print("\nExercise 2: Block Coalescing")
    print("-" * 40)

    coal_fn = coalesce_free_blocks if coalesce_free_blocks.__code__.co_code != (lambda: None).__code__.co_code else _sol_coalesce_free_blocks
    if coal_fn is _sol_coalesce_free_blocks:
        print("  (Using reference solution — implement coalesce_free_blocks to test yours)")

    # Test 2a: merge two adjacent free blocks
    blocks = [Block(0, 32, False), Block(32, 16, True), Block(48, 16, True), Block(64, 32, False)]
    result = coal_fn(blocks)
    check("merges two adjacent free blocks", len(result), 3)
    check("merged block start", result[1].start, 32)
    check("merged block size", result[1].size, 32)
    check("merged block is free", result[1].is_free, True)

    # Test 2b: merge three adjacent free blocks
    blocks = [Block(0, 10, True), Block(10, 20, True), Block(30, 30, True), Block(60, 40, False)]
    result = coal_fn(blocks)
    check("merges three adjacent free into one", len(result), 2)
    check("merged block size", result[0].size, 60)

    # Test 2c: no adjacent free blocks
    blocks = [Block(0, 10, True), Block(10, 20, False), Block(30, 10, True)]
    result = coal_fn(blocks)
    check("no merging needed", len(result), 3)

    # Test 2d: empty input
    result = coal_fn([])
    check("empty input", result, [])

    # --- Exercise 3: Fragmentation ---
    print("\nExercise 3: Fragmentation Measurement")
    print("-" * 40)

    frag_fn = measure_fragmentation if measure_fragmentation.__code__.co_code != (lambda: None).__code__.co_code else _sol_measure_fragmentation
    if frag_fn is _sol_measure_fragmentation:
        print("  (Using reference solution — implement measure_fragmentation to test yours)")

    # Run a random workload
    random.seed(123)
    alloc = MiniAllocator(512)
    addrs = {}
    next_id = 0

    for _ in range(100):
        if not addrs or random.random() < 0.6:
            sz = random.randint(4, 40)
            a = alloc.malloc(sz)
            if a is not None:
                addrs[next_id] = a
            next_id += 1
        else:
            aid = random.choice(list(addrs.keys()))
            alloc.free(addrs.pop(aid))

    metrics = frag_fn(alloc)
    check("total_free is non-negative", metrics["total_free"] >= 0, True)
    check("largest_free <= total_free", metrics["largest_free"] <= metrics["total_free"], True)
    check("ext frag in [0, 1]", 0.0 <= metrics["external_fragmentation"] <= 1.0, True)
    check("num_free_blocks >= 0", metrics["num_free_blocks"] >= 0, True)

    # Verify against solution
    sol_metrics = _sol_measure_fragmentation(alloc)
    check("total_free matches solution", metrics["total_free"], sol_metrics["total_free"])
    check("largest_free matches solution", metrics["largest_free"], sol_metrics["largest_free"])
    check("ext frag matches solution", metrics["external_fragmentation"], sol_metrics["external_fragmentation"])

    # --- Exercise 4: Mark-and-Sweep GC ---
    print("\nExercise 4: Mark-and-Sweep GC")
    print("-" * 40)

    gc_fn = mark_and_sweep if mark_and_sweep.__code__.co_code != (lambda: None).__code__.co_code else _sol_mark_and_sweep
    if gc_fn is _sol_mark_and_sweep:
        print("  (Using reference solution — implement mark_and_sweep to test yours)")

    # Test 4a: simple reachability
    #   root -> 1 -> 2    (3 is unreachable)
    heap = {
        1: HeapObject(1, 32),
        2: HeapObject(2, 64),
        3: HeapObject(3, 16),
    }
    heap[1].references = [2]
    garbage = gc_fn(heap, roots=[1])
    check("simple: obj 3 is garbage", garbage, [3])
    check("marks are reset", all(not o.marked for o in heap.values()), True)

    # Test 4b: cycle — all reachable
    #   root -> 1 -> 2 -> 3 -> 1  (cycle, all reachable)
    heap = {
        1: HeapObject(1, 10),
        2: HeapObject(2, 20),
        3: HeapObject(3, 30),
    }
    heap[1].references = [2]
    heap[2].references = [3]
    heap[3].references = [1]
    garbage = gc_fn(heap, roots=[1])
    check("cycle: no garbage", garbage, [])

    # Test 4c: disconnected cycle — unreachable
    #   root -> 1     4 -> 5 -> 4  (4,5 are a cycle but unreachable)
    heap = {
        1: HeapObject(1, 10),
        4: HeapObject(4, 40),
        5: HeapObject(5, 50),
    }
    heap[4].references = [5]
    heap[5].references = [4]
    garbage = gc_fn(heap, roots=[1])
    check("unreachable cycle: 4,5 are garbage", garbage, [4, 5])

    # Test 4d: multiple roots
    #   roots: 1, 3    1->2    3->4    5 is unreachable
    heap = {
        1: HeapObject(1, 10),
        2: HeapObject(2, 20),
        3: HeapObject(3, 30),
        4: HeapObject(4, 40),
        5: HeapObject(5, 50),
    }
    heap[1].references = [2]
    heap[3].references = [4]
    garbage = gc_fn(heap, roots=[1, 3])
    check("multiple roots: only 5 is garbage", garbage, [5])

    # Test 4e: empty heap
    garbage = gc_fn({}, roots=[])
    check("empty heap: no garbage", garbage, [])

    # --- Summary ---
    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    print("=" * 40)


if __name__ == "__main__":
    run_tests()
