# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Loader subclasses know how to load classes under their entry point which conform
to their subclasses.
'''
import pkg_resources
from typing import List

class Entrypoint(object):
    '''
    Uses the pkg_resources.iter_entry_points on the ENTRY_POINT of the class
    '''

    ENTRY_POINT = 'util.entrypoint'

    @classmethod
    def load(cls, loading=None):
        '''
        Loads all installed loading and returns them as a list. Sources to be
        loaded should be registered to ENTRY_POINT via setuptools.
        '''
        loading_classes = []
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            loaded = i.load()
            if issubclass(loaded, cls):
                loading_classes.append(loaded)
                if loading is not None and i.name == loading:
                    return loaded
        if loading is not None:
            raise KeyError('%s was not found in (%s)' % \
                    (repr(loading), ', '.join(list(map(str, loading_classes)))))
        return loading_classes

    @classmethod
    def load_multiple(cls, to_load: List[str]):
        '''
        Loads each class requested without instantiating it.
        '''
        return {name: cls.load(name) for name in to_load}
