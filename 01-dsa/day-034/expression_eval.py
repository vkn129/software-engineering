"""
Day 34: Expression Evaluation — Full Pipeline

This module implements the complete expression evaluation pipeline:
  string → tokens → postfix → result
  string → tokens → postfix → expression tree → result

Supported operators: +, -, *, /, ^ (power), unary minus, parentheses.

The key insight: infix notation is for humans, postfix is for machines.
The shunting-yard algorithm is the bridge between the two worlds.

Run: python expression_eval.py
"""


# ==========================================================================
# Token representation
# ==========================================================================

# We represent tokens as (type, value) tuples.
# Types: 'NUM', 'OP', 'LPAREN', 'RPAREN', 'NEG' (unary minus)
#
# Why tuples instead of a Token class? For a learning exercise, tuples
# make the algorithm's data flow visible. In production you would use
# dataclasses or an enum for type safety.

# Operator metadata: (precedence, associativity)
# Higher precedence number = binds tighter.
# 'L' = left-associative, 'R' = right-associative.
OPERATORS = {
    '+': (1, 'L'),
    '-': (1, 'L'),
    '*': (2, 'L'),
    '/': (2, 'L'),
    '^': (3, 'R'),
}

# Unary minus gets higher precedence than any binary operator
# so that -3^2 is parsed as -(3^2) = -9, matching math convention.
UNARY_NEG_PRECEDENCE = 4


# ==========================================================================
# Step 1: Tokenization
# ==========================================================================

def tokenize(expr):
    """Convert an expression string into a list of (type, value) tokens.

    Handles:
    - Multi-digit numbers and decimals (e.g., 3.14, 100)
    - Operators: +, -, *, /, ^
    - Parentheses
    - Unary minus: detected by context (start of expression, after '(' or
      after another operator)

    Why tokenization is a separate step: it isolates the messy string
    parsing from the clean algorithmic logic of shunting-yard. The
    shunting-yard algorithm does not care whether '42' was one character
    or two — it just sees a NUM token. Separation of concerns.
    """
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        # Skip whitespace — it carries no meaning in arithmetic expressions.
        if ch.isspace():
            i += 1
            continue

        # Numbers: consume all consecutive digits and at most one decimal point.
        # We do this greedily so "314" becomes one token, not three.
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue

        # Parentheses
        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue

        # Operators
        if ch in OPERATORS:
            # Detect unary minus: '-' is unary when there is no operand
            # immediately before it. This happens at the start of the
            # expression, after '(', or after another operator.
            if ch == '-':
                is_unary = (
                    len(tokens) == 0 or
                    tokens[-1][0] == 'LPAREN' or
                    tokens[-1][0] == 'OP' or
                    tokens[-1][0] == 'NEG'
                )
                if is_unary:
                    tokens.append(('NEG', '~'))  # ~ represents unary minus
                    i += 1
                    continue

            tokens.append(('OP', ch))
            i += 1
            continue

        raise ValueError(f"Unexpected character '{ch}' at position {i}")

    return tokens


# ==========================================================================
# Step 2: Shunting-Yard Algorithm (Infix → Postfix)
# ==========================================================================

def _precedence(token):
    """Return precedence of an operator token.

    Why a separate function: keeps the shunting-yard logic clean. The
    algorithm only cares about "is this operator stronger than that one?"
    — the details of which operator has which number live here.
    """
    tok_type, tok_val = token
    if tok_type == 'NEG':
        return UNARY_NEG_PRECEDENCE
    return OPERATORS[tok_val][0]


def _is_left_assoc(token):
    """Return True if the operator is left-associative."""
    tok_type, tok_val = token
    if tok_type == 'NEG':
        # Unary minus is right-associative: --3 means -(-3)
        return False
    return OPERATORS[tok_val][1] == 'L'


def infix_to_postfix(tokens):
    """Convert infix tokens to postfix using the shunting-yard algorithm.

    This is the heart of expression evaluation. The algorithm uses an
    operator stack to reorder tokens so that higher-precedence operators
    come first — eliminating the need for parentheses.

    The invariant maintained: at any point during processing, the operator
    stack contains operators in non-decreasing precedence from bottom to
    top. When a new operator would violate this (because it has lower or
    equal precedence), we pop until the invariant is restored.
    """
    output = []       # The postfix result (a queue, but we use a list)
    op_stack = []     # Operator waiting area

    for token in tokens:
        tok_type, tok_val = token

        if tok_type == 'NUM':
            # Numbers go directly to output — they need no reordering.
            output.append(token)

        elif tok_type in ('OP', 'NEG'):
            # Pop operators from the stack that should be evaluated before
            # this one. The conditions:
            #   1. Stack is not empty
            #   2. Top of stack is not a left paren (parens create scope)
            #   3. Top operator has higher precedence, OR
            #      top operator has equal precedence AND current is left-associative
            #
            # Condition 3 is where associativity matters. For left-associative
            # operators like +, equal precedence means "the one already on
            # the stack goes first" (left-to-right evaluation). For right-
            # associative operators like ^, equal precedence means "wait" —
            # the rightmost one should be evaluated first.
            while (op_stack and
                   op_stack[-1][0] != 'LPAREN' and
                   (_precedence(op_stack[-1]) > _precedence(token) or
                    (_precedence(op_stack[-1]) == _precedence(token) and _is_left_assoc(token)))):
                output.append(op_stack.pop())
            op_stack.append(token)

        elif tok_type == 'LPAREN':
            # Left paren creates a "barrier" on the stack. No operator
            # will be popped past it until the matching right paren.
            op_stack.append(token)

        elif tok_type == 'RPAREN':
            # Pop everything until we hit the matching left paren.
            # The paren pair is discarded — their job (grouping) is now
            # encoded in the postfix order.
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parentheses: extra ')'")
            op_stack.pop()  # Discard the '('

    # Pop remaining operators. If a '(' is still on the stack, there
    # was a missing ')'.
    while op_stack:
        if op_stack[-1][0] == 'LPAREN':
            raise ValueError("Mismatched parentheses: extra '('")
        output.append(op_stack.pop())

    return output


# ==========================================================================
# Step 3: Postfix Evaluation
# ==========================================================================

def evaluate_postfix(tokens):
    """Evaluate a postfix token list using a stack.

    This is beautifully simple compared to infix evaluation:
    - See a number? Push it.
    - See a binary operator? Pop two, apply, push result.
    - See unary minus? Pop one, negate, push result.

    No precedence, no parentheses, no ambiguity. This simplicity is WHY
    we converted to postfix in the first place. Stack-based VMs (JVM,
    CPython, WebAssembly) use this exact approach for expression evaluation.
    """
    stack = []

    for token in tokens:
        tok_type, tok_val = token

        if tok_type == 'NUM':
            stack.append(tok_val)

        elif tok_type == 'NEG':
            if len(stack) < 1:
                raise ValueError("Invalid expression: not enough operands for unary minus")
            stack.append(-stack.pop())

        elif tok_type == 'OP':
            if len(stack) < 2:
                raise ValueError(f"Invalid expression: not enough operands for '{tok_val}'")
            # Pop right operand first — it was pushed last.
            # Order matters for non-commutative operators (- and /).
            right = stack.pop()
            left = stack.pop()

            if tok_val == '+':
                stack.append(left + right)
            elif tok_val == '-':
                stack.append(left - right)
            elif tok_val == '*':
                stack.append(left * right)
            elif tok_val == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                stack.append(left / right)
            elif tok_val == '^':
                stack.append(left ** right)

    if len(stack) != 1:
        raise ValueError(f"Invalid expression: {len(stack)} values remain on stack")

    return stack[0]


# ==========================================================================
# Step 4: Expression Tree
# ==========================================================================

class ExprTreeNode:
    """A node in an expression tree (Abstract Syntax Tree).

    Why trees instead of just evaluating postfix directly?
    1. Trees can be TRANSFORMED (optimization, simplification).
       e.g., `x * 0` → `0`, `x + 0` → `x`
    2. Trees can generate CODE for different targets (x86, ARM, WASM).
    3. Trees can be ANALYZED (find all variables, check types).
    4. Trees separate PARSING from EVALUATION — you parse once, evaluate
       many times with different variable bindings.

    Direct postfix evaluation is evaluate-and-forget. Trees remember structure.
    """
    __slots__ = ('value', 'node_type', 'left', 'right')

    def __init__(self, value, node_type, left=None, right=None):
        self.value = value
        self.node_type = node_type  # 'NUM', 'OP', 'NEG'
        self.left = left
        self.right = right

    def __repr__(self):
        if self.node_type == 'NUM':
            return f"Num({self.value})"
        if self.node_type == 'NEG':
            return f"Neg({self.left})"
        return f"Op({self.left} {self.value} {self.right})"


def build_expression_tree(postfix_tokens):
    """Build an expression tree from postfix tokens.

    Same algorithm as postfix evaluation, but instead of computing
    numbers, we build tree nodes. When we see an operator, we pop
    child NODES (not numbers) and create a parent node.

    This is how compilers work: parse tokens into a tree, then walk
    the tree for code generation, optimization, or interpretation.
    """
    stack = []

    for token in postfix_tokens:
        tok_type, tok_val = token

        if tok_type == 'NUM':
            stack.append(ExprTreeNode(tok_val, 'NUM'))

        elif tok_type == 'NEG':
            if len(stack) < 1:
                raise ValueError("Invalid expression for tree building")
            child = stack.pop()
            # Unary minus has one child (left), no right child.
            stack.append(ExprTreeNode('~', 'NEG', left=child))

        elif tok_type == 'OP':
            if len(stack) < 2:
                raise ValueError("Invalid expression for tree building")
            right = stack.pop()
            left = stack.pop()
            stack.append(ExprTreeNode(tok_val, 'OP', left=left, right=right))

    if len(stack) != 1:
        raise ValueError("Invalid expression for tree building")

    return stack[0]


def evaluate_tree(root):
    """Recursively evaluate an expression tree.

    This is the simplest possible tree-walking interpreter. Production
    compilers do exactly this for constant folding (evaluating constant
    sub-expressions at compile time).

    The recursion mirrors the tree structure: to evaluate a node, first
    evaluate its children, then apply the operator. This is post-order
    traversal — the same order as postfix notation.
    """
    if root is None:
        raise ValueError("Cannot evaluate None node")

    if root.node_type == 'NUM':
        return root.value

    if root.node_type == 'NEG':
        return -evaluate_tree(root.left)

    # Binary operator
    left_val = evaluate_tree(root.left)
    right_val = evaluate_tree(root.right)

    if root.value == '+':
        return left_val + right_val
    elif root.value == '-':
        return left_val - right_val
    elif root.value == '*':
        return left_val * right_val
    elif root.value == '/':
        if right_val == 0:
            raise ZeroDivisionError("Division by zero")
        return left_val / right_val
    elif root.value == '^':
        return left_val ** right_val
    else:
        raise ValueError(f"Unknown operator: {root.value}")


# ==========================================================================
# Helper: full pipeline in one call
# ==========================================================================

def evaluate(expr):
    """Evaluate an infix expression string and return the numeric result.

    This is the public API. It chains the full pipeline:
      string → tokens → postfix → result
    """
    tokens = tokenize(expr)
    postfix = infix_to_postfix(tokens)
    return evaluate_postfix(postfix)


def tree_from_expr(expr):
    """Build an expression tree from an infix expression string."""
    tokens = tokenize(expr)
    postfix = infix_to_postfix(tokens)
    return build_expression_tree(postfix)


# ==========================================================================
# Helper: format postfix tokens as a readable string
# ==========================================================================

def postfix_to_string(postfix_tokens):
    """Convert postfix tokens to a readable string for display."""
    parts = []
    for tok_type, tok_val in postfix_tokens:
        if tok_type == 'NUM':
            # Show integers without decimal point for cleanliness
            parts.append(str(int(tok_val)) if tok_val == int(tok_val) else str(tok_val))
        elif tok_type == 'NEG':
            parts.append('NEG')
        else:
            parts.append(str(tok_val))
    return ' '.join(parts)


# ==========================================================================
# Demo
# ==========================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Expression Evaluation — Full Pipeline Demo")
    print("=" * 60)

    test_expressions = [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "2 ^ 3 ^ 2",
        "-3 + 4",
        "-(3 + 4) * 2",
        "10 / (5 - 3)",
        "3.5 * 2 + 1",
        "2 ^ 10",
    ]

    for expr in test_expressions:
        print(f"\nExpression: {expr}")

        # Step 1: Tokenize
        tokens = tokenize(expr)
        print(f"  Tokens:   {tokens}")

        # Step 2: Infix to Postfix
        postfix = infix_to_postfix(tokens)
        print(f"  Postfix:  {postfix_to_string(postfix)}")

        # Step 3: Evaluate Postfix
        result = evaluate_postfix(postfix)
        print(f"  Result:   {result}")

        # Step 4: Build and evaluate expression tree
        tree = build_expression_tree(postfix)
        tree_result = evaluate_tree(tree)
        print(f"  Tree:     {tree}")
        print(f"  Tree eval:{tree_result}")

        # Sanity check: both methods should agree
        assert result == tree_result, "Postfix and tree evaluation disagree!"

    print("\n" + "=" * 60)
    print("Associativity demo")
    print("=" * 60)

    # Left-associative: 8 - 3 - 2 = (8 - 3) - 2 = 3
    expr = "8 - 3 - 2"
    result = evaluate(expr)
    print(f"\n  {expr} = {result}  (left-assoc: (8-3)-2 = 3)")
    assert result == 3.0

    # Right-associative: 2 ^ 3 ^ 2 = 2 ^ (3 ^ 2) = 2 ^ 9 = 512
    expr = "2 ^ 3 ^ 2"
    result = evaluate(expr)
    print(f"  {expr} = {result}  (right-assoc: 2^(3^2) = 512)")
    assert result == 512.0

    print("\n" + "=" * 60)
    print("All assertions passed.")
    print("=" * 60)
