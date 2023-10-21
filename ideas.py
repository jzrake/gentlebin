from functools import update_wrapper
from numpy import linspace, zeros_like
from gentle import Array


class Kernel:
    def __init__(self, func):
        self.func = func
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        """
        Pass-through arguments to the wrapped function
        """
        return self.func(*args, **kwargs)

    def __matmul__(self, array: Array):
        """
        Boilerplate executor implementation, a sequential for-loop
        """
        result = zeros_like(array)
        for i in range(array.size):
            result[i] = self.func(array, i)
        return result


def kernel(f):
    """
    A decorator to mark a function as a kernel

    Kernel functions can in principle be mapped over over an array, and have
    syntactic sugar for that mapping, e.g. my_kernel @ an_array.
    """

    return Kernel(f)


@kernel
def diff(a: Array, i: int):
    """
    Return the centered difference of an array, at the given index
    """
    if i > 0 and i < a.size - 1:
        return a[i + 1] - a[i - 1]
    else:
        return 0.0


a = linspace(0.0, 1.0, 11)

# Call the diff function normally at some index
print(diff(a, 0))

# Map the diff function over an array
print(diff @ a)
