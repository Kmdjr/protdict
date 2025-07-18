from _collections_abc import Iterable

from collections.abc import Iterable
from .nums import clamp

def multi_isinstance(items: Iterable, valid_types: Iterable, raise_val_error: bool = False) -> bool:
    """
    Checks whether each item in `items` is an instance of the corresponding type in `valid_types`.

    If `valid_types` is shorter than `items`, the last type in `valid_types` is reused.
    `valid_types` entries may be a single type or a tuple/list of types.
    """
    # 1) Basic sanity checks
    if not isinstance(items, Iterable) or isinstance(items, dict):
        if raise_val_error:
            raise ValueError("`items` must be a non-dict iterable.")
        return False
    if not isinstance(valid_types, Iterable) or isinstance(valid_types, dict):
        if raise_val_error:
            raise ValueError("`valid_types` must be a non-dict iterable.")
        return False

    # 2) Turn into indexable list
    valid_types = list(valid_types)
    if not valid_types:
        if raise_val_error:
            raise ValueError("`valid_types` must contain at least one type.")
        return False

    # 3) Check each item
    for idx, val in enumerate(items):
        # pick the matching expected_type (or last one if we run out)
        ti = clamp(idx, 0, len(valid_types) - 1)
        expected = valid_types[ti]

        # normalize to a tuple of types
        if isinstance(expected, (list, tuple)):
            type_tuple = tuple(expected)
        elif isinstance(expected, type):
            type_tuple = (expected,)
        else:
            if raise_val_error:
                raise ValueError(f"Invalid entry in valid_types: {expected!r}")
            return False

        # final isinstance check
        if not isinstance(val, type_tuple):
            return False

    return True



def is_type_exclude(obj, types: tuple, exclusions: tuple) -> bool:
    """
    Returns True if `obj` is an instance of any type in `types`, but not in `exclusions`.

    Args:
        obj (Any): Object to check.
        types (tuple): Types to match.
        exclusions (tuple): Types to exclude.

    Returns:
        bool: True if `obj` matches types and not exclusions, False otherwise.
    """
    if isinstance(obj, types) and not isinstance(obj, exclusions):
        return True
    return False