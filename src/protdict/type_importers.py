from .protdict_class import Data
from .dataval_class import DataVal
from typing import Callable

def data_type(val:dict) -> Data:
    return Data(val.get("__values__",None),val.get("__frozen__",False),val.get("__essentials_typing__",True))

def dataval_type(val:dict) -> DataVal:
    return DataVal.create(val)

def set_type(val) -> set:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = set()
    for item in val:
        result.add(tm.deserialize(item))
    return result

def tuple_type(val) -> tuple:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = []
    for item in val:
        result.append(tm.deserialize(item))
    return tuple(result)

def list_type(val) -> list:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = []
    for item in val:
        result.append(tm.deserialize(item))
    return result

def dict_type(val) -> dict:
    from .typing_manager import get_type_manager
    tm = get_type_manager()
    result = {}
    for key, v in val.items():
        result[key] = tm.deserialize(v)
    return result

def float_type(val:float) -> float:
    return float(val)

def int_type(val:float) -> int:
    return int(val)

def str_type(val:str) -> str:
    return str(val)

def bool_type(val:bool) -> bool:
    return bool(val)



builtin_type_importers:dict[str,Callable] = {
    int.__name__:int_type,
    float.__name__:float_type,
    set.__name__:set_type,
    tuple.__name__:tuple_type,
    dict.__name__:dict_type,
    list.__name__:list_type,
    Data.__name__:data_type,
    DataVal.__name__:dataval_type,
    bool.__name__:bool_type,
    str.__name__:str_type
}