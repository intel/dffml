'''Lang Feature'''
from typing import Dict

from .cloc import GitClocFeature

class GitLangsFeature(GitClocFeature):
    '''
    Language usage by percentage for a git repo
    '''

    NAME: str = 'langs'

    def dtype(self):
        return Dict[str, float]

    def length(self):
        return 1

    def percentage_of(self, numbers):
        for key in ['sum', 'total']:
            if key in numbers:
                del numbers[key]
        whole = sum(numbers.values())
        for key in numbers.keys():
            numbers[key] /= whole
        return numbers

    async def calc(self, data):
        return self.percentage_of({lang: numbers['code'] for lang, numbers in \
                    (data.temp.get('cloc_data'))[0].items()})

class GitLangFeature(GitLangsFeature):
    '''
    Most used language for a git repo
    '''

    NAME: str = 'lang'

    def dtype(self):
        return str

    async def calc(self, data):
        langs_percentages = await super().calc(data)
        return sorted(langs_percentages,
                key=langs_percentages.__getitem__)[::-1][0]
