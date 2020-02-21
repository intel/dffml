import pkg_resources
from pathlib import Path
import distutils.dir_util
from typing import NamedTuple

from .os import chdir

# The folder where DFFML is installed
INSTALL_LOCATION = Path(
    pkg_resources.resource_filename("dffml", "skel")
).parent


class SkelTemplateConfig(NamedTuple):
    """
    Variables used to find are replace strings starting with REPLACE_ in
    skel/ sub directories.
    """

    org: str
    package: str
    description: str
    name: str
    email: str
    dffml_version: str


class Skel:
    @property
    def skel(self):
        return Path(INSTALL_LOCATION, "skel")

    @property
    def common(self):
        return self.skel / Path("common")

    def common_files(self):
        """
        Files that are in common skeleton
        """
        return [path for path in self.common.rglob("*") if not path.is_dir()]

    def plugins(self):
        return [
            path
            for path in self.skel.glob("*")
            if "common" != path.name and path.is_dir()
        ]

    def create_symlinks(self, plugin):
        with chdir(plugin):
            for filepath in self.common_files():
                linkpath = filepath.relative_to(self.common)
                # Don't symlink if we already have
                if linkpath.is_symlink():
                    continue
                # Resolving first gives more helpful error message if it fails
                linkpath.resolve().symlink_to(filepath)

    def copy_template(self, plugin, target):
        # Recursive copy (shutil.copytree doesn't do the right thing if
        # target exists)
        distutils.dir_util.copy_tree(self.common, target)
        distutils.dir_util.copy_tree(plugin, target)

    def rename_template(self, target, config: SkelTemplateConfig):
        # Rename
        src = Path(target, "REPLACE_IMPORT_PACKAGE_NAME")
        dest = Path(target, config.package.replace("-", "_"))
        src.rename(dest)
        # Rename all variables in all files
        rename = {
            "REPLACE_ORG_NAME": config.org,
            "REPLACE_PACKAGE_NAME": config.package,
            "REPLACE_IMPORT_PACKAGE_NAME": config.package.replace("-", "_"),
            "REPLACE_DESCRIPTION": config.description,
            "REPLACE_AUTHOR_NAME": config.name,
            "REPLACE_AUTHOR_EMAIL": config.email,
            "REPLACE_DFFML_VERSION": config.dffml_version,
        }
        for path in dest.parent.rglob("*"):
            # Skip directories
            if path.is_dir():
                continue
            # Skip egg-info and __pycache__ if present
            if ".egg-info" in path.name or "__pycache__" in path.name:
                continue
            # Open file and find replace all variables
            contents = path.read_bytes()
            for find, replace in rename.items():
                contents = contents.replace(find.encode(), replace.encode())
            path.write_bytes(contents)

    def from_template(self, plugin_name, target, config):
        plugin = self.skel / Path(plugin_name)
        self.copy_template(plugin, target)
        self.rename_template(target, config)
