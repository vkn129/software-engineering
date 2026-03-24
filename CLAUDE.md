# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Software Engineering Mastery

A hands-on software engineering learning lab — building real systems while mastering CS fundamentals from first principles. The goal is deep understanding of how computers work end-to-end, not framework familiarity.

## Learning Philosophy

Same first-principles approach as the ai-to-ai project:
- Understand **why** things exist before using them
- **Implement from scratch** before using libraries
- Always cover **failure modes** and what breaks
- Connect every concept to Physics, Mathematics, and Economics constraints

## Architecture

```
software-engineering/
├── 01-dsa/              # Data structures & algorithms from scratch
├── 02-systems/          # OS, networking, distributed systems
├── 03-databases/        # Storage engines, transactions, replication
├── 04-architecture/     # System design, patterns, trade-offs
├── 05-production/       # Monitoring, debugging, incident response
├── experiments/         # Quick experiments and benchmarks
└── projects/            # Real projects applying concepts
```

## Related Skills

- `/dsa-mastery` — 90-day algorithms learning path
- `/production-systems` — failure-first teaching for any systems topic
- `/first-principles` — distinguished-engineer-level depth for any CS topic
- `/math-through-code` — learn math by implementing it
- `/learn` — general systems-first learning path generator

## Tech Stack

- **Languages**: Python (algorithms), C (systems), Go (networking), TypeScript (applications)
- **No frameworks first** — standard library implementations before libraries

## Commands

```bash
# Python
python -m venv .venv && source .venv/bin/activate
python -m pytest <module>/tests/

# C
gcc -Wall -Wextra -o <name> <file>.c && ./<name>
```

## Conventions

- Each directory has its own README explaining what was learned and why
- Code comments explain the **why**, not the **what**
- Every implementation has corresponding tests
- Commit messages: `[layer] description` (e.g., `[01-dsa] implement red-black tree from scratch`)
