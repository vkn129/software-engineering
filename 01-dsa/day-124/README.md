# Day 124: Digit DP

## Why Digit DP

You're asked: "count numbers in `[L, R]` that have property P."

If R is small (say 10^7), brute force works. But typical inputs are
**R up to 10^18**. You can't iterate. You need to think
**digit by digit**.

Digit DP is the technique that lets you build numbers one digit at a
time, counting only those that satisfy P, in time **O(digits × states)**.

The framework:
1. Reduce `count(L, R) = count(0, R) - count(0, L-1)`.
2. Define a recursion that fills digits left-to-right, tracking just
   enough state to decide whether a partial prefix can still extend
   to a valid number.

## State Design — The Critical Part

The universal digit DP state:

```
solve(pos, tight, leading_zero, <property_state>)
```

- **`pos`**: current digit index from the left (0 to len(N)-1).
- **`tight`**: bool. If True, the digits placed so far equal the prefix
  of N; the next digit is limited to `digits[pos]`. If False, we've
  already gone strictly below, so the next digit is free 0..9.
- **`leading_zero`**: bool. Are we still in leading zeros? Distinguishes
  "0042" treated as 42 from "0042" treated as a 4-digit number. Critical
  for properties involving digit count.
- **`<property_state>`**: whatever P needs (sum-so-far, last digit, etc.).

**Recurrence**:
```
def solve(pos, tight, lz, prop):
    if pos == n:
        return 1 if satisfies_property(prop, lz) else 0

    limit = digits[pos] if tight else 9
    total = 0
    for d in range(0, limit + 1):
        new_tight = tight and (d == limit)
        new_lz = lz and (d == 0)
        new_prop = update_prop(prop, d, new_lz)
        total += solve(pos + 1, new_tight, new_lz, new_prop)
    return total
```

Memoize on `(pos, tight, lz, prop)` — but **only the states that don't
depend on tight** can be memoized across calls with different N.
The tight=True states must be re-counted per call (their answer
depends on N).

## Example 1: Count Numbers with No Consecutive 1s in Binary

Property: in the binary representation, no two adjacent bits are both 1.

**Property state**: `last_bit` (0 or 1).

**Transition**: forbid `d = 1` when `last_bit = 1`.

Subproblem dependency:
```
solve(pos, tight, lz, last_bit)
   |
   v
solve(pos+1, new_tight, new_lz, d)
```

Only the next position's state depends on current — DAG by position.

## Example 2: Count Numbers in [L, R] with Digit Sum = K

**Property state**: `sum_so_far` (0..162 for 18-digit numbers).

**Final check**: `sum_so_far == K`.

Subproblem dependency: same DAG by `pos`, with `sum_so_far` updated
by adding `d` each step.

## Example 3: Count Numbers Divisible by M

**Property state**: `remainder` (mod M).

**Final check**: `remainder == 0`.

The state space is `O(digits × 2 × 2 × M)`. For M up to 10^4 and
digits up to 18, that's 720K states — very fast.

## Subproblem Dependency Graph

```
   solve(pos=0, tight=T, lz=T, prop=0)
        |
        | d in 0..digits[0]
        v
   solve(pos=1, tight=?, lz=?, prop=?)
        |
        | d in 0..(digits[1] or 9)
        v
   ...
        |
        v
   solve(pos=n, terminal)
```

The DP is a DAG with at most n positions × 2 × 2 × |prop_space| nodes.
Memoization shrinks total work proportionally.

## Why Tight Cannot Be Memoized Naively

Consider state `(pos=3, tight=True, lz=F, sum=5)`. The "tight=True"
means: previous digits equal `digits[0..2]`, i.e., they depend on N.
If we re-call with different N, this state's answer differs.

**Two solutions**:
1. Reset memo per N (or use `lru_cache(maxsize=None)` with N hashed in).
2. Memoize ONLY tight=False states; they're independent of N.

The "tight=False" branch dominates the state space, so option 2 saves
most of the memoization benefit.

## Pitfalls

1. **Leading zeros**: forgetting `lz` breaks "number of digits" properties.
   "0042" → count "0042" or "42"?
2. **Tight propagation**: `new_tight = tight AND (d == limit)`. Both
   conditions matter.
3. **Memoization across N**: if you reuse memo across `count(R)` and
   `count(L-1)`, ONLY the tight=False entries are sharable. Easiest:
   clear memo between calls.
4. **Negative L**: handle L = 0 specially (most problems exclude
   negatives).
5. **Off-by-one** in `count(L, R) = count(R) - count(L-1)`. Always
   compute `count(N)` as "numbers in `[0, N]`".

## Real-World Usage

| System | Application | Why Digit DP |
|--------|-------------|--------------|
| **Competitive programming** | Count integers with bizarre digit constraints | Direct fit |
| **Cryptography** | Count keys avoiding weak forms (no 0-runs etc.) | Same framework |
| **Compliance** | "How many account numbers in [A, B] are valid checksums?" | Digit-position DP |
| **Lotteries / combinatorics** | Count tickets matching a pattern | Digit DP |
| **Probability** | P(random k-digit number satisfies P) by counting | Direct application |

## Checkpoint Questions

1. Define a property where the leading_zero state is **not** needed.
2. Define a property where the leading_zero state IS needed; explain
   what goes wrong without it.
3. What's the time complexity of digit DP for "count numbers in [0, N]
   divisible by M"? Compare against brute force.
4. Why is the `tight=True` branch not memoizable across different N?
5. Modify the "digit sum = k" DP to also require the number be a
   palindrome. What new state do you need? How does the recurrence
   change?
