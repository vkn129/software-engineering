# Day 48: Splay Trees — Amortized O(log n), Why Caches Love Them

## Why This Exists

AVL trees and red-black trees guarantee O(log n) per operation by storing extra metadata (height or color) at every node and running rebalancing logic after each mutation. This works, but it pays a cost on *every* operation regardless of the access pattern.

Splay trees take a radically different approach: **no metadata at all**. No height, no color, no balance factor. Instead, every time you access a node, you **move it to the root** through a sequence of rotations called *splaying*. This sounds expensive — and for any single operation, it can be. A single splay might take O(n). But across a sequence of operations, the amortized cost is O(log n) per operation.

The key insight is the **working set property**: recently accessed elements stay near the root and are fast to access again. If your workload has **temporal locality** — you tend to re-access elements you recently accessed — splay trees outperform balanced BSTs because frequently used nodes migrate to the top of the tree.

This is why caches love splay trees. Caches exploit temporal locality by definition. Garbage collectors, network routers, and memory allocators all exhibit access patterns where a small subset of elements is "hot" at any given time. Splay trees naturally adapt to this pattern without any explicit frequency counting or recency tracking.

Daniel Sleator and Robert Tarjan invented splay trees in 1985. Tarjan is the same person behind union-find, strongly connected components, and amortized analysis itself. Splay trees are a masterclass in the idea that **worst-case per-operation guarantees are not always what matters** — what matters is total cost over time.

## Theory (40 min)

### The Splay Operation

The core idea: after accessing node X, **splay X to the root**. Splaying is a sequence of rotations that depends on X's position relative to its parent P and grandparent G (if it exists).

There are three cases:

#### Case 1: Zig (X is a child of the root)

X is one step from the root. Perform a single rotation to make X the root.

```
    P              X
   / \            / \
  X   C   ->    A   P
 / \               / \
A   B             B   C
```

This only happens when P is the root. It is the base case.

#### Case 2: Zig-Zig (X and P are both left children, or both right children)

X and P are on the same side. Rotate P first, then rotate X. The order matters — rotating P first (not X first) is what gives the amortized O(log n) guarantee.

```
      G              X
     / \            / \
    P   D          A   P
   / \       ->       / \
  X   C              B   G
 / \                    / \
A   B                  C   D
```

**Why rotate P first?** If you rotate X first (like in a naive move-to-root heuristic), you get O(n) amortized cost. Sleator and Tarjan's key discovery was that rotating P before X flattens the path, roughly halving the depth of all nodes along it. This path compression is what makes the amortized analysis work.

#### Case 3: Zig-Zag (X is a left child and P is a right child, or vice versa)

X and P are on opposite sides. Rotate X twice — once around P, once around G. This is like an AVL double rotation.

```
    G              X
   / \           /   \
  P   D   ->   P     G
 / \           / \   / \
A   X         A   B C   D
   / \
  B   C
```

#### Splaying Process

To splay X to the root, repeatedly apply the appropriate case (zig, zig-zig, or zig-zag) based on X's position relative to its parent and grandparent, moving X up two levels each time (or one level in the zig case when X's parent is the root).

### Operations Built on Splay

**Search(key)**: Walk down the tree like a normal BST search. If found, splay the node to the root. If not found, splay the last node visited (the "almost found" node).

**Insert(key)**: Insert like a normal BST, then splay the new node to the root.

**Delete(key)**: Splay the node to the root, remove it, then merge the left and right subtrees. To merge: splay the maximum of the left subtree (so the left subtree's root has no right child), then attach the right subtree as its right child.

**Split(key)**: Splay key to the root. The left subtree contains all keys < key, the right subtree contains all keys > key. This gives you two trees in O(log n) amortized.

**Merge(T1, T2)**: Requires all keys in T1 < all keys in T2. Splay the maximum of T1 to the root (it has no right child), then attach T2 as its right child. O(log n) amortized.

### Amortized Analysis: The Potential Method

The amortized cost is proven using the **potential method**. Define a potential function:

```
Phi(T) = sum over all nodes X of log(size(X))
```

Where size(X) is the number of nodes in the subtree rooted at X, and log is base 2.

The **amortized cost** of an operation = actual cost + change in potential.

The key result: splaying a node at depth d has amortized cost at most 3 * log(n) + 1, regardless of the actual depth. When a deep node is splayed (high actual cost), the tree becomes more balanced (potential drops), and the drop in potential "pays for" the expensive operation.

This is the genius of splay trees: expensive operations restructure the tree to make future operations cheaper.

### The Working Set Property

Splay trees satisfy the **working set theorem**: the amortized cost of accessing element X is O(log W(X)), where W(X) is the number of distinct elements accessed since the last access to X.

In plain English: if you just accessed X, it is near the root. Accessing it again is fast. If you have not accessed X in a while (many other elements were accessed in between), it may have drifted deeper, and accessing it is slower.

This is exactly what caches want. A cache hit should be fast. Splay trees deliver this naturally — hot elements rise to the top, cold elements sink.

### Where Splay Trees Excel

1. **Caches**: Temporal locality means recently accessed items are accessed again soon. Splay trees keep them near the root.

2. **Garbage collectors**: Objects tend to be allocated and freed in clusters. The allocator's free-list tree benefits from splay behavior.

3. **Network routers**: Routing table lookups have temporal locality — the same destinations are looked up repeatedly in bursts.

4. **Compression algorithms**: Move-to-front coding in algorithms like BWT (used in bzip2) exploits the same locality that splay trees exploit.

5. **Any workload where a small "working set" is accessed frequently**: Splay trees adapt to the working set automatically, without any parameter tuning.

### Comparison with AVL and Red-Black Trees

| Property | AVL Tree | Red-Black Tree | Splay Tree |
|---|---|---|---|
| Worst-case per operation | O(log n) | O(log n) | O(n) |
| Amortized per operation | O(log n) | O(log n) | O(log n) |
| Extra metadata per node | Height (int) | Color (bit) | None |
| Cache-friendly access | No adaptation | No adaptation | Yes — hot nodes near root |
| Working set property | No | No | Yes |
| Implementation complexity | Moderate | High | Low |
| Best for uniform access | Competitive | Competitive | Slightly worse |
| Best for skewed access | No advantage | No advantage | Major advantage |

**When NOT to use splay trees**: When you need guaranteed O(log n) per operation (real-time systems), or when your access pattern is truly uniform random (no locality to exploit). In purely adversarial or sequential access patterns, individual operations can be O(n), which may be unacceptable even if the amortized cost is fine.

### Failure Modes

**Sequential access**: If you access all n elements in sorted order, each access walks the entire spine of the tree. Individual operations are O(n). The amortized cost is still O(log n) per operation over the whole sequence, but individual latency spikes can be severe.

**No locality**: If every access is to a uniformly random element that was not recently accessed, splay trees provide no benefit over balanced BSTs, and the constant overhead of splaying makes them slightly slower.

**Concurrent access**: Splay trees mutate the tree on every read (even searches splay). This makes them hostile to concurrent access — every read is a write. Read-heavy concurrent workloads are a poor fit unless you use a variant like semi-splay trees.

## Practice (20 min)

Work through `practice.py`. You will implement splay tree operations and explore the working set property. Each exercise tests a different aspect of splay tree behavior.

## Daily Project

Run `splay_tree.py` to see:
- A full splay tree implementation with all three rotation cases
- Visual demonstrations of the splay operation restructuring the tree
- Split and merge operations
- Access counting that demonstrates the working set property
- Performance comparison: uniform random vs temporal locality access patterns

Study how the splay operation moves nodes to the root and flattens the tree along the path. Then study how split and merge decompose into splay operations — this pattern appears in many advanced data structures (link-cut trees, for example).

## Checkpoint Questions

1. Why does the zig-zig case rotate the parent first instead of the child? What goes wrong (in terms of amortized complexity) if you rotate the child first?

2. A splay tree has no height or color metadata. What is the trade-off? What capability do you lose by having no per-operation worst-case guarantee?

3. You are building a DNS resolver cache where 90% of lookups are for the same 100 domains. Would a splay tree or a red-black tree be a better choice for the underlying data structure? Justify your answer using the working set property.

4. Splay trees mutate the tree structure on every search (not just insert/delete). Why does this make them problematic for concurrent (multi-threaded) workloads? What modifications would you need?

5. The amortized analysis uses a potential function Phi = sum of log(size(X)) over all nodes. Intuitively, why does splaying a deep node decrease the potential? What does a decrease in potential "mean" in terms of tree shape?
