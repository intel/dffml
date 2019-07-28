import os
import glob
import shutil
import getpass
import configparser
import pkg_resources
import distutils.dir_util

from ..version import VERSION
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD

config = configparser.ConfigParser()
config.read(os.path.join(os.path.expanduser("~"), ".gitconfig"))

USER = getpass.getuser()
NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")


def create_from_skel(name):
    class CreateCMD(CMD):

        arg_user = Arg(
            "-user",
            help=f"Your username (default: {USER})",
            default=USER,
            required=False,
        )
        arg_name = Arg(
            "-name",
            help=f"Your name (default: {NAME})",
            default=NAME,
            required=False,
        )
        arg_email = Arg(
            "-email",
            help=f"Your email (default: {EMAIL})",
            default=EMAIL,
            required=False,
        )
        arg_description = Arg(
            "-description",
            help=f"Description of python package (default: DFFML {name} {{package name}})",
            default=None,
            required=False,
        )
        arg_target = Arg(
            "-target",
            help=f"Directory to put code in (default: same as package name)",
            default=None,
            required=False,
        )
        arg_package = Arg("package", help="Name of python package to create")

        async def run(self):
            # Set description if None
            if not self.description:
                self.description = f"DFFML {name} {self.package}"
            # Set target directory to package name if not given
            if not self.target:
                self.target = self.package
            # Extract
            skel_dir = pkg_resources.resource_filename(
                "dffml", os.path.join("skel", name)
            )
            # Recursive copy (shutil.copytree doesn't do the right thing if
            # target exists)
            distutils.dir_util.copy_tree(skel_dir, self.target)
            # Rename
            src = os.path.join(self.target, "REPLACE_IMPORT_PACKAGE_NAME")
            dest = os.path.join(self.target, self.package.replace("-", "_"))
            os.rename(src, dest)
            # Rename all variables in all files
            rename = {
                "REPLACE_ORG_NAME": self.user,
                "REPLACE_PACKAGE_NAME": self.package,
                "REPLACE_IMPORT_PACKAGE_NAME": self.package.replace("-", "_"),
                "REPLACE_DESCRIPTION": self.description,
                "REPLACE_AUTHOR_NAME": self.name,
                "REPLACE_AUTHOR_EMAIL": self.email,
                "REPLACE_DFFML_VERSION": VERSION,
            }
            for filename in glob.glob(
                os.path.join(self.target, "**"), recursive=True
            ):
                # Skip directories
                if not os.path.isfile(filename):
                    continue
                # Skip egg-info and __pycache__ if present
                if ".egg-info" in filename or "__pycache__" in filename:
                    continue
                # Open file and find replace all variables
                with open(filename, "r+") as handle:
                    contents = handle.read()
                    for find, replace in rename.items():
                        contents = contents.replace(find, replace)
                    handle.seek(0)
                    handle.truncate(0)
                    handle.write(contents)

    return CreateCMD


class Create(CMD):
    """
    Create new models, operations, etc. Copies samples out of dffml/skel/ and
    does re-naming.
    """

    model = create_from_skel("model")
    operations = create_from_skel("operations")
    service = create_from_skel("service")
