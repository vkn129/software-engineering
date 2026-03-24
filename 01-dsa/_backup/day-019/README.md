# Day 19: Searching — Linear and Binary Search from Scratch

## Why This Exists

Every program you have ever used does searching. When you hit Ctrl+F, when a database answers a query, when your OS finds a file, when a router looks up a destination — search is the primitive beneath it all. Understanding search is not optional. It is the foundation everything else rests on.

Here is the uncomfortable truth about binary search: Donald Knuth observed that "although the basic idea of binary search is comparatively straightforward, the details can be surprisingly tricky, and many good programmers have done it wrong in the first several attempts." Jon Bentley reported that only about 10% of professional programmers can write a correct binary search when given a few hours. The first binary search was published in 1946; the first *correct* binary search was not published until 1962. That is sixteen years of bugs.

Why? Because binary search has a narrow contract with reality. Your loop invariant must be airtight. Your boundary conditions must be exact. An off-by-one error does not give you a slightly wrong answer — it gives you an infinite loop or a missed element. This is the kind of precision that separates engineers who build reliable systems from those who build systems that "mostly work."

Linear search, meanwhile, gets dismissed as "trivial." It is not. Linear search is the *only* option when data is unsorted. It is optimal for small inputs (where the overhead of maintaining a sorted structure exceeds the cost of scanning). CPU caches love sequential access — a linear scan through contiguous memory can beat a binary search through a linked structure, even with worse asymptotic complexity. Physics (memory latency, cache lines) overrides mathematics (Big-O) at small scales.

## Theory (40 min)

### Linear Search: The Baseline

Linear search examines each element in sequence until it finds the target or exhausts the collection. It is the brute-force baseline against which we measure everything else.

```
Array: [4, 2, 7, 1, 9, 3]
Target: 7

Step 1: Check index 0 → 4 ≠ 7
Step 2: Check index 1 → 2 ≠ 7
Step 3: Check index 2 → 7 = 7 → FOUND at index 2
```

**Complexity:**
- Best case: Theta(1) — target is the first element
- Worst case: Theta(n) — target is last or absent
- Average case: Theta(n) — on average, check n/2 elements

**When linear search is actually optimal:**
1. **Unsorted data** — you cannot binary search unsorted data. Period.
2. **Small arrays** — for n < ~64, the overhead of binary search's comparisons and branch mispredictions can make linear search faster. The crossover point depends on your hardware.
3. **Searching once** — if you search once, sorting + binary search is O(n log n + log n) vs O(n). Linear wins.
4. **Linked lists** — no random access means no binary search.

### Binary Search: The Most Important Algorithm in CS

Binary search requires sorted input and eliminates half the search space with each comparison. This is the physical manifestation of the information-theoretic principle: each yes/no question should maximally reduce uncertainty.

```
Sorted Array: [1, 3, 5, 7, 9, 11, 13, 15]
Target: 7

Step 1: lo=0, hi=7, mid=3 → arr[3]=7 = 7 → FOUND

Target: 6

Step 1: lo=0, hi=7, mid=3 → arr[3]=7 > 6 → search left half
Step 2: lo=0, hi=2, mid=1 → arr[1]=3 < 6 → search right half
Step 3: lo=2, hi=2, mid=2 → arr[2]=5 < 6 → search right half
Step 4: lo=3, hi=2 → lo > hi → NOT FOUND
```

**Complexity:** Theta(log n) in the worst case. This is extraordinary. For n = 1 billion elements, binary search needs at most 30 comparisons. Linear search needs up to 1 billion.

### The Loop Invariant: Why Binary Search Is Hard

A loop invariant is a property that is true before and after every iteration of the loop. For binary search, the invariant is:

> **If the target exists in the array, it exists in arr[lo..hi] (inclusive).**

Every line of your implementation must maintain this invariant. Let us trace through the correct implementation:

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1       # Invariant established: target in arr[0..n-1]

    while lo <= hi:                  # If lo > hi, search space is empty → not found
        mid = lo + (hi - lo) // 2   # Why not (lo + hi) // 2? Integer overflow.
        if arr[mid] == target:
            return mid               # Found it
        elif arr[mid] < target:
            lo = mid + 1             # Target > arr[mid], so target in arr[mid+1..hi]
        else:
            hi = mid - 1             # Target < arr[mid], so target in arr[lo..mid-1]

    return -1                        # Search space empty, target not found
```

**The classic bugs:**

1. **`mid = (lo + hi) // 2`** — In languages with fixed-width integers (C, Java), this overflows when lo + hi > INT_MAX. The fix: `lo + (hi - lo) // 2`. Python has arbitrary-precision integers so it does not overflow, but write it correctly anyway — you will use other languages.

2. **`lo <= hi` vs `lo < hi`** — Using `<` instead of `<=` misses the case where lo == hi (a single-element search space). This is the most common off-by-one error.

3. **`lo = mid` instead of `lo = mid + 1`** — We already checked arr[mid] and it was not the target. Including mid in the next search space means we might loop forever when lo == mid (which happens when lo + 1 == hi).

### Recursive vs Iterative

```python
def binary_search_recursive(arr, target, lo, hi):
    if lo > hi:
        return -1
    mid = lo + (hi - lo) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)
```

The recursive version is cleaner to reason about but has O(log n) stack overhead. The iterative version uses O(1) space. In practice, the iterative version is preferred — not because log n stack frames is expensive (it is not), but because compilers do not always optimize tail recursion, and in interviews you want to show you can manage state explicitly.

### Counting Comparisons: The Information-Theoretic View

You have a sorted array of n elements. The target is equally likely to be any of them (or absent). How many yes/no questions do you need to identify it?

Each comparison has 3 outcomes (less, equal, greater), but let us simplify to binary decisions. With k binary questions, you can distinguish among 2^k possibilities. To distinguish among n elements, you need k >= log2(n) questions. Binary search achieves this bound — it is *optimal* for comparison-based search in a sorted array.

## Practice (20 min)

Work through `practice.py`. Implement each search function from scratch, then run the file to check your solutions against the built-in test cases.

Also run `searching.py` to see step-by-step visualizations of both algorithms and empirical timing comparisons.

## Daily Project

Run `searching.py`. The script demonstrates:
1. Step-by-step traces of linear and binary search
2. Timing comparisons across increasing input sizes
3. Comparison counting to verify the theoretical bounds

Your tasks:
1. Before running, predict the number of comparisons binary search will make for an array of 1000 elements (worst case).
2. Run the script and verify your prediction.
3. Study the visualization output to understand exactly how the search space shrinks.

## Checkpoint Questions

1. You have an unsorted array of 100 elements and need to search it once. Should you sort it first and use binary search, or just do linear search? What if you need to search it 1000 times?

2. Write the loop invariant for binary search. Now explain what goes wrong (specifically which iteration breaks) if you use `lo = mid` instead of `lo = mid + 1`.

3. Binary search on an array of 1 billion elements takes at most how many comparisons? Show the math. Now: how many comparisons would it take on an array of 1 trillion elements?

4. Why is `mid = lo + (hi - lo) // 2` safer than `mid = (lo + hi) // 2`? In which languages does this matter, and why does Python get away with it?

5. A colleague argues that linear search is "always worse" than binary search. Give three concrete scenarios where linear search is the better choice.
