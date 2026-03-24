# Day 34: Expression Evaluation

## Why This Exists

Every time you type `2 + 3 * 4` into a calculator, a programming language, or a SQL query, something must figure out that multiplication happens before addition. That "something" is an expression evaluator, and it sits at the heart of:

1. **Compilers and interpreters.** Every programming language parses source code into an Abstract Syntax Tree (AST). The expression `a + b * c` becomes a tree where `*` is evaluated before `+`, not because of magic, but because the parser was built with precedence rules. If you understand expression evaluation, you understand the core of how compilers work.

2. **Calculators and spreadsheets.** Excel, Google Sheets, Wolfram Alpha — they all tokenize your input, respect operator precedence, handle parentheses, and evaluate. The algorithm you will implement today (shunting-yard) is exactly what these tools use internally.

3. **SQL parsers and query planners.** A SQL `WHERE` clause like `price > 100 AND category = 'books' OR stock < 10` is an expression. The database must parse it into a tree, respecting `AND`/`OR` precedence, then evaluate it against every row. Same algorithm, different operators.

4. **Configuration languages and DSLs.** Prometheus queries, Grafana alert rules, Terraform expressions — any domain-specific language that allows arithmetic or logic needs expression evaluation.

The deeper lesson: **notation is a design choice with trade-offs.** Infix notation (`2 + 3`) is human-friendly but ambiguous without precedence rules and parentheses. Postfix notation (`2 3 +`) is unambiguous and trivial to evaluate with a stack. The shunting-yard algorithm is the bridge between the two — it converts human-friendly infix into machine-friendly postfix. Understanding this bridge teaches you how all parsing works.

## Theory

### Three Notations for the Same Expression

Consider `3 + 4 * 2`. There are three ways to write it:

| Notation | Expression | How Operator Relates to Operands |
|----------|-----------|----------------------------------|
| **Infix** | `3 + 4 * 2` | Operator sits **between** operands |
| **Prefix** (Polish) | `+ 3 * 4 2` | Operator comes **before** operands |
| **Postfix** (Reverse Polish) | `3 4 2 * +` | Operator comes **after** operands |

All three represent the same computation: multiply 4 by 2, then add 3. The result is 11.

**Why postfix matters:** Postfix requires no parentheses and no precedence rules. You evaluate it left-to-right with a single stack. This is why HP calculators used Reverse Polish Notation — it is mechanically simpler. Stack-based virtual machines (JVM bytecode, Python bytecode, WebAssembly) use postfix for the same reason.

**Why prefix matters:** Prefix notation is what Lisp uses: `(+ 3 (* 4 2))`. It maps directly to function calls and is trivial to parse recursively. It is also how expression trees are traversed in pre-order.

### Operator Precedence and Associativity

Precedence answers: "Which operator binds tighter?"

```
3 + 4 * 2
```

`*` has higher precedence than `+`, so `4 * 2` is computed first. Without precedence rules, the expression is ambiguous — it could mean `(3 + 4) * 2 = 14` or `3 + (4 * 2) = 11`.

Standard precedence (low to high):

| Precedence | Operators | Meaning |
|-----------|-----------|---------|
| 1 | `+`, `-` | Addition, subtraction |
| 2 | `*`, `/` | Multiplication, division |
| 3 | `^` | Exponentiation |
| 4 | unary `-` | Negation |

**Associativity** answers: "When two operators have the same precedence, which one goes first?"

- **Left-associative** (`+`, `-`, `*`, `/`): `8 - 3 - 2` means `(8 - 3) - 2 = 3`, not `8 - (3 - 2) = 7`
- **Right-associative** (`^`): `2 ^ 3 ^ 2` means `2 ^ (3 ^ 2) = 512`, not `(2 ^ 3) ^ 2 = 64`

Getting associativity wrong produces subtle bugs. This is why the shunting-yard algorithm explicitly checks associativity when comparing operators.

### The Shunting-Yard Algorithm

Invented by Edsger Dijkstra (yes, the same Dijkstra as the shortest-path algorithm). It converts infix to postfix using two structures:

- An **output queue** (the postfix result)
- An **operator stack** (temporary holding area)

The algorithm processes tokens left to right:

```
For each token:
  If NUMBER:  push to output
  If OPERATOR (op1):
      While there is an operator op2 on the stack AND
            (op2 has greater precedence than op1, OR
             op2 has equal precedence and op1 is left-associative)
        AND op2 is not '(':
          Pop op2 to output
      Push op1 to stack
  If '(':  push to stack
  If ')':
      While top of stack is not '(':
          Pop to output
      Pop '(' from stack (discard it)

After all tokens: pop remaining operators to output
```

**Why it works:** The operator stack acts as a "waiting area." An operator waits on the stack until it knows whether the next operator has higher precedence. If the next operator is weaker or equal (with left-associativity), the waiting operator can safely go to the output because it will be evaluated first. This is the same logic a human uses when reading `3 + 4 * 2` — you "hold" the `+` in your mind and evaluate `4 * 2` first.

The name "shunting-yard" comes from a railroad switchyard where train cars are rearranged — operators are "shunted" between the stack and output.

### Expression Trees (AST)

An expression tree makes the structure explicit:

```
        +
       / \
      3    *
          / \
         4   2
```

- **Leaf nodes** are operands (numbers, variables)
- **Internal nodes** are operators
- **Children** of an operator node are its operands
- **In-order traversal** gives infix: `3 + 4 * 2`
- **Pre-order traversal** gives prefix: `+ 3 * 4 2`
- **Post-order traversal** gives postfix: `3 4 2 * +`

Building a tree from postfix is straightforward: use a stack of nodes instead of a stack of numbers. When you see an operator, pop two node children, create a parent node, push it back.

**Evaluating a tree** is recursive: if the node is a number, return it. If it is an operator, recursively evaluate the children and apply the operator. This recursive structure is why compilers love trees — code generation is a recursive walk over the AST.

### Unary Minus

Unary minus (negation) is tricky because `-` can mean two things:
- `3 - 2` (binary subtraction)
- `-3 + 2` (unary negation)

The distinction depends on context. A `-` is unary when it appears:
- At the start of the expression
- After an opening parenthesis `(`
- After another operator

The standard approach: during tokenization, detect unary minus and replace it with a distinct token (e.g., `NEG` or `~`) that has higher precedence than binary operators and is right-associative.

## Practice

Work through `expression_eval.py` to understand the full pipeline:
1. Tokenization — converting a string into a list of tokens
2. Infix to postfix — shunting-yard algorithm
3. Postfix evaluation — stack-based computation
4. Expression tree — building and evaluating an AST

Then complete the exercises in `practice.py`:
1. Basic calculator (+ - and parentheses only)
2. Evaluate expressions with variables
3. Convert infix to prefix notation
4. Pretty-print an expression tree
5. Extend the evaluator with function calls (sin, sqrt)

## Checkpoint Questions

1. Why does postfix notation not need parentheses? What property makes it unambiguous?
2. Walk through the shunting-yard algorithm on `3 + 4 * 2 ^ 5` — show the state of the output queue and operator stack after each token.
3. Why is `^` right-associative while `*` is left-associative? What real-world math convention does this reflect?
4. Given the postfix `5 3 + 8 2 - *`, draw the expression tree and evaluate it.
5. How would you extend the shunting-yard algorithm to handle function calls like `sin(x + 1)`? What changes to the token types and stack logic are needed?
6. Why do compilers build expression trees instead of directly evaluating expressions? What can a tree do that direct evaluation cannot?
