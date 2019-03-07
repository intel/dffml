'''Authors Feature'''
from dffml_feature_git.util.proc import create, stop, check_output

from .git import GitFeature

class GitAuthorsFeature(GitFeature):
    '''
    Counts the number of unique authors within the frequency.
    '''

    NAME: str = 'authors'

    async def git_parse(self, data):
        authors = []
        for current in range(0, self.LENGTH * self.FREQUENCY.MONTHS,
                self.FREQUENCY.MONTHS):
            current_authors = {}
            proc = await data.git.create('log',
                    '--pretty=format:%aN',
                    '--date', 'relative',
                    '--before', '%d months' % (current),
                    '--after', '%d months' % (current + \
                            self.FREQUENCY.MONTHS))
            while not proc.stdout.at_eof():
                line = await proc.stdout.readline()
                line = line.decode(errors='ignore').strip()
                if line != '':
                    current_authors.setdefault(line, 0)
            await stop(proc)
            authors.append(len(current_authors))
        data.temp.setdefault(self.NAME, authors)
        await data.data.set(self.NAME, await self.calc(data))

    async def calc(self, data):
        return data.temp.get(self.NAME)
