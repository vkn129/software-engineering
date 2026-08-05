"""
Day 167 Practice: Rate Limiting

Implement TODOs, run: python practice.py
"""

from collections import deque


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: Token bucket — single decision
# ===================================================================
# Given current state (tokens, last_refill), capacity, rate, now,
# return (allowed, new_tokens, new_last).

def token_bucket_step(tokens, last, capacity, rate, now):
    """Refill then try to consume 1 token. Return (allowed, tokens, last)."""
    # TODO
    pass


def _sol_token_bucket_step(tokens, last, capacity, rate, now):
    elapsed = now - last
    if elapsed > 0:
        tokens = min(capacity, tokens + elapsed * rate)
        last = now
    if tokens >= 1.0:
        return True, tokens - 1.0, last
    return False, tokens, last


# ===================================================================
# Exercise 2: Leaky bucket — single decision
# ===================================================================
# water leaks at `leak_rate`. Try to add 1 unit.

def leaky_bucket_step(water, last, capacity, leak_rate, now):
    """Return (allowed, water, last)."""
    # TODO
    pass


def _sol_leaky_bucket_step(water, last, capacity, leak_rate, now):
    elapsed = now - last
    if elapsed > 0:
        water = max(0.0, water - elapsed * leak_rate)
        last = now
    if water + 1.0 <= capacity:
        return True, water + 1.0, last
    return False, water, last


# ===================================================================
# Exercise 3: Fixed-window decision
# ===================================================================
# Given (window_id_seen, count, limit, window_secs, now),
# return (allowed, window_id, count).

def fixed_window_step(window_seen, count, limit, window_secs, now):
    # TODO
    pass


def _sol_fixed_window_step(window_seen, count, limit, window_secs, now):
    w = int(now // window_secs)
    if w != window_seen:
        window_seen = w
        count = 0
    if count < limit:
        return True, w, count + 1
    return False, w, count


# ===================================================================
# Exercise 4: Sliding-window counter — effective count
# ===================================================================
# Given current window, current_count, prev_count, window_secs, now,
# return float "effective" count used to decide.

def sliding_effective(current_w, current_count, prev_count, window_secs, now):
    """Return effective request count for this moment."""
    # TODO
    pass


def _sol_sliding_effective(current_w, current_count, prev_count, window_secs, now):
    elapsed = (now - current_w * window_secs) / window_secs
    return current_count + prev_count * (1.0 - elapsed)


# ===================================================================
# Exercise 5: Sliding-window log — single decision
# ===================================================================
# Drop timestamps <= (now - window), then if len < limit add now.

def sliding_log_step(timestamps, limit, window_secs, now):
    """timestamps: deque-like. Return (allowed, new_timestamps)."""
    # TODO
    pass


def _sol_sliding_log_step(timestamps, limit, window_secs, now):
    ts = deque(timestamps)
    cutoff = now - window_secs
    while ts and ts[0] <= cutoff:
        ts.popleft()
    if len(ts) < limit:
        ts.append(now)
        return True, ts
    return False, ts


# ===================================================================
# Exercise 6: Simulate a burst at fixed-window boundary
# ===================================================================
# Returns how many of the requests in `times` were allowed.

def simulate_fixed_window(times, limit, window_secs):
    """times: list[float]. Return int = count allowed."""
    # TODO
    pass


def _sol_simulate_fixed_window(times, limit, window_secs):
    w_seen = None
    count = 0
    allowed = 0
    for t in times:
        ok, w_seen, count = _sol_fixed_window_step(w_seen, count, limit, window_secs, t)
        if ok:
            allowed += 1
    return allowed


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} expected={expected} got={got}")
            failed += 1

    # Ex 1
    print("Exercise 1: token_bucket_step")
    ok, tok, last = try_or_sol("token_bucket_step", 5.0, 0.0, 5.0, 1.0, 0.0)
    check("burst allowed", ok, True)
    check("tokens decremented", round(tok, 2), 4.0)
    # exhaust
    ok2, tok2, _ = try_or_sol("token_bucket_step", 0.0, 0.0, 5.0, 1.0, 0.0)
    check("denied when empty", ok2, False)

    # Ex 2
    print("\nExercise 2: leaky_bucket_step")
    ok, water, _ = try_or_sol("leaky_bucket_step", 2.0, 0.0, 3.0, 1.0, 0.0)
    check("fits", ok, True)
    check("water increased", water, 3.0)
    ok2, _, _ = try_or_sol("leaky_bucket_step", 3.0, 0.0, 3.0, 1.0, 0.0)
    check("denied at capacity", ok2, False)

    # Ex 3
    print("\nExercise 3: fixed_window_step")
    ok, w, c = try_or_sol("fixed_window_step", None, 0, 2, 10.0, 0.0)
    check("first allowed", ok, True)
    ok2, _, c2 = try_or_sol("fixed_window_step", w, c, 2, 10.0, 1.0)
    check("second allowed", ok2, True)
    ok3, _, _ = try_or_sol("fixed_window_step", w, c2, 2, 10.0, 2.0)
    check("third denied", ok3, False)

    # Ex 4
    print("\nExercise 4: sliding_effective")
    eff = try_or_sol("sliding_effective", 1, 5, 10, 10.0, 15.0)   # 50% into window
    check("blended count", eff, 5 + 10 * 0.5)

    # Ex 5
    print("\nExercise 5: sliding_log_step")
    ok, ts = try_or_sol("sliding_log_step", [], 2, 10.0, 0.0)
    check("first allowed", ok, True)
    ok, ts = try_or_sol("sliding_log_step", ts, 2, 10.0, 1.0)
    check("second allowed", ok, True)
    ok, ts = try_or_sol("sliding_log_step", ts, 2, 10.0, 2.0)
    check("third denied", ok, False)
    ok, ts = try_or_sol("sliding_log_step", ts, 2, 10.0, 11.0)   # first expires
    check("after expiry allowed", ok, True)

    # Ex 6
    print("\nExercise 6: simulate_fixed_window double-burst")
    times = [9.9, 9.91, 9.92, 10.0, 10.01, 10.02]
    allowed = try_or_sol("simulate_fixed_window", times, 3, 10.0)
    check("boundary lets 6 through", allowed, 6)

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
