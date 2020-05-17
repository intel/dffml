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

# Golang
cached_golang = cached_download_unpack_archive(
    "https://dl.google.com/go/go1.14.linux-amd64.tar.gz",
    downloads / "golang.tar.gz",
    downloads / "golang-download",
    "5dcc7b2e9049d80ceee9d3a7a4b76b578f42de64eaadabd039f080a9f329f2ad448da710626ed8fb4b070b4555b50e6f",
)
cached_golangci_lint = cached_download_unpack_archive(
    "https://github.com/golangci/golangci-lint/releases/download/v1.23.7/golangci-lint-1.23.7-linux-amd64.tar.gz",
    downloads / "golangci-lint.tar.gz",
    downloads / "golangci-lint-download",
    "088a65ae7aa45c8a5695f40cc90672d00dece7f08ce307567fddc8b2d03858cb5baf9d162193922d36c57c504cc52999",
)
cached_target_cri_resource_manager = cached_download_unpack_archive(
    "https://github.com/intel/cri-resource-manager/archive/c5e6091c79830cf7d076bbdec59c4a253b369d6a.tar.gz",
    downloads / "cri-resource-manager.tar.gz",
    downloads / "cri-resource-manager-download",
    "bdcbc8dadf9c6ee2f7571d10cb54459fe54773036982ad7485f007606efae96d7aaec7da18e2fea806fb6f68eb1722a8",
)

# Rust
cached_rust = cached_download_unpack_archive(
    "https://static.rust-lang.org/dist/rust-1.42.0-x86_64-unknown-linux-gnu.tar.gz",
    downloads / "rust.tar.gz",
    downloads / "rust-download",
    "ad2ab72dc407b0f5d34621640555e2da751da8803cbad734396faa54111e03093093f6fa66f14a1948bece8f9e33730d",
)
cached_cargo_audit = cached_download_unpack_archive(
    "https://github.com/RustSec/cargo-audit/archive/v0.11.2.tar.gz",
    downloads / "cargo_audit.tar.gz",
    downloads / "cargo-audit-download",
    "dea36731efaac4d0fd37a295c65520a7e9b23b5faa0a92dce7ab20764f8323fc34856079524c676e4cad1cb065ee6472",
)
cached_target_crates = cached_download_unpack_archive(
    "https://github.com/rust-lang/crates.io/archive/8c1a7e29073e175f0e69e0e537374269da244cee.tar.gz",
    downloads / "crates.tar.gz",
    downloads / "crates-download",
    "1bf0c3459373882f51132942872d0dbf8da01eee8d42c3c2090d234e4db99b39d4858c1fd2492c85917d670cae2519ca",
)
