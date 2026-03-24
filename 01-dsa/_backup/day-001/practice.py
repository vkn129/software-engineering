"""
Day 1 Practice: Analyze the Complexity of These Functions

For each function below:
1. Read the code carefully
2. Determine the Big-O (upper bound)
3. Determine the Big-Omega (lower bound)
4. Determine the Big-Theta (tight bound) if possible
5. Write your answer in the TODO comment

After you fill in all answers, run this file to check against solutions.

Run: python practice.py
"""


# ---------------------------------------------------------------------------
# Function 1
# ---------------------------------------------------------------------------
def func1(arr):
    """What is the complexity of this function?"""
    n = len(arr)
    total = 0
    for i in range(n):
        for j in range(n):
            total += arr[i] * arr[j]
    return total

# TODO: Your analysis for func1
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning:


# ---------------------------------------------------------------------------
# Function 2
# ---------------------------------------------------------------------------
def func2(arr):
    """What is the complexity of this function?"""
    n = len(arr)
    total = 0
    for i in range(n):
        for j in range(i, n):
            total += 1
    return total

# TODO: Your analysis for func2
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning (hint: how many times does the inner loop run in total?):


# ---------------------------------------------------------------------------
# Function 3
# ---------------------------------------------------------------------------
def func3(n):
    """What is the complexity of this function?"""
    if n <= 1:
        return 1
    count = 0
    i = 1
    while i < n:
        count += 1
        i *= 2  # i doubles each iteration
    return count

# TODO: Your analysis for func3
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning (hint: how many times can you double 1 before reaching n?):


# ---------------------------------------------------------------------------
# Function 4
# ---------------------------------------------------------------------------
def func4(arr):
    """What is the complexity of this function?"""
    n = len(arr)
    total = 0
    for i in range(n):
        j = 1
        while j < n:
            total += arr[i]
            j *= 2
    return total

# TODO: Your analysis for func4
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning:


# ---------------------------------------------------------------------------
# Function 5
# ---------------------------------------------------------------------------
def func5(arr):
    """What is the complexity of this function?
    Hint: look at BOTH loops. They are sequential, not nested."""
    n = len(arr)

    # Phase 1
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1

    # Phase 2
    for i in range(n):
        total += arr[i]

    return total

# TODO: Your analysis for func5
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning:


# ---------------------------------------------------------------------------
# Function 6 (TRICKY)
# ---------------------------------------------------------------------------
def func6(arr):
    """What is the complexity of this function?"""
    n = len(arr)
    total = 0
    i = n
    while i > 0:
        for j in range(i):
            total += 1
        i //= 2  # i halves each outer iteration
    return total

# TODO: Your analysis for func6
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning (hint: sum the inner loop counts: n + n/2 + n/4 + ... + 1):


# ---------------------------------------------------------------------------
# Function 7 (TRICKY)
# ---------------------------------------------------------------------------
def func7(n):
    """What is the complexity of this function?"""
    if n <= 1:
        return 0
    count = 0
    for i in range(n):
        count += 1
    return count + func7(n // 2)

# TODO: Your analysis for func7
# Big-O:
# Big-Omega:
# Big-Theta:
# Reasoning (hint: the function does n work, then recurses on n/2):


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all functions above
# ===========================================================================


SOLUTIONS = """
╔══════════════════════════════════════════════════════════════╗
║                        SOLUTIONS                            ║
╚══════════════════════════════════════════════════════════════╝

Function 1: Theta(n^2)
  Two nested loops, each running n times.
  Total operations: n * n = n^2.
  O(n^2), Omega(n^2), therefore Theta(n^2).

Function 2: Theta(n^2)
  Inner loop runs (n-i) times for each i.
  Total: n + (n-1) + (n-2) + ... + 1 = n(n+1)/2 = n^2/2 + n/2.
  Drop constants and lower terms: Theta(n^2).
  The triangle is still quadratic — half as many operations
  as func1, but the same growth rate.

Function 3: Theta(log n)
  i starts at 1 and doubles each iteration until it reaches n.
  Number of doublings: log2(n).
  O(log n), Omega(log n), therefore Theta(log n).

Function 4: Theta(n log n)
  Outer loop: n iterations.
  Inner loop: j doubles from 1 to n, so log2(n) iterations.
  Total: n * log(n).
  O(n log n), Omega(n log n), therefore Theta(n log n).

Function 5: Theta(n^2)
  Phase 1: n^2 operations (nested loops).
  Phase 2: n operations (single loop).
  Sequential, so we ADD: n^2 + n.
  Drop lower term: Theta(n^2).

Function 6: Theta(n)
  Inner loop runs i times. i goes: n, n/2, n/4, ..., 1.
  Total work: n + n/2 + n/4 + ... + 1.
  This is a geometric series that sums to ~2n.
  Therefore Theta(n). This one surprises people — the halving
  of the outer loop makes the total linear, not n*log(n).

Function 7: Theta(n)
  Does n work, then recurses on n/2.
  Total: n + n/2 + n/4 + ... + 1 = ~2n.
  Same geometric series as func6. Theta(n).
  Many people guess O(n log n) because they see "n work"
  and "log n recursive calls," but the n ALSO halves each time.
"""


def verify_solutions():
    """Run all functions to confirm they work, and print solutions."""
    import time

    test_sizes = [100, 200, 400, 800]
    functions_with_arrays = [
        ("func1", func1, "Theta(n^2)"),
        ("func2", func2, "Theta(n^2)"),
        ("func4", func4, "Theta(n log n)"),
        ("func5", func5, "Theta(n^2)"),
        ("func6", func6, "Theta(n)"),
    ]
    functions_with_ints = [
        ("func3", func3, "Theta(log n)"),
        ("func7", func7, "Theta(n)"),
    ]

    print("Empirical verification — timing each function at increasing sizes:\n")

    for name, func, expected in functions_with_arrays:
        print(f"  {name} (expected {expected}):")
        prev_t = None
        for n in test_sizes:
            arr = list(range(n))
            start = time.perf_counter()
            func(arr)
            t = time.perf_counter() - start
            ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "—"
            print(f"    n={n:>5}  time={t:.6f}s  ratio={ratio}")
            prev_t = t
        print()

    for name, func, expected in functions_with_ints:
        print(f"  {name} (expected {expected}):")
        int_sizes = [1000, 2000, 4000, 8000]
        prev_t = None
        for n in int_sizes:
            start = time.perf_counter()
            for _ in range(1000):  # repeat to get measurable times
                func(n)
            t = time.perf_counter() - start
            ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "—"
            print(f"    n={n:>5}  time={t:.6f}s  ratio={ratio}")
            prev_t = t
        print()

    print(SOLUTIONS)


if __name__ == "__main__":
    print("Day 1 Practice: Complexity Analysis")
    print("=" * 60)
    print()
    print("Have you written your answers in the TODO comments above?")
    print("Running verification and showing solutions...\n")
    verify_solutions()
