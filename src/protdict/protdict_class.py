from .functional_utils.lists import in_lower_list, mergel, clean_values
from .functional_utils.types import multi_isinstance, PermissionError
from typing import Optional, Callable, Any, List, Dict, Union
from .dataval_class import DataVal

class Data:
    def __init__(self, data_dictionary:dict,frozen:bool=False,essentials_typing:bool=True,**Essentials):
        self.frozen = data_dictionary.get("_data_frozen",frozen)

        pass

    def _set_new_val( self, name:str, value: Any, *, essential: bool = False, protected: bool = False, frozen: bool = False, 
        hidden: bool = False, types:str|list[str]|type|list[type]|None = None, validator:str|list[str]|None = None, 
        description: str = "", source: str = "", metadata: Any = None, tags:str|list[str]|None = None,override:bool=False):
        if not isinstance(name,str):
            raise TypeError("name must be of type string but was of type ",type(name))
        self._frozen_check()
        current:DataVal = getattr(self,name,None)
        if current: self._permission_check(current,override)
        newval:DataVal = DataVal(value,essential=essential,protected=protected,frozen=frozen,hidden=hidden,types=types,validator=validator,
                description=description,source=source,metadata=metadata)
        setattr(self,name,newval)
    
    def set(self, name:str, value: Any, *, essential: bool = False, protected: bool = False, frozen: bool = False, 
        hidden: bool = False, types:str|list[str]|type|list[type]|None = None, validator:str|list[str]|None = None, 
        description: str = "", source: str = "", metadata: Any = None, tags:str|list[str]|None = None):
        self._set_new_val(value,essential=essential,protected=protected,frozen=frozen,hidden=hidden,types=types,validator=validator,
                description=description,source=source,metadata=metadata,override=False)
    
    def oset(self, name:str, value: Any, *, essential: bool = False, protected: bool = False, frozen: bool = False, 
        hidden: bool = False, types:str|list[str]|type|list[type]|None = None, validator:str|list[str]|None = None, 
        description: str = "", source: str = "", metadata: Any = None, tags:str|list[str]|None = None):
        self._set_new_val(value,essential=essential,protected=protected,frozen=frozen,hidden=hidden,types=types,validator=validator,
                description=description,source=source,metadata=metadata,override=True)
    
    def is_frozen(self,target:"Data"|DataVal=None) -> bool:
        """Returns True if a `target` if frozen or self if not given. False if not."""
        target = self if target is None else target
        if not isinstance(target,(Data,DataVal)):
            raise TypeError("value should be of type Data or DataVal but is of type: ",str(type(target)))
        return target.frozen
        
        

        




    def _permission_check(self,val:DataVal|"Data",override:bool=False):
        if val.frozen: raise PermissionError(val,frozen=True)
        if not override:
            if val.protected or val.essential: raise PermissionError(val,protected=val.protected,essential=val.essential)
    
    def _frozen_check(self):
        if self.frozen: raise PermissionError(self,frozen=True)