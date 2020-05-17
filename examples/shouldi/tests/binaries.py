import pathlib
from dffml import cached_download_unpack_archive

downloads = pathlib.Path(__file__).parent / "downloads"

# JavaScript
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

# Java
cached_openjdk = cached_download_unpack_archive(
    "https://download.java.net/openjdk/jdk14/ri/openjdk-14+36_linux-x64_bin.tar.gz",
    downloads / "java.tar.gz",
    downloads / "java-download",
    "d87ab7b623e17c85d763fd9bf810fc6de7d7c001facf238266bb316586081732cfd4b08d9fbaa83655cbdf9a4f497ac9",
)
cached_dependency_check = cached_download_unpack_archive(
    "https://dl.bintray.com/jeremy-long/owasp/dependency-check-5.3.2-release.zip",
    downloads / "dependency_check.zip",
    downloads / "dependency_check-download",
    "02652657e658193369ccd38c000dfbdcbafdcbe991467a8d4f4ef6845ec7af1eae6e2739df6ec851b2d5684fede77c5b",
)
cached_target_rxjava = cached_download_unpack_archive(
    "https://github.com/ReactiveX/RxJava/archive/v2.2.16.tar.gz",
    downloads / "RxJava.tar.gz",
    downloads / "RxJava-download",
    "2a15b4eb165e36a3de35e0d53f90b99bb328e3c18b7ef4f0a6c253d3898e794dec231fc726e154f339151eb8cf5ee5bb",
)
