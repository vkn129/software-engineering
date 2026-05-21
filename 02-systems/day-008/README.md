# Day 8: File Systems — inodes, Blocks, Directories

## Why This Exists

Your program wants to store a string of bytes beyond its own lifetime. RAM dies with the process. The filesystem is the contract that lets you name a byte sequence, survive reboots, share it between processes, and extend it over time — all without knowing anything about how spinning platters or NAND cells physically work.

The design problem is harder than it looks. You need fast lookup by name, efficient random access by offset, space efficiency for both tiny and huge files, and safe sharing of data between names. The inode abstraction, invented at Bell Labs for UNIX in the early 1970s, solves all four with a single elegant structure that modern filesystems (ext4, XFS, APFS, NTFS) still use at their core.

### What If This Didn't Exist?

Without a structured filesystem, every program that wanted persistence would invent its own layout on disk — a nightmare of incompatible binary formats. Early CP/M machines used a flat file allocation table that worked fine for floppy disks but became catastrophically slow on hard drives: finding file X required scanning the entire FAT sequentially. Without inodes, renaming a file would require copying every byte. Without the separation of name (directory entry) from data (inode), hard links would be impossible and moving files across directories in the same volume would require actual I/O instead of a pointer update. The inode design lets `mv` on the same filesystem be a metadata-only operation that completes in microseconds regardless of file size.

### Why This Name?

"inode" stands for index node. The original UNIX source code used `inode` as a C struct name. "Index" because it is the lookup index into the disk: given an inode number you can find the file's data in O(1). "Node" because early designers thought of the file tree as a graph. The superblock holds the global index of inodes; each inode is itself an index of data blocks. It is indexes all the way down.

### The Physics Connection

Spinning disks have seek latency (~5 ms) that dwarfs sequential read time. Block sizes (4 KB on most modern systems) are chosen to match the disk's optimal I/O granularity — too small and you pay seek overhead on every read; too large and you waste space on small files. The direct/indirect/double-indirect pointer hierarchy trades pointer-fetch latency against the improbability of needing it: 99% of files fit entirely in direct blocks (12 × 4 KB = 48 KB), so the common path pays zero extra seeks. SSDs eliminate rotational latency but retain the block abstraction because it aligns with NAND erase blocks (~128 KB) and simplifies crash-consistency reasoning. Even on NVMe, random 512-byte reads are 10× slower than sequential 4 KB reads due to internal parallelism geometry.

### The Mathematics Connection

The three-level pointer scheme gives a specific maximum file size determined by block size B and pointer size P (8 bytes on 64-bit systems). Pointers per block = B/P. For B = 4096:

- Direct: 12 blocks = 48 KB
- Single-indirect: 512 blocks = 2 MB
- Double-indirect: 512² blocks = 1 GB
- Triple-indirect: 512³ blocks = 512 GB

Total max ≈ 512 GB per file for a basic three-level scheme (ext2/ext3). Ext4 uses extents instead — a (start_block, length) pair that describes runs of contiguous blocks, reducing metadata overhead from O(n) pointers to O(log n) extent tree nodes, pushing max file size to 16 TB with 4 KB blocks.

### The Economics Connection

Every filesystem design is a trade-off table. A large block size improves throughput for sequential workloads (video streaming) but wastes space for workloads dominated by small files (source code repos, email). The inode count is fixed at `mkfs` time in ext2/ext3: run out of inodes before running out of disk space and you cannot create new files even though bytes are free — a real-world failure mode that bites Linux servers hosting millions of small cache files. ZFS solves this by allocating inode-like "dnodes" dynamically, at the cost of complexity. The economics are: pay upfront (fixed inode table, simpler code) vs. pay per use (dynamic dnodes, better flexibility). Cloud storage (S3) abandons inodes entirely for a flat key-value model, accepting no hard links and no atomic rename in exchange for infinite horizontal scalability.

### When Does This Break?

**Crash consistency:** if the OS writes the inode update but crashes before writing the data block, or writes data but not the inode, the filesystem is inconsistent. Classic UNIX solved this with `fsck` on reboot — a full disk scan that took hours on large disks. Journaling filesystems (ext3, ext4, NTFS) write a journal entry before modifying metadata, so recovery replays the journal instead of scanning. **Directory corruption:** a directory is just a file whose bytes are `(inum, name)` pairs; corruption here breaks path resolution for all children. **Link storms:** a file with millions of hard links has a refcount that must be decremented on every `unlink` — O(1) per call but the bookkeeping can confuse tools like `find` and `du` that assume trees. **Symlink loops:** `ln -s /a /a/b` creates a loop; the kernel catches this with a hop counter (MAXSYMLINKS = 40 on Linux).

### When Should You Violate This?

Skip the POSIX filesystem abstraction when your access pattern is fundamentally incompatible with it. Log-structured databases (RocksDB, LevelDB) bypass the filesystem's block cache and do their own buffering because they need write ordering guarantees the filesystem doesn't provide efficiently. High-frequency trading systems write directly to raw block devices to eliminate the VFS layer's syscall overhead. Distributed object stores (Ceph, S3) replace inodes with a flat namespace plus consistent hashing because replication and sharding are impossible to retrofit onto inode semantics. The rule: the inode abstraction is right for almost every general-purpose workload; abandon it only when you have profiled evidence that a specific constraint (ordering, latency, namespace size) is irreconcilable with it.

## Theory

### The Disk Layout

A formatted disk partition is divided into fixed-size regions:

```
| Superblock | Inode Bitmap | Data Bitmap | Inode Table | Data Blocks |
```

- **Superblock** — global metadata: block size, total blocks, total inodes, free counts, filesystem magic number and version. The OS reads the superblock first on mount. It is replicated at multiple offsets on disk as a corruption hedge.
- **Inode bitmap** — one bit per inode slot. 1 = in use, 0 = free. Used by `create` to find a free inode number in O(inodes/8) time.
- **Data bitmap** — one bit per data block. Same purpose for block allocation.
- **Inode table** — array of fixed-size inode structs. Inode number → byte offset = inum × sizeof(inode). O(1) lookup.
- **Data blocks** — the actual file content, organized as 4 KB (or configurable) chunks.

### The Inode

Each inode stores:
- `size` — byte count of the file
- `type` — regular, directory, symlink, device
- `nlink` — number of hard links (directory entries pointing here)
- `uid`, `gid`, `permissions`
- `atime`, `mtime`, `ctime` — access, modification, change timestamps
- `direct[0..11]` — 12 block numbers for the first 48 KB of file data
- `indirect` — block number of a block full of block numbers (extends range by B/8 × B bytes)
- `double_indirect` — block of blocks of block numbers

The inode does **not** store the filename. The filename lives in the directory that contains this file. This is the key insight that makes hard links work.

### Directories

A directory is a regular file whose content is a sequence of `(inode_number, name)` pairs. When you call `open("/home/user/notes.txt")`, the kernel:

1. Starts at the root inode (always inode 2 in ext2).
2. Reads root's data blocks as directory entries. Scans for the entry named `"home"`. Gets its inode number.
3. Reads inode for `"home"`. Reads its data blocks as directory entries. Scans for `"user"`.
4. Reads inode for `"user"`. Scans for `"notes.txt"`. Gets its inode number.
5. Reads inode for `"notes.txt"`. Now has type, size, permissions, block pointers.
6. Checks permissions. Returns a file descriptor backed by this inode.

Each step costs at least one disk seek (inode read) + one block read (directory data). This is why deep directory trees have higher open latency. Modern kernels cache the inode and directory entry ("dentry cache") so repeated opens of the same path cost zero disk I/O.

### Hard vs Symbolic Links

**Hard link:** a second directory entry pointing to the same inode number. `nlink` on the inode is incremented. Both names are equal — there is no "original." Deleting one name decrements `nlink`; the inode and data blocks are freed only when `nlink` reaches 0 and no process has the file open. Hard links cannot cross filesystem boundaries (inode numbers are per-filesystem) and cannot point to directories (to prevent cycles).

**Symbolic link:** a separate inode of type `symlink` whose data block contains the target path string. Every access through a symlink re-resolves the target path. Symlinks can cross filesystems, can point to directories, can be dangling (pointing to a nonexistent target). They add at least one extra inode lookup per path component.

## Practice

Work through `practice.py`. Five exercises with TODO slots and full solutions below each. Complete the TODO before reading the solution.

## Checkpoint Questions

1. A 4 KB block stores 512 8-byte block pointers. What is the maximum file size (in GB) for a filesystem with 12 direct, 1 single-indirect, 1 double-indirect, and 1 triple-indirect block pointer, using 4 KB blocks?

2. You call `rename("/a/x", "/b/x")` where `/a` and `/b` are on the same ext4 filesystem. How many inodes are modified? Which ones, and why does the file content not need to move?

3. A process opens a file, then another process calls `unlink()` on that filename. What happens to the file's data? When is it actually freed?

4. Explain why `du -sh /large_dir` can take 10 seconds while `df -h` returns instantly.

5. A filesystem has 1 million inode slots and 500 GB of data blocks. You store 2 million 1-byte files. What error do you get, and why?
