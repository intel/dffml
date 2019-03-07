'''Work Feature'''
import asyncio
from asyncio.subprocess import PIPE

from dffml_feature_git.util.proc import create, stop, check_output

from .git import GitFeature

def simpsons_diversity_index(*args):
    '''
    From https://en.wikipedia.org/wiki/Diversity_index#Simpson_index

    The measure equals the probability that two entities taken at random from
    the dataset of interest represent the same type.
    '''
    if len(args) < 2:
        return 0
    def __n_times_n_minus_1(number):
        return number * (number - 1)
    try:
        return int(round((1.0 - (float(sum(map(__n_times_n_minus_1, args))) \
                / float(sum(args) * (sum(args) - 1)))) * 100.0))
    except ZeroDivisionError:
        return 0

class GitWorkFeature(GitFeature):
    '''
    Calculates the spread of authors and returns an integer between 0 and 10
    representing how varying the authorship of code is. For example a repo with
    two authors where one commits 90% of the lines of code would calculates to
    a 1. Equal work would calculate to a 10.
    '''

    NAME: str = 'work'

    async def git_parse(self, data):
        work = []
        for current in range(0, self.LENGTH * self.FREQUENCY.MONTHS,
                self.FREQUENCY.MONTHS):
            author = ''
            current_work = {}
            proc = await data.git.create('log',
                    '--pretty=format:Author:%aN', '--numstat',
                    '--before', '%d months' % (current),
                    '--after', '%d months' % (current + \
                            self.FREQUENCY.MONTHS))
            while not proc.stdout.at_eof():
                line = await proc.stdout.readline()
                line = line.decode(errors='ignore').rstrip()
                if line.startswith('Author:'):
                    author = line.split(':')[1]
                    if author and author not in current_work:
                        current_work[author] = 0
                elif line and author in current_work and \
                        line.split()[0].isdigit():
                    current_work[author] += int(line.split()[0])
            work.append(current_work)
            await stop(proc)
        data.temp.setdefault(self.NAME, work)

    async def calc(self, data):
        return [simpsons_diversity_index(*authorship.values()) \
                for authorship in data.temp.get(self.NAME)]
