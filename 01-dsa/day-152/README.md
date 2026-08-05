# Day 152: Fast Fourier Transform (Cooley-Tukey)

## Why It Matters

The FFT is the most important algorithm of the 20th century after sorting.
It collapses an O(n²) operation into O(n log n) and unlocks:

- **Audio/image processing**: spectrum analysis, MP3/JPEG, filtering.
- **Polynomial multiplication in O(n log n)** — used by big-integer
  multiplication in GMP, Python's `int.__mul__` (over ~1000 digits), and
  competitive programming.
- **Convolution** (signal filtering): convert "convolve" to "pointwise
  multiply in frequency", then convert back.
- **Number Theoretic Transform (NTT)**: the FFT's modular cousin —
  used in lattice cryptography (Kyber, Dilithium).

## The Discrete Fourier Transform (DFT)

Given a vector `a[0..n-1]`, the DFT produces `A[0..n-1]` defined by

```
A[k] = sum_{j=0..n-1}  a[j] * w^(j*k),   w = e^(-2*pi*i/n)  (n-th root of unity)
```

Direct evaluation = O(n²). The FFT reduces it to O(n log n) by exploiting
algebraic structure in the powers of `w`.

## Cooley-Tukey Radix-2 (Decimation in Time)

Assume `n` is a power of two. Split `a` into even/odd indices:

```
a_even[k] = a[2k]
a_odd[k]  = a[2k+1]
```

Then:

```
A[k]       = E[k] + w^k * O[k]
A[k + n/2] = E[k] - w^k * O[k]      (for k = 0..n/2-1)
```

This is the **butterfly**. Each level of the recursion halves the problem
size. log2(n) levels × n work per level = **O(n log n)**.

### Iterative Form (Bit-reversal Permutation)

Recursion is clean but slow. Production FFT does it iteratively:

1. **Bit-reverse permute** the input array. After reversal, the order
   matches what the recursion produces at the leaves.
2. **Butterfly stages**: for each block size `m = 2, 4, 8, ..., n`,
   combine pairs of size `m/2` blocks using the butterfly.

```
for m = 2; m <= n; m *= 2:
    w_m = e^(-2*pi*i/m)
    for k = 0; k < n; k += m:
        w = 1
        for j = 0; j < m/2; j++:
            t = w * a[k + j + m/2]
            u = a[k + j]
            a[k + j]         = u + t
            a[k + j + m/2]   = u - t
            w *= w_m
```

In-place, O(n log n) time, O(n) space. The shape of modern FFT libraries.

## Inverse FFT

Same structure, but `w = e^(+2*pi*i/n)` (conjugate). Divide by n at end.

```
ifft(A) = conj(fft(conj(A))) / n
```

The conjugate trick lets you reuse the same code for both directions.

## Polynomial Multiplication via FFT

Two polynomials `p` (degree `d1`) and `q` (degree `d2`) multiply to a
polynomial of degree `d1 + d2`. Naive multiplication: O((d1+d2)²).

FFT-based:
1. Pad both to length `n >= d1 + d2 + 1`, rounded to a power of 2.
2. `P = fft(p)`, `Q = fft(q)`.
3. Pointwise multiply: `R[k] = P[k] * Q[k]`.
4. `r = ifft(R)` — the coefficients of the product.

Total: **O(n log n)**. For multiplying 10000-coefficient polynomials,
that's millions of ops instead of trillions.

## Why It Works (One Sentence)

Polynomials are determined by their values at enough points. Powers of
roots of unity are *exactly* the right set of points for fast
multipoint evaluation and interpolation.

## Floating Point: The Catch

FFT uses complex floats. Roundoff accumulates as O(eps * log n). For
typical coefficients up to ~10^15 and n up to 10^6, results are accurate
to single-digit ULPs — good enough for signal processing, not always
for integer arithmetic.

For *exact* integer convolution, use NTT (day 153).

## Failure Modes

1. **Non-power-of-two n**: classic Cooley-Tukey breaks. Pad to next
   power of 2, or use Bluestein/mixed-radix.
2. **Float precision loss**: integer answers from FFT can be off by 1
   or 2 from the true value if coefficients are large. Round at the end.
3. **Forgetting to divide by n in IFFT**: result is scaled by n.
4. **Bit-reversal off-by-one**: easy to write a buggy bit-reversal
   that fails only on certain sizes.
5. **Cache thrash**: large FFTs that don't fit in L2 are bandwidth-bound;
   real libraries (FFTW) use cache-oblivious or tiled algorithms.

## Complexity Summary

| Operation | Naive | FFT |
|-----------|-------|-----|
| DFT | O(n²) | O(n log n) |
| Polynomial multiply | O(n²) | O(n log n) |
| Convolution | O(n²) | O(n log n) |
| Big-integer multiply (>1000 digits) | O(n²) | O(n log n) |

## Real-World Usage

| System | Use |
|--------|-----|
| GMP / Python big int | FFT for very large multiplication |
| MP3 / Vorbis / AAC | Modified DCT (FFT cousin) |
| JPEG | Discrete Cosine Transform |
| Radar / sonar | Spectrum analysis |
| Software-defined radio | Frequency-domain filtering |
| Competitive programming | Polynomial convolution, string matching |

## Checkpoint Questions

1. The butterfly combines two half-FFTs. Why does it take only O(n)
   work *total* per recursion level, not O(n) per output?
2. Why must `n` be a power of two for radix-2? What does Bluestein do?
3. Show how bit-reversal permutation arises naturally from the recursive
   even/odd split.
4. The IFFT divides by `n`. Why? (Hint: orthogonality of roots of unity.)
5. Multiplying two 1000-digit integers via FFT — what's the round-off
   risk, and how do real libraries (e.g., GMP) mitigate it?
6. Why is FFT memory-bound for large `n` even though it is O(n log n)
   work? What is "cache-oblivious FFT"?
