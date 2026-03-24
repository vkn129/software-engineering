# Day 43: BST Operations — Insert, Search, Delete, Successor/Predecessor

## Why Binary Search Trees Exist

Arrays give O(1) random access but O(n) insert/delete (shifting). Linked lists give O(1) insert/delete at a known position but O(n) search (no random access). Hash tables give O(1) average-case everything but **destroy ordering** — you cannot iterate sorted, find the nearest value, or answer range queries.

The forcing function: **we need a data structure that keeps data sorted while supporting O(log n) insert, search, and delete**. Binary search trees solve this by encoding the binary search algorithm into a tree structure.

## The BST Invariant

For every node in the tree:

```
all keys in left subtree < node.key < all keys in right subtree
```

This single rule gives you everything:

| Property | Why It Works |
|----------|-------------|
| **Search in O(h)** | At each node, go left or right — eliminating half the remaining tree (like binary search) |
| **Sorted iteration** | Inorder traversal (Left, Root, Right) visits nodes in ascending order — the invariant guarantees it |
| **Min/Max in O(h)** | Minimum is the leftmost node; maximum is the rightmost |
| **Successor/predecessor** | Navigate to the "next" or "previous" element in sorted order |
| **Range queries** | Collect all keys between lo and hi by pruning subtrees that can't contain matches |

Where `h` is the height of the tree. For a balanced BST, h = O(log n). This is the critical caveat.

## Why Inorder = Sorted Order

The BST invariant is recursive: every subtree is itself a BST. Inorder traversal processes left subtree, then root, then right subtree. Since everything left < root < everything right, and each side is recursively sorted, the output is the complete sorted sequence.

This is why BSTs are sometimes called "sorted dictionaries" — they maintain key order as a structural invariant, not by explicitly sorting.

## Insertion

Insert always adds a new leaf. Walk down from the root:
- If key < current node, go left
- If key > current node, go right
- When you hit None, that's where the new node goes

```
Insert 6 into:        Result:
      8                  8
     / \                / \
    3   10             3   10
   / \                / \
  1   5              1   5
                          \
                           6
```

Time: O(h). No rebalancing in a basic BST — the shape depends entirely on insertion order.

## Search

Identical to binary search, but on a tree instead of an array:
- If key == current, found it
- If key < current, search left
- If key > current, search right
- If current is None, key doesn't exist

Time: O(h). This is binary search embodied as a data structure.

## Deletion — The Tricky Operation

Three cases, increasing in complexity:

### Case 1: Leaf Node (no children)
Simply remove it. The parent's pointer becomes None.

### Case 2: One Child
Replace the node with its only child. The child "moves up."

### Case 3: Two Children
This is the hard case. You can't just remove the node — both subtrees need a parent. The solution: **replace the node's key with its inorder successor** (the smallest key in the right subtree), then delete the successor (which has at most one child, so it's Case 1 or 2).

Why the inorder successor? Because it's the smallest value greater than the deleted node — swapping it in preserves the BST invariant for both subtrees.

You could also use the inorder predecessor (largest value in left subtree). Both work.

## Successor and Predecessor

**Successor(x)**: the node with the smallest key greater than x.
- If x has a right subtree: successor is the leftmost node in the right subtree
- If x has no right subtree: successor is the lowest ancestor whose left subtree contains x

**Predecessor(x)**: the node with the largest key less than x.
- If x has a left subtree: predecessor is the rightmost node in the left subtree
- If x has no left subtree: predecessor is the lowest ancestor whose right subtree contains x

Why they matter:
- **Iterators**: Moving to the "next" element in a sorted collection (e.g., C++ `std::set::iterator++`)
- **Deletion**: Case 3 deletion uses successor to find the replacement
- **Range queries**: Starting from floor(lo) and walking successors until ceil(hi)

## Floor and Ceil

- **floor(key)**: largest key in the BST that is <= key
- **ceil(key)**: smallest key in the BST that is >= key

These are essential for "nearest value" queries: "what's the closest price <= my budget?" or "what's the next scheduled event >= now?"

## Rank and Select (Order Statistics)

- **rank(key)**: how many keys in the BST are strictly less than key
- **select(k)**: find the kth smallest key (0-indexed)

These require knowing subtree sizes. Each node stores `size = 1 + size(left) + size(right)`. Then:
- rank: compare key with current node, add left subtree size if going right
- select: if k < left.size, go left; if k == left.size, return current; else go right with k - left.size - 1

## The Fatal Flaw: Degradation to O(n)

If you insert sorted data [1, 2, 3, 4, 5] into a BST, you get:

```
1
 \
  2
   \
    3
     \
      4
       \
        5
```

This is a linked list. Every operation is O(n). The BST gives no guarantees about balance — only the invariant left < root < right.

This is why self-balancing BSTs exist (AVL trees, Red-Black trees — Days 46-48). They add rotation operations to keep h = O(log n) after every insert/delete.

## Duplicate Handling Ambiguity

The standard BST invariant (left < root < right) has no room for duplicates. Options:
1. **Disallow duplicates** (like a set) — simplest, what we implement here
2. **Left subtree <= root** — duplicates go left, but complicates deletion
3. **Count field** — store a count at each node for repeated keys
4. **Linked list at each node** — each node holds a list of values with the same key

There's no universally "correct" answer — it depends on the use case.

## Complexity Summary

| Operation | Average (balanced) | Worst (degenerate) |
|-----------|-------------------|-------------------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Min/Max | O(log n) | O(n) |
| Successor/Predecessor | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Range query [lo, hi] | O(log n + k) | O(n) |

Where k is the number of keys in the range.

## Files

- **`bst.py`** — Complete BST implementation with insert, search, delete, min, max, successor, predecessor, floor, ceil, rank, select, range_query
- **`practice.py`** — 6 exercises with test harness

## Running

```bash
# Run the BST demo
python3 bst.py

# Run practice exercises (tests against reference solutions)
python3 practice.py
```

## Checkpoint Questions

Before moving to Day 44, you should be able to answer:
- Why does deleting a node with two children require finding the inorder successor (or predecessor)?
- What insertion order produces the worst-case BST shape? What order produces the best?
- Why is floor(key) not the same as "search for key, if not found return the last node you visited"?
- If a BST has n nodes and height h, what's the relationship between h and the time to find the rank of a key?
- Why do balanced BSTs (AVL, Red-Black) exist if basic BSTs already provide O(log n) average case?
