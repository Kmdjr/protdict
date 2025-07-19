from typing import Any, Callable
from .protdict_class import Data
from .dataval_class import DataVal

class TypeManager:
    """
    Manages registered types for serialization and validation.
    Resolves type names <-> actual types.
    """
    def __init__(self):
        self._types = {}
        self._exporters = {}
        self._importers = {}
        self._builtin_types = {}
        self.register_builtin_types()
        self.register_builtin_funcs()

    def register_builtin_types(self):
        """
        Registers common Python builtins and internal types.
        Uses type.__name__ as the key to avoid naming errors.
        """
        default_types = [
            int, float, str, bool,
            list, dict, set, tuple,
            Data, DataVal
        ]
        for t in default_types:
            self._builtin_types[t.__name__] = t
            self._types[t.__name__] = t

    def register_builtin_funcs(self):
        from .type_exporters import builtin_type_exporters
        from .type_importers import builtin_type_importers
        self._exporters = builtin_type_exporters
        self._importers = builtin_type_importers

    def register_type(
        self,
        type_ref: type,
        *,
        exporter: Callable[[Any], dict] = None,
        importer: Callable[[dict], Any] = None,
        overwrite: bool = False
    ):
        """
        Register a type by its class name and optional custom (de)serializers.
        - type_ref: the class/type
        - exporter: function that turns an instance into a dict
        - importer: function that takes that dict and returns an instance
        - overwrite: if True, replaces existing registration
        """
        if not isinstance(type_ref, type):
            raise TypeError("type_ref must be a type")

        name = type_ref.__name__
        if name in self._types and not overwrite:
            raise ValueError(f"Type '{name}' already registered")

        self._types[name] = type_ref
        if exporter:
            self._exporters[name] = exporter
        if importer:
            self._importers[name] = importer

    def resolve(self, names: str|list[str], *, strict=False) -> list[type]|type:
        """
        Convert str or list of type names to actual Python types.
        - strict=True raises an error if any type is not found.
        - if list[str] passed in as names, return will be list of types.
        - if str is passed in as names, return will be singular type.
        """
        names = names if isinstance(names,list) else [names]
        resolved = []
        for name in names:
            t = self._types.get(name)
            if t:
                resolved.append(t)
            elif strict:
                raise ValueError(f"Unknown type: '{name}'")
        return resolved[0] if len(resolved) == 1 else resolved

    def reverse(self, types: list[type]) -> list[str]:
        """
        Convert list of Python types to their registered names.
        Falls back to type.__name__ if not registered.
        """
        name_map = {v: k for k, v in self._types.items()}
        return [name_map.get(t, t.__name__) for t in types]

    def get_registered(self) -> dict[str, type]:
        """Returns a copy of all registered types."""
        return dict(self._types)

    def serialize(self, value: Any) -> dict | Any:
        """
        Attempt to export a value via its registered serializer.
        Falls back to __dict__ or raw value.
        """
        t = type(value)
        name = t.__name__
        if name in self._exporters:
            return self._exporters[name](value)
        elif hasattr(value, "__dict__"):
            return self._exporters[dict.__name__](vars(value))  # shallow copy of instance dict
        return {"__value__":value,"_type":type(value).__name__}  # fallback to raw
 
    def deserialize(self, serialized_dict:dict[str]) -> Any:
        """
        If type_ref is a class, grab its __name__; if string, use it directly.
        Then run the registered importer if present, else return raw.
        """
        from .functional_utils.types import DataParsingError
        _typen = serialized_dict.get("_type")
        _type = self.resolve(_typen)
        value = serialized_dict.get("__value__")
        converter = self._importers.get(_typen)
        if _typen is None or _type is None:
            raise DataParsingError(serialized_dict,_typen,_type,converter,value)
        if converter is None:
            return value  # fallback
        return converter(value)

# --------------------------
# GLOBAL INSTANCE MANAGEMENT
# --------------------------

_DEFAULT_TYPE_MANAGER = None

def get_type_manager() -> TypeManager:
    """
    Access the shared global TypeManager instance.
    Lazily initializes on first use.
    """
    global _DEFAULT_TYPE_MANAGER
    if _DEFAULT_TYPE_MANAGER is None:
        _DEFAULT_TYPE_MANAGER = TypeManager()
    return _DEFAULT_TYPE_MANAGER

def set_type_manager(new_manager: TypeManager):
    """
    Replace the global shared TypeManager instance.
    Only use this if you're deliberately overriding the system.
    """
    if not isinstance(new_manager, TypeManager):
        raise TypeError("new_manager must be a TypeManager instance")
    global _DEFAULT_TYPE_MANAGER
    _DEFAULT_TYPE_MANAGER = new_manager
