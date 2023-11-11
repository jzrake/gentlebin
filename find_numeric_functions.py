from importlib.util import spec_from_file_location, module_from_spec
from inspect import signature, Parameter
from typing import get_type_hints


def has_simple_numeric_signature(f):
    numeric_types = (int, float)
    sig = signature(f)
    return (
        all(p.annotation in numeric_types for p in sig.parameters.values())
        and sig.return_annotation in numeric_types
    )


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-c", "--check", action="store_true")
    args = parser.parse_args()

    spec = spec_from_file_location("source", args.filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    scope = dict()

    for key in dir(module):
        item = getattr(module, key)
        if callable(item) and has_simple_numeric_signature(item):
            scope[key] = item

    print(scope)
