# Day 106: Binary Search Variations

## Why "Variations" Matters

Plain binary search ("does x exist?") is the easy case. The real-world variants
all answer different questions over a *monotonic predicate*:

- **Leftmost** insertion point: where would x go to keep the array sorted? (`bisect_left`)
- **Rightmost** insertion point: how many elements ≤ x? (`bisect_right`)
- **First true / last false**: locate a boundary in a sorted boolean predicate.
- **Search on answer space**: when the *input* isn't sorted but the *answer* is monotonic — Newton-style numerical methods, capacity allocation, Koko-eats-bananas-style problems.

C++'s `std::lower_bound`/`std::upper_bound`, Python's `bisect`, Rust's
`partition_point`, Postgres B-tree page descent — all are these variants.

## The Unified Template

Every binary search is the same loop:

```
lo, hi = 0, n          # half-open [lo, hi)
while lo < hi:
    mid = (lo + hi) // 2
    if predicate(mid):
        hi = mid       # answer is at mid or left
    else:
        lo = mid + 1   # answer is strictly right
return lo              # first index where predicate is True
```

Pick the right `predicate` and you get every variant for free:

| Variant | Predicate |
|---------|-----------|
| `lower_bound(x)` | `a[m] >= x` |
| `upper_bound(x)` | `a[m] > x` |
| First true | `pred(m)` directly |
| Min capacity | `can_finish(capacity = m)` |

## Why `(lo + hi) // 2` Is a Trap in C/Java

In Python it's fine — integers are arbitrary precision. In C/Java/Rust with
fixed-width ints, `lo + hi` can overflow when both are near `INT_MAX`. The
fix used in JDK's `Arrays.binarySearch` since 2006:

```
mid = lo + (hi - lo) / 2     # subtraction never overflows
```

Joshua Bloch wrote about this in *"Extra, Extra — Read All About It: Nearly
All Binary Searches and Mergesorts Are Broken"* (Google Research, 2006). The
bug had lived in JDK for nine years.

## Search on Answer Space

When the input isn't sorted but the *answer* satisfies a monotonic predicate,
binary-search the **answer range** instead of the array.

Example — Koko eating bananas: minimum speed `k` so she finishes in `h` hours.

```
def can_finish(k):
    return sum(ceil(p / k) for p in piles) <= h

# Binary search k in [1, max(piles)]
```

`can_finish` is monotonic in `k` (faster speed → fewer hours), so we can
binary search even though the input piles are unsorted.

Real examples: VM bin-packing, allocate-pages, ship-within-D-days, the
"split array largest sum" family — all are Lagrangian-style optimizations
where you binary search the *value* and check feasibility.

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| Infinite loop | `mid = (lo + hi) // 2` with `lo = mid` update | Always shrink window: `lo = mid + 1` or `hi = mid` |
| Overflow | C/Java with large `lo + hi` | `mid = lo + (hi - lo) // 2` |
| Off-by-one | Mixing closed `[lo, hi]` and half-open `[lo, hi)` | Pick one convention and stick to it |
| Wrong predicate direction | `<=` instead of `<` flips left/right | Write the predicate as `pred(m)`, derive bounds from there |
| Non-monotonic predicate | Predicate doesn't satisfy `false...false true...true` | Binary search is invalid; use linear scan or different structure |

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Search sorted array | O(log n) | O(1) |
| Search on answer space (range R) | O(log R · cost(check)) | O(1) |

Cache behavior degrades on huge arrays: each step jumps half the array,
defeating L1/L2 prefetch. For arrays > L2, B-trees (Postgres, MySQL InnoDB)
beat binary search because they keep keys on the same page.

## Real Systems

- **Python `bisect`**: pure C implementation of `bisect_left` and `bisect_right`.
- **C++ `std::lower_bound`/`std::upper_bound`**: standard partition-point search.
- **Postgres planner**: uses binary search on histograms for selectivity estimation.
- **InnoDB**: binary search within a B+tree page (16 KB) to find a key.
- **Linux kernel `bsearch()`**: kernel-internal sorted array lookup.

## Checkpoint Questions

1. Why does `(lo + hi) // 2` overflow in C but not Python?
2. Write the predicate for `upper_bound(x)` vs `lower_bound(x)`. How do they differ?
3. In Koko-eats-bananas, why is `can_finish(k)` monotonic in `k`?
4. When does binary search degrade in practice on huge arrays despite O(log n)?
5. How do you know if a problem admits "search on answer space"?
6. Why do most production B-tree implementations binary-search within a page rather than linear-search?
