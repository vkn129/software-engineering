# Day 1: Big-O, Big-Omega, Big-Theta

## Why This Exists

Every line of code you write has a cost. When your function processes 100 items in 0.01 seconds, everything feels fine. But when a customer uploads 10 million items and your server hangs for 45 minutes, you have a problem. Complexity theory gives you the vocabulary and mental framework to predict these disasters *before* they happen -- at the whiteboard, not in production.

The real power of asymptotic analysis is abstraction. You do not need to know the exact CPU, the clock speed, the cache line size, or the OS scheduler's behavior. You strip all of that away and ask: "As input grows toward infinity, how does the work grow?" This lets you compare algorithms on paper, without running a single benchmark, and be right about which one wins at scale.

There are three notations -- Big-O, Big-Omega, and Big-Theta -- and most engineers only know one of them (Big-O). That is like knowing "less than" but not "greater than" or "equals." Today you will learn all three, understand their formal definitions, and build intuition by measuring real code.

### What If This Didn't Exist?

Before asymptotic notation, the only way to compare algorithms was to run them on specific hardware and measure. Your analysis was tied to a particular machine, compiler, and input — change any of those and your conclusions were worthless. Engineers had no portable vocabulary for "this algorithm scales badly." Without Big-O, every performance discussion devolves into benchmarking arguments where nobody agrees because everyone tested on different machines. The layer below — raw operation counting — produces functions like T(n) = 3.7n^2 + 14.2n + 97 that are impossible to compare across implementations without first stripping away the noise that asymptotic notation removes.

### Why This Name?

The "Big-O" notation was introduced by Paul Bachmann in 1894 in his book "Die Analytische Zahlentheorie" and popularized by Edmund Landau, which is why it is sometimes called "Landau notation." The letter O stands for "Ordnung," the German word for "order" (as in "order of magnitude"). Big-Omega was introduced by Hardy and Littlewood around 1914 as the natural complement — the lower bound to O's upper bound. Big-Theta was formalized by Donald Knuth in 1976 because he was frustrated that engineers kept using Big-O when they meant a tight bound, and he wanted a notation that explicitly said "exactly this growth rate."

### The Physics Connection

Asymptotic analysis abstracts away physical constants, but those constants exist because of physics. The "constant factor" you drop includes cache line sizes (64 bytes on modern x86), memory latency (~100ns for DRAM vs ~1ns for L1 cache), and speed-of-light delays (~3.3ns per meter of fiber). Two O(n) algorithms can differ by 100x in wall-clock time because one streams sequentially through memory (exploiting prefetching and cache lines) while the other chases pointers randomly (stalling on every access). The abstraction is powerful precisely because it separates the algorithmic scaling law from the hardware constants — but you must remember that the constants are dictated by transistor physics and electromagnetic propagation.

### The Mathematics Connection

Big-O is formally a statement about the eventual dominance of one function over another — it belongs to the field of asymptotic analysis in real analysis. The key mathematical insight is that polynomial growth rates form a strict hierarchy: n^a is always eventually dominated by n^b when a < b, regardless of constant multipliers. This connects to information theory: processing n items requires at least reading them (Omega(n)), and distinguishing n! orderings requires at least log2(n!) = Omega(n log n) comparisons. The impossibility results — like the fact that no comparison sort beats n log n — come directly from combinatorial counting arguments that are as rigorous as any theorem in mathematics.

### The Economics Connection

Asymptotic notation is a trade-off between precision and usefulness. You sacrifice exact operation counts (cheap to compute, hard to compare) for growth-rate classes (easy to compare, but they hide constants). An engineer choosing between O(n) and O(n^2) is making an economic bet: the O(n) algorithm will cost less at scale, but might have a larger constant factor that makes it slower for small inputs. There is also the developer-time trade-off: analyzing exact T(n) for every function is expensive in human hours, while Big-O gives you an 80/20 answer — 80% of the insight for 20% of the effort. The dropped constants are the "price" you pay for a portable, hardware-independent comparison.

### When Does This Break?

Big-O fails you when constants matter — and they always matter at finite scale. An O(n) algorithm with a constant of 10^9 is slower than an O(n^2) algorithm for all inputs under a billion. Galactic algorithms like the Coppersmith-Winograd matrix multiplication (O(n^2.373)) have constants so large they never beat the naive O(n^3) on any real input. Big-O also breaks when comparing algorithms in the same class: O(n log n) merge sort vs O(n log n) heapsort differ by ~2x due to cache behavior, but Big-O cannot distinguish them. Adversarial inputs can also exploit the gap between average and worst case — quicksort is O(n log n) expected but O(n^2) worst case, and attackers have exploited this to DOS hash tables in web frameworks.

### When Should You Violate This?

Ignore asymptotic analysis when your input size is permanently small. If n is always under 100, an O(n^2) algorithm with small constants will outperform an O(n log n) algorithm with large overhead — this is why Timsort switches to insertion sort for small runs. Ignore it when constant factors dominate: GPU-accelerated matrix multiplication with worse theoretical complexity can beat CPU algorithms with better Big-O because the parallelism constant is 1000x. Ignore it during prototyping — writing the simplest O(n^2) solution first and optimizing only when profiling shows it matters is often the economically rational choice. The abstraction exists to guide decisions at scale, not to replace measurement at every scale.

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
