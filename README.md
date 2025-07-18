# protdict

\\

A flexible key-value store for Python with fine-grained protection, type locking, and utility operations. Ideal when you need a dictionary-like object but want built-in safeguards against accidental overwrites, deletions, or type mismatches.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)

   * [Protected vs. Unprotected](#protected-vs-unprotected)
   * [Type Locking](#type-locking)
   * [Kwarg Protections](#kwarg-protections)
   * [O‑family Methods (](#o-family-methods)[`oset`](#o-family-methods)[, ](#o-family-methods)[`oerase`](#o-family-methods)[, ](#o-family-methods)[`ounprotect`](#o-family-methods)[)](#o-family-methods)
5. [API Reference](#api-reference)
6. [Advanced Operations](#advanced-operations)

   * [`merge_dict`](#merge_dict--absorb)[ & ](#merge_dict--absorb)[`absorb`](#merge_dict--absorb)
   * [`export`](#export--clone)[ & ](#export--clone)[`clone`](#export--clone)
7. [Examples](#examples)
8. [Testing](#testing)
9. [Contributing](#contributing)
10. [License](#license)

---

## Features

* **Attribute Access**: Access keys via `d.key` or `d["key"]`.
* **Protection**: Mark entries as protected to prevent deletion or mutation.
* **Type Locking**: Enforce that values remain the same type once set.
* **Kwarg Initialization**: Treat constructor kwargs as protected (and optionally type-locked) from the start.
* **O‑Methods**: `oset`, `oerase`, `ounprotect` for overriding protections when you really mean it.
* **Merge & Absorb**: Combine or absorb another `Data` object or plain dict with fine-grained control.
* **Export & Clone**: Serialize to a tags-based dict and rebuild the same protections and types.

---

## Installation

Install from PyPI:

```bash
pip install protdict
```

Or install the latest from GitHub:

```bash
git clone https://github.com/Kmdjr/protdict
cd protdict
pip install -e .
```

---

## Quick Start

```python
from protdict import Data

# Basic initialization
data = Data({
    'a': 1,
    'b': {'value': 2, 'tags': ['protected', 'typed']},
}, b=10)

print(data.a)       # 1
print(data.b)       # 10

# Protect / Unprotect
data.protect('a')
# data.erase('a')  # => False (protected)
data.unprotect('a')
data.erase('a')    # True

# Type Lock
data.set('x', 5)
data.add_typing('x')
# data.set('x', 'five')  # prints type-lock error

data.oset('x', 'five')  # override lock, sets to 'five'
print(data.x)      # 'five'
```

---

## Core Concepts

### Protected vs. Unprotected

* **Unprotected** entries behave like normal attributes:

  * Can be overwritten with `set`.
  * Can be deleted with `erase`.
* **Protected** entries cannot be mutated or deleted by default.

  * Use `protect(name)` to mark.
  * Use `unprotect(name)` to remove protection.

### Type Locking

* Use `add_typing(name)` to lock the current type of a key.
* Locked keys reject new values of the wrong type (via `set`, prints or raises error).
* Remove with `remove_typing(name)` or clear all via `rem_all_typings()`.

### Kwarg Protections

* Any `**kwargs` passed to the constructor are automatically *protected*.
* If `initial_typing=True`, those kwargs are also locked to their initial type.

### O‑family Methods

* **`oset(name, value)`**: Overwrite even if protected or type-locked.
* **`oerase(name)`**: Force-delete any key, protected or not.
* **`ounprotect(name)`**: Remove protection unconditionally.

---

## API Reference

### `Data(data_dictionary: dict, initial_typing: bool=False, **kwargs)`

Initialize a new instance.

### `hasprop(name: str, include_protected: bool=True) -> bool`

Check existence (optionally exclude protected).

### `set(name: str, value) -> bool`

Set a value unless protected or type-locked.

### `oset(name: str, value) -> bool`

Force-set ignoring protections.

### `erase(name: str) -> bool`

Delete unless protected.

### `oerase(name: str) -> bool`

Force-delete ignoring protections.

### `add_typing(name: str, type_lock: type=None) -> bool`

Lock a key’s type.

### `remove_typing(name: str) -> bool`

Remove a key’s type lock.

### `protect(name: str) -> bool`

Mark a key protected.

### `unprotect(name: str) -> bool`

Remove protection (unless it originated from kwargs).

### `ounprotect(name: str) -> bool`

Remove protection unconditionally.

### `merge_dict(new_data: dict, overwrite_current: bool=False, protect_current: bool=False, protect_new_added_keys: bool=False) -> bool`

Merge in new key/values with options.

### `absorb(other: Data, include_protected: bool=False, overwrite: bool=False) -> bool`

Copy keys from another `Data` instance.

### `export() -> dict`

Dump into a plain dict with tags that can be used as then data\_dictionary input to reconstruct an exact copy (see clone() for this in action.)

### `clone() -> Data`

Create a deep clone preserving protections and types.

*For full method list, see the docstrings in* `src/protdict/data_class.py`.

---

## Advanced Operations

See `merge_dict` & `absorb` for bulk updates.
Use `export()` + `Data(exported_dict)` to round-trip state and metadata.

---

## Examples

For more usage patterns, see `test_suite.py` in the repository, which exercises:

* Basic init & access
* Tag handling
* Type-lock errors & overrides
* Protect/unprotect flows
* Merge & absorb scenarios
* Dunder methods (`[], in, len, iter`, etc.)
* Utility functions in `functional_utils`

---

## Testing

Run the provided smoke tests:

```bash
python test_suite.py
```

For a more structured suite, import tests into `pytest`:

```bash
pip install pytest
pytest
```

---

## Contributing

1. Fork the repo
2. Create a new branch (`git checkout -b feature/YourThing`)
3. Add tests in `test_suite.py`
4. Make your changes
5. Update `CHANGELOG.md` and bump `version` in `setup.cfg` & `__init__.py`
6. Submit a pull request

Please follow PEP8 and write docstring updates as needed.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
