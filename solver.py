from math import sqrt
from gentle import Array


def return_12() -> int:
    return 12


def simple_arithmetic(c: int, d: float, e: float) -> float:
    x: float = d + e
    y: float = d - e + 12.0
    z: float = sqrt(5.0 + 6.0 + x if c else 7.0)
    y += 3.0
    return y


def tuples(c: int, d: float, e: float) -> tuple[float, int]:
    x: float = d + e
    y: float = d - e + 12.0
    z: float = sqrt(5.0 + 6.0 + x if c else 7.0)
    m: tuple[float, int] = (z, 2)
    return m


def for_loop(c: int) -> int:
    y: int = 0
    for a in range(c, c + 10, 2):
        y += a
        y -= 2
    return y


def if_statement(c: int) -> int:
    if c:
        return 13
    elif c + 1:
        return 14
    else:
        return 15


def simple_kernel(a: Array[float], i: int) -> float:
    return a[i]
