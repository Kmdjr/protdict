"""
Extensive test suite for protdict.Data class.
"""
from src.protdict.data_class import Data


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
    d.set("num", "string")  # should print a type-lock error
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


def main():
    test_basic()
    test_tags_and_kwargs()
    test_typing()
    test_protect_unprotect()
    test_erase()
    test_merge_and_absorb()
    test_export_clone()


if __name__ == "__main__":
    main()
