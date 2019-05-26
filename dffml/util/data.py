"""
Various helper functions for manipulating python data structures and values
"""
from functools import wraps


def merge(one, two):
    for key, value in two.items():
        if key in one and isinstance(value, dict):
            merge(one[key], two[key])
        else:
            one[key] = two[key]


def traverse_config_set(target, *args):
    """
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    """
    # Seperate the path down from the value to set
    path, value = args[:-1], args[-1]
    current = target
    last = target
    for level in path:
        if not level in current:
            current[level] = {"arg": None, "config": {}}
        last = current[level]
        current = last["config"]
    last["arg"] = value
    return target


def traverse_config_get(target, *args):
    """
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    """
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last["config"]
    return last["arg"]


def ignore_args(func):
    """
    Decorator to call the decorated function without any arguments passed to it.
    """

    @wraps(func)
    def wrapper(*_args, **_kwargs):
        return func()

    return wrapper
