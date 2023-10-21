from typing import TypeVar, Generic, Protocol, Self
from dataclasses import dataclass


T = TypeVar("T", int, float)


class Array(Generic[T], Protocol):
    """
    A generic intended to model abstract data accesses

    On the C side it would be implemented as a pointer and a sequence of
    strides.
    """

    def __getitem__(self, i: int) -> T:
        ...

    def __setitem__(self, i: int, v: T) -> None:
        ...

    @property
    def size(self) -> int:
        ...
