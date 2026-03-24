# Day 6: Lower Bounds — Why Comparison Sorting Can't Beat O(n log n)

## Why This Exists

Most of algorithm study focuses on upper bounds: "I found an algorithm that runs in O(n log n)." But that leaves a critical question unanswered: **can we do better?** Lower bounds answer this. They tell you when to stop searching for a faster algorithm because one provably cannot exist.

This matters for two practical reasons. First, it prevents you from wasting time trying to invent an O(n) comparison sort — the math proves it is impossible. Second, it tells you when an algorithm is **optimal**: if you prove a lower bound of Omega(n log n) for a problem and you have an O(n log n) algorithm, you are done. No cleverness will ever improve it (within the model).

Lower bounds are proven using three main techniques: the decision tree model (which reduces computation to counting leaves in a tree), information-theoretic arguments (which reason about how many bits of information each operation reveals), and adversary arguments (which construct worst-case inputs that force any algorithm to work hard). Today we implement all three.

The decision tree model is especially important because it connects algebra (Stirling's approximation), combinatorics (counting permutations), and trees (binary tree height) into one elegant proof. Understanding it means understanding why the comparison sorting bound is not just empirically observed — it is mathematically inevitable.

## Theory (40 min)

### The Decision Tree Model

Every comparison-based algorithm can be modeled as a binary tree:
- Each internal node is a comparison (is a[i] < a[j]?)
- Each leaf is one possible outcome (one permutation, one search result, etc.)
- The algorithm's worst-case time is the **height** of this tree

```
           a < b?
          /      \
      b < c?     a < c?
      /    \     /    \
   [abc] a<c?  [bac] b<c?
         / \         / \
      [acb][cab]  [bca][cba]
```

For sorting n elements, there are n! possible permutations. Each must be a distinct leaf (otherwise the algorithm cannot distinguish two different inputs). A binary tree with L leaves has height at least ceil(log2(L)).

Therefore: **height >= log2(n!) = Omega(n log n)**

This follows from Stirling's approximation: log2(n!) = n*log2(n) - n*log2(e) + O(log n) ~ n*log2(n).

### Information-Theoretic Lower Bounds

A comparison yields 1 bit of information (yes or no). To distinguish among K possible outcomes, you need at least ceil(log2(K)) bits. This is Shannon's counting argument applied to computation.

- Sorting: K = n! outcomes -> log2(n!) = Omega(n log n) comparisons
- Searching unsorted: K = n possible locations -> log2(n) = Omega(log n)... but we also need to inspect each element at least once to confirm, giving Omega(n)
- Searching sorted: K = n possible locations -> log2(n) = Omega(log n) comparisons
- Finding maximum: must "eliminate" n-1 elements -> Omega(n-1) comparisons

### Adversary Arguments

Instead of analyzing a specific algorithm, we construct an **adversary** — an opponent who answers each query in the way that forces the algorithm to ask as many questions as possible, while remaining consistent with at least one valid input.

For finding the maximum of n elements:
- The adversary maintains a set of elements that could still be the maximum
- Each comparison can eliminate at most 1 element from this set
- We start with n candidates, need to reduce to 1
- Therefore: at least n-1 comparisons are required

### Why This Doesn't Apply to Non-Comparison Sorts

Counting sort, radix sort, and bucket sort beat O(n log n) because they do not use comparisons as their fundamental operation. They exploit the **structure** of the keys (integers in a known range, fixed-length strings, etc.). The decision tree model only applies when the algorithm's only way to learn about the input is through pairwise comparisons.

This is a key lesson: **lower bounds are always relative to a model of computation.** Change the model, change the bound.

## Practice (20 min)

Work through `practice.py`. Prove lower bounds for five different problems using decision trees, information theory, and adversary arguments. Each exercise has a computational verification.

Also run `lower_bounds.py` to see the decision tree model built and verified from scratch, with Stirling's approximation computed and compared against actual values.

## Daily Project

In `lower_bounds.py`:

1. Build a decision tree for sorting 3 elements and verify it has the minimum possible height
2. Compute log2(n!) using Stirling's approximation and compare to exact values
3. Implement an adversary for the "find maximum" problem that forces n-1 comparisons
4. Show empirically that no comparison sort beats the theoretical lower bound

## Checkpoint Questions

1. A binary tree has 120 leaves. What is the minimum possible height? How does this relate to sorting 5 elements?

2. If someone claims to have a comparison-based sorting algorithm that runs in O(n) time, what specific mathematical fact proves they are wrong?

3. Radix sort runs in O(nk) time where k is the number of digits. Does this violate the Omega(n log n) lower bound? Why or why not?

4. The adversary argument for finding the maximum shows that n-1 comparisons are necessary. Is n-1 also sufficient? What algorithm achieves this?

5. Why does the lower bound proof require that every permutation appears as a distinct leaf in the decision tree? What would go wrong if two permutations shared a leaf?
