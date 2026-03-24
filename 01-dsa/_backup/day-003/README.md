# Day 3: Recurrence Relations & Master Theorem

## Why This Exists

Yesterday you learned to write recursive functions. Today you learn to answer the question every engineer should ask after writing one: "How fast is this, actually?"

When you write a loop, counting operations is straightforward — you see the iteration, you count. But when a function calls itself, the total work is hidden behind layers of self-reference. T(n) = 2T(n/2) + n looks simple on paper, but it encodes an entire tree of computation. If you cannot solve recurrences, you cannot analyze any divide-and-conquer algorithm, any tree operation, any dynamic programming solution. You are flying blind.

This matters in practice. The difference between T(n) = 2T(n/2) + O(n) and T(n) = 2T(n/2) + O(n^2) is the difference between an algorithm that handles a billion records in seconds and one that takes hours. In 2012, Knight Capital lost $440 million in 45 minutes partly because a system that was supposed to process orders in linear time had a hidden quadratic loop. Understanding recurrences is understanding the cost of your design decisions.

The Master Theorem is the shortcut. Instead of grinding through algebra every time, you pattern-match against three cases and read off the answer. But you need to understand the recursion tree method first — otherwise the Master Theorem is just a magic formula you cannot debug when it does not apply.

## Theory (40 min)

### From Code to Recurrence

Every recursive function has a recurrence hiding inside it. To find it, ask two questions:
1. How many recursive calls, and on what input size?
2. How much non-recursive work at each call?

```python
def merge_sort(arr):
    if len(arr) <= 1:        # Base case: T(1) = O(1)
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])    # T(n/2)
    right = merge_sort(arr[mid:])   # T(n/2)
    return merge(left, right)       # O(n) work
```

This gives us: **T(n) = 2T(n/2) + O(n)**, with T(1) = O(1).

Another example:
```python
def binary_search(arr, target, lo, hi):
    if lo > hi:              # T(1) = O(1)
        return -1
    mid = (lo + hi) // 2    # O(1) work
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, hi)  # T(n/2)
    else:
        return binary_search(arr, target, lo, mid - 1)  # T(n/2)
```

Only ONE branch executes, so: **T(n) = T(n/2) + O(1)**.

### Method 1: Substitution (Guess and Prove)

1. Guess the answer (from experience or intuition).
2. Substitute it into the recurrence.
3. Prove by induction that it works.

Example: T(n) = 2T(n/2) + n. Guess T(n) = O(n log n), meaning T(n) <= cn log n for some c.

```
Assume T(k) <= ck log k for all k < n.
T(n) = 2T(n/2) + n
     <= 2 * c(n/2) * log(n/2) + n
     = cn * (log n - 1) + n
     = cn*log(n) - cn + n
     <= cn*log(n)          [when c >= 1]
```

The guess checks out. This method works but requires a correct guess.

### Method 2: Recursion Tree

Draw the tree of recursive calls. At each level, compute the total work. Sum across all levels.

```
T(n) = 2T(n/2) + n

Level 0:              n                    work = n
Level 1:       n/2        n/2              work = n
Level 2:    n/4  n/4   n/4  n/4           work = n
...
Level k:    1 1 1 1 1 1 1 1 ... 1          work = n

Height of tree: log2(n)
Total work: n * log2(n) = O(n log n)
```

Another example — T(n) = 3T(n/4) + n^2:

```
Level 0:                    n^2                         work = n^2
Level 1:      (n/4)^2  (n/4)^2  (n/4)^2                work = 3(n/4)^2 = (3/16)n^2
Level 2:  9 nodes of (n/16)^2 each                      work = (3/16)^2 * n^2
...

Each level's work shrinks by factor 3/16.
Geometric series dominated by first term: O(n^2).
```

### Method 3: The Master Theorem

For recurrences of the form **T(n) = aT(n/b) + O(n^d)** where a >= 1, b > 1, d >= 0:

Compare **log_b(a)** with **d**:

| Case | Condition | Result | Intuition |
|------|-----------|--------|-----------|
| 1 | d < log_b(a) | T(n) = O(n^(log_b(a))) | Leaves dominate — tree has so many branches that the bottom level does most work |
| 2 | d = log_b(a) | T(n) = O(n^d * log n) | Perfect balance — each level does equal work, multiply by number of levels |
| 3 | d > log_b(a) | T(n) = O(n^d) | Root dominates — non-recursive work at the top level dwarfs everything below |

**Case 1 example:** T(n) = 8T(n/2) + n. Here a=8, b=2, d=1. log_2(8) = 3 > 1. Leaves win: O(n^3).

**Case 2 example:** T(n) = 2T(n/2) + n. Here a=2, b=2, d=1. log_2(2) = 1 = d. Balance: O(n log n). This is merge sort.

**Case 3 example:** T(n) = 3T(n/4) + n^2. Here a=3, b=4, d=2. log_4(3) ≈ 0.79 < 2. Root wins: O(n^2).

### When Master Theorem Does NOT Apply

- Non-polynomial f(n): T(n) = 2T(n/2) + n*log(n). The "extra" log factor means this is not O(n^d) for integer d. You need the extended version (Akra-Bazzi) or recursion tree.
- Unequal subproblems: T(n) = T(n/3) + T(2n/3) + n. Different split sizes break the aT(n/b) form.
- Subtraction instead of division: T(n) = T(n-1) + n. This is not T(n/b); it is a linear recurrence.

### Common Recurrences You Should Memorize

| Recurrence | Solution | Algorithm |
|------------|----------|-----------|
| T(n) = T(n-1) + O(1) | O(n) | Linear scan, factorial |
| T(n) = T(n-1) + O(n) | O(n^2) | Selection sort, insertion sort |
| T(n) = T(n/2) + O(1) | O(log n) | Binary search |
| T(n) = T(n/2) + O(n) | O(n) | Geometric series (quickselect avg) |
| T(n) = 2T(n/2) + O(1) | O(n) | Tree traversal |
| T(n) = 2T(n/2) + O(n) | O(n log n) | Merge sort |
| T(n) = 2T(n-1) + O(1) | O(2^n) | Towers of Hanoi, naive Fibonacci |

## Practice (20 min)

Work through `practice.py`. For each code snippet, write the recurrence relation, identify which Master Theorem case applies (or why it does not apply), and solve for the complexity.

Also run `recurrence_relations.py` to see the recursion tree method visualized and empirical verification that the Master Theorem gives correct growth rates.

## Daily Project

Run `recurrence_relations.py` and study the output. The script builds actual recursion trees, counts work at each level, and times recursive functions to verify the theoretical predictions. Your tasks:

1. Before running, predict the output for each recurrence.
2. Run the script and verify your predictions against the empirical measurements.
3. The script includes a mystery recurrence at the end. Determine its complexity class from the measurements, then prove it using the recursion tree method.

## Checkpoint Questions

1. Write the recurrence for a function that splits its input into 3 equal parts, recurses on all 3, and does O(n) work at each level. Apply the Master Theorem. What is the complexity?

2. Why does T(n) = T(n/2) + O(n) give O(n) and not O(n log n)? Draw the recursion tree and explain why the geometric series converges instead of accumulating log(n) equal terms.

3. T(n) = 2T(n/2) + n*log(n). Can you apply the basic Master Theorem? Why or why not? What method would you use instead?

4. A colleague claims their algorithm is O(n log n) because "it splits in half and does linear work." But their code actually makes 3 recursive calls on n/2 each. What is the real complexity, and why is the colleague wrong?

5. Explain intuitively why Case 1 of the Master Theorem (leaves dominate) happens. What does it mean physically that the branching factor overwhelms the shrinkage?
