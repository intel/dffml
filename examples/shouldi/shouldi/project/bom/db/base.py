import abc
import dataclasses
import pkg_resources
from typing import Union

from ..base import Dependency, DependencyExtra


class DatabaseError(Exception):
    pass


class DependencyDB(abc.ABC):
    def __init__(self, config: str):
        self.config = config

    @abc.abstractmethod
    def lookup(self, dependency: Dependency) -> Dependency:
        """
        Use any information given in the Dependency to look up a more complete
        version of it. Including information from extra if found. Return the
        same Dependency or the updated version with more information.
        """

    @abc.abstractmethod
    def extra(self, dependency: Dependency) -> Union[None, DependencyExtra]:
        """
        Return the DependencyExtra object associated with the dependency, or
        None if it does not exist in this database.
        """

    @classmethod
    @abc.abstractmethod
    def applicable(cls, config: str) -> bool:
        """
        Return true if the config string given can be used to configure this
        database.
        """

    def save(self, dependency: Dependency):
        """
        Update the dependency in the database
        """
        pass

    def load(config: str):
        try:
            for i in pkg_resources.iter_entry_points(
                __package__.replace(".", "_")
            ):
                loaded = i.load()
                if loaded.applicable(config):
                    return loaded(config)
        except Exception as error:
            raise DatabaseError(config) from error
        raise NotImplementedError(f"No known database connector for {config}")
