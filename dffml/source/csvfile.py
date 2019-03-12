# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Loads repos from a csv file, using columns as features
'''
import os
import csv
import ast
import urllib.request

from ..repo import Repo
from .memory import MemorySource
from .file import FileSource

from .log import LOGGER

LOGGER = LOGGER.getChild('csv')

csv.register_dialect('strip', skipinitialspace=True)

class CSVSource(FileSource, MemorySource):
    '''
    Uses a CSV file as the source of repo feature data
    '''

    async def load_fd(self, fd):
        '''
        Parses a CSV stream into Repo instances
        '''
        i = 0
        self.mem = {}
        for data in csv.DictReader(fd, dialect='strip'):
            for key, value in data.items():
                try:
                    data[key] = ast.literal_eval(value)
                except (SyntaxError, ValueError):
                    data[key] = value
            if not data.get('classification') is None:
                classification = data['classification']
                del data['classification']
                if not data.get('prediction') is None and not data.get('confidence') is None:
                    prediction = data['prediction']
                    del data['prediction']
                    confidence = data['confidence']
                    del data['confidence']
                    repo = Repo(str(i), data={'features': data,
                    'classification': str(classification), 'prediction': {'classification':str(prediction),'confidence': str(confidence)}})
                else:
                    repo = Repo(str(i), data={'features': data,
                    'classification': str(classification)})

            else:
                repo = Repo(str(i), data={'features': data})
            i += 1
            self.mem[repo.src_url] = repo
        LOGGER.debug('%r loaded %d records', self, len(self.mem))

    async def dump_fd(self, fd):
        '''
        Dumps data into a CSV stream
        '''
        samplekey = list(self.mem.keys())[0]
        sampledata = self.mem[samplekey]
        fieldnames = list(sampledata.dict()['features'].keys()) + ['classification']
        if 'prediction' in sampledata.dict():
            fieldnames += ['prediction','confidence']
        writer = csv.DictWriter(fd, fieldnames=fieldnames)
        writer.writeheader()
        for data in self.mem.values():
            row = {}
            for key,value in data.dict()['features'].items():
                row[key] = value

            row['classification'] = data.dict()['classification']
            if 'prediction' in data.dict():
                row['prediction'] = data.dict()['prediction']['classification']
                row['confidence'] = data.dict()['prediction']['confidence']
            writer.writerow(row)
        LOGGER.debug('%r saved %d records', self, len(self.mem))
