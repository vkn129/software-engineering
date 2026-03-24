"""
Day 2: Recursion Basics — Visualizing the Call Stack

This script demonstrates fundamental recursive patterns with
call-stack visualization so you can SEE what recursion does.

Run: python recursion_basics.py
"""


# ---------------------------------------------------------------------------
# Helper: indentation-based call stack visualizer
# ---------------------------------------------------------------------------

def trace(func):
    """Decorator that prints indented call/return traces.
    This lets you visualize the call stack without a debugger."""
    trace.depth = 0

    def wrapper(*args):
        indent = "  " * trace.depth
        args_str = ", ".join(str(a) for a in args)
        print(f"{indent}-> {func.__name__}({args_str})")
        trace.depth += 1
        result = func(*args)
        trace.depth -= 1
        print(f"{indent}<- {func.__name__}({args_str}) = {result}")
        return result

    return wrapper


# ---------------------------------------------------------------------------
# Pattern 1: Linear Recursion — problem shrinks by 1 each call
# ---------------------------------------------------------------------------

@trace
def factorial(n):
    """n! = n * (n-1) * ... * 1
    Base case: 0! = 1
    Recursive case: n! = n * (n-1)!

    Why this works: if (n-1)! is correct (leap of faith),
    then multiplying by n gives n!.
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)


@trace
def sum_list(arr):
    """Sum all elements in a list.
    Base case: empty list has sum 0.
    Recursive case: first element + sum of the rest.

    Note: arr[1:] creates a new list each time — this is O(n)
    per call, making the total O(n^2). In practice, you'd pass
    an index instead. We use slicing here for clarity.
    """
    if len(arr) == 0:
        return 0
    return arr[0] + sum_list(arr[1:])


# ---------------------------------------------------------------------------
# Pattern 2: Binary Recursion — two recursive calls
# ---------------------------------------------------------------------------

@trace
def fibonacci(n):
    """Fibonacci: F(0)=0, F(1)=1, F(n) = F(n-1) + F(n-2)

    This is the NAIVE version. It recomputes the same values
    many, many times. fibonacci(5) calls fibonacci(3) twice,
    fibonacci(2) three times, etc.

    Time complexity: O(2^n) — exponential!
    Space complexity: O(n) — maximum stack depth is n.
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


# ---------------------------------------------------------------------------
# Pattern 3: Divide and Conquer
# ---------------------------------------------------------------------------

def merge_sort(arr):
    """Merge sort: split array in half, sort each half, merge.

    This is the canonical divide-and-conquer algorithm:
    1. DIVIDE: split into two halves
    2. CONQUER: recursively sort each half
    3. COMBINE: merge two sorted halves

    T(n) = 2T(n/2) + O(n)  =>  O(n log n)
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def merge(left, right):
    """Merge two sorted lists into one sorted list. O(n) work."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------------
# Pattern 4: Tail Recursion
# ---------------------------------------------------------------------------

@trace
def factorial_tail(n, accumulator=1):
    """Tail-recursive factorial.

    The recursive call is the LAST operation — there is no
    "n * recursive_result" to compute after the call returns.
    The result is built up in the accumulator parameter.

    In languages with tail-call optimization (Scheme, Scala),
    this uses O(1) stack space. Python does NOT optimize this,
    but the pattern is still worth knowing.
    """
    if n <= 1:
        return accumulator
    return factorial_tail(n - 1, n * accumulator)


# ---------------------------------------------------------------------------
# Recursion on Strings
# ---------------------------------------------------------------------------

@trace
def reverse_string(s):
    """Reverse a string recursively.
    Base case: empty or single-char string is already reversed.
    Recursive case: last char + reverse of everything except last.
    """
    if len(s) <= 1:
        return s
    return s[-1] + reverse_string(s[:-1])


@trace
def is_palindrome(s):
    """Check if a string is a palindrome.
    Base case: strings of length 0 or 1 are palindromes.
    Recursive case: first and last chars must match,
    and the substring between them must be a palindrome.
    """
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome(s[1:-1])


# ---------------------------------------------------------------------------
# Main demonstrations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("RECURSION BASICS: Call Stack Visualization")
    print("=" * 60)

    # --- Factorial ---
    print("\n--- factorial(5) ---")
    print("Watch the indentation: each level = one stack frame\n")
    result = factorial(5)
    print(f"\nResult: 5! = {result}")
    print(f"Stack depth: 5 frames (linear recursion = O(n) space)")

    # --- Sum of a list ---
    print("\n\n--- sum_list([3, 1, 4, 1, 5]) ---\n")
    result = sum_list([3, 1, 4, 1, 5])
    print(f"\nResult: {result}")

    # --- Fibonacci (shows exponential blowup) ---
    print("\n\n--- fibonacci(5) ---")
    print("Notice how many calls are made for a small input!\n")
    trace.depth = 0
    result = fibonacci(5)
    print(f"\nResult: F(5) = {result}")
    print("Count the lines above: far more than 5 calls for n=5")
    print("This is why naive Fibonacci is O(2^n)")

    # --- Tail recursion comparison ---
    print("\n\n--- factorial_tail(5) ---")
    print("Compare with regular factorial: same result, but")
    print("the accumulator carries the computation forward.\n")
    trace.depth = 0
    result = factorial_tail(5)
    print(f"\nResult: 5! = {result}")

    # --- String recursion ---
    print("\n\n--- reverse_string('hello') ---\n")
    trace.depth = 0
    result = reverse_string("hello")
    print(f"\nResult: '{result}'")

    print("\n\n--- is_palindrome('racecar') ---\n")
    trace.depth = 0
    result = is_palindrome("racecar")
    print(f"\nResult: {result}")

    print("\n\n--- is_palindrome('hello') ---\n")
    trace.depth = 0
    result = is_palindrome("hello")
    print(f"\nResult: {result}")

    # --- Merge sort (no tracing — too many calls) ---
    print("\n\n--- merge_sort([38, 27, 43, 3, 9, 82, 10]) ---")
    arr = [38, 27, 43, 3, 9, 82, 10]
    sorted_arr = merge_sort(arr)
    print(f"Input:  {arr}")
    print(f"Sorted: {sorted_arr}")
    print("Merge sort: T(n) = 2T(n/2) + O(n) => O(n log n)")

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS:")
    print("  1. Every recursive call adds a frame to the call stack")
    print("  2. The base case is what stops the recursion")
    print("  3. Trust the recursive call works (leap of faith)")
    print("  4. Binary recursion can cause exponential calls")
    print("  5. Divide-and-conquer splits, solves, and combines")
    print("=" * 60)
