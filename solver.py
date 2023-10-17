from math import sqrt


def return_12() -> int:
    return 12


def do_easy_math(c: int, d: float, e: float) -> tuple[float, int]:
    x: float = d + e
    y: float = d - e + 12.0
    z: float = sqrt(5.0 + 6.0 + x if c else 7.0)
    m: tuple[float, int] = (z, 2)
    return m
