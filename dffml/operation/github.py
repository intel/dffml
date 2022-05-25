import sys
import importlib
import dataclasses
import importlib.util

from ..util.asynctestcase import AsyncTestCase
from ..util.config.inspect import make_config_inspect


@op(
    imp_enter={
        "bs4": lambda: importlib.import_module("bs4"),
    },
)
def bs4_parse_html():
    soup = self.parent.bs4.BeautifulSoup(html_doc, 'html.parser')
    return soup.pretitify()


def operation_for_sync_urlopen(
    url: Union[str, urllib.request.Request],
    protocol_allowlist: List[str] = DEFAULT_PROTOCOL_ALLOWLIST,
    **kwargs,
):
    """
    Check that ``url`` has a protocol defined in ``protocol_allowlist``, then
    return the result of calling :py:func:`urllib.request.urlopen` passing it
    ``url`` and any keyword arguments.
    """
    validate_protocol(url, protocol_allowlist=protocol_allowlist)
    return urllib.request.urlopen(url, **kwargs)

GITHUB_DISCUSSION_DEFAULT_DATAFLOW = DataFlow(
    # Copy from our remap flow
)

@config
class GitHubDiscussionConfig:
    dataflow: DataFlow = field("Default flow", default_factory=lambda: GITHUB_DISCUSSION_DEFAULT_DATAFLOW)

GitHubDiscussion = NewType("GitHubDiscussion", dict)

async def github_discussion(self, ) -> GitHubDiscussion:



class TestGitHubOperations(AsyncTestCase):
    async def test_create_status(self):
        file_path = "~/Documents/python/dffml/.venv/lib/python3.7/site-packages/github/Commit.py"
        module_name = "github.commit"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        print(module.Commit.create_status)

        config = make_config_inspect(
            "GitHubCommitCreateStatusConfig", module.Commit.create_status
        )

        import pprint

        pprint.pprint(list(dataclasses.fields(config)))

        print(config())
