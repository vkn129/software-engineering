# Day 40: Morris Traversal — O(1) Space Inorder Without Stack + Threaded Binary Trees

## Why O(1) Space Traversal Matters

Every traversal we have built so far uses O(h) space:
- **Recursive DFS**: The call stack holds up to h frames
- **Iterative DFS**: An explicit stack holds up to h nodes
- **BFS**: A queue holds up to w nodes (width of the widest level)

For a balanced tree with 1 billion nodes, h = 30, so O(h) is fine. But consider:
- **Embedded systems** with kilobytes of RAM traversing sensor trees
- **Massive unbalanced trees** where h approaches n (a linked-list-shaped tree with 10 million nodes needs a 10-million-entry stack)
- **Memory-constrained batch processing** where you traverse millions of trees and every byte counts

The question: can we traverse a binary tree using only O(1) extra space — no stack, no recursion, no parent pointers?

**Yes. That is Morris Traversal.**

## The Brilliant Insight: Threads

The key observation is simple but profound: **a binary tree with n nodes has n+1 null pointers**. Every leaf has two nulls, and internal nodes with one child have one null. These null pointers are wasted space.

What if we temporarily repurpose those null pointers to point back to ancestor nodes — creating "threads" that let us navigate back up without a stack?

### The Threading Idea

In an inorder traversal, after we finish processing a node's left subtree, we need to return to that node. Normally the stack does this. Morris instead:

1. Finds the **inorder predecessor** of the current node (the rightmost node in its left subtree)
2. Sets that predecessor's right pointer to the current node (creates a thread)
3. Moves left
4. Later, when we follow the thread back, we detect it (predecessor's right == current) and remove it

The tree is temporarily modified during traversal, then fully restored.

```
Original:          After threading 4→2→1:

        4                  4
       / \                / \
      2   5              2   5
     / \                / \
    1   3              1   3
                        \   \
                    (thread→2) (thread→4)
```

## Morris Inorder Algorithm — Step by Step

```
current = root
while current is not None:
    if current.left is None:
        VISIT current           # no left subtree, process now
        current = current.right # move right (may follow a thread)
    else:
        # Find inorder predecessor (rightmost in left subtree)
        predecessor = current.left
        while predecessor.right is not None and predecessor.right is not current:
            predecessor = predecessor.right

        if predecessor.right is None:
            # First visit: create thread, move left
            predecessor.right = current
            current = current.left
        else:
            # Second visit: thread exists, remove it, process current
            predecessor.right = None
            VISIT current
            current = current.right
```

Each node is visited at most twice (once to create the thread, once to remove it), so the algorithm is O(n) time despite the inner while loop.

## Why O(n) Time Despite Nested Loops?

This trips people up. The inner `while` loop finding predecessors looks like it could make things O(n^2). But consider: every edge in the tree is traversed at most twice during the entire algorithm — once going down to find the predecessor, once going back up following the thread. Since a tree with n nodes has n-1 edges, the total work across ALL iterations of the inner loop is O(n). This is an amortized argument, similar to why a series of n stack operations is O(n) total even though individual operations vary.

## Morris Preorder — The Subtle Difference

For preorder, the only change is WHEN we visit the node:
- **Inorder**: Visit on the SECOND encounter (after left subtree is done)
- **Preorder**: Visit on the FIRST encounter (before going left)

This means we move `VISIT current` to the `predecessor.right is None` branch.

## Threaded Binary Trees — Making Threads Permanent

Morris creates temporary threads and removes them. A **threaded binary tree** makes these threads permanent:

- **Right-threaded**: Every null right pointer points to the inorder successor
- **Left-threaded**: Every null left pointer points to the inorder predecessor
- **Fully threaded**: Both

Each node stores a boolean flag (`right_is_thread`) to distinguish real children from threads.

### Why Threaded Trees Exist

Threaded binary trees were invented by Perlis and Thornton in 1960 — before Morris traversal (1979). The motivation:
- O(1) space inorder traversal at any time, without modifying the tree
- O(1) inorder successor/predecessor lookup (no need to walk up or keep a stack)
- Useful in database indexes where you need to iterate sorted records without extra memory

The tradeoff: every insert/delete must maintain the threading invariant, adding complexity to mutations.

## When NOT to Use Morris Traversal

1. **Concurrent access**: Morris temporarily modifies tree structure. If another thread reads the tree during traversal, it sees corrupted pointers. This is a showstopper for concurrent systems.
2. **Immutable trees**: Functional programming, persistent data structures, or const-qualified trees cannot be modified. Morris is impossible.
3. **When O(h) space is fine**: For balanced trees, O(log n) stack space is trivial. Morris adds code complexity for no practical benefit.
4. **Postorder**: Morris postorder is significantly more complex than inorder/preorder. Prefer iterative postorder with a stack unless space is truly critical.

## Connection to Previous Days

- **Day 36**: We built recursive and iterative traversals with O(h) space. Morris eliminates that space.
- **Day 37 (BST)**: Morris `is_bst` validates a BST in O(1) space by checking inorder sortedness.
- **Day 29 (Stacks)**: The explicit stack in iterative traversal is what Morris replaces.

## Failure Modes

1. **Forgetting to restore threads**: If you exit early (break out of the loop), the tree is left in a corrupted state with dangling threads. Always traverse to completion or add cleanup logic.
2. **Infinite loops**: If thread removal is buggy, following a thread leads back to the same node forever. The `predecessor.right is not current` guard in the inner loop prevents this.
3. **Applying to trees with parent pointers**: If nodes already have parent pointers, threads are unnecessary — just follow parent pointers. Using Morris adds complexity for no gain.
4. **Concurrent modification**: As noted above, Morris + concurrent readers = data corruption.

## What to Build Today

1. `morris_inorder(root)` — O(1) space inorder traversal
2. `morris_preorder(root)` — O(1) space preorder traversal
3. `is_bst_morris(root)` — validate BST without extra space
4. `kth_smallest_morris(root, k)` — find kth smallest in BST
5. `ThreadedBinaryTree` — permanent threading for O(1) successor lookup
6. Practice: recover a BST with two swapped nodes using Morris

## Checkpoint Questions

Before moving to Day 41, you should be able to answer:
- Why does Morris traversal run in O(n) time despite the nested while loop? (Hint: count total edge traversals, not per-node work.)
- What happens if you break out of a Morris traversal early? How would you make early exit safe?
- Why is Morris preorder the same algorithm with the VISIT moved, but Morris postorder is fundamentally harder?
- In a threaded binary tree, how do you distinguish a real right child from a thread? Why is this flag necessary?
- When would you choose a threaded binary tree over Morris traversal?
