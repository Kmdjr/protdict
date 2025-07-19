from .protdict_class import Data
from .dataval_class import DataVal
from typing import Callable


def data_type(val:Data) -> dict:
    return {"__value__":val.export(),"_type":Data.__name__}

def dataval_type(val:DataVal) -> dict:
    return {"__value__":val.export(),"_type":DataVal.__name__}

def set_type(val:set) -> dict:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = []
    for item in val:
        result.append(tm.serialize(item))
    return {"__value__":result,"_type":set.__name__}

def tuple_type(val:tuple) -> dict:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = []
    for item in val:
        result.append(tm.serialize(item))
    
    return {"__value__":result,"_type":tuple.__name__}

def list_type(val:list) -> dict:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = []
    for item in val:
        result.append(tm.serialize(item))
    
    return {"__value__":result,"_type":list.__name__}

def dict_type(val:dict) -> dict:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = {}
    for key, v in val.items():
        result[key] = tm.serialize(v)
    return {"__value__":result,"_type":dict.__name__}

def num_type(val:int|float) -> dict:
    kind = int if isinstance(val,int) else float
    return {"__value__":val,"_type":kind.__name__}

def str_type(val:str) -> dict:
    return {"__value__":val,"_type":str.__name__}

def bool_type(val:bool) -> dict:
    return {"__value__":val,"_type":bool.__name__}



builtin_type_exporters:dict[str,Callable] = {
    int.__name__:num_type,
    float.__name__:num_type,
    set.__name__:set_type,
    tuple.__name__:tuple_type,
    dict.__name__:dict_type,
    list.__name__:list_type,
    Data.__name__:data_type,
    DataVal.__name__:dataval_type,
    bool.__name__:bool_type,
    str.__name__:str_type

}
