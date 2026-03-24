"""
Day 35: Calculator Language Interpreter

A complete interpreter demonstrating the lexer -> parser -> evaluator pipeline.
Supports arithmetic, variables, built-in functions, and a REPL.

No external libraries. Everything from scratch.
"""

from __future__ import annotations
import sys
from enum import Enum, auto
from typing import Any


# =============================================================================
# Stage 0: Token Types and Token Class
# =============================================================================

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()

    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    PERCENT = auto()     # %
    POWER = auto()       # **
    EQUALS = auto()      # =

    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,

    # Special
    EOF = auto()
    NEWLINE = auto()


class Token:
    """A tagged substring from the source text, with position info for error reporting."""

    __slots__ = ('type', 'value', 'pos', 'end_pos')

    def __init__(self, type: TokenType, value: Any, pos: int, end_pos: int):
        self.type = type
        self.value = value
        self.pos = pos          # column where this token starts (0-indexed)
        self.end_pos = end_pos  # column where this token ends

    def __repr__(self):
        if self.type == TokenType.NUMBER:
            return f"NUM({self.value})"
        if self.type == TokenType.IDENTIFIER:
            return f"ID({self.value})"
        return f"{self.type.name}"


# =============================================================================
# Stage 1: Lexer
# =============================================================================

class LexerError(Exception):
    """Error during tokenization, with position information."""

    def __init__(self, message: str, pos: int, source: str):
        self.pos = pos
        self.source = source
        super().__init__(self._format(message))

    def _format(self, message: str) -> str:
        pointer = ' ' * self.pos + '^'
        return f"{message}\n  {self.source}\n  {pointer}"


class Lexer:
    """
    Converts a string of characters into a stream of tokens.

    The lexer is deliberately simple: it doesn't understand grammar or meaning.
    It just classifies substrings. "3 + + 4" is perfectly valid token output:
    [NUM(3), PLUS, PLUS, NUM(4)]. The parser decides if that's legal.

    Why a class instead of a function? We need to maintain position state as we
    scan through the input. A generator would also work, but a class makes the
    state explicit and debuggable.
    """

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Scan the entire source and return all tokens."""
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.source[self.pos]

            # Numbers: integer or float
            # We handle this first because '.' could start a number like '.5'
            if ch.isdigit() or (ch == '.' and self._peek_next().isdigit()):
                self._read_number()

            # Identifiers and keywords: [a-zA-Z_][a-zA-Z0-9_]*
            elif ch.isalpha() or ch == '_':
                self._read_identifier()

            # Two-character operator: **
            elif ch == '*' and self._peek_next() == '*':
                self.tokens.append(Token(TokenType.POWER, '**', self.pos, self.pos + 2))
                self.pos += 2

            # Single-character operators and delimiters
            elif ch == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '*':
                self.tokens.append(Token(TokenType.STAR, '*', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '/':
                self.tokens.append(Token(TokenType.SLASH, '/', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '%':
                self.tokens.append(Token(TokenType.PERCENT, '%', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.pos, self.pos + 1))
                self.pos += 1
            elif ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.pos, self.pos + 1))
                self.pos += 1
            else:
                raise LexerError(f"Unexpected character: '{ch}'", self.pos, self.source)

        # Always end with EOF so the parser knows when to stop
        self.tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
        return self.tokens

    def _peek_next(self) -> str:
        """Look at the next character without consuming it. Returns '' at end."""
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return ''

    def _skip_whitespace(self):
        """Advance past spaces and tabs. We don't skip newlines -- they could be significant."""
        while self.pos < len(self.source) and self.source[self.pos] in ' \t':
            self.pos += 1

    def _read_number(self):
        """
        Read an integer or floating-point number.

        Why not just use float(substring)? Because we need to know exactly where
        the number ends in the source, and we need to reject things like "3.4.5".
        """
        start = self.pos
        has_dot = False

        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == '.' and not has_dot:
                has_dot = True
                self.pos += 1
            else:
                break

        text = self.source[start:self.pos]
        value = float(text) if has_dot else int(text)
        self.tokens.append(Token(TokenType.NUMBER, value, start, self.pos))

    def _read_identifier(self):
        """Read a variable name or keyword."""
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
        text = self.source[start:self.pos]
        self.tokens.append(Token(TokenType.IDENTIFIER, text, start, self.pos))


# =============================================================================
# Stage 2: AST Nodes
# =============================================================================
# The Abstract Syntax Tree is the bridge between parsing and evaluation.
# Each node type represents a different kind of computation.

class ASTNode:
    """Base class for all AST nodes. Carries position for error reporting."""
    pass


class NumberNode(ASTNode):
    """A literal number like 42 or 3.14."""
    __slots__ = ('value', 'pos')

    def __init__(self, value: float | int, pos: int):
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Num({self.value})"


class BinaryOpNode(ASTNode):
    """
    A binary operation: left op right.

    The tree structure encodes precedence. In "3 + 4 * 2":
        BinaryOp(+, Num(3), BinaryOp(*, Num(4), Num(2)))
    The * is deeper in the tree, so it gets evaluated first.
    """
    __slots__ = ('op', 'left', 'right', 'pos')

    def __init__(self, op: str, left: ASTNode, right: ASTNode, pos: int):
        self.op = op
        self.left = left
        self.right = right
        self.pos = pos

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


class UnaryOpNode(ASTNode):
    """A unary operation like -5 or +3."""
    __slots__ = ('op', 'operand', 'pos')

    def __init__(self, op: str, operand: ASTNode, pos: int):
        self.op = op
        self.operand = operand
        self.pos = pos

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class VariableNode(ASTNode):
    """A variable reference like x or counter."""
    __slots__ = ('name', 'pos')

    def __init__(self, name: str, pos: int):
        self.name = name
        self.pos = pos

    def __repr__(self):
        return f"Var({self.name})"


class AssignNode(ASTNode):
    """
    Variable assignment: name = expression.

    Assignment is an expression in our language, so "x = y = 5" works:
    it's parsed as "x = (y = 5)", and the value of an assignment is the
    assigned value. This is how C, Python, and most languages work.
    """
    __slots__ = ('name', 'expr', 'pos')

    def __init__(self, name: str, expr: ASTNode, pos: int):
        self.name = name
        self.expr = expr
        self.pos = pos

    def __repr__(self):
        return f"Assign({self.name}, {self.expr})"


class FunctionCallNode(ASTNode):
    """A function call like abs(-5) or min(3, 7)."""
    __slots__ = ('name', 'args', 'pos')

    def __init__(self, name: str, args: list[ASTNode], pos: int):
        self.name = name
        self.args = args
        self.pos = pos

    def __repr__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        return f"Call({self.name}, [{args_str}])"


# =============================================================================
# Stage 2: Parser (Recursive Descent with Precedence Climbing)
# =============================================================================

class ParseError(Exception):
    """Error during parsing, with position information."""

    def __init__(self, message: str, pos: int, source: str):
        self.pos = pos
        self.source = source
        super().__init__(self._format(message))

    def _format(self, message: str) -> str:
        pointer = ' ' * self.pos + '^'
        return f"{message}\n  {self.source}\n  {pointer}"


class Parser:
    """
    Recursive descent parser that builds an AST from a token stream.

    Grammar (from lowest to highest precedence):
        statement   -> IDENT '=' expression | expression
        expression  -> term (('+' | '-') term)*
        term        -> factor (('*' | '/' | '%') factor)*
        factor      -> power
        power       -> unary ('**' power)?        # right-associative via recursion
        unary       -> ('-' | '+') unary | primary
        primary     -> NUMBER
                     | IDENT '(' args? ')'        # function call
                     | IDENT                       # variable
                     | '(' expression ')'          # grouping

    Why recursive descent?
    - Each grammar rule is one method: easy to read, write, and debug
    - Error messages are natural: you know what you expected at each point
    - Extensible: adding new syntax means adding new methods
    - No external tools needed (unlike parser generators like yacc/bison)

    Why not a Pratt parser or precedence climbing table?
    - For a calculator this size, explicit recursion is clearer
    - The "climbing" happens naturally through the call chain:
      expression -> term -> factor -> power -> unary -> primary
      Each level "climbs" to higher precedence
    """

    def __init__(self, tokens: list[Token], source: str):
        self.tokens = tokens
        self.source = source
        self.pos = 0

    def parse(self) -> ASTNode:
        """Parse the entire token stream into an AST."""
        node = self._statement()

        if self.current().type != TokenType.EOF:
            tok = self.current()
            raise ParseError(
                f"Unexpected token: {tok}",
                tok.pos, self.source
            )
        return node

    # -- Token access helpers --

    def current(self) -> Token:
        """The token we're currently looking at."""
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        """Look ahead without consuming."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self) -> Token:
        """Consume the current token and return it."""
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type: TokenType) -> Token:
        """Consume the current token if it matches, or raise an error."""
        tok = self.current()
        if tok.type != type:
            raise ParseError(
                f"Expected {type.name}, got {tok.type.name}",
                tok.pos, self.source
            )
        return self.advance()

    def match(self, *types: TokenType) -> Token | None:
        """If current token matches any of the types, consume and return it."""
        if self.current().type in types:
            return self.advance()
        return None

    # -- Grammar rules (each method = one precedence level) --

    def _statement(self) -> ASTNode:
        """
        statement -> IDENT '=' expression | expression

        Assignment check: if we see IDENT followed by '=', it's assignment.
        Otherwise, parse as expression. This two-token lookahead is why we
        keep this separate from expression.
        """
        if (self.current().type == TokenType.IDENTIFIER and
                self.peek().type == TokenType.EQUALS):
            name_tok = self.advance()   # consume identifier
            self.advance()              # consume '='
            expr = self._expression()
            return AssignNode(name_tok.value, expr, name_tok.pos)

        return self._expression()

    def _expression(self) -> ASTNode:
        """
        expression -> term (('+' | '-') term)*

        Lowest precedence binary operators. The while loop handles chains
        like "1 + 2 - 3 + 4", building a left-associative tree:
            ((1 + 2) - 3) + 4
        """
        left = self._term()

        while True:
            op_tok = self.match(TokenType.PLUS, TokenType.MINUS)
            if not op_tok:
                break
            right = self._term()
            left = BinaryOpNode(op_tok.value, left, right, op_tok.pos)

        return left

    def _term(self) -> ASTNode:
        """
        term -> factor (('*' | '/' | '%') factor)*

        Middle precedence. Same left-associative pattern as expression.
        """
        left = self._factor()

        while True:
            op_tok = self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)
            if not op_tok:
                break
            right = self._factor()
            left = BinaryOpNode(op_tok.value, left, right, op_tok.pos)

        return left

    def _factor(self) -> ASTNode:
        """factor -> power (just a pass-through for clarity)."""
        return self._power()

    def _power(self) -> ASTNode:
        """
        power -> unary ('**' power)?

        Exponentiation is RIGHT-associative: 2 ** 3 ** 2 = 2 ** (3 ** 2) = 512
        NOT (2 ** 3) ** 2 = 64.

        We achieve right-associativity by recursing into _power() on the right
        side instead of calling the next-higher-precedence _unary(). This makes
        the right side "greedier" -- it grabs everything to its right first.
        """
        base = self._unary()

        if self.match(TokenType.POWER):
            # Recurse into _power (not _unary!) for right-associativity
            exponent = self._power()
            return BinaryOpNode('**', base, exponent, base.pos)

        return base

    def _unary(self) -> ASTNode:
        """
        unary -> ('-' | '+') unary | primary

        Unary operators bind tighter than binary operators but looser than
        primary expressions. "-3 ** 2" is "-(3 ** 2)" = -9, not "(-3) ** 2" = 9.
        Wait -- actually in our grammar, unary is BELOW power, so "-3 ** 2" is
        parsed as "-(3 ** 2)". This matches Python's behavior.
        """
        op_tok = self.match(TokenType.MINUS, TokenType.PLUS)
        if op_tok:
            operand = self._unary()  # recurse for chains like --5
            return UnaryOpNode(op_tok.value, operand, op_tok.pos)

        return self._primary()

    def _primary(self) -> ASTNode:
        """
        primary -> NUMBER
                 | IDENT '(' args? ')'    # function call
                 | IDENT                   # variable reference
                 | '(' expression ')'      # grouping

        The "bottom" of the precedence hierarchy. Everything that's not an
        operator lands here.
        """
        tok = self.current()

        # Number literal
        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(tok.value, tok.pos)

        # Identifier: could be variable or function call
        if tok.type == TokenType.IDENTIFIER:
            self.advance()

            # Function call: identifier followed by '('
            if self.current().type == TokenType.LPAREN:
                self.advance()  # consume '('
                args = self._argument_list()
                self.expect(TokenType.RPAREN)
                return FunctionCallNode(tok.value, args, tok.pos)

            # Plain variable reference
            return VariableNode(tok.value, tok.pos)

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self.advance()  # consume '('
            expr = self._expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"Unexpected token: {tok.type.name}",
            tok.pos, self.source
        )

    def _argument_list(self) -> list[ASTNode]:
        """Parse comma-separated arguments: expr (',' expr)*"""
        args = []

        if self.current().type == TokenType.RPAREN:
            return args  # empty argument list

        args.append(self._expression())
        while self.match(TokenType.COMMA):
            args.append(self._expression())

        return args


# =============================================================================
# Stage 3: Evaluator
# =============================================================================

class EvalError(Exception):
    """Error during evaluation, with position information."""

    def __init__(self, message: str, pos: int, source: str):
        self.pos = pos
        self.source = source
        super().__init__(self._format(message))

    def _format(self, message: str) -> str:
        pointer = ' ' * self.pos + '^'
        return f"{message}\n  {self.source}\n  {pointer}"


class Environment:
    """
    Variable storage. A flat dictionary for now.

    In a full language, this would be a chain of scopes (each scope pointing
    to its parent) to support local variables, closures, etc. For a calculator,
    a single global scope is sufficient.
    """

    def __init__(self):
        self.variables: dict[str, float | int] = {}
        # Pre-populate with useful constants
        self.variables['pi'] = 3.141592653589793
        self.variables['e'] = 2.718281828459045
        self.variables['tau'] = 6.283185307179586

    def get(self, name: str) -> float | int | None:
        return self.variables.get(name)

    def set(self, name: str, value: float | int):
        self.variables[name] = value

    def list_variables(self) -> dict[str, float | int]:
        return dict(self.variables)


class Evaluator:
    """
    Walks the AST and computes results.

    The evaluator uses the Visitor pattern implicitly: each node type has a
    corresponding _eval_* method. This is simpler than a formal visitor for
    our purposes, but the principle is the same -- separate the operation
    (evaluation) from the data structure (AST).

    Why not evaluate during parsing?
    - Separation of concerns: parsing is about structure, evaluation is about meaning
    - We could add optimization passes between parsing and evaluation
    - We could compile the AST to bytecode instead of interpreting it
    - Error messages can reference the original source via AST position info
    """

    # Built-in functions: name -> (function, min_args, max_args)
    BUILTINS: dict[str, tuple[callable, int, int]] = {
        'abs': (lambda args: abs(args[0]), 1, 1),
        'min': (lambda args: min(args), 1, 100),
        'max': (lambda args: max(args), 1, 100),
    }

    def __init__(self, env: Environment, source: str):
        self.env = env
        self.source = source

    def evaluate(self, node: ASTNode) -> float | int:
        """Dispatch to the appropriate evaluation method based on node type."""
        if isinstance(node, NumberNode):
            return self._eval_number(node)
        elif isinstance(node, BinaryOpNode):
            return self._eval_binary(node)
        elif isinstance(node, UnaryOpNode):
            return self._eval_unary(node)
        elif isinstance(node, VariableNode):
            return self._eval_variable(node)
        elif isinstance(node, AssignNode):
            return self._eval_assign(node)
        elif isinstance(node, FunctionCallNode):
            return self._eval_function_call(node)
        else:
            raise EvalError(f"Unknown node type: {type(node).__name__}", 0, self.source)

    def _eval_number(self, node: NumberNode) -> float | int:
        return node.value

    def _eval_binary(self, node: BinaryOpNode) -> float | int:
        """
        Evaluate a binary operation by evaluating both sides then applying the operator.

        Note: both sides are always evaluated. For short-circuit operators like 'and'/'or',
        you'd need to check the left side before evaluating the right. That's why those
        operators are fundamentally different from arithmetic operators.
        """
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            if right == 0:
                raise EvalError("Division by zero", node.pos, self.source)
            result = left / right
            # Return int if the division is exact
            if isinstance(left, int) and isinstance(right, int) and left % right == 0:
                return int(result)
            return result
        elif node.op == '%':
            if right == 0:
                raise EvalError("Modulo by zero", node.pos, self.source)
            return left % right
        elif node.op == '**':
            return left ** right
        else:
            raise EvalError(f"Unknown operator: {node.op}", node.pos, self.source)

    def _eval_unary(self, node: UnaryOpNode) -> float | int:
        operand = self.evaluate(node.operand)
        if node.op == '-':
            return -operand
        elif node.op == '+':
            return operand
        else:
            raise EvalError(f"Unknown unary operator: {node.op}", node.pos, self.source)

    def _eval_variable(self, node: VariableNode) -> float | int:
        value = self.env.get(node.name)
        if value is None:
            raise EvalError(f"Undefined variable: '{node.name}'", node.pos, self.source)
        return value

    def _eval_assign(self, node: AssignNode) -> float | int:
        """
        Evaluate the right side, store it, and return the value.
        Returning the value enables chained assignment: x = y = 5
        """
        value = self.evaluate(node.expr)
        self.env.set(node.name, value)
        return value

    def _eval_function_call(self, node: FunctionCallNode) -> float | int:
        if node.name not in self.BUILTINS:
            raise EvalError(
                f"Unknown function: '{node.name}'. Available: {', '.join(sorted(self.BUILTINS))}",
                node.pos, self.source
            )

        func, min_args, max_args = self.BUILTINS[node.name]

        if len(node.args) < min_args:
            raise EvalError(
                f"'{node.name}' requires at least {min_args} argument(s), got {len(node.args)}",
                node.pos, self.source
            )
        if len(node.args) > max_args:
            raise EvalError(
                f"'{node.name}' accepts at most {max_args} argument(s), got {len(node.args)}",
                node.pos, self.source
            )

        # Evaluate all arguments
        arg_values = [self.evaluate(arg) for arg in node.args]
        return func(arg_values)


# =============================================================================
# Interpreter: Ties the Pipeline Together
# =============================================================================

class Interpreter:
    """
    The top-level interface that runs the full pipeline: source -> tokens -> AST -> result.

    This is the only class external code needs to interact with. It manages the
    environment (variable state) across multiple expressions, which is essential
    for a REPL.
    """

    def __init__(self):
        self.env = Environment()

    def execute(self, source: str) -> float | int:
        """Run a single expression through the full pipeline."""
        # Stage 1: Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Stage 2: Parse
        parser = Parser(tokens, source)
        ast = parser.parse()

        # Stage 3: Evaluate
        evaluator = Evaluator(self.env, source)
        result = evaluator.evaluate(ast)

        return result

    def execute_verbose(self, source: str) -> tuple[list[Token], ASTNode, float | int]:
        """
        Run the pipeline and return intermediate results for demonstration.
        Returns (tokens, ast, result).
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens, source)
        ast = parser.parse()

        evaluator = Evaluator(self.env, source)
        result = evaluator.evaluate(ast)

        return tokens, ast, result


# =============================================================================
# AST Visualization (for demo mode)
# =============================================================================

def format_ast(node: ASTNode, indent: int = 0, prefix: str = "") -> str:
    """Pretty-print an AST as a tree structure."""
    lines = []
    connector = prefix

    if isinstance(node, NumberNode):
        lines.append(f"{connector}{node.value}")
    elif isinstance(node, VariableNode):
        lines.append(f"{connector}${node.name}")
    elif isinstance(node, AssignNode):
        lines.append(f"{connector}ASSIGN {node.name} =")
        child_prefix = " " * indent + "  "
        lines.append(format_ast(node.expr, indent + 2, child_prefix))
    elif isinstance(node, UnaryOpNode):
        lines.append(f"{connector}UNARY {node.op}")
        child_prefix = " " * indent + "  "
        lines.append(format_ast(node.operand, indent + 2, child_prefix))
    elif isinstance(node, BinaryOpNode):
        lines.append(f"{connector}BINARY {node.op}")
        child_prefix = " " * indent + "  L: "
        lines.append(format_ast(node.left, indent + 5, child_prefix))
        child_prefix = " " * indent + "  R: "
        lines.append(format_ast(node.right, indent + 5, child_prefix))
    elif isinstance(node, FunctionCallNode):
        lines.append(f"{connector}CALL {node.name}")
        for i, arg in enumerate(node.args):
            child_prefix = " " * indent + f"  arg{i}: "
            lines.append(format_ast(arg, indent + 7, child_prefix))

    return "\n".join(lines)


# =============================================================================
# Demo Mode: Shows the Pipeline Step by Step
# =============================================================================

def run_demo():
    """Demonstrate the interpreter pipeline with annotated examples."""
    interp = Interpreter()

    examples = [
        ("Basic arithmetic", "3 + 4 * 2"),
        ("Precedence with parens", "(3 + 4) * 2"),
        ("Exponentiation (right-associative)", "2 ** 3 ** 2"),
        ("Unary minus", "-5 + 3"),
        ("Variable assignment", "x = 10"),
        ("Using variables", "x * 2 + 1"),
        ("Chained operations", "y = x ** 2 - 3 * x + 2"),
        ("Built-in function", "abs(-42)"),
        ("Nested functions", "max(abs(-5), min(3, 7))"),
        ("Modulo", "17 % 5"),
        ("Float arithmetic", "3.14 * 2"),
        ("Complex expression", "(x + y) / abs(x - y)"),
    ]

    print("=" * 70)
    print("  CALCULATOR INTERPRETER -- PIPELINE DEMONSTRATION")
    print("=" * 70)
    print()
    print("Each expression goes through: Source -> Tokens -> AST -> Result")
    print()

    for title, expr in examples:
        print(f"--- {title} ---")
        print(f"  Source: {expr}")
        try:
            tokens, ast, result = interp.execute_verbose(expr)

            # Show tokens (skip EOF for clarity)
            token_strs = [repr(t) for t in tokens if t.type != TokenType.EOF]
            print(f"  Tokens: [{', '.join(token_strs)}]")

            # Show AST
            print(f"  AST:    {repr(ast)}")

            # Show tree
            print(f"  Tree:")
            for line in format_ast(ast, indent=10).split('\n'):
                print(f"          {line}")

            # Show result
            print(f"  Result: {result}")
        except (LexerError, ParseError, EvalError) as e:
            print(f"  Error:  {e}")
        print()

    print("=" * 70)
    print("  DEMONSTRATING ERROR REPORTING")
    print("=" * 70)
    print()

    error_examples = [
        ("Unknown character", "3 @ 4"),
        ("Missing operand", "3 +"),
        ("Unmatched paren", "(3 + 4"),
        ("Division by zero", "1 / 0"),
        ("Undefined variable", "z + 1"),
        ("Unknown function", "sqrt(4)"),
    ]

    for title, expr in error_examples:
        print(f"--- {title} ---")
        print(f"  Source: {expr}")
        try:
            result = interp.execute(expr)
            print(f"  Result: {result}")
        except (LexerError, ParseError, EvalError) as e:
            print(f"  Error:  {e}")
        print()


# =============================================================================
# REPL
# =============================================================================

def run_repl():
    """Interactive Read-Eval-Print Loop."""
    interp = Interpreter()

    print("Calculator Interpreter REPL")
    print("Type expressions to evaluate. Special commands:")
    print("  :vars    -- show all variables")
    print("  :demo    -- run demonstration")
    print("  :ast <e> -- show AST for expression")
    print("  :quit    -- exit")
    print()

    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not line:
            continue

        # Meta-commands
        if line == ':quit' or line == ':exit':
            print("Goodbye!")
            break
        elif line == ':vars':
            variables = interp.env.list_variables()
            if variables:
                max_name = max(len(n) for n in variables)
                for name, val in sorted(variables.items()):
                    print(f"  {name:<{max_name}} = {val}")
            else:
                print("  (no variables defined)")
            continue
        elif line == ':demo':
            run_demo()
            continue
        elif line.startswith(':ast '):
            expr = line[5:].strip()
            if expr:
                try:
                    tokens, ast, result = interp.execute_verbose(expr)
                    token_strs = [repr(t) for t in tokens if t.type != TokenType.EOF]
                    print(f"  Tokens: [{', '.join(token_strs)}]")
                    print(f"  AST:    {repr(ast)}")
                    print(f"  Tree:")
                    for tree_line in format_ast(ast, indent=4).split('\n'):
                        print(f"    {tree_line}")
                    print(f"  Result: {result}")
                except (LexerError, ParseError, EvalError) as e:
                    print(f"  Error: {e}")
            continue

        # Normal expression evaluation
        try:
            result = interp.execute(line)
            print(f"  = {result}")
        except (LexerError, ParseError, EvalError) as e:
            print(f"  Error: {e}")


# =============================================================================
# Tests
# =============================================================================

def run_tests():
    """Comprehensive test suite for the interpreter."""
    interp = Interpreter()
    passed = 0
    failed = 0

    def check(expr: str, expected, desc: str = ""):
        nonlocal passed, failed
        label = f"{expr}" + (f" ({desc})" if desc else "")
        try:
            result = interp.execute(expr)
            if isinstance(expected, float):
                ok = abs(result - expected) < 1e-9
            else:
                ok = result == expected
            if ok:
                passed += 1
            else:
                print(f"  FAIL: {label}")
                print(f"    expected {expected}, got {result}")
                failed += 1
        except Exception as e:
            print(f"  FAIL: {label}")
            print(f"    raised {type(e).__name__}: {e}")
            failed += 1

    def check_error(expr: str, error_type: type, desc: str = ""):
        nonlocal passed, failed
        label = f"{expr}" + (f" ({desc})" if desc else "")
        try:
            interp.execute(expr)
            print(f"  FAIL: {label}")
            print(f"    expected {error_type.__name__}, but got no error")
            failed += 1
        except error_type:
            passed += 1
        except Exception as e:
            print(f"  FAIL: {label}")
            print(f"    expected {error_type.__name__}, got {type(e).__name__}: {e}")
            failed += 1

    print("Running interpreter tests...\n")

    # Reset environment for clean test run
    interp = Interpreter()

    # -- Arithmetic --
    check("2 + 3", 5, "addition")
    check("10 - 4", 6, "subtraction")
    check("3 * 7", 21, "multiplication")
    check("20 / 4", 5, "exact division")
    check("7 / 2", 3.5, "float division")
    check("17 % 5", 2, "modulo")
    check("2 ** 10", 1024, "exponentiation")

    # -- Precedence --
    check("3 + 4 * 2", 11, "mul before add")
    check("(3 + 4) * 2", 14, "parens override")
    check("2 ** 3 ** 2", 512, "right-associative power")
    check("2 + 3 * 4 + 5", 19, "mixed precedence")
    check("10 - 2 - 3", 5, "left-associative subtraction")
    check("100 / 10 / 2", 5.0, "left-associative division")

    # -- Unary --
    check("-5", -5, "unary minus")
    check("+5", 5, "unary plus")
    check("--5", 5, "double negative")
    check("-3 + 7", 4, "unary in expression")
    check("-(3 + 4)", -7, "unary on group")

    # -- Nested parentheses --
    check("((((5))))", 5, "deeply nested parens")
    check("(2 + 3) * (4 - 1)", 15, "multiple groups")

    # -- Variables --
    check("x = 42", 42, "assignment returns value")
    check("x", 42, "variable recall")
    check("x + 8", 50, "variable in expression")
    check("y = x * 2", 84, "variable in assignment")
    check("y", 84, "second variable")

    # -- Built-in functions --
    check("abs(-10)", 10, "abs negative")
    check("abs(10)", 10, "abs positive")
    check("min(5, 3, 8, 1)", 1, "min multiple args")
    check("max(5, 3, 8, 1)", 8, "max multiple args")
    check("abs(min(-3, -7))", 7, "nested function calls")

    # -- Complex expressions --
    check("a = 3", 3)
    check("b = 4", 4)
    check("a ** 2 + b ** 2", 25, "Pythagorean")
    check("(a + b) * (a - b)", -7, "difference of squares")

    # -- Floats --
    check("3.14 * 2", 6.28, "float multiplication")
    check("0.1 + 0.2", 0.3, "float addition (approx)")

    # -- Constants --
    check("pi", 3.141592653589793, "pi constant")
    check("e", 2.718281828459045, "e constant")

    # -- Errors --
    check_error("1 / 0", EvalError, "division by zero")
    check_error("1 % 0", EvalError, "modulo by zero")
    check_error("unknown_var", EvalError, "undefined variable")
    check_error("sqrt(4)", EvalError, "unknown function")
    check_error("3 @ 4", LexerError, "bad character")
    check_error("(3 + 4", ParseError, "missing close paren")
    check_error("3 +", ParseError, "missing operand")

    print(f"\nResults: {passed} passed, {failed} failed, {passed + failed} total")
    return failed == 0


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            run_demo()
        elif sys.argv[1] == '--test':
            success = run_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--eval':
            # Evaluate a single expression from command line
            expr = ' '.join(sys.argv[2:])
            interp = Interpreter()
            try:
                result = interp.execute(expr)
                print(result)
            except (LexerError, ParseError, EvalError) as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Usage: python calculator.py [--demo | --test | --eval <expr>]")
            print("  No args: start REPL")
            print("  --demo:  run demonstration")
            print("  --test:  run test suite")
            print("  --eval:  evaluate expression")
    else:
        run_repl()
