from ...source.source import Sources
from ...base import field


FIELD_SOURCES = field(
    "Sources for loading and saving",
    default_factory=lambda: Sources(),
    labeled=True,
)
