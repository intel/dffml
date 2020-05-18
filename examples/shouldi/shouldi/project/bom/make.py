import uuid
import pathlib
import dataclasses
from typing import List, Optional

from .python import python_bom

from .base import BOM
from .db.base import DependencyDB


def mkbom(
    authoritative: DependencyDB,
    dbs: List[DependencyDB],
    root: pathlib.Path,
    *,
    add: Optional[List[pathlib.Path]] = None,
):
    for discover in [python_bom]:
        bom = discover(root)
        if bom is not None:
            break
    if bom is None:
        bom = BOM(dependencies=[])
    # Load extra data about a dependencies
    for db in dbs:
        for dependency in bom.dependencies:
            extra = db.extra(dependency)
            if extra is not None:
                dependency.extra[db.name] = extra
    # Ensure we have authoritative information on dependencies
    for i, dependency in enumerate(bom.dependencies):
        # Check if any extra dependency info knows of the authoritative UUID
        authoritative_uuids = list(
            filter(
                bool, map(lambda extra: extra.uuid, dependency.extra.values())
            )
        )
        # If there are any DependencyExtra objects in extra, use the first
        # one's UUID as the name for the new authoritative UUID. Otherwise
        # use a random UUID
        name = uuid.uuid4()
        for extra in dependency.extra.values():
            if extra.uuid:
                name = extra.uuid
                break
        # Set the UUID to the correct value (possibly creating a new one)
        bom.dependencies[i] = dependency = dataclasses.replace(
            dependency, uuid=uuid.uuid5(authoritative.uuid, str(name))
        )
        # If we don't have an authoritative UUID for this dependency, save
        if not authoritative_uuids:
            authoritative.save(dependency)
        # Update any DependencyExtra objects that didn't know about the
        # authoritative so they know about it's new UUID
        for db in dbs:
            if (
                db.name not in dependency.extra
                or dependency.extra[db.name].uuid != dependency.uuid
            ):
                db.save(dependency)
    if add is not None:
        for adddb in add:
            for name, dependency in adddb.dependencies.items():
                dependency = authoritative.lookup(dependency)
                for db in dbs:
                    # Load extra data about a dependency
                    extra = db.extra(dependency)
                    if extra is not None:
                        dependency.extra[db.name] = extra
                # Add to dependency list
                bom.dependencies.append(dependency)
    return bom
