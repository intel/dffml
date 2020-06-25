import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="webhook_headers", primitive="Dict[str,Any]"),
    Definition(name="payload", primitive="bytes"),
    Definition(name="git_payload", primitive="Dict[str,Any]"),
    Definition(name="docker_image_id", primitive="str"),
    Definition(name="is_default_branch", primitive="bool"),
    Definition(name="docker_image_tag", primitive="str"),
    Definition(name="docker_running_containers", primitive="List[str]"),
    Definition(name="got_running_containers", primitive="bool"),
    Definition(name="is_image_built", primitive="bool"),
    Definition(name="docker_commands", primitive="Dict[str,Any]"),
    Definition(name="docker_restarted_containers", primitive="str"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
