from configparser import ConfigParser

from ..base import config
from ..record import Record
from .file import FileSource
from .memory import MemorySource
from ..util.data import parser_helper
from ..util.entrypoint import entrypoint


@config
class INISourceConfig:
    filename: str
    readwrite: bool = False
    allowempty: bool = False


@entrypoint("ini")
class INISource(FileSource, MemorySource):
    """
    Source to read files in .ini format.
    """

    CONFIG = INISourceConfig

    async def load_fd(self, fileobj):
        # Creating an instance of configparser
        parser = ConfigParser()
        # Read from a file object
        parser.read_file(fileobj)
        # Get all the sections present in the file
        sections = parser.sections()

        self.mem = {}

        # Go over each section
        for section in sections:
            # Get data under each section as a dict
            temp_dict = {}
            for k, v in parser.items(section):
                temp_dict[k] = parser_helper(v)
            # Each section used as a record
            self.mem[str(section)] = Record(
                str(section), data={"features": temp_dict}
            )

        self.logger.debug("%r loaded %d sections", self, len(self.mem))

    async def dump_fd(self, fileobj):
        # Create an instance of configparser
        parser = ConfigParser()

        # Go over each section and record in mem
        for section, record in self.mem.items():
            # Get each section data as a dict
            section_data = record.features()
            if section not in parser.keys():
                # If section does not exist add new section
                parser.add_section(section)
            # Set section data
            parser[section] = section_data

        # Write to the fileobject
        parser.write(fileobj)

        self.logger.debug("%r saved %d sections", self, len(self.mem))
