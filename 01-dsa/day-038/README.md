# Day 38: Lowest Common Ancestor (LCA)

## Why LCA Exists

You have two nodes in a tree. You need to find the deepest node that is an ancestor of both. This sounds abstract until you realize it powers three systems you use daily:

1. **git merge-base**: When you run `git merge feature main`, git finds the LCA of both branch tips in the commit DAG. That LCA is the "merge base" -- the point where the branches diverged. Without it, git can't compute the three-way diff needed for merging.

2. **Filesystem paths**: Given `/home/user/docs/report.txt` and `/home/user/photos/vacation.jpg`, the common ancestor directory is `/home/user/`. Every `..` in a relative path is walking toward the LCA.

3. **Network routing**: In a hierarchical routing topology, the LCA of two hosts determines the highest-level router that must handle traffic between them. Closer LCA = less backbone traffic.

The forcing function: **any time two entities share a hierarchical structure, their relationship is defined by their LCA.**

## The Mathematical Model

Given a rooted tree T and two nodes u, v:

```
LCA(u, v) = the deepest node w such that w is an ancestor of both u and v
```

Properties:
- LCA(u, u) = u (every node is its own ancestor)
- LCA(u, v) = u if u is an ancestor of v
- LCA(u, v) = LCA(v, u) (symmetric)
- If u and v are in different subtrees of w, then LCA(u, v) = w

## Three Approaches and Their Trade-offs

### Approach 1: Parent Pointers — O(n) time, O(n) space per query

If each node stores a pointer to its parent, LCA reduces to **finding the intersection of two linked lists** (the paths from each node to the root). This is the same algorithm from Day 21 (linked list intersection).

```
Walk both nodes to root, measuring depths.
Advance the deeper node by |depth(u) - depth(v)| steps.
Walk both up in lockstep until they meet.
```

**When to use**: When you already have parent pointers (DOM trees, git commit objects). Adding parent pointers doubles memory but makes LCA trivial.

### Approach 2: Recursive — O(n) time, O(h) space per query

The elegant insight: traverse the tree once. For each node, check if p or q is in its left subtree, right subtree, or is the node itself.

```
If both targets are in different subtrees → current node is LCA
If both are in the same subtree → LCA is deeper in that subtree
If current node IS one of the targets → current node is LCA
```

**When to use**: One-off queries on general binary trees. Simple to implement, hard to beat for single queries.

### Approach 3: Binary Lifting — O(n log n) preprocessing, O(log n) per query

For **repeated queries** on the same tree, O(n) per query is unacceptable. Binary lifting preprocesses the tree so each query takes O(log n).

The idea: for each node, precompute its ancestor at distance 1, 2, 4, 8, 16, ... (powers of 2). Then to jump k levels up, decompose k into binary and take the corresponding jumps.

```
up[node][j] = ancestor 2^j levels above node
up[node][0] = parent(node)
up[node][j] = up[up[node][j-1]][j-1]   (jump 2^(j-1) twice)
```

To find LCA(u, v):
1. Bring both nodes to the same depth using binary jumps
2. Binary-search for the LCA by jumping both nodes up together

**When to use**: Trees with millions of nodes and thousands of LCA queries (competitive programming, phylogenetic trees, network topology analysis).

### BST Optimization — O(h) time

For Binary Search Trees, we don't need full traversal. The BST property tells us:
- If both values < current → LCA is in left subtree
- If both values > current → LCA is in right subtree
- Otherwise → current node is the LCA (the "split point")

This is O(h), which is O(log n) for balanced BSTs.

## Why Naive O(n) Per Query Is Unacceptable

Consider a phylogenetic tree with 10 million species. A bioinformatics pipeline needs to compute LCA for every pair in a set of 10,000 species. That's ~50 million LCA queries.

- Naive: 50M * 10M = 5 * 10^14 operations. **Years** of computation.
- Binary lifting: 10M * 23 preprocessing + 50M * 23 queries ~ 10^9 operations. **Seconds.**

The preprocessing cost pays for itself after just 2-3 queries on a large tree.

## Connection to Other Problems

| Problem | How LCA Helps |
|---------|---------------|
| Distance between two nodes | dist(u,v) = depth(u) + depth(v) - 2*depth(LCA(u,v)) |
| Path queries (sum, max, min) | Split path u→v into u→LCA and v→LCA |
| Tree isomorphism | Compare subtree structures rooted at LCA |
| Range minimum query (RMQ) | LCA on Cartesian tree = RMQ on array (Euler tour reduction) |

## Failure Modes

1. **Assuming nodes exist in the tree**: If p or q isn't in the tree, the recursive approach silently returns the wrong answer. Production code must validate inputs.
2. **Forgetting the p == LCA case**: If p is an ancestor of q, then p itself is the LCA. Missing this case is the most common bug.
3. **Binary lifting overflow**: If `up[node][j-1]` is the root (or null), `up[node][j]` must also be root/null, not undefined. Forgetting this corrupts the sparse table.
4. **BST approach on non-BST**: Using value comparisons on a general binary tree gives wrong answers. Always verify the tree is actually a BST before using the optimized approach.
5. **Stack overflow on deep trees**: The recursive approach uses O(h) stack space. On a degenerate tree with 100K nodes, Python crashes. Use iterative approaches or increase the recursion limit for production.

## What to Build Today

1. `lca_with_parent(p, q)` -- parent pointer approach (linked list intersection)
2. `lca_recursive(root, p, q)` -- the elegant O(n) recursive solution
3. `lca_bst(root, p, q)` -- BST-optimized using value comparisons
4. `LCAPreprocessor` class -- binary lifting for O(log n) repeated queries

## Checkpoint Questions

Before moving to Day 39, you should be able to answer:
- Why does the recursive LCA algorithm work even when one target is an ancestor of the other?
- What is the time complexity of binary lifting preprocessing, and why is LOG_MAX = ceil(log2(n))?
- How does `git merge-base` relate to LCA? What happens when there are multiple merge bases (criss-cross merges)?
- Why can't you use the BST optimization on a general binary tree?
- How would you compute the distance between two nodes using only their depths and the LCA?
