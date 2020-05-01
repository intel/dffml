import abc
import inspect
import functools
import collections
from typing import Any, List, Optional, Dict, Tuple, Union, AsyncIterator

from ..df.base import BaseDataFlowObject, BaseDataFlowObjectContext
from ..util.entrypoint import base_entry_point


Condition = collections.namedtuple(
    "Condition", ["column", "operation", "value"]
)
Conditions = Union[List[List[Condition]], List[List[Tuple[str]]]]


class DatabaseContextConstraint(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in vars(cls).keys():
            func = getattr(cls, attr)
            if (
                (not attr.startswith("__"))
                and inspect.isfunction(func)
                and not (
                    inspect.ismethod(func) and func.__self__ is cls
                )  # checks if `@classmethod`
            ):
                setattr(cls, attr, cls.sanitize(func))


class BaseDatabaseContext(
    BaseDataFlowObjectContext, DatabaseContextConstraint
):
    """
    Base context class for database interaction
    """

    def __init__(self, parent: "BaseDatabase"):
        self.parent = parent

    @classmethod
    def sanitize_non_bindable(self, val):
        if val.replace("_", "").isalnum():
            return val
        raise ValueError(
            f"`{val}` : Only alphanumeric [a-zA-Z0-9] characters are allowed as table,column names"
        )

    @classmethod
    def sanitize(self, func):
        sig = inspect.signature(func)

        def scrub(obj):
            if isinstance(obj, str):
                return self.sanitize_non_bindable(obj)
            if isinstance(obj, Dict):
                nobj = {
                    self.sanitize_non_bindable(k): v for k, v in obj.items()
                }
                return nobj
            if isinstance(obj, List):
                nobj = list(map(scrub, obj))
                return nobj
            if isinstance(obj, Condition):
                column, *others = obj
                nobj = Condition._make([scrub(column), *others])
                return nobj
            else:
                return obj

        @functools.wraps(func)
        def wrappper(*args, **kwargs):
            bounded = sig.bind(*args, **kwargs)
            for arg in bounded.arguments:
                if arg == "self" or arg == "cls":
                    continue
                if arg == "conditions":
                    bounded.arguments[arg] = self.make_conditions(
                        bounded.arguments[arg]
                    )
                bounded.arguments[arg] = scrub(bounded.arguments[arg])
            return func(*bounded.args, **bounded.kwargs)

        return wrappper

    @classmethod
    def make_conditions(self, lst):
        if (not lst) or isinstance(lst[0][0], Condition):
            return lst
        res = [list(map(Condition._make, cnd)) for cnd in lst]
        return res

    @abc.abstractmethod
    async def create_table(
        self, table_name: str, cols: Dict[str, str]
    ) -> None:
        """
        Creates a table with name `table_name` if it doesn't exist
        """

    @abc.abstractmethod
    async def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Inserts values to corresponding cols (according to position) to the
        table `table_name`
        """

    @abc.abstractmethod
    async def update(
        self,
        table_name: str,
        data: Dict[str, Any],
        conditions: Optional[Conditions] = None,
    ) -> None:
        """
        Updates values of rows (satisfying `conditions` if provided) with `data`
        in `table_name`
        """

    @abc.abstractmethod
    async def lookup(
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Returns list of rows (satisfying `conditions` if provided) from
        `table_name`
        """

    @abc.abstractmethod
    async def remove(
        self, table_name: str, conditions: Optional[Conditions] = None
    ):
        """
        Removes rows (satisfying `conditions`) from `table_name`
        """

    @abc.abstractmethod
    async def insert_or_update(
        self, table_name: str, data: Dict[str, Any]
    ) -> None:
        try:
            await self.insert(table_name, data)
        except:
            await self.update(table_name, data, conditions=[])


@base_entry_point("dffml.db", "db")
class BaseDatabase(BaseDataFlowObject):
    """
    Base class for database interaction
    """

    def __call__(self) -> BaseDatabaseContext:
        return self.CONTEXT(self)
