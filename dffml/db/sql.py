"""
Base classes to wrap various SQL based databases in dffml.db abstraction.
"""
from typing import Dict, Any, List, Tuple, Optional

from .base import BaseDatabaseContext, Conditions


class SQLDatabaseContext(BaseDatabaseContext):
    # BIND_DECLARATION is the string used to bind a param
    BIND_DECLARATION: str = "?"

    @classmethod
    def make_condition_expression(cls, conditions):
        """
        Returns a dict with keys 'expression','values' if conditions is not empty
        else returns `None`

        example::

            Input : conditions = [
                [["firstName", "=", "John"], ["lastName", "=", "Miles"]],
                [["age", "<", "38"]],
            ]

            Output : {
                'expression':
                    '((firstName = ? ) OR (lastName = ? )) AND ((age < ? ))',
                'values':
                     ['John', 'Miles', '38']
                }
        """

        def _make_condition_expression(conditions):
            def make_or(lst):
                val_list = []
                exp = []

                for cnd in lst:
                    exp.append(
                        f"(`{cnd.column}` {cnd.operation} {cls.BIND_DECLARATION} )"
                    )
                    val_list.append(cnd.value)

                result = {"expression": " OR ".join(exp), "values": val_list}

                return result

            lst = map(make_or, conditions)

            result_exps = []
            result_vals = []
            for result in lst:
                temp_exp = result["expression"]
                temp_exp = f"({temp_exp})"
                result_exps.append(temp_exp)
                result_vals.extend(result["values"])

            result_exps = " AND ".join(result_exps)
            result = {"expression": result_exps, "values": result_vals}

            return result

        condition_dict = None
        if (not conditions == None) and (len(conditions) != 0):
            condition_dict = _make_condition_expression(conditions)
        return condition_dict

    def create_table_query(
        self, table_name: str, cols: Dict[str, str], *args, **kwargs
    ) -> None:
        """
        Creates a create query. Table with name ``table_name`` will be created
        if it doesn't exist.

        Parameters
        ----------
        table_name : str
            Name of the table.
        `cols` : dict
            Mapping of column names to type of columns.

        Returns
        -------
        query : str
            ``CREATE`` query
        """

        query = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ("
            + ", ".join([f"`{k}` {v}" for k, v in cols.items()])
            + ")"
        )

        return query

    def insert_query(
        self, table_name: str, data: Dict[str, Any], *args, **kwargs
    ) -> None:
        """
        Creates insert query. Keys in ``data`` dict correspond to the columns in
        ``table_name``.

        Parameters
        ----------
        table_name : str
            Name of the table.
        data : dict, optional
            Columns names are keys, values are data to insert.

        Returns
        -------
        query : str
            ``INSERT`` query
        parameters : tuple
            Variables to bind
        """
        col_exp = ", ".join([f"`{col}`" for col in data])
        query = (
            f"INSERT INTO {table_name} "
            + f"( {col_exp} )"
            + f" VALUES( {', '.join([self.BIND_DECLARATION] * len(data))} ) "
        )
        return query, list(data.values())

    def update_query(
        self,
        table_name: str,
        data: Dict[str, Any],
        conditions: Optional[Conditions] = None,
    ) -> None:
        """
        Creates update query setting values of rows (satisfying ``conditions``
        if provided) with ``data`` in ``table_name``.

        Parameters
        ----------
        table_name : str
            Name of the table.
        data : dict, optional
            Columns names to update mapped to value to set to.
        conditions: Conditions, optional
            Nested array of conditions to satisfy, becomes ``WHERE``.

        Returns
        -------
        query : str
            ``UPDATE`` query
        parameters : tuple
            Variables to bind
        """
        query_values = list(data.values())
        condition_dict = self.make_condition_expression(conditions)

        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values.extend(condition_dict["values"])
        else:
            condition_exp = None

        query = (
            f"UPDATE {table_name} SET "
            + " ,".join([f"`{col}` = {self.BIND_DECLARATION}" for col in data])
            + (f" WHERE {condition_exp}" if condition_exp is not None else "")
        )

        return query, query_values

    def lookup_query(
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
    ) -> Tuple[str, Tuple[Any]]:
        """
        Creates a query string and tuple of parameters used as bindings.

        Parameters
        ----------
        table_name : str
            Name of the table.
        cols : list, optional
            Columns names to return
        conditions: Conditions, optional
            Nested array of conditions to satisfy, becomes ``WHERE``.

        Returns
        -------
        query : str
            ``SELECT`` query
        parameters : tuple
            Variables to bind
        """

        condition_dict = self.make_condition_expression(conditions)
        query_values = []
        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values.extend(condition_dict["values"])
        else:
            condition_exp = None

        if not cols:
            col_exp = "*"
        else:
            col_exp = ", ".join([f"`{col}`" for col in cols])

        query = f"SELECT {col_exp} FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )

        return query, query_values

    def remove_query(
        self, table_name: str, conditions: Optional[Conditions] = None
    ):
        """
        Creates a delete query to remove rows from ``table_name`` (satisfying
        ``conditions`` if provided).

        Parameters
        ----------
        table_name : str
            Name of the table.
        conditions: Conditions, optional
            Nested array of conditions to satisfy, becomes ``WHERE``.

        Returns
        -------
        query : str
            ``DELETE`` query
        parameters : tuple
            Variables to bind
        """
        condition_dict = self.make_condition_expression(conditions)
        query_values = []
        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values = condition_dict["values"]
        else:
            condition_exp = None

        query = f"DELETE FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )

        return query, query_values
