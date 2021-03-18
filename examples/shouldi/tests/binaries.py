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
    "https://static.rust-lang.org/dist/rust-1.50.0-x86_64-unknown-linux-gnu.tar.gz",
    downloads / "rust.tar.gz",
    downloads / "rust-download",
    "f6eb40e09d7fa6f38f7374f6736a773b01ac191e5d421d583b7e7dd4d07c44fc6b8a7a2637af780cfab08b91715f8147",
)
cached_cargo_audit = cached_download_unpack_archive(
    "https://github.com/RustSec/cargo-audit/archive/v0.14.0.tar.gz",
    downloads / "cargo_audit.tar.gz",
    downloads / "cargo-audit-download",
    "871b353a43c1c90892c85534c688a4a74c8b488ae2f7851e6e0753810f4423a4176d24eb707dd8e4ba31afd7785f1205",
)
cached_target_rust_clippy = cached_download_unpack_archive(
    "https://github.com/rust-lang/rust-clippy/archive/52c25e9136f533c350fa1916b5bf5103f69c0f4d.tar.gz",
    downloads / "rust-clippy.tar.gz",
    downloads / "rust-clippy-download",
    "25d4eb2845136f1338ebc13443867ffce74830f034f581aa0cc87f160a9d44269c9d849674a5ca0fa637632e9575d951",
)
