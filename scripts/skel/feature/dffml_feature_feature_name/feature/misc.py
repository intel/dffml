# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Docstring for this miscellaneous feature.
'''
from typing import Type

from dffml.feature import Feature

from .log import LOGGER

class MiscFeature(Feature):
    '''
    Explination of this feature for users of the CLI
    '''

    LOGGER = LOGGER.getChild('MiscFeature')

    NAME: str = 'misc'

    def dtype(self) -> Type:
        '''
        Models need to know a Feature's datatype the python data type.
        '''
        return int

    def length(self) -> int:
        '''
        Models need to know a Feature's length, 1 means single value, more than
        that is the length of the array calc returns.
        '''
        return 1

    async def applicable(self, data) -> bool:
        '''
        Check if it makes sense to run the feature on this key
        '''
        return data.src_url != 'key_that_causes_failure_for_all'

    async def fetch(self, data):
        '''
        Fetch retrieves any additional information about the software we are
        evaluating. Any data fetched should be stored in tempdir().
        '''
        await data.data.set('feature_name_misc',
                            '%s + feature_name_misc' % (data.src_url,))

    async def parse(self, data):
        '''
        Parse the data we downloaded in fetch() into a usable form.
        '''
        pass

    async def calc(self, data):
        '''
        Calculates the score for this feature based on data found by parse().
        '''
        return await data.data.get('feature_name_misc')

    async def setUp(self, data):
        '''
        Preform setup
        '''
        pass

    async def tearDown(self, data, error=False):
        '''
        Release any post calculation resources
        '''
        pass

    async def open(self):
        '''
        Opens any resources needed
        '''
        pass

    async def close(self):
        '''
        Closes any opened resources
        '''
        pass
