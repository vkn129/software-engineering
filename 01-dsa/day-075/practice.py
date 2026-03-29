"""
Day 75 Practice: Locality-Sensitive Hashing Exercises

5 exercises covering MinHash, LSH banding, random projection, and streaming.
All pure Python 3, no external dependencies.
"""

import math
import random
from collections import defaultdict

from lsh import MinHash, LSHIndex, RandomProjectionLSH, shingle


# ---------------------------------------------------------------------------
# Exercise 1: Near-Duplicate Document Detection
# ---------------------------------------------------------------------------

def exercise_1_near_duplicate_detection():
    """
    Given 20 documents, find all pairs with Jaccard similarity > 0.5.
    Use MinHash + LSH banding instead of all-pairs comparison.
    """
    print("=" * 70)
    print("Exercise 1: Near-Duplicate Document Detection")
    print("=" * 70)

    # 20 documents with known similarities
    base_texts = [
        "the quick brown fox jumps over the lazy dog in the sunny park",
        "machine learning algorithms can process very large datasets efficiently",
        "the cat sat on the warm mat and watched the small birds outside",
        "quantum computing uses qubits for massively parallel computation tasks",
        "python is a very popular programming language for data science work",
    ]

    documents = {}
    rng = random.Random(42)

    # Create 4 variants of each base text (20 total)
    for i, base in enumerate(base_texts):
        words = base.split()
        documents[f"doc_{i*4}"] = base

        # Variant 1: swap 1-2 words
        w = words[:]
        idx = rng.randint(0, len(w) - 2)
        w[idx] = rng.choice(["big", "fast", "new", "old", "red"])
        documents[f"doc_{i*4+1}"] = ' '.join(w)

        # Variant 2: add a few words
        w = words[:]
        w.insert(rng.randint(0, len(w)), "really")
        w.insert(rng.randint(0, len(w)), "very")
        documents[f"doc_{i*4+2}"] = ' '.join(w)

        # Variant 3: remove a few words
        w = words[:]
        if len(w) > 6:
            for _ in range(2):
                w.pop(rng.randint(0, len(w) - 1))
        documents[f"doc_{i*4+3}"] = ' '.join(w)

    # Shingle all documents
    shingles = {doc_id: shingle(text, k=2) for doc_id, text in documents.items()}

    # --- Brute force ground truth ---
    doc_ids = sorted(documents.keys())
    threshold = 0.5
    true_similar = set()
    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):
            jac = MinHash.exact_jaccard(shingles[doc_ids[i]], shingles[doc_ids[j]])
            if jac > threshold:
                true_similar.add((doc_ids[i], doc_ids[j]))

    print(f"\n  Total documents: {len(documents)}")
    print(f"  Brute force comparisons: {len(doc_ids) * (len(doc_ids)-1) // 2}")
    print(f"  True similar pairs (Jaccard > {threshold}): {len(true_similar)}")

    # --- LSH approach ---
    num_perm = 128
    seed = 42
    minhashes = {}
    for doc_id in doc_ids:
        mh = MinHash(num_perm=num_perm, seed=seed)
        mh.add_set(shingles[doc_id])
        minhashes[doc_id] = mh

    # Use b=16, r=8 for threshold ~0.52
    lsh = LSHIndex(num_perm=num_perm, num_bands=16, num_rows=8, seed=seed)
    for doc_id in doc_ids:
        lsh.insert(doc_id, minhashes[doc_id])

    candidates = lsh.find_all_candidate_pairs()

    # Filter candidates by estimated similarity
    found_similar = set()
    for d1, d2 in candidates:
        est_jac = MinHash.jaccard(minhashes[d1], minhashes[d2])
        if est_jac > threshold:
            found_similar.add((d1, d2))

    tp = found_similar & true_similar
    fp = found_similar - true_similar
    fn = true_similar - found_similar

    print(f"\n  LSH candidate pairs: {len(candidates)}")
    print(f"  Pairs passing similarity filter: {len(found_similar)}")
    print(f"  True positives: {len(tp)}")
    print(f"  False positives: {len(fp)}")
    print(f"  False negatives: {len(fn)}")
    precision = len(tp) / len(found_similar) if found_similar else 0
    recall = len(tp) / len(true_similar) if true_similar else 0
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"\n  Comparisons saved: {len(doc_ids)*(len(doc_ids)-1)//2 - len(candidates)}"
          f" ({100*(1 - len(candidates)/(len(doc_ids)*(len(doc_ids)-1)//2)):.1f}%)")

    if fn:
        print(f"\n  Missed pairs (false negatives):")
        for d1, d2 in sorted(fn):
            exact = MinHash.exact_jaccard(shingles[d1], shingles[d2])
            print(f"    {d1} vs {d2}: exact Jaccard = {exact:.3f}")


# ---------------------------------------------------------------------------
# Exercise 2: MinHash Accuracy Measurement
# ---------------------------------------------------------------------------

def exercise_2_minhash_accuracy():
    """
    Compare estimated vs exact Jaccard similarity for sets with known overlaps.
    Measure how accuracy improves with more hash functions.
    """
    print("\n" + "=" * 70)
    print("Exercise 2: MinHash Accuracy vs Number of Permutations")
    print("=" * 70)

    universe_size = 1000
    set_size = 200
    rng = random.Random(42)

    # Create set pairs with known approximate overlaps
    target_similarities = [0.1, 0.3, 0.5, 0.7, 0.9]

    print(f"\n  Universe size: {universe_size}")
    print(f"  Set size: ~{set_size}")
    print(f"  Permutation counts tested: 16, 32, 64, 128, 256\n")

    perm_counts = [16, 32, 64, 128, 256]

    header = f"  {'Target J':>10} {'Exact J':>10}"
    for k in perm_counts:
        header += f" {'k='+str(k):>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    universe = list(range(universe_size))

    for target_sim in target_similarities:
        # Create two sets with approximately the target overlap
        # J = |intersect| / |union|
        # If both sets have size s, and overlap is o:
        # J = o / (2s - o)  =>  o = J * 2s / (1 + J)
        overlap_size = int(target_sim * 2 * set_size / (1 + target_sim))
        overlap_size = max(1, min(overlap_size, set_size))

        shared = rng.sample(universe, overlap_size)
        remaining = [x for x in universe if x not in set(shared)]

        only_a_size = set_size - overlap_size
        only_b_size = set_size - overlap_size
        only_a = rng.sample(remaining, min(only_a_size, len(remaining)))
        remaining2 = [x for x in remaining if x not in set(only_a)]
        only_b = rng.sample(remaining2, min(only_b_size, len(remaining2)))

        set_a = set(shared + only_a)
        set_b = set(shared + only_b)
        exact_j = MinHash.exact_jaccard(set_a, set_b)

        row = f"  {target_sim:>10.2f} {exact_j:>10.3f}"

        for num_perm in perm_counts:
            # Average over multiple trials for stable measurement
            errors = []
            for trial in range(20):
                seed = 42 + trial
                mh_a = MinHash(num_perm=num_perm, seed=seed).add_set(str(x) for x in set_a)
                mh_b = MinHash(num_perm=num_perm, seed=seed).add_set(str(x) for x in set_b)
                est_j = MinHash.jaccard(mh_a, mh_b)
                errors.append(abs(est_j - exact_j))
            mean_error = sum(errors) / len(errors)
            row += f" {mean_error:>10.4f}"

        print(row)

    # Theoretical error: std dev of MinHash estimate = sqrt(J(1-J)/k)
    print("\n  Theoretical std dev = sqrt(J*(1-J)/k):")
    row = f"  {'J=0.5':>10} {'theory':>10}"
    for k in perm_counts:
        std = math.sqrt(0.5 * 0.5 / k)
        row += f" {std:>10.4f}"
    print(row)
    print("\n  Observation: error decreases as ~1/sqrt(k), matching theory.")


# ---------------------------------------------------------------------------
# Exercise 3: Tune Banding Parameters
# ---------------------------------------------------------------------------

def exercise_3_tune_banding():
    """
    Show how false positive and false negative rates vary with b and r.
    Plot the S-curve for different configurations (text-based plot).
    """
    print("\n" + "=" * 70)
    print("Exercise 3: Banding Parameter Tuning (S-Curve Analysis)")
    print("=" * 70)

    num_perm = 128
    configs = [
        (2, 64,   "b=2,r=64  (very strict)"),
        (8, 16,   "b=8,r=16  (strict)"),
        (16, 8,   "b=16,r=8  (balanced)"),
        (32, 4,   "b=32,r=4  (permissive)"),
        (64, 2,   "b=64,r=2  (very permissive)"),
        (128, 1,  "b=128,r=1 (trivial: any match)"),
    ]

    # Print S-curves
    print("\n  Candidate probability P(s) = 1 - (1 - s^r)^b")
    print(f"\n  {'Similarity':>12}", end="")
    for _, _, label in configs:
        print(f" {label:>22}", end="")
    print()
    print("  " + "-" * (12 + 22 * len(configs)))

    similarities = [i / 20 for i in range(21)]  # 0.0 to 1.0 step 0.05
    for s in similarities:
        row = f"  {s:>12.2f}"
        for b, r, _ in configs:
            p = LSHIndex.candidate_probability(s, b, r)
            row += f" {p:>22.4f}"
        print(row)

    # Text-based visualization of S-curves
    print("\n  S-Curve Visualization (threshold marked with |):\n")
    width = 50
    for b, r, label in configs:
        thresh = (1.0 / b) ** (1.0 / r)
        print(f"  {label}")
        for s_val in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            p = LSHIndex.candidate_probability(s_val, b, r)
            bar_len = int(p * width)
            bar = "#" * bar_len + "." * (width - bar_len)
            marker = " <-- threshold" if abs(s_val - round(thresh, 1)) < 0.05 else ""
            print(f"    s={s_val:.1f} [{bar}] {p:.3f}{marker}")
        print()

    # Show false positive/negative rates for a specific threshold
    print("\n  Analysis: targeting Jaccard threshold = 0.5")
    print(f"  {'Config':>22} {'Threshold':>10} {'FP@0.3':>8} {'FP@0.4':>8} {'FN@0.6':>8} {'FN@0.7':>8}")
    for b, r, label in configs:
        thresh = (1.0 / b) ** (1.0 / r)
        fp_03 = LSHIndex.candidate_probability(0.3, b, r)
        fp_04 = LSHIndex.candidate_probability(0.4, b, r)
        fn_06 = 1 - LSHIndex.candidate_probability(0.6, b, r)
        fn_07 = 1 - LSHIndex.candidate_probability(0.7, b, r)
        print(f"  {label:>22} {thresh:>10.3f} {fp_03:>8.4f} {fp_04:>8.4f} {fn_06:>8.4f} {fn_07:>8.4f}")

    print("\n  Key insight: stricter configs (high r) reduce false positives but increase")
    print("  false negatives. The banding technique creates a sharp transition at the threshold,")
    print("  and we choose b,r to place that transition at our desired similarity cutoff.")


# ---------------------------------------------------------------------------
# Exercise 4: Image Similarity (Simplified)
# ---------------------------------------------------------------------------

def exercise_4_image_similarity():
    """
    Represent images as feature vectors, use random projection LSH
    to find similar images.

    We simulate image features as vectors where similar images have
    correlated features (e.g., color histograms, edge statistics).
    """
    print("\n" + "=" * 70)
    print("Exercise 4: Image Similarity with Random Projection LSH")
    print("=" * 70)

    dim = 64  # Simulated feature vector dimensionality
    rng = random.Random(42)

    # Simulate image categories with feature clusters
    categories = {
        "sunset": [rng.gauss(2, 0.5) if i < 20 else rng.gauss(-1, 0.5) for i in range(dim)],
        "ocean":  [rng.gauss(-1, 0.5) if i < 20 else rng.gauss(2, 0.5) if i < 40 else rng.gauss(0, 0.5) for i in range(dim)],
        "forest": [rng.gauss(0, 0.5) if i < 30 else rng.gauss(3, 0.5) if i < 50 else rng.gauss(-1, 0.5) for i in range(dim)],
        "city":   [rng.gauss(-2, 0.5) for i in range(dim)],
    }

    # Generate 10 images per category with noise
    images = {}
    image_labels = {}
    for cat, center in categories.items():
        for j in range(10):
            name = f"{cat}_{j}"
            vec = [c + rng.gauss(0, 0.5) for c in center]
            images[name] = vec
            image_labels[name] = cat

    print(f"\n  Total images: {len(images)}")
    print(f"  Categories: {list(categories.keys())}")
    print(f"  Feature dimensions: {dim}")

    # Build LSH index
    lsh = RandomProjectionLSH(dim=dim, num_bits=10, num_tables=10, seed=42)
    for name, vec in images.items():
        lsh.insert(name, vec)

    # Query examples
    queries = ["sunset_0", "ocean_3", "forest_7", "city_2"]
    print("\n  Query results (top 5 neighbors):")
    total_correct = 0
    total_retrieved = 0

    for query_name in queries:
        query_vec = images[query_name]
        query_cat = image_labels[query_name]
        results = lsh.query(query_vec, top_k=6)  # top 6 includes self
        # Remove self
        results = [(name, sim) for name, sim in results if name != query_name][:5]

        correct = sum(1 for name, _ in results if image_labels[name] == query_cat)
        total_correct += correct
        total_retrieved += len(results)

        print(f"\n    Query: {query_name} (category: {query_cat})")
        for name, sim in results:
            cat = image_labels[name]
            match = "OK" if cat == query_cat else "MISS"
            print(f"      {name:>12} ({cat:>8}): cosine={sim:.4f}  [{match}]")
        print(f"      Precision@5: {correct}/{len(results)}")

    overall_precision = total_correct / total_retrieved if total_retrieved else 0
    print(f"\n  Overall category precision@5: {overall_precision:.3f}")

    # Brute force comparison
    print("\n  Brute-force vs LSH comparison for 'sunset_0':")
    query_vec = images["sunset_0"]
    all_sims = [(name, RandomProjectionLSH.cosine_similarity(query_vec, vec))
                for name, vec in images.items() if name != "sunset_0"]
    all_sims.sort(key=lambda x: -x[1])
    brute_top5 = all_sims[:5]
    lsh_top5 = [(name, sim) for name, sim in lsh.query(query_vec, top_k=6) if name != "sunset_0"][:5]

    brute_set = {name for name, _ in brute_top5}
    lsh_set = {name for name, _ in lsh_top5}
    overlap = brute_set & lsh_set

    print(f"    Brute force top 5: {[n for n, _ in brute_top5]}")
    print(f"    LSH top 5:         {[n for n, _ in lsh_top5]}")
    print(f"    Overlap: {len(overlap)}/5 = recall@5 = {len(overlap)/5:.2f}")


# ---------------------------------------------------------------------------
# Exercise 5: Streaming Deduplication
# ---------------------------------------------------------------------------

def exercise_5_streaming_dedup():
    """
    Process items one at a time. Flag duplicates using LSH index.
    Simulates a real-world stream of articles where duplicates arrive over time.
    """
    print("\n" + "=" * 70)
    print("Exercise 5: Streaming Deduplication")
    print("=" * 70)

    # Simulate a stream of articles, some are near-duplicates
    base_articles = [
        "breaking news the stock market reached all time highs today as investors cheered economic data",
        "scientists discover new species of deep sea fish in the pacific ocean near hydrothermal vents",
        "the president signed a new climate bill into law today during a ceremony at the white house",
        "local sports team wins championship game in overtime thriller before packed stadium crowd",
        "tech company announces revolutionary new smartphone with advanced artificial intelligence features",
        "severe weather warning issued for coastal areas as hurricane approaches the eastern seaboard",
        "researchers develop promising new treatment for rare genetic disease affecting young children",
        "international space station crew completes record breaking spacewalk to repair solar panels",
    ]

    rng = random.Random(42)

    def create_variant(text, change_level):
        """Create a near-duplicate with controlled amount of change."""
        words = text.split()
        n_changes = max(1, int(len(words) * change_level))
        synonyms = ["big", "new", "good", "great", "fast", "small", "old",
                     "major", "key", "top", "latest", "recent", "important"]
        w = words[:]
        for _ in range(n_changes):
            idx = rng.randint(0, len(w) - 1)
            if rng.random() < 0.5:
                w[idx] = rng.choice(synonyms)
            else:
                w.insert(idx, rng.choice(synonyms))
        return ' '.join(w)

    # Build stream: originals + duplicates arriving later
    stream = []
    ground_truth = {}  # article_id -> original_id (None if original)

    # First, add originals
    for i, text in enumerate(base_articles):
        article_id = f"article_{len(stream)}"
        stream.append((article_id, text))
        ground_truth[article_id] = None  # original

    # Add near-duplicates scattered through the stream
    for i, text in enumerate(base_articles):
        # Each original gets 1-3 near-duplicates
        n_dupes = rng.randint(1, 3)
        for d in range(n_dupes):
            change = rng.uniform(0.05, 0.25)  # 5-25% words changed
            variant = create_variant(text, change)
            article_id = f"article_{len(stream)}"
            stream.append((article_id, variant))
            ground_truth[article_id] = f"article_{i}"  # links to original

    # Shuffle to simulate random arrival order
    rng.shuffle(stream)

    print(f"\n  Stream size: {len(stream)} articles")
    print(f"  Originals: {len(base_articles)}")
    print(f"  Near-duplicates: {len(stream) - len(base_articles)}")

    # Process stream
    num_perm = 128
    seed = 42
    lsh = LSHIndex(num_perm=num_perm, num_bands=16, num_rows=8, seed=seed)

    flagged_dupes = []
    seen = {}  # article_id -> minhash
    similarity_threshold = 0.4

    print(f"\n  Processing stream (similarity threshold: {similarity_threshold})...")
    print(f"  {'Article':>14} {'Status':>10} {'Best Match':>14} {'Similarity':>12} {'Correct':>8}")
    print("  " + "-" * 62)

    for article_id, text in stream:
        shingles_set = shingle(text, k=2)

        # Create MinHash for this article
        mh = MinHash(num_perm=num_perm, seed=seed)
        mh.add_set(shingles_set)

        # Query the index for candidates
        candidates = lsh.query(mh)

        # Check if any candidate is similar enough
        best_match = None
        best_sim = 0.0
        for cand_id in candidates:
            sim = MinHash.jaccard(mh, seen[cand_id])
            if sim > best_sim:
                best_sim = sim
                best_match = cand_id

        is_duplicate = best_sim > similarity_threshold
        is_actually_dupe = ground_truth[article_id] is not None
        correct = (is_duplicate == is_actually_dupe)

        status = "DUPLICATE" if is_duplicate else "NEW"
        match_str = best_match if best_match else "-"
        sim_str = f"{best_sim:.3f}" if best_match else "-"
        correct_str = "yes" if correct else "NO"

        print(f"  {article_id:>14} {status:>10} {match_str:>14} {sim_str:>12} {correct_str:>8}")

        if is_duplicate:
            flagged_dupes.append((article_id, best_match, best_sim))

        # Add to index regardless (some systems skip adding duplicates)
        lsh.insert(article_id, mh)
        seen[article_id] = mh

    # Summary statistics
    actual_dupes = {aid for aid, orig in ground_truth.items() if orig is not None}
    flagged_set = {aid for aid, _, _ in flagged_dupes}

    tp = len(flagged_set & actual_dupes)
    fp = len(flagged_set - actual_dupes)
    fn = len(actual_dupes - flagged_set)
    tn = len(stream) - tp - fp - fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n  --- Summary ---")
    print(f"  True positives:  {tp}")
    print(f"  False positives: {fp}")
    print(f"  False negatives: {fn}")
    print(f"  True negatives:  {tn}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")
    print(f"\n  In a real system, flagged duplicates would be reviewed or suppressed.")
    print(f"  The threshold and LSH parameters can be tuned based on tolerance for")
    print(f"  false positives vs false negatives.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    exercise_1_near_duplicate_detection()
    exercise_2_minhash_accuracy()
    exercise_3_tune_banding()
    exercise_4_image_similarity()
    exercise_5_streaming_dedup()
