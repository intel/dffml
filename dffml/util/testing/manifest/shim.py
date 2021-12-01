#!/usr/bin/env python
r"""
Manifest Shim
=============

Validate and parse a manifest. Execute something for the next stage of parsing.

This script is a shim layer to call the appropriate parser for a given
manifest format and version. This shim abstracts the complexities of manifest
versioning and if desired validation. This phased approach to parsing
simplifies the maintenance of manifest formats and parsers. It also makes
it easier for the CI/CD community to work towards manifest schema alignment,
as the shared shim layer facilities sharing of validation mechanisms and next
phase parsing where appropriate.

Updates
-------

This file has been vendored into multiple locations. Please be sure to track
progress as the format evolves upstream. Upstream URL:
https://github.com/intel/dffml/blob/manifest/dffml/util/testing/manifest/shim.py

Pull Request for discussion, questions, comments, concerns, review:
https://github.com/intel/dffml/pull/1273/files

Usage
-----

This file allows for registration of next phase parsers via environment
variables.

The purpose of this script is to preform the initial validation and parsing of
the manifest. It's responsibility is to then call the appropriate next phase
manifest parser. It will pass the manifest's data in a format the next phase
requests, and execute the next phase using capabilities implemented within this
file.

Download the shim

.. code-block:: console
    :test:
    :replace: import os; cmds[0] = ["cp", os.path.join(ctx["root"], "dffml", "util", "testing", "manifest", "shim.py"), "shim.py"]

    $ curl -sfLO https://github.com/intel/dffml/raw/manifest/dffml/util/testing/manifest/shim.py

Create the following files. The first is a manifest with a ``$schema`` which
will give the shim the format name and version based on the filename.

**manifest-sample.yaml**

.. code-block:: yaml
    :test:
    :filepath: manifest-sample.yaml

    ---
    $schema: https://example.com/my.manifest.format.0.0.1.json.schema
    testplan:
    - git:
        repo: https://example.com/my-repo.git
        branch: main
        file: my_test.py
    - git:
        repo: https://example.com/their-repo.git
        branch: main
        file: beef.py
    - git:
        repo: https://example.com/their-repo.git
        branch: main
        file: other.py
    - git:
        repo: https://example.com/my-repo.git
        branch: main
        file: face.py

The second is a manifest in another format entirely. You can also use the shim
to parse it, but you must provide a way to get that manifests format name and
version.

**manifest-sample.txt**

.. code-block:: yaml
    :test:
    :filepath: manifest-sample.txt

    https://example.com/alt.git#dev yo.py
    https://example.com/aux.git#main yoma.py

We need to write a custom parser for the non-JSON/YAML input format. We can do
this via a supplemental setup file used to initialized the shim's environment.

.. note::

    When debugging writing a custom parser. It can be good to add the
    ``--log debug`` flag to the invocation of the shim.

**setup_shim.py**

.. code-block:: python
    :test:
    :filepath: setup_shim.py

    from typing import Dict, Any


    def parse_my_manifest_format_0_0_0(contents: bytes) -> Dict[str, Any]:
        return {
            "$schema": "https://example.com/my.manifest.format.0.0.0.json.schema",
            "testplan": [
                dict(
                    zip(
                        ["repo", "branch", "file"],
                        [*line.split()[0].split("#"), line.split()[1]],
                    )
                )
                for line in contents.decode().strip().split("\n")
            ]
        }


    def next_phase_print_repos_with_branches_0_0_0(manifest: Dict[str, Any]) -> None:
        for testcase in manifest["testplan"]:
            print(testcase["repo"] + "#" + testcase["branch"])


    def next_phase_print_repos_with_branches_0_0_1(manifest: Dict[str, Any]) -> None:
        for testcase in manifest["testplan"]:
            print(testcase["git"]["repo"] + "#" + testcase["git"]["branch"])


    def setup_shim(parsers, next_phase_parser_class, next_phase_parsers, **kwargs):
        # Put the parser at the front of the list to try since YAML will also
        # successfully parse the format
        parsers.insert(0, ("my.manifest.format.0.0.0", parse_my_manifest_format_0_0_0))

        # Declare another next phase parser (rather than registering via
        # environment variables, this enables use of Python).
        parser = next_phase_parser_class(
            name="repos-with-branch",
            format="my.manifest.format",
            version="0.0.0",
            action="call_function",
            target=next_phase_print_repos_with_branches_0_0_0,
        )
        # Add the next phase parser
        next_phase_parsers[(parser.format, parser.version, parser.name)] = parser

        # Again for the other format version
        parser = next_phase_parser_class(
            name="repos-with-branch",
            format="my.manifest.format",
            version="0.0.1",
            action="call_function",
            target=next_phase_print_repos_with_branches_0_0_1,
        )
        # Add the next phase parser
        next_phase_parsers[(parser.format, parser.version, parser.name)] = parser

A script to list the git repos given manifests

**ls-manifest-testplan-git-repo.sh**

.. code-block:: bash
    :test:
    :overwrite:
    :filepath: ls-manifest-testplan-git-repo.sh

    #!/usr/bin/env sh
    set -euo pipefail

    # Python to use
    PYTHON=${PYTHON:-"python3"}
    # Absolute path to the directory this file is in
    SELF_DIR="$(realpath $(dirname $0))"
    # Path to manifest shim
    SHIM="${PYTHON} ${SELF_DIR}/shim.py"
    # Selector for next phase to preform
    NEXT_PHASE=${NEXT_PHASE:-"repos"}

    # The 0.0.0 manifest format, the non-YAML based one
    export MANIFEST_PARSER_NAME_GIT_REPOS_0_0_0="repos"
    export MANIFEST_PARSER_FORMAT_GIT_REPOS_0_0_0="my.manifest.format"
    export MANIFEST_PARSER_VERSION_GIT_REPOS_0_0_0="0.0.0"
    export MANIFEST_PARSER_SERIALIZE_GIT_REPOS_0_0_0="env"
    export MANIFEST_PARSER_ACTION_GIT_REPOS_0_0_0="exec_stdin"
    export MANIFEST_PARSER_TARGET_GIT_REPOS_0_0_0="${SHELL}"
    export MANIFEST_PARSER_ARGS_GIT_REPOS_0_0_0="-c \"grep '_REPO=' | sed -e 's/.*_REPO=//g'\""

    # The 0.0.1 manifest format, the YAML based one
    export MANIFEST_PARSER_NAME_GIT_REPOS_0_0_1="repos"
    export MANIFEST_PARSER_FORMAT_GIT_REPOS_0_0_1="my.manifest.format"
    export MANIFEST_PARSER_VERSION_GIT_REPOS_0_0_1="0.0.1"
    export MANIFEST_PARSER_SERIALIZE_GIT_REPOS_0_0_1="env"
    export MANIFEST_PARSER_ACTION_GIT_REPOS_0_0_1="exec_stdin"
    export MANIFEST_PARSER_TARGET_GIT_REPOS_0_0_1="${SHELL}"
    export MANIFEST_PARSER_ARGS_GIT_REPOS_0_0_1="-c \"grep '_GIT_REPO=' | sed -e 's/.*_GIT_REPO=//g'\""

    while test $# -gt 0
    do
      $SHIM --insecure --no-schema-check --input-target "${1}" \
        --setup setup_shim.py --parser "${NEXT_PHASE}"
      shift
    done

.. code-block:: console
    :test:

    $ bash ls-manifest-testplan-git-repo.sh ./manifest-sample.txt ./manifest-sample.yaml
    https://example.com/alt.git
    https://example.com/aux.git
    https://example.com/my-repo.git
    https://example.com/their-repo.git
    https://example.com/their-repo.git
    https://example.com/my-repo.git

We can now easily select whcih next phase parser to use since the shim layer has
them all registered.

.. code-block:: console
    :test:

    $ NEXT_PHASE=repos-with-branch bash ls-manifest-testplan-git-repo.sh ./manifest-sample.txt ./manifest-sample.yaml
    https://example.com/alt.git#dev
    https://example.com/aux.git#main
    https://example.com/my-repo.git#main
    https://example.com/their-repo.git#main
    https://example.com/their-repo.git#main
    https://example.com/my-repo.git#main

A script to list the test property of the given git repo for the given manifests

**ls-manifest-testplan-git-test.sh**

.. code-block:: bash
    :test:
    :filepath: ls-manifest-testplan-git-test.sh

    #!/usr/bin/env sh
    set -euo pipefail

    GIT_REPO="${1}"
    shift

    # Python to use
    PYTHON=${PYTHON:-"python3"}
    # Absolute path to the directory this file is in
    SELF_DIR="$(realpath $(dirname $0))"
    # Path to manifest shim
    SHIM="${PYTHON} ${SELF_DIR}/shim.py"

    # This script uses the shim layer to call the appropriate parser for the
    # manifest version. Currently there is only one version of the format. If we
    # move the to the next version we might want to parse it differently.

    # The 0.0.0 manifest format, the non-YAML based one
    export MANIFEST_PARSER_NAME_GIT_REPOS_0_0_0="env-style"
    export MANIFEST_PARSER_FORMAT_GIT_REPOS_0_0_0="my.manifest.format"
    export MANIFEST_PARSER_VERSION_GIT_REPOS_0_0_0="0.0.0"
    export MANIFEST_PARSER_SERIALIZE_GIT_REPOS_0_0_0="env"
    export MANIFEST_PARSER_ACTION_GIT_REPOS_0_0_0="stdout"

    # The 0.0.1 manifest format, the YAML based one
    export MANIFEST_PARSER_NAME_GIT_REPOS_0_0_1="env-style"
    export MANIFEST_PARSER_FORMAT_GIT_REPOS_0_0_1="my.manifest.format"
    export MANIFEST_PARSER_VERSION_GIT_REPOS_0_0_1="0.0.1"
    export MANIFEST_PARSER_SERIALIZE_GIT_REPOS_0_0_1="env"
    export MANIFEST_PARSER_ACTION_GIT_REPOS_0_0_1="stdout"

    while test $# -gt 0
    do
      # Parse the manifest from YAML into essentially a bash environment
      # KEY=value. It will now be in the following form:
      #
      #   $SCHEMA=https://example.com/my.manifest.format.0.0.0.json.schema
      #   TESTPLAN_0_GIT_REPO=https://example.com/my-repo.git
      #   TESTPLAN_0_GIT_BRANCH=main
      #   TESTPLAN_0_GIT_FILE=my_test.py
      #   TESTPLAN_1_GIT_REPO=https://example.com/their-repo.git
      #   TESTPLAN_1_GIT_BRANCH=main
      #   TESTPLAN_1_GIT_FILE=beef.py
      #   TESTPLAN_2_GIT_REPO=https://example.com/their-repo.git
      #   TESTPLAN_2_GIT_BRANCH=main
      #   TESTPLAN_2_GIT_FILE=other.py
      #   TESTPLAN_3_GIT_REPO=https://example.com/my-repo.git
      #   TESTPLAN_3_GIT_BRANCH=main
      #   TESTPLAN_3_GIT_FILE=face.py
      #
      manifest=$($SHIM --insecure --no-schema-check --setup setup_shim.py \
        --input-target "${1}" --parser env-style)
      shift
      # Find any GIT_REPO lines which match the repo we're looking for.
      # Cut off the _GIT_REPO and after part, we need to know the prefix since
      # we need to know the GIT_FILE that is referenced by the same prefix.
      testplan_indexes=$(grep "_REPO=$GIT_REPO" <<<"${manifest}" \
        | sed -e 's/_REPO.*//g')
      # If it doesn't then check the next index
      if [ "x${testplan_indexes}" == "x" ]; then
        continue
      fi
      # Check each index we found. Look for the file associated with the index
      for testplan_index in ${testplan_indexes[@]}; do
        testcase=$(grep "${testplan_index}_FILE=" <<<"${manifest}" \
          | sed -e 's/.*_FILE=//g')
        echo "$GIT_REPO/$testcase"
      done
    done

.. code-block:: console
    :test:

    $ bash ls-manifest-testplan-git-test.sh https://example.com/alt.git ./manifest-sample.txt
    https://example.com/alt.git/yo.py
    $ bash ls-manifest-testplan-git-test.sh https://example.com/my-repo.git ./manifest-sample.yaml
    https://example.com/my-repo.git/my_test.py
    https://example.com/my-repo.git/face.py

Contributing
------------

This section is documentation for contributing to the TPS Report (manifest)
shim.

We want this shim to be usable on a default format which we'll work to define as
a community upstream. We also want to enable the usage of this shim on abitrary
formats.

Design Goals
````````````

This shim MUST

- Work with arbitrary manifest formats

- Discover verification mechanisms

- Verify the manifest (think secure boot)

- Parse the manifest

- Discover next phase parsers

- Output the manifest in a format the next phase parser can understand

- Execute the next phase parser

Format
``````

We need to come up with a format that allows us to evolve it as we move
forward.

To make sure we have forwards / backwards compatibility we should
include information which allows us to identify what format the document
is in, and what version of that format it is. This will likely also feed
into our input dataflow requirements as we'll need to have the ability
to check an arbitrary input to see if we might have an applicable
converter.

Let's learn from JSON Schema and include a URL where we might be able
to find the schema for the document. We can double up on our previous
needs by asking that the filename of the URL can help us identify our
document format.

We'll parse the URL for the filename component. When we parse it
we'll split on ``.``. If the first part up until the semantic version
will be treated as the format name. Then the semantic version is the
version of the format. Then the rest should be the extension which is
associated with the format which we can use to validate the contents
of the document, such as JSON schema.

Optionally the schema URL may include a hash after which a key value pair may
specify a validation action and target respectively.

.. code-block:: yaml

    $schema: "https://example.com/my.document.format.0.0.0.schema.json#sha256=dfd781dca25694dd808630ff4f27f290ba394143bdcae02911bcafa4a13b8319"

Testing
```````

DFFML's ``tests/test_docstrings.py`` currently handles testing of the shim.

.. code-block:: console

    $ python -u -m unittest discover -v -k manifest

TODO
----

- Review hash calls and update allowlist in ``test_hash_usages()``

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

Notes
-----

- SSH public keys: https://github.com/$USERNAME.keys

- https://github.com/mjg59/ssh_pki
"""
import os
import io
import sys
import copy
import hmac
import json
import shlex
import pickle
import logging
import pathlib
import hashlib
import argparse
import functools
import importlib
import traceback
import contextlib
import subprocess
import dataclasses
import urllib.parse
import importlib.util
from typing import Any, Callable, Dict, Tuple, List, Optional, Union, Type


LOGGER = logging.getLogger(pathlib.Path(__file__).stem)


def popen_write_to_stdin(
    cmd: List[str], write: bytes, **kwargs
) -> subprocess.Popen:
    """
    Call :py:func:`subprocess.Popen`
    """
    read_end, write_end = os.pipe()
    proc = subprocess.Popen(cmd, stdin=read_end, **kwargs)
    os.close(read_end)
    # TODO Should this write be non-blocking in the event that the process dies
    # without finishing reading? What will happen? Can never remember, there's a
    # million reaons why to always use async, this is likley another one.
    # Need to test.
    os.write(write_end, write)
    os.close(write_end)
    return proc


def decode_if_bytes(func):
    """
    Decorator to decode first argument to wrapped function from bytes if the
    argument is an instance of bytes

    >>> import json
    >>> from dffml.util.testing.manifest.shim import decode_if_bytes
    >>>
    >>> decode_if_bytes(json.loads)(b"{}")
    {}
    """

    @functools.wraps(func)
    def wrapper(contents, *args, **kwargs):
        return func(
            contents.decode() if isinstance(contents, bytes) else contents
        )

    return wrapper


# The set of parser attempts we've hardcoded into this file
json_loads_decode_if_bytes = decode_if_bytes(json.loads)
DEFAULT_PARSERS = [
    ("json", json_loads_decode_if_bytes),
]


def parse(
    contents: str, parsers: List[Tuple[str, Callable[[bytes], Any]]] = None
) -> Any:
    r'''
    Given the contents of the manifest file as bytes, parse the contents into
    a dictionary object.

    :param str conents: string containing the manifest file's contents
    :return: a dictionary representing the manifest
    :rtype: dict

    >>> import textwrap
    >>> from dffml.util.testing.manifest.shim import parse
    >>>
    >>> parse(
    ...     textwrap.dedent(
    ...         """\
    ...         $schema: https://example.com/my.manifest.format.0.0.0.schema.json
    ...         testplan:
    ...         - git:
    ...             repo: https://example.com/my-repo.git
    ...             branch: main
    ...             file: my_test.py
    ...         """
    ...     )
    ... )
    {'$schema': 'https://example.com/my.manifest.format.0.0.0.schema.json', 'testplan': [{'git': {'repo': 'https://example.com/my-repo.git', 'branch': 'main', 'file': 'my_test.py'}}]}
    '''
    if parsers is None:
        parsers = DEFAULT_PARSERS
    # If we get the end of the list of parsers to try There will be and an
    # Exception we can raise
    errors = {}
    for name, parser in parsers:
        try:
            return parser(contents)
        except Exception as error:
            errors[name] = (error, traceback.format_exc())
            LOGGER.getChild(f"parse.{name}").debug(errors[name][1])
    for name, (_error, traceback_string) in errors.items():
        print(f"Parser {name!r}: {traceback_string}", file=sys.stderr)
    raise list(errors.values())[-1][0]


def serializer_env(
    manifest,
    quoted: bool = False,
    prefix: Optional[List[str]] = None,
    output: Optional[io.BytesIO] = None,
) -> bytes:
    """
    Take a dictionary manifest and output it so that it could be parsed by
    a shell environment.

    This function calls itself recursivly using prefix and output to write
    nested keys to the output buffer.

    >>> from dffml.util.testing.manifest.shim import serializer_env
    >>>
    >>> obj = {
    ...     "key1": "hello",
    ...     "key2": [
    ...         {"indexed_subkey3": "world", "indexed_subkey4": "hi"},
    ...         {"indexed_subkey5": "there"},
    ...     ]
    ... }
    >>>
    >>> print(serializer_env(obj).decode(), end="")
    KEY1=hello
    KEY2_0_INDEXED_SUBKEY3=world
    KEY2_0_INDEXED_SUBKEY4=hi
    KEY2_1_INDEXED_SUBKEY5=there
    >>>
    >>> print(serializer_env(obj, quoted=True).decode(), end="")
    KEY1="hello"
    KEY2_0_INDEXED_SUBKEY3="world"
    KEY2_0_INDEXED_SUBKEY4="hi"
    KEY2_1_INDEXED_SUBKEY5="there"
    """
    if prefix is None:
        prefix = []
    if output is not None:
        if isinstance(manifest, dict):
            for key, value in manifest.items():
                serializer_env(
                    value, quoted=quoted, prefix=prefix + [key], output=output
                )
        elif isinstance(manifest, list):
            for i, value in enumerate(manifest):
                serializer_env(
                    value,
                    quoted=quoted,
                    prefix=prefix + [str(i)],
                    output=output,
                )
        else:
            # In this case the manifest is any other non-iterable value
            formatted = "_".join(prefix).upper() + "="
            if quoted:
                formatted += f'"{manifest!s}"'
            else:
                formatted += str(manifest)
            output.write(formatted.encode() + b"\n")
    else:
        with io.BytesIO() as output:
            serializer_env(manifest, quoted=quoted, output=output)
            return output.getvalue()


def serializer_env_quoted(manifest) -> bytes:
    return serializer_env(manifest, quoted=True)


# Serialization to the next phase parser
DEFAULT_SERIALIZERS = {
    "none": lambda manifest: manifest,
    "json": lambda manifest: json.dumps(manifest).encode(),
    "pickle": pickle.dumps,
    "env": serializer_env,
    "env_quoted": serializer_env_quoted,
}

# Try to parse with yaml if available
with contextlib.suppress((ImportError, ModuleNotFoundError)):
    import yaml

    yaml_safe_load_decode_if_bytes = decode_if_bytes(yaml.safe_load)
    DEFAULT_PARSERS.append(("yaml", yaml_safe_load_decode_if_bytes))
    DEFAULT_SERIALIZERS["yaml"] = lambda manifest: yaml.dump(manifest).encode()


def discover_dataclass_environ(
    dataclass,
    prefix: str,
    environ: Dict[str, str] = None,
    *,
    dataclass_key: str = None,
):
    r"""
    >>> import dataclasses
    >>> from dffml.util.testing.manifest.shim import discover_dataclass_environ
    >>>
    >>> @dataclasses.dataclass
    ... class MyDataclass:
    ...     name: str
    ...     version: str
    ...
    ...     PREFIX = "MYPREFIX_"
    >>>
    >>> discover_dataclass_environ(
    ...     MyDataclass,
    ...     MyDataclass.PREFIX,
    ...     {
    ...         "MYPREFIX_NAME_EXAMPLE_FORMAT": "Example Format",
    ...         "MYPREFIX_VERSION_EXAMPLE_FORMAT": "0.0.0",
    ...     },
    ... )
    {'example_format': MyDataclass(name='Example Format', version='0.0.0')}
    >>>
    >>> discover_dataclass_environ(
    ...     MyDataclass,
    ...     MyDataclass.PREFIX,
    ...     {
    ...         "MYPREFIX_VERSION_EXAMPLE_FORMAT": "0.0.0",
    ...     },
    ...     dataclass_key="name",
    ... )
    {'example_format': MyDataclass(name='example_format', version='0.0.0')}
    """
    if environ is None:
        environ = os.environ
    discovered_parsers = {}
    for key, value in environ.items():
        if not key.startswith(prefix):
            continue
        metadata_key, parser_name = (
            key[len(prefix) :].lower().split("_", maxsplit=1)
        )
        discovered_parsers.setdefault(parser_name, {})
        discovered_parsers[parser_name][metadata_key] = value
    # Ensure they are loaded into the correct class
    for key, value in discovered_parsers.items():
        if dataclass_key is not None and dataclass_key not in value:
            value[dataclass_key] = key
        discovered_parsers[key] = dataclass(**value)
    return discovered_parsers


@dataclasses.dataclass
class ManifestFormatParser:
    """
    Read in configuration to determine what the next phase of parsing is.

    args holds arguments passed to target.
    """

    name: str
    format: str
    version: str
    action: str
    serialize: str = "none"
    target: Union[str, Callable[[Dict[str, Any]], Any]] = ""
    args: str = ""

    PREFIX: str = "MANIFEST_PARSER_"
    DATACLASS_KEY: str = "name"


def next_phase_parser_action_stdout(
    args: argparse.Namespace, parser: ManifestFormatParser, manifest: bytes
):
    """
    String encode the manifest bytes and print to stdout
    """
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write(manifest)
    else:
        sys.stdout.write(manifest.decode())


def next_phase_parser_action_exec_stdin(
    args: argparse.Namespace, parser: ManifestFormatParser, manifest: bytes
):
    """
    Execute the next phase and pass the manifest via stdin
    """
    popen_write_to_stdin(
        [parser.target, *shlex.split(parser.args)], manifest
    ).wait()


def next_phase_parser_action_call_function(
    args: argparse.Namespace,
    parser: ManifestFormatParser,
    manifest: Dict[str, Any],
):
    """
    Execute the next phase and pass the manifest as only argument to the
    parser.target function.
    """
    parser.target(manifest)


DEFAULT_FORMAT_PARSER_ACTIONS = {
    "stdout": next_phase_parser_action_stdout,
    "exec_stdin": next_phase_parser_action_exec_stdin,
    "call_function": next_phase_parser_action_call_function,
}


class ValidationError(Exception):
    """
    Raised when manifest validation fails
    """


def validation_action_hashlib(
    args: argparse.Namespace, contents: bytes
) -> bytes:
    """
    Use the validation target as the hash algorithm. Compare digest of contents
    to the zeroth index of validation args.
    """
    hash_validation = hashlib.new(args.validation_target)
    hash_validation.update(contents)
    manifest_hash = hash_validation.hexdigest()
    if not hmac.compare_digest(args.validation_args[0], manifest_hash):
        raise ValidationEror(
            f"Manifest hash {manifest_hash} was not equal to given hash {args.validation_args[0]}"
        )
    return contents


def validation_action_exec_stdin(
    args: argparse.Namespace, contents: bytes
) -> bytes:
    """
    Execute the validation target and pass the manifest via stdin
    """
    cmd = [args.validation_target, *args.validation_args]
    proc = popen_write_to_stdin(
        cmd, contents, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    proc.wait()
    if proc.returncode != 0:
        raise ValidationError(f"{stderr.decode()}")
    return stdout


DEFAULT_VALIDATION_ACTIONS = {
    "hashlib": validation_action_hashlib,
    "exec_stdin": validation_action_exec_stdin,
}


def input_action_stdin(args: argparse.Namespace):
    """
    Read manifest from stdin
    """
    return sys.stdin.buffer.read()


def input_action_target(args: argparse.Namespace):
    """
    Manifest is input target
    """
    return args.input_target.encode()


def input_action_read_bytes(args: argparse.Namespace):
    """
    Read manifest from target filepath as bytes
    """
    if args.input_target is None:
        raise ValueError("input target must be filepath but was None")
    input_target_path = pathlib.Path(args.input_target)
    if not input_target_path.exists():
        raise ValueError(
            f"input target must be filepath but was {args.input_target!r}"
        )
    return input_target_path.read_bytes()


DEFAULT_INPUT_ACTIONS = {
    "stdin": input_action_stdin,
    "target": input_action_target,
    "read_bytes": input_action_read_bytes,
}


def parse_schema_url(schema_url):
    """
    Parse a schema URL. Return a tuple of document format, document version,
    schema URL, schema validation action, schema validation target.

    Do not assume any extension. Many will use JSON schema but some may have a
    binary manifest format or something that doesn't lend itself to JSON schema.
    """
    parsed = urllib.parse.urlparse(schema_url)
    document_format_version = pathlib.Path(parsed.path).name
    document_format_version_split = document_format_version.split(".")
    # Once we find three integer values we are at the end (beginning from left
    # right) of the semantic version.
    ints_found = 0
    for i, value in enumerate(document_format_version_split[::-1]):
        ints_found += int(value.isdigit())
        if ints_found == 3:
            break
    i += 1
    document_format = ".".join(document_format_version_split[:-i])
    document_version = ".".join(document_format_version_split[-i : (-i + 3)])
    schema_valiation_action = None
    schema_valiation_target = None
    if parsed.fragment and "=" in parsed.fragment:
        (
            schema_valiation_action,
            schema_valiation_target,
        ) = parsed.fragment.split("=", maxsplit=1)
    return (
        document_format,
        document_version,
        parsed._replace(fragment="").geturl(),
        schema_valiation_action,
        schema_valiation_target,
    )


class InputActionNotFound(Exception):
    """
    Input actions are used to read in manifest. If one is not found then the
    manifest cannot be read.
    """


class ValidationActionNotFound(Exception):
    """
    Validation actions are used to verify the manifest comes from a trusted
    source. If one is not found then the manifest cannot be parsed.
    """


class ParserNotFound(Exception):
    """
    Document format/version/action combination not found. It was not registered
    via the environment.
    """


class SchemaNotFound(Exception):
    """
    Raised when document does not have a $schema key at the top level
    """


class NextPhaseActionNotFound(Exception):
    """
    Next phase action handles transition to next phase by handing off serialized
    manifest to selected parser.
    """


class SerializerNotFound(Exception):
    """
    Manifest must be serialized into a format the next phase understands. This
    is raised if the serializer selected by the next phase parser was not found.
    """


def shim(
    args: argparse.Namespace,
    environ: Optional[Dict[str, str]] = None,
    parsers: Optional[List[Tuple[str, Callable[[bytes], Any]]]] = None,
    input_actions: Optional[
        Dict[str, Callable[[argparse.Namespace], bytes]]
    ] = None,
    validation_actions: Optional[
        Dict[str, Callable[[argparse.Namespace, bytes], bytes]]
    ] = None,
    serializers: Optional[Dict[str, Callable[[Any], bytes]]] = None,
    format_parser_actions: Optional[
        Dict[str, Callable[[argparse.Namespace, bytes], Any]]
    ] = None,
    next_phase_parsers: Dict[
        Tuple[str, str, str], ManifestFormatParser
    ] = None,
    next_phase_parser_class: Type[ManifestFormatParser] = ManifestFormatParser,
):
    r'''
    Python Examples
    ---------------

    >>> import sys
    >>> import types
    >>> import hashlib
    >>> import textwrap
    >>> from dffml.util.testing.manifest.shim import shim, ManifestFormatParser
    >>>
    >>> DOCUMENT_FORMAT = "my.manifest.format"
    >>> DOCUMENT_VERSION = "0.0.0"
    >>>
    >>> contents = f"""\
    ... ---
    ... $schema: https://example.com/{DOCUMENT_FORMAT}.{DOCUMENT_VERSION}.schema.json
    ... testplan:
    ... - git:
    ...     repo: https://example.com/my-repo.git
    ...     branch: dev
    ...     file: my_test.py
    ... - git:
    ...     repo: https://example.com/their-repo.git
    ...     branch: main
    ...     file: their_test.py
    ... """
    >>>
    >>> contents_sha256 = hashlib.sha256(contents.encode()).hexdigest()
    >>>
    >>> ManifestFormatParser.PREFIX
    'MANIFEST_PARSER_'
    >>>
    >>> PARSER_KEY = "ONE"
    >>> environ = {
    ...     f"MANIFEST_PARSER_NAME_{PARSER_KEY}": "A",
    ...     f"MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "json",
    ...     f"MANIFEST_PARSER_ACTION_{PARSER_KEY}": "stdout",
    ... }
    >>>
    >>> PARSER_KEY = "TWO"
    >>> environ.update({
    ...     f"MANIFEST_PARSER_NAME_{PARSER_KEY}": "B",
    ...     f"MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "yaml",
    ...     f"MANIFEST_PARSER_ACTION_{PARSER_KEY}": "exec_stdin",
    ...     f"MANIFEST_PARSER_TARGET_{PARSER_KEY}": "cat",
    ... })
    >>>
    >>> PARSER_KEY = "THREE"
    >>> environ.update({
    ...     f"MANIFEST_PARSER_NAME_{PARSER_KEY}": "C",
    ...     f"MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "pickle",
    ...     f"MANIFEST_PARSER_ACTION_{PARSER_KEY}": "exec_stdin",
    ...     f"MANIFEST_PARSER_TARGET_{PARSER_KEY}": sys.executable,
    ...     f"MANIFEST_PARSER_ARGS_{PARSER_KEY}": "-c 'import sys, pickle, pprint; pprint.pprint(pickle.load(sys.stdin.buffer))'",
    ... })
    >>>
    >>> PARSER_KEY = "FOUR"
    >>> environ.update({
    ...     f"MANIFEST_PARSER_NAME_{PARSER_KEY}": "D",
    ...     f"MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "env",
    ...     f"MANIFEST_PARSER_ACTION_{PARSER_KEY}": "stdout",
    ... })
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=True,
    ...         only_validate=False,
    ...         parser="A",
    ...         input_target=contents,
    ...     ),
    ...     environ=environ,
    ... )
    {"$schema": "https://example.com/my.manifest.format.0.0.0.schema.json", "testplan": [{"git": {"repo": "https://example.com/my-repo.git", "branch": "dev", "file": "my_test.py"}}, {"git": {"repo": "https://example.com/their-repo.git", "branch": "main", "file": "their_test.py"}}]}
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=True,
    ...         only_validate=False,
    ...         parser="D",
    ...         input_target=contents,
    ...     ),
    ...     environ=environ,
    ... )
    $SCHEMA=https://example.com/my.manifest.format.0.0.0.schema.json
    TESTPLAN_0_GIT_REPO=https://example.com/my-repo.git
    TESTPLAN_0_GIT_BRANCH=dev
    TESTPLAN_0_GIT_FILE=my_test.py
    TESTPLAN_1_GIT_REPO=https://example.com/their-repo.git
    TESTPLAN_1_GIT_BRANCH=main
    TESTPLAN_1_GIT_FILE=their_test.py
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=True,
    ...         only_validate=False,
    ...         parser="B",
    ...         input_target=contents,
    ...     ),
    ...     environ=environ,
    ... )
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=False,
    ...         only_validate=False,
    ...         parser="C",
    ...         input_target=contents,
    ...         validation_action="hashlib",
    ...         validation_target="sha256",
    ...         validation_args=[contents_sha256],
    ...     ),
    ...     environ=environ,
    ... )
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=False,
    ...         only_validate=False,
    ...         parser="C",
    ...         input_target=contents,
    ...         validation_action="exec_stdin",
    ...         validation_target=sys.executable,
    ...         validation_args=["-c", f'import sys, hmac, hashlib; stdin = sys.stdin.buffer.read(); rc = 0 if hmac.compare_digest(hashlib.sha256(stdin).hexdigest(), \"{contents_sha256}\") else 1; print(stdin.decode()); sys.exit(rc)'],
    ...     ),
    ...     environ=environ,
    ... )
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         no_schema_check=True,
    ...         input_action="target",
    ...         insecure=False,
    ...         only_validate=False,
    ...         parser="C",
    ...         input_target=contents,
    ...         validation_action="exec_stdin",
    ...         validation_target=sys.executable,
    ...         validation_args=["-c", f'import sys, hmac, hashlib; stdin = sys.stdin.buffer.read(); rc = 0 if hmac.compare_digest(hashlib.sha256(stdin).hexdigest(), \"{contents_sha256}a\") else 1; print(stdin.decode()); sys.exit(rc)'],
    ...     ),
    ...     environ=environ,
    ... )
    Traceback (most recent call last):
        ...
    dffml.util.testing.manifest.shim.ValidationError

    Console Examples
    ----------------


    Download the shim

    .. code-block:: console
        :test:
        :replace: import os; cmds[0] = ["cp", os.path.join(ctx["root"], "dffml", "util", "testing", "manifest", "shim.py"), "shim.py"]

        $ curl -sfLO https://github.com/intel/dffml/raw/manifest/dffml/util/testing/manifest/shim.py

    Create a test manifest

    **manifest.yaml**

    .. code-block:: yaml
        :test:
        :filepath: manifest.yaml

        ---
        $schema: https://example.com/my.manifest.format.0.0.0.schema.json
        testplan:
        - git:
            repo: https://example.com/my-repo.git
            branch: dev
            file: my_test.py
        - git:
            repo: https://example.com/their-repo.git
            branch: main
            file: their_test.py

    Write whatever code you need to initialize the shim's environment.

    **my_shim_setup.py**

    .. code-block:: python
        :test:
        :filepath: my_shim_setup.py

        """
        Ensure we can parse YAML manifests. Do this by downloading PyYAML to a
        cache directory and doing a direct import, or downloading to a tempdir
        every execution. If it's already installed, great. This should be a last
        resort.
        """
        import re
        import sys
        import pathlib
        import tempfile
        import platform
        import zipimport
        import contextlib
        import urllib.request

        import shim

        # In the event that PyYAML is not installed this installs it locally
        # (relative to this file)
        PYYAML_URL: str = "https://pypi.org/simple/pyyaml/"
        CACHE: pathlib.Path = pathlib.Path(__file__).resolve().parent.joinpath(
            ".cache", "wheels",
        )


        @contextlib.contextmanager
        def cache_dir():
            """
            Try to cache locally if possible, create a directory to store wheels in
            relative to this file. If that fails, use a tempdir.
            """
            try:
                CACHE.mkdir(parents=True, exist_ok=True)
                yield CACHE
            except:
                with tempfile.TemporaryDirectory() as tempdir:
                    yield tempdir


        def setup_shim_func(parsers, next_phase_parsers, **kwargs):
            # Declare another parser
            parser = shim.ManifestFormatParser(
                name="myparser",
                format="my.manifest.format",
                version="0.0.0",
                serialize="env",
                action="stdout"
            )
            # Add the parser
            next_phase_parsers[(parser.format, parser.version, parser.name)] = parser

            # Download PyYAML and load the parser if not preloaded
            if len(parsers) < 2:
                return

            # Use ether the cache or a temporary directory to hold the package
            with cache_dir() as package_dir:
                # Path to wheel on disk
                wheel_path = pathlib.Path(package_dir, "package.whl")
                # Download if not cached
                if not wheel_path.exists():
                    # Find the correct package
                    with urllib.request.urlopen(PYYAML_URL) as response:
                        links = re.findall(r"(https://.*.whl)", response.read().decode())
                    # Search backwards because last links are the most recent package versions
                    end_href = '" '
                    links = [
                        link[: link.index(end_href)]
                        for link in links[::-1]
                        if (
                            end_href in link
                            and f"cp{sys.version_info.major}{sys.version_info.minor}" in link
                            and platform.machine() in link
                            and {"darwin": "macos"}.get(sys.platform, sys.platform) in link
                        )
                    ]
                    # Grab the most recent applicable wheel link
                    wheel_url = links[0]
                    # Download the wheel
                    with urllib.request.urlopen(wheel_url) as response:
                        wheel_path.write_bytes(response.read())
                # Load the module from the downloaded wheel
                yaml = zipimport.zipimporter(str(wheel_path)).load_module("yaml")
                # Setup the parser for use by the shim
                parsers.append(("yaml", shim.decode_if_bytes(yaml.safe_load)))

    .. code-block:: console
        :test:

        $ python -u shim.py \
            --setup my_shim_setup.py --setup-function-name setup_shim_func \
            --insecure --no-schema-check \
            --input-target manifest.yaml --parser myparser
    '''
    # Set environment to os.environ if not given
    if environ is None:
        environ = copy.deepcopy(os.environ)
    # Load defaults if not given
    if parsers is None:
        parsers = copy.deepcopy(DEFAULT_PARSERS)
    if input_actions is None:
        input_actions = copy.deepcopy(DEFAULT_INPUT_ACTIONS)
    if validation_actions is None:
        validation_actions = copy.deepcopy(DEFAULT_VALIDATION_ACTIONS)
    if format_parser_actions is None:
        format_parser_actions = copy.deepcopy(DEFAULT_FORMAT_PARSER_ACTIONS)
    if serializers is None:
        serializers = copy.deepcopy(DEFAULT_SERIALIZERS)
    if next_phase_parsers is None:
        next_phase_parsers = {}
    # Discover options for format parsers for next phase
    next_phase_parsers.update(
        {
            (parser.format, parser.version, parser.name): parser
            for parser in discover_dataclass_environ(
                next_phase_parser_class,
                next_phase_parser_class.PREFIX,
                environ=environ,
                dataclass_key=next_phase_parser_class.DATACLASS_KEY,
            ).values()
        }
    )
    # Run any Python assisted setup for extra features not defined in upstream
    if args.setup is not None:
        # Check if file exists
        setup_path = pathlib.Path(args.setup)
        if not setup_path.exists():
            # Provide helpful error message if not
            raise FileNotFoundError(
                f"Setup file {args.setup!r} does not exist"
            )
        # Module name is filename without the extension
        setup_module_name = setup_path.stem
        # Create module from file
        spec = importlib.util.spec_from_file_location(
            setup_module_name, setup_path
        )
        setup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup_module)
        if not hasattr(setup_module, args.setup_function_name):
            # Raise exception if the there is not setup function
            raise ValueError(
                f"setup module {args.setup!r} has no"
                f" function named {args.setup_function_name!r}"
            )
        # Call the setup function
        getattr(setup_module, args.setup_function_name)(**locals())
    # Determine how to get the manifest
    if args.input_action not in input_actions:
        raise InputActionNotFound(
            "Input action is used to read in manifest"
            f" {args.input_action!r} not found in loaded input actions:"
            f" {input_actions!r}"
        )
    input_action = input_actions[args.input_action]
    # Get the manifest and any validation data that might be associated with it
    contents = input_action(args)
    # Validate the manifest
    if not args.insecure:
        if args.validation_action is None:
            # Ensure we have a validation action if we are not in insecure mode
            raise ValueError(
                "If not in insecure mode a validation action must be specified."
                f" Choose from {set(validation_actions.keys())!r}"
            )
        # Determine how to get validate the manifest
        if args.validation_action not in validation_actions:
            raise ValidationActionNotFound(
                "Validation action is used to read in manifest"
                f" {args.validation_action!r} not found in loaded"
                f" validation actions: {validation_actions!r}"
            )
        validation_action = validation_actions[args.validation_action]
        # Validate the manifest. Override unvalidated contents with just
        # validated.
        contents = validation_action(args, contents)
    if args.only_validate:
        # Bail if we are only validating the manifest and not parsing it
        return
    # Parse the manifest
    manifest = parse(contents, parsers=parsers)
    # Ensure we have
    if "$schema" not in manifest:
        raise SchemaNotFound(
            "Manifest does not contain $schema key at document root"
        )
    # Determine document format and version
    (
        document_format,
        document_version,
        schema_url,
        schema_validation_action,
        schema_validation_target,
    ) = parse_schema_url(manifest["$schema"])
    # Validate schema
    if not args.no_schema_check:
        raise NotImplementedError(
            f"schema validation not implemented {(schema_url, schema_validation_action, schema_validation_target)!r}"
        )
    # Grab mapped parser
    format_version_action = (
        document_format,
        document_version,
        args.parser,
    )
    if format_version_action not in next_phase_parsers:
        raise ParserNotFound(
            "Unknown document format/version/action combination."
            " Was it registered via environment variables?"
            f" {format_version_action!r} not found in: {next_phase_parsers!r}"
        )
    parser = next_phase_parsers[format_version_action]
    # Determine how to get the manifest
    if parser.action not in format_parser_actions:
        raise NextPhaseActionNotFound(
            "Unknown action (tranistion to next phase is done by the"
            f' "action") {parser.action!r} not found in:'
            f" {format_parser_actions!r}"
        )
    action = format_parser_actions[parser.action]
    # Pick serialization method according to parsers requirements
    if parser.serialize not in serializers:
        raise SerializerNotFound(
            "Unknown serializer (serializes manifest before next phase)"
            f" {parser.serialize!r} not found in:"
            f" {serializers!r}"
        )
    serializer = serializers[parser.serialize]
    # Serialize manifest
    serialized = serializer(manifest)
    # Send manifest to next phase
    action(args, parser, serialized)


# Function name which will setup the shim environment. The function will be
# passed all of the same objects shim() is passed.
DEFAULT_SETUP_FUNCTION_NAME = "setup_shim"


def make_parser():
    parser = argparse.ArgumentParser(
        prog="shim.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )

    parser.add_argument("--log", default="critical")
    parser.add_argument(
        "-l", "--lockdown", action="store_true", default=False,
    )
    parser.add_argument(
        "-s", "--strict", action="store_true", default=False,
    )
    parser.add_argument(
        "--setup",
        default=None,
        help=f"Python script with a {DEFAULT_SETUP_FUNCTION_NAME} function",
    )
    parser.add_argument(
        "--setup-function-name",
        default=DEFAULT_SETUP_FUNCTION_NAME,
        help="Name of the function which preforms setup within setup file",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        default=False,
        help=f"Skip manifest validation (validation currently unsupported)",
    )
    parser.add_argument(
        "--only-validate",
        action="store_true",
        default=False,
        help=f"Exit after validating the manifest (validation currently unsupported)",
    )
    parser.add_argument(
        "--no-schema-check",
        action="store_true",
        default=False,
        help=f"Skip checking that the manifest adheres to the schema",
    )
    parser.add_argument(
        "--input-action",
        choices=DEFAULT_INPUT_ACTIONS.keys(),
        default="read_bytes",
        help=f"Method for aquiring manifest",
    )
    parser.add_argument(
        "--input-target",
        help="External callable to run which provides manifest",
    )
    parser.add_argument(
        "--input-args",
        nargs="?",
        default=[],
        help="Arguments for input action if externally callable",
    )
    parser.add_argument(
        "--validation-action",
        choices=DEFAULT_VALIDATION_ACTIONS.keys(),
        help=f"Method for aquiring manifest",
    )
    parser.add_argument(
        "--validation-target",
        help="External callable to run which does validation",
    )
    parser.add_argument(
        "--validation-args", help="Arguments for validation target",
    )
    parser.add_argument(
        "--parser", required=True, help=f"Parser to handle next phase",
    )
    parser.add_argument(
        "--target", help="Target for next phase of manifest processing",
    )
    parser.add_argument(
        "args",
        nargs="?",
        default=[],
        help="Arguments for format parser. Will be run through templating before use",
    )
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper()))

    shim(args)


if __name__ == "__main__":
    main()
