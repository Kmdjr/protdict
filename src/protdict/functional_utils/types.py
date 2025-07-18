from _collections_abc import Iterable

from collections.abc import Iterable
from .nums import clamp

from collections.abc import Iterable
from .nums import clamp

def multi_isinstance(items: Iterable, valid_types: Iterable, raise_val_error: bool = False) -> bool:
    """
    Checks whether each item in `items` is an instance of the corresponding type in `valid_types`.
    If `valid_types` is shorter, its last entry is reused. Entries can be a type, or
    a list/tuple of types (or None, which is treated as type(None)).
    """
    # 1) Sanity checks
    if not isinstance(items, Iterable) or isinstance(items, dict):
        if raise_val_error:
            raise ValueError("`items` must be a non-dict iterable.")
        return False
    if not isinstance(valid_types, Iterable) or isinstance(valid_types, dict):
        if raise_val_error:
            raise ValueError("`valid_types` must be a non-dict iterable.")
        return False

    vt = list(valid_types)
    if not vt:
        if raise_val_error:
            raise ValueError("`valid_types` must contain at least one entry.")
        return False

    # 2) Iterate & check
    for idx, val in enumerate(items):
        ti = clamp(idx, 0, len(vt) - 1)
        expected = vt[ti]

        # Build a tuple of real types for isinstance()
        raw_types = expected if isinstance(expected, (list, tuple)) else (expected,)
        clean_types = []
        for t in raw_types:
            if t is None:
                clean_types.append(type(None))
            elif isinstance(t, type):
                clean_types.append(t)
            else:
                if raise_val_error:
                    raise ValueError(f"Invalid type specifier in valid_types: {t!r}")
                # skip anything else
        if not clean_types:
            if raise_val_error:
                raise ValueError(f"No valid types derived from: {expected!r}")
            return False

        type_tuple = tuple(clean_types)
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