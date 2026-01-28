# Basic SageMath Examples
# This file demonstrates basic SageMath syntax and features

# =============================================================================
# Variables and Symbolic Computation
# =============================================================================

# Define symbolic variables
x, y, z = var('x y z')

# Basic arithmetic
result = 2 + 3 * 4 - 1
print(f"Basic arithmetic: {result}")

# Symbolic expressions
expr = x^2 + 2*x*y + y^2
expanded = expand(expr)
factored = factor(expr)
print(f"Expression: {expr}")
print(f"Factored: {factored}")

# =============================================================================
# Calculus
# =============================================================================

# Differentiation
f = x^3 + 2*x^2 - x + 1
df = diff(f, x)
print(f"f(x) = {f}")
print(f"f'(x) = {df}")

# Integration
integral_f = integrate(f, x)
print(f"Integral of f(x) = {integral_f}")

# Definite integral
definite = integrate(x^2, x, 0, 1)
print(f"Integral from 0 to 1 of x^2 = {definite}")

# =============================================================================
# Linear Algebra
# =============================================================================

# Matrix creation
M = matrix([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
print(f"Matrix M:\n{M}")

# Matrix operations
det_M = M.det()
inv_M = M.inverse()
print(f"Determinant: {det_M}")
print(f"Inverse:\n{inv_M}")

# Eigenvalues
eigenvalues = M.eigenvalues()
print(f"Eigenvalues: {eigenvalues}")

# =============================================================================
# Number Theory
# =============================================================================

# Prime numbers
p = next_prime(100)
print(f"Next prime after 100: {p}")

# Factorization
n = 12345678
factors = factor(n)
print(f"Factorization of {n}: {factors}")

# GCD and LCM
a, b = 48, 180
print(f"GCD({a}, {b}) = {gcd(a, b)}")
print(f"LCM({a}, {b}) = {lcm(a, b)}")

# =============================================================================
# Polynomial Rings
# =============================================================================

# Define polynomial ring
R.<t> = PolynomialRing(QQ)
p = t^4 - 1
roots = p.roots()
print(f"Polynomial: {p}")
print(f"Roots in QQ: {roots}")

# Factorization over different fields
print(f"Factored over QQ: {factor(p)}")

# =============================================================================
# Functions and Control Flow
# =============================================================================

def fibonacci(n):
    """Compute the n-th Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# List comprehension
fib_list = [fibonacci(i) for i in range(10)]
print(f"First 10 Fibonacci numbers: {fib_list}")

# Conditional
for i in range(2, 20):
    if is_prime(i):
        print(f"{i} is prime")
