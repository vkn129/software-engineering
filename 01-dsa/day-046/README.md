# Day 46: AVL Trees — Rotations, Balance Factor, Self-Balancing

## Why This Exists

Binary search trees have a problem that can silently destroy your performance guarantees. Insert the values 1, 2, 3, 4, 5 into a plain BST and you get a linked list — every node has only a right child. Your O(log n) search just became O(n). In production, if your BST receives sorted or nearly-sorted input (which happens more often than you think — timestamps, auto-incrementing IDs, alphabetical data), your "efficient" tree degrades to the worst possible shape.

In 1962, two Soviet mathematicians — Georgy **Adelson-Velsky** and Evgenii **Landis** — published the first self-balancing binary search tree. Their insight: after every insertion or deletion, check whether the tree has become unbalanced, and if so, fix it immediately with local restructuring operations called **rotations**. The resulting data structure guarantees O(log n) height at all times, regardless of insertion order.

This was the AVL tree — the first data structure to prove that you could maintain balance automatically without rebuilding the entire tree. Every self-balancing tree that followed (red-black trees, B-trees, splay trees) builds on the ideas AVL trees introduced.

## Theory

### The Balance Factor Invariant

Every node in an AVL tree carries a **balance factor**:

```
balance_factor(node) = height(left_subtree) - height(right_subtree)
```

The AVL invariant states:

> For every node in the tree, |balance_factor| <= 1.

That is, the balance factor must be -1, 0, or +1. If any node reaches -2 or +2 after an insertion or deletion, the tree is out of balance and must be fixed immediately.

**Why this guarantees O(log n) height**: An AVL tree of height h has at least F(h+2) - 1 nodes, where F is the Fibonacci sequence. Since Fibonacci grows exponentially (~1.618^h), the height of an AVL tree with n nodes is bounded by approximately 1.44 * log2(n). This is slightly worse than a perfectly balanced tree (log2(n)), but the constant factor is small.

### Height Convention

We define:
- Height of `None` (empty subtree) = -1
- Height of a leaf node = 0
- Height of any other node = 1 + max(height(left), height(right))

This makes the math clean: a leaf has balance factor 0 - 0 = 0, which is correct.

### The Four Rotation Cases

When a node becomes unbalanced (balance factor of +2 or -2), exactly one of four cases applies. Each case has a specific rotation that fixes it.

#### Case 1: Left-Left (LL) — Right Rotation

The imbalance is caused by insertion into the **left subtree of the left child**.

```
        z (+2)                  y (0)
       / \                    /   \
      y   T4                 x     z
     / \          =>        / \   / \
    x   T3                T1  T2 T3 T4
   / \
  T1  T2
```

**Fix**: Single right rotation at z. Node y becomes the new root of this subtree.

#### Case 2: Right-Right (RR) — Left Rotation

Mirror of LL. The imbalance is in the **right subtree of the right child**.

```
    z (-2)                    y (0)
   / \                      /   \
  T1   y                   z     x
      / \       =>        / \   / \
     T2  x              T1  T2 T3 T4
        / \
       T3  T4
```

**Fix**: Single left rotation at z.

#### Case 3: Left-Right (LR) — Left Rotation then Right Rotation

The imbalance is in the **right subtree of the left child**. A single right rotation will not fix this — it would just move the problem to the other side.

```
      z (+2)               z (+2)                x (0)
     / \                  / \                   /   \
    y   T4    Left       x   T4   Right        y     z
   / \        rot at    / \       rot at      / \   / \
  T1  x       y =>     y   T3    z =>       T1  T2 T3 T4
     / \              / \
    T2  T3           T1  T2
```

**Fix**: Left rotate at y, then right rotate at z.

#### Case 4: Right-Left (RL) — Right Rotation then Left Rotation

Mirror of LR. The imbalance is in the **left subtree of the right child**.

```
    z (-2)              z (-2)                   x (0)
   / \                 / \                      /   \
  T1   y    Right     T1  x     Left           z     y
      / \   rot at       / \    rot at        / \   / \
     x   T4  y =>       T2  y   z =>        T1  T2 T3 T4
    / \                     / \
   T2  T3                  T3  T4
```

**Fix**: Right rotate at y, then left rotate at z.

### Why Rotations Preserve BST Property

A rotation never violates the BST ordering invariant. Consider a right rotation at z where y is z's left child:

- Before: all keys in y's left subtree < y.key < all keys in y's right subtree < z.key < all keys in z's right subtree
- After: the same ordering holds — y becomes the parent, z becomes y's right child, and y's old right subtree becomes z's left subtree. Every key is still in the correct relative position.

This is why rotations are safe — they restructure the tree's shape without breaking its search property.

### How Rebalancing Decides Which Case

After inserting or deleting a node, walk back up the tree updating heights. At the first node where |balance_factor| == 2:

```
if balance_factor == +2:        # left-heavy
    if balance_factor(left_child) >= 0:
        # LL case -> right rotate
    else:
        # LR case -> left rotate left child, then right rotate
elif balance_factor == -2:      # right-heavy
    if balance_factor(right_child) <= 0:
        # RR case -> left rotate
    else:
        # RL case -> right rotate right child, then left rotate
```

### AVL vs. Red-Black Trees

| Property | AVL Tree | Red-Black Tree |
|----------|----------|----------------|
| Height bound | 1.44 log n (strict) | 2 log n (looser) |
| Lookup speed | Faster (shorter height) | Slightly slower |
| Insert cost | More rotations (up to O(log n)) | At most 2 rotations |
| Delete cost | More rotations (up to O(log n)) | At most 3 rotations |
| Use case | Read-heavy workloads | Write-heavy workloads |

**Where AVL is preferred**: Database indexes where reads vastly outnumber writes. The stricter balancing means shorter trees, which means fewer disk seeks or cache misses per lookup. PostgreSQL's in-memory index structures, for example, benefit from AVL-style tight balancing.

**Where red-black wins**: General-purpose maps and sets (like C++ `std::map`, Java `TreeMap`) where inserts and deletes are frequent. The looser balancing means fewer rotations per mutation.

### Complexity Summary

| Operation | Time Complexity | Rotations |
|-----------|----------------|-----------|
| Search | O(log n) guaranteed | 0 |
| Insert | O(log n) guaranteed | At most 2 (one single or one double) |
| Delete | O(log n) guaranteed | Up to O(log n) along the path |
| Space | O(n) | — |

### Failure Modes and Pitfalls

1. **Forgetting to update heights bottom-up**: After a rotation, both the old root and the new root have changed heights. If you update in the wrong order (parent before child), your balance factors will be stale and future rotations will be incorrect. Always update the node that moves down first, then the node that moves up.

2. **Off-by-one in height of None**: If you define height(None) = 0 instead of -1, a leaf node gets height 1, and your balance factor calculations shift. Be consistent.

3. **Not handling deletion rebalancing up the full path**: Insertion can cause at most one imbalance point (the lowest ancestor that becomes unbalanced). Deletion can cause imbalances all the way up to the root — you must check and fix every ancestor, not just the first unbalanced one.

4. **LR/RL misdiagnosis**: If the left child has a negative balance factor, you have an LR case, not LL. Applying a single right rotation to an LR case does not fix the tree — it just shifts the imbalance. You must do the double rotation.

5. **Memory overhead**: Each node stores an extra height field (or balance factor). For millions of nodes, this adds up. In extremely memory-constrained environments, you might prefer a red-black tree that encodes its balancing information in a single bit.

## Checkpoint Questions

Before moving on, make sure you can answer:

1. What is the balance factor of a node, and what values are legal in an AVL tree?
2. Draw the four rotation cases (LL, RR, LR, RL) and explain when each applies.
3. Why does a right rotation preserve the BST ordering invariant?
4. Why might deletion require O(log n) rotations while insertion requires at most 2?
5. When would you choose an AVL tree over a red-black tree, and vice versa?
6. What is the maximum height of an AVL tree with 1 million nodes?
7. What goes wrong if you forget to update heights after a rotation?
