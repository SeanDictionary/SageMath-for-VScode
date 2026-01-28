# Basic SageMath test file for extension testing

# Variable definitions
x = var('x')
y = var('y')

# Basic arithmetic
result = 2 + 3 * 4
print(f"Result: {result}")

# Symbolic computation
expr = x^2 + 2*x + 1
factored = factor(expr)
print(f"Factored: {factored}")

# Matrix operations
M = matrix([[1, 2], [3, 4]])
det_M = M.det()
print(f"Determinant: {det_M}")

# Polynomial ring
R.<t> = PolynomialRing(QQ)
p = t^3 - 2*t + 1
roots = p.roots()
print(f"Roots: {roots}")

# Function definition
def my_function(n):
    """A simple function for testing."""
    return factorial(n)

# List comprehension
squares = [i^2 for i in range(10)]
print(f"Squares: {squares}")

# Conditional
if is_prime(17):
    print("17 is prime")
else:
    print("17 is not prime")

# Loop
for i in range(5):
    print(f"Iteration {i}: {fibonacci(i)}")

# Class definition
class MyClass:
    def __init__(self, value):
        self.value = value
    
    def compute(self):
        return self.value^2

# Cryptographic operations (common in CTF)
from sage.all import *
p = next_prime(2^128)
print(f"Large prime: {p}")
