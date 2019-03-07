'''Commits Feature'''
from dffml_feature_git.util.proc import stop

from .git import GitFeature

class GitCommitsFeature(GitFeature):
    '''
    Counts the number of commits within the frequency.
    '''

    NAME: str = 'commits'

    async def git_parse(self, data):
        commits = []
        for current in range(0, self.LENGTH * self.FREQUENCY.MONTHS,
                self.FREQUENCY.MONTHS):
            lines = 0
            proc = await data.git.create('log',
                    '--oneline', '--date', 'relative',
                    '--before', '%d months' % (current),
                    '--after', '%d months' % (current + \
                            self.FREQUENCY.MONTHS))
            while not proc.stdout.at_eof():
                if (await proc.stdout.readline()) != b'':
                    lines += 1
            commits.append(lines)
            await stop(proc)
        data.temp.setdefault('commits', commits)
        await data.data.set('commits', await self.calc(data))

    async def calc(self, data):
        return data.temp.get('commits')
