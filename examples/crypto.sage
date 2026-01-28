# Cryptography Examples for CTF
# Common cryptographic operations in SageMath

# =============================================================================
# RSA Basics
# =============================================================================

# Generate RSA parameters
p = next_prime(2^512)
q = next_prime(2^512 + 1000)
n = p * q
phi = (p - 1) * (q - 1)
e = 65537

# Compute private key
d = inverse_mod(e, phi)

print("=== RSA Parameters ===")
print(f"p = {p}")
print(f"q = {q}")
print(f"n = {n}")
print(f"e = {e}")
print(f"d = {d}")

# Encryption and Decryption
message = 12345678901234567890
ciphertext = power_mod(message, e, n)
decrypted = power_mod(ciphertext, d, n)

print(f"\nOriginal: {message}")
print(f"Encrypted: {ciphertext}")
print(f"Decrypted: {decrypted}")
print(f"Correct: {message == decrypted}")

# =============================================================================
# Discrete Logarithm
# =============================================================================

print("\n=== Discrete Logarithm ===")

# Small example for demonstration
p_small = 23
g = primitive_root(p_small)
print(f"Primitive root of {p_small}: {g}")

# Compute discrete log
h = power_mod(g, 7, p_small)
# For small values, we can compute discrete log
dlog = discrete_log(h, Mod(g, p_small))
print(f"discrete_log({h}, {g}) mod {p_small} = {dlog}")

# =============================================================================
# Elliptic Curves
# =============================================================================

print("\n=== Elliptic Curves ===")

# Define an elliptic curve over a finite field
p_ec = 2^256 - 2^32 - 977  # secp256k1 prime
F = GF(p_ec)
a, b = 0, 7
E = EllipticCurve(F, [a, b])

print(f"Curve: y^2 = x^3 + {a}x + {b}")
print(f"Order: {E.order()}")

# Point operations (using a smaller curve for speed)
E_small = EllipticCurve(GF(97), [2, 3])
G = E_small.random_point()
print(f"\nSmall curve point G: {G}")
print(f"2*G: {2*G}")
print(f"Order of G: {G.order()}")

# =============================================================================
# Lattice Cryptography
# =============================================================================

print("\n=== Lattice Operations ===")

# Create a lattice basis
B = matrix(ZZ, [[1, 2, 3], [4, 5, 6], [7, 8, 10]])
print(f"Original basis:\n{B}")

# LLL reduction
B_reduced = B.LLL()
print(f"LLL reduced basis:\n{B_reduced}")

# =============================================================================
# Polynomial Operations (for AES, etc.)
# =============================================================================

print("\n=== Finite Field Polynomials ===")

# AES field GF(2^8)
F256.<a> = GF(2^8, modulus=x^8 + x^4 + x^3 + x + 1)
print(f"AES field element: {a}")
print(f"a^254 (inverse of a): {a^254}")
print(f"Verification a * a^254: {a * a^254}")

# =============================================================================
# Chinese Remainder Theorem
# =============================================================================

print("\n=== Chinese Remainder Theorem ===")

remainders = [2, 3, 2]
moduli = [3, 5, 7]
solution = CRT(remainders, moduli)
print(f"x ≡ {remainders} (mod {moduli})")
print(f"Solution: x = {solution}")

# Verify
for r, m in zip(remainders, moduli):
    print(f"  {solution} mod {m} = {solution % m} (expected {r})")

# =============================================================================
# Hash and Encoding Utilities
# =============================================================================

print("\n=== Encoding Utilities ===")

# Integer to bytes and back
msg_int = 0x48656c6c6f  # "Hello" in hex
msg_bytes = Integer(msg_int).digits(256)
print(f"Integer: {hex(msg_int)}")
print(f"Bytes: {msg_bytes}")

# Bytes to string
text = ''.join(chr(b) for b in reversed(msg_bytes))
print(f"Text: {text}")
