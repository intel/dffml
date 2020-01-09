"""
Various helper functions for manipulating python data structures and values
"""
import os
import inspect
import pydoc
import inspect
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


def traverse_get(target, *args):
    """
    Travel down through a dict
    >>> traverse_get({"one": {"two": 3}}, ["one", "two"])
    3
    """
    current = target
    for level in args:
        current = current[level]
    return current

def traverse_set(target,*args):
    """
    >>> traverse_set({"one": {"two": 3}}, ["one", "two"])
    """


def ignore_args(func):
    """
    Decorator to call the decorated function without any arguments passed to it.
    """

    @wraps(func)
    def wrapper(*_args, **_kwargs):
        return func()

    return wrapper


# STANDARD_TYPES Will be the type names which are applicable across languages
# used to transform types from one language into anothers
STANDARD_TYPES = {"Dict": "map", "List": "array", "Any": "generic"}
STANDARD_TYPES_REVERSED = dict(
    zip(STANDARD_TYPES.values(), STANDARD_TYPES.keys())
)


def type_lookup(typename):
    if typename in STANDARD_TYPES_REVERSED:
        typename = f"typing.{STANDARD_TYPES_REVERSED[typename]}"
    # TODO(security) Make sure pydoc.locate won't blow up in our face ever
    typeof = pydoc.locate(typename)
    if typeof is None:
        raise TypeError(typename)
    return typeof


def export_value(obj, key, value):
    # export and _asdict are not classmethods
    if inspect.isclass(value):
        obj[key] = value.__qualname__
    elif hasattr(value, "export"):
        obj[key] = value.export()
    elif hasattr(value, "_asdict"):
        obj[key] = value._asdict()
    elif getattr(value, "__module__", None) == "typing":
        obj[key] = STANDARD_TYPES.get(
            str(value).replace("typing.", ""), "generic"
        )


def export_list(iterable):
    for i, value in enumerate(iterable):
        export_value(iterable, i, value)
        if isinstance(iterable[i], dict):
            iterable[i] = export_dict(**iterable[i])
        elif isinstance(value, list):
            iterable[i] = export_list(iterable[i])
    return iterable


def export_dict(**kwargs):
    """
    Return the dict given as kwargs but first recurse into each element and call
    its export or _asdict function if it is not a serializable type.
    """
    for key, value in kwargs.items():
        export_value(kwargs, key, value)
        if isinstance(kwargs[key], dict):
            kwargs[key] = export_dict(**kwargs[key])
        elif isinstance(kwargs[key], list):
            kwargs[key] = export_list(kwargs[key])
    return kwargs

def explore_directories(path_dict:str):
    """
    path_dict :
        {
            "hello":"there",
            "deadbeef" : path_to_deadbeef
        }
    """
    for key,val in path_dict.items():
        if(os.path.isdir(val)):
            temp_path_dict = {}
            for root,dirs,files in os.walk(val):
                # adding dirs
                temp_path_dict.update(
                    {
                        _dir:os.path.join(root,_dir)
                            for _dir in dirs
                    }
                )
                #adding files
                temp_path_dict.update(
                    {
                        _file.split('.')[0]:os.path.join(root,_file)
                            for  _file in files
                    }
                )
                break
            explore_directories(temp_path_dict)
            path_dict[key]=temp_path_dict
    return path_dict

async def nested_apply(target,func):
    """
    """
    for key,val in target.items():
        if isinstance(val,dict):
            target[key]=await nested_apply(val,func)
        else:
            if(inspect.iscoroutinefunction(func)):
                target[key]=await func(val)
            else:
                target[key]= func(val)
    return target
