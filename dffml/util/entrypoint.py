# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loader subclasses know how to load classes under their entry point which conform
to their subclasses.
"""
import os
import sys
import inspect
import pathlib
import importlib
import traceback
import pkg_resources
from typing import List, Dict, Union, Optional, Iterator, Any

from .log import LOGGER

LOGGER = LOGGER.getChild("entrypoint")


class EntrypointNotFound(Exception):
    pass  # pragma: no cover


class MissingLabel(Exception):
    pass  # pragma: no cover


def load(
    *args: str, relative: Optional[Union[str, pathlib.Path]] = None
) -> Iterator[Any]:
    """
    Load objects given the entrypoint formatted path to the object. Roughly how
    the python stdlib docs say entrypoint loading works.
    """
    # Push current directory into front of path so we can run things
    # relative to where we are in the shell
    if relative is not None:
        if relative == True:
            relative = os.getcwd()
        # str() in case of Path object
        sys.path.insert(0, str(relative))
    try:
        for entry in args:
            modname, qualname_separator, qualname = entry.partition(":")
            obj = importlib.import_module(modname)
            for attr in qualname.split("."):
                if hasattr(obj, "__getitem__"):
                    obj = obj[attr]
                else:
                    obj = getattr(obj, attr)
            yield obj
    finally:
        if relative is not None:
            sys.path.pop(0)


def entrypoint(label):
    """
    If a class if going to be registered with setuptools as an entrypoint it
    must have the label it will be registered under associated with it via this
    decorator.

    This decorator sets the ENTRY_POINT_ORIG_LABEL and ENTRY_POINT_LABEL class
    proprieties to the same value, label.

    Examples
    --------

    >>> from dffml import entrypoint, Entrypoint
    >>>
    >>> @entrypoint('mylabel')
    ... class EntrypointSubclassClass(Entrypoint): pass

    In setup.py, EntrypointSubclassClass needs to have this decorator applied to
    it with label set to mylabel.

    .. code-block:: python

            entry_points={
                'dffml.entrypoint': [
                    'mylabel = module.path.to:EntrypointSubclassClass',
                ]
            }

    """

    def add_entry_point_label(cls):
        cls.ENTRY_POINT_ORIG_LABEL = label
        cls.ENTRY_POINT_LABEL = label
        return cls

    return add_entry_point_label


def base_entry_point(entrypoint, *args):
    """
    Any class which subclasses from Entrypoint needs this decorator applied to
    it. The decorator sets the ENTRYPOINT and ENTRY_POINT_NAME properties on
    the class.

    This allows the load() classmethod to be called to load subclasses of the
    class being decorated. This is how the subclasses get loaded via the
    entry point system by calling BaseClass.load().

    ENTRY_POINT_NAME corresponds to the command line argument and config file
    reference to the class. It comes from all arguments after the entrypoint
    argument (first argument) is a list which would turn into an command line
    argument if it were joined with hyphens.

    Examples
    --------

    >>> from dffml import base_entry_point, Entrypoint
    >>>
    >>> @base_entry_point('dffml.entrypoint', 'entrypoint')
    ... class BaseEntrypointSubclassClass(Entrypoint): pass

    .. code-block:: python

            entry_points={
                # dffml.entrypoint = ENTRYPOINT
                'dffml.entrypoint': [
                    'mylabel = module.path.to:EntrypointSubclassClass',
                ]
            }
    """

    def add_entry_point_and_name(cls):
        cls.ENTRYPOINT = entrypoint
        cls.ENTRY_POINT_NAME = list(args)
        return cls

    return add_entry_point_and_name


class Entrypoint(object):
    """
    Uses the pkg_resources.iter_entry_points on the ENTRYPOINT of the class
    """

    ENTRYPOINT = "util.entrypoint"
    # Label is for configuration. Sometimes multiple of the same classes will be
    # loaded. They need to determine which config options are meant for which
    # class. Therefore a label is applied to each class after it is loaded. If
    # there is only one instance of any type of a certain entry point a label
    # need not be applied because that class will know any thing that applies to
    # configuration for its entry point belongs solely to it.
    ENTRY_POINT_LABEL = ""

    @classmethod
    def load(cls, loading=None, entrypoint=None):
        """
        Loads all installed loading and returns them as a list. Sources to be
        loaded should be registered to ENTRYPOINT via setuptools.
        """
        if inspect.isclass(loading) and issubclass(loading, cls):
            return loading
        if entrypoint is None:
            entrypoint = cls.ENTRYPOINT
        try:
            # Loading from entrypoint if ":" is in name
            if loading is not None and ":" in loading:
                return next(load(loading, relative=True))
        except:
            LOGGER.error("Failed to load %r for %r", loading, cls.ENTRYPOINT)
            raise
        # Load from registered entrypoints otherwise
        loaded_names = []
        loading_classes = []
        for i in pkg_resources.iter_entry_points(entrypoint):
            loaded_names.append(i.name)
            if loading is not None and i.name != loading:
                continue
            try:
                loaded = i.load()
            except Exception as error:
                print(
                    f"Error loading {cls.ENTRYPOINT}.{i.name}: {traceback.format_exc().strip()}",
                    file=sys.stderr,
                    flush=True,
                )
                raise
            loaded.ENTRY_POINT_LABEL = i.name
            loading_classes.append(loaded)
            if loading is not None and i.name == loading:
                return loaded
        if loading is not None:
            raise EntrypointNotFound(
                f"{loading!r} was not found in: {loaded_names}"
            )
        return loading_classes

    @classmethod
    def load_multiple(cls, to_load: List[str]):
        """
        Loads each class requested without instantiating it.
        """
        return {name: cls.load(name) for name in to_load}

    @classmethod
    def load_dict(cls, to_load: Dict[str, str]):
        """
        Loads each class tagged with the key it should be accessed by without
        instantiating it.
        """
        return {key: cls.load(name) for key, name in to_load.items()}

    @classmethod
    def load_labeled(cls, label_and_loading):
        if "=" in label_and_loading:
            label, loading = label_and_loading.split("=", maxsplit=1)
        else:
            raise MissingLabel(
                "%r is missing a label. "
                "Correct syntax: label=%s"
                % (label_and_loading, label_and_loading)
            )

        loaded = cls.load(loading)
        return type(
            loaded.__qualname__, (loaded,), {"ENTRY_POINT_LABEL": label}
        )
