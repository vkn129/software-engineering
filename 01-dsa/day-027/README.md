# Day 27: Linked List Algorithms

## Why This Exists

You have built singly and doubly linked lists. Now comes the real payoff: the classic algorithmic patterns that operate on them. These patterns appear in interviews constantly, but more importantly they teach you to think about pointer manipulation, space constraints, and mathematical invariants.

Why linked list algorithms matter beyond interviews:

1. **Floyd's cycle detection** is used in real systems — detecting infinite loops in state machines, finding duplicate values in bounded arrays, and cycle detection in garbage collectors.
2. **Merge sort on lists** is the only O(n log n) sort that works in O(1) extra space on linked lists (unlike arrays, where merge sort needs O(n) auxiliary space). The Linux kernel uses a variant of this for its linked list sort.
3. **Intersection detection** models real problems: two execution paths converging, two dependency chains sharing a common suffix, two version histories merging.
4. **Merge k sorted lists** is the core operation behind k-way merge in external sorting — how databases sort data that does not fit in memory.

These are not toy problems. They are the algorithmic primitives that systems are built from.

## Theory

### Floyd's Cycle Detection (Tortoise and Hare)

**The problem:** Given a linked list, determine if it contains a cycle. If it does, find where the cycle begins.

**Naive approach:** Use a hash set to track visited nodes. O(n) time, O(n) space. But can we do O(1) space?

**Floyd's insight:** Use two pointers moving at different speeds. If there is a cycle, the fast pointer will eventually lap the slow pointer — they must meet.

**Why they must meet (mathematical proof):**

Let the cycle have length C. Once both pointers are inside the cycle, at each step the gap between them changes by exactly 1 (fast moves 2, slow moves 1). So the relative distance decreases by 1 each step. Starting from any gap g (where 0 < g < C), they meet after exactly g steps.

More formally: if at some point the fast pointer is `d` steps ahead of slow within the cycle, then after `d` more steps, fast has moved `2d` and slow has moved `d`, so fast is now `d + 2d - d = 2d` steps from where slow started, and slow is `d` steps from where slow started. The gap is `d - d = 0` modulo C... they collide.

**Finding the cycle start:**

Let:
- `a` = distance from head to cycle start
- `b` = distance from cycle start to meeting point
- `C` = cycle length

When they meet, slow has traveled `a + b` steps. Fast has traveled `a + b + kC` steps (k full laps). Since fast moves twice as fast: `2(a + b) = a + b + kC`, so `a + b = kC`, thus `a = kC - b`.

This means: if you put one pointer at the head and one at the meeting point, both moving at speed 1, they will meet at the cycle start. The pointer from head travels `a` steps. The pointer from the meeting point travels `a = kC - b` steps, which brings it from position `b` in the cycle to position `b + kC - b = kC = 0` — the cycle start.

**Complexity:** O(n) time, O(1) space. Elegant.

### Merge Sort on Linked Lists

Arrays need O(n) auxiliary space for merge sort because merging two sorted halves in-place is impractical. Linked lists do not have this problem — you can rearrange nodes by rewiring pointers without allocating new nodes.

**Algorithm:**
1. **Split** the list in half using slow/fast pointers (finding the midpoint)
2. **Recursively sort** each half
3. **Merge** the two sorted halves by pointer manipulation

The split is O(n), the merge is O(n), and we recurse log(n) levels deep. Total: O(n log n) time, O(log n) stack space (O(1) heap space — no auxiliary arrays).

**Why this matters:** For arrays, quicksort usually beats merge sort due to cache locality. For linked lists, merge sort is king because: (a) no random access needed, (b) no auxiliary space, (c) linked lists have poor cache locality anyway, so quicksort loses its advantage.

### Finding the Intersection of Two Lists

Two singly linked lists may converge at some node and share a common tail:

```
A: a1 -> a2 ----\
                  -> c1 -> c2 -> c3
B: b1 -> b2 -> b3/
```

**Approach:** Compute lengths of both lists. Advance the longer list's pointer by the length difference. Then walk both pointers in lockstep — the first node where they are the same object (not just equal value) is the intersection.

**Alternative (elegant):** When pointer A reaches the end, redirect it to the head of B. When pointer B reaches the end, redirect it to the head of A. They will meet at the intersection after traversing `lenA + lenB - common` nodes each. If no intersection, they both reach None simultaneously.

**Complexity:** O(n + m) time, O(1) space.

### Palindrome Check

**Approach:** Find the middle using slow/fast pointers. Reverse the second half in-place. Compare the two halves node by node. Optionally restore the list by reversing the second half again.

**Why reverse in-place?** We could copy values to an array and check, but that is O(n) space. The in-place approach is O(1) space — a common interview constraint that tests your pointer manipulation skills.

### Merge K Sorted Lists

**Naive:** Merge lists pairwise repeatedly. This works but is O(Nk) where N is total nodes.

**Heap approach:** Maintain a min-heap of size k containing the head of each list. Extract the minimum, append it to the result, and push that node's next into the heap. Each of the N total nodes enters and leaves the heap exactly once. Each heap operation is O(log k).

**Complexity:** O(N log k) time, O(k) space for the heap. This is optimal — you cannot do better than O(N log k) because you need to compare elements from k sources.

## Practice

Work through the implementations in `linked_list_algorithms.py`, then tackle the exercises in `practice.py`.

**Suggested order:**
1. Read the implementations and trace through examples by hand
2. Implement the practice exercises without looking at solutions
3. Verify with `python practice.py`

## Checkpoint Questions

Before moving on, you should be able to answer:

1. **Why must the fast and slow pointers meet in Floyd's algorithm?** What is the mathematical invariant that guarantees collision?
2. **Why is merge sort preferred over quicksort for linked lists?** What property of arrays makes quicksort better there but not here?
3. **In the intersection algorithm, why does the "redirect to other head" trick work?** What quantity do both pointers travel before meeting?
4. **Why does the palindrome check reverse only the second half?** What would go wrong if you reversed the first half instead?
5. **Why is the heap approach for merging k lists O(N log k) and not O(N log N)?** What determines the heap size?
6. **Merge sort on lists uses O(log n) stack space. Is there a way to do it iteratively in true O(1) space?** (Hint: bottom-up merge sort.)
