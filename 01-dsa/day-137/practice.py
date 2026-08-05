"""
Day 137 Practice: Aho-Corasick

6 exercises: trie build, failure links, multi-pattern search, count matches,
keyword censoring, first-match position.
"""

from collections import deque


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Reference AC implementation
# ===================================================================

class _AC:
    def __init__(self):
        self.goto = [{}]
        self.fail = [0]
        self.output = [[]]

    def add(self, p):
        node = 0
        for c in p:
            if c not in self.goto[node]:
                self.goto.append({})
                self.fail.append(0)
                self.output.append([])
                self.goto[node][c] = len(self.goto) - 1
            node = self.goto[node][c]
        self.output[node].append(p)

    def build(self):
        q = deque()
        for c, child in self.goto[0].items():
            self.fail[child] = 0
            q.append(child)
        while q:
            u = q.popleft()
            for c, v in self.goto[u].items():
                f = self.fail[u]
                while f != 0 and c not in self.goto[f]:
                    f = self.fail[f]
                if c in self.goto[f] and self.goto[f][c] != v:
                    self.fail[v] = self.goto[f][c]
                else:
                    self.fail[v] = 0
                # Merge outputs from fail chain into v
                self.output[v].extend(self.output[self.fail[v]])
                q.append(v)

    def search(self, text):
        out = []
        state = 0
        for i, c in enumerate(text):
            while state != 0 and c not in self.goto[state]:
                state = self.fail[state]
            if c in self.goto[state]:
                state = self.goto[state][c]
            for p in self.output[state]:
                out.append((i - len(p) + 1, p))
        return out


def _build_ac(patterns):
    ac = _AC()
    for p in patterns:
        if p:
            ac.add(p)
    ac.build()
    return ac


# ===================================================================
# Exercise 1: Count Trie Nodes
# ===================================================================
# Return number of trie nodes (excluding root counts as 1).

def trie_node_count(patterns):
    """Number of nodes in the Aho-Corasick trie (including root)."""
    # TODO
    pass


def _sol_trie_node_count(patterns):
    ac = _AC()
    for p in patterns:
        if p:
            ac.add(p)
    return len(ac.goto)


# ===================================================================
# Exercise 2: Multi-Pattern Search
# ===================================================================

def multi_match(text, patterns):
    """Return list of (start_index, pattern) sorted by (start_index, pattern)."""
    # TODO
    pass


def _sol_multi_match(text, patterns):
    ac = _build_ac(patterns)
    return sorted(set(ac.search(text)))


# ===================================================================
# Exercise 3: Count Distinct Patterns Found
# ===================================================================

def count_distinct_hits(text, patterns):
    """How many distinct patterns appear at least once in text?"""
    # TODO
    pass


def _sol_count_distinct_hits(text, patterns):
    ac = _build_ac(patterns)
    found = {p for _, p in ac.search(text)}
    return len(found)


# ===================================================================
# Exercise 4: Censor Bad Words
# ===================================================================
# Replace every occurrence of any pattern with '*' (preserving length).
# Overlapping matches: replace all covered positions.

def censor(text, bad_words):
    """Return text with every pattern match replaced by '*' characters."""
    # TODO
    pass


def _sol_censor(text, bad_words):
    ac = _build_ac(bad_words)
    hits = ac.search(text)
    mask = [False] * len(text)
    for start, p in hits:
        for k in range(start, start + len(p)):
            if 0 <= k < len(text):
                mask[k] = True
    return "".join("*" if mask[i] else c for i, c in enumerate(text))


# ===================================================================
# Exercise 5: First Match Position
# ===================================================================
# Earliest (position, pattern) tuple in the text. If tie on position,
# return the longer pattern. None if no match.

def first_match(text, patterns):
    """Earliest match in text; tie-break by longer pattern."""
    # TODO
    pass


def _sol_first_match(text, patterns):
    ac = _build_ac(patterns)
    hits = ac.search(text)
    if not hits:
        return None
    # earliest start, then longest pattern
    return min(hits, key=lambda x: (x[0], -len(x[1])))


# ===================================================================
# Exercise 6: Has Any Pattern?
# ===================================================================
# True if ANY pattern appears in text (short-circuit when found).

def contains_any(text, patterns):
    """True if at least one pattern appears anywhere in text."""
    # TODO
    pass


def _sol_contains_any(text, patterns):
    ac = _build_ac(patterns)
    state = 0
    for c in text:
        while state != 0 and c not in ac.goto[state]:
            state = ac.fail[state]
        if c in ac.goto[state]:
            state = ac.goto[state][c]
        if ac.output[state]:
            return True
    return False


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
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    print("Exercise 1: Trie Node Count")
    check("he/she/his/hers", try_or_sol("trie_node_count", ["he", "she", "his", "hers"]), 10)
    check("empty list", try_or_sol("trie_node_count", []), 1)
    check("shared prefix", try_or_sol("trie_node_count", ["abc", "abd"]), 5)

    print("\nExercise 2: Multi-Match")
    hits = try_or_sol("multi_match", "ushers", ["he", "she", "his", "hers"])
    check("ushers matches", hits, [(1, 'she'), (2, 'he'), (2, 'hers')])
    check("no patterns", try_or_sol("multi_match", "abc", []), [])
    check("no matches", try_or_sol("multi_match", "xyz", ["abc"]), [])

    print("\nExercise 3: Count Distinct Hits")
    check("3 distinct",
          try_or_sol("count_distinct_hits", "ushers", ["he", "she", "his", "hers"]), 3)
    check("zero", try_or_sol("count_distinct_hits", "xyz", ["abc", "def"]), 0)
    check("overlap same",
          try_or_sol("count_distinct_hits", "ababab", ["ab", "ba"]), 2)

    print("\nExercise 4: Censor")
    check("simple", try_or_sol("censor", "hello world", ["world", "hell"]),
          "****o *****")
    check("no hit", try_or_sol("censor", "clean text", ["bad"]), "clean text")
    check("overlap", try_or_sol("censor", "aaaa", ["aa"]), "****")

    print("\nExercise 5: First Match")
    check("at 2 longer",
          try_or_sol("first_match", "ushers", ["he", "hers"]), (2, "hers"))
    check("none", try_or_sol("first_match", "abc", ["xyz"]), None)
    check("earliest wins",
          try_or_sol("first_match", "abcdef", ["cde", "ab"]), (0, "ab"))

    print("\nExercise 6: Contains Any")
    check("yes", try_or_sol("contains_any", "hello", ["xy", "ell"]), True)
    check("no", try_or_sol("contains_any", "hello", ["xy", "abc"]), False)
    check("empty patterns", try_or_sol("contains_any", "hello", []), False)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
