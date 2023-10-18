from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T", int, float)


class view(Generic[T]):
    """
    A generic intended to model abstract data accesses

    On the C side it would be implemented as a pointer and a sequence of
    strides.
    """

    def __init__(self) -> None:
        self._v: list[T] = list()

    def __getitem__(self, i: int) -> T:
        return self._v[i]

    def __setitem__(self, i: int, v: T) -> None:
        pass
