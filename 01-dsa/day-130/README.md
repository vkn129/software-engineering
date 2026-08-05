# Day 130: Fractional Knapsack — Greedy Works, 0/1 Doesn't

## The Two Knapsack Problems

You have a bag of capacity `W`. You have `n` items, each with value `v[i]`
and weight `w[i]`. Pick items to maximize total value without exceeding `W`.

- **Fractional knapsack**: you can take a **fraction** of an item (e.g.,
  half a kilo of gold dust).
- **0/1 knapsack**: each item is **indivisible**. Take it whole or skip it.

These look almost identical. They are wildly different in complexity:

| Variant | Best algorithm | Time |
|---------|---------------|------|
| Fractional | Greedy by value/weight | O(n log n) |
| 0/1 | Dynamic programming | O(nW) pseudo-polynomial |

In fact 0/1 knapsack is **NP-hard** in general (when `W` is given in
binary). Greedy on it gives only a 2-approximation.

## Fractional Knapsack — Greedy Solution

**Greedy choice**: sort items by `value/weight` (density) descending.
Take items greedily; if the next whole item doesn't fit, take the
fraction that fills the bag.

```python
def fractional_knapsack(items, W):
    items.sort(key=lambda x: x[0]/x[1], reverse=True)  # by density
    total = 0
    for value, weight in items:
        if W >= weight:
            total += value
            W -= weight
        else:
            total += value * (W / weight)
            break
    return total
```

Time: `O(n log n)`.

## Correctness — Exchange Argument

**Claim**: After sorting by density descending, taking items greedily
(with the last one fractional) gives the optimal value.

**Proof**: Let `G` be the greedy solution and `O` be any optimal solution.
Both fill the knapsack exactly (else you could top off with more of the
densest remaining item — and any optimal must do this).

Suppose `G != O`. Find the highest-density item `i` where they differ:
greedy takes a fraction `g_i >= o_i` (greedy takes more of `i`), and some
lower-density item `j` has `g_j <= o_j` (greedy takes less of `j`).

Transfer a tiny weight `ε` from `j` to `i` in `O`:
- Capacity unchanged.
- Value change = `ε * (v_i/w_i - v_j/w_j) >= 0` since `i`'s density ≥ `j`'s.

So `O` got no worse. Continue until `O = G`. Greedy is optimal. ∎

The key insight: **fractional allows tiny exchanges**, which is exactly
what the exchange argument needs.

## Why Greedy Fails on 0/1 Knapsack

The exchange argument **breaks**: you can't transfer `ε`. You can only
swap whole items. A small density advantage on one item may not justify
displacing a heavier, lower-density item.

### Concrete counterexample

Capacity `W = 50`. Items `(value, weight)`:
- Item A: (60, 10)  → density 6.0
- Item B: (100, 20) → density 5.0
- Item C: (120, 30) → density 4.0

**Greedy by density**: take A (10/50), take B (30/50), can't fit C
(would need 30 but only 20 left). If fractional were allowed: take 2/3
of C → 80. Total = 60 + 100 + 80 = 240.

**Greedy 0/1 (round down)**: take A, take B, skip C. Total = 60 + 100 = 160.

**Optimal 0/1**: skip A, take B and C. Weight = 50, value = 100 + 120 = 220.

So greedy gives 160 vs optimal 220. **27% off**. Density-greedy is wrong.

### Worst-case ratio for density-greedy on 0/1

Greedy can be **arbitrarily bad** in the worst case. Example: two items.
- A: (1, 1) → density 1
- B: (W - 1, W) → density (W-1)/W < 1

Greedy picks A first → must skip B → total = 1. Optimal picks B → total
= W - 1. Ratio = 1/(W-1) → 0 as W grows.

### Modified greedy: a 2-approximation

There is a greedy variant that gives a **2-approximation** for 0/1
knapsack:

```
Run density-greedy → G
Take max-value single item that fits → M
Return max(G, M)
```

Proof: any optimal solution that exceeds capacity after adding the next
item's density-greedy choice can be bounded by `G + v_max <= 2 * OPT`.
This isn't tight but is provably within factor 2.

A true approximation scheme (FPTAS) for 0/1 knapsack exists — but it's
DP with rescaling, not greedy.

## Why the Difference? Matroid Theory Hints

Fractional knapsack reduces to a **uniform matroid** with weight-budget
constraints — Edmonds' theorem applies, greedy is optimal.

0/1 knapsack has a **knapsack constraint** (`Σ w_i * x_i <= W`, `x_i ∈ {0,1}`).
The feasible region is **not a matroid**. It violates the exchange axiom:
two feasible sets of unequal size may not allow swapping any element.

Concretely: `A = {item1 (weight 30)}, B = {item2 (weight 20), item3 (weight 20)}`,
capacity 40. `|A|=1 < 2=|B|`, but adding any element of `B \ A` to `A`
breaks capacity. Matroid axiom violated → greedy not guaranteed.

## Practical Use Cases

### Fractional knapsack appears in
- **Fluid mixing / blending**: choose ingredients by margin/cost ratio.
- **Time slicing**: divide CPU time across jobs by value/time-required.
- **Portfolio optimization** (continuous version): allocate capital by
  return/risk ratio (Markowitz).

### 0/1 knapsack appears in
- **Capital budgeting**: project selection under budget.
- **Cargo loading**: container packing.
- **Subset selection**: feature selection in ML under budget constraints.

For 0/1 cases in production:
- Small `W` → DP works (O(nW)).
- Large `W` → use branch-and-bound or FPTAS.
- Real-time → use the 2-approximation greedy and live with the gap.

## Failure Modes

1. **Tie in density**: pick arbitrarily — answer unaffected for fractional.
2. **Integer overflow in value × W/weight**: do the division first or use
   floats.
3. **Zero-weight items**: density is undefined / infinite. Always take them.
4. **Confusing 0/1 with fractional**: shipping a fractional solution to a
   0/1 problem produces non-integer item counts → invalid. Always confirm
   the problem statement.

## Checkpoint

1. Why does the exchange argument work for fractional but fail for 0/1?
2. Construct an instance where density-greedy on 0/1 returns less than
   half of optimal.
3. State the 2-approximation modification for 0/1 greedy.
4. What's the running time of DP for 0/1 knapsack with capacity `W` and
   `n` items? Why is it called "pseudo-polynomial"?
5. Identify three real systems where you'd choose fractional vs 0/1.
6. Sketch how Edmonds' matroid theorem applies to fractional knapsack but
   not to 0/1.
