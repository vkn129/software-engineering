"""
Day 163 Practice: Merkle Trees

Implement TODOs, run: python practice.py
"""

import hashlib


def _h_leaf(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def _h_node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: leaf hashes
# ===================================================================

def hash_leaves(blocks):
    """Hash each block (bytes or str) with the leaf domain tag.
    Returns list[bytes]."""
    # TODO
    pass


def _sol_hash_leaves(blocks):
    out = []
    for b in blocks:
        if isinstance(b, str):
            b = b.encode()
        out.append(_h_leaf(b))
    return out


# ===================================================================
# Exercise 2: build next level from current level
# ===================================================================
# Pair adjacent nodes; duplicate the last if odd count.

def build_level(level):
    """level: list[bytes]. Return next level up."""
    # TODO
    pass


def _sol_build_level(level):
    out = []
    for i in range(0, len(level), 2):
        left = level[i]
        right = level[i + 1] if i + 1 < len(level) else left
        out.append(_h_node(left, right))
    return out


# ===================================================================
# Exercise 3: compute Merkle root
# ===================================================================

def merkle_root(blocks):
    """Return root bytes for a list of data blocks."""
    # TODO
    pass


def _sol_merkle_root(blocks):
    level = _sol_hash_leaves(blocks)
    while len(level) > 1:
        level = _sol_build_level(level)
    return level[0]


# ===================================================================
# Exercise 4: inclusion proof
# ===================================================================
# Return [(sibling_hash, side)] from leaf to root.

def inclusion_proof(blocks, index):
    """blocks: list of data. index: leaf to prove. Return list of (hash, 'L'|'R')."""
    # TODO
    pass


def _sol_inclusion_proof(blocks, index):
    levels = [_sol_hash_leaves(blocks)]
    while len(levels[-1]) > 1:
        levels.append(_sol_build_level(levels[-1]))
    path = []
    idx = index
    for level in levels[:-1]:
        sib = idx ^ 1
        if sib >= len(level):
            sib = idx
        side = "R" if sib > idx else "L"
        path.append((level[sib], side))
        idx //= 2
    return path


# ===================================================================
# Exercise 5: verify an inclusion proof
# ===================================================================

def verify(leaf_data, proof, root):
    """Recompute root from leaf+proof. Return bool."""
    # TODO
    pass


def _sol_verify(leaf_data, proof, root):
    if isinstance(leaf_data, str):
        leaf_data = leaf_data.encode()
    h = _h_leaf(leaf_data)
    for sibling, side in proof:
        h = _h_node(sibling, h) if side == "L" else _h_node(h, sibling)
    return h == root


# ===================================================================
# Exercise 6: detect tampering across two snapshots
# ===================================================================
# Given two block lists, return list of indices that differ AND for which
# the Merkle root changed (the root MUST change if any index differs).

def find_tampered_indices(old_blocks, new_blocks):
    """Return sorted list of indices i where old_blocks[i] != new_blocks[i].
    Assumes same length."""
    # TODO
    pass


def _sol_find_tampered_indices(old_blocks, new_blocks):
    return [i for i in range(len(old_blocks)) if old_blocks[i] != new_blocks[i]]


# ===================================================================
# Test runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} expected={expected} got={got}")
            failed += 1

    # Ex 1
    print("Exercise 1: hash_leaves")
    leaves = try_or_sol("hash_leaves", ["a", "b", "c"])
    check("3 leaves", len(leaves), 3)
    check("32-byte hash", len(leaves[0]), 32)
    check("distinct hashes", len(set(leaves)), 3)

    # Ex 2
    print("\nExercise 2: build_level")
    nxt = try_or_sol("build_level", leaves)
    check("3 -> 2 (odd dup)", len(nxt), 2)
    nxt2 = try_or_sol("build_level", nxt)
    check("2 -> 1", len(nxt2), 1)

    # Ex 3
    print("\nExercise 3: merkle_root")
    r1 = try_or_sol("merkle_root", ["a", "b", "c", "d"])
    check("root is 32 bytes", len(r1), 32)
    r2 = try_or_sol("merkle_root", ["a", "b", "c", "d"])
    check("deterministic", r1, r2)
    r3 = try_or_sol("merkle_root", ["a", "b", "c", "X"])
    check("change in leaf -> change in root", r1 != r3, True)

    # Ex 4
    print("\nExercise 4: inclusion_proof")
    blocks = [f"tx{i}" for i in range(8)]
    p = try_or_sol("inclusion_proof", blocks, 3)
    check("proof depth 3", len(p), 3)
    check("side annotated", all(s in ("L", "R") for _, s in p), True)

    # Ex 5
    print("\nExercise 5: verify")
    root = try_or_sol("merkle_root", blocks)
    ok = try_or_sol("verify", blocks[3], p, root)
    check("valid proof verifies", ok, True)
    bad = try_or_sol("verify", "tx-fake", p, root)
    check("bad leaf rejected", bad, False)

    # Ex 6
    print("\nExercise 6: find_tampered_indices")
    old = ["a", "b", "c", "d"]
    new = ["a", "B", "c", "D"]
    idxs = try_or_sol("find_tampered_indices", old, new)
    check("indices 1 and 3", idxs, [1, 3])
    check("same content -> empty",
          try_or_sol("find_tampered_indices", old, old), [])

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
