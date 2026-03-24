"""
Day 42 Practice: File System Tree Exercises
=============================================
Implement each function. Run this file to test your solutions.

Key insight: every file system operation is a tree operation.
    Path resolution = walking named edges from root/cwd
    find            = DFS with predicate
    du              = postorder accumulation
    tree            = preorder display
    diff            = parallel DFS comparison

These exercises build the core operations from scratch.
"""

import fnmatch


# ─── Shared Node Class ──────────────────────────────────────────────

class FSNode:
    """File system node — either a file or directory."""

    def __init__(self, name, is_dir=True):
        self.name = name
        self.is_dir = is_dir
        self.children = {}   # name → FSNode (only for directories)
        self.content = ""    # only for files
        self.size = 0        # file size in bytes
        self.parent = None   # back pointer for pwd / ..


def build_sample_tree():
    """
    Build a sample file system tree for testing:

    /
    ├── home/
    │   └── user/
    │       ├── docs/
    │       │   ├── resume.pdf  (1024B)
    │       │   └── notes.txt   (256B)
    │       ├── projects/
    │       │   ├── app.py      (512B)
    │       │   ├── test_app.py (384B)
    │       │   ├── utils.py    (128B)
    │       │   └── data/
    │       │       └── config.json (64B)
    │       └── .bashrc         (96B)
    ├── etc/
    │   └── config.yml          (48B)
    └── tmp/
        ├── scratch.py          (32B)
        └── test_tmp.py         (16B)
    """
    root = FSNode("/", is_dir=True)
    root.parent = root

    def _mknode(parent, name, is_dir=True, content="", size=0):
        node = FSNode(name, is_dir=is_dir)
        node.parent = parent
        if not is_dir:
            node.content = content
            node.size = size
        parent.children[name] = node
        return node

    home = _mknode(root, "home")
    user = _mknode(home, "user")
    docs = _mknode(user, "docs")
    _mknode(docs, "resume.pdf", is_dir=False, content="x" * 1024, size=1024)
    _mknode(docs, "notes.txt", is_dir=False, content="x" * 256, size=256)

    projects = _mknode(user, "projects")
    _mknode(projects, "app.py", is_dir=False, content="x" * 512, size=512)
    _mknode(projects, "test_app.py", is_dir=False, content="x" * 384, size=384)
    _mknode(projects, "utils.py", is_dir=False, content="x" * 128, size=128)
    data = _mknode(projects, "data")
    _mknode(data, "config.json", is_dir=False, content="x" * 64, size=64)

    _mknode(user, ".bashrc", is_dir=False, content="x" * 96, size=96)

    etc = _mknode(root, "etc")
    _mknode(etc, "config.yml", is_dir=False, content="x" * 48, size=48)

    tmp = _mknode(root, "tmp")
    _mknode(tmp, "scratch.py", is_dir=False, content="x" * 32, size=32)
    _mknode(tmp, "test_tmp.py", is_dir=False, content="x" * 16, size=16)

    return root


# ─── Exercise 1: Path Resolution ────────────────────────────────────
#
# Implement resolve(root, cwd, path) that takes:
#   - root: the root FSNode of the file system
#   - cwd: the current working directory FSNode
#   - path: a string path like "/home/user", "docs/notes.txt", "..", "."
#
# Returns the FSNode that the path refers to.
#
# Rules:
#   - Absolute paths (starting with /) begin at root
#   - Relative paths begin at cwd
#   - "." means current directory (no-op)
#   - ".." means parent directory (follow parent pointer)
#   - Ignore empty components (from // or trailing /)
#   - Raise ValueError if path component doesn't exist
#   - Raise ValueError if traversing through a file (non-directory)
#
# This is the FUNDAMENTAL operation — every other command uses it.

def resolve(root, cwd, path):
    # TODO: implement
    pass


# ─── Exercise 2: Find with Glob Matching ────────────────────────────
#
# Implement find_glob(node, pattern) that searches a subtree using
# DFS and returns paths matching a glob pattern.
#
# Use fnmatch.fnmatch(name, pattern) for matching:
#   fnmatch("app.py", "*.py")      → True
#   fnmatch("test_app.py", "test_*") → True
#   fnmatch("README.md", "*.py")   → False
#
# Returns a sorted list of paths relative to the starting node.
# Format paths as: "name" for direct children, "dir/name" for deeper.
# Include the root as "." if it matches.
#
# Example: find_glob(projects_node, "*.py")
#   → ["app.py", "test_app.py", "utils.py"]

def find_glob(node, pattern):
    # TODO: implement DFS with fnmatch predicate
    pass


# ─── Exercise 3: Disk Usage (du) ────────────────────────────────────
#
# Implement du(node) that returns a list of (path, size) tuples
# showing the cumulative size of each node in the subtree.
#
# This is POSTORDER traversal: compute children sizes first,
# then the parent's total = sum of children.
#
# File size = node.size
# Directory size = sum of all descendant file sizes
#
# Return entries in postorder (children before parent).
# Format: [("child1", 100), ("child2", 200), (".", 300)]
# Use "." for the root of the subtree.
#
# Example for projects/:
#   [("data/config.json", 64), ("data", 64),
#    ("app.py", 512), ("test_app.py", 384), ("utils.py", 128),
#    (".", 1088)]
#
# Note: children within a directory should be in sorted order.

def du(node):
    # TODO: implement postorder size accumulation
    pass


# ─── Exercise 4: Tree Display ───────────────────────────────────────
#
# Implement tree_display(node) that returns a string showing the
# tree structure with box-drawing characters, like the Unix `tree` command.
#
# Output format for the sample tree's projects/ directory:
#
#   projects/
#   ├── app.py (512B)
#   ├── data/
#   │   └── config.json (64B)
#   ├── test_app.py (384B)
#   └── utils.py (128B)
#
# Rules:
#   - Root line: "name/" for dirs, "name (sizeB)" for files
#   - Children are sorted alphabetically
#   - Use "├── " for non-last children, "└── " for last child
#   - Use "│   " to extend lines from non-last parents, "    " for last
#   - Files show: "name (sizeB)"
#   - Directories show: "name/"
#
# This is PREORDER traversal: print node, then recurse into children.

def tree_display(node):
    # TODO: implement preorder tree display
    pass


# ─── Exercise 5: Directory Diff ─────────────────────────────────────
#
# Implement diff_trees(node_a, node_b) that compares two directory
# trees and returns a list of differences.
#
# Each difference is a tuple: (change_type, path)
#   change_type is one of:
#     "only_in_a"   — exists in A but not B
#     "only_in_b"   — exists in B but not A
#     "type_mismatch" — same name but one is file, other is dir
#     "content_differs" — both are files but different content
#
# The path should be relative to the root of comparison.
# Return differences sorted by path.
#
# This is a PARALLEL DFS: walk both trees simultaneously,
# comparing at each level.
#
# Example:
#   Tree A: root/ → {a.txt("hello"), b.txt("world"), sub/ → {c.txt}}
#   Tree B: root/ → {a.txt("hello"), b.txt("WORLD"), d.txt, sub/ → {}}
#   Result: [("content_differs", "b.txt"),
#            ("only_in_b", "d.txt"),
#            ("only_in_a", "sub/c.txt")]

def diff_trees(node_a, node_b):
    # TODO: implement parallel DFS comparison
    pass


# ─── Reference Solutions ─────────────────────────────────────────────

def _sol_resolve(root, cwd, path):
    """Path resolution: the fundamental file system operation."""
    if not path or path == ".":
        return cwd

    # Absolute vs relative starting point
    current = root if path.startswith("/") else cwd

    # Split into components, filter empties
    parts = [p for p in path.split("/") if p]

    for part in parts:
        if part == ".":
            continue
        elif part == "..":
            current = current.parent
        else:
            if not current.is_dir:
                raise ValueError(f"'{current.name}' is not a directory")
            if part not in current.children:
                raise ValueError(f"'{part}' not found in '{current.name}'")
            current = current.children[part]

    return current


def _sol_find_glob(node, pattern):
    """DFS find with glob pattern matching."""
    results = []

    def _dfs(current, current_path):
        # Check if this node's name matches the pattern
        if fnmatch.fnmatch(current.name, pattern):
            results.append(current_path)

        # Recurse into directory children (sorted for deterministic order)
        if current.is_dir:
            for child_name in sorted(current.children):
                child = current.children[child_name]
                if current_path == ".":
                    child_path = child_name
                else:
                    child_path = current_path + "/" + child_name
                _dfs(child, child_path)

    _dfs(node, ".")
    return results


def _sol_du(node):
    """Postorder disk usage accumulation."""
    results = []

    def _postorder(current, current_path):
        if not current.is_dir:
            # File: size is just node.size
            results.append((current_path, current.size))
            return current.size

        # Directory: sum children sizes (postorder — children first)
        total = 0
        for child_name in sorted(current.children):
            child = current.children[child_name]
            if current_path == ".":
                child_path = child_name
            else:
                child_path = current_path + "/" + child_name
            total += _postorder(child, child_path)

        results.append((current_path, total))
        return total

    _postorder(node, ".")
    return results


def _sol_tree_display(node):
    """Preorder tree display with box-drawing characters."""
    lines = []

    # Root line
    if node.is_dir:
        lines.append(node.name + "/")
    else:
        lines.append(f"{node.name} ({node.size}B)")

    if node.is_dir:
        children = sorted(node.children.items())
        for i, (child_name, child) in enumerate(children):
            is_last = (i == len(children) - 1)
            _sol_tree_lines(child, "", is_last, lines)

    return "\n".join(lines)


def _sol_tree_lines(node, prefix, is_last, lines):
    """Helper: recursively build tree display lines."""
    connector = "└── " if is_last else "├── "
    if node.is_dir:
        lines.append(prefix + connector + node.name + "/")
    else:
        lines.append(prefix + connector + f"{node.name} ({node.size}B)")

    if node.is_dir:
        extension = "    " if is_last else "│   "
        children = sorted(node.children.items())
        for i, (child_name, child) in enumerate(children):
            child_is_last = (i == len(children) - 1)
            _sol_tree_lines(child, prefix + extension, child_is_last, lines)


def _sol_diff_trees(node_a, node_b):
    """Parallel DFS comparing two directory trees."""
    diffs = []

    def _compare(a, b, path):
        # Both should be directories at this point (or we handle files inline)
        if not a.is_dir or not b.is_dir:
            # Shouldn't reach here from the top level (handled below),
            # but safety check
            if a.is_dir != b.is_dir:
                diffs.append(("type_mismatch", path))
                return
            # Both files
            if a.content != b.content:
                diffs.append(("content_differs", path))
            return

        # Get all child names from both
        all_names = sorted(set(list(a.children.keys()) + list(b.children.keys())))

        for name in all_names:
            child_path = name if path == "." else path + "/" + name

            in_a = name in a.children
            in_b = name in b.children

            if in_a and not in_b:
                # Only in A — report this and all descendants
                _report_all(a.children[name], child_path, "only_in_a", diffs)
            elif in_b and not in_a:
                # Only in B — report this and all descendants
                _report_all(b.children[name], child_path, "only_in_b", diffs)
            else:
                # In both — check for type mismatch or recurse
                child_a = a.children[name]
                child_b = b.children[name]

                if child_a.is_dir != child_b.is_dir:
                    diffs.append(("type_mismatch", child_path))
                elif child_a.is_dir:
                    # Both directories — recurse
                    _compare(child_a, child_b, child_path)
                else:
                    # Both files — compare content
                    if child_a.content != child_b.content:
                        diffs.append(("content_differs", child_path))

    def _report_all(node, path, change_type, diffs):
        """Report a node and all its descendants as a single change type."""
        diffs.append((change_type, path))
        if node.is_dir:
            for child_name in sorted(node.children):
                child_path = path + "/" + child_name
                _report_all(node.children[child_name], child_path, change_type, diffs)

    _compare(node_a, node_b, ".")
    return sorted(diffs, key=lambda x: x[1])


# ─── Test Runner ─────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")
            failed += 1

    root = build_sample_tree()

    # ── Exercise 1: Path Resolution ──
    print("\n── Exercise 1: Path Resolution ──")
    fn1 = resolve if resolve(root, root, "/home") is not None else _sol_resolve

    # Absolute paths
    node = fn1(root, root, "/home/user")
    check("absolute /home/user", node.name, "user")

    node = fn1(root, root, "/home/user/docs/resume.pdf")
    check("absolute to file", node.name, "resume.pdf")

    node = fn1(root, root, "/")
    check("root path", node.name, "/")

    # Relative paths
    user = fn1(root, root, "/home/user")
    node = fn1(root, user, "docs")
    check("relative docs", node.name, "docs")

    node = fn1(root, user, "docs/notes.txt")
    check("relative docs/notes.txt", node.name, "notes.txt")

    # Dot and dotdot
    node = fn1(root, user, ".")
    check("dot stays", node.name, "user")

    node = fn1(root, user, "..")
    check("dotdot to home", node.name, "home")

    node = fn1(root, user, "../..")
    check("dotdot dotdot to root", node.name, "/")

    node = fn1(root, user, "docs/../projects")
    check("docs/../projects", node.name, "projects")

    # Trailing slash / double slash
    node = fn1(root, root, "/home/user/")
    check("trailing slash", node.name, "user")

    node = fn1(root, root, "/home//user")
    check("double slash", node.name, "user")

    # Error cases
    try:
        fn1(root, root, "/nonexistent")
        check("nonexistent raises", False, True)
    except ValueError:
        check("nonexistent raises ValueError", True, True)

    try:
        fn1(root, root, "/home/user/docs/resume.pdf/inside")
        check("traverse through file raises", False, True)
    except ValueError:
        check("traverse through file raises ValueError", True, True)

    # ── Exercise 2: Find with Glob ──
    print("\n── Exercise 2: Find with Glob ──")
    projects = fn1(root, root, "/home/user/projects")
    fn2 = find_glob if find_glob(projects, "*.py") is not None else _sol_find_glob

    check("*.py in projects",
          fn2(projects, "*.py"),
          ["app.py", "test_app.py", "utils.py"])

    check("test_* in projects",
          fn2(projects, "test_*"),
          ["test_app.py"])

    check("*.json in projects",
          fn2(projects, "*.json"),
          ["data/config.json"])

    check("no match",
          fn2(projects, "*.rs"),
          [])

    # Search from root for all .py files
    fn2_root = find_glob if find_glob(root, "*.py") is not None else _sol_find_glob
    all_py = fn2_root(root, "*.py")
    check("*.py from root count", len(all_py), 5)  # app.py, test_app.py, utils.py, scratch.py, test_tmp.py

    # Pattern matching directory (glob matches name, not type)
    check("data* in projects",
          fn2(projects, "data"),
          ["data"])

    # ── Exercise 3: Disk Usage (du) ──
    print("\n── Exercise 3: Disk Usage (du) ──")
    fn3 = du if du(projects) is not None else _sol_du

    du_projects = fn3(projects)
    check("du projects last entry (total)",
          du_projects[-1],
          (".", 1088))  # 512 + 384 + 128 + 64

    # Check that it's postorder (children before parent)
    paths = [entry[0] for entry in du_projects]
    dot_idx = paths.index(".")
    check("postorder: root is last", dot_idx, len(paths) - 1)

    # Check data subdirectory
    data_node = fn1(root, root, "/home/user/projects/data")
    du_data = fn3(data_node)
    check("du data/",
          du_data,
          [("config.json", 64), (".", 64)])

    # Single file
    resume = fn1(root, root, "/home/user/docs/resume.pdf")
    du_resume = fn3(resume)
    check("du single file",
          du_resume,
          [(".", 1024)])

    # ── Exercise 4: Tree Display ──
    print("\n── Exercise 4: Tree Display ──")
    fn4 = tree_display if tree_display(projects) is not None else _sol_tree_display

    tree_str = fn4(projects)
    lines = tree_str.strip().split("\n")
    check("tree root line", lines[0], "projects/")
    check("tree has correct line count", len(lines), 6)

    # Check specific lines
    check("tree first child", lines[1], "├── app.py (512B)")
    check("tree data dir", lines[2], "├── data/")
    check("tree data child", lines[3], "│   └── config.json (64B)")
    check("tree test_app", lines[4], "├── test_app.py (384B)")
    check("tree last child", lines[5], "└── utils.py (128B)")

    # Single file
    resume = fn1(root, root, "/home/user/docs/resume.pdf")
    check("tree single file", fn4(resume), "resume.pdf (1024B)")

    # Empty directory
    empty_dir = FSNode("empty", is_dir=True)
    check("tree empty dir", fn4(empty_dir), "empty/")

    # ── Exercise 5: Directory Diff ──
    print("\n── Exercise 5: Directory Diff ──")

    # Build two trees for comparison
    def build_tree_a():
        r = FSNode("root", is_dir=True)
        r.parent = r
        a = FSNode("a.txt", is_dir=False); a.content = "hello"; a.parent = r
        r.children["a.txt"] = a
        b = FSNode("b.txt", is_dir=False); b.content = "world"; b.parent = r
        r.children["b.txt"] = b
        sub = FSNode("sub", is_dir=True); sub.parent = r
        r.children["sub"] = sub
        c = FSNode("c.txt", is_dir=False); c.content = "inside"; c.parent = sub
        sub.children["c.txt"] = c
        return r

    def build_tree_b():
        r = FSNode("root", is_dir=True)
        r.parent = r
        a = FSNode("a.txt", is_dir=False); a.content = "hello"; a.parent = r
        r.children["a.txt"] = a
        b = FSNode("b.txt", is_dir=False); b.content = "WORLD"; b.parent = r  # different
        r.children["b.txt"] = b
        d = FSNode("d.txt", is_dir=False); d.content = "new"; d.parent = r  # only in B
        r.children["d.txt"] = d
        sub = FSNode("sub", is_dir=True); sub.parent = r
        r.children["sub"] = sub
        # sub is empty — c.txt missing
        return r

    tree_a = build_tree_a()
    tree_b = build_tree_b()

    fn5 = diff_trees if diff_trees(tree_a, tree_b) is not None else _sol_diff_trees

    diffs = fn5(tree_a, tree_b)
    check("diff finds content difference",
          ("content_differs", "b.txt") in diffs, True)
    check("diff finds only_in_b",
          ("only_in_b", "d.txt") in diffs, True)
    check("diff finds only_in_a",
          ("only_in_a", "sub/c.txt") in diffs, True)
    check("diff count", len(diffs), 3)

    # Identical trees
    tree_a2 = build_tree_a()
    tree_a3 = build_tree_a()
    check("identical trees no diffs", fn5(tree_a2, tree_a3), [])

    # Type mismatch: file in A, dir in B with same name
    def build_mismatch_a():
        r = FSNode("root", is_dir=True); r.parent = r
        x = FSNode("x", is_dir=False); x.content = "file"; x.parent = r
        r.children["x"] = x
        return r

    def build_mismatch_b():
        r = FSNode("root", is_dir=True); r.parent = r
        x = FSNode("x", is_dir=True); x.parent = r
        r.children["x"] = x
        return r

    check("type mismatch",
          fn5(build_mismatch_a(), build_mismatch_b()),
          [("type_mismatch", "x")])

    # ── Summary ──
    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercises need work — implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
