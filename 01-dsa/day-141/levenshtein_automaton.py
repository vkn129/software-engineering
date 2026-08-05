"""
Day 141: Levenshtein Automaton

Build a DFA that accepts all strings within edit distance k of pattern P.
Once built, each candidate runs in O(len(candidate)) time.

State = capped DP column. Transitions cached. Subset-construction-style
exploration: start from initial column, BFS over reachable columns under
every input symbol that matters.
"""

from collections import deque


# ---------------------------------------------------------------------------
# 1. Naive DP baseline
# ---------------------------------------------------------------------------

def edit_distance(a, b):
    """Classic Wagner-Fischer DP. O(len(a) * len(b)) time, O(len(b)) space."""
    m, n = len(a), len(b)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[n]


def within_distance_naive(pattern, candidate, k):
    """Reference: brute-force edit distance, then compare to k."""
    return edit_distance(pattern, candidate) <= k


# ---------------------------------------------------------------------------
# 2. DP column transition (the heart of the automaton)
# ---------------------------------------------------------------------------

def initial_column(m, k):
    """Column before reading any input: [0, 1, 2, ..., m], capped at k+1."""
    return tuple(min(i, k + 1) for i in range(m + 1))


def step_column(prev, pattern, c, k):
    """
    Given DP column `prev` (length m+1), input char c, pattern P, edit cap k,
    return the next DP column (a tuple, so hashable).

    prev[i] = min edits to align candidate-so-far with P[0..i].
    """
    m = len(pattern)
    cap = k + 1
    nxt = [min(prev[0] + 1, cap)]  # one more delete from candidate
    for i in range(1, m + 1):
        match_cost = 0 if pattern[i - 1] == c else 1
        v = min(
            nxt[i - 1] + 1,           # insert
            prev[i] + 1,              # delete pattern char
            prev[i - 1] + match_cost, # match/substitute
        )
        nxt.append(min(v, cap))
    return tuple(nxt)


def is_accept(column, k):
    """A column accepts iff the last entry (full alignment) is within k."""
    return column[-1] <= k


def is_dead(column, k):
    """If every entry exceeds k, no continuation can ever reach acceptance."""
    return min(column) > k


# ---------------------------------------------------------------------------
# 3. DFA construction via BFS over reachable columns
# ---------------------------------------------------------------------------

class LevenshteinDFA:
    """
    DFA for {s : edit_distance(pattern, s) <= k}.

    States are DP columns (tuples). Transitions cached for every char in the
    pattern alphabet; one extra "OTHER" transition handles characters absent
    from the pattern.
    """

    OTHER = None  # sentinel for "any char not in pattern alphabet"

    def __init__(self, pattern, k):
        self.pattern = pattern
        self.k = k
        self.alphabet = set(pattern)
        self.start = initial_column(len(pattern), k)
        # transitions[state][char] -> next_state; transitions[state][OTHER] is fallback
        self.transitions = {}
        self.accepting = set()
        self._build()

    def _build(self):
        seen = {self.start}
        queue = deque([self.start])
        while queue:
            state = queue.popleft()
            if is_accept(state, self.k):
                self.accepting.add(state)
            self.transitions[state] = {}
            for c in self.alphabet:
                nxt = step_column(state, self.pattern, c, self.k)
                self.transitions[state][c] = nxt
                if nxt not in seen and not is_dead(nxt, self.k):
                    seen.add(nxt)
                    queue.append(nxt)
                elif nxt not in seen:
                    seen.add(nxt)  # still record dead state once
            # one transition for every char NOT in pattern alphabet
            other = step_column(state, self.pattern, "\0_OTHER_\0", self.k)
            self.transitions[state][self.OTHER] = other
            if other not in seen and not is_dead(other, self.k):
                seen.add(other)
                queue.append(other)

    def accepts(self, candidate):
        """Run the DFA. Early-exit when state goes dead."""
        state = self.start
        for c in candidate:
            nxt = self.transitions[state].get(c)
            if nxt is None:
                nxt = self.transitions[state][self.OTHER]
            if is_dead(nxt, self.k):
                return False
            # OTHER successor may not yet have its row built if it was first
            # seen as dead — but accepts() only needs lookup if not dead.
            if nxt not in self.transitions:
                # lazy: extend on demand (rare edge case)
                self._extend(nxt)
            state = nxt
        return is_accept(state, self.k)

    def _extend(self, state):
        """Build transitions for a state that was queued but not expanded."""
        self.transitions[state] = {}
        if is_accept(state, self.k):
            self.accepting.add(state)
        for c in self.alphabet:
            self.transitions[state][c] = step_column(state, self.pattern, c, self.k)
        self.transitions[state][self.OTHER] = step_column(
            state, self.pattern, "\0_OTHER_\0", self.k
        )

    def num_states(self):
        return len(self.transitions)


# ---------------------------------------------------------------------------
# 4. Dictionary fuzzy search
# ---------------------------------------------------------------------------

def fuzzy_search(pattern, dictionary, k):
    """Return all words within edit distance k. O(n) per word after build."""
    dfa = LevenshteinDFA(pattern, k)
    return [w for w in dictionary if dfa.accepts(w)]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 141: Levenshtein Automaton")
    print("=" * 60)

    pattern, k = "kitten", 2
    dfa = LevenshteinDFA(pattern, k)
    print(f"\nPattern '{pattern}', k={k}")
    print(f"  DFA states: {dfa.num_states()}")

    tests = ["kitten", "sitten", "sittin", "sitting", "kit", "cat", "kittenz"]
    for t in tests:
        ed = edit_distance(pattern, t)
        in_dfa = dfa.accepts(t)
        in_naive = ed <= k
        status = "OK" if in_dfa == in_naive else "MISMATCH"
        print(f"  '{t:10s}' ed={ed} dfa={in_dfa} naive={in_naive} [{status}]")

    print("\n--- Dictionary fuzzy lookup ---")
    dictionary = [
        "kitten", "kitchen", "mitten", "bitten", "kettle",
        "kit", "kits", "kitty", "kittens", "smitten",
    ]
    hits = fuzzy_search("kitten", dictionary, 1)
    print(f"  k=1 hits: {hits}")
    hits = fuzzy_search("kitten", dictionary, 2)
    print(f"  k=2 hits: {hits}")

    print("\n--- State count vs k ---")
    for kk in range(0, 4):
        d = LevenshteinDFA("levenshtein", kk)
        print(f"  k={kk}: {d.num_states()} states")


if __name__ == "__main__":
    demo()
