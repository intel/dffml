"""
Remove dataclasses library and remove it from the requirements list of torch.
pkg_resoruces will complain if we do not fixup torch's METADATA file to remove
dataclasses.
"""
import sys
import site
import pathlib
import subprocess

subprocess.call(
    [sys.executable, "-m", "pip", "uninstall", "-y", "dataclasses"]
)

for sitedir in site.getsitepackages():
    for metadata_path in pathlib.Path(sitedir).rglob("**/torch-*/METADATA"):
        metadata = metadata_path.read_bytes()
        metadata = metadata.replace(b"Requires-Dist: dataclasses\n", b"")
        metadata_path.write_bytes(metadata)
