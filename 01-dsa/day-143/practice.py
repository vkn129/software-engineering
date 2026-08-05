"""
Day 143 Practice: Regex Engine

6 exercises. Implement TODOs, then run: python practice.py
"""

CONCAT = "\x08"
PREC = {"|": 1, CONCAT: 2, "?": 3, "*": 3}


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: Insert explicit CONCAT between adjacent tokens
# ---------------------------------------------------------------------------

def insert_concat(regex):
    """Insert CONCAT char between tokens that should be concatenated."""
    # TODO
    pass


def _sol_insert_concat(regex):
    out = []
    for i, c in enumerate(regex):
        out.append(c)
        if c in "(|":
            continue
        if i + 1 < len(regex):
            nxt = regex[i + 1]
            if nxt in ")|*?":
                continue
            out.append(CONCAT)
    return "".join(out)


# ---------------------------------------------------------------------------
# Exercise 2: Shunting yard to postfix
# ---------------------------------------------------------------------------

def to_postfix(regex_with_concat):
    """Convert infix (with CONCAT explicit) to postfix list of tokens."""
    # TODO
    pass


def _sol_to_postfix(regex):
    out = []
    ops = []
    for c in regex:
        if c == "(":
            ops.append(c)
        elif c == ")":
            while ops and ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()
        elif c in PREC:
            while ops and ops[-1] != "(" and PREC.get(ops[-1], 0) >= PREC[c]:
                out.append(ops.pop())
            ops.append(c)
        else:
            out.append(c)
    while ops:
        out.append(ops.pop())
    return out


# ---------------------------------------------------------------------------
# Exercise 3: Match a single literal regex (no operators)
# ---------------------------------------------------------------------------

def match_literal(pattern, text):
    """Exact string equality. Return True iff pattern == text."""
    # TODO
    pass


def _sol_match_literal(pattern, text):
    return pattern == text


# ---------------------------------------------------------------------------
# Exercise 4: Simple matcher for alternation only (no nesting, no *, no ?)
# ---------------------------------------------------------------------------

def match_alt(pattern, text):
    """Pattern like 'foo|bar|baz'. Return True iff text equals one branch."""
    # TODO
    pass


def _sol_match_alt(pattern, text):
    return text in pattern.split("|")


# ---------------------------------------------------------------------------
# Exercise 5: Full Thompson matcher (use the solution NFA below)
# ---------------------------------------------------------------------------

class _State:
    __slots__ = ("eps", "char", "target", "is_accept")
    def __init__(self):
        self.eps = []
        self.char = None
        self.target = None
        self.is_accept = False


def _patch(outs, state):
    for o in outs:
        o(state)


def _build_nfa(postfix):
    stack = []
    for tok in postfix:
        if tok == CONCAT:
            f2 = stack.pop(); f1 = stack.pop()
            _patch(f1[1], f2[0])
            stack.append((f1[0], f2[1]))
        elif tok == "|":
            f2 = stack.pop(); f1 = stack.pop()
            s = _State()
            s.eps.append(f1[0]); s.eps.append(f2[0])
            stack.append((s, f1[1] + f2[1]))
        elif tok == "*":
            f = stack.pop()
            s = _State()
            s.eps.append(f[0])
            out = lambda t, st=s: st.eps.append(t)
            _patch(f[1], s)
            stack.append((s, [out]))
        elif tok == "?":
            f = stack.pop()
            s = _State()
            s.eps.append(f[0])
            out = lambda t, st=s: st.eps.append(t)
            stack.append((s, f[1] + [out]))
        else:
            s = _State()
            s.char = tok
            out = lambda t, st=s: setattr(st, "target", t)
            stack.append((s, [out]))
    final = _State()
    final.is_accept = True
    _patch(stack[0][1], final)
    return stack[0][0]


def _eps_closure(states):
    closure = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        for t in s.eps:
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def regex_match(regex, text):
    """Compile and match. Return True iff regex fully accepts text."""
    # TODO: implement using _build_nfa, _eps_closure, insert_concat, to_postfix
    pass


def _sol_regex_match(regex, text):
    if not regex:
        return text == ""
    pf = _sol_to_postfix(_sol_insert_concat(regex))
    start = _build_nfa(pf)
    current = _eps_closure({start})
    for c in text:
        nxt = set()
        for s in current:
            if s.char == c and s.target is not None:
                nxt.add(s.target)
        current = _eps_closure(nxt)
        if not current:
            return False
    return any(s.is_accept for s in current)


# ---------------------------------------------------------------------------
# Exercise 6: Character class via alternation (utility helper)
# ---------------------------------------------------------------------------

def expand_class(chars):
    """Convert e.g. 'abc' into regex string '(a|b|c)'. Empty -> ''."""
    # TODO
    pass


def _sol_expand_class(chars):
    if not chars:
        return ""
    return "(" + "|".join(chars) + ")"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got!r}  expected={expected!r}")
            failed += 1

    print("Exercise 1: insert_concat")
    check("ab", try_or_sol("insert_concat", "ab"), f"a{CONCAT}b")
    check("a|b", try_or_sol("insert_concat", "a|b"), "a|b")
    check("a*b", try_or_sol("insert_concat", "a*b"), f"a*{CONCAT}b")
    check("(a|b)c", try_or_sol("insert_concat", "(a|b)c"), f"(a|b){CONCAT}c")

    print("\nExercise 2: to_postfix")
    check("ab", try_or_sol("to_postfix", f"a{CONCAT}b"), ["a", "b", CONCAT])
    check("a|b", try_or_sol("to_postfix", "a|b"), ["a", "b", "|"])
    check("a*", try_or_sol("to_postfix", "a*"), ["a", "*"])
    # (a|b)c -> ab|c.
    check("(a|b)c", try_or_sol("to_postfix", f"(a|b){CONCAT}c"),
          ["a", "b", "|", "c", CONCAT])

    print("\nExercise 3: match_literal")
    check("exact", try_or_sol("match_literal", "abc", "abc"), True)
    check("mismatch", try_or_sol("match_literal", "abc", "abd"), False)
    check("empty", try_or_sol("match_literal", "", ""), True)

    print("\nExercise 4: match_alt")
    check("first branch", try_or_sol("match_alt", "foo|bar", "foo"), True)
    check("second branch", try_or_sol("match_alt", "foo|bar", "bar"), True)
    check("no branch", try_or_sol("match_alt", "foo|bar", "baz"), False)

    print("\nExercise 5: regex_match")
    cases = [
        ("a", "a", True), ("a", "b", False),
        ("ab", "ab", True), ("ab", "a", False),
        ("a|b", "a", True), ("a|b", "b", True), ("a|b", "c", False),
        ("a*", "", True), ("a*", "aaaa", True), ("a*", "ab", False),
        ("a?b", "b", True), ("a?b", "ab", True), ("a?b", "aab", False),
        ("(a|b)*c", "c", True), ("(a|b)*c", "abbac", True),
        ("(a|b)*c", "abx", False),
    ]
    for r, t, e in cases:
        check(f"/{r}/ on {t!r}", try_or_sol("regex_match", r, t), e)

    print("\nExercise 6: expand_class")
    check("abc", try_or_sol("expand_class", "abc"), "(a|b|c)")
    check("single", try_or_sol("expand_class", "x"), "(x)")
    check("empty", try_or_sol("expand_class", ""), "")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
