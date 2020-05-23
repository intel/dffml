import os

from ...source.file import FileSourceConfig
from ...source.json import JSONSource
from ...source.source import Sources
from ...base import field


FIELD_SOURCES = field(
    "Sources for loading and saving",
    default_factory=lambda: Sources(
        JSONSource(
            FileSourceConfig(
                filename=os.path.join(
                    os.path.expanduser("~"), ".cache", "dffml.json"
                )
            )
        )
    ),
    labeled=True,
    required=True,
)
