import sys

from dffml.df import Definition

definitions = [
    Definition(
        name="URL",
        primitive="string",
    ),
    Definition(
        name="URLBytes",
        primitive="python_obj"
    ),
    Definition(
        name="RPMObject",
        primitive="python_obj"
    ),
    Definition(
        name="rpm_filename",
        primitive="str"
    ),
    Definition(
        name="binary",
        primitive="str"
    ),
    Definition(
        name="binary_is_PIE",
        primitive="bool"
    )
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
