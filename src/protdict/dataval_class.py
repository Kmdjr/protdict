import time
from typing import Any, Union, List, Dict
from .typing_manager import get_type_manager

class DataVal:
    """
    Internal wrapper for a single Data entry, with full (de)serialization support.
    """

    def __init__( self, value: Any, *, essential: bool = False, protected: bool = False, frozen: bool = False, 
        hidden: bool = False, types:str|list[str]|type|list[type]|None = None, validator:str|list[str]|None = None, 
        description: str = "", source: str = "", metadata: Any = None, tags:str|list[str]|None = None ):

        tm = get_type_manager()

        # ——— 2) Validate simple flags ———
        for flag_name, flag_val in (("essential", essential),("protected", protected),("frozen", frozen),("hidden", hidden)):
            if not isinstance(flag_val, bool):
                raise TypeError(f"'{flag_name}' must be bool, got {type(flag_val).__name__}")

        if not isinstance(description, str):
            raise TypeError(f"'description' must be str, got {type(description).__name__}")
        if not isinstance(source, str):
            raise TypeError(f"'source' must be str, got {type(source).__name__}")

        # ——— 3) Normalize & validate tags ———
        if tags is None:
            self.tags: List[str] = []
        elif isinstance(tags, str):
            self.tags = [tags]
        elif isinstance(tags, list) and all(isinstance(t, str) for t in tags):
            self.tags = tags
        else:
            raise TypeError("'tags' must be a string, list of strings, or None")

        # ——— 4) Normalize & validate runtime type constraints ———
        if types is None:
            self.types: List[type] = []
        elif isinstance(types, type):
            self.types = [types]
        elif isinstance(types, list) and all(isinstance(t, type) for t in types):
            self.types = types
        elif isinstance(types, str):
            self.types = tm.resolve([types], strict=True)
        elif isinstance(types, list) and all(isinstance(t, str) for t in types):
            self.types = tm.resolve(types, strict=True)
        else:
            raise TypeError(
                "'types' must be a type, list of types, string, list of strings, or None"
            )

        # ——— 5) Normalize & validate validators ———
        if validator is None:
            self.validators: List[str] = []
        elif isinstance(validator, str):
            self.validators = [validator]
        elif isinstance(validator, list) and all(isinstance(v, str) for v in validator):
            self.validators = validator
        else:
            raise TypeError("'validator' must be a string, list of strings, or None")

        # ——— 6) Enforce the types constraint on the (possibly imported) value ———
        if self.types and not isinstance(value, tuple(self.types)):
            raise TypeError(
                f"Invalid value type: expected one of {self.types}, got {type(value).__name__}"
            )

        # ——— 7) Finally assign all fields ———
        self.value = value
        self.essential = essential
        self.protected = protected
        self.frozen = frozen
        self.hidden = hidden
        self.description = description
        self.source = source
        self.metadata = metadata

    def export(self) -> Dict[str, Any]:
        """
        1) Pick the _type name (override or actual)  
        2) Serialize the value (built-ins or custom)  
        3) Convert tuples→lists for JSON  
        4) Emit all metadata + types (as str list) + validators
        """
        tm = get_type_manager()
        type_name = self._type or type(self.value).__name__

        # 1. serialize value
        raw = tm.serialize(self.value)

        return {
            "__value__": raw,
            "_type": type_name,
            "essential": self.essential,
            "protected": self.protected,
            "frozen": self.frozen,
            "hidden": self.hidden,
            "description": self.description,
            "source": self.source,
            "metadata": self.metadata,
            "tags": self.tags,
            "types": tm.reverse(self.types),
            "validators": self.validators,
        }

    @classmethod
    def create(cls, data: Dict[str, Any]) -> "DataVal":
        """
        1) Read _type and raw value  
        2) Reconstruct built-ins (tuple, set, primitives)  
        3) Run custom importer if registered  
        4) Resolve types constraint strings → classes  
        5) Pass everything back into the constructor
        """
        tm = get_type_manager()
        raw = data["__value__"]
        type_name = data["_type"]
        _type = tm.resolve(type_name)
        value = tm.deserialize({"__value__":raw,"_type":type_name})
        constraints = tm.resolve(data.get("types", []), strict=True)

        return cls(
            value,
            essential=data.get("essential", False),
            protected=data.get("protected", False),
            frozen=data.get("frozen", False),
            hidden=data.get("hidden", False),
            types=constraints,
            validator=data.get("validators", []),
            description=data.get("description", ""),
            source=data.get("source", ""),
            metadata=data.get("metadata", None),
            _type=type_name,
            tags=data.get("tags", []),
        )
