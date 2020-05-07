# The following code ensures everything has a page under docs/api/
import sys
import inspect
import pathlib
import importlib
from typing import Optional, Callable


def modules(
    root: pathlib.Path,
    package_name: str,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
):
    for path in root.rglob("*.py"):
        # Figure out name
        import_name = pathlib.Path(str(path)[len(str(root)) :]).parts[1:]
        import_name = (
            package_name
            + "."
            + ".".join(
                list(import_name[:-1]) + [import_name[-1].replace(".py", "")]
            )
        )
        # Check if we should skip importing this file
        if skip and skip(import_name, path):
            continue
        # Import module
        yield import_name, path


package_name = "dffml"
root = pathlib.Path(__file__).parent.parent / package_name
skel = root / "skel"
# Skip any files in skel and __main__.py and __init__.py
skip = lambda _import_name, path: skel in path.parents or path.name.startswith(
    "__"
)


def gen_toctree(
    root: pathlib.Path,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
):
    names = []
    for path in root.glob("*.py"):
        # Figure out name
        import_name = pathlib.Path(str(path)[len(str(root)) :]).parts[1:]
        import_name = (
            package_name
            + "."
            + ".".join(
                list(import_name[:-1]) + [import_name[-1].replace(".py", "")]
            )
        )
        # Check if we should skip importing this file
        if skip and skip(import_name, path):
            continue
        names.append(path.stem)
    for path in root.rglob("__init__.py"):
        if path.parent.parent == root:
            names.append(path.parent.name + "/index")
    return (
        inspect.cleandoc(
            f"""
        .. toctree::
            :glob:
            :maxdepth: 2
            :caption: Contents:

        """
        )
        + "\n\n    "
        + "\n    ".join(names)
    )


for import_name, import_path in modules(root, package_name, skip=skip):
    import_name_no_package = import_name[len(package_name) + 1 :]
    path = (
        root.parent
        / "docs"
        / "api"
        / pathlib.Path(*import_name_no_package.split("."))
    ).with_suffix(".rst")
    index = path.parent / "index.rst"
    # Use parent.parts[1:] to remove docs/ from the path
    index_template = (
        root.parent
        / "scripts"
        / "docs"
        / "templates"
        / pathlib.Path(*path.parent.parts[1:])
        / "index.rst"
    )
    page_template = (
        root.parent
        / "scripts"
        / "docs"
        / "templates"
        / pathlib.Path(*path.parts[1:])
    )
    title = " ".join(import_name_no_package.split(".")).title()
    page = (
        inspect.cleandoc(
            f"""
            {title}
            {"=" * len(title)}

            .. automodule:: {import_name}
               :members:
           """
        ).lstrip()
        + "\n"
    )
    index_title = " ".join(import_name_no_package.split(".")[:-1]).title()
    index_content = (
        inspect.cleandoc(
            f"""
            {index_title}
            {"=" * len(index_title)}
            """
        ).lstrip()
        + "\n"
    )
    if index_template.is_file():
        index_content = index_template.read_text()
    index_content += gen_toctree(import_path.parent, skip=skip) + "\n"

    """
    print()
    print()
    print()
    print(index)
    print()
    print(index_content)
    print()
    print(path)
    print()
    print(page)
    print()
    print("-" * 40)
    """

    if page_template.is_file():
        page = page_template.read_text()

    if not index.parent.is_dir():
        index.parent.mkdir(parents=True)
    index.write_text(index_content)

    path.write_text(page)
