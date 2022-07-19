"""
fib() - fibonaci
2020-1101 PP new, from RealPython - micropython course
"""

a = 20

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print(list(fib(a)))
