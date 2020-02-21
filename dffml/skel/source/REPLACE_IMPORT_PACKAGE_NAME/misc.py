from typing import AsyncIterator, Dict, List

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint
from dffml.base import config


@config
class MiscSourceConfig:
    repos: List[Repo]


class MiscSourceContext(BaseSourceContext):
    async def update(self, repo):
        self.parent.mem[repo.key] = repo

    async def repos(self) -> AsyncIterator[Repo]:
        for repo in self.parent.mem.values():
            yield repo

    async def repo(self, key: str) -> Repo:
        return self.parent.mem.get(key, Repo(key))


@entrypoint("misc")
class MiscSource(BaseSource):
    """
    Stores repos ... somewhere! (skeleton template is in memory)
    """

    CONTEXT = MiscSourceContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.mem: Dict[str, Repo] = {}
        if isinstance(self.config, MiscSourceConfig):
            self.mem = {repo.key: repo for repo in self.config.repos}

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args, above, "keys", Arg(type=str, nargs="+", default=[])
        )
        return args

    @classmethod
    def config(cls, config, *above):
        return MiscSourceConfig(
            repos=list(map(Repo, cls.config_get(config, above, "keys")))
        )
