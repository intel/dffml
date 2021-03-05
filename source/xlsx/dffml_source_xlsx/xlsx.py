from openpyxl import Workbook, load_workbook

from dffml import config
from dffml.util.entrypoint import entrypoint
from dffml.source.file import FileSource
from dffml.source.memory import MemorySource
from dffml.record import Record


@config
class XLSXSourceConfig:
    filename: str
    readwrite: bool = False
    allowempty: bool = False


@entrypoint("xlsx")
class XLSXSource(FileSource, MemorySource):
    """
    Source to read files in .xlsx format.
    """

    CONFIG = XLSXSourceConfig

    async def load_fd(self, fd):
        excel_file = load_workbook(fd.name)  # Loading the Workbook
        excel_sheet = excel_file.active  # Current Working Sheet

        self.mem = {}
        max_rows = excel_sheet.max_row  # Total Rows in the excel sheet
        max_columns = (
            excel_sheet.max_column
        )  # Total Columns in the excel sheet
        for row in range(
            2, max_rows + 1
        ):  # Iterate over each record rows excluding the features
            temp_dict = {}
            for col in range(1, max_columns + 1):
                feature = excel_sheet.cell(row=1, column=col)  # Features data
                cell_element = excel_sheet.cell(
                    row=row, column=col
                )  # Cell content corresponding to the feature data
                temp_dict[str(feature.value)] = cell_element.value
            self.mem[str(row - 1)] = Record(
                str(row - 1), data={"features": temp_dict}
            )
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        excel_file = Workbook()
        excel_sheet = excel_file.active  # Current Working Sheet
        features = []  # Record what features are present in the XLSX files
        for section, records in self.mem.items():  # Iterating over each row
            section_data = records.features()
            if (
                not features
            ):  # If the fetures list is empty add the features, and then append it to the excel_sheet
                for key, value in section_data.items():
                    features.append(key)
                excel_sheet.append(features)
            row = []
            for key, value in section_data.items():
                row.append(value)
            excel_sheet.append(row)  # append the rows in the excel_file
        excel_file.save(filename=fd.name)  # save the excel file
        self.logger.debug("%r saved %d records", self, len(self.mem))
