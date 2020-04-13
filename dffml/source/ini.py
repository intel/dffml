from configparser import ConfigParser

from ..record import Record
from .file import FileSource
from ..base import config, field
from .memory import MemorySource
from ..util.entrypoint import entrypoint


@config
class INISourceConfig:
    filename: str
    feature: str = field("Name of the feature the data will be referenced as")
    readwrite: bool = False
    allowempty: bool = False


@entrypoint("ini")
class INISource(FileSource, MemorySource):
    """
    Source to read files in .ini format.
    """

    CONFIG = INISourceConfig

    async def load_fd(self, ifile):
        # creating an instance of configparser
        parser = ConfigParser()
        # read from a file object
        parser.read_file(ifile)
        # get all the sections present in the file
        sections = parser.sections()

        self.mem = {}

        # go over each section
        for section in sections:
            # get the name and value pair under each section
            for name, value in parser.items(section):
                self.mem[str(section)] = Record(
                    str(section),  # each section used as a record
                    data={"features": {str(name): str(value)}},
                )

        self.logger.debug("%r loaded %d sections", self, len(self.mem))

    async def dump_fd(self, fd):
        # create an instance of configparser
        parser = ConfigParser()
        # read the fileobj(fd) as dict where key is section name and values are dict of option and value pair
        parser.read_dict(fd)

        # go over each section in mem
        for section in self.mem.keys():
            # get each section data as a dict
            section_data = section.features()
            if section not in parser.keys():
                # if section does not exist add new section
                parser.add_section(section)
            parser[section] = section_data  # set section data

        # write to the fileobject
        parser.write(fd)

        self.logger.debug("%r saved %d sections", self, len(self.mem))
