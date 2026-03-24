# Day 9: GCD, Extended Euclidean -- Why These Matter for RSA

## Why This Exists

Every time you connect to a website over HTTPS, your browser and the server perform
a mathematical handshake that depends on finding the Greatest Common Divisor of two
numbers. The RSA cryptosystem -- which protects virtually all internet commerce --
requires computing "modular multiplicative inverses," which requires the Extended
Euclidean Algorithm. Without GCD, there is no secure internet.

But GCD is not just cryptography trivia. It appears everywhere:
- **Reducing fractions**: 6/8 becomes 3/4 by dividing by GCD(6,8) = 2
- **Hash table sizing**: choosing table sizes coprime to step sizes avoids clustering
- **Music theory**: rhythm patterns repeat at intervals determined by GCD
- **Pixel grids**: the number of grid cells a diagonal line crosses involves GCD

Euclid described this algorithm around 300 BCE, making it one of the oldest
algorithms still in daily use. Understanding it deeply means understanding a
2300-year-old idea that secures your bank account today.

## Theory (40 min)

### 1. What GCD Actually Means

GCD(a, b) is the largest positive integer that divides both a and b.

GCD(12, 8) = 4 because:
- Divisors of 12: {1, 2, 3, 4, 6, 12}
- Divisors of 8:  {1, 2, 4, 8}
- Common: {1, 2, 4} → largest is 4

The naive approach (enumerate all divisors) is O(min(a,b)). For cryptographic
numbers with 300+ digits, this is impossibly slow. We need something better.

### 2. The Euclidean Algorithm

Key insight: GCD(a, b) = GCD(b, a mod b).

Why? If d divides both a and b, then d also divides (a - kb) for any integer k.
Since a mod b = a - (a//b)*b, any common divisor of a and b is also a common
divisor of b and (a mod b). The argument works in reverse too, so the sets of
common divisors are identical.

This gives us a recursive algorithm that terminates when b = 0, at which point
GCD(a, 0) = a. Each step reduces the problem size, and the number of steps is
at most O(log(min(a,b))) -- specifically bounded by ~5 times the number of digits.

### 3. Bezout's Identity

For any integers a and b, there exist integers x and y such that:
    a*x + b*y = GCD(a, b)

This is not obvious. It says that the GCD can always be expressed as a linear
combination of a and b. The Extended Euclidean Algorithm finds x and y.

### 4. Extended Euclidean Algorithm

We augment the basic algorithm to track the coefficients x, y at each step.

Base case: GCD(a, 0) = a, so x=1, y=0 (since a*1 + 0*0 = a).

Recursive case: if we know GCD(b, a mod b) = b*x1 + (a mod b)*y1, then
since a mod b = a - (a//b)*b, we substitute:
    b*x1 + (a - (a//b)*b)*y1 = GCD
    a*y1 + b*(x1 - (a//b)*y1) = GCD

So: x = y1, y = x1 - (a//b)*y1.

### 5. Modular Multiplicative Inverse

The inverse of a modulo m is a number x such that: a*x ≡ 1 (mod m).

This inverse exists if and only if GCD(a, m) = 1 (they are coprime).

To find it: use Extended Euclidean to solve a*x + m*y = 1, then x mod m
is the inverse.

### 6. Connection to RSA

RSA key generation:
1. Choose two large primes p and q
2. Compute n = p*q
3. Compute φ(n) = (p-1)(q-1)
4. Choose public exponent e coprime to φ(n) (usually 65537)
5. Compute private exponent d = e⁻¹ mod φ(n) ← **this uses Extended Euclidean**

Without the modular inverse, step 5 is impossible, and RSA does not work.

## Practice (20 min)

Complete the exercises in `practice.py`:
1. Implement GCD (iterative and recursive)
2. Implement Extended GCD
3. Find modular multiplicative inverses
4. Build a simplified RSA key generator

## Daily Project

Build a working mini-RSA system with small primes. Generate keys, encrypt a number,
decrypt it. Verify that the math works end-to-end. See `gcd_euclidean.py`.

## Checkpoint Questions

1. Why does GCD(a, b) = GCD(b, a mod b)? Can you explain without looking at notes?
2. What is the time complexity of the Euclidean algorithm, and why?
3. When does a modular inverse NOT exist? Give an example.
4. In RSA, why must e and φ(n) be coprime?
5. If someone gives you GCD(a, b) = 7, what can you say about a*x + b*y = 3?
   (Answer: no integer solution exists, because 7 does not divide 3.)
