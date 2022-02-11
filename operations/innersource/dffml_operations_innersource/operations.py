from typing import List

import yaml

from dffml.df.base import op


@op
async def parse_github_workflow(contents: str) -> dict:
    return yaml.safe_load(contents)
