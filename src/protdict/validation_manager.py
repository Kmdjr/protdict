from typing import Any, Callable
from .protdict_class import Data
from .dataval_class import DataVal

class ValidationRegistry:
    def __init__(self):
        self._map:dict[str,list[Callable]] = {}
        self._versions:dict[str,int] = {}

    def register(self,tag:str,funcs:Callable|list[Callable]) -> list[Callable]:
        if not isinstance(tag,str):
            raise ValueError("Expected type 'str' for 'tag'. got type: "+type(tag).__name__+".")
        if not isinstance(funcs,Callable) and not isinstance(funcs,list):
            raise ValueError("Expected type 'Callable' or 'list[Callable]' for 'funcs'. got type: "+type(funcs).__name__+".")
        for fn in funcs:
            if not isinstance(fn,Callable):
                 raise ValueError("Expected type 'Callable' for all values in list 'funcs'. got type: "+type(fn).__name__+".")
        fn = funcs if isinstance(funcs,list) else [funcs]
        mapped = self._map.get(tag,None)
        if mapped is None: self._map[tag] = []
        self._map[tag].extend(fn)
        version = self._versions.get(tag,None)
        if version is None:
            self._versions[tag] = 1
        else:
            self._versions[tag] += 1
        return self.get_tag_info(tag)

    def get(self,tag:str) -> list[Callable]:
        return self._map.get(tag,[])
    
    def version(self,tag:str) -> int:
        return self._versions.get(tag,0)
    
    def get_tag_info(self,tag:str) -> tuple[list[Callable],int]:
        return (self.get(tag),self.version(tag))




_DEAFULT_TAG_VALIDATOR = None

def get_tag_validator() -> ValidationRegistry:
    """
    Access the shared global ValidationRegistry instance.
    Lazily initializes on first use.
    """
    global _DEAFULT_TAG_VALIDATOR
    if _DEAFULT_TAG_VALIDATOR is None:
        _DEAFULT_TAG_VALIDATOR = ValidationRegistry()
    return _DEAFULT_TAG_VALIDATOR

def set_tag_validator(new_validator:ValidationRegistry):
    """
    Replace the global shared ValidationRegistry instance.
    Only use this if you're deliberately overriding the system.
    """
    if not isinstance(new_validator, ValidationRegistry):
        raise TypeError("new_validator must be a TypeManager instance")
    global _DEAFULT_TAG_VALIDATOR
    _DEAFULT_TAG_VALIDATOR = new_validator