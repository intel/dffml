'''
Unorganized metrics
'''
import os
import asyncio

from dffml.metric import Metric, Data

from dffml_metric_git.metric.git import GitMetric
from dffml_metric_git.util.proc import check_output, create, stop

class MetricStub(Metric):

    def dtype(self):
        return bool

    def length(self):
        return 1

class Progess(MetricStub):

    NAME: str = 'progress'

    async def parse(self, data: Data):
        for i in range(0, 20):
            await asyncio.sleep(0.05)
            await data.log('Hi %2.5f', i * 0.05)
        await data.data.set('progress', True)

    async def calc(self, data: Data) -> bool:
        return await data.data.get('progress')

class Grader(MetricStub):

    NAME: str = 'grade'

    async def calc(self, data: Data) -> str:
        return 'A+'

class CoverageMetric(GitMetric):
    '''
    Requirements:
        pip install coverage
    '''

    NAME: str = 'unit tests'

    def dtype(self):
        return bool

    def length(self):
        return 1

    async def applicable(self, data: Data) -> bool:
        if not await super().applicable(data):
            return False
        await super().fetch(data)
        if not os.path.isfile(os.path.join(data.git.cwd, 'setup.py')):
            return False
        await data.log('has setup.py')
        return True
        # await data.log('running pip install')

    async def git_parse(self, data: Data):
        try:
            proc = await create('coverage', 'run', 'setup.py', 'test',
                    cwd=data.git.cwd)
            while proc.returncode is None:
                done, pending = await asyncio.wait(
                        [proc.stdout.readline(), proc.stderr.readline()],
                        timeout=1, return_when=asyncio.FIRST_COMPLETED)
                [fut.cancel() for fut in pending]
                stream = ''.join([fut.result().decode(errors='ignore') \
                        for fut in done])
                await data.log('unittest run: %s', stream.strip())
            exit_code, proc = await stop(proc)
            await data.log('unittest exit code: %r', exit_code)
            await data.data.set('unittest', exit_code)
            report = await check_output('coverage', 'report', '-m',
                    cwd=data.git.cwd)
            await data.log('coverage report: %s', report)
            await data.data.set('coverage_report', report)
            await check_output('coverage', 'html', cwd=data.git.cwd)
            # TODO
            # shutil.make_archive(archive_name, 'gztar', root_dir)
        except RuntimeError as err:
            await data.log('Error in applicable: %r', err)
            raise

    async def calc(self, data: Data):
        return {
                'unittest': await data.data.get('unittest', 0),
                'report': await data.data.get('coverage_report', 0),
                }

class YarnTestMetric(GitMetric):
    '''
    Requirements:
        yarn add
    '''

    NAME: str = 'unit tests'

    def dtype(self):
        return bool

    def length(self):
        return 1

    async def applicable(self, data: Data) -> bool:
        if not await super().applicable(data):
            return False
        await super().fetch(data)
        if not os.path.isfile(os.path.join(data.git.cwd, 'package.json')):
            return False
        await data.log('has package.json')
        await data.log('running yarn install')
        try:
            proc = await create('yarn', 'install', cwd=data.git.cwd)
            while proc.returncode is None:
                done, pending = await asyncio.wait(
                        [proc.stdout.readline(),
                            proc.stderr.readline()],
                        timeout=1,
                        return_when=asyncio.FIRST_COMPLETED)
                [fut.cancel() for fut in pending]
                stream = ''.join([fut.result().decode(errors='ignore') \
                        for fut in done])
                await data.log('yarn install: %s', stream.strip())
            await stop(proc)
        except RuntimeError as err:
            await data.log('Error in applicable: %r', err)
            raise
        return True

    async def git_parse(self, data: Data):
        try:
            proc = await create('yarn', 'run', 'test', cwd=data.git.cwd)
            while proc.returncode is None:
                done, pending = await asyncio.wait(
                        [proc.stdout.readline(),
                            proc.stderr.readline()],
                        timeout=1,
                        return_when=asyncio.FIRST_COMPLETED)
                [fut.cancel() for fut in pending]
                stream = ''.join([fut.result().decode(errors='ignore') \
                        for fut in done])
                await data.log('yarn test: %s', stream.strip())
            exit_code, proc = await stop(proc)
            await data.data.set('yarn_test', exit_code)
            await data.log('yarn test exit code: %r', exit_code)
        except RuntimeError as err:
            await data.log('Error in applicable: %r', err)
            raise

    async def calc(self, data: Data):
        return await data.data.get('yarn_test', 0)
