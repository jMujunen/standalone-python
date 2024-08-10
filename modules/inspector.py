import inspect
from collections.abc import Callable

from fsutils import Dir


def get_methods(obj: object) -> list[tuple[str, Callable]]:
    """Return a list of tuples (name, value) for the given object."""
    methods = []
    for name in dir(obj):
        # Ignore private and built-in attributes
        if not name.startswith("__"):
            try:
                value = getattr(obj, name)
                # If the attribute has a __call__ method, it's probably callable
                if callable(value) or isinstance(value, property):
                    methods.append((name, getattr(obj, name)()))
            except Exception as e:
                # Ignore any errors when calling the attribute
                print(f"Error calling {obj.__class__.__name__}.{name}: {e}")
    return methods


# Example
if __name__ == "__main__":
    obj = Dir("~/.dotfiles")
    methods = get_methods(obj)
    for name, value in methods:
        print(f"{name}: {value}")
