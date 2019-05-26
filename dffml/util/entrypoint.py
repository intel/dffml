# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loader subclasses know how to load classes under their entry point which conform
to their subclasses.
"""
import copy
import pkg_resources
from typing import List, Dict


class MissingLabel(Exception):
    pass  # pragma: no cover


def entry_point(label):
    """
    If a class if going to be registered with setuptools as an entry_point it
    must have the label it will be registered under associated with it via this
    decorator.

    This decorator sets the ENTRY_POINT_ORIG_LABEL and ENTRY_POINT_LABEL class
    proprieties to the same value, label.

    For example in setup.py (dict would be the setup() function in this case).
    EntrypointSubclassClass in this case needs to have this decorator applied to
    it with label set to mylabel.
    >>> dict(
    >>>     entry_points={
    >>>         'dffml.entrypoint': [
    >>>             'mylabel = module.path.to:EntrypointSubclassClass',
    >>>         ]
    >>>     }
    >>> )
    >>> @entry_point('mylabel')
    >>> class EntrypointSubclassClass(Entrypoint): pass
    """

    def add_entry_point_label(cls):
        cls.ENTRY_POINT_ORIG_LABEL = label
        cls.ENTRY_POINT_LABEL = label
        return cls

    return add_entry_point_label


def base_entry_point(entrypoint, *args):
    """
    Any class which subclasses from Entrypoint needs this decorator applied to
    it. The decorator sets the ENTRY_POINT and ENTRY_POINT_NAME proprieties on
    the class.

    This allows the load() classmethod to be called to load subclasses of the
    class being decorated. This is how the subclasses get loaded via the
    entry point system by calling BaseClass.load().

    ENTRY_POINT_NAME corresponds to the command line argument and config file
    reference to the class. It comes from all arguments after the entrypoint
    argument (first argument) is a list which would turn into an command line
    argument if it were joined with hyphens.
    >>> dict(
    >>>     entry_points={
    >>>         'dffml.entrypoint': [ # Same as ENTRY_POINT
    >>>             'mylabel = module.path.to:EntrypointSubclassClass',
    >>>         ]
    >>>     }
    >>> )
    >>> @base_entry_point('dffml.entrypoint', 'entrypoint')
    >>> class BaseEntrypointSubclassClass(Entrypoint): pass
    """

    def add_entry_point_and_name(cls):
        cls.ENTRY_POINT = entrypoint
        cls.ENTRY_POINT_NAME = list(args)
        return cls

    return add_entry_point_and_name


class Entrypoint(object):
    """
    Uses the pkg_resources.iter_entry_points on the ENTRY_POINT of the class
    """

    ENTRY_POINT = "util.entrypoint"
    # Label is for configuration. Sometimes multiple of the same classes will be
    # loaded. They need to determine which config options are meant for which
    # class. Therefore a label is applied to each class after it is loaded. If
    # there is only one instance of any type of a certain entry point a label
    # need not be applied because that class will know any thing that applies to
    # configuration for its entry point belongs solely to it.
    ENTRY_POINT_LABEL = ""

    @classmethod
    def load(cls, loading=None):
        """
        Loads all installed loading and returns them as a list. Sources to be
        loaded should be registered to ENTRY_POINT via setuptools.
        """
        loaded_names = []
        loading_classes = []
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            loaded = i.load()
            loaded.ENTRY_POINT_LABEL = i.name
            if issubclass(loaded, cls):
                loaded_names.append(i.name)
                loading_classes.append(loaded)
                if loading is not None and i.name == loading:
                    return loaded
        if loading is not None:
            raise KeyError(
                "%s was not found in (%s)"
                % (repr(loading), ", ".join(loaded_names))
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
        loaded = copy.deepcopy(cls.load(loading))
        loaded.ENTRY_POINT_LABEL = label
        return loaded
