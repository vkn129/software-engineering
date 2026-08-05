"""
Day 156 Practice: MapReduce

6 exercises building up a MapReduce-style pipeline. Run: python practice.py
"""

from collections import defaultdict


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: word_count_map
# ===================================================================
# Emit (lowercased word, 1) for each whitespace-separated token. Strip
# non-alphanumeric characters. Skip empty tokens.
def word_count_map(doc_id, text):
    """Yield (word, 1) pairs."""
    # TODO
    pass


def _sol_word_count_map(doc_id, text):
    out = []
    for w in text.lower().split():
        w = "".join(ch for ch in w if ch.isalnum())
        if w:
            out.append((w, 1))
    return out


# ===================================================================
# Exercise 2: word_count_reduce
# ===================================================================
def word_count_reduce(word, counts):
    """Return total count for `word`."""
    # TODO
    pass


def _sol_word_count_reduce(word, counts):
    return sum(counts)


# ===================================================================
# Exercise 3: shuffle
# ===================================================================
# Group key-value pairs by key into a dict.
def shuffle(pairs):
    """[(k, v), (k, v2), ...] → {k: [v, v2, ...]}."""
    # TODO
    pass


def _sol_shuffle(pairs):
    out = defaultdict(list)
    for k, v in pairs:
        out[k].append(v)
    return dict(out)


# ===================================================================
# Exercise 4: run_mapreduce (sequential)
# ===================================================================
# Glue map + shuffle + reduce. Return a dict of final results.
def run_mapreduce(inputs, map_fn, reduce_fn):
    """inputs: list of (k, v). map_fn returns iterable of (k2, v2)."""
    # TODO
    pass


def _sol_run_mapreduce(inputs, map_fn, reduce_fn):
    intermediate = defaultdict(list)
    for k, v in inputs:
        for k2, v2 in map_fn(k, v):
            intermediate[k2].append(v2)
    return {k: reduce_fn(k, vs) for k, vs in intermediate.items()}


# ===================================================================
# Exercise 5: combiner
# ===================================================================
# Apply a per-key local reduce to a single mapper's output before shuffle.
# Should produce at most one (k, v) per distinct k in input.
def apply_combiner(pairs, combiner_fn):
    """pairs: [(k, v)...], combiner_fn(k, [v...]) -> v'."""
    # TODO
    pass


def _sol_apply_combiner(pairs, combiner_fn):
    groups = defaultdict(list)
    for k, v in pairs:
        groups[k].append(v)
    return [(k, combiner_fn(k, vs)) for k, vs in groups.items()]


# ===================================================================
# Exercise 6: hash_partition
# ===================================================================
# Assign each (k, v) to one of R partitions using hash(k) % R.
# Return list of length R, each a list of (k, v).
def hash_partition(pairs, R):
    """Return [partition_0, partition_1, ..., partition_{R-1}]."""
    # TODO
    pass


def _sol_hash_partition(pairs, R):
    parts = [[] for _ in range(R)]
    for k, v in pairs:
        parts[hash(k) % R].append((k, v))
    return parts


# ===================================================================
# Test runner
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
            print(f"  FAIL: {name}  expected {expected}, got {got}")
            failed += 1

    print("Exercise 1: word_count_map")
    out = list(try_or_sol("word_count_map", "d1", "The quick, brown fox!"))
    check("4 tokens", sorted(out), [("brown", 1), ("fox", 1), ("quick", 1), ("the", 1)])
    check("empty", list(try_or_sol("word_count_map", "d1", "")), [])

    print("\nExercise 2: word_count_reduce")
    check("sum", try_or_sol("word_count_reduce", "the", [1, 1, 1, 1]), 4)
    check("single", try_or_sol("word_count_reduce", "x", [5]), 5)

    print("\nExercise 3: shuffle")
    check("group", try_or_sol("shuffle", [("a", 1), ("b", 2), ("a", 3)]),
          {"a": [1, 3], "b": [2]})
    check("empty", try_or_sol("shuffle", []), {})

    print("\nExercise 4: run_mapreduce")
    docs = [("d1", "a b a"), ("d2", "b c")]
    result = try_or_sol("run_mapreduce", docs, _sol_word_count_map, _sol_word_count_reduce)
    check("word count", result, {"a": 2, "b": 2, "c": 1})

    print("\nExercise 5: apply_combiner")
    pairs = [("a", 1), ("b", 1), ("a", 1), ("a", 1)]
    combined = try_or_sol("apply_combiner", pairs, lambda k, vs: sum(vs))
    check("collapses", sorted(combined), [("a", 3), ("b", 1)])

    print("\nExercise 6: hash_partition")
    # We can't predict hash exactly across runs, but each pair must go to
    # exactly one partition.
    pairs = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
    parts = try_or_sol("hash_partition", pairs, 2)
    check("two partitions", len(parts), 2)
    flat = sorted([p for part in parts for p in part])
    check("preserves all pairs", flat, sorted(pairs))

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
