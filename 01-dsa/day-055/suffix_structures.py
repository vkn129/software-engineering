"""
Day 55: Suffix Array and LCP Array
====================================
Suffix array: sorted array of all suffix start positions.
LCP array: longest common prefix between consecutive sorted suffixes.

Together they enable fast pattern matching, longest repeated substring,
distinct substring counting, and the Burrows-Wheeler Transform.

Run: python suffix_structures.py
"""


# ─── Suffix Array Construction ──────────────────────────────────────

def build_suffix_array(text):
    """
    Build suffix array using O(n log² n) prefix doubling.

    Idea: sort suffixes by their first 1 character, then first 2,
    then first 4, etc. At each step, use the previous ranking to
    compare pairs of halves in O(1).

    For production use, SA-IS algorithm builds in O(n).
    We use prefix doubling for clarity.
    """
    n = len(text)
    if n == 0:
        return []

    # Initial ranking: by single character
    sa = list(range(n))
    rank = [ord(c) for c in text]
    tmp = [0] * n

    k = 1
    while k < n:
        # Sort by (rank[i], rank[i + k]) — rank of two halves
        def compare_key(i):
            second = rank[i + k] if i + k < n else -1
            return (rank[i], second)

        sa.sort(key=compare_key)

        # Compute new ranks
        tmp[sa[0]] = 0
        for i in range(1, n):
            prev_key = (rank[sa[i - 1]], rank[sa[i - 1] + k] if sa[i - 1] + k < n else -1)
            curr_key = (rank[sa[i]], rank[sa[i] + k] if sa[i] + k < n else -1)
            tmp[sa[i]] = tmp[sa[i - 1]] + (0 if curr_key == prev_key else 1)

        rank = tmp[:]

        # Early termination: all ranks are unique
        if rank[sa[-1]] == n - 1:
            break
        k *= 2

    return sa


# ─── LCP Array (Kasai's Algorithm) ─────────────────────────────────

def build_lcp_array(text, sa):
    """
    Kasai's algorithm: build LCP array in O(n).

    LCP[i] = length of longest common prefix between
              text[sa[i]..] and text[sa[i-1]..]

    Key insight: if LCP between suffix at position i and its predecessor
    is h, then the LCP for position i+1 is at least h-1. This prevents
    redundant comparisons and ensures O(n) total.
    """
    n = len(text)
    rank = [0] * n
    lcp = [0] * n

    # Build inverse suffix array (rank[i] = position of suffix i in SA)
    for i in range(n):
        rank[sa[i]] = i

    h = 0  # Current LCP length
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]  # Previous suffix in sorted order
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1  # Key insight: next LCP is at least h-1
        else:
            h = 0

    return lcp


# ─── Pattern Search ────────────────────────────────────────────────

def search_pattern(text, sa, pattern):
    """
    Find all occurrences of pattern in text using binary search on SA.
    Returns list of starting positions. O(m log n) where m = |pattern|.
    """
    n = len(text)
    m = len(pattern)

    # Binary search for lower bound
    lo, hi = 0, n - 1
    left = n
    while lo <= hi:
        mid = (lo + hi) // 2
        suffix = text[sa[mid]:sa[mid] + m]
        if suffix < pattern:
            lo = mid + 1
        else:
            left = mid
            hi = mid - 1

    # Binary search for upper bound
    lo, hi = 0, n - 1
    right = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        suffix = text[sa[mid]:sa[mid] + m]
        if suffix > pattern:
            hi = mid - 1
        else:
            right = mid
            lo = mid + 1

    if left > right:
        return []

    return sorted(sa[left:right + 1])


# ─── Longest Repeated Substring ────────────────────────────────────

def longest_repeated_substring(text):
    """
    Find the longest substring that appears at least twice.
    = suffix at SA[i] where LCP[i] is maximum.
    """
    if len(text) <= 1:
        return ""

    sa = build_suffix_array(text)
    lcp = build_lcp_array(text, sa)

    max_lcp = 0
    max_idx = 0
    for i in range(1, len(lcp)):
        if lcp[i] > max_lcp:
            max_lcp = lcp[i]
            max_idx = i

    if max_lcp == 0:
        return ""
    return text[sa[max_idx]:sa[max_idx] + max_lcp]


# ─── Count Distinct Substrings ─────────────────────────────────────

def count_distinct_substrings(text):
    """
    Count distinct non-empty substrings.
    Total possible = n*(n+1)/2
    Duplicates = sum(LCP)
    Distinct = n*(n+1)/2 - sum(LCP)
    """
    n = len(text)
    if n == 0:
        return 0

    sa = build_suffix_array(text)
    lcp = build_lcp_array(text, sa)

    total = n * (n + 1) // 2
    duplicates = sum(lcp)
    return total - duplicates


# ─── Burrows-Wheeler Transform ─────────────────────────────────────

def bwt(text):
    """
    Compute BWT from suffix array.
    BWT[i] = text[sa[i] - 1] (character before each sorted suffix).
    If sa[i] == 0, wrap around to text[-1].

    BWT clusters similar characters together because sorted suffixes
    that share a prefix tend to be preceded by similar characters.
    """
    sa = build_suffix_array(text)
    return ''.join(text[sa[i] - 1] for i in range(len(text)))


def inverse_bwt(bwt_string):
    """
    Reconstruct original text from BWT.
    Uses the LF-mapping property.
    """
    n = len(bwt_string)
    if n == 0:
        return ""

    # Build table of (char, original_index) sorted by char (stable)
    table = sorted(range(n), key=lambda i: bwt_string[i])

    # Follow chain from the row where original ended (marked by $)
    idx = bwt_string.index('$') if '$' in bwt_string else 0
    result = []
    for _ in range(n):
        idx = table[idx]
        result.append(bwt_string[idx])

    return ''.join(result)


# ─── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 55: Suffix Array & LCP Array")
    print("=" * 60)

    text = "banana$"

    # Suffix Array
    sa = build_suffix_array(text)
    print(f"\nText: '{text}'")
    print(f"Suffix Array: {sa}")
    print(f"\nSorted suffixes:")
    for i, pos in enumerate(sa):
        print(f"  SA[{i}] = {pos}: '{text[pos:]}'")

    # LCP Array
    lcp = build_lcp_array(text, sa)
    print(f"\nLCP Array: {lcp}")
    for i in range(1, len(sa)):
        print(f"  LCP[{i}] = {lcp[i]}: '{text[sa[i]:sa[i] + lcp[i]]}' (between '{text[sa[i-1]:]}' and '{text[sa[i]:]}')")

    # Pattern Search
    print(f"\n--- Pattern Search ---")
    for pat in ["an", "na", "ban", "xyz"]:
        positions = search_pattern(text, sa, pat)
        print(f"  '{pat}' found at positions: {positions}")

    # Longest Repeated Substring
    print(f"\n--- Longest Repeated Substring ---")
    for s in ["banana$", "abcabc", "aabaa"]:
        print(f"  '{s}' → '{longest_repeated_substring(s)}'")

    # Distinct Substrings
    print(f"\n--- Distinct Substrings ---")
    for s in ["abc", "aaa", "banana$"]:
        print(f"  '{s}': {count_distinct_substrings(s)} distinct substrings")

    # BWT
    print(f"\n--- Burrows-Wheeler Transform ---")
    text = "banana$"
    b = bwt(text)
    print(f"  BWT('{text}') = '{b}'")
    reconstructed = inverse_bwt(b)
    print(f"  Inverse BWT = '{reconstructed}'")

    print("\n✓ All demos complete")
