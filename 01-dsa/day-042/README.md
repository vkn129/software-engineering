# Day 42: Mini-Project — In-Memory File System

## Week 6 Capstone: Trees Meet the Real World

This is where all the binary tree concepts from Days 36-41 come together. We build a practical system that every programmer uses daily: a **file system**. The twist: once you understand trees, you already understand file systems.

## Why File Systems Are Trees

Every file system is a tree. Not a binary tree — an **N-ary tree** where each node (directory) can have any number of children, and edges have **names** (the file/directory names).

```
/                          ← root node
├── home/                  ← child of root, named "home"
│   ├── user/              ← child of home, named "user"
│   │   ├── docs/          ← directory node (children = {})
│   │   │   ├── resume.pdf ← leaf node (file)
│   │   │   └── notes.txt  ← leaf node (file)
│   │   └── .bashrc        ← leaf node (file)
│   └── guest/
└── etc/
    └── config.yml
```

The forcing function: **hierarchy requires trees**. You can't represent `/home/user/docs/resume.pdf` in a flat list without encoding the parent-child relationships — which is just reinventing a tree with extra steps.

### Why N-ary, Not Binary?

Binary trees restrict each node to two children. Directories have arbitrary numbers of entries. The data structure shifts from:

```python
# Binary tree
class Node:
    left: Node
    right: Node

# N-ary tree (file system)
class FSNode:
    children: dict[str, FSNode]  # name → child node
```

The `dict` is critical — it gives O(1) child lookup by name, which is exactly what path resolution needs.

## Unix Inodes: The Real Implementation

In a real Unix file system, the tree structure works through **inodes** (index nodes):

| Concept | What It Is | Tree Analogy |
|---------|-----------|--------------|
| **Inode** | Metadata block (permissions, size, timestamps, data pointers) | Tree node |
| **Directory entry** | A (name, inode_number) pair | Named edge |
| **Directory** | A file whose content is a list of directory entries | Internal node |
| **Regular file** | A file whose content is actual data | Leaf node |

A directory is literally a lookup table: `name → inode`. When you type `ls /home/user`, the kernel:
1. Reads the root directory's inode (always inode 2)
2. Scans root's entries for "home" → gets inode 47
3. Reads inode 47's entries for "user" → gets inode 103
4. Lists inode 103's entries

This is **tree traversal along a path** — the same operation as walking from root to a specific node.

## Every Unix Command Is a Tree Operation

| Command | Tree Operation | Traversal Type |
|---------|---------------|----------------|
| `ls` | List children of current node | Direct children |
| `cd path` | Walk tree edges by name | Path traversal |
| `pwd` | Trace ancestor chain to root | Root-to-node path |
| `find` | DFS with predicate filtering | Full DFS |
| `mkdir -p` | Create nodes along a path, adding intermediates | Path creation |
| `rm -rf` | Delete subtree, children before parent | **Postorder** (exactly!) |
| `du` | Sum sizes bottom-up | **Postorder accumulation** |
| `tree` | Display full subtree structure | **Preorder** (parent before children) |
| `cp -r` | Deep copy a subtree | **Preorder** (create parent, then children) |

### rm -rf Is Postorder Traversal

This is the key insight. You **cannot** delete a directory before its contents:

```
rm -rf projects/
  1. rm projects/src/main.py     ← leaf
  2. rm projects/src/utils.py    ← leaf
  3. rm projects/src/            ← now empty, can delete
  4. rm projects/README.md       ← leaf
  5. rm projects/                ← now empty, can delete
```

Children before parent = **postorder**. This is exactly why postorder exists as a traversal order.

### du Is Postorder Accumulation

```
du projects/
  projects/src/main.py    4K    ← leaf size
  projects/src/utils.py   2K    ← leaf size
  projects/src/            6K    ← sum of children
  projects/README.md      1K    ← leaf size
  projects/                7K    ← sum of children
```

You compute a directory's size by summing its children's sizes — which requires computing children first. Postorder again.

## Path Resolution: The Core Algorithm

Resolving `/home/user/docs` to the actual node is the fundamental operation. Every command calls it.

```
resolve("/home/user/docs")
  1. Start at root (because path starts with /)
  2. Split: ["home", "user", "docs"]
  3. root.children["home"]  → home_node
  4. home_node.children["user"] → user_node
  5. user_node.children["docs"] → docs_node
  6. Return docs_node
```

Edge cases that make it interesting:
- **Absolute path** (`/home/user`): start at root
- **Relative path** (`docs/notes.txt`): start at current working directory
- **`.`** (current directory): no-op in path
- **`..`** (parent directory): follow parent pointer
- **Trailing slashes**: `/home/user/` same as `/home/user`
- **Nonexistent path**: raise appropriate error

## Complexity Analysis

| Operation | Time Complexity | Why |
|-----------|----------------|-----|
| `_resolve(path)` | O(d) where d = path depth | Walk d edges, each O(1) dict lookup |
| `ls` | O(k) where k = number of children | List dict keys |
| `find` | O(n) where n = total nodes in subtree | Must visit every node |
| `mkdir -p` | O(d) | Create up to d nodes |
| `rm -rf` | O(n) | Must visit and delete every node in subtree |
| `du` | O(n) | Must visit every node to sum sizes |
| `pwd` | O(d) | Walk parent pointers to root |

## What This Project Synthesizes

| Concept from Days 36-41 | Where It Appears Here |
|--------------------------|----------------------|
| Tree traversal (DFS) | `find`, `rm -rf`, `du`, `tree` |
| Preorder traversal | `tree` display, `cp -r` |
| Postorder traversal | `rm -rf`, `du` |
| Parent pointers | `pwd`, `cd ..` |
| Path from root to node | `pwd`, path resolution |
| N-ary tree generalization | Every node has `dict` of children |
| Recursive structure | Every operation decomposes recursively |

## Files

- **`filesystem.py`** — Complete in-memory file system implementation with all commands
- **`practice.py`** — 5 exercises: path resolution, glob find, du, tree display, directory diff

## Running

```bash
# Run the interactive demo
python3 filesystem.py

# Run practice exercises (tests against reference solutions)
python3 practice.py
```
