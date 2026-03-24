"""
Day 35 Practice: Extending the Calculator Interpreter

Four exercises that progressively extend the calculator with real language features.
Each exercise builds on calculator.py -- import and extend the existing classes.

Run: python practice.py
"""

from __future__ import annotations
import sys
import copy

# Import everything from the main calculator module
from calculator import (
    TokenType, Token, Lexer, LexerError,
    Parser, ParseError,
    ASTNode, NumberNode, BinaryOpNode, UnaryOpNode, VariableNode, AssignNode, FunctionCallNode,
    Evaluator, EvalError, Environment,
    Interpreter, format_ast,
)


# =============================================================================
# Exercise 1: Comparison Operators
# =============================================================================
# Add ==, !=, <, >, <=, >= to the calculator.
# These should have LOWER precedence than arithmetic but HIGHER than assignment.
# Return 1 for true, 0 for false (since we don't have a boolean type).
#
# Grammar change:
#   statement   -> IDENT '=' comparison | comparison
#   comparison  -> expression (('==' | '!=' | '<' | '>' | '<=' | '>=') expression)?
#   expression  -> term (('+' | '-') term)*
#   ... (rest unchanged)
#
# You need to:
# 1. Add new TokenTypes (EQ, NEQ, LT, GT, LTE, GTE)
# 2. Extend the Lexer to recognize these tokens
# 3. Add a ComparisonNode AST node (or reuse BinaryOpNode)
# 4. Add a _comparison() method to the Parser between _statement and _expression
# 5. Handle comparison ops in the Evaluator
#
# Examples:
#   3 > 2        => 1
#   5 == 5       => 1
#   3 + 1 >= 4   => 1   (arithmetic happens first, then comparison)
#   1 != 1       => 0

def exercise_1_comparison_operators():
    """
    TODO: Implement comparison operators for the calculator.

    Approach:
    - Subclass or extend Lexer, Parser, and Evaluator
    - Add new token types for ==, !=, <, >, <=, >=
    - Insert comparison precedence between assignment and addition

    Return an interpreter-like object with an .execute(source) method.
    """
    # TODO: Your implementation here
    pass


def _sol_exercise_1():
    """Solution: Comparison operators."""

    # -- Extended token types --
    # We can't easily extend an Enum, so we'll use string-based token types
    # for the new operators and patch the lexer.

    class ComparisonToken:
        EQ = 'EQ'      # ==
        NEQ = 'NEQ'    # !=
        LT = 'LT'      # <
        GT = 'GT'       # >
        LTE = 'LTE'    # <=
        GTE = 'GTE'    # >=

    COMPARISON_OPS = {ComparisonToken.EQ, ComparisonToken.NEQ,
                      ComparisonToken.LT, ComparisonToken.GT,
                      ComparisonToken.LTE, ComparisonToken.GTE}

    class ExtToken(Token):
        """Token that can also carry string-based type for extensions."""
        def __init__(self, type, value, pos, end_pos):
            # type can be a TokenType enum OR a string
            self.type = type
            self.value = value
            self.pos = pos
            self.end_pos = end_pos

        def __repr__(self):
            if isinstance(self.type, str):
                return f"{self.type}({self.value})"
            return super().__repr__()

    class ComparisonLexer(Lexer):
        """Lexer extended with comparison operators."""

        def tokenize(self):
            """Override to handle multi-character comparison operators."""
            while self.pos < len(self.source):
                self._skip_whitespace()
                if self.pos >= len(self.source):
                    break

                ch = self.source[self.pos]
                nch = self._peek_next()

                # Two-character comparisons first
                if ch == '=' and nch == '=':
                    self.tokens.append(ExtToken(ComparisonToken.EQ, '==', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '!' and nch == '=':
                    self.tokens.append(ExtToken(ComparisonToken.NEQ, '!=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<' and nch == '=':
                    self.tokens.append(ExtToken(ComparisonToken.LTE, '<=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '>' and nch == '=':
                    self.tokens.append(ExtToken(ComparisonToken.GTE, '>=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<':
                    self.tokens.append(ExtToken(ComparisonToken.LT, '<', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == '>':
                    self.tokens.append(ExtToken(ComparisonToken.GT, '>', self.pos, self.pos + 1))
                    self.pos += 1
                # Numbers
                elif ch.isdigit() or (ch == '.' and nch.isdigit()):
                    self._read_number()
                elif ch.isalpha() or ch == '_':
                    self._read_identifier()
                elif ch == '*' and nch == '*':
                    self.tokens.append(Token(TokenType.POWER, '**', self.pos, self.pos + 2))
                    self.pos += 2
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

            self.tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
            return self.tokens

    class ComparisonParser(Parser):
        """Parser extended with comparison precedence level."""

        def _statement(self):
            # The lexer already distinguishes '=' (EQUALS) from '==' (EQ),
            # so we only need to check for the EQUALS token type for assignment.
            if (self.current().type == TokenType.IDENTIFIER and
                    self.peek().type == TokenType.EQUALS):
                name_tok = self.advance()
                self.advance()  # consume '='
                expr = self._comparison()
                return AssignNode(name_tok.value, expr, name_tok.pos)

            return self._comparison()

        def _comparison(self):
            """comparison -> expression (comp_op expression)?"""
            left = self._expression()

            tok = self.current()
            if isinstance(tok.type, str) and tok.type in COMPARISON_OPS:
                op_tok = self.advance()
                right = self._expression()
                return BinaryOpNode(op_tok.value, left, right, op_tok.pos)

            return left

    class ComparisonEvaluator(Evaluator):
        """Evaluator extended with comparison operators."""

        def _eval_binary(self, node):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if node.op == '==':
                return 1 if left == right else 0
            elif node.op == '!=':
                return 1 if left != right else 0
            elif node.op == '<':
                return 1 if left < right else 0
            elif node.op == '>':
                return 1 if left > right else 0
            elif node.op == '<=':
                return 1 if left <= right else 0
            elif node.op == '>=':
                return 1 if left >= right else 0
            else:
                return super()._eval_binary(node)

    class ComparisonInterpreter:
        def __init__(self):
            self.env = Environment()

        def execute(self, source):
            lexer = ComparisonLexer(source)
            tokens = lexer.tokenize()
            parser = ComparisonParser(tokens, source)
            ast = parser.parse()
            evaluator = ComparisonEvaluator(self.env, source)
            return evaluator.evaluate(ast)

    return ComparisonInterpreter()


# =============================================================================
# Exercise 2: Ternary Conditional
# =============================================================================
# Add the ternary operator: condition ? true_expr : false_expr
#
# Grammar:
#   conditional -> comparison ('?' expression ':' expression)?
#
# Insert between statement and comparison. The condition is truthy if non-zero.
#
# You need to:
# 1. Add QUESTION and COLON token types
# 2. Extend Lexer to recognize ? and :
# 3. Add TernaryNode(condition, true_expr, false_expr) AST node
# 4. Add _conditional() parser method
# 5. Handle TernaryNode in evaluator (short-circuit: only evaluate the taken branch)
#
# Examples:
#   1 ? 10 : 20          => 10
#   0 ? 10 : 20          => 20
#   3 > 2 ? 100 : 200    => 100   (comparison first, then ternary)
#   x = 5 > 3 ? 1 : 0    => 1

def exercise_2_ternary_conditional():
    """
    TODO: Implement ternary conditional (condition ? true_val : false_val).

    Build on top of Exercise 1's comparison operators for useful conditions.
    The condition is truthy if non-zero. Only the selected branch should be evaluated
    (short-circuit evaluation).

    Return an interpreter-like object with an .execute(source) method.
    """
    # TODO: Your implementation here
    pass


def _sol_exercise_2():
    """Solution: Ternary conditional, building on comparison operators."""

    # We need the comparison infrastructure from exercise 1
    sol1 = _sol_exercise_1()

    # Access the classes from sol1's closure -- we'll rebuild extending them
    # Actually, let's build it fresh for clarity

    class TernaryToken:
        QUESTION = 'QUESTION'
        COLON = 'COLON'
        # Comparison tokens
        EQ = 'EQ'
        NEQ = 'NEQ'
        LT = 'LT'
        GT = 'GT'
        LTE = 'LTE'
        GTE = 'GTE'

    COMPARISON_OPS = {TernaryToken.EQ, TernaryToken.NEQ,
                      TernaryToken.LT, TernaryToken.GT,
                      TernaryToken.LTE, TernaryToken.GTE}

    class TernaryNode(ASTNode):
        __slots__ = ('condition', 'true_expr', 'false_expr', 'pos')

        def __init__(self, condition, true_expr, false_expr, pos):
            self.condition = condition
            self.true_expr = true_expr
            self.false_expr = false_expr
            self.pos = pos

        def __repr__(self):
            return f"Ternary({self.condition}, {self.true_expr}, {self.false_expr})"

    class TernaryLexer(Lexer):
        def tokenize(self):
            while self.pos < len(self.source):
                self._skip_whitespace()
                if self.pos >= len(self.source):
                    break

                ch = self.source[self.pos]
                nch = self._peek_next()

                if ch == '?':
                    self.tokens.append(Token(TernaryToken.QUESTION, '?', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == ':':
                    self.tokens.append(Token(TernaryToken.COLON, ':', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == '=' and nch == '=':
                    self.tokens.append(Token(TernaryToken.EQ, '==', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '!' and nch == '=':
                    self.tokens.append(Token(TernaryToken.NEQ, '!=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<' and nch == '=':
                    self.tokens.append(Token(TernaryToken.LTE, '<=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '>' and nch == '=':
                    self.tokens.append(Token(TernaryToken.GTE, '>=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<':
                    self.tokens.append(Token(TernaryToken.LT, '<', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == '>':
                    self.tokens.append(Token(TernaryToken.GT, '>', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch.isdigit() or (ch == '.' and nch.isdigit()):
                    self._read_number()
                elif ch.isalpha() or ch == '_':
                    self._read_identifier()
                elif ch == '*' and nch == '*':
                    self.tokens.append(Token(TokenType.POWER, '**', self.pos, self.pos + 2))
                    self.pos += 2
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

            self.tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
            return self.tokens

    class TernaryParser(Parser):
        def _statement(self):
            if (self.current().type == TokenType.IDENTIFIER and
                    self.peek().type == TokenType.EQUALS):
                eq_tok = self.peek()
                if isinstance(eq_tok.type, str) and eq_tok.type == TernaryToken.EQ:
                    return self._conditional()
                name_tok = self.advance()
                self.advance()
                expr = self._conditional()
                return AssignNode(name_tok.value, expr, name_tok.pos)
            return self._conditional()

        def _conditional(self):
            """conditional -> comparison ('?' expression ':' expression)?"""
            left = self._comparison()

            tok = self.current()
            if isinstance(tok.type, str) and tok.type == TernaryToken.QUESTION:
                q_tok = self.advance()  # consume '?'
                true_expr = self._expression()
                # expect ':'
                colon = self.current()
                if not (isinstance(colon.type, str) and colon.type == TernaryToken.COLON):
                    raise ParseError("Expected ':' in ternary expression", colon.pos, self.source)
                self.advance()  # consume ':'
                false_expr = self._expression()
                return TernaryNode(left, true_expr, false_expr, q_tok.pos)

            return left

        def _comparison(self):
            left = self._expression()
            tok = self.current()
            if isinstance(tok.type, str) and tok.type in COMPARISON_OPS:
                op_tok = self.advance()
                right = self._expression()
                return BinaryOpNode(op_tok.value, left, right, op_tok.pos)
            return left

    class TernaryEvaluator(Evaluator):
        def evaluate(self, node):
            if isinstance(node, TernaryNode):
                return self._eval_ternary(node)
            return super().evaluate(node)

        def _eval_ternary(self, node):
            """Short-circuit: only evaluate the branch that's taken."""
            condition = self.evaluate(node.condition)
            if condition != 0:  # truthy = non-zero
                return self.evaluate(node.true_expr)
            else:
                return self.evaluate(node.false_expr)

        def _eval_binary(self, node):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '==':
                return 1 if left == right else 0
            elif node.op == '!=':
                return 1 if left != right else 0
            elif node.op == '<':
                return 1 if left < right else 0
            elif node.op == '>':
                return 1 if left > right else 0
            elif node.op == '<=':
                return 1 if left <= right else 0
            elif node.op == '>=':
                return 1 if left >= right else 0
            return super()._eval_binary(node)

    class TernaryInterpreter:
        def __init__(self):
            self.env = Environment()

        def execute(self, source):
            lexer = TernaryLexer(source)
            tokens = lexer.tokenize()
            parser = TernaryParser(tokens, source)
            ast = parser.parse()
            evaluator = TernaryEvaluator(self.env, source)
            return evaluator.evaluate(ast)

    return TernaryInterpreter()


# =============================================================================
# Exercise 3: User-Defined Functions
# =============================================================================
# Add the ability to define and call custom functions:
#   def f(x, y) = x + y
#   f(3, 4)  => 7
#
# This requires:
# 1. New token: DEF keyword
# 2. DefNode AST: name, parameter names, body expression
# 3. FunctionValue: stored in environment, holds (params, body, closure_env)
# 4. Parser: detect "def" keyword and parse function definition
# 5. Evaluator: store function in env, call by creating new scope with args bound
#
# Key insight: when calling a user function, you create a NEW environment
# containing only the parameters, with the outer environment as parent.
# This gives you lexical scoping.
#
# Examples:
#   def square(x) = x ** 2
#   square(5)                    => 25
#   def hyp(a, b) = (a**2 + b**2) ** 0.5
#   hyp(3, 4)                   => 5.0
#   def factorial(n) = n * factorial(n - 1)   # won't work without if/else!

def exercise_3_user_defined_functions():
    """
    TODO: Implement user-defined functions.

    Syntax: def name(param1, param2) = body_expression
    Calling: name(arg1, arg2)

    Functions are stored in the environment. When called, a new scope is created
    with parameters bound to argument values, and the body is evaluated in that scope.

    Return an interpreter-like object with an .execute(source) method.
    """
    # TODO: Your implementation here
    pass


def _sol_exercise_3():
    """Solution: User-defined functions with lexical scoping."""

    class FuncToken:
        DEF = 'DEF'
        # Include comparison + ternary tokens too for full-featured interpreter
        QUESTION = 'QUESTION'
        COLON = 'COLON'
        EQ = 'EQ'
        NEQ = 'NEQ'
        LT = 'LT'
        GT = 'GT'
        LTE = 'LTE'
        GTE = 'GTE'

    COMPARISON_OPS = {FuncToken.EQ, FuncToken.NEQ,
                      FuncToken.LT, FuncToken.GT,
                      FuncToken.LTE, FuncToken.GTE}

    class TernaryNode(ASTNode):
        __slots__ = ('condition', 'true_expr', 'false_expr', 'pos')
        def __init__(self, condition, true_expr, false_expr, pos):
            self.condition = condition
            self.true_expr = true_expr
            self.false_expr = false_expr
            self.pos = pos

    class DefNode(ASTNode):
        """Function definition: def name(params) = body"""
        __slots__ = ('name', 'params', 'body', 'pos')
        def __init__(self, name, params, body, pos):
            self.name = name
            self.params = params  # list of parameter names
            self.body = body      # AST node for body expression
            self.pos = pos
        def __repr__(self):
            return f"Def({self.name}({', '.join(self.params)}) = {self.body})"

    class FunctionValue:
        """A user-defined function stored in the environment."""
        def __init__(self, name, params, body, closure_env):
            self.name = name
            self.params = params
            self.body = body
            self.closure_env = closure_env  # environment at definition time

    class ScopedEnvironment(Environment):
        """Environment with parent scope for lexical scoping."""
        def __init__(self, parent=None):
            super().__init__()
            self.parent = parent
            if parent is not None:
                # Don't re-add constants in child scopes
                self.variables = {}

        def get(self, name):
            val = self.variables.get(name)
            if val is not None:
                return val
            if self.parent is not None:
                return self.parent.get(name)
            return None

        def set(self, name, value):
            self.variables[name] = value

    class FuncLexer(Lexer):
        def _read_identifier(self):
            start = self.pos
            while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                self.pos += 1
            text = self.source[start:self.pos]
            if text == 'def':
                self.tokens.append(Token(FuncToken.DEF, 'def', start, self.pos))
            else:
                self.tokens.append(Token(TokenType.IDENTIFIER, text, start, self.pos))

        def tokenize(self):
            while self.pos < len(self.source):
                self._skip_whitespace()
                if self.pos >= len(self.source):
                    break

                ch = self.source[self.pos]
                nch = self._peek_next()

                if ch == '?':
                    self.tokens.append(Token(FuncToken.QUESTION, '?', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == ':':
                    self.tokens.append(Token(FuncToken.COLON, ':', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == '=' and nch == '=':
                    self.tokens.append(Token(FuncToken.EQ, '==', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '!' and nch == '=':
                    self.tokens.append(Token(FuncToken.NEQ, '!=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<' and nch == '=':
                    self.tokens.append(Token(FuncToken.LTE, '<=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '>' and nch == '=':
                    self.tokens.append(Token(FuncToken.GTE, '>=', self.pos, self.pos + 2))
                    self.pos += 2
                elif ch == '<':
                    self.tokens.append(Token(FuncToken.LT, '<', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch == '>':
                    self.tokens.append(Token(FuncToken.GT, '>', self.pos, self.pos + 1))
                    self.pos += 1
                elif ch.isdigit() or (ch == '.' and nch.isdigit()):
                    self._read_number()
                elif ch.isalpha() or ch == '_':
                    self._read_identifier()
                elif ch == '*' and nch == '*':
                    self.tokens.append(Token(TokenType.POWER, '**', self.pos, self.pos + 2))
                    self.pos += 2
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

            self.tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
            return self.tokens

    class FuncParser(Parser):
        def _statement(self):
            # Function definition: def name(params) = body
            tok = self.current()
            if isinstance(tok.type, str) and tok.type == FuncToken.DEF:
                return self._function_def()

            # Assignment
            if (self.current().type == TokenType.IDENTIFIER and
                    self.peek().type == TokenType.EQUALS):
                eq_tok = self.peek()
                if isinstance(eq_tok.type, str) and eq_tok.type == FuncToken.EQ:
                    return self._conditional()
                name_tok = self.advance()
                self.advance()
                expr = self._conditional()
                return AssignNode(name_tok.value, expr, name_tok.pos)

            return self._conditional()

        def _function_def(self):
            """def name(param1, param2) = body"""
            def_tok = self.advance()  # consume 'def'
            name_tok = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.LPAREN)

            params = []
            if self.current().type != TokenType.RPAREN:
                params.append(self.expect(TokenType.IDENTIFIER).value)
                while self.current().type == TokenType.COMMA:
                    self.advance()
                    params.append(self.expect(TokenType.IDENTIFIER).value)

            self.expect(TokenType.RPAREN)
            self.expect(TokenType.EQUALS)
            body = self._conditional()

            return DefNode(name_tok.value, params, body, def_tok.pos)

        def _conditional(self):
            left = self._comparison()
            tok = self.current()
            if isinstance(tok.type, str) and tok.type == FuncToken.QUESTION:
                q_tok = self.advance()
                true_expr = self._expression()
                colon = self.current()
                if not (isinstance(colon.type, str) and colon.type == FuncToken.COLON):
                    raise ParseError("Expected ':' in ternary", colon.pos, self.source)
                self.advance()
                false_expr = self._expression()
                return TernaryNode(left, true_expr, false_expr, q_tok.pos)
            return left

        def _comparison(self):
            left = self._expression()
            tok = self.current()
            if isinstance(tok.type, str) and tok.type in COMPARISON_OPS:
                op_tok = self.advance()
                right = self._expression()
                return BinaryOpNode(op_tok.value, left, right, op_tok.pos)
            return left

    class FuncEvaluator(Evaluator):
        def evaluate(self, node):
            if isinstance(node, TernaryNode):
                cond = self.evaluate(node.condition)
                return self.evaluate(node.true_expr if cond != 0 else node.false_expr)
            if isinstance(node, DefNode):
                return self._eval_def(node)
            return super().evaluate(node)

        def _eval_def(self, node):
            func = FunctionValue(node.name, node.params, node.body, self.env)
            self.env.set(node.name, func)
            return 0  # definition returns 0

        def _eval_function_call(self, node):
            # Check for user-defined function first
            func_val = self.env.get(node.name)
            if isinstance(func_val, FunctionValue):
                if len(node.args) != len(func_val.params):
                    raise EvalError(
                        f"'{node.name}' expects {len(func_val.params)} args, got {len(node.args)}",
                        node.pos, self.source
                    )
                # Evaluate arguments in current scope
                arg_values = [self.evaluate(arg) for arg in node.args]

                # Create new scope with parameters bound
                call_env = ScopedEnvironment(parent=func_val.closure_env)
                for param, val in zip(func_val.params, arg_values):
                    call_env.set(param, val)

                # Evaluate body in new scope
                body_evaluator = FuncEvaluator(call_env, self.source)
                return body_evaluator.evaluate(func_val.body)

            # Fall back to built-in functions
            return super()._eval_function_call(node)

        def _eval_binary(self, node):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '==':
                return 1 if left == right else 0
            elif node.op == '!=':
                return 1 if left != right else 0
            elif node.op == '<':
                return 1 if left < right else 0
            elif node.op == '>':
                return 1 if left > right else 0
            elif node.op == '<=':
                return 1 if left <= right else 0
            elif node.op == '>=':
                return 1 if left >= right else 0
            return super()._eval_binary(node)

    class FuncInterpreter:
        def __init__(self):
            self.env = ScopedEnvironment()
            # Re-add constants to the scoped env
            self.env.set('pi', 3.141592653589793)
            self.env.set('e', 2.718281828459045)
            self.env.set('tau', 6.283185307179586)

        def execute(self, source):
            lexer = FuncLexer(source)
            tokens = lexer.tokenize()
            parser = FuncParser(tokens, source)
            ast = parser.parse()
            evaluator = FuncEvaluator(self.env, source)
            return evaluator.evaluate(ast)

    return FuncInterpreter()


# =============================================================================
# Exercise 4: AST Pretty-Printer
# =============================================================================
# Create a function that takes an expression string and returns a visual
# tree representation of its AST.
#
# Example output for "3 + 4 * 2":
#   BinaryOp(+)
#   |-- Num(3)
#   `-- BinaryOp(*)
#       |-- Num(4)
#       `-- Num(2)
#
# Example output for "x = abs(-5) + 3":
#   Assign(x)
#   `-- BinaryOp(+)
#       |-- Call(abs)
#       |   `-- UnaryOp(-)
#       |       `-- Num(5)
#       `-- Num(3)
#
# You need to:
# 1. Write a recursive function that walks the AST
# 2. Track indentation and whether each node is the last child
# 3. Use box-drawing characters for the tree lines
# 4. Handle all node types

def exercise_4_ast_pretty_printer(source: str) -> str:
    """
    TODO: Parse the given expression and return a pretty-printed AST string.

    Use these box-drawing prefixes:
    - "|-- " for non-last children
    - "`-- " for last children
    - "|   " for continuation lines under non-last children
    - "    " for continuation lines under last children

    The root node should have no prefix.

    Return the tree as a multi-line string.
    """
    # TODO: Your implementation here
    pass


def _sol_exercise_4(source: str) -> str:
    """Solution: AST pretty-printer with box-drawing characters."""

    # Parse the expression
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source)
    ast = parser.parse()

    def _print_node(node: ASTNode, prefix: str = "", is_last: bool = True, is_root: bool = True) -> list[str]:
        """Recursively build tree lines."""
        lines = []

        # Determine the connector for this node
        if is_root:
            connector = ""
        elif is_last:
            connector = "`-- "
        else:
            connector = "|-- "

        # Determine the prefix for children of this node
        if is_root:
            child_prefix = ""
        elif is_last:
            child_prefix = prefix + "    "
        else:
            child_prefix = prefix + "|   "

        if isinstance(node, NumberNode):
            lines.append(f"{prefix}{connector}Num({node.value})")

        elif isinstance(node, VariableNode):
            lines.append(f"{prefix}{connector}Var({node.name})")

        elif isinstance(node, UnaryOpNode):
            lines.append(f"{prefix}{connector}UnaryOp({node.op})")
            lines.extend(_print_node(node.operand, child_prefix, is_last=True, is_root=False))

        elif isinstance(node, BinaryOpNode):
            lines.append(f"{prefix}{connector}BinaryOp({node.op})")
            lines.extend(_print_node(node.left, child_prefix, is_last=False, is_root=False))
            lines.extend(_print_node(node.right, child_prefix, is_last=True, is_root=False))

        elif isinstance(node, AssignNode):
            lines.append(f"{prefix}{connector}Assign({node.name})")
            lines.extend(_print_node(node.expr, child_prefix, is_last=True, is_root=False))

        elif isinstance(node, FunctionCallNode):
            lines.append(f"{prefix}{connector}Call({node.name})")
            for i, arg in enumerate(node.args):
                is_last_arg = (i == len(node.args) - 1)
                lines.extend(_print_node(arg, child_prefix, is_last=is_last_arg, is_root=False))

        return lines

    return "\n".join(_print_node(ast))


# =============================================================================
# Test Runner
# =============================================================================

def run_tests():
    """Test all exercises."""
    passed = 0
    failed = 0

    def check(actual, expected, desc):
        nonlocal passed, failed
        if isinstance(expected, float):
            ok = actual is not None and abs(actual - expected) < 1e-9
        else:
            ok = actual == expected
        if ok:
            passed += 1
        else:
            print(f"  FAIL: {desc}")
            print(f"    expected: {expected}")
            print(f"    got:      {actual}")
            failed += 1

    # ---- Exercise 1: Comparison Operators ----
    print("Exercise 1: Comparison Operators")
    print("-" * 40)

    interp1 = _sol_exercise_1()
    check(interp1.execute("3 > 2"), 1, "3 > 2")
    check(interp1.execute("2 > 3"), 0, "2 > 3")
    check(interp1.execute("5 == 5"), 1, "5 == 5")
    check(interp1.execute("5 == 6"), 0, "5 == 6")
    check(interp1.execute("3 != 4"), 1, "3 != 4")
    check(interp1.execute("3 != 3"), 0, "3 != 3")
    check(interp1.execute("3 + 1 >= 4"), 1, "3 + 1 >= 4 (precedence)")
    check(interp1.execute("2 * 3 < 7"), 1, "2 * 3 < 7 (precedence)")
    check(interp1.execute("10 <= 10"), 1, "10 <= 10")
    check(interp1.execute("10 <= 9"), 0, "10 <= 9")
    print()

    # ---- Exercise 2: Ternary Conditional ----
    print("Exercise 2: Ternary Conditional")
    print("-" * 40)

    interp2 = _sol_exercise_2()
    check(interp2.execute("1 ? 10 : 20"), 10, "truthy ternary")
    check(interp2.execute("0 ? 10 : 20"), 20, "falsy ternary")
    check(interp2.execute("3 > 2 ? 100 : 200"), 100, "comparison + ternary")
    check(interp2.execute("1 == 2 ? 100 : 200"), 200, "false comparison + ternary")
    check(interp2.execute("x = 5 > 3 ? 1 : 0"), 1, "assignment + ternary")
    check(interp2.execute("x"), 1, "assigned value persists")
    print()

    # ---- Exercise 3: User-Defined Functions ----
    print("Exercise 3: User-Defined Functions")
    print("-" * 40)

    interp3 = _sol_exercise_3()
    interp3.execute("def square(x) = x ** 2")
    check(interp3.execute("square(5)"), 25, "square(5)")
    check(interp3.execute("square(3)"), 9, "square(3)")

    interp3.execute("def add(a, b) = a + b")
    check(interp3.execute("add(10, 20)"), 30, "add(10, 20)")

    interp3.execute("def hyp(a, b) = (a**2 + b**2) ** 0.5")
    check(interp3.execute("hyp(3, 4)"), 5.0, "hyp(3, 4)")

    # Verify scoping: function params don't leak
    interp3.execute("g = 100")
    interp3.execute("def f(x) = x + g")
    check(interp3.execute("f(5)"), 105, "function reads global")

    # Nested function calls
    check(interp3.execute("square(add(2, 3))"), 25, "nested user functions")

    # Ternary inside function (conditional dispatch)
    interp3.execute("def myabs(x) = x >= 0 ? x : 0 - x")
    check(interp3.execute("myabs(5)"), 5, "myabs(5)")
    check(interp3.execute("myabs(-5)"), 5, "myabs(-5)")
    print()

    # ---- Exercise 4: AST Pretty-Printer ----
    print("Exercise 4: AST Pretty-Printer")
    print("-" * 40)

    tree1 = _sol_exercise_4("3 + 4 * 2")
    expected1 = (
        "BinaryOp(+)\n"
        "|-- Num(3)\n"
        "`-- BinaryOp(*)\n"
        "    |-- Num(4)\n"
        "    `-- Num(2)"
    )
    check(tree1, expected1, "3 + 4 * 2 tree")

    tree2 = _sol_exercise_4("-5")
    expected2 = (
        "UnaryOp(-)\n"
        "`-- Num(5)"
    )
    check(tree2, expected2, "-5 tree")

    tree3 = _sol_exercise_4("x = 3 + 4")
    expected3 = (
        "Assign(x)\n"
        "`-- BinaryOp(+)\n"
        "    |-- Num(3)\n"
        "    `-- Num(4)"
    )
    check(tree3, expected3, "x = 3 + 4 tree")

    tree4 = _sol_exercise_4("abs(-5)")
    expected4 = (
        "Call(abs)\n"
        "`-- UnaryOp(-)\n"
        "    `-- Num(5)"
    )
    check(tree4, expected4, "abs(-5) tree")

    tree5 = _sol_exercise_4("min(3, 7)")
    expected5 = (
        "Call(min)\n"
        "|-- Num(3)\n"
        "`-- Num(7)"
    )
    check(tree5, expected5, "min(3, 7) tree")

    # Print a sample tree for visual verification
    print()
    print("  Sample tree for '(a + b) * abs(-c)':")
    sample = _sol_exercise_4("(a + b) * abs(-c)")  # won't error during parse
    for line in sample.split('\n'):
        print(f"    {line}")
    print()

    # ---- Summary ----
    print("=" * 40)
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    return failed == 0


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
