import sys
import textwrap
import unittest
import importlib
import contextlib

from dffml import *


def requires_module(module_name):
    with contextlib.suppress((ImportError, ModuleNotFoundError)):
        setattr(
            sys.modules[__name__],
            module_name,
            importlib.import_module(module_name),
        )

    return unittest.skipIf(
        module_name not in sys.modules[__name__].__dict__,
        f"Requires {module_name} module",
    )


async def convert(document):
    """
    Convert is very similar to any other dataflow. With one major difference.
    The output is explicitly a :py:class:`DataFlow <dffml.df.types.DataFlow>`.

    The input is the output of some dataflow. That dataflow might load a file,
    parse a directory, look at a database for what to do. The output of the
    conversion is a dataflow.

    For convenience we provide helper functions, or wrappers, similar to how we
    did with
    :py:func:`dataset_source <dffml.source.dataset.base.dataset_source>`

    We'll register conversions as plugins.

    We may also register input sources as plugins, that could be interesting, it
    might also be the same as a configloader, we'll have to see how it goes for
    multiple input types / situations.
    """


class TestCLIDataFlowConvert(AsyncTestCase):
    @requires_module("yaml")
    async def test_convert_yaml_server_platform_validation(self):
        """
        Background
        ----------

        Let's come up with a format that allows us to evolve it as we move
        forward (we should go apply these principles to our own dataflow format
        at some point).

        To make sure we have forwards / backwards compatibility we should
        include information which allows us to identify what format the document
        is in, and what version of that format it is. This will likely also feed
        into our input dataflow requirements as we'll need to have the ability
        to check an arbitrary input to see if we might have an applicable
        converter.

        Let's learn from JSON Schema and include a URL where we might be able
        to find the schema for the document. We can double up on our previous
        needs by asking that the filename of the URL can help us identify our
        document format (we'll provide fallback for if we don't have control
        over the filename via the ``document_format`` and ``$document_version``
        keys). We'll parse the URL for the filename component. When we parse it
        we'll split on ``.``. If the first part is eff (Extensible Format
        Format) we'll treat the rest up until the semantic version as the format
        name. Then the semantic version is the version of the format. Then the
        rest should be the extension which is associated with the format which
        we can use to validate the contents of the document, such as JSON
        schema.

        ``$schema: "https://example.com/eff.my.document.format.0.0.0.schema.json"``

        Immediate TODO
        --------------

        - If they proivde a docker image use the image similar to existing
          cluster. Otherwise use existing image plus given information as
          runtime context.

        - Make sure that it's easy for people to change this code. Submit PR to
          manifest parsing repo. Make sure others have maintainer access to the
          branch that this is on.

        TODO
        ----

        - Verification of the manifest. Idea: Developer generates manifest.
          Signs manifest with public asymmetric key. Prepends base64 encoded
          signature as a valid key, ``$signature``. This means you have to
          parse the YAML before you have verified the signature, which is not
          ideal. However, it's one method available to us and a simple parse
          without the use of a full YAML parser could be done. Or we could
          distribute out of band and verify the document before the conversion
          stage, in the loading stage.

        - Verification of references within manifest. Do we support public
          portion of CA key embedded in the document various places? We
          could then use it for things like verification of git repos where
          the CA must sign all developer keys which are in the repo history.
          This will apply to anything that is an external reference in the
          document. There should be a way for the document to include an HMAC or
          something like that or something more dynamic like a CA.
        """
        print(
            yaml.safe_load(
                textwrap.dedent(
                    """\
                    $document_format: my.document.format
                    $document_version: 0.0.0
                    bkc: bkcX
                    platform: platformX
                    testplan:
                    - git:
                        repo: https://example.com/my-repo.git
                        branch: main
                        file: my_test.py
                    """
                )
            )
        )
