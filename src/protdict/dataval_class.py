import time
from typing import Any, Union, List, Dict, Callable
from .typing_manager import get_type_manager
from .validation_manager import get_tag_validator

class DataVal:
    """
    Internal wrapper for a single Data entry, with full (de)serialization support.
    """

    def __init__( self, value: Any, *, essential: bool = False, protected: bool = False, frozen: bool = False, 
        hidden: bool = False, types:str|list[str]|type|list[type]|None = None, 
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
            self._tags:dict[str] = {}
        elif isinstance(tags,str):
            self._tags = {tags:{"version":0,"funcs":[]}}
        elif isinstance(tags,list) and all(isinstance(t,str) for t in tags):
            self._tags = {t:{"version":0,"funcs":[]} for t in tags}
        self._check_tag_validators()

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

        # ——— 6) Enforce the types constraint on the (possibly imported) value ———
        if self.types and not isinstance(value, tuple(self.types)):
            raise TypeError(
                f"Invalid value type: expected one of {self.types}, got {type(value).__name__}"
            )

        # ——— 7) Finally assign all fields ———
        self._value = value
        self.essential = essential
        self.protected = protected
        self.frozen = frozen
        self.hidden = hidden
        self.description = description
        self.source = source
        self.metadata = metadata

    ## Property Setters and Dunders:

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self,new_val):
        if self.frozen:
            raise ValueError("Value is frozen. Use .unfreeze() method to make it not read-only")
        if self.essential:
            raise ValueError("Value is marked as essential. Use o* family methods to overwrite value or remove it from essentials.")
        self._type_check(new_val)
        self._validate(new_val)
        self._value = new_val
    
    @property
    def tags(self):
        return [tag for tag in self._tags.keys()]

    def export(self) -> Dict[str, Any]:
        """
        1) Pick the _type name (override or actual)  
        2) Serialize the value (built-ins or custom)  
        3) Convert tuples→lists for JSON  
        4) Emit all metadata + types (as str list) + validators
        """
        tm = get_type_manager()
        type_name = type(self.value).__name__

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
        }

    def _check_tag_validators(self):
        tv = get_tag_validator()
        for name, info in self._tags.items():
            if info.get("version") < tv.version(name):
                updated = tv.get_tag_info(name)
                info["version"] = updated[1]
                info["funcs"] = updated[0]

    def _validate(self,new_val):
        self._check_tag_validators()
        for tag,info in self._tags.items():
            for func in info.get("funcs"):
                try:
                    result = func(new_val)
                except Exception as e:
                    raise ValueError(f"Validator for tag '{tag}' raised and exception: {e}")
                if result is False:
                    raise ValueError(f"Validation failed for the tag '{tag}' with value: {new_val}")
                    

    def _type_check(self,new_val):
        if self.types:
            if type(new_val) not in self.types:
                raise TypeError("Expected new value to be of type: "+", ".join(self.types)+" but got: "+type(new_val).__name__)
    
    def get_tags(self):
        return [t for t in self._tags.keys()]
    
    def set_tag(self,tag:str):
        if not isinstance(tag,str):
            raise ValueError("Expected 'tag' as type 'str'. got type: ",type(tag).__name__,".")
        self._tags[tag] = 0

        

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
            description=data.get("description", ""),
            source=data.get("source", ""),
            metadata=data.get("metadata", None),
            _type=type_name,
            tags=data.get("tags", []),
        )









    ## CLASS DUNDERS ##
    def __setattr__(self, name, value):
        # Internal safe paths (used in __init__ or internally)
        if name in {
            "_value", "_tags", "_type", "_tag_validators",
            "_tag_versions", "_type_check", "_validate", "_check_tag_validators"
        }:
            super().__setattr__(name, value)
            return

        # Redirect .value → use the property (calls setter, handles validation)
        if name == "value":
            object.__setattr__(self, name, value)
            return

        # Block setting frozen — force .freeze() or .unfreeze()
        if name == "frozen":
            raise AttributeError("Cannot assign 'frozen' directly. Use .freeze() or .unfreeze().")

        # Block essential — must use overwrite methods
        if name == "essential":
            raise AttributeError("Cannot assign 'essential' directly. Use overwrite-safe methods.")

        # Block setting protected unless essential is False
        if name == "protected":
            if not isinstance(value, bool):
                raise TypeError(f"Expected bool for 'protected', got {type(value).__name__}")
            if getattr(self, "essential", False):
                raise AttributeError("Cannot modify 'protected' while 'essential' is True.")
            super().__setattr__(name, value)
            return

        # Block setting hidden unless valid bool
        if name == "hidden":
            if not isinstance(value, bool):
                raise TypeError(f"Expected bool for 'hidden', got {type(value).__name__}")
            super().__setattr__(name, value)
            return

        # Do not allow direct type reassignment
        if name == "types":
            raise AttributeError("Do not assign 'types' directly. Use .set_types() instead.")

        # Allow safe descriptive fields
        if name in {"description", "source", "metadata"}:
            super().__setattr__(name, value)
            return

        # Everything else is blocked
        raise AttributeError(f"Attribute '{name}' cannot be set directly.")


            