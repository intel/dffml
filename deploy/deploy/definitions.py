import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="git_payload_string", primitive="str"),
    Definition(name="git_payload", primitive="Dict[Any]"),
    Definition(name="docker_image_id",primitive="str"),
    Definition(name="is_default_branch",primitive="bool"),
    Definition(name="docker_image_tag",primitive="str")
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
