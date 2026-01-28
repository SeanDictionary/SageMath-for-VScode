# Algebraic Computations in SageMath

# =============================================================================
# Polynomial Arithmetic
# =============================================================================

print("=== Polynomial Arithmetic ===")

# Define polynomial ring over rationals
R.<x> = PolynomialRing(QQ)

# Basic polynomials
f = x^4 - 5*x^2 + 4
g = x^2 - 1

print(f"f(x) = {f}")
print(f"g(x) = {g}")

# Operations
print(f"f + g = {f + g}")
print(f"f * g = {f * g}")
print(f"f / g = {f.quo_rem(g)}")  # quotient and remainder

# GCD of polynomials
h = gcd(f, g)
print(f"gcd(f, g) = {h}")

# Factorization
print(f"factor(f) = {factor(f)}")

# =============================================================================
# Solving Equations
# =============================================================================

print("\n=== Solving Equations ===")

# Symbolic variables
x, y = var('x y')

# Solve single equation
solutions = solve(x^2 - 5*x + 6 == 0, x)
print(f"Solutions of x^2 - 5x + 6 = 0: {solutions}")

# System of equations
system = [x + y == 10, x - y == 2]
solution = solve(system, [x, y])
print(f"System solution: {solution}")

# Numerical solutions
numerical = find_root(cos(x) - x, 0, 1)
print(f"Numerical root of cos(x) = x: {numerical}")

# =============================================================================
# Group Theory
# =============================================================================

print("\n=== Group Theory ===")

# Symmetric group
S4 = SymmetricGroup(4)
print(f"Order of S4: {S4.order()}")

# Permutations
p1 = S4("(1,2,3)")
p2 = S4("(1,2)")
print(f"p1 = {p1}")
print(f"p2 = {p2}")
print(f"p1 * p2 = {p1 * p2}")
print(f"Order of p1: {p1.order()}")

# Cyclic group
Z6 = CyclicPermutationGroup(6)
print(f"\nCyclic group Z6, generators: {Z6.gens()}")

# =============================================================================
# Ring Theory
# =============================================================================

print("\n=== Ring Theory ===")

# Integers modulo n
Zn = Integers(12)
print(f"Z/12Z elements: {list(Zn)}")
print(f"Units in Z/12Z: {[a for a in Zn if gcd(a, 12) == 1]}")

# Quotient ring
R.<x> = PolynomialRing(QQ)
I = R.ideal(x^2 + 1)
Q = R.quotient(I, 'i')
i = Q.gen()
print(f"\nIn Q[x]/(x^2+1):")
print(f"i^2 = {i^2}")
print(f"(1 + i)^2 = {(1 + i)^2}")

# =============================================================================
# Field Extensions
# =============================================================================

print("\n=== Field Extensions ===")

# Algebraic number field
K.<a> = NumberField(x^2 - 2)
print(f"K = Q(sqrt(2))")
print(f"a^2 = {a^2}")
print(f"(1 + a)^3 = {(1 + a)^3}")

# Minimal polynomial
print(f"Minimal polynomial of a: {a.minpoly()}")

# =============================================================================
# Vector Spaces
# =============================================================================

print("\n=== Vector Spaces ===")

# Vector space over rationals
V = QQ^3
v1 = V([1, 2, 3])
v2 = V([4, 5, 6])

print(f"v1 = {v1}")
print(f"v2 = {v2}")
print(f"v1 + v2 = {v1 + v2}")
print(f"Dot product: {v1.dot_product(v2)}")

# Subspace
W = V.subspace([v1, v2])
print(f"Dimension of span(v1, v2): {W.dimension()}")

# =============================================================================
# Combinatorics
# =============================================================================

print("\n=== Combinatorics ===")

# Binomial coefficients
print(f"C(10, 3) = {binomial(10, 3)}")
print(f"10! = {factorial(10)}")

# Partitions
partitions_5 = Partitions(5).list()
print(f"Partitions of 5: {partitions_5}")

# Permutations
perms = Permutations([1, 2, 3]).list()
print(f"Permutations of [1,2,3]: {perms}")
