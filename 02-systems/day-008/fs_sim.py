"""
fs_sim.py — in-memory inode-based filesystem simulation.

Implements a minimal UNIX-style filesystem with:
  - Superblock (global metadata)
  - Inode table (12 direct + 1 indirect pointer per inode)
  - Free-block bitmap
  - Directory entries as (inum, name) pairs stored in inode data

All storage is simulated as a flat Block array (list of bytearray).
"""

import struct
import math

# ---------------------------------------------------------------------------
# Constants — these match a toy 4 KB block filesystem
# ---------------------------------------------------------------------------

BLOCK_SIZE    = 64        # bytes per block (small so indirect blocks fire early)
PTR_SIZE      = 4         # bytes per block pointer (supports up to 2^32 blocks)
PTRS_PER_BLK  = BLOCK_SIZE // PTR_SIZE   # 16 pointers per indirect block
N_DIRECT      = 12        # direct block pointers in inode
TOTAL_BLOCKS  = 512       # total data blocks in the simulated device
TOTAL_INODES  = 64        # maximum number of inodes

# Inode types
TYPE_FREE  = 0
TYPE_FILE  = 1
TYPE_DIR   = 2
TYPE_LINK  = 3  # symbolic link

# Directory entry format: 4-byte inum + 28-byte name (null-padded) = 32 bytes
DIRENT_SIZE   = 32
DIRENT_FMT    = f"<I28s"   # little-endian uint32 + 28 raw bytes
ROOT_INUM     = 0           # inode 0 is always the root directory

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _encode_name(name: str) -> bytes:
    """Encode a filename into exactly 28 bytes (null-padded, truncated)."""
    raw = name.encode("utf-8")[:27]
    return raw.ljust(28, b"\x00")

def _decode_name(raw: bytes) -> str:
    return raw.rstrip(b"\x00").decode("utf-8")

def _pack_dirent(inum: int, name: str) -> bytes:
    return struct.pack(DIRENT_FMT, inum, _encode_name(name))

def _unpack_dirent(data: bytes) -> tuple:
    inum, raw_name = struct.unpack(DIRENT_FMT, data)
    return inum, _decode_name(raw_name)

# ---------------------------------------------------------------------------
# Inode structure
# ---------------------------------------------------------------------------

class Inode:
    """
    In-memory inode. On a real disk this would be packed into a fixed-size
    binary struct. We keep it as a Python object for clarity.

    Pointer layout mirrors ext2:
      direct[0..11]  — points directly at data blocks
      indirect       — points at a block that contains PTRS_PER_BLK block ptrs
    """

    def __init__(self, inum: int):
        self.inum       = inum
        self.type       = TYPE_FREE
        self.size       = 0           # logical byte count
        self.nlink      = 0           # hard-link reference count
        self.direct     = [-1] * N_DIRECT   # -1 = not allocated
        self.indirect   = -1          # -1 = not allocated

    def is_free(self) -> bool:
        return self.type == TYPE_FREE

    def clear(self):
        self.type     = TYPE_FREE
        self.size     = 0
        self.nlink    = 0
        self.direct   = [-1] * N_DIRECT
        self.indirect = -1

    def __repr__(self):
        type_name = {TYPE_FREE: "free", TYPE_FILE: "file",
                     TYPE_DIR: "dir", TYPE_LINK: "symlink"}[self.type]
        return (f"Inode(inum={self.inum}, type={type_name}, "
                f"size={self.size}, nlink={self.nlink})")

# ---------------------------------------------------------------------------
# Filesystem core
# ---------------------------------------------------------------------------

class FileSystem:
    """
    In-memory filesystem with UNIX inode semantics.

    Device layout (logical):
      blocks[0 .. TOTAL_BLOCKS-1]   — the raw block array
      inodes[0 .. TOTAL_INODES-1]   — inode table (separate from blocks for clarity)
      free_bitmap                   — one bool per block (True = free)
    """

    def __init__(self):
        self.blocks      = [bytearray(BLOCK_SIZE) for _ in range(TOTAL_BLOCKS)]
        self.inodes      = [Inode(i) for i in range(TOTAL_INODES)]
        self.free_bitmap = [True] * TOTAL_BLOCKS   # all blocks free
        self.superblock  = {
            "block_size":    BLOCK_SIZE,
            "total_blocks":  TOTAL_BLOCKS,
            "total_inodes":  TOTAL_INODES,
            "free_blocks":   TOTAL_BLOCKS,
            "free_inodes":   TOTAL_INODES,
        }

    # ------------------------------------------------------------------
    # mkfs — initialise the filesystem and create the root directory
    # ------------------------------------------------------------------

    def mkfs(self):
        """
        Format the filesystem. Allocates root inode (inum=ROOT_INUM)
        and writes the mandatory '.' and '..' self-referential entries.
        """
        # Reset everything
        for blk in self.blocks:
            blk[:] = bytearray(BLOCK_SIZE)
        for inode in self.inodes:
            inode.clear()
        self.free_bitmap = [True] * TOTAL_BLOCKS
        self.superblock["free_blocks"] = TOTAL_BLOCKS
        self.superblock["free_inodes"] = TOTAL_INODES

        # Allocate root directory
        root = self.inodes[ROOT_INUM]
        root.type  = TYPE_DIR
        root.nlink = 2   # '.' entry + one reference from parent (itself here)
        self.superblock["free_inodes"] -= 1

        # Write '.' and '..' directory entries into root
        self._dir_add_entry(ROOT_INUM, ROOT_INUM, ".")
        self._dir_add_entry(ROOT_INUM, ROOT_INUM, "..")

    # ------------------------------------------------------------------
    # Block allocation helpers
    # ------------------------------------------------------------------

    def _alloc_block(self) -> int:
        """Find and reserve a free data block. Returns block number."""
        for i, free in enumerate(self.free_bitmap):
            if free:
                self.free_bitmap[i] = False
                self.superblock["free_blocks"] -= 1
                self.blocks[i][:] = bytearray(BLOCK_SIZE)  # zero on alloc
                return i
        raise OSError("No free blocks (disk full)")

    def _free_block(self, bnum: int):
        """Release a data block back to the pool."""
        if bnum < 0 or bnum >= TOTAL_BLOCKS:
            return
        self.free_bitmap[bnum] = True
        self.superblock["free_blocks"] += 1

    # ------------------------------------------------------------------
    # Inode allocation helpers
    # ------------------------------------------------------------------

    def _alloc_inode(self, itype: int) -> int:
        """Find a free inode slot, initialise it, return inum."""
        for inode in self.inodes:
            if inode.is_free():
                inode.type  = itype
                inode.size  = 0
                inode.nlink = 1
                inode.direct   = [-1] * N_DIRECT
                inode.indirect = -1
                self.superblock["free_inodes"] -= 1
                return inode.inum
        raise OSError("No free inodes")

    def _free_inode(self, inum: int):
        inode = self.inodes[inum]
        inode.clear()
        self.superblock["free_inodes"] += 1

    # ------------------------------------------------------------------
    # Block-level read/write via the pointer tree
    # ------------------------------------------------------------------

    def _get_block_num(self, inode: Inode, logical_blk: int,
                       allocate: bool = False) -> int:
        """
        Translate a logical block index within a file to a physical block number.

        - Blocks 0..N_DIRECT-1 use direct pointers.
        - Blocks N_DIRECT..N_DIRECT+PTRS_PER_BLK-1 go through the single
          indirect block (allocated on demand if allocate=True).

        Returns -1 if the block is not allocated and allocate=False.
        """
        if logical_blk < N_DIRECT:
            # Fast path: direct pointer
            if allocate and inode.direct[logical_blk] == -1:
                inode.direct[logical_blk] = self._alloc_block()
            return inode.direct[logical_blk]

        # Single-indirect zone
        indirect_idx = logical_blk - N_DIRECT
        if indirect_idx >= PTRS_PER_BLK:
            raise OSError(
                f"File too large: logical block {logical_blk} exceeds "
                f"direct ({N_DIRECT}) + indirect ({PTRS_PER_BLK}) capacity"
            )

        # Allocate the indirect block itself if needed
        if inode.indirect == -1:
            if not allocate:
                return -1
            inode.indirect = self._alloc_block()

        # Read the pointer stored at position indirect_idx inside the indirect block
        ind_blk = self.blocks[inode.indirect]
        offset  = indirect_idx * PTR_SIZE
        ptr     = struct.unpack_from("<I", ind_blk, offset)[0]

        if ptr == 0 and allocate:
            # 0 means unallocated (we zero blocks on alloc so this is safe)
            new_blk = self._alloc_block()
            struct.pack_into("<I", ind_blk, offset, new_blk)
            ptr = new_blk

        return ptr if ptr != 0 else -1

    def _block_read(self, inode: Inode, logical_blk: int) -> bytearray:
        bnum = self._get_block_num(inode, logical_blk)
        if bnum == -1:
            return bytearray(BLOCK_SIZE)   # sparse: return zeros
        return bytearray(self.blocks[bnum])

    def _block_write(self, inode: Inode, logical_blk: int, data: bytes):
        bnum = self._get_block_num(inode, logical_blk, allocate=True)
        self.blocks[bnum][:len(data)] = data

    # ------------------------------------------------------------------
    # High-level file operations
    # ------------------------------------------------------------------

    def create(self, parent_inum: int, name: str) -> int:
        """
        Create a new empty regular file in parent directory.
        Returns the new inode number.
        """
        self._ensure_dir(parent_inum)
        inum = self._alloc_inode(TYPE_FILE)
        self._dir_add_entry(parent_inum, inum, name)
        return inum

    def write(self, inum: int, data: bytes, offset: int = 0):
        """
        Write bytes into a file starting at offset.
        Grows the file if needed. Overwrites existing bytes.
        """
        inode = self.inodes[inum]
        if inode.type not in (TYPE_FILE, TYPE_LINK, TYPE_DIR):
            raise OSError(f"Inode {inum} is not writable (type={inode.type})")

        pos = offset
        remaining = data
        while remaining:
            logical_blk = pos // BLOCK_SIZE
            blk_offset  = pos % BLOCK_SIZE
            chunk       = min(BLOCK_SIZE - blk_offset, len(remaining))

            # Read-modify-write so we don't clobber data outside our range
            bnum = self._get_block_num(inode, logical_blk, allocate=True)
            blk  = self.blocks[bnum]
            blk[blk_offset:blk_offset + chunk] = remaining[:chunk]

            remaining = remaining[chunk:]
            pos += chunk

        inode.size = max(inode.size, pos)

    def read(self, inum: int, length: int = -1, offset: int = 0) -> bytes:
        """Read up to length bytes from file at offset. -1 = read entire file."""
        inode = self.inodes[inum]
        if inode.type not in (TYPE_FILE, TYPE_LINK):
            raise OSError(f"Inode {inum} is not a regular file")

        if length == -1:
            length = inode.size - offset
        length = max(0, min(length, inode.size - offset))

        result = bytearray()
        pos = offset
        while len(result) < length:
            logical_blk = pos // BLOCK_SIZE
            blk_offset  = pos % BLOCK_SIZE
            chunk       = min(BLOCK_SIZE - blk_offset, length - len(result))

            blk = self._block_read(inode, logical_blk)
            result.extend(blk[blk_offset:blk_offset + chunk])
            pos += chunk

        return bytes(result)

    def unlink(self, parent_inum: int, name: str):
        """
        Remove a directory entry. Decrements nlink on the inode.
        Frees inode + data blocks only when nlink reaches 0 (and no
        open file descriptors — we skip the fd tracking for brevity).
        """
        inum = self._dir_remove_entry(parent_inum, name)
        inode = self.inodes[inum]
        inode.nlink -= 1
        if inode.nlink == 0:
            self._release_inode_blocks(inode)
            self._free_inode(inum)

    def link(self, existing_inum: int, parent_inum: int, new_name: str):
        """
        Hard link: add a new directory entry pointing at an existing inode.
        Increments nlink. Directories cannot be hard-linked (prevents cycles).
        """
        inode = self.inodes[existing_inum]
        if inode.type == TYPE_DIR:
            raise OSError("Cannot create hard link to directory")
        self._dir_add_entry(parent_inum, existing_inum, new_name)
        inode.nlink += 1

    def mkdir(self, parent_inum: int, name: str) -> int:
        """Create a subdirectory. Returns the new directory's inum."""
        self._ensure_dir(parent_inum)
        inum = self._alloc_inode(TYPE_DIR)
        inode = self.inodes[inum]
        inode.nlink = 2   # '.' + parent's ref

        # Add '.' and '..' entries inside the new dir
        self._dir_add_entry(inum, inum, ".")
        self._dir_add_entry(inum, parent_inum, "..")

        # Add the new dir's name into the parent
        self._dir_add_entry(parent_inum, inum, name)
        # Parent nlink++ because '..' in child points back to parent
        self.inodes[parent_inum].nlink += 1
        return inum

    def ls(self, dir_inum: int) -> list:
        """
        Return list of (name, inum) for all entries in the directory,
        excluding '.' and '..'.
        """
        self._ensure_dir(dir_inum)
        entries = self._read_dirents(dir_inum)
        return [(name, inum) for name, inum in entries
                if name not in (".", "..")]

    # ------------------------------------------------------------------
    # Path resolution — walks the inode tree for open("/a/b/c")
    # ------------------------------------------------------------------

    def resolve(self, path: str) -> int:
        """
        Translate an absolute path to an inode number.
        This mimics the kernel's namei() loop.
        """
        if not path.startswith("/"):
            raise OSError("Only absolute paths supported")

        parts = [p for p in path.split("/") if p]
        inum  = ROOT_INUM

        for part in parts:
            inode = self.inodes[inum]
            if inode.type != TYPE_DIR:
                raise FileNotFoundError(f"Not a directory at component before '{part}'")
            entries = dict(self._read_dirents(inum))
            if part not in entries:
                raise FileNotFoundError(f"No such file or directory: '{part}'")
            inum = entries[part]

        return inum

    # ------------------------------------------------------------------
    # Directory helpers (internal)
    # ------------------------------------------------------------------

    def _ensure_dir(self, inum: int):
        if self.inodes[inum].type != TYPE_DIR:
            raise OSError(f"Inode {inum} is not a directory")

    def _read_dirents(self, dir_inum: int) -> list:
        """Return list of (name, inum) pairs from directory data blocks."""
        inode = self.inodes[dir_inum]
        raw   = self.read_raw(inode)
        entries = []
        for i in range(0, len(raw), DIRENT_SIZE):
            chunk = raw[i:i + DIRENT_SIZE]
            if len(chunk) < DIRENT_SIZE:
                break
            inum, name = _unpack_dirent(chunk)
            if inum == 0 and not name:
                continue   # empty slot
            entries.append((name, inum))
        return entries

    def read_raw(self, inode: Inode) -> bytes:
        """Read all bytes of an inode (any type) for internal use."""
        result = bytearray()
        pos = 0
        while pos < inode.size:
            logical_blk = pos // BLOCK_SIZE
            blk_offset  = pos % BLOCK_SIZE
            chunk       = min(BLOCK_SIZE - blk_offset, inode.size - pos)
            blk         = self._block_read(inode, logical_blk)
            result.extend(blk[blk_offset:blk_offset + chunk])
            pos += chunk
        return bytes(result)

    def _dir_add_entry(self, dir_inum: int, target_inum: int, name: str):
        """Append a (inum, name) entry to a directory file."""
        inode  = self.inodes[dir_inum]
        offset = inode.size
        packed = _pack_dirent(target_inum, name)
        self.write(dir_inum, packed, offset)

    def _dir_remove_entry(self, dir_inum: int, name: str) -> int:
        """
        Remove named entry from directory. Returns the removed inum.
        We zero out the entry in place (simple linear scan; production
        filesystems reuse freed slots).
        """
        inode = self.inodes[dir_inum]
        raw   = bytearray(self.read_raw(inode))
        for i in range(0, len(raw), DIRENT_SIZE):
            chunk = raw[i:i + DIRENT_SIZE]
            if len(chunk) < DIRENT_SIZE:
                break
            inum, entry_name = _unpack_dirent(chunk)
            if entry_name == name:
                # Zero this slot
                raw[i:i + DIRENT_SIZE] = bytearray(DIRENT_SIZE)
                # Write back all directory data
                self.write(dir_inum, bytes(raw), 0)
                inode.size = len(raw)
                return inum
        raise FileNotFoundError(f"No entry named '{name}' in inode {dir_inum}")

    def _release_inode_blocks(self, inode: Inode):
        """Free all data blocks owned by an inode (called when nlink→0)."""
        for bnum in inode.direct:
            if bnum != -1:
                self._free_block(bnum)

        if inode.indirect != -1:
            ind_blk = self.blocks[inode.indirect]
            for i in range(PTRS_PER_BLK):
                ptr = struct.unpack_from("<I", ind_blk, i * PTR_SIZE)[0]
                if ptr != 0:
                    self._free_block(ptr)
            self._free_block(inode.indirect)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self):
        sb = self.superblock
        used_blks  = sb["total_blocks"] - sb["free_blocks"]
        used_inodes = sb["total_inodes"] - sb["free_inodes"]
        print("=== Filesystem Stats ===")
        print(f"  Block size      : {sb['block_size']} bytes")
        print(f"  Total blocks    : {sb['total_blocks']}")
        print(f"  Used blocks     : {used_blks}")
        print(f"  Free blocks     : {sb['free_blocks']}")
        print(f"  Total inodes    : {sb['total_inodes']}")
        print(f"  Used inodes     : {used_inodes}")
        print(f"  Free inodes     : {sb['free_inodes']}")
        max_file_blks = N_DIRECT + PTRS_PER_BLK
        max_file_bytes = max_file_blks * BLOCK_SIZE
        print(f"  Max file size   : {max_file_bytes} bytes "
              f"({N_DIRECT} direct + {PTRS_PER_BLK} indirect blocks × {BLOCK_SIZE}B)")


# ---------------------------------------------------------------------------
# Demo — exercises every major code path
# ---------------------------------------------------------------------------

def main():
    fs = FileSystem()
    fs.mkfs()

    print("=== mkfs complete ===\n")

    # 1. Create a directory tree: /docs  /docs/notes
    docs_inum  = fs.mkdir(ROOT_INUM, "docs")
    notes_inum = fs.mkdir(docs_inum, "notes")
    print(f"Created /docs (inum={docs_inum}), /docs/notes (inum={notes_inum})")

    # 2. Create and write a small file in /docs
    hello_inum = fs.create(docs_inum, "hello.txt")
    fs.write(hello_inum, b"Hello, filesystem!\n")
    content = fs.read(hello_inum)
    print(f"\nWrote and read /docs/hello.txt: {content!r}")

    # 3. Write a file large enough to exercise indirect blocks
    #    BLOCK_SIZE=64, N_DIRECT=12 → direct capacity = 768 bytes
    #    Writing 1 KB forces allocation through the indirect pointer
    large_inum = fs.create(notes_inum, "large.bin")
    large_data = bytes(range(256)) * 4   # 1024 bytes
    fs.write(large_inum, large_data)
    readback = fs.read(large_inum)

    inode = fs.inodes[large_inum]
    indirect_used = inode.indirect != -1
    print(f"\nWrote {len(large_data)}-byte file /docs/notes/large.bin")
    print(f"  Indirect block allocated: {indirect_used}  "
          f"(direct capacity = {N_DIRECT * BLOCK_SIZE} bytes)")
    print(f"  Data integrity check    : {readback == large_data}")

    # 4. Hard link — two names, one inode
    fs.link(hello_inum, ROOT_INUM, "hello_alias.txt")
    alias_inum = fs.resolve("/hello_alias.txt")
    print(f"\nHard link /hello_alias.txt → inum {alias_inum} "
          f"(same as /docs/hello.txt inum={hello_inum}? "
          f"{alias_inum == hello_inum})")
    print(f"  nlink on shared inode   : {fs.inodes[hello_inum].nlink}")

    # Read through the alias to confirm shared data
    alias_content = fs.read(alias_inum)
    print(f"  Content via alias       : {alias_content!r}")

    # 5. Demonstrate path resolution: open("/docs/notes/large.bin")
    resolved_inum = fs.resolve("/docs/notes/large.bin")
    print(f"\nPath resolution /docs/notes/large.bin → inum {resolved_inum} "
          f"(matches? {resolved_inum == large_inum})")

    # 6. ls output
    print("\n=== Directory listings ===")
    for path, dir_inum in [("/", ROOT_INUM), ("/docs", docs_inum),
                            ("/docs/notes", notes_inum)]:
        entries = fs.ls(dir_inum)
        print(f"  {path}: {entries}")

    # 7. Unlink hello.txt — nlink drops but alias still live
    fs.unlink(docs_inum, "hello.txt")
    print(f"\nAfter unlink /docs/hello.txt:")
    print(f"  nlink = {fs.inodes[hello_inum].nlink}  (inode still alive via alias)")
    print(f"  Alias content still readable: {fs.read(alias_inum)!r}")

    # 8. Unlink the alias too — now nlink=0, blocks freed
    fs.unlink(ROOT_INUM, "hello_alias.txt")
    print(f"\nAfter unlink /hello_alias.txt:")
    print(f"  Inode {hello_inum} is free: {fs.inodes[hello_inum].is_free()}")

    # 9. Final stats
    print()
    fs.stats()


if __name__ == "__main__":
    main()
