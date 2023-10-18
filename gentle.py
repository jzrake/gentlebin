from typing import TypeVar, Generic, Protocol
from dataclasses import dataclass


T = TypeVar("T", int, float)


class Index(Protocol):
    def jump(self, axis: int, offset: int) -> Index:
        ...


class View(Generic[T], Protocol):
    """
    A generic intended to model abstract data accesses

    On the C side it would be implemented as a pointer and a sequence of
    strides.
    """

    def __getitem__(self, i: int) -> T:
        ...

    def __setitem__(self, i: int, v: T) -> None:
        ...
