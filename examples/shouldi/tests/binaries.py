import pathlib
from dffml import cached_download_unpack_archive

downloads = pathlib.Path(__file__).parent / "downloads"

cached_node = cached_download_unpack_archive(
    "https://nodejs.org/dist/v14.2.0/node-v14.2.0-linux-x64.tar.xz",
    downloads / "node.tar.gz",
    downloads / "node-download",
    "fa2a9dfa4d0f99a0cc3ee6691518c026887677a0d565b12ebdcf9d78341db2066427c9970c41cbf72776a370bbb42729",
)

cached_target_javascript_algorithms = cached_download_unpack_archive(
    "https://github.com/trekhleb/javascript-algorithms/archive/ba2d8dc4a8e27659c1420fe52390cb7981df4a94.tar.gz",
    downloads / "javascript_algo.tar.gz",
    downloads / "javascript_algo-download",
    "36b3ce51780ee6ea8dcec266c9d09e3a00198868ba1b041569950b82cf45884da0c47ec354dd8514022169849dfe8b7c",
)
