"""
practice.py — Day 8: File Systems exercises.

Five exercises. Complete each TODO before reading the solution below it.
Run the file to see solutions execute: python practice.py
"""

from fs_sim import (FileSystem, ROOT_INUM, BLOCK_SIZE, N_DIRECT,
                    PTRS_PER_BLK, PTR_SIZE, TYPE_LINK,
                    _pack_dirent, _encode_name)
import struct

DIVIDER = "-" * 60


# ============================================================
# Exercise 1: Symbolic links
# ============================================================
# A symbolic link is an inode of type TYPE_LINK whose data
# contains the target path string (not a block pointer).
# Implement symlink(fs, parent_inum, name, target_path) and
# readlink(fs, inum) -> str.
# Then demonstrate that after unlinking the target the symlink
# becomes dangling (resolve raises FileNotFoundError).
# ============================================================

print(DIVIDER)
print("Exercise 1: Symbolic links")
print(DIVIDER)

# TODO: implement symlink() and readlink() and show dangling-link behaviour


# --- Solution 1 ---

def symlink(fs: FileSystem, parent_inum: int, name: str, target: str) -> int:
    """
    Create a symbolic link named `name` in `parent_inum` pointing at `target`.
    The link target is stored as UTF-8 bytes in the inode's data blocks —
    exactly like a regular file, but with type=TYPE_LINK.
    """
    inum = fs._alloc_inode(TYPE_LINK)
    fs.write(inum, target.encode("utf-8"))
    fs._dir_add_entry(parent_inum, inum, name)
    return inum


def readlink(fs: FileSystem, inum: int) -> str:
    """Return the target string stored in a symlink inode."""
    inode = fs.inodes[inum]
    if inode.type != TYPE_LINK:
        raise OSError(f"Inode {inum} is not a symlink")
    return fs.read_raw(inode).decode("utf-8")


def resolve_symlink(fs: FileSystem, path: str, max_hops: int = 8) -> int:
    """
    Like fs.resolve() but follows symlinks (up to max_hops to detect loops).
    A real kernel uses MAXSYMLINKS=40 and returns ELOOP when exceeded.
    """
    for _ in range(max_hops):
        inum = fs.resolve(path)
        inode = fs.inodes[inum]
        if inode.type != TYPE_LINK:
            return inum
        target = readlink(fs, inum)
        # Relative target: treat as relative to the symlink's parent directory
        if not target.startswith("/"):
            parent = "/".join(path.split("/")[:-1]) or "/"
            target = parent.rstrip("/") + "/" + target
        path = target
    raise OSError(f"Too many levels of symbolic links (possible loop)")


fs1 = FileSystem()
fs1.mkfs()

target_inum = fs1.create(ROOT_INUM, "real.txt")
fs1.write(target_inum, b"I am the real file")

link_inum = symlink(fs1, ROOT_INUM, "alias.lnk", "/real.txt")
print(f"symlink /alias.lnk -> /real.txt  (link inum={link_inum})")
print(f"readlink: {readlink(fs1, link_inum)!r}")

resolved = resolve_symlink(fs1, "/alias.lnk")
print(f"Resolved /alias.lnk to inum={resolved}, content={fs1.read(resolved)!r}")

# Create dangling link
fs1.unlink(ROOT_INUM, "real.txt")
print("Unlinked /real.txt...")
try:
    resolve_symlink(fs1, "/alias.lnk")
    print("  ERROR: should have raised FileNotFoundError")
except FileNotFoundError as e:
    print(f"  Dangling link correctly raises FileNotFoundError: {e}")

print()


# ============================================================
# Exercise 2: Max file size calculation
# ============================================================
# Given:
#   block_size B, pointer_size P (bytes), n_direct direct pointers,
#   plus 1 single-indirect, 1 double-indirect, 1 triple-indirect.
# Compute the maximum file size in bytes.
# Then verify with our simulation's parameters (no triple-indirect).
# ============================================================

print(DIVIDER)
print("Exercise 2: Maximum file size calculation")
print(DIVIDER)

# TODO: write max_file_size(B, P, n_direct, levels) where levels is the
# number of indirection levels (1=single, 2=double, 3=triple).


# --- Solution 2 ---

def max_file_size(B: int, P: int, n_direct: int, indirect_levels: int) -> int:
    """
    Compute maximum file size in bytes.

    ptrs_per_blk = B // P
    direct_bytes = n_direct * B
    single_indirect = ptrs_per_blk^1 * B
    double_indirect = ptrs_per_blk^2 * B
    triple_indirect = ptrs_per_blk^3 * B
    """
    ptrs = B // P
    total = n_direct * B
    for level in range(1, indirect_levels + 1):
        total += (ptrs ** level) * B
    return total


# Real ext2/ext3 with 4 KB blocks, 4-byte pointers, 12 direct, 3 levels
B_ext2 = 4096
P_ext2 = 4
ext2_max = max_file_size(B_ext2, P_ext2, 12, 3)
print(f"ext2/ext3 (4 KB blocks, 3-level indirect, 12 direct):")
print(f"  Max file size = {ext2_max:,} bytes = {ext2_max / (1024**3):.1f} GB")

# Our simulation: 64-byte blocks, 4-byte pointers, 12 direct, 1 level
sim_max = max_file_size(BLOCK_SIZE, PTR_SIZE, N_DIRECT, 1)
print(f"\nOur fs_sim (block={BLOCK_SIZE}B, ptr={PTR_SIZE}B, {N_DIRECT} direct, 1 indirect):")
print(f"  ptrs_per_block = {BLOCK_SIZE // PTR_SIZE}")
print(f"  direct cap     = {N_DIRECT * BLOCK_SIZE} bytes")
print(f"  indirect cap   = {(BLOCK_SIZE // PTR_SIZE) * BLOCK_SIZE} bytes")
print(f"  Max file size  = {sim_max} bytes = {sim_max / 1024:.2f} KB")

# Verify by trying to write exactly max_size bytes
fs2 = FileSystem()
fs2.mkfs()
inum = fs2.create(ROOT_INUM, "maxfile")
try:
    # Write sim_max bytes (should succeed)
    chunk = bytes(range(256)) * (sim_max // 256) + bytes(range(sim_max % 256))
    fs2.write(inum, chunk)
    print(f"\nWrote {sim_max} bytes (max) successfully: True")
    # One byte more should fail
    fs2.write(inum, b"X", sim_max)
    print("  Wrote beyond max: should have failed!")
except OSError as e:
    print(f"  Writing one byte beyond max raises OSError: {e}")

print()


# ============================================================
# Exercise 3: Fragmentation when files grow
# ============================================================
# Demonstrate external fragmentation: create several small files,
# delete the even-numbered ones, then try to write a large file.
# Show that the free blocks are non-contiguous (scattered in bitmap).
# ============================================================

print(DIVIDER)
print("Exercise 3: Fragmentation when files grow")
print(DIVIDER)

# TODO: demonstrate fragmentation by alternating allocate/free and inspecting
# the free_bitmap before and after.


# --- Solution 3 ---

fs3 = FileSystem()
fs3.mkfs()

# Create 8 small files, each consuming exactly 1 block
FILE_COUNT = 8
file_inums = []
for i in range(FILE_COUNT):
    inum = fs3.create(ROOT_INUM, f"file{i}.txt")
    fs3.write(inum, bytes([i] * BLOCK_SIZE))
    file_inums.append(inum)

# Snapshot of which blocks are used
def used_blocks(fs):
    return [i for i, free in enumerate(fs.free_bitmap) if not free]

before = used_blocks(fs3)
print(f"After creating {FILE_COUNT} files, used blocks: {before}")

# Delete even-numbered files → creates "holes" in the block layout
for i in range(0, FILE_COUNT, 2):
    fs3.unlink(ROOT_INUM, f"file{i}.txt")

after_delete = used_blocks(fs3)
free_list = [i for i, free in enumerate(fs3.free_bitmap) if free]
print(f"After deleting even files, used blocks: {after_delete}")
print(f"Free blocks (fragmented): {free_list[:16]}{'...' if len(free_list) > 16 else ''}")

# Now write a large file — it will be split across non-contiguous blocks
large_inum = fs3.create(ROOT_INUM, "large.bin")
large_data = bytes(range(128)) * 2  # 256 bytes = 4 blocks
fs3.write(large_inum, large_data)

large_inode = fs3.inodes[large_inum]
large_blocks = [b for b in large_inode.direct if b != -1]
print(f"Large file's data blocks: {large_blocks}")
print(f"Are they contiguous? {large_blocks == list(range(large_blocks[0], large_blocks[0] + len(large_blocks)))}")
print(f"Data integrity check: {fs3.read(large_inum) == large_data}")
print("Key insight: the filesystem works correctly despite fragmentation,")
print("but a sequential read now requires multiple non-contiguous disk seeks.")

print()


# ============================================================
# Exercise 4: Hard link refcount semantics on unlink
# ============================================================
# Show exactly when an inode's blocks are freed:
#   - create a file
#   - hard link it 3 times
#   - unlink one at a time, tracking nlink and free_blocks
# ============================================================

print(DIVIDER)
print("Exercise 4: Hard link refcount semantics")
print(DIVIDER)

# TODO: demonstrate that data is freed only when nlink hits 0,
# and that each unlink decrements nlink by exactly 1.


# --- Solution 4 ---

fs4 = FileSystem()
fs4.mkfs()

inum = fs4.create(ROOT_INUM, "original.txt")
# Write enough data to consume 2 blocks so we can watch free_blocks change
fs4.write(inum, b"A" * (BLOCK_SIZE + 1))

def snap(fs, label, inum):
    inode = fs.inodes[inum]
    alive = not inode.is_free()
    print(f"  [{label}] nlink={inode.nlink if alive else 'N/A'}, "
          f"inode_alive={alive}, "
          f"free_blocks={fs.superblock['free_blocks']}")

snap(fs4, "after create", inum)

# Add 2 hard links (3 names total: original + link_a + link_b)
fs4.link(inum, ROOT_INUM, "link_a.txt")
fs4.link(inum, ROOT_INUM, "link_b.txt")
snap(fs4, "after 2 hard links", inum)

fs4.unlink(ROOT_INUM, "original.txt")
snap(fs4, "unlink original (nlink=2)", inum)

# Data still readable through link_a
content = fs4.read(inum)
print(f"  Content still accessible via inum: len={len(content)}, data={content[:8]!r}...")

fs4.unlink(ROOT_INUM, "link_a.txt")
snap(fs4, "unlink link_a   (nlink=1)", inum)

fs4.unlink(ROOT_INUM, "link_b.txt")
snap(fs4, "unlink link_b   (nlink=0, freed)", inum)
print("  Blocks freed only when last hard link removed.")

print()


# ============================================================
# Exercise 5: Recursive du (disk usage)
# ============================================================
# Implement du(fs, path) -> int that returns the total bytes
# consumed by a directory tree, following the real du semantics:
#   - a file's cost = bytes allocated in blocks (round up to block boundary)
#   - hard links: count each inode's blocks only ONCE
#   - do not recurse into symlinks
# ============================================================

print(DIVIDER)
print("Exercise 5: Recursive du (disk usage)")
print(DIVIDER)

# TODO: implement du(fs, path) recursively.
# Hint: track visited inums to avoid double-counting hard links.


# --- Solution 5 ---

def _du_blocks(inode) -> int:
    """Number of data blocks allocated for this inode (not counting indirect meta)."""
    count = sum(1 for b in inode.direct if b != -1)
    if inode.indirect != -1:
        # Count blocks pointed to by the indirect block
        # We don't have easy access to fs here — handle in du() instead
        pass
    return count


def du(fs: FileSystem, path: str, visited: set = None) -> int:
    """
    Compute disk usage in bytes (block-rounded) for path and all children.
    visited tracks inums already counted so hard links are not double-counted.
    """
    if visited is None:
        visited = set()

    inum = fs.resolve(path)
    inode = fs.inodes[inum]

    if inode.type == TYPE_LINK:
        # Symlinks are tiny; count their own inode blocks but don't recurse
        if inum in visited:
            return 0
        visited.add(inum)
        blks_used = sum(1 for b in inode.direct if b != -1)
        return blks_used * BLOCK_SIZE

    if inum in visited:
        return 0   # Hard link: already counted
    visited.add(inum)

    # Count this inode's own data blocks (rounded up to BLOCK_SIZE)
    direct_count = sum(1 for b in inode.direct if b != -1)
    indirect_count = 0
    if inode.indirect != -1:
        ind_blk = fs.blocks[inode.indirect]
        for i in range(PTRS_PER_BLK):
            ptr = struct.unpack_from("<I", ind_blk, i * PTR_SIZE)[0]
            if ptr != 0:
                indirect_count += 1
    total_blks = direct_count + indirect_count
    my_bytes = total_blks * BLOCK_SIZE

    if inode.type != 2:   # TYPE_DIR = 2
        return my_bytes

    # Recurse into directory children
    children_bytes = 0
    for name, child_inum in fs.ls(inum):
        child_path = path.rstrip("/") + "/" + name
        children_bytes += du(fs, child_path, visited)

    return my_bytes + children_bytes


# Build a tree to test du:
#   /
#   ├── docs/
#   │   ├── a.txt  (2 blocks)
#   │   └── b.txt  (hard link to a.txt — should NOT double-count)
#   └── media/
#       └── video.bin  (3 blocks)

fs5 = FileSystem()
fs5.mkfs()

docs_inum  = fs5.mkdir(ROOT_INUM, "docs")
media_inum = fs5.mkdir(ROOT_INUM, "media")

a_inum = fs5.create(docs_inum, "a.txt")
fs5.write(a_inum, b"X" * (BLOCK_SIZE * 2))   # exactly 2 blocks

fs5.link(a_inum, docs_inum, "b.txt")          # hard link — same inode

vid_inum = fs5.create(media_inum, "video.bin")
fs5.write(vid_inum, b"V" * (BLOCK_SIZE * 3))  # exactly 3 blocks

total = du(fs5, "/")
print(f"du /  = {total} bytes")

docs_du = du(fs5, "/docs")
print(f"du /docs = {docs_du} bytes  (a.txt uses 2 blocks; b.txt is hard link, not double-counted)")

media_du = du(fs5, "/media")
print(f"du /media = {media_du} bytes  (video.bin = 3 blocks)")

a_direct = [b for b in fs5.inodes[a_inum].direct if b != -1]
docs_inode = fs5.inodes[docs_inum]
docs_dir_blocks = sum(1 for b in docs_inode.direct if b != -1)
file_bytes = len(a_direct) * BLOCK_SIZE   # 2 blocks for a.txt (b.txt is same inode)
dir_bytes  = docs_dir_blocks * BLOCK_SIZE
print(f"\na.txt direct blocks: {a_direct}")
print(f"b.txt inum same as a.txt: {fs5.resolve('/docs/b.txt') == a_inum}")
print(f"du /docs = dir_blocks({docs_dir_blocks}×{BLOCK_SIZE}) + file_blocks(2×{BLOCK_SIZE}) = {docs_du} bytes")
print(f"b.txt (hard link) NOT double-counted: {docs_du == dir_bytes + file_bytes}")
