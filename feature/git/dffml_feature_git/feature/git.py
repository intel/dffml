'''Git based features'''
import os
import sys
import shutil
import asyncio
import tempfile
from asyncio.subprocess import PIPE
from typing import Type

from dffml.feature import Feature
from dffml.feature.feature import Quarterly
from dffml.util.tempdir import TempDir

from dffml_feature_git.util.proc import check_output, create, stop
from .log import LOGGER

LOGGER = LOGGER.getChild('git')

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

class Git(object):

    TIMEOUT = 10
    DEFAULT_MAIN_BRANCH = 'master'
    NO_SPACE = 'No space left on device'

    def __init__(self, tempdir: TempDir, cwd: str = '',
            binary: str = 'git') -> None:
        self.tempdir = tempdir
        self.cwd = cwd if len(cwd) else ''
        self.binary = binary
        self.main_branch: str = ''

    async def _create(self, *args, **kwargs):
        return await create(self.binary, *args, **kwargs, cwd=self.cwd)

    async def create(self, *args, **kwargs):
        return await self._create(*args, **kwargs)

    async def check_output(self, *args, **kwargs):
        return await check_output(self.binary, *args, **kwargs, cwd=self.cwd)

    async def checkout(self, branch: str = ''):
        if not branch:
            branch = self.main_branch
        return await self.check_output('checkout', '-f', branch)

    async def ls_remote(self, src_url):
        return (await self._ls_remote(src_url) or await self._svn_info(src_url))

    async def _svn_info(self, src_url):
        env = os.environ.copy()
        env['git_askpass'] = 'echo'
        proc = await create('svn', 'info', src_url, env=env)
        done, pending = await asyncio.wait(
                [proc.stdout.read(), proc.stderr.read()],
                timeout=self.TIMEOUT,
                return_when=asyncio.FIRST_COMPLETED)
        [fut.cancel() for fut in pending]
        first = ''.join([fut.result().decode(errors='ignore') \
                for fut in done])
        LOGGER.debug('svn info result: %r', first)
        try:
            proc.kill()
        except:
            pass
        exit_code = await proc.wait()
        if exit_code != 0:
            return False
        return True

    async def _ls_remote(self, src_url):
        with tempfile.TemporaryDirectory(prefix='git_') as tempdir:
            env = os.environ.copy()
            env['git_askpass'] = 'echo'
            proc = await create(self.binary, 'ls-remote', '--exit-code',
                        src_url, '-h', 'HEAD', env=env, cwd=tempdir)
            done, pending = await asyncio.wait(
                    [proc.stdout.read(8), proc.stderr.read(5)],
                    timeout=self.TIMEOUT,
                    return_when=asyncio.FIRST_COMPLETED)
            [fut.cancel() for fut in pending]
            first = ''.join([fut.result().decode(errors='ignore') \
                    for fut in done])
            LOGGER.debug('ls-remote result: %r', first)
            if first.startswith('fatal'):
                LOGGER.debug('ls-remote result: fatal%s', await
                        proc.stderr.read())
                await proc.wait()
                return False
            elif first.startswith('Username'):
                LOGGER.debug('ls-remote got auth challenge')
                proc.kill()
                await proc.wait()
                return False
            # TODO Configurable ls-remote timeout
            done, pending = await asyncio.wait([proc.wait()],
                    timeout=10)
            cancelled = bool(len([fut.cancel() for fut in pending]))
            if cancelled:
                try:
                    proc.kill()
                except:
                    pass
                await proc.wait()
                return False
            else:
                exit_code = [fut.result() for fut in done][0]
                if exit_code != 0:
                    return False
            return True

    async def clone(self, src_url: str):
        if not (await self._clone(src_url) or await self._svn_clone(src_url)):
            return False
        self.main_branch = await self.infer_main_branch()
        LOGGER.debug('main branch for %r is %r', src_url, self.main_branch)
        return await self.check_output('log', '-n', '1')

    async def _svn_clone(self, src_url: str):
        if not await self._svn_info(src_url):
            return False
        env = os.environ.copy()
        env['git_askpass'] = 'echo'
        if self.cwd is False or not len(self.cwd):
            self.cwd = self.tempdir.mktempdir()
        proc = await self.create('svn', 'clone', src_url, self.cwd, env=env)
        await self._handle_clone_stream(proc, src_url)
        return True

    async def _clone(self, src_url: str):
        '''
        Downloads a git repo using the git binary. This requires that the git
        binary be in the PATH environment variable.
        '''
        if not await self._ls_remote(src_url):
            return False
        env = os.environ.copy()
        env['git_askpass'] = 'echo'
        if self.cwd is False or not len(self.cwd):
            self.cwd = self.tempdir.mktempdir()
        proc = await self.create('clone', src_url, self.cwd, env=env)
        await self._handle_clone_stream(proc, src_url)
        return True

    async def _handle_clone_stream(self, proc, src_url: str):
        error = Exception('No errors')
        try:
            done, pending = await asyncio.wait(
                    [proc.stdout.read(8), proc.stderr.read(5)],
                    timeout=self.TIMEOUT,
                    return_when=asyncio.FIRST_COMPLETED)
            [fut.cancel() for fut in pending]
            first = ''.join([str(fut.result()) for fut in done])
            LOGGER.debug('clone result: %s', first)
            if first == 'fatal':
                raise RuntimeError(await proc.stderr.readline())
            elif first == 'Username':
                raise RuntimeError('Requires authentication')
            stream = ''
            while proc.returncode is None:
                done, pending = await asyncio.wait(
                        [proc.stdout.readline(),
                            proc.stderr.readline()],
                        timeout=self.TIMEOUT,
                        return_when=asyncio.FIRST_COMPLETED)
                [fut.cancel() for fut in pending]
                stream = ''.join([fut.result().decode(errors='ignore') \
                        for fut in done])
                LOGGER.debug('clone stream %r: %r', src_url, stream)
            await stop(proc)
        except RuntimeError as err:
            error = RuntimeError(repr(stream))
            if self.NO_SPACE in stream:
                LOGGER.critical('Git clone error: %s', self.NO_SPACE)
                if os.path.isdir(self.cwd):
                    shutil.rmtree(self.cwd)
                error = RuntimeError(self.NO_SPACE)
        if str(error) != 'No errors':
            raise error

    async def infer_main_branch(self):
        try:
            branches = (await self.check_output('branch', '-r')).split('\n')
            main = [branch for branch in branches \
                    if '->' in branch][0].split()[-1]
            main = '/'.join(main.split('/')[1:])
        except Exception as error:
            LOGGER.error('Infering main branch: %s', error)
            return self.DEFAULT_MAIN_BRANCH
        return main

class GitFeature(Feature):
    '''
    Git repo based features
    '''

    NAME: str = 'git'
    INAPPLICABLE_MESSAGE = 'Not a git repo'
    LENGTH: int = 10
    FREQUENCY: int = Quarterly # type: ignore

    def dtype(self) -> Type:
        return int

    def length(self) -> int:
        return self.LENGTH

    async def applicable(self, data):
        async with (await data.mklock('git_lock')):
            # Count number of git features so that only the last feature removes
            # the directory on tearDown
            num_git_features = data.temp.get('num_git_features', 0)
            num_git_features += 1
            data.temp['num_git_features'] = num_git_features
            # If is_git_repo has been set to False then src is not a git repo
            is_git_repo = data.temp.get('is_git_repo', None)
            if not is_git_repo is None:
                return is_git_repo
            # Create an instance of the git helper so we can run git commands
            data.git = Git(TempDir())
            await data.log('Git start ls-remote')
            is_git_repo = await data.git.ls_remote(data.src_url)
            await data.log('Git ls-remote complete')
            data.temp.setdefault('is_git_repo', is_git_repo)
            return is_git_repo

    async def fetch(self, data):
        async with (await data.mklock('git_lock')):
            if not os.path.isdir(data.git.cwd):
                await data.log('Git start clone')
                await data.git.clone(data.src_url)
                await data.log('Git clone complete')
                LOGGER.debug('Cloned to: %s', data.git.cwd)

    async def parse(self, data):
        async with (await data.mklock('git_lock')):
            LOGGER.debug('%s took git_lock', self.__class__.__qualname__)
            await data.git.checkout()
            return await self.git_parse(data)

    async def tearDown(self, data):
        async with (await data.mklock('git_lock')):
            data.temp['num_git_features'] -= 1
            if data.temp['num_git_features'] == 0:
                data.git.tempdir.rmtempdirs()
