"""
Remove dataclasses library and remove it from the requirements list of torch.
pkg_resoruces will complain if we do not fixup torch's METADATA file to remove
dataclasses.
"""
import sys
import site
import pathlib
import itertools
import subprocess

subprocess.call(
    [sys.executable, "-m", "pip", "uninstall", "-y", "dataclasses"]
)

for sitedir in itertools.chain(
    site.getsitepackages(),
    filter(lambda i: pathlib.Path(i).is_dir(), sys.argv[1:]),
):
    print("sitedir", sitedir)
    for metadata_path in pathlib.Path(sitedir).rglob("**/torch-*/METADATA"):
        print("Patching", metadata_path)
        metadata = metadata_path.read_bytes()
        metadata = metadata.replace(b"Requires-Dist: dataclasses\n", b"")
        metadata_path.write_bytes(metadata)
        print("Patched ", metadata_path)
