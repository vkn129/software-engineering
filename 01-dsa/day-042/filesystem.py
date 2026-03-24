"""
Day 42: In-Memory File System
==============================
A complete in-memory file system built on an N-ary tree.

Every Unix command maps to a tree operation:
    ls    = list children
    cd    = walk edges by name
    pwd   = trace ancestor chain to root
    find  = DFS with predicate
    mkdir = create nodes along a path
    rm -rf = postorder deletion
    du    = postorder size accumulation
    tree  = preorder display

The core insight: path resolution is tree traversal.
    /home/user/docs → root → home → user → docs
    Each step is a dict lookup: node.children[name]
"""

import copy


class FSNode:
    """
    File system node — either a file or directory.

    Directories are internal nodes (children dict maps names to FSNodes).
    Files are leaf nodes (content string, size in bytes).
    Parent pointer enables pwd (trace path back to root).
    """

    def __init__(self, name, is_dir=True):
        self.name = name
        self.is_dir = is_dir
        self.children = {}   # name → FSNode (only meaningful for directories)
        self.content = ""    # only meaningful for files
        self.size = 0        # file size in bytes (content length)
        self.parent = None   # back pointer for pwd / cd ..

    def __repr__(self):
        kind = "dir" if self.is_dir else f"file({self.size}B)"
        return f"FSNode({self.name!r}, {kind})"


class FileSystemError(Exception):
    """Base error for file system operations."""
    pass


class FileNotFoundError_(FileSystemError):
    """Path does not exist."""
    pass


class NotADirectoryError_(FileSystemError):
    """Expected a directory but got a file."""
    pass


class IsADirectoryError_(FileSystemError):
    """Expected a file but got a directory."""
    pass


class FileExistsError_(FileSystemError):
    """Path already exists."""
    pass


class FileSystem:
    """
    In-memory file system backed by an N-ary tree.

    The root node represents "/" and is always a directory.
    cwd (current working directory) tracks where we are in the tree.
    """

    def __init__(self):
        self.root = FSNode("/", is_dir=True)
        self.root.parent = self.root  # root's parent is itself (Unix convention)
        self.cwd = self.root

    # ─── Path Resolution ────────────────────────────────────────────
    # This is THE core operation. Every command calls it.
    # Handles: absolute paths, relative paths, ".", "..", trailing slashes

    def _resolve(self, path):
        """
        Resolve a path string to the FSNode it refers to.

        Absolute paths (starting with /) begin at root.
        Relative paths begin at cwd.
        "." means current node, ".." means parent.

        Raises FileNotFoundError_ if any component doesn't exist.
        Raises NotADirectoryError_ if a non-final component is a file.
        """
        if not path or path == ".":
            return self.cwd

        # Determine starting point
        if path.startswith("/"):
            current = self.root
        else:
            current = self.cwd

        # Split path into components, filtering empty strings from
        # leading /, trailing /, or double //
        parts = [p for p in path.split("/") if p]

        for i, part in enumerate(parts):
            if part == ".":
                continue
            elif part == "..":
                current = current.parent
            else:
                if not current.is_dir:
                    raise NotADirectoryError_(
                        f"'{current.name}' is not a directory"
                    )
                if part not in current.children:
                    raise FileNotFoundError_(f"No such file or directory: '{path}'")
                current = current.children[part]

        return current

    def _resolve_parent(self, path):
        """
        Resolve the parent directory of a path and return (parent_node, basename).
        Creates no nodes — just finds where the new node would go.
        """
        parts = [p for p in path.split("/") if p]
        if not parts:
            raise FileSystemError("Invalid path")

        basename = parts[-1]
        if len(parts) == 1:
            # Parent is either root (absolute) or cwd (relative)
            parent = self.root if path.startswith("/") else self.cwd
        else:
            parent_path = "/".join(parts[:-1])
            if path.startswith("/"):
                parent_path = "/" + parent_path
            parent = self._resolve(parent_path)

        if not parent.is_dir:
            raise NotADirectoryError_(f"'{parent.name}' is not a directory")

        return parent, basename

    # ─── Directory Operations ────────────────────────────────────────

    def mkdir(self, path, parents=False):
        """
        Create a directory. If parents=True, create intermediate directories
        (like mkdir -p). Otherwise, parent must already exist.
        """
        if parents:
            # mkdir -p: create each component along the path
            if path.startswith("/"):
                current = self.root
            else:
                current = self.cwd

            parts = [p for p in path.split("/") if p]
            for part in parts:
                if part == ".":
                    continue
                elif part == "..":
                    current = current.parent
                else:
                    if not current.is_dir:
                        raise NotADirectoryError_(
                            f"'{current.name}' is not a directory"
                        )
                    if part not in current.children:
                        new_dir = FSNode(part, is_dir=True)
                        new_dir.parent = current
                        current.children[part] = new_dir
                    elif not current.children[part].is_dir:
                        raise FileExistsError_(
                            f"'{part}' exists and is not a directory"
                        )
                    current = current.children[part]
            return current
        else:
            parent, basename = self._resolve_parent(path)
            if basename in parent.children:
                raise FileExistsError_(f"'{basename}' already exists")
            new_dir = FSNode(basename, is_dir=True)
            new_dir.parent = parent
            parent.children[basename] = new_dir
            return new_dir

    def touch(self, path, content=""):
        """
        Create a file (or update content if it exists).
        Parent directory must exist.
        """
        parent, basename = self._resolve_parent(path)
        if basename in parent.children:
            node = parent.children[basename]
            if node.is_dir:
                raise IsADirectoryError_(f"'{basename}' is a directory")
            node.content = content
            node.size = len(content.encode("utf-8"))
        else:
            new_file = FSNode(basename, is_dir=False)
            new_file.content = content
            new_file.size = len(content.encode("utf-8"))
            new_file.parent = parent
            parent.children[basename] = new_file
        return parent.children[basename]

    def ls(self, path="."):
        """
        List directory contents. Returns sorted list of names.
        Directories get a trailing / for clarity.
        """
        node = self._resolve(path)
        if not node.is_dir:
            return [node.name]
        return sorted(
            name + ("/" if child.is_dir else "")
            for name, child in node.children.items()
        )

    def cd(self, path):
        """Change current working directory."""
        node = self._resolve(path)
        if not node.is_dir:
            raise NotADirectoryError_(f"'{path}' is not a directory")
        self.cwd = node

    def pwd(self):
        """
        Print working directory — trace parent pointers from cwd to root.
        This is walking the ancestor chain, which gives the path.
        """
        if self.cwd is self.root:
            return "/"

        parts = []
        node = self.cwd
        while node is not self.root:
            parts.append(node.name)
            node = node.parent
        parts.reverse()
        return "/" + "/".join(parts)

    # ─── Search: DFS with Predicate ─────────────────────────────────

    def find(self, path=".", name=None, type=None):
        """
        Find files/directories matching criteria (DFS traversal).

        name: exact name to match (or None for any)
        type: 'f' for files only, 'd' for directories only, None for both

        Returns list of paths relative to the search root.
        """
        start = self._resolve(path)
        results = []

        def _dfs(node, current_path):
            # Check if this node matches the criteria
            matches = True
            if name is not None and node.name != name:
                matches = False
            if type == "f" and node.is_dir:
                matches = False
            if type == "d" and not node.is_dir:
                matches = False

            if matches:
                results.append(current_path)

            # Recurse into directory children
            if node.is_dir:
                for child_name in sorted(node.children):
                    child = node.children[child_name]
                    child_path = (
                        current_path + "/" + child_name
                        if current_path != "."
                        else child_name
                    )
                    _dfs(child, child_path)

        _dfs(start, ".")
        return results

    # ─── Deletion: Postorder Traversal ───────────────────────────────
    # rm -rf is EXACTLY postorder: you must delete children before parent.

    def rm(self, path, recursive=False):
        """
        Remove a file or directory.
        Directories require recursive=True (like rm -rf).
        Cannot remove root.
        """
        node = self._resolve(path)

        if node is self.root:
            raise FileSystemError("Cannot remove root directory")

        if node.is_dir and node.children and not recursive:
            raise FileSystemError(
                f"Directory '{node.name}' is not empty (use recursive=True)"
            )

        # Postorder deletion: children first, then parent
        # For files or empty dirs this is trivial.
        # For non-empty dirs with recursive=True, we clear children.
        if node.is_dir and recursive:
            self._rm_recursive(node)

        # If cwd was inside the deleted subtree, move to parent
        check = self.cwd
        while check is not self.root:
            if check is node:
                self.cwd = node.parent
                break
            check = check.parent

        # Remove from parent's children
        parent = node.parent
        del parent.children[node.name]

    def _rm_recursive(self, node):
        """Postorder deletion of all descendants."""
        if not node.is_dir:
            return
        # Delete children first (postorder!)
        for child_name in list(node.children.keys()):
            child = node.children[child_name]
            self._rm_recursive(child)
            del node.children[child_name]

    # ─── Disk Usage: Postorder Accumulation ──────────────────────────
    # du computes sizes bottom-up — children before parent.

    def du(self, path="."):
        """
        Compute total disk usage (recursive size in bytes).
        Uses postorder traversal: compute children sizes first,
        then sum for parent.
        """
        node = self._resolve(path)
        return self._du_recursive(node)

    def _du_recursive(self, node):
        """Postorder size accumulation."""
        if not node.is_dir:
            return node.size

        total = 0
        for child in node.children.values():
            total += self._du_recursive(child)
        return total

    # ─── Tree Display: Preorder Traversal ────────────────────────────
    # tree prints parent before children — preorder.

    def tree(self, path=".", prefix=""):
        """
        Visual tree display (like the `tree` command).
        Preorder traversal: print node, then recurse into children.
        Returns the display as a string.
        """
        node = self._resolve(path)
        lines = []
        self._tree_recursive(node, "", True, lines)
        return "\n".join(lines)

    def _tree_recursive(self, node, prefix, is_last, lines):
        """Build tree display lines with box-drawing characters."""
        # Determine the display name
        if node is self.root:
            display = "/"
        elif node.is_dir:
            display = node.name + "/"
        else:
            display = f"{node.name} ({node.size}B)"

        # Add the line
        if not prefix and node is self.root:
            lines.append(display)
        else:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + display)

        # Recurse into children
        if node.is_dir:
            children = sorted(node.children.items())
            for i, (child_name, child) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                if not prefix and node is self.root:
                    child_prefix = ""
                else:
                    extension = "    " if is_last else "│   "
                    child_prefix = prefix + extension
                self._tree_recursive(child, child_prefix, is_last_child, lines)

    # ─── File Content Operations ─────────────────────────────────────

    def cat(self, path):
        """Read file content."""
        node = self._resolve(path)
        if node.is_dir:
            raise IsADirectoryError_(f"'{path}' is a directory")
        return node.content

    def write(self, path, content):
        """Write content to a file. Creates the file if it doesn't exist."""
        try:
            node = self._resolve(path)
            if node.is_dir:
                raise IsADirectoryError_(f"'{path}' is a directory")
            node.content = content
            node.size = len(content.encode("utf-8"))
        except FileNotFoundError_:
            self.touch(path, content)

    # ─── Move and Copy ───────────────────────────────────────────────

    def mv(self, src, dst):
        """
        Move/rename a file or directory.
        If dst is an existing directory, move src into it.
        Otherwise, rename src to dst.
        """
        src_node = self._resolve(src)

        if src_node is self.root:
            raise FileSystemError("Cannot move root directory")

        # Check if dst is an existing directory → move into it
        try:
            dst_node = self._resolve(dst)
            if dst_node.is_dir:
                # Move src into dst directory
                if src_node.name in dst_node.children:
                    raise FileExistsError_(
                        f"'{src_node.name}' already exists in '{dst}'"
                    )
                # Remove from old parent
                old_parent = src_node.parent
                del old_parent.children[src_node.name]
                # Add to new parent
                dst_node.children[src_node.name] = src_node
                src_node.parent = dst_node
                return
            else:
                # dst exists and is a file — overwrite
                dst_parent = dst_node.parent
                old_parent = src_node.parent
                del old_parent.children[src_node.name]
                del dst_parent.children[dst_node.name]
                src_node.name = dst_node.name
                src_node.parent = dst_parent
                dst_parent.children[dst_node.name] = src_node
                return
        except FileNotFoundError_:
            pass

        # dst doesn't exist — rename src to dst basename in dst's parent
        dst_parent, dst_basename = self._resolve_parent(dst)
        if dst_basename in dst_parent.children:
            raise FileExistsError_(f"'{dst_basename}' already exists")

        # Remove from old parent
        old_parent = src_node.parent
        del old_parent.children[src_node.name]

        # Add to new parent with new name
        src_node.name = dst_basename
        src_node.parent = dst_parent
        dst_parent.children[dst_basename] = src_node

    def cp(self, src, dst, recursive=False):
        """
        Copy a file or directory.
        Directories require recursive=True (like cp -r).
        If dst is an existing directory, copy src into it.
        """
        src_node = self._resolve(src)

        if src_node.is_dir and not recursive:
            raise FileSystemError(
                f"'{src}' is a directory (use recursive=True)"
            )

        # Deep copy the source subtree
        cloned = self._deep_copy(src_node)

        # Determine destination
        try:
            dst_node = self._resolve(dst)
            if dst_node.is_dir:
                # Copy into directory
                if cloned.name in dst_node.children:
                    raise FileExistsError_(
                        f"'{cloned.name}' already exists in '{dst}'"
                    )
                cloned.parent = dst_node
                dst_node.children[cloned.name] = cloned
                self._fix_parents(cloned)
                return
        except FileNotFoundError_:
            pass

        # dst doesn't exist — copy with new name
        dst_parent, dst_basename = self._resolve_parent(dst)
        cloned.name = dst_basename
        cloned.parent = dst_parent
        dst_parent.children[dst_basename] = cloned
        self._fix_parents(cloned)

    def _deep_copy(self, node):
        """
        Deep copy a subtree (preorder: copy parent, then children).
        """
        new_node = FSNode(node.name, is_dir=node.is_dir)
        new_node.content = node.content
        new_node.size = node.size

        if node.is_dir:
            for child_name, child in node.children.items():
                child_copy = self._deep_copy(child)
                child_copy.parent = new_node
                new_node.children[child_name] = child_copy

        return new_node

    def _fix_parents(self, node):
        """Ensure all parent pointers in a subtree are correct."""
        if node.is_dir:
            for child in node.children.values():
                child.parent = node
                self._fix_parents(child)


# ─── Demo ────────────────────────────────────────────────────────────

def demo():
    """
    A realistic file system session demonstrating all operations.
    """
    fs = FileSystem()

    print("=" * 60)
    print("In-Memory File System Demo")
    print("=" * 60)

    # Create project structure with mkdir -p
    print("\n── Creating project structure (mkdir -p) ──")
    fs.mkdir("/home/user/projects/webapp/src", parents=True)
    fs.mkdir("/home/user/projects/webapp/tests", parents=True)
    fs.mkdir("/home/user/projects/webapp/docs", parents=True)
    fs.mkdir("/home/user/documents", parents=True)
    fs.mkdir("/tmp", parents=True)
    print(f"pwd: {fs.pwd()}")  # /

    # Create files with content
    print("\n── Creating files (touch/write) ──")
    fs.write("/home/user/projects/webapp/src/app.py",
             "from flask import Flask\napp = Flask(__name__)\n")
    fs.write("/home/user/projects/webapp/src/utils.py",
             "def helper():\n    return 42\n")
    fs.write("/home/user/projects/webapp/src/config.py",
             "DEBUG = True\nPORT = 8080\n")
    fs.write("/home/user/projects/webapp/tests/test_app.py",
             "def test_index():\n    assert True\n")
    fs.write("/home/user/projects/webapp/tests/test_utils.py",
             "def test_helper():\n    assert helper() == 42\n")
    fs.write("/home/user/projects/webapp/README.md",
             "# WebApp\nA simple web application.\n")
    fs.write("/home/user/projects/webapp/docs/api.md",
             "# API Reference\n## GET /\nReturns hello world.\n")
    fs.write("/home/user/documents/notes.txt",
             "Remember to buy groceries.\n")
    fs.write("/tmp/scratch.txt", "temporary data")

    # Navigate and list
    print("\n── Navigation (cd, pwd, ls) ──")
    fs.cd("/home/user/projects/webapp")
    print(f"pwd: {fs.pwd()}")
    print(f"ls:  {fs.ls()}")

    fs.cd("src")
    print(f"pwd: {fs.pwd()}")
    print(f"ls:  {fs.ls()}")

    fs.cd("..")
    print(f"cd ..: {fs.pwd()}")

    fs.cd("../..")
    print(f"cd ../..: {fs.pwd()}")

    # Read file content
    print("\n── Reading files (cat) ──")
    fs.cd("/home/user/projects/webapp")
    print(f"cat src/app.py:")
    print(fs.cat("src/app.py"))

    # Find files
    print("── Finding files (find with DFS) ──")
    print("All items in webapp:")
    for item in fs.find("."):
        print(f"  {item}")

    print("\nOnly files:")
    for item in fs.find(".", type="f"):
        print(f"  {item}")

    print("\nOnly directories:")
    for item in fs.find(".", type="d"):
        print(f"  {item}")

    print("\nFiles named 'test_app.py':")
    for item in fs.find(".", name="test_app.py"):
        print(f"  {item}")

    # Disk usage (postorder accumulation)
    print("\n── Disk usage (du — postorder traversal) ──")
    print(f"du src/: {fs.du('src')} bytes")
    print(f"du tests/: {fs.du('tests')} bytes")
    print(f"du .: {fs.du('.')} bytes")
    print(f"du /: {fs.du('/')} bytes")

    # Tree display (preorder traversal)
    print("\n── Tree display (preorder traversal) ──")
    print(fs.tree("."))

    print("\n── Full tree from root ──")
    print(fs.tree("/"))

    # Copy
    print("\n── Copy (cp — preorder deep copy) ──")
    fs.cp("src/app.py", "src/app_backup.py")
    print(f"ls src/: {fs.ls('src')}")

    fs.cp("src", "src_backup", recursive=True)
    print(f"ls .: {fs.ls()}")

    # Move/rename
    print("\n── Move/rename (mv) ──")
    fs.mv("src/app_backup.py", "src/app_old.py")
    print(f"ls src/: {fs.ls('src')}")

    # Disk usage after changes
    print(f"\n── Updated disk usage ──")
    print(f"du .: {fs.du('.')} bytes")

    # Remove (postorder deletion)
    print("\n── Remove (rm -rf — postorder deletion) ──")
    fs.cd("/home/user/projects/webapp")
    print(f"Before rm: {fs.ls()}")
    fs.rm("src_backup", recursive=True)
    print(f"After rm src_backup/: {fs.ls()}")

    fs.rm("src/app_old.py")
    print(f"After rm app_old.py, ls src/: {fs.ls('src')}")

    # Final tree
    print("\n── Final tree from root ──")
    print(fs.tree("/"))

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
