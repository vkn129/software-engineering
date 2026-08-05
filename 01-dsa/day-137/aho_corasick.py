"""
Day 137: Aho-Corasick — From Scratch

Trie + failure links = scan text once, find ALL pattern matches in O(n + k).
The algorithm behind antivirus engines and network IDS.
"""

from collections import deque
import time


# ---------------------------------------------------------------------------
# 1. Aho-Corasick Automaton
# ---------------------------------------------------------------------------

class AhoCorasick:
    """
    Build once with a list of patterns, then match many texts.
    Supports overlapping matches (default behavior).
    """

    def __init__(self):
        # Each node: goto dict, fail link, output list, dict_link
        self.goto = [{}]        # goto[node][char] -> next node
        self.fail = [0]         # fail[node] -> longest proper suffix node
        self.output = [[]]      # output[node] -> patterns ending here
        self.dict_link = [0]    # nearest ancestor (via fail) with output

    def add_pattern(self, pattern):
        """Insert pattern into the trie. Call this BEFORE build()."""
        node = 0
        for c in pattern:
            if c not in self.goto[node]:
                self.goto.append({})
                self.fail.append(0)
                self.output.append([])
                self.dict_link.append(0)
                self.goto[node][c] = len(self.goto) - 1
            node = self.goto[node][c]
        self.output[node].append(pattern)

    def build(self):
        """
        Build failure links via BFS. Also compute dict_link for fast emit.
        Must be called after all patterns are added, before any search.
        """
        q = deque()
        # Depth-1 nodes: fail = root
        for c, child in self.goto[0].items():
            self.fail[child] = 0
            q.append(child)

        while q:
            u = q.popleft()
            for c, v in self.goto[u].items():
                # Find fail for v: walk fail chain from parent
                f = self.fail[u]
                while f != 0 and c not in self.goto[f]:
                    f = self.fail[f]
                if c in self.goto[f] and self.goto[f][c] != v:
                    self.fail[v] = self.goto[f][c]
                else:
                    self.fail[v] = 0
                # Dictionary suffix link
                if self.output[self.fail[v]]:
                    self.dict_link[v] = self.fail[v]
                else:
                    self.dict_link[v] = self.dict_link[self.fail[v]]
                q.append(v)

    def search(self, text):
        """
        Find ALL occurrences of ALL patterns in text.
        Returns list of (position, pattern) tuples, ordered by position.
        """
        results = []
        state = 0
        for i, c in enumerate(text):
            # Follow fail links until we find a transition or hit root
            while state != 0 and c not in self.goto[state]:
                state = self.fail[state]
            if c in self.goto[state]:
                state = self.goto[state][c]
            # Emit outputs at this node and walk dict_link chain
            if self.output[state]:
                for p in self.output[state]:
                    results.append((i - len(p) + 1, p))
            d = self.dict_link[state]
            while d != 0:
                for p in self.output[d]:
                    results.append((i - len(p) + 1, p))
                d = self.dict_link[d]
        return results


# ---------------------------------------------------------------------------
# 2. Build helper
# ---------------------------------------------------------------------------

def build_ac(patterns):
    ac = AhoCorasick()
    for p in patterns:
        if p:  # skip empty
            ac.add_pattern(p)
    ac.build()
    return ac


# ---------------------------------------------------------------------------
# 3. Naive Multi-Pattern Search (for comparison)
# ---------------------------------------------------------------------------

def naive_multi_search(text, patterns):
    """Run a brute-force search for each pattern. O(n * sum(|p|))."""
    out = []
    for p in patterns:
        if not p:
            continue
        i = 0
        while i <= len(text) - len(p):
            if text[i:i + len(p)] == p:
                out.append((i, p))
            i += 1
    return sorted(out)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 65)
    print("DEMO 1: Aho-Corasick Basic")
    print("=" * 65)
    patterns = ["he", "she", "his", "hers"]
    text = "ushers"
    print(f"  patterns: {patterns}")
    print(f"  text:     {text!r}")
    ac = build_ac(patterns)
    print(f"  matches:  {ac.search(text)}")
    print("  Expected: she at 1, he at 2, hers at 2")


def demo_signatures():
    print("\n" + "=" * 65)
    print("DEMO 2: Network IDS-style Signature Match")
    print("=" * 65)
    signatures = [
        "SELECT * FROM",
        "DROP TABLE",
        "UNION SELECT",
        "id=1' OR",
        "GET /admin",
    ]
    payload = (
        "POST /login HTTP/1.1\r\n"
        "Cookie: session=abc; q=1\r\n"
        "data=user&query=id=1' OR 1=1--&path=GET /admin/users"
    )
    ac = build_ac(signatures)
    hits = ac.search(payload)
    print(f"  payload (truncated): {payload[:60]!r}...")
    print(f"  signature hits:")
    for pos, sig in hits:
        print(f"    at {pos:3d}: {sig!r}")


def demo_speed_vs_naive():
    print("\n" + "=" * 65)
    print("DEMO 3: Aho-Corasick vs Naive Multi-Pattern")
    print("=" * 65)
    import random
    random.seed(1)
    alpha = "acgt"
    text = "".join(random.choice(alpha) for _ in range(200000))
    patterns = ["".join(random.choice(alpha) for _ in range(8)) for _ in range(200)]

    t0 = time.perf_counter()
    ac = build_ac(patterns)
    ac_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    ac_hits = ac.search(text)
    ac_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    naive_hits = naive_multi_search(text, patterns)
    naive_time = time.perf_counter() - t0

    print(f"  text len: 200,000  patterns: 200x len-8")
    print(f"  AC build: {ac_build:.4f}s")
    print(f"  AC scan:  {ac_time:.4f}s  (hits: {len(ac_hits)})")
    print(f"  naive:    {naive_time:.4f}s  (hits: {len(naive_hits)})")
    print(f"  speedup:  {naive_time / ac_time:.1f}x")
    assert sorted(ac_hits) == sorted(naive_hits), "AC and naive disagree!"


def demo_overlapping():
    print("\n" + "=" * 65)
    print("DEMO 4: Overlapping & Substring Patterns")
    print("=" * 65)
    patterns = ["aa", "aaa", "aaaa"]
    text = "aaaaa"
    ac = build_ac(patterns)
    hits = ac.search(text)
    print(f"  patterns: {patterns}")
    print(f"  text:     {text!r}")
    print(f"  hits:     {hits}")
    print("  Every position emits all matching pattern lengths.")


if __name__ == "__main__":
    demo_basic()
    demo_signatures()
    demo_speed_vs_naive()
    demo_overlapping()
