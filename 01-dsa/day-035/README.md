# Day 35: Calculator Language Interpreter (Mini-Project)

## Why This Exists

Every programming language, every config file parser, every SQL engine, every template system
starts with the same three-stage pipeline: **lex -> parse -> evaluate**. Understanding this
pipeline is understanding the foundation of all language implementation.

This isn't academic. When you write a regex, you're writing a mini-language that gets lexed,
parsed, and evaluated. When you use f-strings, template literals, or string interpolation --
same pipeline. When your build tool reads a config file -- same pipeline. When your ORM
translates method calls to SQL -- same pipeline.

Building a calculator interpreter from scratch teaches you:
- **How text becomes structure** (lexing: characters -> tokens)
- **How structure becomes meaning** (parsing: tokens -> AST)
- **How meaning becomes results** (evaluation: AST -> values)
- **Why error messages are hard** (position tracking through transformations)
- **Why operator precedence exists** (not syntax sugar -- it's semantics)

This is also the gateway to understanding compilers, transpilers, and code analysis tools.

## Theory

### The Pipeline: Lexer -> Parser -> Evaluator

```
Source Text          Tokens              AST                 Result
"3 + 4 * 2"  --->  [3, +, 4, *, 2]  --->  BinaryOp(+,    --->  11
                                             3,
                                             BinaryOp(*,
                                               4, 2))
```

Each stage has a single responsibility:

**Stage 1: Lexer (Tokenizer)**
- Input: raw string of characters
- Output: stream of tokens (tagged substrings)
- Responsibility: strip whitespace, classify characters, handle multi-char tokens
- Key insight: the lexer doesn't understand structure -- "3 + + 4" is fine at this stage

**Stage 2: Parser**
- Input: stream of tokens
- Output: Abstract Syntax Tree (AST)
- Responsibility: enforce grammar rules, handle precedence, detect syntax errors
- Key insight: the parser doesn't compute anything -- it builds a tree representing intent

**Stage 3: Evaluator (Interpreter)**
- Input: AST
- Output: computed values
- Responsibility: walk the tree, perform operations, manage variables
- Key insight: the evaluator doesn't parse -- it trusts the tree structure

### Why Three Stages Instead of One?

You could evaluate "3 + 4 * 2" by scanning left-to-right. But then:
- How do you handle `*` before `+`? (precedence)
- How do you handle `(3 + 4) * 2`? (grouping)
- How do you report "error at column 5"? (position tracking)
- How do you optimize `x * 0` to `0`? (transformation)
- How do you compile to machine code? (code generation)

Separation of concerns makes each problem solvable independently.

### Recursive Descent Parsing

The most intuitive parsing technique. Each grammar rule becomes a function:

```
expression  ->  term (('+' | '-') term)*
term        ->  factor (('*' | '/' | '%') factor)*
factor      ->  power
power       ->  unary ('**' power)?          # right-associative!
unary       ->  ('-' | '+') unary | primary
primary     ->  NUMBER | IDENT | '(' expression ')' | function_call
```

Each function calls the next-lower-precedence function, creating the correct tree structure
naturally. `expression()` calls `term()`, which calls `factor()`, which calls `power()`,
which calls `unary()`, which calls `primary()`.

### Precedence Climbing

Operator precedence determines tree shape:

```
3 + 4 * 2

With correct precedence (* before +):        Without:
        +                                        *
       / \                                      / \
      3   *                                    +   2
         / \                                  / \
        4   2                                3   4

Result: 11                                  Result: 14
```

Our precedence levels (low to high):
1. Assignment: `=`
2. Addition: `+`, `-`
3. Multiplication: `*`, `/`, `%`
4. Exponentiation: `**` (right-associative!)
5. Unary: `-x`, `+x`
6. Primary: numbers, variables, parenthesized expressions, function calls

### Variables and Environment

An environment is just a dictionary mapping names to values. Assignment stores,
reference looks up. This is the seed of all scope/binding systems in programming languages.

```
Environment: { "x": 5, "pi": 3.14159 }

Evaluate "x * pi":
  1. Look up "x" -> 5
  2. Look up "pi" -> 3.14159
  3. Multiply -> 15.70795
```

### The REPL Pattern

Read-Eval-Print-Loop: the fundamental interactive computing pattern since LISP in 1958.

```
while True:
    text = input("> ")        # Read
    result = evaluate(text)    # Eval
    print(result)              # Print
                               # Loop
```

Every shell, every interactive interpreter, every debugger console follows this pattern.

## What We Build Today

A complete calculator language supporting:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`
- Parentheses: `(3 + 4) * 2`
- Unary operators: `-5`, `+3`
- Variables: `x = 5`, then `x * 2`
- Built-in functions: `abs(-5)`, `min(3, 7)`, `max(1, 2)`
- Error reporting with column positions
- Interactive REPL with step-by-step demo mode

## Practice Exercises

See `practice.py` for four exercises:
1. **Comparison operators** -- extend the lexer, parser, and evaluator for `==`, `!=`, `<`, `>`, `<=`, `>=`
2. **Ternary conditional** -- implement `condition ? true_val : false_val`
3. **User-defined functions** -- `def f(x, y) = x + y`, then `f(3, 4)`
4. **AST pretty-printer** -- visual tree display command

## Checkpoint Questions

1. Why does the parser handle `**` differently from `*`? What would go wrong if exponentiation
   were left-associative like multiplication? (Hint: evaluate `2 ** 3 ** 2` both ways.)

2. The lexer produces `[MINUS, NUMBER(3)]` for input `-3`. Why not produce `[NUMBER(-3)]` instead?
   When would the difference matter? (Hint: consider `5-3` vs `5 - 3`.)

3. Our evaluator walks the AST recursively. For the expression `((((((1))))))`, how deep does
   the recursion go during parsing vs during evaluation? Why are they different?

4. If we added short-circuit evaluation for `and`/`or`, which stage of the pipeline would need
   to change? Could you implement short-circuiting in the parser? Why or why not?

5. Our environment is a flat dictionary. What would need to change to support nested scopes
   (like function-local variables that shadow globals)? Sketch the data structure.
