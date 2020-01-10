# General
from .high_level import train, accuracy, predict
from .feature import Features, Feature, DefFeature

# Sources
from .source.source import Sources, BaseSource, BaseSourceContext
from .source.csv import CSVSource
from .source.json import JSONSource

# Models
from .model import Model, ModelContext

# Used to declare our namespace for resource discovery
__import__("pkg_resources").declare_namespace(__name__)
