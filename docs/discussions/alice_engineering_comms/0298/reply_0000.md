- https://github.com/bitnami/containers/blob/5cb1cc56d8b4088aa9882fe3a938c1b9712bad03/bitnami/kubectl/1.27/debian-11/Dockerfile#L20

```console
$ curl -Ls "https://sbom.k8s.io/$(curl -Ls https://dl.k8s.io/release/stable.txt)/release" | grep "SPDXID: SPDXRef-Package-registry.k8s.io" |  grep -v sha256 | cut -d- -f3- | sed 's/-/\//' | sed 's/-v1/:v1/' | grep amd64
registry.k8s.io/kube-controller-manager-amd64:v1.27.3
registry.k8s.io/kube-scheduler-amd64:v1.27.3
registry.k8s.io/conformance-amd64:v1.27.3
registry.k8s.io/kube-proxy-amd64:v1.27.3
registry.k8s.io/kube-apiserver-amd64:v1.27.3
$ curl -Ls "https://sbom.k8s.io/$(curl -Ls https://dl.k8s.io/release/stable.txt)/release" | grep -n -C 5 kubectl
$ docker run --rm -ti --entrypoint kubectl registry.k8s.io/conformance-amd64:v1.27.3 --help
```