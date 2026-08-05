"""
Day 139: Regex via Thompson NFA — From Scratch

Parse -> compile to NFA -> simulate in O(nm).
Immune to ReDoS by design (no backtracking).
Supports: literals, '.', '*', '+', '?', '|', '(', ')'.

Compare to Python's `re` module (backtracking) at the bottom of demos —
do NOT use re for our actual implementation.
"""

import time


# ---------------------------------------------------------------------------
# 1. NFA Representation
# ---------------------------------------------------------------------------

# State transitions:
#   - 'epsilon' edges: target states reached with no input
#   - 'char' edge: target if input char matches (None = wildcard)
#
# We use integer state IDs and parallel arrays for speed.

class NFA:
    """A Thompson NFA. Each state has up to 2 epsilon edges and 1 char edge."""

    def __init__(self):
        # Per state:
        self.char = []       # char to match (None=ε-only, '.'=wildcard, else literal)
        self.out1 = []       # primary out edge (state id or -1)
        self.out2 = []       # secondary out edge (for split nodes); -1 if unused
        self.start = -1
        self.accept = -1

    def new_state(self, ch, o1=-1, o2=-1):
        idx = len(self.char)
        self.char.append(ch)
        self.out1.append(o1)
        self.out2.append(o2)
        return idx


# ---------------------------------------------------------------------------
# 2. Parser (recursive descent on regex grammar)
# ---------------------------------------------------------------------------
#
# Grammar:
#   regex   = term ('|' term)*
#   term    = factor*                    (concatenation)
#   factor  = atom ('*' | '+' | '?')?
#   atom    = literal | '.' | '(' regex ')'

class Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def eat(self):
        c = self.s[self.i]
        self.i += 1
        return c

    def parse(self):
        return self._regex()

    def _regex(self):
        # term ('|' term)*
        left = self._term()
        while self.peek() == "|":
            self.eat()
            right = self._term()
            left = ("alt", left, right)
        return left

    def _term(self):
        # factor*
        parts = []
        while self.peek() not in (None, "|", ")"):
            parts.append(self._factor())
        if not parts:
            return ("empty",)
        node = parts[0]
        for p in parts[1:]:
            node = ("concat", node, p)
        return node

    def _factor(self):
        node = self._atom()
        if self.peek() in ("*", "+", "?"):
            q = self.eat()
            node = (q, node)  # ('*', x), ('+', x), ('?', x)
        return node

    def _atom(self):
        c = self.eat()
        if c == "(":
            inner = self._regex()
            if self.peek() != ")":
                raise ValueError("expected ')'")
            self.eat()
            return inner
        elif c == ".":
            return ("any",)
        elif c in "*+?|)":
            raise ValueError(f"unexpected token {c!r}")
        else:
            return ("lit", c)


# ---------------------------------------------------------------------------
# 3. Compile AST to NFA (Thompson's Construction)
# ---------------------------------------------------------------------------

def compile_nfa(ast):
    nfa = NFA()
    start, accept = _compile(ast, nfa)
    nfa.start = start
    nfa.accept = accept
    return nfa


def _compile(node, nfa):
    """Return (start_state, accept_state) for the sub-NFA."""
    kind = node[0]
    if kind == "lit":
        a = nfa.new_state(node[1])  # consumes node[1]
        b = nfa.new_state(None)     # accept (no out edges by default)
        nfa.out1[a] = b
        return a, b
    if kind == "any":
        a = nfa.new_state(".")
        b = nfa.new_state(None)
        nfa.out1[a] = b
        return a, b
    if kind == "empty":
        a = nfa.new_state(None)
        return a, a
    if kind == "concat":
        s1, a1 = _compile(node[1], nfa)
        s2, a2 = _compile(node[2], nfa)
        # Patch: a1 -> s2 via epsilon. Make a1 a split with one out to s2.
        nfa.char[a1] = None  # epsilon
        nfa.out1[a1] = s2
        return s1, a2
    if kind == "alt":
        s1, a1 = _compile(node[1], nfa)
        s2, a2 = _compile(node[2], nfa)
        # New start with two ε edges
        ns = nfa.new_state(None, s1, s2)
        # New accept; route both inner accepts to it via ε.
        na = nfa.new_state(None)
        nfa.char[a1] = None
        nfa.out1[a1] = na
        nfa.char[a2] = None
        nfa.out1[a2] = na
        return ns, na
    if kind == "*":
        s, a = _compile(node[1], nfa)
        ns = nfa.new_state(None, s, -1)   # split: enter or skip
        na = nfa.new_state(None)
        nfa.out2[ns] = na
        nfa.char[a] = None
        nfa.out1[a] = ns                   # loop back via the same split
        return ns, na
    if kind == "+":
        s, a = _compile(node[1], nfa)
        # Like star but mandatory first pass: route accept to a split,
        # which either loops back or exits.
        split = nfa.new_state(None, s, -1)
        na = nfa.new_state(None)
        nfa.out2[split] = na
        nfa.char[a] = None
        nfa.out1[a] = split
        return s, na
    if kind == "?":
        s, a = _compile(node[1], nfa)
        ns = nfa.new_state(None, s, -1)
        na = nfa.new_state(None)
        nfa.out2[ns] = na
        nfa.char[a] = None
        nfa.out1[a] = na
        return ns, na
    raise ValueError(f"unknown node kind: {kind}")


# ---------------------------------------------------------------------------
# 4. NFA Simulation (O(nm), no backtracking)
# ---------------------------------------------------------------------------

def _epsilon_closure(nfa, states):
    """BFS-expand state set via all ε transitions. O(|states| + |edges|)."""
    closure = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        if nfa.char[s] is None:
            # epsilon edges: out1, out2
            for t in (nfa.out1[s], nfa.out2[s]):
                if t != -1 and t not in closure:
                    closure.add(t)
                    stack.append(t)
    return closure


def _step(nfa, states, c):
    """Advance state set by consuming character c."""
    nxt = set()
    for s in states:
        ch = nfa.char[s]
        if ch is not None:
            if ch == "." or ch == c:
                t = nfa.out1[s]
                if t != -1:
                    nxt.add(t)
    return _epsilon_closure(nfa, nxt)


def fullmatch(pattern, text):
    """True iff `pattern` matches the entire `text`. O(|text| * |pattern|)."""
    ast = Parser(pattern).parse()
    nfa = compile_nfa(ast)
    states = _epsilon_closure(nfa, {nfa.start})
    for c in text:
        states = _step(nfa, states, c)
        if not states:
            return False
    return nfa.accept in states


def search(pattern, text):
    """
    True iff `pattern` matches any substring of `text`.
    Equivalent to fullmatching `.*pattern.*`. O(|text| * |pattern|).
    """
    # Wrap: prepend implicit ".*" by always re-adding start to state set.
    ast = Parser(pattern).parse()
    nfa = compile_nfa(ast)
    states = _epsilon_closure(nfa, {nfa.start})
    if nfa.accept in states:
        return True
    for c in text:
        states = _step(nfa, states, c) | _epsilon_closure(nfa, {nfa.start})
        if nfa.accept in states:
            return True
    return False


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 65)
    print("DEMO 1: Basic Regex Matching")
    print("=" * 65)
    cases = [
        ("a", "a", True),
        ("a", "b", False),
        ("a*", "", True),
        ("a*", "aaaa", True),
        ("a*b", "aaab", True),
        ("a|b", "a", True),
        ("a|b", "c", False),
        ("(ab)+", "ababab", True),
        ("(ab)+", "abab", True),
        ("(ab)+", "abx", False),
        ("colou?r", "color", True),
        ("colou?r", "colour", True),
        ("colou?r", "colouur", False),
        (".", "x", True),
        ("h.llo", "hello", True),
    ]
    for pat, txt, want in cases:
        got = fullmatch(pat, txt)
        status = "PASS" if got == want else "FAIL"
        print(f"  [{status}] fullmatch({pat!r:14s}, {txt!r:10s}) = {got} (want {want})")


def demo_search():
    print("\n" + "=" * 65)
    print("DEMO 2: Substring Search")
    print("=" * 65)
    cases = [
        ("abc", "xxabcxx", True),
        ("a*b", "xxxbyyy", True),
        ("a*b", "xxxyyy", False),
    ]
    for pat, txt, want in cases:
        got = search(pat, txt)
        status = "PASS" if got == want else "FAIL"
        print(f"  [{status}] search({pat!r:8s}, {txt!r:10s}) = {got}")


def demo_redos():
    print("\n" + "=" * 65)
    print("DEMO 3: ReDoS — Backtracking vs NFA")
    print("=" * 65)
    # Pathological pattern that causes Python's `re` to explode.
    # We use this regex ONLY for the sanity comparison; our matcher
    # supports the simpler pattern below.
    nfa_pat = "(a+)+"   # our matcher implements basic features
    text_ok = "a" * 30           # all a's: matches
    text_bad = "a" * 30 + "!"    # adds non-matching char

    # Our NFA simulation: linear time.
    t0 = time.perf_counter()
    r1 = fullmatch(nfa_pat, text_ok)
    t1 = time.perf_counter() - t0
    print(f"  fullmatch({nfa_pat!r}, 'a'*30)   -> {r1}, time {t1:.6f}s")

    t0 = time.perf_counter()
    r2 = fullmatch(nfa_pat, text_bad)
    t2 = time.perf_counter() - t0
    print(f"  fullmatch({nfa_pat!r}, 'a'*30+'!')-> {r2}, time {t2:.6f}s")

    # Comparison to Python's `re` (do NOT use re in production for untrusted patterns).
    import re as _re
    # Anchored fullmatch with ^...$
    pat = r"(a+)+$"
    t0 = time.perf_counter()
    m1 = _re.match(pat, text_ok) is not None
    t1 = time.perf_counter() - t0
    print(f"  re.match({pat!r}, 'a'*30)     -> {m1}, time {t1:.6f}s")

    # The dangerous one: increase length until you notice the explosion.
    # Keep it short to not hang the demo.
    bad_text = "a" * 24 + "!"
    t0 = time.perf_counter()
    m2 = _re.match(pat, bad_text) is not None
    t2 = time.perf_counter() - t0
    print(f"  re.match({pat!r}, 'a'*24+'!')-> {m2}, time {t2:.4f}s")
    print(f"  (Add more a's to re.match -> exponential blowup. NFA stays linear.)")


def demo_nfa_size():
    print("\n" + "=" * 65)
    print("DEMO 4: NFA Size = O(regex length)")
    print("=" * 65)
    for pat in ["a", "a*b", "a|b|c", "(ab)+c?", "(a|b)*c(d|e)+"]:
        nfa = compile_nfa(Parser(pat).parse())
        print(f"  pattern {pat!r:18s} -> {len(nfa.char)} states")


if __name__ == "__main__":
    demo_basic()
    demo_search()
    demo_redos()
    demo_nfa_size()
