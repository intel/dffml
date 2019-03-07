'''Cloc Feature'''
from dffml_feature_git.util.proc import inpath, create, stop

from .log import LOGGER

from .monthly import GitMonthlyFeature

class GitClocFeature(GitMonthlyFeature):
    '''
    Count Lines Of Code
    '''

    NAME: str = 'cloc'
    BINARY: str = 'cloc'
    FASTER_THAN_CLOC = ['tokei']

    def __init__(self):
        super().__init__()
        self.binary = self.BINARY
        for binary in self.FASTER_THAN_CLOC:
            if inpath(binary):
                self.binary = binary

    async def applicable(self, data):
        return inpath(self.binary) \
                and await GitMonthlyFeature.applicable(self, data)

    async def git_parse(self, data):
        if not data.temp.get('cloc_data', False):
            data.temp.setdefault('cloc_data', [{'sum': 0}] * self.LENGTH)
            await super().git_parse(data)

    async def month_parse(self, data, i):
        parsed = data.temp.get('cloc_data')
        proc = await create(self.binary, data.git.cwd)
        cols  = []
        while not proc.stdout.at_eof():
            line = (await proc.stdout.readline()).decode().split()
            if not line or line[0].startswith('-'):
                continue
            LOGGER.debug('%s line: %r', self.binary, line)
            if line[0].lower().startswith('lang'):
                cols = [cat.lower() for cat in line[1:]]
                # Tokei -> cloc compatibility
                if 'comments' in cols:
                    cols[cols.index('comments')] = 'comment'
                continue
            if cols:
                header_cols = [word for word in line if not word.isdigit()]
                header = ''.join([c for c in '_'.join(header_cols).lower() \
                        if c.isalpha() or c == '_'])
                # Tokei -> cloc compatibility
                if header == 'total':
                    header = 'sum'
                parsed[i][header] = dict(zip(cols,
                    map(int, line[len(header_cols):])))
        LOGGER.debug('parsed[%d]: %r', i, parsed[i])
        await stop(proc)

    async def calc(self, data):
        try:
            return [int(100 * month['sum']['comment'] / \
                    (month['sum']['comment'] + month['sum']['code']))
                    for month in (data.temp.get('cloc_data'))]
        except ZeroDivisionError:
            return [0 for month in (data.temp.get('cloc_data'))]
