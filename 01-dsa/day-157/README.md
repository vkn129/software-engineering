# Day 157: Randomized Algorithms

## Why Randomness Helps

For some problems, no deterministic algorithm is known to be fast — but adding
**randomness** makes the problem fall over. The wins come in three flavors:

1. **Average-case speed**: randomized quicksort beats deterministic O(n²) worst case in expectation.
2. **Simplicity**: Karger's min-cut is 5 lines; deterministic min-cut needs max-flow machinery.
3. **Tractable approximation**: where exact is NP-hard, sampling gives bounded error.

This is not a hack. Randomized algorithms have rigorous probabilistic guarantees —
"the answer is correct with probability ≥ 0.99" is as solid as a deterministic bound.

## Two Species of Randomized Algorithm

### Las Vegas — Always Correct, Random Runtime

The output is guaranteed correct. Only the **time** is random.

Examples:
- **Randomized Quicksort**: correctness is a sorted array — always sorted. Expected O(n log n); worst case O(n²) with vanishing probability.
- **Treap insertions**: always a valid BST; balance is probabilistic.

You measure these by **expected runtime**.

### Monte Carlo — Always Fast, Random Correctness

Runtime is bounded. The output may be wrong with bounded probability.

Examples:
- **Miller-Rabin primality**: 99.9999% accurate per round; run k rounds for 1 - 4^-k confidence.
- **Karger's min-cut**: returns *a* cut; finds the *minimum* cut with probability ≥ 2/(n(n-1)).
- **Bloom filters**: false positives possible.

You measure these by **error probability**, often "boosted" by repetition.

### Converting Between Them

Any Las Vegas → Monte Carlo: cap the runtime, return "fail" if exceeded.
Any Monte Carlo → Las Vegas: if you can verify correctness in poly time, retry until correct.

## Randomized Quicksort

Standard quicksort picks the first element as pivot — adversarial input (already
sorted) gives O(n²). Randomized quicksort picks a **uniformly random** pivot.

**Theorem**: Expected comparisons = 2n ln n ≈ 1.39 n log₂ n.

**Proof sketch**: For any pair (a_i, a_j), the probability they get compared is
2 / (j - i + 1) — they're compared iff one of them is the first pivot from the
range [a_i, ..., a_j]. Sum over all pairs:

```
E[comparisons] = sum_{i<j} 2/(j-i+1) = 2n H_n - 4n + O(log n) ≈ 2n ln n
```

The randomness means **no input is adversarial**. The adversary cannot construct
a worst case because the pivot is chosen at run time.

## Karger's Min-Cut

A jaw-dropping algorithm. Goal: find the minimum set of edges whose removal
disconnects a graph.

```
while |V| > 2:
    pick a random edge (u, v)
    contract it (merge u and v into one vertex, drop self-loops)
return the edges between the two remaining super-vertices
```

That's it. Six lines.

**Probability of correctness per run**: ≥ 2 / (n(n-1))

That's tiny — for n=100, about 0.02%. So we **boost** by running k times and
returning the smallest cut found. After k = n² ln n runs, the probability that
*every single run* misses the min cut is:

```
(1 - 2/n²)^(n² ln n) ≤ e^(-2 ln n) = 1/n²
```

So with O(n² log n) repetitions, we're correct with probability ≥ 1 - 1/n² — high probability.

**Why does it work?** A min cut has very few edges relative to the graph.
The probability that a random edge is NOT in the min cut is high. By induction,
contracting random edges rarely destroys the min cut.

Karger-Stein (1993) improves this with recursion to O(n² log³ n) — within
poly-log of the best deterministic algorithm.

## Reservoir Sampling (Preview — full treatment Day 159)

To pick k uniformly random items from a stream of unknown length: keep a
reservoir, replace with probability k/i at item i. Proof of uniformity is
beautiful induction.

## Miller-Rabin Primality

Probabilistic primality test. For a candidate prime p:
- Pick random witness a
- Compute a^(p-1) mod p
- If ≠ 1, p is composite (proven)
- If = 1, p is probably prime (might be a "Fermat liar")

With k random witnesses, error ≤ 4^-k. Cryptographic libraries set k=40 →
error < 10^-24. Used for RSA key generation.

## Bottom Line

| Algorithm | Type | Why used over deterministic |
|---|---|---|
| Randomized quicksort | Las Vegas | Avoids worst-case adversarial input |
| Miller-Rabin | Monte Carlo | Deterministic AKS is poly but slow |
| Karger | Monte Carlo | Far simpler than max-flow min-cut |
| Bloom filters | Monte Carlo (one-sided) | Constant space; can't be deterministic |
| Treap | Las Vegas | No rebalancing logic; expected balance |

Randomness is a **resource**. Like time and space, you spend it for performance
gains or simplicity gains.

## Checkpoint Questions

1. Why does randomized quicksort's expected runtime not depend on the input distribution?
2. In Karger's algorithm, prove that a fixed min cut survives one contraction with probability ≥ 1 - 2/n.
3. You have a Monte Carlo algorithm with 1/2 error probability. How many independent runs to drive error below 10^-6?
4. Convert randomized quicksort into a Monte Carlo algorithm. What does "fail" mean?
5. Miller-Rabin has one-sided error: composites can be falsely declared prime, but primes are always declared prime. What does this mean for the kinds of mistakes possible?
