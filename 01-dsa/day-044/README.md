# Day 44: BST to Sorted Array and Back

## Why Conversions Between BSTs and Sorted Structures Matter

Every database, file system, and search engine faces the same operational reality: data structures must be **transformed** between representations. A B-tree index gets rebuilt from a sorted run during bulk loading. Two sorted indexes merge during compaction. An unbalanced BST degrades to O(n) and must be rebalanced. These aren't academic exercises — they're the maintenance operations that keep systems fast.

The core insight: **a BST's inorder traversal produces sorted output**, and **a sorted sequence can reconstruct a balanced BST**. This bidirectional relationship is the foundation of:

- **Rebalancing**: Unbalanced BST -> sorted array -> balanced BST (the naive but correct approach before learning rotations)
- **Bulk loading**: Databases receive sorted data and build balanced indexes in O(n) instead of O(n log n) insertions
- **Merge operations**: LSM-trees merge sorted runs; merging two BSTs is equivalent to merging two sorted sequences
- **Serialization**: Converting a BST to a sorted list for transmission, then reconstructing on the other end

## Sorted Array to Balanced BST

The key insight is **binary search on the array**. The middle element becomes the root (this ensures equal-sized subtrees), and we recurse on left and right halves.

```
sorted array: [1, 2, 3, 4, 5, 6, 7]

Pick middle (index 3) = 4 as root
Left half  [1, 2, 3] -> pick 2 as left child
Right half [5, 6, 7] -> pick 6 as right child
Recurse...

Result:
        4
       / \
      2   6
     / \ / \
    1  3 5  7
```

**Why the middle element?** Any other choice creates an imbalance. Choosing the first element gives a right-skewed tree (degenerate). The middle element guarantees height = floor(log2(n)), which is optimal.

**Time**: O(n) — each element visited exactly once
**Space**: O(log n) — recursion depth on a balanced split

## BST to Sorted Array

Inorder traversal. This is the simplest conversion — the BST property guarantees left < root < right, so inorder (left, root, right) produces sorted output.

**Time**: O(n)
**Space**: O(n) for the output array, O(h) for the call stack

## BST to Sorted Doubly Linked List (In-Place)

This is the most elegant conversion. Instead of allocating a new array, we **rewire the existing tree pointers**:
- `node.left` becomes the `prev` pointer
- `node.right` becomes the `next` pointer

The algorithm performs an inorder traversal, linking each node to its predecessor. The result is a circular doubly linked list using only the existing node pointers — zero extra allocation.

```
BST:          4
             / \
            2   5
           / \
          1   3

DLL: 1 <-> 2 <-> 3 <-> 4 <-> 5
     ^                        |
     |________________________|  (circular)
```

**Why circular?** It gives O(1) access to both the minimum (head) and maximum (head.left) — useful for range queries and merge operations.

## Sorted DLL Back to BST

The inverse operation. Given a sorted doubly linked list and its length n:
1. Recursively build the left subtree of size n//2
2. The current head of the list becomes the root
3. Advance the head pointer
4. Recursively build the right subtree of size n - n//2 - 1

This is an **inorder construction** — we consume nodes from the list in sorted order, which naturally fills the BST correctly. The trick is using a mutable reference (list or class attribute) to track the current position in the linked list.

**Time**: O(n), **Space**: O(log n) recursion stack

## Merging Two BSTs

The classic approach:
1. Convert both BSTs to sorted arrays — O(m + n) time and space
2. Merge the two sorted arrays — O(m + n), standard merge from merge sort
3. Build a balanced BST from the merged array — O(m + n)

Total: O(m + n) time and space. This is optimal — you must examine every node at least once.

**Alternative (space-optimized)**: Convert both BSTs to sorted DLLs in-place, merge the DLLs, convert merged DLL back to BST. This avoids the O(m + n) array allocation.

## Flatten BST to Right-Skewed List

Convert the BST so every node has no left child — effectively a sorted linked list using only right pointers. This is useful for:
- Simple iteration without a stack
- Serialization where you want sequential access
- Converting to a format that's easy to stream

## Failure Modes

1. **Off-by-one in array splitting**: Using `mid = (lo + hi) // 2` vs `mid = lo + (hi - lo) // 2` — both work for this problem, but the latter avoids integer overflow in languages without arbitrary precision integers.

2. **Forgetting to null out pointers**: When converting BST to DLL, if you don't set `node.left` and `node.right` correctly, you create cycles that cause infinite loops.

3. **Mutating while traversing**: In-place conversions modify the tree structure during traversal. If your traversal depends on the original structure (e.g., recursion using `node.left` after you've already overwritten it), you get corruption. Save references before modifying.

4. **Assuming BST property without validation**: If the input tree isn't actually a BST, the "sorted" array won't be sorted, and all downstream operations produce garbage.

5. **Stack overflow on degenerate trees**: A skewed BST with 100,000 nodes hits Python's recursion limit. For production code, use iterative approaches (Morris traversal from Day 40).

## What to Build Today

1. `sorted_array_to_bst(arr)` — binary search construction
2. `bst_to_sorted_array(root)` — inorder traversal
3. `bst_to_sorted_dll(root)` — in-place pointer rewiring
4. `sorted_dll_to_bst(head, n)` — inorder construction from DLL
5. `merge_two_bsts(root1, root2)` — full pipeline
6. `flatten_bst_to_sorted_list(root)` — right-skewed conversion
7. `balance_bst(root)` — rebalance via sorted array round-trip

## Checkpoint Questions

Before moving to Day 45, you should be able to answer:

- Why does choosing the middle element of a sorted array guarantee a balanced BST?
- What is the time complexity of rebalancing a BST via the sorted-array round-trip? Is there a way to do it faster?
- When converting a BST to a DLL in-place, why must you save `node.right` before modifying it during inorder traversal?
- Why is merging two BSTs via sorted arrays O(m + n) and not O((m + n) log(m + n))?
- In what real-world system would you use BST-to-sorted-DLL conversion instead of BST-to-sorted-array?
