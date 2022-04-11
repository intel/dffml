"""
Expose Pandas DataFrame as DFFML Source
"""
from typing import AsyncIterator, List


from ..record import Record
from ..base import config, field
from ..util.entrypoint import entrypoint
from ..util.net import DEFAULT_PROTOCOL_ALLOWLIST
from .source import BaseSourceContext, BaseSource


class DataFrameSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        # Shorthand for DataFrame
        df = self.parent.config.dataframe
        # Store feature data
        features = record.features()
        for col in df.columns:
            if col in features:
                df.loc[record.key, col] = features[col]
        # Store prediction
        predictions = record.predictions()
        for col in self.parent.config.predictions:
            if col in predictions:
                df.loc[record.key, col] = predictions[col]["value"]

    async def records(self) -> AsyncIterator[Record]:
        for row in self.parent.config.dataframe.itertuples():
            features = dict(row._asdict())
            predictions = {
                key: {"value": features[key]}
                for key in self.parent.config.predictions
            }
            del features["Index"]
            for key in predictions.keys():
                if key in features:
                    del features[key]
            yield Record(
                str(row.Index),
                data={"features": features, "prediction": predictions},
            )

    async def record(self, key: str) -> Record:
        data = self.parent.config.dataframe.iloc[int(key)]
        predictions = {
            key: data[key] for key in self.parent.config.predictions
        }
        features = {
            key: value for key in data.items() if key not in predictions
        }
        return Record(
            str(key), data={"features": features, "prediction": predictions},
        )


@config
class DataFrameSourceConfig:
    dataframe: "pandas.DataFrame" = field(
        "The pandas DataFrame to proxy", default=None
    )
    predictions: List[str] = field(
        "Prediction columns whose values we have to update",
        default_factory=lambda: [],
    )
    # TODO Get rid of this basic appoach when we implement #1168
    html: str = field(
        "Construct a DataFrame using DataFrame.read_html(). Passing this as URL",
        default=None,
    )
    html_table_index: int = field(
        "If there are multiple html tables on a page, which one? Array indexed"
        ", so first table means 0, if you want the second table on the page"
        ", use 1 here.",
        default=0,
    )
    excel: str = field(
        "Path to excel file to load from", default=None,
    )
    sheet_name: int = field(
        "Name of excel sheet to grab or index", default=0,
    )
    protocol_allowlist: List[str] = field(
        'List of protocols allowed for ``html`` URL. Example ``["http://"]``',
        default_factory=lambda: DEFAULT_PROTOCOL_ALLOWLIST,
    )


@entrypoint("dataframe")
class DataFrameSource(BaseSource):
    r"""
    Proxy for a pandas DataFrame

    Examples
    --------

    You can pass a pandas DataFrame to this class directly via the Python API.
    Or you can create DataFrames from other data sources via the Python API or
    the command line.

    **Example of creating a DataFrame from HTML via command line.**

    Create an HTML table.

    **index.html**

    .. code-block:: html
        :test:
        :filepath: index.html

        <table>
          <tr>
            <th>Years</th>
            <th>Salary</th>
          </tr>
          <tr>
            <td>0</td>
            <td>10</td>
          </tr>
          <tr>
            <td>1</td>
            <td>20</td>
          </tr>
          <tr>
            <td>2</td>
            <td>30</td>
          </tr>
        </table>

    Start the HTTP server to server the HTML page with the table

    .. code-block:: console
        :test:
        :daemon: 8000

        $ python -m http.server 8000

    In another terminal. List all the records in the source.

    .. code-block:: console
        :test:
        :replace: cmds[0][-3] = cmds[0][-3].replace("8000", str(ctx["HTTP_SERVER"]["8000"]))

        $ dffml list records \
            -sources table=dataframe \
            -source-table-html http://127.0.0.1:8000/index.html \
            -source-table-protocol_allowlist http://

        [
            {
                "extra": {},
                "features": {
                    "Salary": 10,
                    "Years": 0
                },
                "key": "0"
            },
            {
                "extra": {},
                "features": {
                    "Salary": 20,
                    "Years": 1
                },
                "key": "1"
            },
            {
                "extra": {},
                "features": {
                    "Salary": 30,
                    "Years": 2
                },
                "key": "2"
            }
        ]

    """

    CONFIG = DataFrameSourceConfig
    CONTEXT = DataFrameSourceContext

    def __init__(self, config):
        super().__init__(config)
        # Create DataFrame if not given
        if self.config.dataframe is None:
            try:
                # Try import
                import pandas
            except (ModuleNotFoundError, ImportError) as error:
                # If it fails say that pandas must be installed to create new
                # DataFrames
                raise PandasNotInstalled(
                    "Pandas is required to create new DataFrames. $ pip install pandas"
                ) from error
            # TODO Modify this in line with changes for #1168
            if self.config.html is not None:
                dataframes = pandas.read_html(self.config.html)
                if self.config.html_table_index >= len(dataframes):
                    raise DataFrameHTMLTableIndexNotFoundError(
                        f"Index {self.config.html_table_index} requested"
                        f" {len(dataframes)} table(s) found."
                    )
                self.config.dataframe = dataframes[
                    self.config.html_table_index
                ]
            elif self.config.excel is not None:
                self.config.dataframe = pandas.read_excel(
                    self.config.excel, self.config.sheet_name,
                )
            else:
                # Create empty DataFrame
                self.config.dataframe = pandas.DataFrame()
