"""
Day 124 Practice: Digit DP

Fill in each TODO. Run; expect Results: 6/6 passed.
"""

from functools import lru_cache


# ---------------------------------------------------------------------------
# Problem 1: Count numbers in [0, N] with digit sum exactly K
# ---------------------------------------------------------------------------

def digit_sum_count(N, K):
    """
    TODO: digit DP. State: (pos, tight, sum_so_far).
    """
    pass


def _sol_digit_sum_count(N, K):
    if N < 0 or K < 0:
        return 0
    d = list(map(int, str(N)))
    n = len(d)

    @lru_cache(maxsize=None)
    def go(pos, tight, s):
        if s > K:
            return 0
        if pos == n:
            return 1 if s == K else 0
        lim = d[pos] if tight else 9
        tot = 0
        for x in range(0, lim + 1):
            tot += go(pos + 1, tight and (x == lim), s + x)
        return tot

    r = go(0, True, 0)
    go.cache_clear()
    return r


# ---------------------------------------------------------------------------
# Problem 2: Count numbers in [0, N] divisible by M
# ---------------------------------------------------------------------------

def divisible_count(N, M):
    """
    TODO: state (pos, tight, rem mod M).
    """
    pass


def _sol_divisible_count(N, M):
    if N < 0 or M <= 0:
        return 0
    d = list(map(int, str(N)))
    n = len(d)

    @lru_cache(maxsize=None)
    def go(pos, tight, rem):
        if pos == n:
            return 1 if rem == 0 else 0
        lim = d[pos] if tight else 9
        tot = 0
        for x in range(0, lim + 1):
            tot += go(pos + 1, tight and (x == lim), (rem * 10 + x) % M)
        return tot

    r = go(0, True, 0)
    go.cache_clear()
    return r


# ---------------------------------------------------------------------------
# Problem 3: Count numbers in [0, N] with no consecutive 1s in binary
# ---------------------------------------------------------------------------

def no_consec_ones(N):
    """
    TODO: walk bits left to right; state (pos, tight, last_bit).
    """
    pass


def _sol_no_consec_ones(N):
    if N < 0:
        return 0
    bits = bin(N)[2:]
    n = len(bits)

    @lru_cache(maxsize=None)
    def go(pos, tight, last):
        if pos == n:
            return 1
        lim = int(bits[pos]) if tight else 1
        tot = 0
        for b in range(0, lim + 1):
            if b == 1 and last == 1:
                continue
            tot += go(pos + 1, tight and (b == lim), b)
        return tot

    r = go(0, True, 0)
    go.cache_clear()
    return r


# ---------------------------------------------------------------------------
# Problem 4: Count numbers in [L, R] with given digit sum K
# ---------------------------------------------------------------------------

def digit_sum_range(L, R, K):
    """TODO: use _sol_digit_sum_count(R, K) - _sol_digit_sum_count(L-1, K)."""
    pass


def _sol_digit_sum_range(L, R, K):
    return _sol_digit_sum_count(R, K) - _sol_digit_sum_count(L - 1, K)


# ---------------------------------------------------------------------------
# Problem 5: Count numbers in [0, N] whose digits are all distinct
# ---------------------------------------------------------------------------

def distinct_digits_count(N):
    """
    TODO: state (pos, tight, leading_zero, used_mask).
    Mask: 10 bits, bit d = 1 if digit d already used.
    """
    pass


def _sol_distinct_digits_count(N):
    if N < 0:
        return 0
    d = list(map(int, str(N)))
    n = len(d)

    @lru_cache(maxsize=None)
    def go(pos, tight, lz, used):
        if pos == n:
            return 1
        lim = d[pos] if tight else 9
        tot = 0
        for x in range(0, lim + 1):
            new_lz = lz and (x == 0)
            if not new_lz and (used >> x) & 1:
                continue
            new_used = used if new_lz else used | (1 << x)
            tot += go(pos + 1, tight and (x == lim), new_lz, new_used)
        return tot

    r = go(0, True, True, 0)
    go.cache_clear()
    return r


# ---------------------------------------------------------------------------
# Problem 6: Sum of all digit-sums of numbers in [0, N]
# ---------------------------------------------------------------------------

def total_digit_sum(N):
    """
    TODO: not just count — sum of digit_sum(x) for x in [0, N].
    State: return (count, total_digit_sum_in_that_branch).
    """
    pass


def _sol_total_digit_sum(N):
    if N < 0:
        return 0
    d = list(map(int, str(N)))
    n = len(d)

    @lru_cache(maxsize=None)
    def go(pos, tight):
        if pos == n:
            return (1, 0)
        lim = d[pos] if tight else 9
        cnt = 0
        s = 0
        for x in range(0, lim + 1):
            c2, s2 = go(pos + 1, tight and (x == lim))
            cnt += c2
            s += s2 + x * c2
        return (cnt, s)

    _, total = go(0, True)
    go.cache_clear()
    return total


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    total = 6

    # Brute helpers
    def b_dsum(N, K):
        return sum(1 for x in range(N + 1) if sum(int(c) for c in str(x)) == K)
    def b_div(N, M):
        return N // M + 1
    def b_nc(N):
        return sum(1 for x in range(N + 1) if "11" not in bin(x)[2:])
    def b_distinct(N):
        cnt = 0
        for x in range(N + 1):
            s = str(x)
            if len(set(s)) == len(s):
                cnt += 1
        return cnt
    def b_tds(N):
        return sum(sum(int(c) for c in str(x)) for x in range(N + 1))

    c1 = [(100, 5), (1000, 10), (500, 7), (9999, 18)]
    fn = digit_sum_count if digit_sum_count(10, 1) is not None else _sol_digit_sum_count
    if all(fn(N, K) == b_dsum(N, K) for N, K in c1):
        passed += 1; print("  [PASS] 1: digit_sum_count")
    else:
        print("  [FAIL] 1: digit_sum_count")

    c2 = [(100, 7), (1000, 13), (500, 5)]
    fn = divisible_count if divisible_count(10, 2) is not None else _sol_divisible_count
    if all(fn(N, M) == b_div(N, M) for N, M in c2):
        passed += 1; print("  [PASS] 2: divisible_count")
    else:
        print("  [FAIL] 2: divisible_count")

    c3 = [5, 10, 100, 1000]
    fn = no_consec_ones if no_consec_ones(5) is not None else _sol_no_consec_ones
    if all(fn(N) == b_nc(N) for N in c3):
        passed += 1; print("  [PASS] 3: no_consec_ones")
    else:
        print("  [FAIL] 3: no_consec_ones")

    c4 = [(10, 100, 5), (1, 500, 7), (50, 999, 10)]
    fn = digit_sum_range if digit_sum_range(1, 10, 1) is not None else _sol_digit_sum_range
    if all(fn(L, R, K) == b_dsum(R, K) - b_dsum(L - 1, K) for L, R, K in c4):
        passed += 1; print("  [PASS] 4: digit_sum_range")
    else:
        print("  [FAIL] 4: digit_sum_range")

    c5 = [9, 99, 100, 1234, 9999]
    fn = distinct_digits_count if distinct_digits_count(9) is not None else _sol_distinct_digits_count
    if all(fn(N) == b_distinct(N) for N in c5):
        passed += 1; print("  [PASS] 5: distinct_digits_count")
    else:
        print("  [FAIL] 5: distinct_digits_count")

    c6 = [9, 99, 100, 1000]
    fn = total_digit_sum if total_digit_sum(9) is not None else _sol_total_digit_sum
    if all(fn(N) == b_tds(N) for N in c6):
        passed += 1; print("  [PASS] 6: total_digit_sum")
    else:
        print("  [FAIL] 6: total_digit_sum")

    print(f"\nResults: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
