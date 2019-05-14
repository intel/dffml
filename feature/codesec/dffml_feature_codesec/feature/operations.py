import io
import os
import sys
import tarfile
import asyncio
import concurrent.futures
from typing import Dict, Any, NamedTuple

import aiohttp
from elftools.elf.descriptions import describe_e_type
from elftools.elf.elffile import ELFFile
from rpmfile import RPMFile
from rpmfile.errors import RPMError

from dffml.df.types import Stage, Operation
from dffml.df.base import op, \
                          OperationImplementationContext, \
                          OperationImplementation

from dffml_feature_git.util.proc import check_output

# pylint: disable=no-name-in-module
from .definitions import URL, \
    URLBytes, \
    RPMObject, \
    rpm_filename, \
    binary, \
    binary_is_PIE

from .log import LOGGER

url_to_urlbytes = Operation(
    name='url_to_urlbytes',
    inputs={
        'URL': URL,
    },
    outputs={
        'download': URLBytes
    },
    conditions=[])

class URLBytesObject(NamedTuple):
    URL: str
    body: bytes

    def __repr__(self):
        return '%s(URL=%s, body=%s...)' % (self.__class__.__qualname__,
                                           self.URL, self.body[:10],)

class URLToURLBytesContext(OperationImplementationContext):

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.debug('Start resp: %s', inputs['URL'])
        async with self.parent.session.get(inputs['URL']) as resp:
            return {
                'download': URLBytesObject(URL=inputs['URL'],
                                           body=await resp.read())
            }

class URLToURLBytes(OperationImplementation):

    op = url_to_urlbytes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.session = None

    def __call__(self,
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') \
            -> URLToURLBytesContext:
        return URLToURLBytesContext(self, ctx, ictx)

    async def __aenter__(self) -> 'OperationImplementationContext':
        self.client = aiohttp.ClientSession(trust_env=True)
        self.session = await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.__aexit__(exc_type, exc_value, traceback)
        self.client = None
        self.session = None

@op(inputs={
        'download': URLBytes,
    },
    outputs={
        'rpm': RPMObject
    })
async def urlbytes_to_tarfile(download: URLBytesObject):
    fileobj = io.BytesIO(download.body)
    try:
        rpm = tarfile.open(name=download.URL, fileobj=fileobj)
        return {
            'rpm': rpm.__enter__()
        }
    except Exception as error:
        LOGGER.debug('urlbytes_to_tarfile: Failed to instantiate '
                     'TarFile(%s): %s', download.URL, error)

@op(inputs={
        'download': URLBytes,
    },
    outputs={
        'rpm': RPMObject
    })
async def urlbytes_to_rpmfile(download: URLBytesObject):
    fileobj = io.BytesIO(download.body)
    try:
        rpm = RPMFile(name=download.URL, fileobj=fileobj)
        return {
            'rpm': rpm.__enter__()
        }
    except AssertionError as error:
        LOGGER.debug('urlbytes_to_rpmfile: Failed to instantiate '
                     'RPMFile(%s): %s', download.URL, error)
    except RPMError as error:
        LOGGER.debug('urlbytes_to_rpmfile: Failed to instantiate '
                     'RPMFile(%s): %s', download.URL, error)

@op(inputs={
        'rpm': RPMObject
    },
    outputs={
        'files': rpm_filename
    },
    expand=['files'])
async def files_in_rpm(rpm: RPMFile):
    return {
        'files': list(map(lambda rpminfo: rpminfo.name, rpm.getmembers()))
    }

is_binary_pie = Operation(
    name='is_binary_pie',
    inputs={
        'rpm': RPMObject,
        'filename': rpm_filename
    },
    outputs={
        'is_pie': binary_is_PIE
    },
    conditions=[])

class IsBinaryPIEContext(OperationImplementationContext):

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        rpm: RPMfile = inputs['rpm']
        filename: str = inputs['filename']
        with rpm.extractfile(filename) as handle:
            sig = handle.read(4)
            if len(sig) != 4 or sig != b'\x7fELF':
                return
            handle.seek(0)
            return {
                'is_pie': bool(describe_e_type(ELFFile(handle).header.e_type)
                               .split()[0] == 'DYN')
            }

class IsBinaryPIE(OperationImplementation):

    op = is_binary_pie

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = None
        self.pool = None
        self.__pool = None

    def __call__(self,
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') \
            -> IsBinaryPIEContext:
        return IsBinaryPIEContext(self, ctx, ictx)

    async def __aenter__(self) -> 'OperationImplementationContext':
        self.loop = asyncio.get_event_loop()
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.__pool = self.pool.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__pool.__exit__(exc_type, exc_value, traceback)
        self.__pool = None
        self.pool = None
        self.loop = None

@op(inputs={
        'rpm': RPMObject
    },
    outputs={},
    stage=Stage.CLEANUP)
async def cleanup_rpm(rpm: RPMFile):
    rpm.__exit__(None, None, None)
