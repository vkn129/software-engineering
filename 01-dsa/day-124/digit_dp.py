"""
Day 124: Digit DP — From Scratch

Count integers in [L, R] (R up to 10^18) satisfying a property.
Build numbers digit by digit; track minimal state.

  1. No consecutive 1s in binary representation
  2. Digit sum exactly K
  3. Divisible by M
"""

from functools import lru_cache


# ---------------------------------------------------------------------------
# 1. Count numbers in [0, N] whose binary representation has no consecutive 1s
# ---------------------------------------------------------------------------

def no_consec_ones_count(N):
    if N < 0:
        return 0
    bits = bin(N)[2:]
    n = len(bits)

    @lru_cache(maxsize=None)
    def go(pos, tight, last):
        if pos == n:
            return 1
        limit = int(bits[pos]) if tight else 1
        total = 0
        for b in range(0, limit + 1):
            if b == 1 and last == 1:
                continue
            total += go(pos + 1, tight and (b == limit), b)
        return total

    res = go(0, True, 0)
    go.cache_clear()
    return res


# ---------------------------------------------------------------------------
# 2. Count numbers in [0, N] with digit sum exactly K
# ---------------------------------------------------------------------------

def digit_sum_eq_count(N, K):
    if N < 0 or K < 0:
        return 0
    digits = list(map(int, str(N)))
    n = len(digits)

    @lru_cache(maxsize=None)
    def go(pos, tight, s):
        if s > K:
            return 0
        if pos == n:
            return 1 if s == K else 0
        limit = digits[pos] if tight else 9
        total = 0
        for d in range(0, limit + 1):
            total += go(pos + 1, tight and (d == limit), s + d)
        return total

    res = go(0, True, 0)
    go.cache_clear()
    return res


# ---------------------------------------------------------------------------
# 3. Count numbers in [0, N] divisible by M
# ---------------------------------------------------------------------------

def divisible_by_m_count(N, M):
    if N < 0 or M <= 0:
        return 0
    digits = list(map(int, str(N)))
    n = len(digits)

    @lru_cache(maxsize=None)
    def go(pos, tight, rem):
        if pos == n:
            return 1 if rem == 0 else 0
        limit = digits[pos] if tight else 9
        total = 0
        for d in range(0, limit + 1):
            total += go(pos + 1, tight and (d == limit), (rem * 10 + d) % M)
        return total

    res = go(0, True, 0)
    go.cache_clear()
    return res


# ---------------------------------------------------------------------------
# Range queries: f(L, R) = count(R) - count(L - 1)
# ---------------------------------------------------------------------------

def range_no_consec_ones(L, R):
    return no_consec_ones_count(R) - no_consec_ones_count(L - 1)


def range_digit_sum(L, R, K):
    return digit_sum_eq_count(R, K) - digit_sum_eq_count(L - 1, K)


def range_divisible(L, R, M):
    return divisible_by_m_count(R, M) - divisible_by_m_count(L - 1, M)


# ---------------------------------------------------------------------------
# Brute force checks
# ---------------------------------------------------------------------------

def _brute_no_consec_ones(N):
    cnt = 0
    for x in range(0, N + 1):
        b = bin(x)[2:]
        if "11" not in b:
            cnt += 1
    return cnt


def _brute_digit_sum(N, K):
    cnt = 0
    for x in range(0, N + 1):
        if sum(int(d) for d in str(x)) == K:
            cnt += 1
    return cnt


def _brute_divisible(N, M):
    return N // M + 1


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_no_consec():
    print("=" * 60)
    print("DEMO 1: Numbers with No Consecutive 1s in Binary")
    print("=" * 60)
    for N in [5, 10, 100, 1000]:
        dp = no_consec_ones_count(N)
        bf = _brute_no_consec_ones(N)
        print(f"  N = {N:5}  DP = {dp:6}  brute = {bf:6}  match = {dp == bf}")
    # Big
    N = 10 ** 18
    print(f"\n  N = 10^18 -> {no_consec_ones_count(N)}")


def demo_digit_sum():
    print("\n" + "=" * 60)
    print("DEMO 2: Numbers in [0, N] with Digit Sum = K")
    print("=" * 60)
    for N, K in [(100, 5), (1000, 10), (9999, 18)]:
        dp = digit_sum_eq_count(N, K)
        bf = _brute_digit_sum(N, K)
        print(f"  N = {N:5}, K = {K:3}  DP = {dp:5}  brute = {bf:5}")
    # Big
    print(f"\n  N = 10^18, K = 50 -> {digit_sum_eq_count(10**18, 50)}")


def demo_divisible():
    print("\n" + "=" * 60)
    print("DEMO 3: Numbers in [0, N] Divisible by M")
    print("=" * 60)
    for N, M in [(100, 7), (1000, 13), (10000, 99)]:
        dp = divisible_by_m_count(N, M)
        bf = _brute_divisible(N, M)
        print(f"  N = {N:6}, M = {M:3}  DP = {dp:6}  brute = {bf:6}")


if __name__ == "__main__":
    demo_no_consec()
    demo_digit_sum()
    demo_divisible()
