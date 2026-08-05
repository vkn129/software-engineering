"""
Day 139 Practice: Regex via NFA

6 exercises: literal match, wildcard, star, plus/optional, alternation,
grouped quantifiers. Build from scratch; do NOT use Python's `re`.
"""


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Reference NFA matcher (used by _sol_*)
# ===================================================================

class _NFA:
    def __init__(self):
        self.char = []
        self.out1 = []
        self.out2 = []
        self.start = -1
        self.accept = -1

    def new(self, ch, o1=-1, o2=-1):
        i = len(self.char)
        self.char.append(ch)
        self.out1.append(o1)
        self.out2.append(o2)
        return i


class _Parser:
    def __init__(self, p):
        self.s = p
        self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def eat(self):
        c = self.s[self.i]
        self.i += 1
        return c

    def parse(self):
        return self._r()

    def _r(self):
        l = self._t()
        while self.peek() == "|":
            self.eat()
            l = ("alt", l, self._t())
        return l

    def _t(self):
        parts = []
        while self.peek() not in (None, "|", ")"):
            parts.append(self._f())
        if not parts:
            return ("empty",)
        n = parts[0]
        for p in parts[1:]:
            n = ("concat", n, p)
        return n

    def _f(self):
        n = self._a()
        if self.peek() in ("*", "+", "?"):
            n = (self.eat(), n)
        return n

    def _a(self):
        c = self.eat()
        if c == "(":
            n = self._r()
            self.eat()
            return n
        if c == ".":
            return ("any",)
        return ("lit", c)


def _build(node, nfa):
    k = node[0]
    if k == "lit":
        a = nfa.new(node[1])
        b = nfa.new(None)
        nfa.out1[a] = b
        return a, b
    if k == "any":
        a = nfa.new(".")
        b = nfa.new(None)
        nfa.out1[a] = b
        return a, b
    if k == "empty":
        a = nfa.new(None)
        return a, a
    if k == "concat":
        s1, a1 = _build(node[1], nfa)
        s2, a2 = _build(node[2], nfa)
        nfa.char[a1] = None
        nfa.out1[a1] = s2
        return s1, a2
    if k == "alt":
        s1, a1 = _build(node[1], nfa)
        s2, a2 = _build(node[2], nfa)
        ns = nfa.new(None, s1, s2)
        na = nfa.new(None)
        nfa.char[a1] = None
        nfa.out1[a1] = na
        nfa.char[a2] = None
        nfa.out1[a2] = na
        return ns, na
    if k == "*":
        s, a = _build(node[1], nfa)
        ns = nfa.new(None, s, -1)
        na = nfa.new(None)
        nfa.out2[ns] = na
        nfa.char[a] = None
        nfa.out1[a] = ns
        return ns, na
    if k == "+":
        s, a = _build(node[1], nfa)
        sp = nfa.new(None, s, -1)
        na = nfa.new(None)
        nfa.out2[sp] = na
        nfa.char[a] = None
        nfa.out1[a] = sp
        return s, na
    if k == "?":
        s, a = _build(node[1], nfa)
        ns = nfa.new(None, s, -1)
        na = nfa.new(None)
        nfa.out2[ns] = na
        nfa.char[a] = None
        nfa.out1[a] = na
        return ns, na


def _compile(p):
    nfa = _NFA()
    s, a = _build(_Parser(p).parse(), nfa)
    nfa.start = s
    nfa.accept = a
    return nfa


def _eclose(nfa, st):
    cl = set(st)
    stk = list(st)
    while stk:
        s = stk.pop()
        if nfa.char[s] is None:
            for t in (nfa.out1[s], nfa.out2[s]):
                if t != -1 and t not in cl:
                    cl.add(t)
                    stk.append(t)
    return cl


def _step(nfa, st, c):
    n = set()
    for s in st:
        ch = nfa.char[s]
        if ch is not None and (ch == "." or ch == c):
            if nfa.out1[s] != -1:
                n.add(nfa.out1[s])
    return _eclose(nfa, n)


def _fullmatch(pat, text):
    nfa = _compile(pat)
    st = _eclose(nfa, {nfa.start})
    for c in text:
        st = _step(nfa, st, c)
        if not st:
            return False
    return nfa.accept in st


def _search(pat, text):
    nfa = _compile(pat)
    st = _eclose(nfa, {nfa.start})
    if nfa.accept in st:
        return True
    for c in text:
        st = _step(nfa, st, c) | _eclose(nfa, {nfa.start})
        if nfa.accept in st:
            return True
    return False


# ===================================================================
# Exercise 1: Literal Match
# ===================================================================

def lit_match(pattern, text):
    """fullmatch for pattern with NO metacharacters (only literals)."""
    # TODO: build NFA and simulate (or simply compare strings)
    pass


def _sol_lit_match(pattern, text):
    return _fullmatch(pattern, text)


# ===================================================================
# Exercise 2: Wildcard '.'
# ===================================================================

def wildcard_match(pattern, text):
    """fullmatch supporting '.' as any single char."""
    # TODO
    pass


def _sol_wildcard_match(pattern, text):
    return _fullmatch(pattern, text)


# ===================================================================
# Exercise 3: Star Quantifier
# ===================================================================

def star_match(pattern, text):
    """fullmatch supporting '*' (zero or more)."""
    # TODO
    pass


def _sol_star_match(pattern, text):
    return _fullmatch(pattern, text)


# ===================================================================
# Exercise 4: Plus and Optional
# ===================================================================

def plus_opt_match(pattern, text):
    """fullmatch supporting '+' and '?'."""
    # TODO
    pass


def _sol_plus_opt_match(pattern, text):
    return _fullmatch(pattern, text)


# ===================================================================
# Exercise 5: Alternation and Grouping
# ===================================================================

def alt_match(pattern, text):
    """fullmatch supporting '|', '(', ')'."""
    # TODO
    pass


def _sol_alt_match(pattern, text):
    return _fullmatch(pattern, text)


# ===================================================================
# Exercise 6: Substring Search
# ===================================================================
# True iff pattern matches any contiguous substring of text.

def regex_search(pattern, text):
    """True iff pattern matches any substring of text."""
    # TODO
    pass


def _sol_regex_search(pattern, text):
    return _search(pattern, text)


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

    print("Exercise 1: Literal Match")
    check("equal", try_or_sol("lit_match", "hello", "hello"), True)
    check("differ", try_or_sol("lit_match", "hello", "world"), False)
    check("prefix not match", try_or_sol("lit_match", "hello", "hello!"), False)

    print("\nExercise 2: Wildcard")
    check("h.llo/hello", try_or_sol("wildcard_match", "h.llo", "hello"), True)
    check("h.llo/hallo", try_or_sol("wildcard_match", "h.llo", "hallo"), True)
    check("...", try_or_sol("wildcard_match", "...", "abc"), True)
    check("... too short", try_or_sol("wildcard_match", "...", "ab"), False)

    print("\nExercise 3: Star")
    check("a*", try_or_sol("star_match", "a*", ""), True)
    check("a*aaaa", try_or_sol("star_match", "a*", "aaaa"), True)
    check("a*b/aaab", try_or_sol("star_match", "a*b", "aaab"), True)
    check("a*b/aaa", try_or_sol("star_match", "a*b", "aaa"), False)

    print("\nExercise 4: Plus & Optional")
    check("a+/empty", try_or_sol("plus_opt_match", "a+", ""), False)
    check("a+/a", try_or_sol("plus_opt_match", "a+", "a"), True)
    check("colou?r/color", try_or_sol("plus_opt_match", "colou?r", "color"), True)
    check("colou?r/colour", try_or_sol("plus_opt_match", "colou?r", "colour"), True)

    print("\nExercise 5: Alternation")
    check("a|b/a", try_or_sol("alt_match", "a|b", "a"), True)
    check("a|b/c", try_or_sol("alt_match", "a|b", "c"), False)
    check("(ab)+/abab", try_or_sol("alt_match", "(ab)+", "abab"), True)
    check("(cat|dog)s/cats", try_or_sol("alt_match", "(cat|dog)s", "cats"), True)

    print("\nExercise 6: Substring Search")
    check("abc in xxabc", try_or_sol("regex_search", "abc", "xxabcyy"), True)
    check("abc not in xy", try_or_sol("regex_search", "abc", "xyxy"), False)
    check("a+ in bbbab", try_or_sol("regex_search", "a+", "bbbab"), True)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
