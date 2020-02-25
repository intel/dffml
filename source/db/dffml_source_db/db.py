from dffml.base import config
from dffml.db.base import BaseDatabase
from dffml.util.entrypoint import entrypoint


@config
class AbstractDatabaseConfig:
    dbImplementation: str


@entrypoint("abstractdb")
class AbstractDatabase(BaseDatabase):
    pass
    # TODO: Instantiate the subclass of BaseDatabase as specified by the config
