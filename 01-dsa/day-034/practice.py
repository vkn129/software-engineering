"""
Day 34 Practice: Expression Evaluation Exercises

5 exercises that build on the core expression evaluation pipeline.
Each exercise has a TODO stub and a _sol_ solution below it.

Rules:
- Do NOT import any libraries (except math for Exercise 5 only).
- Build on the concepts from expression_eval.py.
- Comments explain WHY, not WHAT.

Run: python practice.py
"""


# ==========================================================================
# Exercise 1: Basic Calculator (+ - and parentheses only)
# ==========================================================================
# LeetCode 224 pattern. Given a string with +, -, (, ), and non-negative
# integers, evaluate it.
#
# Why this is useful: this is the simplest non-trivial expression evaluator.
# It forces you to handle parentheses and unary minus without the complexity
# of precedence (since + and - have the same precedence). Many interview
# problems are variations of this.

def basic_calculator(s):
    """Evaluate expression with +, -, (, ) and non-negative integers.

    Examples:
        "1 + 1"         → 2
        " 2-1 + 2 "     → 3
        "(1+(4+5+2)-3)+(6+8)" → 23
        "-2 + 3"        → 1

    Hint: Use a stack to handle parentheses. When you see '(', push
    the current result and sign onto the stack. When you see ')',
    pop and combine. This avoids full tokenize → postfix conversion
    for the simpler case.
    """
    # TODO: implement this
    pass


def _sol_basic_calculator(s):
    """Stack-based approach: track running result and current sign.

    The key insight: parentheses create nested scopes. A stack stores
    the "outer" result and sign when we enter a scope, and restores
    them when we leave. This is simpler than full shunting-yard because
    we only have two operators at the same precedence level.
    """
    stack = []
    result = 0
    num = 0
    sign = 1  # +1 or -1, representing the sign before the current number

    for ch in s:
        if ch.isdigit():
            # Build multi-digit number. Multiply by 10 to shift previous
            # digits left, then add new digit. Same as int("42") but
            # character by character.
            num = num * 10 + int(ch)
        elif ch == '+':
            # Flush the current number with its sign, reset for next number.
            result += sign * num
            num = 0
            sign = 1
        elif ch == '-':
            result += sign * num
            num = 0
            sign = -1
        elif ch == '(':
            # Save current state (result so far and pending sign) and
            # start fresh inside the parentheses. When we hit ')', we
            # will combine.
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif ch == ')':
            # Flush current number, then combine with saved state.
            # The saved sign tells us whether this parenthesized group
            # is added or subtracted from the outer result.
            result += sign * num
            num = 0
            result *= stack.pop()   # saved sign
            result += stack.pop()   # saved result
        # Spaces are ignored — we just skip them.

    # Flush the last number (no trailing operator to trigger it).
    result += sign * num
    return result


# ==========================================================================
# Exercise 2: Evaluate with Variables
# ==========================================================================
# Extend the evaluator to handle named variables. A variable mapping is
# provided as a dictionary.
#
# Why this matters: every real expression evaluator (SQL WHERE clauses,
# template engines, config languages) supports variables. The change is
# small — add a VAR token type and look it up during evaluation — but it
# bridges the gap between "calculator" and "interpreter."

def evaluate_with_vars(expr, variables):
    """Evaluate an infix expression where tokens can be variable names.

    Supports: +, -, *, /, ^, (, ), numbers, and variable names.
    Variable names are alphabetic strings (e.g., "x", "speed").

    Args:
        expr: string like "x + y * 2"
        variables: dict like {"x": 10, "y": 3}

    Returns:
        Numeric result.

    Examples:
        evaluate_with_vars("x + y * 2", {"x": 10, "y": 3})  → 16
        evaluate_with_vars("(a + b) ^ 2", {"a": 1, "b": 2}) → 9
    """
    # TODO: implement this
    pass


def _sol_evaluate_with_vars(expr, variables):
    """Tokenize with variable support, then use standard shunting-yard.

    The only change from the base implementation: during tokenization,
    alphabetic strings become VAR tokens. During postfix evaluation,
    VAR tokens are looked up in the variables dict. Everything else
    (shunting-yard, precedence, associativity) stays the same.

    This demonstrates a key design principle: if your pipeline is well-
    separated (tokenize → convert → evaluate), adding features means
    changing one stage, not rewriting everything.
    """
    OPERATORS = {
        '+': (1, 'L'), '-': (1, 'L'),
        '*': (2, 'L'), '/': (2, 'L'),
        '^': (3, 'R'),
    }
    UNARY_NEG_PREC = 4

    # --- Tokenize (extended with VAR support) ---
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue
        if ch.isalpha():
            # Variable names: consume all consecutive alpha characters.
            start = i
            while i < n and expr[i].isalpha():
                i += 1
            tokens.append(('VAR', expr[start:i]))
            continue
        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue
        if ch in OPERATORS:
            if ch == '-':
                is_unary = (
                    len(tokens) == 0 or
                    tokens[-1][0] in ('LPAREN', 'OP', 'NEG')
                )
                if is_unary:
                    tokens.append(('NEG', '~'))
                    i += 1
                    continue
            tokens.append(('OP', ch))
            i += 1
            continue
        raise ValueError(f"Unexpected character '{ch}'")

    # --- Shunting-yard (VAR tokens are treated like NUM — go to output) ---
    def prec(tok):
        if tok[0] == 'NEG':
            return UNARY_NEG_PREC
        return OPERATORS[tok[1]][0]

    def left_assoc(tok):
        if tok[0] == 'NEG':
            return False
        return OPERATORS[tok[1]][1] == 'L'

    output = []
    op_stack = []
    for tok in tokens:
        if tok[0] in ('NUM', 'VAR'):
            output.append(tok)
        elif tok[0] in ('OP', 'NEG'):
            while (op_stack and op_stack[-1][0] != 'LPAREN' and
                   (prec(op_stack[-1]) > prec(tok) or
                    (prec(op_stack[-1]) == prec(tok) and left_assoc(tok)))):
                output.append(op_stack.pop())
            op_stack.append(tok)
        elif tok[0] == 'LPAREN':
            op_stack.append(tok)
        elif tok[0] == 'RPAREN':
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            op_stack.pop()
    while op_stack:
        output.append(op_stack.pop())

    # --- Evaluate postfix (VAR tokens looked up in dict) ---
    stack = []
    for tok in output:
        if tok[0] == 'NUM':
            stack.append(tok[1])
        elif tok[0] == 'VAR':
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Undefined variable: {name}")
            stack.append(variables[name])
        elif tok[0] == 'NEG':
            stack.append(-stack.pop())
        elif tok[0] == 'OP':
            r = stack.pop()
            l = stack.pop()
            if tok[1] == '+': stack.append(l + r)
            elif tok[1] == '-': stack.append(l - r)
            elif tok[1] == '*': stack.append(l * r)
            elif tok[1] == '/': stack.append(l / r)
            elif tok[1] == '^': stack.append(l ** r)
    return stack[0]


# ==========================================================================
# Exercise 3: Infix to Prefix Conversion
# ==========================================================================
# Prefix notation (Polish notation) puts the operator BEFORE its operands.
# Infix: 3 + 4 * 2  →  Prefix: + 3 * 4 2
#
# Why prefix matters: it is the notation Lisp uses, and it maps directly
# to function calls: +(3, *(4, 2)). It is also the pre-order traversal
# of the expression tree. Understanding all three notations (infix, prefix,
# postfix) means understanding tree traversals from a different angle.

def infix_to_prefix(expr):
    """Convert an infix expression string to prefix notation string.

    Args:
        expr: string like "3 + 4 * 2"

    Returns:
        string like "+ 3 * 4 2"

    Examples:
        "3 + 4 * 2"       → "+ 3 * 4 2"
        "(3 + 4) * 2"     → "* + 3 4 2"
        "2 ^ 3 ^ 2"       → "^ 2 ^ 3 2"

    Hint: One approach — reverse the expression, swap ( and ), run
    shunting-yard with adjusted associativity, reverse the output.
    Another approach — build the expression tree and do pre-order traversal.
    """
    # TODO: implement this
    pass


def _sol_infix_to_prefix(expr):
    """Build expression tree, then pre-order traverse.

    We reuse the pipeline from expression_eval.py conceptually:
    tokenize → postfix → tree → pre-order string.

    The tree approach is cleaner than the "reverse and swap" trick because
    it is obvious WHY it works: pre-order traversal of the AST is, by
    definition, prefix notation.
    """
    OPERATORS = {
        '+': (1, 'L'), '-': (1, 'L'),
        '*': (2, 'L'), '/': (2, 'L'),
        '^': (3, 'R'),
    }

    # --- Tokenize ---
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue
        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue
        if ch in OPERATORS:
            tokens.append(('OP', ch))
            i += 1
            continue
        raise ValueError(f"Unexpected character '{ch}'")

    # --- Shunting-yard ---
    def prec(tok):
        return OPERATORS[tok[1]][0]

    def left_assoc(tok):
        return OPERATORS[tok[1]][1] == 'L'

    output = []
    op_stack = []
    for tok in tokens:
        if tok[0] == 'NUM':
            output.append(tok)
        elif tok[0] == 'OP':
            while (op_stack and op_stack[-1][0] != 'LPAREN' and
                   (prec(op_stack[-1]) > prec(tok) or
                    (prec(op_stack[-1]) == prec(tok) and left_assoc(tok)))):
                output.append(op_stack.pop())
            op_stack.append(tok)
        elif tok[0] == 'LPAREN':
            op_stack.append(tok)
        elif tok[0] == 'RPAREN':
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            op_stack.pop()
    while op_stack:
        output.append(op_stack.pop())

    # --- Build tree from postfix ---
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    stack = []
    for tok in output:
        if tok[0] == 'NUM':
            stack.append(Node(tok[1]))
        elif tok[0] == 'OP':
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(tok[1], left, right))
    root = stack[0]

    # --- Pre-order traversal = prefix notation ---
    def preorder(node):
        if node.left is None and node.right is None:
            # Leaf: format number (no trailing .0 for integers)
            v = node.val
            return str(int(v)) if v == int(v) else str(v)
        parts = [str(node.val)]
        parts.append(preorder(node.left))
        parts.append(preorder(node.right))
        return ' '.join(parts)

    return preorder(root)


# ==========================================================================
# Exercise 4: Pretty-Print Expression Tree
# ==========================================================================
# Visualizing the tree makes the structure concrete. This is useful for
# debugging compilers and understanding how precedence creates tree shape.
#
# Why this matters: every compiler has a --dump-ast flag. Being able to
# print a tree readably is a fundamental debugging skill.

def pretty_print_tree(expr):
    """Build an expression tree and return a multi-line string visualization.

    Args:
        expr: infix expression string like "3 + 4 * 2"

    Returns:
        Multi-line string showing the tree structure.

    Example output for "3 + 4 * 2":
        +
        ├── 3
        └── *
            ├── 4
            └── 2

    Example output for "(3 + 4) * 2":
        *
        ├── +
        │   ├── 3
        │   └── 4
        └── 2
    """
    # TODO: implement this
    pass


def _sol_pretty_print_tree(expr):
    """Build tree, then recursively format with box-drawing characters.

    The formatting uses Unicode box-drawing characters for clean output.
    Each recursive call adds a prefix that depends on whether this node
    is the last child (└──) or not (├──). The accumulated prefix creates
    the vertical lines (│) that connect siblings.
    """
    OPERATORS = {
        '+': (1, 'L'), '-': (1, 'L'),
        '*': (2, 'L'), '/': (2, 'L'),
        '^': (3, 'R'),
    }

    # --- Tokenize ---
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue
        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue
        if ch in OPERATORS:
            tokens.append(('OP', ch))
            i += 1
            continue
        raise ValueError(f"Unexpected character '{ch}'")

    # --- Shunting-yard ---
    def prec(tok):
        return OPERATORS[tok[1]][0]
    def left_assoc(tok):
        return OPERATORS[tok[1]][1] == 'L'

    output = []
    op_stack = []
    for tok in tokens:
        if tok[0] == 'NUM':
            output.append(tok)
        elif tok[0] == 'OP':
            while (op_stack and op_stack[-1][0] != 'LPAREN' and
                   (prec(op_stack[-1]) > prec(tok) or
                    (prec(op_stack[-1]) == prec(tok) and left_assoc(tok)))):
                output.append(op_stack.pop())
            op_stack.append(tok)
        elif tok[0] == 'LPAREN':
            op_stack.append(tok)
        elif tok[0] == 'RPAREN':
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            op_stack.pop()
    while op_stack:
        output.append(op_stack.pop())

    # --- Build tree ---
    class Node:
        def __init__(self, val, ntype, left=None, right=None):
            self.val = val
            self.ntype = ntype
            self.left = left
            self.right = right

    stack = []
    for tok in output:
        if tok[0] == 'NUM':
            stack.append(Node(tok[1], 'NUM'))
        elif tok[0] == 'OP':
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(tok[1], 'OP', left, right))

    if not stack:
        return ""
    root = stack[0]

    # --- Format tree ---
    def fmt_val(node):
        if node.ntype == 'NUM':
            v = node.val
            return str(int(v)) if v == int(v) else str(v)
        return str(node.val)

    lines = []

    def build(node, prefix, is_last):
        """Recursively build lines for the tree.

        prefix: the string to prepend (builds up │ and spaces from ancestors)
        is_last: whether this node is the last child of its parent
        """
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + fmt_val(node))

        # Collect children (binary tree: left then right)
        children = []
        if node.left is not None:
            children.append(node.left)
        if node.right is not None:
            children.append(node.right)

        # The prefix extension: if this node is the last child, its
        # sub-tree does not need a vertical bar. Otherwise, draw │.
        extension = "    " if is_last else "│   "
        for i, child in enumerate(children):
            build(child, prefix + extension, i == len(children) - 1)

    # Root has no connector prefix
    lines.append(fmt_val(root))
    children = []
    if root.left is not None:
        children.append(root.left)
    if root.right is not None:
        children.append(root.right)
    for i, child in enumerate(children):
        build(child, "", i == len(children) - 1)

    return '\n'.join(lines)


# ==========================================================================
# Exercise 5: Add sin() and sqrt() Function Support
# ==========================================================================
# Extend the expression evaluator to handle function calls.
#
# Why this matters: the jump from "calculator" to "programming language"
# starts with function calls. Functions are syntactically different from
# operators (they use name + parens), so the tokenizer, shunting-yard,
# and evaluator all need small extensions. This teaches you how language
# features compose.
#
# math module IS allowed for this exercise only (for sin, sqrt values).

def evaluate_with_functions(expr):
    """Evaluate an expression that may contain sin() and sqrt() calls.

    Supports: +, -, *, /, ^, (, ), numbers, sin(), sqrt().
    Assumes single-argument functions only.

    Examples:
        "sqrt(4)"           → 2.0
        "sin(0)"            → 0.0
        "sqrt(9) + 1"       → 4.0
        "sin(0) + sqrt(16)" → 4.0
        "sqrt(2 ^ 2 + 3 ^ 2)" → ~3.605

    Hint: Add a FUNC token type. In shunting-yard, push FUNC onto the
    operator stack. When you encounter ')' and the top of the stack
    (after popping to '(') is a FUNC, pop it to the output. During
    postfix evaluation, FUNC pops one value and applies the function.
    """
    # TODO: implement this
    pass


def _sol_evaluate_with_functions(expr):
    """Extended pipeline with FUNC token support.

    The shunting-yard extension for functions:
    1. Tokenizer recognizes known function names → FUNC tokens
    2. FUNC tokens are pushed onto the operator stack (like a prefix operator)
    3. When ')' is encountered and a FUNC sits on top after popping to '(',
       the FUNC is moved to output
    4. During postfix evaluation, FUNC pops one operand and applies the function

    This is exactly how Dijkstra described function handling in the original
    shunting-yard paper.
    """
    import math

    OPERATORS = {
        '+': (1, 'L'), '-': (1, 'L'),
        '*': (2, 'L'), '/': (2, 'L'),
        '^': (3, 'R'),
    }
    FUNCTIONS = {'sin': math.sin, 'sqrt': math.sqrt}
    UNARY_NEG_PREC = 4

    # --- Tokenize (extended with FUNC) ---
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue
        if ch.isalpha():
            start = i
            while i < n and expr[i].isalpha():
                i += 1
            name = expr[start:i]
            if name in FUNCTIONS:
                tokens.append(('FUNC', name))
            else:
                raise ValueError(f"Unknown identifier: {name}")
            continue
        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue
        if ch in OPERATORS:
            if ch == '-':
                is_unary = (
                    len(tokens) == 0 or
                    tokens[-1][0] in ('LPAREN', 'OP', 'NEG', 'FUNC')
                )
                if is_unary:
                    tokens.append(('NEG', '~'))
                    i += 1
                    continue
            tokens.append(('OP', ch))
            i += 1
            continue
        raise ValueError(f"Unexpected character '{ch}'")

    # --- Shunting-yard (extended with FUNC) ---
    def prec(tok):
        if tok[0] == 'NEG':
            return UNARY_NEG_PREC
        return OPERATORS[tok[1]][0]

    def left_assoc(tok):
        if tok[0] == 'NEG':
            return False
        return OPERATORS[tok[1]][1] == 'L'

    output = []
    op_stack = []
    for tok in tokens:
        if tok[0] == 'NUM':
            output.append(tok)
        elif tok[0] == 'FUNC':
            # Functions go on the operator stack, just like '('.
            # They will be popped when we hit the matching ')'.
            op_stack.append(tok)
        elif tok[0] in ('OP', 'NEG'):
            while (op_stack and op_stack[-1][0] not in ('LPAREN', 'FUNC') and
                   (prec(op_stack[-1]) > prec(tok) or
                    (prec(op_stack[-1]) == prec(tok) and left_assoc(tok)))):
                output.append(op_stack.pop())
            op_stack.append(tok)
        elif tok[0] == 'LPAREN':
            op_stack.append(tok)
        elif tok[0] == 'RPAREN':
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parentheses")
            op_stack.pop()  # pop '('
            # If a function sits on top of the stack, pop it to output.
            # This handles sin(...) — the FUNC was pushed before the '('.
            if op_stack and op_stack[-1][0] == 'FUNC':
                output.append(op_stack.pop())
    while op_stack:
        output.append(op_stack.pop())

    # --- Evaluate postfix (extended with FUNC) ---
    stack = []
    for tok in output:
        if tok[0] == 'NUM':
            stack.append(tok[1])
        elif tok[0] == 'NEG':
            stack.append(-stack.pop())
        elif tok[0] == 'FUNC':
            # Functions consume one argument (single-argument functions).
            arg = stack.pop()
            stack.append(FUNCTIONS[tok[1]](arg))
        elif tok[0] == 'OP':
            r = stack.pop()
            l = stack.pop()
            if tok[1] == '+': stack.append(l + r)
            elif tok[1] == '-': stack.append(l - r)
            elif tok[1] == '*': stack.append(l * r)
            elif tok[1] == '/': stack.append(l / r)
            elif tok[1] == '^': stack.append(l ** r)
    return stack[0]


# ==========================================================================
# Test runner
# ==========================================================================

def run_tests():
    """Run all exercises and verify solutions."""
    import math

    passed = 0
    failed = 0

    def check(name, got, expected, tolerance=None):
        nonlocal passed, failed
        if tolerance is not None:
            ok = abs(got - expected) < tolerance
        else:
            ok = got == expected
        if ok:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} — got {got}, expected {expected}")

    # --- Exercise 1: Basic Calculator ---
    print("\nExercise 1: Basic Calculator")
    for fn_name, fn in [("yours", basic_calculator), ("solution", _sol_basic_calculator)]:
        if fn("1 + 1") is None and fn_name == "yours":
            print(f"  SKIP: {fn_name} (not implemented)")
            continue
        print(f"  [{fn_name}]")
        check("1 + 1", fn("1 + 1"), 2)
        check("2-1 + 2", fn(" 2-1 + 2 "), 3)
        check("nested parens", fn("(1+(4+5+2)-3)+(6+8)"), 23)
        check("unary minus", fn("-2 + 3"), 1)
        check("double parens", fn("((3))"), 3)
        check("negative result", fn("1 - 5"), -4)

    # --- Exercise 2: Evaluate with Variables ---
    print("\nExercise 2: Evaluate with Variables")
    for fn_name, fn in [("yours", evaluate_with_vars), ("solution", _sol_evaluate_with_vars)]:
        if fn("x", {"x": 1}) is None and fn_name == "yours":
            print(f"  SKIP: {fn_name} (not implemented)")
            continue
        print(f"  [{fn_name}]")
        check("x + y * 2", fn("x + y * 2", {"x": 10, "y": 3}), 16)
        check("(a + b) ^ 2", fn("(a + b) ^ 2", {"a": 1, "b": 2}), 9)
        check("single var", fn("x", {"x": 42}), 42)
        check("var * var", fn("x * x", {"x": 5}), 25)

    # --- Exercise 3: Infix to Prefix ---
    print("\nExercise 3: Infix to Prefix")
    for fn_name, fn in [("yours", infix_to_prefix), ("solution", _sol_infix_to_prefix)]:
        if fn("1 + 2") is None and fn_name == "yours":
            print(f"  SKIP: {fn_name} (not implemented)")
            continue
        print(f"  [{fn_name}]")
        check("3 + 4 * 2", fn("3 + 4 * 2"), "+ 3 * 4 2")
        check("(3 + 4) * 2", fn("(3 + 4) * 2"), "* + 3 4 2")
        check("2 ^ 3 ^ 2", fn("2 ^ 3 ^ 2"), "^ 2 ^ 3 2")
        check("1 + 2 + 3", fn("1 + 2 + 3"), "+ + 1 2 3")

    # --- Exercise 4: Pretty-Print Tree ---
    print("\nExercise 4: Pretty-Print Expression Tree")
    for fn_name, fn in [("yours", pretty_print_tree), ("solution", _sol_pretty_print_tree)]:
        result = fn("3 + 4 * 2")
        if result is None and fn_name == "yours":
            print(f"  SKIP: {fn_name} (not implemented)")
            continue
        print(f"  [{fn_name}]")
        # Check that the tree output contains expected nodes
        tree_str = fn("3 + 4 * 2")
        check("root is +", tree_str.split('\n')[0], "+")
        check("contains *", "*" in tree_str, True)
        check("contains 3", "3" in tree_str, True)
        print(f"    Output:\n{_indent(tree_str, 6)}")

        tree_str2 = fn("(3 + 4) * 2")
        check("grouped root is *", tree_str2.split('\n')[0], "*")
        print(f"    Output:\n{_indent(tree_str2, 6)}")

    # --- Exercise 5: Functions (sin, sqrt) ---
    print("\nExercise 5: Function Support (sin, sqrt)")
    for fn_name, fn in [("yours", evaluate_with_functions), ("solution", _sol_evaluate_with_functions)]:
        if fn("sqrt(4)") is None and fn_name == "yours":
            print(f"  SKIP: {fn_name} (not implemented)")
            continue
        print(f"  [{fn_name}]")
        check("sqrt(4)", fn("sqrt(4)"), 2.0)
        check("sin(0)", fn("sin(0)"), 0.0, tolerance=1e-9)
        check("sqrt(9) + 1", fn("sqrt(9) + 1"), 4.0)
        check("sin(0) + sqrt(16)", fn("sin(0) + sqrt(16)"), 4.0, tolerance=1e-9)
        check("sqrt(2^2 + 3^2)", fn("sqrt(2 ^ 2 + 3 ^ 2)"), math.sqrt(13), tolerance=1e-9)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 40}")


def _indent(text, spaces):
    """Indent every line of text by the given number of spaces."""
    prefix = ' ' * spaces
    return '\n'.join(prefix + line for line in text.split('\n'))


if __name__ == '__main__':
    run_tests()
