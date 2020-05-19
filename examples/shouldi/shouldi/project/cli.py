import pathlib

from dffml import CMD, Arg

from .bom.make import mkbom
from .bom.db.base import DependencyDB
from .bom.db.yaml import YAMLDB


class ProjectCreateCMD(CMD):
    """
    Create a project from a source directory

    Example arguments to automatticly discover projects for tpm2-pytss project
    and add extra dependencies too it. Combining with lookups in custom
    database.

        --dbs mydb --add ./tpm2-pytss/.tools/shouldi/deps.yaml -- ./tpm2-pytss
    """

    arg_source = Arg(
        "source",
        type=pathlib.Path,
        help="Path to directory containing source code of project",
    )
    arg_dbs = Arg(
        "--dbs",
        nargs="+",
        default=[],
        type=DependencyDB.load,
        help="Databases to search for info on dependencies",
    )
    arg_add = Arg(
        "--add",
        nargs="+",
        default=[],
        type=DependencyDB.load,
        help="YAML files containing info to supplement or override auto-detected info",
    )
    arg_authoritative = Arg(
        "--authoritative",
        nargs="+",
        type=pathlib.Path,
        help="Database to use as authoritative source",
        default=YAMLDB(
            pathlib.Path(__file__).parent.parent.parent / "db.yaml"
        ),
    )

    async def run(self):
        return mkbom(self.authoritative, self.dbs, self.source, add=self.add)


class ProjectCMD(CMD):
    """
    Dependency management, scanning, and reporting commands
    """

    create = ProjectCreateCMD
