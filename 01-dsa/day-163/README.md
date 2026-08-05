# Day 163: Merkle Trees

## Why Merkle Trees Exist

Problem: "Prove that a single record belongs to a 10-million-row dataset
without sending all 10 million rows."

Or: "Two replicas disagree about a billion keys. Find the differences
without comparing them all."

Or: "I have a 4 GB file. Prove a 1 KB chunk is unmodified."

Hashing alone is not enough: a flat hash of the whole dataset proves
nothing about an individual element. Merkle trees solve this with
**logarithmic proofs**.

## Construction

```
                    root
                   /    \
                h(AB)    h(CD)
               /    \    /    \
             h(A)  h(B) h(C)  h(D)
              |     |    |     |
              A     B    C     D
```

1. Hash every leaf.
2. Hash pairs of adjacent leaves -> parent.
3. Repeat until one root remains.

For N leaves, tree depth = `ceil(log2(N))`. Storage = `O(N)` nodes.

**Odd numbers**: duplicate the last leaf (Bitcoin's choice) or carry it up
(Certificate Transparency's choice). Both work; mixing them across
implementations causes interop bugs.

## Inclusion Proof (Merkle Path)

To prove element X is in the tree at index i:
- Send the sibling hash at each level (`log2(N)` hashes)
- Verifier rebuilds the path: combine X's hash with each sibling,
  alternating left/right based on i's bit at that level.
- If the recomputed root matches the trusted root, X is in.

**Size**: 32 bytes (sha256) * log2(N). For N=1 billion, proof = ~960 bytes.
Compare to sending all 1 billion records.

## Why Git Uses Them

A Git commit is a Merkle tree root over the entire repository state:
- Blobs (file contents) are leaves
- Tree objects (directories) are inner nodes
- Commit object pins the tree root

```
git log shows commit hashes — each is the root of a Merkle DAG.
```

Consequences:
- Two commits with identical content have identical hashes.
- Tampering with any file changes its blob hash, which changes its tree
  hash, which changes the commit hash — visible everywhere.
- Sub-tree sharing across commits: unchanged directories reuse the same
  hash, so storage stays small.

## Why Bitcoin Uses Them

Each block header contains a Merkle root of all transactions in the
block. A light client (mobile wallet) wants to know "did transaction T
get included in block B?" without downloading B's 2 MB of transactions.

The full node sends `log2(N)` hashes (a Merkle proof). The light client
combines them with hash(T) and checks the result against the trusted
block header. This is **SPV** — Simplified Payment Verification.

For 2000 transactions per block: proof = 11 * 32 = 352 bytes.

## Other Real Systems

| System | Use |
|--------|-----|
| **Cassandra / DynamoDB anti-entropy** | Compare Merkle trees of replica ranges. Mismatched subtrees identify which keys to repair. |
| **IPFS / Filecoin** | Content-addressed storage; every object is a Merkle DAG node. |
| **Certificate Transparency** | Append-only logs of issued TLS certs; auditors verify inclusion in `log(N)` time. |
| **ZFS / btrfs** | Block checksums roll up into per-file Merkle trees for silent corruption detection. |
| **Ethereum state trie** | Merkle Patricia trie — variant for sparse keyspaces. |

## Failure Modes

1. **Second-preimage attack**: if leaf and inner-node hashes use the same
   domain, an attacker can claim a 2-leaf subtree is a single leaf with
   the same hash. Mitigate by domain-separating: `H(0x00 || leaf)` for
   leaves, `H(0x01 || left || right)` for inner nodes. RFC 6962
   (Certificate Transparency) does this; Bitcoin does not — and there's
   a real vulnerability class around it.

2. **Length-extension on misused hash**: SHA-256 plain `H(left || right)`
   is fine because both halves are fixed-length. Don't try this with
   variable-length serialization.

3. **Odd-leaf rule mismatch**: as above — Bitcoin duplicates, CT carries
   up. Pick one and stick with it.

## Checkpoint Questions

1. What's the size of an inclusion proof for N=1024 leaves? For N=1 trillion?
2. Why does domain separation between leaf and inner hashes matter?
3. In Cassandra anti-entropy, why compare Merkle roots before comparing
   subtrees?
4. Sketch how Git knows a directory hasn't changed across two commits.
5. SPV clients trust block headers but not transactions. What does the
   Merkle proof give them that the header alone does not?
6. How would you make a Merkle tree append-friendly without rebuilding
   the entire tree on each insert?
