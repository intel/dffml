import pathlib
from typing import List

from dffml import CMD, config, field

from .bom.make import mkbom
from .bom.db.base import DependencyDB
from .bom.db.yaml import YAMLDB


@config
class ProjectCreateCMDConfig:
    source: pathlib.Path = field(
        "Path to directory containing source code of project",
    )
    dbs: List[DependencyDB.load] = field(
        "Databases to search for info on dependencies",
        default_factory=lambda: [],
    )
    add: List[DependencyDB.load] = field(
        "YAML files containing info to supplement or override auto-detected info",
        default_factory=lambda: [],
    )
    authoritative: List[pathlib.Path] = field(
        "Database to use as authoritative source",
        default=YAMLDB(
            pathlib.Path(__file__).parent.parent.parent / "db.yaml"
        ),
    )


class ProjectCreateCMD(CMD):
    """
    Create a project from a source directory

    Example arguments to automatticly discover projects for tpm2-pytss project
    and add extra dependencies too it. Combining with lookups in custom
    database.

        -dbs mydb -add ./tpm2-pytss/.tools/shouldi/deps.yaml -- ./tpm2-pytss
    """

    CONFIG = ProjectCreateCMDConfig

    async def run(self):
        return mkbom(self.authoritative, self.dbs, self.source, add=self.add)


class ProjectCMD(CMD):
    """
    Dependency management, scanning, and reporting commands
    """

    create = ProjectCreateCMD
