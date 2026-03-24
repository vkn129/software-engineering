# Day 1: Big-O, Big-Omega, Big-Theta

## Why This Exists

Every line of code you write has a cost. When your function processes 100 items in 0.01 seconds, everything feels fine. But when a customer uploads 10 million items and your server hangs for 45 minutes, you have a problem. Complexity theory gives you the vocabulary and mental framework to predict these disasters *before* they happen -- at the whiteboard, not in production.

The real power of asymptotic analysis is abstraction. You do not need to know the exact CPU, the clock speed, the cache line size, or the OS scheduler's behavior. You strip all of that away and ask: "As input grows toward infinity, how does the work grow?" This lets you compare algorithms on paper, without running a single benchmark, and be right about which one wins at scale.

There are three notations -- Big-O, Big-Omega, and Big-Theta -- and most engineers only know one of them (Big-O). That is like knowing "less than" but not "greater than" or "equals." Today you will learn all three, understand their formal definitions, and build intuition by measuring real code.

## Theory (40 min)

### What "Complexity" Actually Means

We count *operations*, not seconds. An operation is any constant-time step: an assignment, a comparison, an arithmetic operation, an array index lookup. The total count of operations is a function of the input size, T(n).

For example, this function:
```python
def sum_list(arr):
    total = 0          # 1 operation
    for x in arr:      # n iterations
        total += x     # 1 operation per iteration
    return total       # 1 operation
```
has T(n) = n + 2. We do not care about the +2 at scale. That is where asymptotic notation comes in.

### Big-O: Upper Bound

**Formal definition:** f(n) is O(g(n)) if there exist constants c > 0 and n0 >= 0 such that for all n >= n0:

    f(n) <= c * g(n)

In plain English: beyond some point, f(n) never grows faster than a constant multiple of g(n). Big-O gives you a *ceiling* on growth.

- T(n) = 3n + 5 is O(n). Pick c=4, n0=5. Then 3n+5 <= 4n for all n >= 5.
- T(n) = n^2 + 100n is O(n^2). Pick c=2, n0=100.
- T(n) = n is O(n^2). This is technically true but unhelpfully loose. Big-O is an upper bound, not a tight bound.

### Big-Omega: Lower Bound

**Formal definition:** f(n) is Omega(g(n)) if there exist constants c > 0 and n0 >= 0 such that for all n >= n0:

    f(n) >= c * g(n)

This is the *floor*. It says the algorithm takes *at least* this much work. Useful for proving that no algorithm can do better than a certain bound (we will use this on Day 6 for sorting lower bounds).

- T(n) = 3n + 5 is Omega(n). Pick c=1, n0=0.
- T(n) = n^2 + 100n is Omega(n^2). Pick c=1, n0=0.

### Big-Theta: Tight Bound

**Formal definition:** f(n) is Theta(g(n)) if f(n) is both O(g(n)) and Omega(g(n)). Equivalently, there exist c1, c2 > 0 and n0 such that for all n >= n0:

    c1 * g(n) <= f(n) <= c2 * g(n)

This is the one you actually want most of the time. When someone says "this algorithm is O(n log n)," they usually *mean* Theta(n log n). Theta says: the growth rate is *exactly* this class, up to constant factors.

### Common Complexity Classes (Slowest to Fastest)

| Class | Name | Example |
|-------|------|---------|
| O(1) | Constant | Hash table lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search |
| O(n log n) | Linearithmic | Merge sort |
| O(n^2) | Quadratic | Bubble sort |
| O(n^3) | Cubic | Naive matrix multiply |
| O(2^n) | Exponential | Brute-force subsets |
| O(n!) | Factorial | Brute-force permutations |

### Rules for Determining Complexity

1. **Drop constants:** O(3n) = O(n)
2. **Drop lower-order terms:** O(n^2 + n) = O(n^2)
3. **Sequential blocks add:** O(n) then O(n^2) = O(n^2)
4. **Nested loops multiply:** loop n * loop n = O(n^2)
5. **Logarithmic patterns:** Halving or doubling each step = O(log n)

### Best, Worst, and Average Case

Big-O/Omega/Theta describe the *growth rate* of a function. Best/worst/average describe *which input* you are analyzing. They are independent concepts.

- Linear search, worst case: Theta(n) -- element is last or absent
- Linear search, best case: Theta(1) -- element is first
- Linear search, average case: Theta(n) -- on average, check half the list

## Practice (20 min)

Work through `practice.py`. For each function, determine the Big-O, Big-Omega, and Big-Theta complexity. Write your answers in the TODO comments, then run the file to check against the provided solutions.

Also run `complexity_basics.py` to see empirical measurements of different complexity classes and verify that the growth patterns match theory.

## Daily Project

Run `complexity_basics.py` and study the output. The script times functions of different complexity classes across increasing input sizes and prints a table. Your task:

1. Predict what the ratios between consecutive measurements should be for each complexity class.
2. Run the script and compare predictions to reality.
3. Add one new function to the script: an O(n * sqrt(n)) function. Measure it. Where does it fall in the table?

## Checkpoint Questions

1. If f(n) = 5n^2 + 3n + 7, prove formally (with specific c and n0) that f(n) is O(n^2). Then prove it is Omega(n^2). What does that tell you about its Theta?

2. Why is saying "this algorithm is O(n^2)" technically less informative than saying it is "Theta(n^2)"? Give a concrete example where the distinction matters.

3. A function has a for-loop that runs n times, and inside it calls another function that sometimes does O(1) work and sometimes does O(n) work depending on the input. What is the worst-case complexity? What additional information would you need to determine the average-case complexity?

4. You measure a function at n=1000 taking 0.01s and at n=2000 taking 0.04s. The time quadrupled when input doubled. What complexity class does this suggest, and why?

5. Can an algorithm be O(n^2) but not Omega(n^2)? Give an example.
