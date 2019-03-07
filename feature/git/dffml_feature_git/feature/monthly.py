'''Checkout each month Feature'''
import abc

from dffml.feature import Data

from .git import GitFeature

class GitMonthlyFeature(GitFeature):
    '''
    Checkout the repo each month
    '''

    NAME: str = 'cloc'

    async def git_parse(self, data):
        i = -1
        for current in range(0, self.LENGTH * self.FREQUENCY.MONTHS,
                self.FREQUENCY.MONTHS):
            last_commit = (await data.git.check_output('log',
                '--pretty=oneline',
                '--no-abbrev-commit', '-n', '1', '--date', 'relative',
                '--before', '%d months' % (current))).strip()
            i += 1
            if len(last_commit) == 0:
                continue
            last_commit = last_commit.split()[0]
            await data.git.check_output('reset', '--hard', last_commit)
            await data.git.checkout(last_commit)
            await self.month_parse(data, i)

    @abc.abstractmethod
    async def month_parse(self, data: Data, i: int):
        '''
        Parse the git repo this month
        '''
        pass
