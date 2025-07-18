"""
Extensive test suite for protdict.Data class and supporting utilities.
"""
import sys, os
# Ensure project root is on path
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, proj_root)

# Import Data and utilities
from src.protdict.data_class import Data
from src.protdict.functional_utils.lists import in_lower_list, mergel, clean_values
from src.protdict.functional_utils.types import multi_isinstance
from collections.abc import Iterable


def separator(title):
    print("\n" + "=" * 30)
    print(f"== {title} ==")
    print("=" * 30)


def test_basic():
    separator("Basic Initialization & Access")
    d = Data({"x": 10, "y": 20})
    print("d.x:", d.x)
    print("d.y:", d.y)
    print("keys():", d.keys())
    print("as_dict():", d.as_dict())


def test_tags_and_kwargs():
    separator("Tags and Kwargs")
    d = Data(
        {"a": {"value": 1, "tags": ["protected", "typed"]},
         "b": {"value": "hi", "tags": ["kwarg"]}},
        b="hello"
    )
    print("Initial Data object:", d)
    print("tags('a'):", d.tags("a", None))
    print("tags('b'):", d.tags("b", None))
    print("protected_keys():", d.protected_keys())
    print("typed_keys():", d.typed_keys())
    print("kwarg_keys():", d.kwarg_keys())


def test_typing():
    separator("Typing Lock")
    d = Data({"num": 2}, num=2, initial_typing=True)
    print("Typed from kwargs:", d.typed_keys())
    print("Attempt to set num to string:")
    d.set("num", "string")  # type-lock error
    print("Overwrite num with oset to 5:")
    d.oset("num", 5)
    print("d.num after oset:", d.num)


def test_protect_unprotect():
    separator("Protect / Unprotect")
    d = Data({"x": 1, "y": 2})
    print("Before protect x, keys():", d.keys())
    d.protect("x")
    print("After protect x, protected_keys():", d.protected_keys())
    print("Attempt erase('x') (should be False):", d.erase("x"))
    d.unprotect("x")
    print("After unprotect x, protected_keys():", d.protected_keys())
    print("Now erase('x') (should be True):", d.erase("x"))
    print("x in d after erase:", hasattr(d, "x"))


def test_erase():
    separator("Erase / OErase")
    d = Data({"p": 100, "q": 200}, q=200)
    print("Initial keys():", d.keys(), "protected_keys():", d.protected_keys())
    res = d.erase("q")
    print("Erase protected 'q' without override (should be False):", res, "keys():", d.keys())
    res = d.oerase("q")
    print("Force erase 'q' with oerase (should be True):", res, "keys():", d.keys())


def test_merge_and_absorb():
    separator("Merge and Absorb")
    d1 = Data({"a": 1, "b": 2})
    d2 = Data({"b": 3, "c": 4})
    print("Initial d1:", d1.as_dict())
    d1.merge_dict({"b": 10, "d": 5}, overwrite_current=False, protect_new_added_keys=True)
    print("After merge_dict no overwrite:", d1.as_dict(), "protected:", d1.protected_keys())
    d1.merge_dict({"b": 20}, overwrite_current=True)
    print("After merge_dict overwrite b:", d1.as_dict())

    print("\nAbsorb d2 into d1 (overwrite=False):")
    d1.absorb(d2)
    print("After absorb no overwrite:", d1.as_dict())
    print("Absorb d2 into d1 (overwrite=True):")
    d1.absorb(d2, overwrite=True)
    print("After absorb with overwrite:", d1.as_dict())


def test_export_clone():
    separator("Export and Clone")
    d = Data({"x": 5}, y={"value": 6, "tags": ["protected"]}, z=7)
    print("Original (include_protected=True):", d.as_dict(include_protected=True))
    exp = d.export()
    print("Exported dict:", exp)
    d2 = Data(data_dictionary=exp)
    print("Reconstructed (include_protected=True):", d2.as_dict(include_protected=True))


def test_dunders_and_basic_ops():
    separator("Dunders & Basic Ops")
    d = Data({"a": 1}, b=2)
    # __getitem__, __setitem__, __delitem__
    d["c"] = 3
    print("After setitem 'c':", d.c)
    del d["c"]
    print("After delitem 'c', contains 'c':", 'c' in d)
    # __contains__
    print("Contains 'a':", 'a' in d)
    # __len__, __bool__
    print("Length:", len(d), "Bool(empty?):", bool(Data({})) )
    # __iter__
    print("Iterated keys:", list(iter(d)))
    # __eq__
    d2 = Data({"a":1}, b=2)
    print("Equality d == d2:", d == d2)


def test_get_keys_values_items():
    separator("get, keys, values, items")
    d = Data({"x": 9}, y=10)
    print("get existing x:", d.get("x", None))
    print("get missing z:", d.get("z", 'default'))
    print("keys():", d.keys())
    print("values():", d.values())
    print("items():", d.items())


def test_clear_update():
    separator("clear & update")
    d = Data({"x":1, "y":2}, y=2)
    d.clear()
    print("After clear, len:", len(d))
    d.update({"a":10, "y":20})
    print("After update, a:", d.get("a"), "y (unchanged protected):", getattr(d, 'y', None))


def test_keys_by_tag_and_bundle():
    separator("keys_by_tag & bundle_keys")
    d = Data({"p":1, "q":{"value":2,"tags":["protected","typed"]}}, r=3)
    print("keys_by_tag:", d.keys_by_tag())
    b = d.bundle_keys(protected_tag=True, typed_tag=False, kwarg_tag=False, no_tags=True)
    print("bundle_keys (untagged only):", b)


def test_set_all_and_rem_all_typings():
    separator("set_all_typings & rem_all_typings")
    d = Data({"x":1, "y":2, "z":3}, initial_typing=False)
    count_all = d.set_all_typings()
    print("Type locks set (all):", count_all, "typed_keys:", d.typed_keys())
    count_rem = d.rem_all_typings()
    print("Type locks removed (keep protected):", count_rem, "typed_keys now:", d.typed_keys())


def test_functional_utils():
    separator("functional_utils tests")
    # in_lower_list
    print("in_lower_list('A',['a','b']):", in_lower_list('A', ['a','b']))
    # mergel
    print("mergel([1,2],[3,4]):", mergel([1,2], [3,4]))
    # clean_values removes blocked values
    print("clean_values(['a','b'], ['b']):", clean_values(['a','b'], ['b']))
    # multi_isinstance
    print("multi_isinstance([1,'a'], [int,str]):", multi_isinstance([1,'a'], [int,str]))
    try:
        multi_isinstance('not iterable', [int], raise_val_error=True)
    except ValueError as e:
        print("Caught expected ValueError for items arg")


def main():
    import time
    libname:str = "protodict"
    ver:str = "0.0.2"
    start_time = time.perf_counter()
    test_basic()
    test_tags_and_kwargs()
    test_typing()
    test_protect_unprotect()
    test_erase()
    test_merge_and_absorb()
    test_export_clone()
    test_dunders_and_basic_ops()
    test_get_keys_values_items()
    test_clear_update()
    test_keys_by_tag_and_bundle()
    test_set_all_and_rem_all_typings()
    test_functional_utils()
    end_time = time.perf_counter()
    elapsed_time = end_time-start_time
    print(f"===| Test Suite for {libname} on v.{ver} Completed! -> Elapsed Time: {elapsed_time:.4f} seconds |===")


if __name__ == "__main__":
    main()
