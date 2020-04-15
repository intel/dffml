import json
from typing import List,Dict,Any

from dffml.df.base import op
from .definitions import git_payload_string,git_payload

from dffml_feature_git.feature.operations import clone_git_repo


@op(
    inputs = {"payload_str":git_payload_string},
    outputs= {"payload":git_payload}
)
def get_payload(payload_str:str)->Dict[str,Any]:
    payload = json.loads(payload_str)
    return {"payload":payload}

@op(
    inputs={"payload":git_payload},
    outputs={"url":clone_git_repo.op.inputs["URL"]}
)
def get_url_from_payload(payload:Dict[str,Any]):
    return {
        "url": payload["repository"]["clone_url"]
    }


