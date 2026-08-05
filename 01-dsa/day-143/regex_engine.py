"""
Day 143: Regex Engine via Thompson Construction

Operators: literal, concat, | , *, ?, grouping with ( ).
Pipeline: infix -> insert concat -> postfix -> NFA -> simulate.
"""

CONCAT = "\x08"   # internal sentinel for explicit concatenation
EPS = None        # None on a transition label means epsilon


# ---------------------------------------------------------------------------
# 1. Insert explicit concat operator
# ---------------------------------------------------------------------------

def insert_concat(regex):
    """
    Walk the infix regex and insert CONCAT between two tokens that should be
    concatenated. Concatenation goes between (a)(b), ab, a(b, )a, *b, ?b, etc.
    """
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
# 2. Shunting yard: infix -> postfix
# ---------------------------------------------------------------------------

PREC = {"|": 1, CONCAT: 2, "?": 3, "*": 3}


def to_postfix(regex):
    """Standard Dijkstra shunting yard. All operators left-assoc."""
    out = []
    ops = []
    for c in regex:
        if c == "(":
            ops.append(c)
        elif c == ")":
            while ops and ops[-1] != "(":
                out.append(ops.pop())
            assert ops, "Unbalanced parens"
            ops.pop()
        elif c in PREC:
            while ops and ops[-1] != "(" and PREC.get(ops[-1], 0) >= PREC[c]:
                out.append(ops.pop())
            ops.append(c)
        else:
            out.append(c)
    while ops:
        op = ops.pop()
        assert op != "(", "Unbalanced parens"
        out.append(op)
    return out


# ---------------------------------------------------------------------------
# 3. Thompson NFA construction
# ---------------------------------------------------------------------------

class State:
    __slots__ = ("eps", "char", "target", "is_accept")

    def __init__(self):
        self.eps = []        # list of epsilon-target states
        self.char = None     # char to match (or None if only eps)
        self.target = None   # state to go to on char
        self.is_accept = False

    def __repr__(self):
        return f"<State id={id(self) % 10000}>"


class Fragment:
    """An NFA fragment: a start state and a list of dangling outputs.

    Each 'output' is a (state, attr, value) triple meaning: setting
    state.<attr> to the eventual destination wires the dangling edge.
    Outputs are attached by `patch` below.
    """
    def __init__(self, start, outs):
        self.start = start
        self.outs = outs   # list of callables: out(target_state) -> wires it


def patch(outs, state):
    for out in outs:
        out(state)


def build_nfa(postfix):
    """Pop fragments off a stack per postfix token; final stack top is full NFA."""
    stack = []
    for tok in postfix:
        if tok == CONCAT:
            f2 = stack.pop()
            f1 = stack.pop()
            patch(f1.outs, f2.start)
            stack.append(Fragment(f1.start, f2.outs))
        elif tok == "|":
            f2 = stack.pop()
            f1 = stack.pop()
            s = State()
            s.eps.append(f1.start)
            s.eps.append(f2.start)
            stack.append(Fragment(s, f1.outs + f2.outs))
        elif tok == "*":
            f = stack.pop()
            s = State()
            s.eps.append(f.start)
            # one dangling out for the new start (when we loop ends)
            def out(target, st=s):
                st.eps.append(target)
            patch(f.outs, s)
            stack.append(Fragment(s, [out]))
        elif tok == "?":
            f = stack.pop()
            s = State()
            s.eps.append(f.start)
            def out(target, st=s):
                st.eps.append(target)
            stack.append(Fragment(s, f.outs + [out]))
        else:
            # literal
            s = State()
            s.char = tok
            def out(target, st=s):
                st.target = target
            stack.append(Fragment(s, [out]))
    assert len(stack) == 1, f"Bad postfix: stack={stack}"
    final = State()
    final.is_accept = True
    patch(stack[0].outs, final)
    return stack[0].start, final


# ---------------------------------------------------------------------------
# 4. Simulation
# ---------------------------------------------------------------------------

def epsilon_closure(states):
    """BFS over epsilon edges from `states`. Return the closure set."""
    closure = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        for t in s.eps:
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def match(regex, text):
    """Full match: does regex accept the entire text?"""
    if not regex:
        return text == ""
    pf = to_postfix(insert_concat(regex))
    start, _final = build_nfa(pf)
    current = epsilon_closure({start})
    for c in text:
        nxt = set()
        for s in current:
            if s.char == c and s.target is not None:
                nxt.add(s.target)
        current = epsilon_closure(nxt)
        if not current:
            return False
    return any(s.is_accept for s in current)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 143: Regex Engine (Thompson construction)")
    print("=" * 60)

    cases = [
        ("a",            ["a",   "",   "ab"],   [True, False, False]),
        ("ab",           ["ab",  "a",  "abc"],  [True, False, False]),
        ("a|b",          ["a",   "b",  "ab"],   [True, True, False]),
        ("a*",           ["",    "a",  "aaaa", "ab"], [True, True, True, False]),
        ("a?b",          ["b",   "ab", "aab"],  [True, True, False]),
        ("(a|b)*c",      ["c",   "ac", "bbac", "abx"], [True, True, True, False]),
        ("a*b*",         ["",    "aaaa", "bbb", "abba"], [True, True, True, False]),
        ("(ab|cd)*",     ["",    "ab", "cdcd", "abcd", "abc"], [True, True, True, True, False]),
    ]
    for regex, inputs, expects in cases:
        print(f"\n  regex /{regex}/")
        for s, exp in zip(inputs, expects):
            got = match(regex, s)
            mark = "OK" if got == exp else "FAIL"
            print(f"    {s!r:14s} -> {got}  (expected {exp})  [{mark}]")

    print("\n--- Pathological case (no catastrophic backtracking) ---")
    # PCRE famously chokes on (a?){30}a^30 against 'a'*30. Thompson stays linear.
    regex = "a?" * 30 + "a" * 30
    text = "a" * 30
    print(f"  regex length {len(regex)}, text length {len(text)}")
    print(f"  matches: {match(regex, text)}  (Thompson handles this in O(n*m))")


if __name__ == "__main__":
    demo()
