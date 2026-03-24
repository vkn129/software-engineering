# Day 36: Binary Tree Fundamentals

## Why Trees Exist

Every data structure we've built so far is **linear** — arrays, linked lists, stacks, queues. They model sequences. But the real world is **hierarchical**: file systems, org charts, HTML DOM, mathematical expressions, decision processes.

The forcing function: **linear structures can't represent hierarchy without O(n) overhead**. If you flatten a file system into an array, finding all files in `/home/user/docs/` requires scanning every entry. A tree gives you O(depth) navigation.

## The Mathematical Model

A **binary tree** is a recursive structure:
- **Base case**: An empty tree (None/null)
- **Recursive case**: A node with a value, a left subtree, and a right subtree

```
T = ∅ | (value, T_left, T_right)
```

This recursive definition is why every tree algorithm naturally decomposes into:
1. Process the current node
2. Recurse on left subtree
3. Recurse on right subtree

The **order** in which you do these three things defines the traversal.

## Terminology — Precise Definitions

| Term | Definition | Why It Matters |
|------|-----------|----------------|
| **Root** | The unique node with no parent | Entry point for all operations |
| **Leaf** | Node with no children | Base case of recursion |
| **Depth** of node | Number of edges from root to node | Root has depth 0 |
| **Height** of node | Number of edges on longest path to leaf | Leaves have height 0 |
| **Height** of tree | Height of root | Determines worst-case for most operations |
| **Level** | Set of all nodes at same depth | BFS processes level by level |
| **Complete** | Every level full except possibly last, filled left-to-right | Enables array representation (heaps) |
| **Full** | Every node has 0 or 2 children | Simplifies many proofs |
| **Perfect** | All internal nodes have 2 children, all leaves at same depth | Has exactly 2^(h+1) - 1 nodes |
| **Balanced** | Height = O(log n) | Guarantees efficient operations |

### Critical Property: Node Count vs Height

- **Best case** (balanced): h = ⌊log₂(n)⌋ → n nodes give O(log n) height
- **Worst case** (degenerate): h = n - 1 → a linked list disguised as a tree
- This is why BST degradation is catastrophic — and why self-balancing trees exist (Days 46-48)

## The Four Traversals

### Why Traversal Order Matters

Each traversal order exists because a specific class of problems needs nodes in that order:

| Traversal | Order | Use Case | Why That Order |
|-----------|-------|----------|---------------|
| **Inorder** | Left → Root → Right | BST gives sorted output | Processes values in order |
| **Preorder** | Root → Left → Right | Serialize/copy a tree | Parent before children |
| **Postorder** | Left → Right → Root | Delete a tree, evaluate expressions | Children before parent (bottom-up) |
| **Level-order (BFS)** | Level by level | Shortest path, level averages | Explores by distance from root |

### The Stack/Queue Duality

- **DFS** (in/pre/post) uses a **stack** — either the call stack (recursion) or explicit
- **BFS** (level-order) uses a **queue** — process nodes in FIFO order

This connects directly to Day 29 (stacks) and Day 31 (queues). Trees are where those abstractions become essential.

## Recursive vs Iterative DFS

Recursive DFS is elegant but has two problems:
1. **Stack overflow** on deep trees (Python default recursion limit: 1000)
2. **No easy pause/resume** — can't process one node, do something else, continue

Iterative DFS with an explicit stack solves both. The key insight: **you're doing exactly what the call stack does, but manually**.

### The Iterative Inorder Trick

Inorder is the trickiest to do iteratively because the root is processed **between** its children. The pattern:

```
Go left as far as possible, pushing nodes onto stack
Pop → that's the current node (process it)
Move to right child
Repeat
```

This simulates the recursive call stack: push = entering a function call, pop = returning from one.

## Counterfactual: What If Trees Didn't Exist?

Without trees:
- **File systems** would be flat directories (early DOS) — no nesting, no organization at scale
- **Compilers** couldn't represent `(a + b) * c` — expression evaluation would require stack manipulation (which is tree simulation anyway)
- **Databases** would rely on hash indexes only — no range queries, no ordered iteration
- **HTML/XML** would be flat markup — no nesting, no components

Every "workaround" for not having trees ends up reinventing trees with different syntax.

## Failure Modes

1. **Recursion depth**: A tree with 10,000 nodes in a chain hits Python's stack limit. Always consider iterative for production code.
2. **Assuming balance**: If you write code assuming height = O(log n), a degenerate input creates O(n) performance — the classic BST trap.
3. **Mutating during traversal**: Modifying the tree while traversing it invalidates iterator state. Production trees need careful concurrency design.
4. **Confusing depth vs height**: Depth counts DOWN from root, height counts UP from leaves. Mixing them up breaks level-order logic.

## What to Build Today

1. `TreeNode` class and tree construction utilities
2. All four traversals — recursive AND iterative
3. Utility functions: height, size, is_balanced, is_symmetric
4. Practice problems testing traversal mastery

## Checkpoint Questions

Before moving to Day 37, you should be able to answer:
- Why is iterative inorder harder than iterative preorder? (Hint: when is the root processed?)
- What's the space complexity of recursive DFS on a balanced tree vs a degenerate tree?
- Why does BFS use O(w) space where w is max width, while DFS uses O(h) where h is height?
- On a perfect binary tree with 1 million nodes, what's the maximum recursion depth?
