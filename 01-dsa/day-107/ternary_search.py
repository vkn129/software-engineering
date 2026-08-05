"""
Day 107: Ternary Search — From Scratch

For unimodal functions: one maximum (or minimum) somewhere in [lo, hi].
Each iteration shrinks the interval by 1/3.
"""

import math
import time


# ---------------------------------------------------------------------------
# 1. Continuous ternary search for the maximum of a unimodal function
# ---------------------------------------------------------------------------

def ternary_search_max(f, lo, hi, eps=1e-9, max_iter=300):
    """
    Find x in [lo, hi] maximizing the unimodal function f.

    eps: target interval width
    max_iter: safety bound for floating-point cases that never reach eps
    """
    for _ in range(max_iter):
        if hi - lo < eps:
            break
        third = (hi - lo) / 3.0
        m1 = lo + third
        m2 = hi - third
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    return (lo + hi) / 2.0


def ternary_search_min(f, lo, hi, eps=1e-9, max_iter=300):
    """Find x in [lo, hi] minimizing the unimodal function f."""
    return ternary_search_max(lambda x: -f(x), lo, hi, eps, max_iter)


# ---------------------------------------------------------------------------
# 2. Integer ternary search
# ---------------------------------------------------------------------------

def ternary_search_int_max(f, lo, hi):
    """
    Max of a unimodal integer function f over [lo, hi] inclusive.
    Stops when the window shrinks below 3 elements and scans directly.
    """
    while hi - lo >= 3:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if f(m1) < f(m2):
            lo = m1 + 1
        else:
            hi = m2 - 1
    # Scan the remaining 0..3 points
    best_x = lo
    best_v = f(lo)
    for x in range(lo + 1, hi + 1):
        v = f(x)
        if v > best_v:
            best_v = v
            best_x = x
    return best_x


# ---------------------------------------------------------------------------
# 3. Golden section search (cuts function evals in half)
# ---------------------------------------------------------------------------

PHI = (math.sqrt(5) - 1) / 2   # 0.6180339...

def golden_section_max(f, lo, hi, eps=1e-9, max_iter=300):
    """
    Golden section search. Reuses one probe across iterations, so it makes
    one function evaluation per iteration (after the initial two).
    """
    # Initial two probes
    m1 = hi - PHI * (hi - lo)
    m2 = lo + PHI * (hi - lo)
    f1 = f(m1)
    f2 = f(m2)
    for _ in range(max_iter):
        if hi - lo < eps:
            break
        if f1 < f2:
            lo = m1
            m1 = m2
            f1 = f2
            m2 = lo + PHI * (hi - lo)
            f2 = f(m2)
        else:
            hi = m2
            m2 = m1
            f2 = f1
            m1 = hi - PHI * (hi - lo)
            f1 = f(m1)
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# 4. Application: projectile range (angle that maximizes distance)
# ---------------------------------------------------------------------------

def projectile_range(angle_rad, v=10.0, g=9.8):
    """Horizontal range of a projectile (vacuum). Max at 45 degrees."""
    return (v * v * math.sin(2 * angle_rad)) / g


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_continuous():
    print("=" * 60)
    print("DEMO 1: Continuous ternary search")
    print("=" * 60)

    # Parabola opening downward: f(x) = -(x-3)^2 + 7, max at x=3
    f = lambda x: -(x - 3) ** 2 + 7
    x = ternary_search_max(f, -10, 10)
    print(f"\n  f(x) = -(x-3)^2 + 7")
    print(f"  argmax in [-10, 10] = {x:.10f}  (true: 3.0)")
    print(f"  f(argmax)           = {f(x):.10f}  (true: 7.0)")


def demo_integer():
    print("\n" + "=" * 60)
    print("DEMO 2: Integer ternary search")
    print("=" * 60)

    # Unimodal integer function: f(k) = -|k - 17| * 5 + 100
    f = lambda k: -abs(k - 17) * 5 + 100
    k = ternary_search_int_max(f, 0, 100)
    print(f"\n  f(k) = -|k - 17| * 5 + 100")
    print(f"  argmax in [0, 100] = {k}  (true: 17)")
    print(f"  f(argmax)          = {f(k)}")


def demo_golden_vs_ternary():
    print("\n" + "=" * 60)
    print("DEMO 3: Golden section vs ternary (function call count)")
    print("=" * 60)

    calls = {"t": 0, "g": 0}

    def f_t(x):
        calls["t"] += 1
        return -(x - 1.7) ** 2 + 5

    def f_g(x):
        calls["g"] += 1
        return -(x - 1.7) ** 2 + 5

    ternary_search_max(f_t, -100, 100, eps=1e-9)
    golden_section_max(f_g, -100, 100, eps=1e-9)

    print(f"\n  Ternary search: {calls['t']} function evaluations")
    print(f"  Golden section: {calls['g']} function evaluations")
    print(f"  Ratio: {calls['t'] / calls['g']:.2f}x")


def demo_projectile():
    print("\n" + "=" * 60)
    print("DEMO 4: Projectile range optimization")
    print("=" * 60)

    angle = ternary_search_max(projectile_range, 0, math.pi / 2)
    print(f"\n  Best launch angle (rad): {angle:.10f}")
    print(f"  Best launch angle (deg): {math.degrees(angle):.6f}")
    print(f"  (Physics says: exactly 45 degrees in vacuum.)")


def demo_non_unimodal_failure():
    print("\n" + "=" * 60)
    print("DEMO 5: Failure mode — non-unimodal function")
    print("=" * 60)

    # Two peaks: at x=-2 (height 4) and x=3 (height 9). Global max is at x=3.
    f = lambda x: max(4 - (x + 2) ** 2, 9 - (x - 3) ** 2)
    x = ternary_search_max(f, -10, 10)
    print(f"\n  Two-peak function: peaks at x=-2 (4) and x=3 (9)")
    print(f"  Ternary search returned x = {x:.6f}, f(x) = {f(x):.6f}")
    print(f"  Correct global max would be x = 3, f(x) = 9")
    print(f"  Lesson: ternary search assumes unimodality; otherwise you")
    print(f"  may get stuck at the wrong peak.")


if __name__ == "__main__":
    demo_continuous()
    demo_integer()
    demo_golden_vs_ternary()
    demo_projectile()
    demo_non_unimodal_failure()
