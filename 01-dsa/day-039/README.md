# Day 39: Tree Diameter, Depth, Balance Checking + Path Sum Problems

## Why These Properties Matter

Days 36-38 built the traversal toolkit. Now we use it to answer **structural questions** about trees: How wide is it? Is it balanced? What paths sum to a target?

These aren't academic exercises. They appear everywhere:
- **Diameter** = longest communication path in a network topology (latency bound)
- **Balance checking** = verifying a BST hasn't degraded to O(n) (performance guarantee)
- **Path sums** = finding routes in weighted graphs, budget allocation in decision trees

The deeper insight: **all of these decompose into the same recursive skeleton**. Once you see it, every tree property problem becomes a variation on one theme.

## Mathematical Definitions

### Diameter

The **diameter** of a binary tree is the length of the longest path between any two nodes. The path length is measured in **number of edges**.

```
diameter(T) = max over all nodes v of (depth_left(v) + depth_right(v))
```

**The critical mistake**: assuming the diameter passes through the root. It does NOT always:

```
        1               Diameter = 4 (path: 5→3→2→4→6)
       / \              This path never touches the root's right subtree.
      2   7
     / \
    3   4
   /     \
  5       6
```

### Depth (Max and Min)

- **max_depth(node)**: number of nodes on the longest root-to-leaf path
- **min_depth(node)**: number of nodes on the shortest root-to-leaf path

```
max_depth(None) = 0
max_depth(node) = 1 + max(max_depth(left), max_depth(right))

min_depth(None) = 0
min_depth(node) = 1 + min(min_depth(left), min_depth(right))
                  BUT only counting paths that reach actual leaves
```

**Gotcha with min_depth**: if a node has only one child, its min depth is NOT 1. You must go through the existing child to reach a leaf.

### Balance

A tree is **height-balanced** if for every node, the height difference between left and right subtrees is at most 1:

```
|height(left) - height(right)| <= 1, for ALL nodes
```

## The Bottom-Up Computation Pattern

Every property here follows the same template:

```
def compute(node):
    if node is None:
        return BASE_VALUE

    left_result = compute(node.left)
    right_result = compute(node.right)

    # Update global answer using left_result + right_result + node
    # Return value that PARENT needs
```

The key distinction: **what you return** (for the parent to use) is often different from **what you track** (the global answer).

| Problem | Return to parent | Track globally |
|---------|-----------------|----------------|
| Diameter | depth of subtree | max(left_depth + right_depth) |
| Balance check | height (or -1 if unbalanced) | whether any subtree failed |
| Max path sum | max single-direction gain | max path through any node |

## Why Naive Balance Checking is O(n^2)

The naive approach calls `height()` at every node:

```python
# BAD: O(n^2) — height() is O(n), called n times
def is_balanced_naive(root):
    if root is None:
        return True
    return (abs(height(root.left) - height(root.right)) <= 1
            and is_balanced_naive(root.left)
            and is_balanced_naive(root.right))
```

For a skewed tree, `height()` traverses O(n) nodes at the root, O(n-1) at the next level, etc. Total: O(n^2).

The fix: compute height **bottom-up** and short-circuit on failure. Each node is visited exactly once: O(n).

## Path Sum Variants

All path sum problems share the recursive skeleton but differ in **where paths can start and end**:

| Variant | Start | End | Technique |
|---------|-------|-----|-----------|
| Root-to-leaf | root | leaf | Subtract node.val, check remainder at leaf |
| Root-to-any | root | any node | Subtract node.val, check remainder at each node |
| Any-to-any downward | any node | any descendant | **Prefix sums** (like subarray sum = k) |
| Any-to-any (max sum) | any node | any node | Bottom-up: return max single-direction gain |

### The Prefix Sum Technique for Path Counts

Counting paths that sum to a target from **any node to any descendant** is the tree analog of "subarray sum equals k" (Day 15).

Maintain a running sum from root. At each node:
- `current_sum - target` appears in prefix map? That many paths end here.
- Add current_sum to prefix map, recurse, then **remove it** (backtrack).

This converts an O(n^2) brute force into O(n).

## Failure Modes

1. **Diameter doesn't pass through root**: The most common bug. You MUST check every node as a potential "turning point" for the longest path.
2. **min_depth with single child**: A node with only a left child has min_depth = 1 + min_depth(left), NOT 1. The missing child is not a valid leaf path.
3. **Forgetting to backtrack prefix sums**: In path_sum_count, you must remove the current node's prefix sum after recursing. Otherwise, sibling subtrees see stale entries.
4. **Negative values in max path sum**: You must clamp child contributions to 0 (don't take a negative-sum path). But the answer itself CAN be negative (single negative node).
5. **Off-by-one in depth vs edges**: Some problems count edges, others count nodes. Diameter is typically edges. max_depth is typically nodes. Always verify the definition.

## What to Build Today

1. `diameter(root)` -- O(n) bottom-up, tracking max diameter as side effect
2. `max_depth(root)` and `min_depth(root)`
3. `is_balanced(root)` -- O(n) single pass with early termination
4. `path_sum_root_to_leaf(root, target)` -- does any root-to-leaf path equal target?
5. `all_root_to_leaf_paths(root)` -- enumerate all paths
6. `path_sum_count(root, target)` -- count paths from any node downward (prefix sum technique)
7. `max_path_sum(root)` -- maximum sum path between any two nodes

## Checkpoint Questions

Before moving to Day 40, you should be able to answer:
- Why can't you compute diameter by just finding the two deepest leaves? (Hint: they might be in the same subtree.)
- What's the recurrence for diameter, and why does each node need to "report" its depth to its parent while "recording" a potential diameter?
- Why is the prefix sum backtracking step essential in path_sum_count? What breaks if you skip it?
- In max_path_sum, why do you return `node.val + max(left, right)` to the parent but track `node.val + left + right` as a candidate answer?
- How does the O(n) balance check achieve early termination, and what sentinel value does it use?
