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

def resolve_types(type_names: list[str]) -> list[type]:
    """
    Converts a list of type name strings to actual Python type objects.

    - Supports basic built-in types: int, float, str, bool, list, dict, set, tuple, Any
    - Ignores unknown type names
    - Returns an empty list if nothing is valid
    """
    from typing import Any
    known_types = {
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "Any": Any
    }

    resolved = []
    for name in type_names:
        t = known_types.get(name)
        if t:
            resolved.append(t)
        # You can optionally log or raise for unknown types if needed

    return resolved
        
class PermissionError(Exception):
    from ..dataval_class import DataVal
    from ..protdict_class import Data
    def __init__(self,obj:Data|DataVal, *, frozen:bool=False,protected:bool=False,essential:bool=False):
        self.obj = obj
        self.pro:bool = protected
        self.ess:bool = essential
        self.f:bool = frozen
        self.message = ""
        if self.f:
            self.message = " is frozen and can not be editted. use .unfreeze() to unfreeze the value."
        else:
            if self.ess:
                self.message += " is an essential"
            if self.pro:
                self.message += "and protected" if self.message != "" else " is a protected"
            if self.message != "":
                self.message += " value. unprotect with .unprotect() or if essential, override with .ounprotect()"
    def __str__(self):
        return f"{self.obj.__name__} {self.message}"

class DataParsingError(Exception):
    def __init__(self,serializing_obj,typen,_type,converter,val):
        self.obj = serializing_obj
        self.fails = {
            "type_name": bool(typen),
            "type" : bool(_type),
            "converter function" :bool(converter),
            "value" : bool(val)
        }
        

    def __str__(self):
        return f"Error while parsing: {str(self.obj)}. Failed at resolving: "+", ".join(key for key in self.fails.keys() if not self.fails[key])

class DataSerializationError(Exception):
    def __init__(self,serializing_obj):
        self.obj = serializing_obj
    
    def __str__(self):
        return f"Error while serializing: {str(self.obj)}."