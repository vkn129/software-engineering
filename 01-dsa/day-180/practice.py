"""
Day 180 Practice: Search refinement building blocks (4 exercises).
"""

import math
from collections import defaultdict


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        r = student_fn(*args, **kwargs)
        if r is not None:
            return r
    return sol_fn(*args, **kwargs)


# ===================================================================
# Ex 1: Levenshtein edit distance
# ===================================================================
# Classic DP. Three operations: insert, delete, substitute (all cost 1).

def edit_distance(a, b):
    """Return Levenshtein distance between a and b."""
    # TODO: implement
    pass


def _sol_edit_distance(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur[j] = min(cur[j-1] + 1, prev[j] + 1, prev[j-1] + cost)
        prev = cur
    return prev[-1]


# ===================================================================
# Ex 2: Trigram set
# ===================================================================
# Return set of length-3 substrings (with $ padding both sides).

def trigrams(s):
    """Return set of trigrams of '$' + s + '$'."""
    # TODO: implement
    pass


def _sol_trigrams(s):
    padded = '$' + s + '$'
    if len(padded) < 3:
        return {padded}
    return {padded[i:i+3] for i in range(len(padded) - 2)}


# ===================================================================
# Ex 3: BM25 idf
# ===================================================================
# Lucene's variant: log((N - df + 0.5) / (df + 0.5) + 1).
# Always non-negative.

def bm25_idf(N, df):
    """Return BM25 idf for term with document frequency df in N-doc corpus."""
    # TODO: implement
    pass


def _sol_bm25_idf(N, df):
    return math.log((N - df + 0.5) / (df + 0.5) + 1.0)


# ===================================================================
# Ex 4: BM25 single-term score
# ===================================================================
# BM25 contribution for one term: idf * tf * (k1+1) / (tf + k1*(1-b+b*dl/avgdl))

def bm25_term_score(N, df, tf, dl, avgdl, k1=1.5, b=0.75):
    """Compute BM25 score contribution for one term in one document."""
    # TODO: implement
    pass


def _sol_bm25_term_score(N, df, tf, dl, avgdl, k1=1.5, b=0.75):
    if tf == 0:
        return 0.0
    idf = _sol_bm25_idf(N, df)
    norm = tf + k1 * (1 - b + b * dl / max(1.0, avgdl))
    return idf * tf * (k1 + 1) / norm


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    passed = failed = 0

    def check(name, got, expected, tol=0):
        nonlocal passed, failed
        ok = (got == expected) if tol == 0 else (abs(got - expected) < tol)
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected={expected}  got={got}")
            failed += 1

    print("Exercise 1: Edit Distance")
    check("kitten/sitting", try_or_sol("edit_distance", "kitten", "sitting"), 3)
    check("same", try_or_sol("edit_distance", "abc", "abc"), 0)
    check("empty left", try_or_sol("edit_distance", "", "abc"), 3)
    check("typo single sub", try_or_sol("edit_distance", "python", "pyhton"), 2)

    print("\nExercise 2: Trigrams")
    tg = try_or_sol("trigrams", "cat")
    check("cat trigrams", tg, {'$ca', 'cat', 'at$'})
    check("contains $ padding", '$ca' in try_or_sol("trigrams", "cat"), True)

    print("\nExercise 3: BM25 IDF")
    # N=10, df=1 -> log((10-1+0.5)/(1+0.5) + 1) = log(9.5/1.5 + 1) = log(7.333...)
    expected = math.log((10 - 1 + 0.5) / (1 + 0.5) + 1.0)
    check("rare term high idf",
          try_or_sol("bm25_idf", 10, 1), expected, tol=1e-9)
    # df = N => positive small value
    check("df=N still non-negative",
          try_or_sol("bm25_idf", 10, 10) >= 0, True)

    print("\nExercise 4: BM25 Term Score")
    # tf=0 -> 0
    check("tf=0 -> 0",
          try_or_sol("bm25_term_score", 10, 5, 0, 100, 100), 0.0, tol=1e-9)
    # Sanity: longer docs penalized
    short_score = try_or_sol("bm25_term_score", 10, 5, 3, 50, 100)
    long_score = try_or_sol("bm25_term_score", 10, 5, 3, 200, 100)
    check("longer doc lower score", short_score > long_score, True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
