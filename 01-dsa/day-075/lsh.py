"""
Day 75: Locality-Sensitive Hashing (LSH)

Three implementations:
1. MinHash — estimates Jaccard similarity between sets
2. LSHIndex — banding technique for near-duplicate detection
3. RandomProjectionLSH — cosine similarity via random hyperplanes

No external dependencies. Pure Python 3.
"""

import hashlib
import math
import random
import struct
from collections import defaultdict


# ---------------------------------------------------------------------------
# MinHash: Jaccard similarity estimation
# ---------------------------------------------------------------------------

class MinHash:
    """
    MinHash signature for a set.

    Why it works: for a random hash function h, the probability that two sets
    A and B have the same minimum hash value equals their Jaccard similarity.
    Using k independent hash functions gives a k-dimensional signature whose
    agreement fraction estimates J(A, B).
    """

    _MERSENNE_PRIME = (1 << 61) - 1  # Large prime for universal hashing
    _MAX_HASH = (1 << 32) - 1

    def __init__(self, num_perm=128, seed=42):
        self.num_perm = num_perm
        self.hashvalues = [self._MAX_HASH] * num_perm
        # Generate random hash function coefficients: h(x) = (a*x + b) mod p
        rng = random.Random(seed)
        self._a = [rng.randint(1, self._MERSENNE_PRIME - 1) for _ in range(num_perm)]
        self._b = [rng.randint(0, self._MERSENNE_PRIME - 1) for _ in range(num_perm)]

    def _hash_token(self, token):
        """Hash a token (string or int) to a 32-bit integer."""
        if isinstance(token, int):
            token = str(token)
        h = hashlib.sha1(token.encode('utf-8')).digest()
        # Take first 4 bytes as uint32
        return struct.unpack('<I', h[:4])[0]

    def update(self, token):
        """Add a single element to the set."""
        hv = self._hash_token(token)
        for i in range(self.num_perm):
            # Universal hash: (a * x + b) mod p mod 2^32
            val = ((self._a[i] * hv + self._b[i]) % self._MERSENNE_PRIME) & self._MAX_HASH
            if val < self.hashvalues[i]:
                self.hashvalues[i] = val

    def add_set(self, items):
        """Convenience: add all items from an iterable."""
        for item in items:
            self.update(item)
        return self

    @staticmethod
    def jaccard(mh1, mh2):
        """Estimate Jaccard similarity from two MinHash signatures."""
        if mh1.num_perm != mh2.num_perm:
            raise ValueError("Signatures must have same number of permutations")
        matches = sum(1 for a, b in zip(mh1.hashvalues, mh2.hashvalues) if a == b)
        return matches / mh1.num_perm

    @staticmethod
    def exact_jaccard(set_a, set_b):
        """Compute exact Jaccard similarity for comparison."""
        a, b = set(set_a), set(set_b)
        if not a and not b:
            return 1.0
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# LSHIndex: Banding technique for near-duplicate detection
# ---------------------------------------------------------------------------

class LSHIndex:
    """
    LSH index using the banding technique over MinHash signatures.

    Divides a signature of length num_perm into b bands of r rows.
    Two items are candidate pairs if they agree on ALL r rows in ANY band.

    P(candidate | similarity s) = 1 - (1 - s^r)^b

    This creates a steep S-curve: items above the threshold are almost
    always found, items below are almost always filtered out.
    """

    def __init__(self, num_perm=128, num_bands=None, num_rows=None, seed=42):
        """
        Configure the LSH index.

        Must satisfy: num_bands * num_rows == num_perm.
        If only num_bands is given, num_rows = num_perm // num_bands.
        If neither given, we pick a default that gives a threshold around 0.5.
        """
        self.num_perm = num_perm
        self.seed = seed

        if num_bands and num_rows:
            if num_bands * num_rows > num_perm:
                raise ValueError(f"b*r={num_bands*num_rows} > num_perm={num_perm}")
            self.num_bands = num_bands
            self.num_rows = num_rows
        elif num_bands:
            self.num_rows = num_perm // num_bands
            self.num_bands = num_bands
        elif num_rows:
            self.num_bands = num_perm // num_rows
            self.num_rows = num_rows
        else:
            # Default: aim for threshold ~0.5
            # threshold ~ (1/b)^(1/r). For b=16, r=8: ~0.52
            self.num_bands = 16
            self.num_rows = num_perm // 16

        # Each band has its own hash table: band_idx -> {bucket_hash -> set of doc_ids}
        self.tables = [defaultdict(set) for _ in range(self.num_bands)]
        self.signatures = {}  # doc_id -> MinHash

    def _get_band(self, signature, band_idx):
        """Extract band from signature and return a hashable bucket key."""
        start = band_idx * self.num_rows
        end = start + self.num_rows
        band = tuple(signature[start:end])
        return band

    def insert(self, doc_id, minhash):
        """Index a document by its MinHash signature."""
        self.signatures[doc_id] = minhash
        sig = minhash.hashvalues
        for band_idx in range(self.num_bands):
            bucket_key = self._get_band(sig, band_idx)
            self.tables[band_idx][bucket_key].add(doc_id)

    def query(self, minhash):
        """Find candidate near-neighbors for a query MinHash."""
        candidates = set()
        sig = minhash.hashvalues
        for band_idx in range(self.num_bands):
            bucket_key = self._get_band(sig, band_idx)
            candidates.update(self.tables[band_idx].get(bucket_key, set()))
        return candidates

    def find_all_candidate_pairs(self):
        """Find all candidate pairs across the entire index."""
        pairs = set()
        for band_idx in range(self.num_bands):
            for bucket, doc_ids in self.tables[band_idx].items():
                doc_list = sorted(doc_ids)
                for i in range(len(doc_list)):
                    for j in range(i + 1, len(doc_list)):
                        pairs.add((doc_list[i], doc_list[j]))
        return pairs

    def threshold(self):
        """
        The approximate similarity threshold for this b,r configuration.
        Items above this similarity have >50% chance of being candidates.
        """
        return (1.0 / self.num_bands) ** (1.0 / self.num_rows)

    @staticmethod
    def candidate_probability(similarity, num_bands, num_rows):
        """P(candidate) = 1 - (1 - s^r)^b"""
        return 1.0 - (1.0 - similarity ** num_rows) ** num_bands


# ---------------------------------------------------------------------------
# RandomProjectionLSH: Cosine similarity
# ---------------------------------------------------------------------------

class RandomProjectionLSH:
    """
    LSH for cosine similarity using random hyperplanes.

    Each hash bit: project vector onto a random normal vector, take the sign.
    P(same bit) = 1 - angle(u,v) / pi

    Multiple hash tables (each with num_bits random projections) increase recall.
    """

    def __init__(self, dim, num_bits=16, num_tables=5, seed=42):
        """
        Args:
            dim: dimensionality of input vectors
            num_bits: bits per hash (more bits = more precision, less recall per table)
            num_tables: number of hash tables (more tables = higher recall)
        """
        self.dim = dim
        self.num_bits = num_bits
        self.num_tables = num_tables

        rng = random.Random(seed)
        # Random hyperplanes: num_tables sets of num_bits random vectors
        self.hyperplanes = []
        for _ in range(num_tables):
            planes = []
            for _ in range(num_bits):
                # Random normal vector (Box-Muller approximation via central limit)
                vec = [rng.gauss(0, 1) for _ in range(dim)]
                planes.append(vec)
            self.hyperplanes.append(planes)

        # Hash tables: table_idx -> {hash_key -> set of (item_id, vector)}
        self.tables = [defaultdict(list) for _ in range(num_tables)]
        self.items = {}  # item_id -> vector

    def _hash_vector(self, vec, table_idx):
        """Compute hash for a vector using the given table's hyperplanes."""
        bits = []
        for plane in self.hyperplanes[table_idx]:
            dot = sum(v * p for v, p in zip(vec, plane))
            bits.append(1 if dot >= 0 else 0)
        return tuple(bits)

    def insert(self, item_id, vector):
        """Add a vector to the index."""
        if len(vector) != self.dim:
            raise ValueError(f"Expected dim={self.dim}, got {len(vector)}")
        self.items[item_id] = vector
        for t in range(self.num_tables):
            h = self._hash_vector(vector, t)
            self.tables[t][h].append(item_id)

    def query(self, vector, top_k=10):
        """
        Find approximate nearest neighbors by cosine similarity.
        Returns list of (item_id, cosine_similarity) sorted by similarity descending.
        """
        candidates = set()
        for t in range(self.num_tables):
            h = self._hash_vector(vector, t)
            for item_id in self.tables[t].get(h, []):
                candidates.add(item_id)

        # Rank candidates by actual cosine similarity
        results = []
        for item_id in candidates:
            sim = self.cosine_similarity(vector, self.items[item_id])
            results.append((item_id, sim))
        results.sort(key=lambda x: -x[1])
        return results[:top_k]

    @staticmethod
    def cosine_similarity(a, b):
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def estimated_cosine_from_hash_agreement(agreement_fraction):
        """
        Given the fraction of hash bits that agree, estimate cosine similarity.
        agreement = 1 - angle/pi  =>  angle = pi * (1 - agreement)
        cosine = cos(angle)
        """
        angle = math.pi * (1.0 - agreement_fraction)
        return math.cos(angle)


# ---------------------------------------------------------------------------
# Shingling helper
# ---------------------------------------------------------------------------

def shingle(text, k=3):
    """
    Convert text to a set of k-character shingles (k-grams).

    Why k-grams? They capture local word order. Two documents with
    similar sentences will share many k-grams, giving high Jaccard similarity.
    k=3 words or k=5-9 characters are common choices.
    """
    text = text.lower().strip()
    words = text.split()
    if len(words) < k:
        return {text}
    return {' '.join(words[i:i+k]) for i in range(len(words) - k + 1)}


# ---------------------------------------------------------------------------
# Demo: detect similar documents
# ---------------------------------------------------------------------------

def demo_document_similarity():
    """
    Demonstrate near-duplicate detection on a small corpus.
    Shows how MinHash + LSH finds similar documents efficiently.
    """
    print("=" * 70)
    print("DEMO: Near-Duplicate Document Detection with MinHash + LSH")
    print("=" * 70)

    documents = {
        "doc1": "The quick brown fox jumps over the lazy dog in the park",
        "doc2": "The quick brown fox leaps over the lazy dog in the garden",  # ~similar to doc1
        "doc3": "A fast brown fox jumps over a lazy dog in the park",         # ~similar to doc1
        "doc4": "Machine learning algorithms process large datasets efficiently",
        "doc5": "Deep learning algorithms process large datasets very efficiently", # ~similar to doc4
        "doc6": "The cat sat on the mat and watched the birds outside",
        "doc7": "The cat sat on the rug and watched the birds fly outside",    # ~similar to doc6
        "doc8": "Quantum computing uses qubits for parallel computation",
        "doc9": "Python is a popular programming language for data science",
        "doc10": "The quick brown fox jumps over the lazy dog in the park today", # ~similar to doc1
    }

    # Step 1: Shingle documents
    print("\n--- Step 1: Shingling (k=3 word shingles) ---")
    shingles = {}
    for doc_id, text in documents.items():
        shingles[doc_id] = shingle(text, k=3)
        print(f"  {doc_id}: {len(shingles[doc_id])} shingles")

    # Step 2: Compute exact Jaccard for ground truth
    print("\n--- Step 2: Exact Jaccard similarities (ground truth) ---")
    doc_ids = sorted(documents.keys())
    exact_pairs = {}
    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):
            jac = MinHash.exact_jaccard(shingles[doc_ids[i]], shingles[doc_ids[j]])
            if jac > 0.1:
                exact_pairs[(doc_ids[i], doc_ids[j])] = jac
                print(f"  {doc_ids[i]} vs {doc_ids[j]}: {jac:.3f}")

    # Step 3: Build MinHash signatures
    print("\n--- Step 3: MinHash signatures (128 permutations) ---")
    num_perm = 128
    seed = 42
    minhashes = {}
    for doc_id in doc_ids:
        mh = MinHash(num_perm=num_perm, seed=seed)
        mh.add_set(shingles[doc_id])
        minhashes[doc_id] = mh

    # Show estimated vs exact for interesting pairs
    print("  Estimated vs exact Jaccard for similar pairs:")
    for (d1, d2), exact_j in sorted(exact_pairs.items(), key=lambda x: -x[1]):
        est_j = MinHash.jaccard(minhashes[d1], minhashes[d2])
        error = abs(est_j - exact_j)
        print(f"    {d1} vs {d2}: exact={exact_j:.3f}  estimated={est_j:.3f}  error={error:.3f}")

    # Step 4: LSH index with banding
    print("\n--- Step 4: LSH with banding (b=16, r=8) ---")
    num_bands = 16
    num_rows = num_perm // num_bands
    lsh = LSHIndex(num_perm=num_perm, num_bands=num_bands, num_rows=num_rows, seed=seed)
    print(f"  Approximate similarity threshold: {lsh.threshold():.3f}")

    for doc_id in doc_ids:
        lsh.insert(doc_id, minhashes[doc_id])

    candidates = lsh.find_all_candidate_pairs()
    print(f"\n  Candidate pairs found by LSH: {len(candidates)}")
    for d1, d2 in sorted(candidates):
        est_j = MinHash.jaccard(minhashes[d1], minhashes[d2])
        exact_j = MinHash.exact_jaccard(shingles[d1], shingles[d2])
        print(f"    {d1} vs {d2}: exact={exact_j:.3f}  estimated={est_j:.3f}")

    # Step 5: Precision/recall analysis
    print("\n--- Step 5: Precision/Recall trade-offs ---")
    threshold = 0.3
    true_pairs = {pair for pair, jac in exact_pairs.items() if jac >= threshold}
    print(f"  Similarity threshold: {threshold}")
    print(f"  True similar pairs (exact Jaccard >= {threshold}): {len(true_pairs)}")
    print(f"  Candidate pairs from LSH: {len(candidates)}")

    # Candidates that are truly similar
    true_positives = candidates & true_pairs
    false_positives = candidates - true_pairs
    false_negatives = true_pairs - candidates

    precision = len(true_positives) / len(candidates) if candidates else 0
    recall = len(true_positives) / len(true_pairs) if true_pairs else 0

    print(f"  True positives: {len(true_positives)}")
    print(f"  False positives: {len(false_positives)}")
    print(f"  False negatives: {len(false_negatives)}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")

    # Step 6: Show effect of different b, r configurations
    print("\n--- Step 6: Effect of band/row configuration ---")
    configs = [
        (4, 32),    # Very selective: high threshold
        (8, 16),    # Moderately selective
        (16, 8),    # Balanced
        (32, 4),    # More permissive
        (64, 2),    # Very permissive: low threshold
    ]

    print(f"  {'b':>4} {'r':>4} {'threshold':>10} {'candidates':>12} {'precision':>10} {'recall':>8}")
    for b, r in configs:
        idx = LSHIndex(num_perm=num_perm, num_bands=b, num_rows=r, seed=seed)
        for doc_id in doc_ids:
            idx.insert(doc_id, minhashes[doc_id])
        cands = idx.find_all_candidate_pairs()
        tp = cands & true_pairs
        prec = len(tp) / len(cands) if cands else 0
        rec = len(tp) / len(true_pairs) if true_pairs else 0
        thresh = idx.threshold()
        print(f"  {b:>4} {r:>4} {thresh:>10.3f} {len(cands):>12} {prec:>10.3f} {rec:>8.3f}")


def demo_cosine_lsh():
    """Demonstrate random projection LSH for cosine similarity."""
    print("\n" + "=" * 70)
    print("DEMO: Random Projection LSH for Cosine Similarity")
    print("=" * 70)

    dim = 50
    rng = random.Random(123)

    # Create clusters of similar vectors
    def make_cluster(center, n, noise=0.1):
        vectors = []
        for _ in range(n):
            vec = [c + rng.gauss(0, noise) for c in center]
            vectors.append(vec)
        return vectors

    center1 = [rng.gauss(0, 1) for _ in range(dim)]
    center2 = [rng.gauss(0, 1) for _ in range(dim)]
    center3 = [rng.gauss(0, 1) for _ in range(dim)]

    cluster1 = make_cluster(center1, 10, noise=0.3)
    cluster2 = make_cluster(center2, 10, noise=0.3)
    cluster3 = make_cluster(center3, 10, noise=0.3)

    # Build index
    lsh = RandomProjectionLSH(dim=dim, num_bits=12, num_tables=8, seed=42)
    all_vectors = []
    for i, vec in enumerate(cluster1 + cluster2 + cluster3):
        label = f"c{i // 10 + 1}_{i % 10}"
        lsh.insert(label, vec)
        all_vectors.append((label, vec))

    # Query with a vector from cluster 1
    print("\n  Query: vector from cluster 1 (c1_0)")
    query_vec = cluster1[0]
    results = lsh.query(query_vec, top_k=10)
    print(f"  Top 10 nearest neighbors:")
    for item_id, sim in results:
        cluster = item_id.split('_')[0]
        print(f"    {item_id} (cluster {cluster}): cosine_sim = {sim:.4f}")

    # Query with a vector from cluster 2
    print("\n  Query: vector from cluster 2 (c2_0)")
    query_vec = cluster2[0]
    results = lsh.query(query_vec, top_k=10)
    print(f"  Top 10 nearest neighbors:")
    for item_id, sim in results:
        cluster = item_id.split('_')[0]
        print(f"    {item_id} (cluster {cluster}): cosine_sim = {sim:.4f}")

    # Compare LSH recall vs brute force
    print("\n  Recall analysis (cluster 1 query):")
    query_vec = cluster1[0]
    lsh_results = {item_id for item_id, _ in lsh.query(query_vec, top_k=10)}

    # Brute force top 10
    all_sims = [(label, RandomProjectionLSH.cosine_similarity(query_vec, vec))
                for label, vec in all_vectors if label != "c1_0"]
    all_sims.sort(key=lambda x: -x[1])
    brute_top10 = {label for label, _ in all_sims[:10]}

    overlap = lsh_results & brute_top10
    recall = len(overlap) / len(brute_top10)
    print(f"  LSH found {len(lsh_results)} candidates, {len(overlap)} in true top-10")
    print(f"  Recall@10: {recall:.2f}")


if __name__ == "__main__":
    demo_document_similarity()
    demo_cosine_lsh()
