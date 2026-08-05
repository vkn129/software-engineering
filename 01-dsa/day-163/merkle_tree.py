"""
Day 163: Merkle Tree — Build, Prove, Verify

Build a balanced binary Merkle tree over N data blocks. Generate
inclusion proofs of size log2(N). Verify with only the root hash.

Domain-separated hashing (RFC 6962 style) to block second-preimage attacks.

Used by: Git (commit/tree objects), Bitcoin (block tx root),
Cassandra anti-entropy, IPFS, Certificate Transparency.
"""

import hashlib


# ---------------------------------------------------------------------------
# Domain-separated hashing
# ---------------------------------------------------------------------------

def _h_leaf(data: bytes) -> bytes:
    """Hash a leaf with a 0x00 domain tag."""
    return hashlib.sha256(b"\x00" + data).digest()


def _h_node(left: bytes, right: bytes) -> bytes:
    """Hash an inner node with a 0x01 domain tag."""
    return hashlib.sha256(b"\x01" + left + right).digest()


# ---------------------------------------------------------------------------
# Merkle tree
# ---------------------------------------------------------------------------

class MerkleTree:
    """
    Stores all levels of the tree. Odd-leaf rule: duplicate the last node
    on each level (Bitcoin style).
    """

    def __init__(self, blocks):
        if not blocks:
            raise ValueError("at least one block required")
        # Level 0 = leaf hashes
        self.levels = [[_h_leaf(b if isinstance(b, bytes) else b.encode())
                        for b in blocks]]
        self.n = len(blocks)
        self._build()

    def _build(self) -> None:
        while len(self.levels[-1]) > 1:
            prev = self.levels[-1]
            nxt = []
            for i in range(0, len(prev), 2):
                left = prev[i]
                right = prev[i + 1] if i + 1 < len(prev) else left  # dup
                nxt.append(_h_node(left, right))
            self.levels.append(nxt)

    @property
    def root(self) -> bytes:
        return self.levels[-1][0]

    def proof(self, index: int) -> list:
        """
        Return list of (sibling_hash, side) for the path from leaf index to
        root. side is 'L' or 'R' indicating whether the sibling is on the
        left or right of the current node.
        """
        if not (0 <= index < self.n):
            raise IndexError(index)
        path = []
        idx = index
        for level in self.levels[:-1]:
            sibling_idx = idx ^ 1
            if sibling_idx >= len(level):
                sibling_idx = idx  # duplicated; sibling is self
            side = "R" if sibling_idx > idx else "L"
            path.append((level[sibling_idx], side))
            idx //= 2
        return path


# ---------------------------------------------------------------------------
# Stateless verifier — does not need the tree, only root + proof
# ---------------------------------------------------------------------------

def verify_proof(leaf_data, proof, root, index=None) -> bool:
    """
    Recompute the root from a leaf and its proof.
    `index` is unused now because side is encoded in each step.
    """
    if isinstance(leaf_data, str):
        leaf_data = leaf_data.encode()
    h = _h_leaf(leaf_data)
    for sibling, side in proof:
        if side == "L":
            h = _h_node(sibling, h)
        else:
            h = _h_node(h, sibling)
    return h == root


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_build_and_prove():
    print("=" * 60)
    print("DEMO 1: Build tree and prove inclusion")
    print("=" * 60)
    blocks = [f"tx-{i}" for i in range(8)]
    tree = MerkleTree(blocks)
    print(f"  8 transactions, root = {tree.root.hex()[:16]}...")
    print(f"  tree depth = {len(tree.levels) - 1}")
    for i in (0, 3, 7):
        p = tree.proof(i)
        ok = verify_proof(blocks[i], p, tree.root)
        print(f"  proof[{i}] size={len(p)} verify={ok}")


def demo_tamper_detection():
    print("\n" + "=" * 60)
    print("DEMO 2: Tampering changes the root")
    print("=" * 60)
    blocks = [f"file:{i}" for i in range(16)]
    tree = MerkleTree(blocks)
    print(f"  original root: {tree.root.hex()[:16]}...")

    blocks[5] = "file:5-TAMPERED"
    tree2 = MerkleTree(blocks)
    print(f"  tampered root: {tree2.root.hex()[:16]}...")
    print(f"  equal: {tree.root == tree2.root}")

    # Old proof against new root must fail
    blocks_orig = [f"file:{i}" for i in range(16)]
    tree_orig = MerkleTree(blocks_orig)
    proof = tree_orig.proof(5)
    bad = verify_proof("file:5-TAMPERED", proof, tree_orig.root)
    print(f"  fake leaf with old proof verifies: {bad} (should be False)")


def demo_large_proof_size():
    print("\n" + "=" * 60)
    print("DEMO 3: Proof size = log2(N)")
    print("=" * 60)
    for n in (16, 256, 4096, 65536):
        blocks = [f"x{i}" for i in range(n)]
        tree = MerkleTree(blocks)
        p = tree.proof(n // 2)
        proof_bytes = len(p) * 32
        full_bytes = n * 32
        print(f"  N={n:>6}  proof={len(p)} hashes ({proof_bytes} B)"
              f"  vs full dataset = {full_bytes} B")


def demo_uneven_leaves():
    print("\n" + "=" * 60)
    print("DEMO 4: Odd leaf count (last duplicated)")
    print("=" * 60)
    blocks = ["a", "b", "c", "d", "e"]   # 5 -> dup
    tree = MerkleTree(blocks)
    for i, b in enumerate(blocks):
        ok = verify_proof(b, tree.proof(i), tree.root)
        print(f"  leaf {i} '{b}' verifies: {ok}")


if __name__ == "__main__":
    demo_build_and_prove()
    demo_tamper_detection()
    demo_large_proof_size()
    demo_uneven_leaves()
