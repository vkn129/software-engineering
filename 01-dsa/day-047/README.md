# Day 47: Red-Black Trees — Relaxed Balancing

## Why This Exists

You have AVL trees. They are perfectly balanced, giving O(log n) for every operation. So why would anyone invent a different self-balancing tree that allows **twice the height** of an AVL tree?

Because AVL trees are **too strict**. Their balance factor of {-1, 0, 1} means almost every insertion or deletion triggers rotations — sometimes cascading all the way up to the root. In a read-heavy workload, this strictness pays off: AVL lookups are slightly faster because the tree is shorter. But in a write-heavy workload, those rotations are expensive. If you are inserting and deleting millions of keys per second — which is exactly what a database index or an OS scheduler does — you need a tree that tolerates a little imbalance in exchange for **fewer structural changes**.

Red-black trees make this trade-off explicit. They relax the balance condition by coloring nodes red or black and enforcing a set of invariants that guarantee the tree's height is at most **2 * log2(n + 1)**. This is taller than an AVL tree's ~1.44 * log2(n), but the relaxed constraints mean inserts require at most **2 rotations** and deletes require at most **3 rotations** — compared to AVL's O(log n) rotations in the worst case.

This is why Java's `TreeMap` and `TreeSet`, C++'s `std::map` and `std::set`, Linux's Completely Fair Scheduler (CFS), and the Linux kernel's virtual memory area (VMA) management all use red-black trees instead of AVL trees. They need guaranteed-fast mutations, and they can tolerate slightly slower lookups.

## The 5 Red-Black Properties

A binary search tree is a red-black tree if and only if it satisfies **all five** of these properties simultaneously:

| # | Property | Why It Matters |
|---|----------|---------------|
| 1 | **Every node is either red or black** | The coloring is the mechanism — it encodes balance information in a single bit per node |
| 2 | **The root is black** | Convention that anchors the invariants; a red root would mean one extra red node on every path |
| 3 | **Every leaf (NIL/sentinel) is black** | NIL nodes are conceptual — they simplify the case analysis by ensuring every real node has two children |
| 4 | **If a node is red, both its children are black** | No two consecutive reds on any path — this is the constraint that prevents extreme imbalance |
| 5 | **Every path from a node to its descendant NIL leaves has the same number of black nodes** | This is the **black-height** invariant — the key property that bounds the tree's height |

### Why These Properties Guarantee h <= 2 * log2(n + 1)

The proof follows from Property 5 (equal black-height) and Property 4 (no consecutive reds):

1. **Black-height definition**: The black-height `bh(x)` of a node `x` is the number of black nodes on any path from `x` (exclusive) to a NIL leaf. By Property 5, this is well-defined (the same for all paths).

2. **Subtree size bound**: A subtree rooted at node `x` contains at least `2^bh(x) - 1` internal nodes. Proof by induction: a NIL has `bh = 0` and `2^0 - 1 = 0` nodes. An internal node `x` with black-height `bh(x)` has children with black-height at least `bh(x) - 1`, so it has at least `2 * (2^(bh(x)-1) - 1) + 1 = 2^bh(x) - 1` nodes.

3. **Height bound**: Let `h` be the tree's height. By Property 4, at least half the nodes on any root-to-leaf path are black. So `bh(root) >= h/2`. Combining with the subtree bound: `n >= 2^(h/2) - 1`, which gives `h <= 2 * log2(n + 1)`.

This means a red-black tree with 1 million nodes has height at most 40, compared to AVL's ~30. The 33% taller tree is the price for cheaper mutations.

## Insert Fixup: The 3 Cases

After a standard BST insert (new node is colored **red**), Property 4 may be violated if the parent is also red. The fixup procedure walks up the tree, handling three cases based on the **uncle** (parent's sibling):

```
Case 1: Uncle is RED
    → Recolor parent and uncle to black, grandparent to red.
    → Move the violation up to the grandparent. Repeat.

Case 2: Uncle is BLACK and node is an "inner" child (e.g., right child of left parent)
    → Rotate node's parent in the opposite direction (left-rotate).
    → This converts to Case 3.

Case 3: Uncle is BLACK and node is an "outer" child (e.g., left child of left parent)
    → Rotate grandparent in the opposite direction (right-rotate).
    → Recolor: parent becomes black, grandparent becomes red.
    → Done.
```

Key insight: Case 1 can propagate up the tree (O(log n) recolorings), but Cases 2 and 3 each do at most one rotation and terminate. So **insert does at most 2 rotations total**.

## Delete Fixup: The 4 Cases

Deletion is harder because removing a black node violates Property 5 (black-height). The fixup considers the **sibling** of the replacement node:

```
Case 1: Sibling is RED
    → Rotate parent toward the deficient side.
    → Recolor sibling to black, parent to red.
    → New sibling is now black → fall into Cases 2-4.

Case 2: Sibling is BLACK with two BLACK children
    → Recolor sibling to red. The "extra blackness" moves up.
    → If parent was red, color it black → done.
    → If parent was black, repeat fixup at parent.

Case 3: Sibling is BLACK, sibling's far child is BLACK, near child is RED
    → Rotate sibling away from the deficient side.
    → Recolor to convert to Case 4.

Case 4: Sibling is BLACK, sibling's far child is RED
    → Rotate parent toward the deficient side.
    → Recolor: sibling takes parent's color, parent becomes black,
      far child becomes black.
    → Done. Black-height restored.
```

Delete does at most **3 rotations total**.

## AVL vs. Red-Black: When to Use Which

| Criterion | AVL | Red-Black |
|-----------|-----|-----------|
| Max height | ~1.44 log n | ~2 log n |
| Lookup speed | Slightly faster (shorter tree) | Slightly slower |
| Insert rotations | O(log n) worst case | At most 2 |
| Delete rotations | O(log n) worst case | At most 3 |
| Insert recolorings | N/A | O(log n) but cheap |
| Memory per node | Balance factor (2 bits) | Color (1 bit) |
| Best for | Read-heavy workloads | Write-heavy workloads |
| Used by | Databases (some), in-memory lookups | Java TreeMap, C++ std::map, Linux kernel |

Rule of thumb: if lookups dominate, consider AVL. If inserts/deletes are frequent, red-black wins.

## Connection to 2-3-4 Trees

A red-black tree is a **binary encoding of a 2-3-4 tree**. The mapping:

- A **black node** with no red children = a **2-node** (one key, two children)
- A **black node** with one red child = a **3-node** (two keys, three children)
- A **black node** with two red children = a **4-node** (three keys, four children)

This explains why red-black properties work: they are simply the rules of 2-3-4 trees translated into a binary tree. The black-height invariant corresponds to the fact that all leaves of a 2-3-4 tree are at the same depth.

### Left-Leaning Red-Black Trees (LLRB)

Sedgewick's simplification restricts the correspondence to **2-3 trees** (no 4-nodes) by adding one extra invariant: **red links lean left only**. This means:
- A node can have a red left child but never a red right child (unless we temporarily violate during fixup)
- This cuts the number of cases roughly in half
- The trade-off: slightly more rotations per operation, but dramatically simpler code

## Where Red-Black Trees Are Used

| System | What It Uses RB Trees For |
|--------|--------------------------|
| **Java TreeMap / TreeSet** | Sorted map/set backed by RB tree — O(log n) get/put with guaranteed ordering |
| **C++ std::map / std::set** | The standard demands sorted containers; most implementations use RB trees |
| **Linux CFS Scheduler** | Tasks sorted by virtual runtime in an RB tree; the leftmost node is the next task to run |
| **Linux kernel VMA** | Virtual memory areas for each process stored in an RB tree for fast range lookups |
| **Nginx timer events** | Red-black tree of pending timers sorted by expiration time |

## Failure Modes

1. **Forgetting to fix the root color**: After insert/delete fixup, the root might end up red. Always force it to black at the end.

2. **Incorrect uncle/sibling identification**: Getting left/right mixed up in the mirror cases is the #1 source of bugs. Be systematic: if parent is a left child, uncle is grandparent's right child, and vice versa.

3. **NIL sentinel vs. None**: Using `None` instead of a sentinel NIL node makes the code messier because you must check for `None` before accessing `.color`. A sentinel simplifies everything.

4. **Transplant not updating parent pointer**: When replacing a subtree during delete, you must update the replacement's parent pointer. Missing this breaks the tree structure silently.

5. **Off-by-one in black-height**: The black-height of a NIL leaf is 0, not 1. The black-height of a black node includes itself for its parent's count but not for its own path count. Be precise about the definition.

## Checkpoint Questions

Before moving on, you should be able to answer:

1. Why does coloring a new node red (not black) minimize violations on insert?
2. How many rotations does an RB insert do in the worst case? Why?
3. Why is Property 5 (equal black-height) the one that really controls the height?
4. If you have a red-black tree with black-height 5, what is the minimum and maximum number of nodes it could contain?
5. Draw the 2-3-4 tree equivalent of an RB tree with nodes [1(B), 2(R), 3(B), 4(R), 5(B)].
6. Why does Linux's CFS scheduler need a self-balancing tree instead of a heap?
7. What happens if you violate Property 4 but maintain Property 5? Is the tree still O(log n)?
