from dffml.source.source import BaseSource
from dffml.util.entrypoint import entrypoint


@entrypoint("dbsource")
class DbAbstractionSource(BaseSource):
    pass


# TODO: Let abstractdb entrypoint instantiate a subclass of BaseDatabase using the db specified in the config
# TODO: Use the instantiated db to implement required source methods
