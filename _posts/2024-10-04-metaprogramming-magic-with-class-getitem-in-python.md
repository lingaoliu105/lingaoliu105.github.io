---
title: "Metaprogramming Magic with __class_getitem__ in Python"
layout: single
post-image: ""
description: "Unlock the power of metaprogramming in Python using __class_getitem__ to create dynamic, flexible classes. Learn how this special method enables advanced techniques and enhances code functionality."
tags:
- __class_getitem__
- class_getitem
- code functionality
- dynamic classes
- metaprogramming
- python
- with
---

## Metaprogramming Magic with `__class_getitem__` in Python

Python has long been celebrated for its simplicity and readability. Yet, beneath its clean syntax lies a powerful system for metaprogramming — the ability of a program to manipulate or generate other programs (or itself) as data. One lesser-known but fascinating feature that supports this capability is the `__class_getitem__` method. Introduced in Python 3.7 and formalized in [PEP 560](https://peps.python.org/pep-0560/), this method allows developers to customize how classes behave when indexed using square brackets, such as in `MyClass[int]`.

This feature was primarily designed to support type hints and the typing module, particularly generic types. But it can also be used creatively to build more expressive and dynamic APIs. In this post, we'll explore how `__class_getitem__` works, why it's useful, and how to use it in your own code.

## Understanding `__class_getitem__`

At first glance, using square brackets on a class like `MyClass[int]` might look like indexing an instance, but in Python, this syntax is interpreted as calling a class-level `__getitem__` method. However, classes themselves don't have a `__getitem__` — instead, Python looks for a special method called `__class_getitem__` to handle this.

Before `__class_getitem__`, indexing a class would raise a `TypeError`. Now, by defining this method on a class, you can control how it responds to such syntax. This is particularly useful for classes that represent generic types, as it allows them to return a specialized version of the class based on the type parameter provided.

Here’s a minimal example:

```python
class MyGeneric:
    def __class_getitem__(cls, key):
        print(f"Accessing {cls.__name__} with key: {key}")
        return type(f"{cls.__name__}[{key.__name__}]", (), {'type_arg': key})

MyGeneric[int]
```

When `MyGeneric[int]` is called, Python invokes `__class_getitem__` with `cls` as `MyGeneric` and `key` as `int`. The method returns a new class dynamically generated with the type argument stored as a class attribute.

This is how the `List[int]`, `Dict[str, int]`, and other generic type annotations in the `typing` module work under the hood.

## Use Cases in Type Hints

One of the most common applications of `__class_getitem__` is in the `typing` module. Python's type hinting system makes heavy use of generics, and `__class_getitem__` is what allows `List`, `Set`, and `Dict` to be used with type parameters.

For example:

```python
from typing import List

List[int]
```

Behind the scenes, `List.__class_getitem__` is called with `int` as the type argument. This returns a `typing._GenericAlias` object representing the specialized type `List[int]`. This object isn’t an instance of `List`, but rather a type expression used by static type checkers like `mypy`.

This mechanism allows developers to build their own generic type systems or libraries that work seamlessly with Python’s type hinting infrastructure.

## Implementing Custom Generic Classes

You can use `__class_getitem__` to create your own generic classes, which can be used in type hints and also carry runtime behavior. Let's say you're building a data structure and want to track the type of data stored inside it.

Here’s a basic example:

```python
from typing import Any

class Container:
    def __class_getitem__(cls, item_type):
        cls._type = item_type
        return cls

# Usage
IntContainer = Container[int]
string_container = Container[str]

print(IntContainer._type)  # <class 'int'>
print(string_container._type)  # <class 'str'>
```

In this case, we’re storing the type argument directly on the class. While simplistic, this pattern is the foundation for more advanced type-driven behaviors.

Note that this approach modifies the original class rather than returning a new one. In practice, you often want to return a new type (or a wrapper) to avoid polluting the base `Container` class.

## Avoiding Class Pollution

Modifying the class directly can lead to unexpected behavior if multiple type arguments are used. To avoid this, a better approach is to return a new class or a proxy object that encapsulates the type argument.

Here’s a more robust version:

```python
class BaseContainer:
    pass

class ContainerMeta(type):
    def __getitem__(cls, item_type):
        name = f"{cls.__name__}[{item_type.__name__}]"
        return type(name, (BaseContainer,), {'_type': item_type})

class Container(metaclass=ContainerMeta):
    pass

# Usage
int_container = Container[int]
print(int_container._type)  # <class 'int'>
print(int_container.__name__)  # Container[int]

str_container = Container[str]
print(str_container._type)  # <class 'str'>
print(str_container.__name__)  # Container[str]
```

In this example, the metaclass `ContainerMeta` controls the behavior of `__class_getitem__`. Each call to `Container[type]` creates a new unique class derived from `BaseContainer`, preserving isolation between different type instantiations.

## Interaction with Static Type Checkers

It's important to note that `__class_getitem__` is primarily used for static type hints. While it can be used at runtime, many type checkers like `mypy` or `pyright