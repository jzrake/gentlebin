from math import sqrt
from gentle import view


def return_12() -> int:
    return 12


def do_easy_math(c: int, d: float, e: float) -> tuple[float, int]:
    x: float = d + e
    y: float = d - e + 12.0
    z: float = sqrt(5.0 + 6.0 + x if c else 7.0)
    m: tuple[float, int] = (z, 2)
    y += 3.0
    return m


def my_kernel(u: view[int], v: view[int]) -> None:
    z: int = u[0] + v[1]
    u[0] += z
