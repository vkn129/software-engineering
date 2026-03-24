# Day 2: Basic Recursion — Call Stack, Base Cases, Recursive Thinking

## Why This Exists

Iteration (loops) is how machines naturally work: do this, then do this, then do this. Recursion is how humans naturally decompose problems: "To solve THIS, first solve a SMALLER version of the same thing." Many algorithms — divide and conquer, tree traversals, dynamic programming — are fundamentally recursive. If you cannot think recursively, these will always feel like magic tricks rather than logical derivations.

The other reason to study recursion deeply is that it is the foundation of complexity analysis for non-trivial algorithms. When you see merge sort's T(n) = 2T(n/2) + O(n), you need to understand what that recurrence *means* — that the function calls itself twice on half-sized inputs and does linear work at each level. Days 3 and 4 build directly on this.

Recursion also teaches you about the call stack, which matters for practical programming. Every recursive call consumes stack space. If you do not understand this, you will write functions that crash with "maximum recursion depth exceeded" and not know why, or worse, you will avoid recursion entirely and miss elegant solutions.

## Theory (40 min)

### The Call Stack

When a function calls another function (or itself), the current function's state — its local variables, where it was in execution — gets pushed onto a stack. When the called function returns, the state is popped and execution resumes.

```
factorial(4)
  -> factorial(3)      # stack: [f(4)]
    -> factorial(2)     # stack: [f(4), f(3)]
      -> factorial(1)   # stack: [f(4), f(3), f(2)]
        -> returns 1    # stack: [f(4), f(3), f(2)]
      -> returns 2*1=2  # stack: [f(4), f(3)]
    -> returns 3*2=6    # stack: [f(4)]
  -> returns 4*6=24     # stack: []
```

Each frame on the stack costs memory. For factorial(10000), you would need 10000 stack frames. Python's default recursion limit is 1000, so deep recursion requires either increasing the limit or converting to iteration.

### Anatomy of a Recursive Function

Every recursive function needs exactly two things:

1. **Base case(s):** When to STOP recursing. Without this, you get infinite recursion (stack overflow). The base case handles the smallest, trivially solvable version of the problem.

2. **Recursive case:** Break the problem into one or more smaller subproblems of the SAME TYPE, solve them recursively, and combine the results.

```python
def factorial(n):
    if n <= 1:          # BASE CASE: 0! = 1! = 1
        return 1
    return n * factorial(n - 1)  # RECURSIVE CASE: n! = n * (n-1)!
```

### How to Think Recursively

The key mental shift: **assume the recursive call works correctly**, then figure out how to use its result. This is called the "recursive leap of faith."

Example: sum of a list.
- Assume `sum_list(arr[1:])` correctly returns the sum of everything except the first element.
- Then `sum_list(arr)` = `arr[0] + sum_list(arr[1:])`.
- Base case: empty list has sum 0.

You do NOT need to trace through every recursive call to understand the function. That is like reading assembly code to understand a for-loop. Trust the abstraction.

### Common Recursive Patterns

**Pattern 1: Linear recursion** — one recursive call, problem shrinks by 1.
- Factorial, linear search, string reversal.
- Produces a linear call stack. T(n) = T(n-1) + O(1) = O(n).

**Pattern 2: Binary recursion** — two recursive calls, problem halves.
- Fibonacci (naive), binary tree traversal.
- Can produce exponential calls if not memoized!

**Pattern 3: Divide and conquer** — split problem, recurse on parts, combine.
- Merge sort, quicksort, binary search.
- T(n) = 2T(n/2) + O(n) = O(n log n) for merge sort.

**Pattern 4: Tail recursion** — recursive call is the LAST thing the function does.
- Some languages optimize tail recursion into a loop (Python does NOT).
- Still useful as a thinking pattern.

### Recursion vs Iteration

Any recursive function can be converted to iteration (usually with an explicit stack). The choice is about clarity:
- Use recursion when the problem has recursive structure (trees, divide and conquer).
- Use iteration when the problem is naturally sequential (array traversal).
- In Python, prefer iteration for deep recursion (>1000 levels) due to stack limits.

## Practice (20 min)

Work through `practice.py`. Implement 6 recursive functions from scratch. Each has a docstring describing what to do and test cases that verify your implementation.

Also run `recursion_basics.py` to see visualizations of the call stack and worked examples of common recursive patterns.

## Daily Project

In `practice.py`, implement all functions marked with TODO. Then:

1. For each function, identify: the base case, the recursive case, and what gets "smaller" in each recursive call.
2. Draw (on paper) the call stack for `fibonacci(5)` — how many total calls are made?
3. Convert one of your recursive solutions to an iterative version and compare clarity.

## Checkpoint Questions

1. What happens if you write a recursive function with no base case? What happens if the base case exists but the recursive call does not make the problem smaller?

2. Why does naive recursive Fibonacci have O(2^n) time complexity even though it only computes n values? Where is the wasted work?

3. `factorial(n)` makes n recursive calls. Each call uses some constant amount of stack memory. What is the space complexity? How is this different from the space complexity of an iterative factorial?

4. Explain the "recursive leap of faith" in your own words. Why is it a more productive way to think about recursion than tracing every call?

5. Can you think of a problem that is naturally recursive but would be awkward to solve iteratively? (Hint: think about nested structures like file systems or JSON.)
