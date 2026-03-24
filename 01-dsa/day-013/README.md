# Day 13: Induction & Loop Invariants -- Proving Algorithms Correct

## Why This Exists

You have been writing algorithms for almost two weeks. You test them, they pass, and you move on. But Dijkstra's observation haunts serious engineers: *"Testing shows the presence of bugs, not their absence."* You can run a million test cases on a sorting algorithm and still not know whether it works for input number one million and one.

Mathematical induction and loop invariants are the tools that let you cross from "probably works" to "provably correct." This is not academic pedantry -- it is the difference between software that fails in production at 3 AM and software you can reason about with certainty. The NASA JPL coding standards require formal correctness arguments for critical systems. Database query planners, cryptographic protocols, and compiler optimizations all rely on formal proofs because the cost of a subtle bug is catastrophic.

The key insight: every loop is secretly performing mathematical induction. The loop variable is the induction variable. The loop body is the inductive step. The initialization is the base case. Once you see this, you can *prove* that any loop does what you claim, not just hope.

## Theory (40 min)

### 1. Mathematical Induction: The Domino Principle

Induction proves that a statement P(n) holds for all natural numbers n >= base.

**Weak induction:**
1. **Base case**: Prove P(base) is true.
2. **Inductive step**: Assume P(k) is true (the *inductive hypothesis*). Prove P(k+1) follows.

Why it works: if P(0) is true and P(k) => P(k+1) for all k, then by chaining: P(0) => P(1) => P(2) => ... This is the domino principle -- knock over the first domino (base case), and if each domino knocks over the next (inductive step), they all fall.

**Strong induction:**
Same structure, but the inductive hypothesis is stronger: assume P(j) is true for *all* j from base through k, then prove P(k+1). This is equivalent in power to weak induction but sometimes makes the proof easier (e.g., when the recursive structure depends on multiple earlier values, not just the immediately preceding one).

**Example: sum of first n natural numbers**
- Claim: sum(1..n) = n(n+1)/2
- Base: n=1, sum = 1 = 1*2/2. Holds.
- Inductive step: assume sum(1..k) = k(k+1)/2. Then sum(1..k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2. QED.

### 2. Loop Invariants: Induction in Disguise

A **loop invariant** is a property that:
1. **Initialization**: Is true before the loop starts (base case).
2. **Maintenance**: If true before an iteration, remains true after the iteration (inductive step).
3. **Termination**: When the loop ends, the invariant combined with the exit condition gives you the postcondition you want.

This is precisely mathematical induction where the induction variable is the loop counter (or, more generally, the iteration number).

### 3. Why Formal Proofs Matter

- **Testing is finite; input spaces are infinite.** You cannot test all 2^64 possible inputs to a 64-bit function.
- **Edge cases hide.** Off-by-one errors in binary search went undetected for decades (Joshua Bloch's 2006 blog post about a bug in java.util.Arrays.binarySearch, present since 1946).
- **Optimizations require proof.** When you replace `x / 2` with `x >> 1`, you need to know they are equivalent for your input domain (they are not for negative numbers in many languages).
- **Composition.** If you prove each function correct, you can reason about compositions. Testing compositions requires combinatorial test cases.

### 4. The Five Algorithms We Will Prove

For each algorithm, we will state the loop invariant, prove initialization, maintenance, and termination, and show how termination + invariant gives correctness.

1. **Binary Search** -- invariant: if target exists, it is in arr[lo..hi]
2. **Insertion Sort** -- invariant: arr[0..i-1] is sorted and contains the original elements
3. **Bubble Sort** -- invariant: after pass i, the last i elements are in their final position
4. **Euclid's GCD** -- invariant: gcd(a, b) = gcd(original_a, original_b) at every step
5. **Fast Exponentiation** -- invariant: result * base^exp = original_base^original_exp

## Practice (20 min)

1. Write the loop invariant for a linear search algorithm
2. Prove insertion sort correctness using the three-part framework
3. Given a broken binary search, identify which part of the invariant is violated
4. Write invariants for two algorithms you have implemented in previous days
5. Use strong induction to prove the Fibonacci recurrence produces correct values

## Daily Project

Implement all five algorithms with their proofs embedded as structured comments. Each proof follows the Initialization / Maintenance / Termination framework. The code should be runnable and produce output demonstrating each algorithm and its invariant in action.

## Checkpoint Questions

1. What is the difference between weak and strong induction? When would you prefer one over the other?
2. Why is the termination argument essential -- what goes wrong if you only prove initialization and maintenance?
3. In binary search, what specific invariant is violated by the classic off-by-one bug (using `hi = mid` instead of `hi = mid - 1`)?
4. How does Euclid's algorithm termination argument work? What is the decreasing quantity?
5. A colleague says "my algorithm passes all tests, so it is correct." What is wrong with this reasoning, and what would you do instead?
