'''Release Feature'''
from datetime import datetime
from dateutil.relativedelta import relativedelta

from dffml_feature_git.util.proc import create, stop, check_output

from .log import LOGGER
from .git import GitFeature

class GitReleaseFeature(GitFeature):
    '''
    Was there a release within the last 6 months
    '''

    NAME = 'release'
    # Number of months since last release
    LAST: int = 18

    def valid_version(self, tag):
        # Remove v from v1 to make isnumeric return True
        tag = tag.replace('v', '')
        # Make the only seperator . instead of - or _
        for replace in ['-', '_']:
            tag = tag.replace(replace, '.')
        # Make sure there is at least one number in the tag when split by .
        return bool(sum([1 for num in tag.split('.') if num.isnumeric()]))

    async def git_parse(self, data):
        release = [0] * self.LENGTH
        releases = []
        # Parse log
        proc = await data.git.create('log', '--tags',
                '--simplify-by-decoration', '--pretty=format:%at %D')
        while not proc.stdout.at_eof():
            line = await proc.stdout.readline()
            line = line.decode(errors='ignore').strip().split()
            LOGGER.debug('%r %s: %r', self, data.src_url, line)
            # Ensure there is at'v'
            # or it starts with v and then a number
            if not line or not self.valid_version(line[-1]):
                continue
            releases.append(datetime.fromtimestamp(int(line[0])))
        await stop(proc)
        # Check if there was a release within LAST months of each quarter
        current = datetime.now()
        for i in range(0, self.LENGTH):
            six_months_from_current = current - relativedelta(months=self.LAST)
            for date in releases:
                if date < current and date > six_months_from_current:
                    release[i] = 1
            current -= relativedelta(months=self.FREQUENCY.MONTHS)
        data.temp.setdefault(self.NAME, release)
        await data.data.set(self.NAME, await self.calc(data))

    async def calc(self, data):
        return data.temp.get(self.NAME)
