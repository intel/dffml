#!/usr/bin/env python
"""
Test Procedure Specification (TPS) Report Manifest Shim
=======================================================

Validate and parse a Test Procedure Specification (TPS) Report manifest. Execute
something for the next stage of parsing.

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

Notes
-----

- SSH public keys: https://github.com/$USERNAME.keys

- https://github.com/mjg59/ssh_pki
"""
import os
import io
import sys
import hmac
import json
import shlex
import pickle
import pathlib
import hashlib
import argparse
import functools
import importlib
import traceback
import contextlib
import subprocess
import dataclasses
import importlib.util
from typing import Dict, List, Callable, Any, Union, Optional


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
DEFAULT_PARSERS = {
    "json": decode_if_bytes(json.loads),
}


def parse(contents: str, parsers: Dict[str, Callable[[str], Any]] = None):
    r'''
    Given the contents of the manifest file as a string, parse the contents into
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
    ...         $document_format: tps.manifest
    ...         $document_version: 0.0.1
    ...         testplan:
    ...         - git:
    ...             repo: https://example.com/my-repo.git
    ...             branch: main
    ...             file: my_test.py
    ...         """
    ...     )
    ... )
    {'$document_format': 'tps.manifest', '$document_version': '0.0.1', 'testplan': [{'git': {'repo': 'https://example.com/my-repo.git', 'branch': 'main', 'file': 'my_test.py'}}]}
    '''
    if parsers is None:
        parsers = DEFAULT_PARSERS
    # If we get the end of the list of parsers to try There will be and an
    # Exception we can raise
    errors = {}
    for name, parser in parsers.items():
        try:
            return parser(contents)
        except Exception as error:
            errors[name] = (error, traceback.format_exc())
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
    "json": lambda manifest: json.dumps(manifest).encode(),
    "pickle": pickle.dumps,
    "env": serializer_env,
    "env_quoted": serializer_env_quoted,
}

# Try to parse with yaml if available
with contextlib.suppress((ImportError, ModuleNotFoundError)):
    import yaml

    DEFAULT_PARSERS["yaml"] = decode_if_bytes(yaml.safe_load)
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
    ...         "MYPREFIX_VERSION_EXAMPLE_FORMAT": "0.0.1",
    ...     },
    ... )
    {'example_format': MyDataclass(name='Example Format', version='0.0.1')}
    >>>
    >>> discover_dataclass_environ(
    ...     MyDataclass,
    ...     MyDataclass.PREFIX,
    ...     {
    ...         "MYPREFIX_VERSION_EXAMPLE_FORMAT": "0.0.1",
    ...     },
    ...     dataclass_key="name",
    ... )
    {'example_format': MyDataclass(name='example_format', version='0.0.1')}
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
    serialize: str
    action: str
    target: str = ""
    args: str = ""

    PREFIX: str = "TPS_MANIFEST_PARSER_"
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


DEFAULT_FORMAT_PARSER_ACTIONS = {
    "stdout": next_phase_parser_action_stdout,
    "exec_stdin": next_phase_parser_action_exec_stdin,
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


class InputActionNotFound(Exception):
    """
    Input actions are used to read in manifest. If one is not found then the
    manifest cannot be read.
    """


class ParserNotFound(Exception):
    """
    Document format/version/action combination not found. It was not registered
    via the environment.
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
    >>> DOCUMENT_FORMAT = "tps.manifest"
    >>> DOCUMENT_VERSION = "0.0.1"
    >>>
    >>> contents = f"""\
    ... $document_format: {DOCUMENT_FORMAT}
    ... $document_version: {DOCUMENT_VERSION}
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
    'TPS_MANIFEST_PARSER_'
    >>>
    >>> PARSER_KEY = "ONE"
    >>> environ = {
    ...     f"TPS_MANIFEST_PARSER_NAME_{PARSER_KEY}": "A",
    ...     f"TPS_MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"TPS_MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"TPS_MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "json",
    ...     f"TPS_MANIFEST_PARSER_ACTION_{PARSER_KEY}": "stdout",
    ... }
    >>>
    >>> PARSER_KEY = "TWO"
    >>> environ.update({
    ...     f"TPS_MANIFEST_PARSER_NAME_{PARSER_KEY}": "B",
    ...     f"TPS_MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"TPS_MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"TPS_MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "yaml",
    ...     f"TPS_MANIFEST_PARSER_ACTION_{PARSER_KEY}": "exec_stdin",
    ...     f"TPS_MANIFEST_PARSER_TARGET_{PARSER_KEY}": "cat",
    ... })
    >>>
    >>> PARSER_KEY = "THREE"
    >>> environ.update({
    ...     f"TPS_MANIFEST_PARSER_NAME_{PARSER_KEY}": "C",
    ...     f"TPS_MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"TPS_MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"TPS_MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "pickle",
    ...     f"TPS_MANIFEST_PARSER_ACTION_{PARSER_KEY}": "exec_stdin",
    ...     f"TPS_MANIFEST_PARSER_TARGET_{PARSER_KEY}": sys.executable,
    ...     f"TPS_MANIFEST_PARSER_ARGS_{PARSER_KEY}": "-c 'import sys, pickle, pprint; pprint.pprint(pickle.load(sys.stdin.buffer))'",
    ... })
    >>>
    >>> PARSER_KEY = "FOUR"
    >>> environ.update({
    ...     f"TPS_MANIFEST_PARSER_NAME_{PARSER_KEY}": "D",
    ...     f"TPS_MANIFEST_PARSER_FORMAT_{PARSER_KEY}": DOCUMENT_FORMAT,
    ...     f"TPS_MANIFEST_PARSER_VERSION_{PARSER_KEY}": DOCUMENT_VERSION,
    ...     f"TPS_MANIFEST_PARSER_SERIALIZE_{PARSER_KEY}": "env",
    ...     f"TPS_MANIFEST_PARSER_ACTION_{PARSER_KEY}": "stdout",
    ... })
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         input_action="target",
    ...         insecure=True,
    ...         only_validate=False,
    ...         parser="A",
    ...         input_target=contents,
    ...     ),
    ...     environ=environ,
    ... )
    {"$document_format": "tps.manifest", "$document_version": "0.0.1", "testplan": [{"git": {"repo": "https://example.com/my-repo.git", "branch": "dev", "file": "my_test.py"}}, {"git": {"repo": "https://example.com/their-repo.git", "branch": "main", "file": "their_test.py"}}]}
    >>>
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
    ...         input_action="target",
    ...         insecure=True,
    ...         only_validate=False,
    ...         parser="D",
    ...         input_target=contents,
    ...     ),
    ...     environ=environ,
    ... )
    $DOCUMENT_FORMAT=tps.manifest
    $DOCUMENT_VERSION=0.0.1
    TESTPLAN_0_GIT_REPO=https://example.com/my-repo.git
    TESTPLAN_0_GIT_BRANCH=dev
    TESTPLAN_0_GIT_FILE=my_test.py
    TESTPLAN_1_GIT_REPO=https://example.com/their-repo.git
    TESTPLAN_1_GIT_BRANCH=main
    TESTPLAN_1_GIT_FILE=their_test.py
    >>> shim(
    ...     types.SimpleNamespace(
    ...         setup=None,
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

        $document_format: tps.manifest
        $document_version: 0.0.1
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

        import shim

        def setup_shim_func(parsers, **kwargs):
            # Declare another parser
            parser = shim.ManifestFormatParser(
                name="myparser",
                format="tps.manifest",
                version="0.0.1",
                serialize="env",
                action="stdout"
            )
            # Add the parser
            parsers[(parser.format, parser.version, parser.name)] = parser

    .. code-block:: console
        :test:

        $ python -u shim.py \
            --setup my_shim_setup.py --setup-function-name setup_shim_func \
            --input-target manifest.yaml --parser myparser --insecure
    '''
    # Set environment to os.environ if not given
    if environ is None:
        environ = os.environ
    # Load default actions if not given
    if input_actions is None:
        input_actions = DEFAULT_INPUT_ACTIONS
    if validation_actions is None:
        validation_actions = DEFAULT_VALIDATION_ACTIONS
    if format_parser_actions is None:
        format_parser_actions = DEFAULT_FORMAT_PARSER_ACTIONS
    if serializers is None:
        serializers = DEFAULT_SERIALIZERS
    # Discover options for format parsers for next phase
    parsers = {
        (parser.format, parser.version, parser.name): parser
        for parser in discover_dataclass_environ(
            ManifestFormatParser,
            ManifestFormatParser.PREFIX,
            environ=environ,
            dataclass_key=ManifestFormatParser.DATACLASS_KEY,
        ).values()
    }
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
        validation_action = validation_actions[args.validation_action]
        # Validate the manifest. Override unvalidated contents with just
        # validated.
        contents = validation_action(args, contents)
    if args.only_validate:
        # Bail if we are only validating the manifest and not parsing it
        return
    # Parse the manifest
    manifest = parse(contents)
    # Grab mapped parser
    format_version_action = (
        manifest.get("$document_format", None),
        manifest.get("$document_version", None),
        args.parser,
    )
    if format_version_action not in parsers:
        raise ParserNotFound(
            "Unknown document format/version/action combination."
            " Was it registered via environment variables?"
            f" {format_version_action!r} not found in: {parsers!r}"
        )
    parser = parsers[format_version_action]
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

    # TODO Addition of remotely loadable PyPi zip packages? Perhaps it's easier
    # if we allow for the importing of a setup file with a setup function in it
    # that is called with the shim execution context (the arguments to shim()).
    # This is useful because often we find ourselves in a situation where the
    # reason we are using the shim is that we have no other dependencies
    # installed other than Python itself. Adding the ability to add more parsers
    # via the importing of another file which can then import or implement
    # parsers would be good.
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

    shim(args)


if __name__ == "__main__":
    main()
