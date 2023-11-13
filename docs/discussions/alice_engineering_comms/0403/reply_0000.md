## 2023-09-27 @pdxjohnny Engineering Logs

- We need to build the dependency graph, KCP is our API layer for Alice. Federated events from SCITT will be transformed into `kubectl apply` YAMLs. GUAC query + evented graph exec + SCITT acts as a firewall for an instance of Alice. KCP, GUAC, forgego all compile to WASM, with the dependency graph of the projects a dev (Alice, Bob, a human, etc.) is working on we can make decisions on what we want to federate to their environment. We want to be able to run a forge in browser. WASM + WebML would make for sweet [EAT](https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#entity-analysis-trinity).
  - > [What’s in a controller?](https://book.kubebuilder.io/cronjob-tutorial/controller-overview#whats-in-a-controller)
    > Controllers are the core of Kubernetes, and of any operator.
    >
    > It’s a controller’s job to ensure that, for any given object, the actual state of the world (both the cluster state, and potentially external state like running containers for Kubelet or loadbalancers for a cloud provider) matches the desired state in the object. Each controller focuses on one root Kind, but may interact with other Kinds.
    >
    > We call this process reconciling.
    >
    > In controller-runtime, the logic that implements the reconciling for a specific kind is called a [Reconciler](https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/reconcile?tab=doc). A reconciler takes the name of an object, and returns whether or not we need to try again (e.g. in case of errors or periodic controllers, like the HorizontalPodAutoscaler).
- https://github.com/kcp-dev/kcp
- https://docs.kcp.io/kcp/v0.11/developers/using-kcp-as-a-library/
- https://docs.kcp.io/kcp/v0.11/developers/writing-kcp-aware-controllers/
- https://docs.kcp.io/kcp/v0.11/CONTRIBUTING/#getting-started
- https://book.kubebuilder.io/quick-start.html
  - Started here
  - https://book.kubebuilder.io/plugins/creating-plugins.html
  - https://book.kubebuilder.io/cronjob-tutorial/controller-overview

```console
$ go version
go version go1.21.0 linux/amd64
```

```bash
git clone -b v0.20.0 https://github.com/kcp-dev/kcp
cd kcp
go run ./cmd/kcp start
export KUBECONFIG=.kcp/admin.kubeconfig
kubectl api-resources
```

```bash
curl -L -o kubebuilder "https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)"
chmod +x kubebuilder && mv kubebuilder "${HOME}/.local/bin/"
mkdir -p ~/projects/guestbook
cd ~/projects/guestbook
kubebuilder init --domain my.domain --repo my.domain/guestbook
kubebuilder create api --group webapp --version v1 --kind Guestbook --resource --controller
make manifests
docker run -e INPUT_GITHUB-TOKEN=$(gh auth token) -e "INPUT_SCRIPT=$(echo console.log('Test'))" -e INPUT_DEBUG=true -e NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt --rm -ti node:latest -ec 'curl -sfL https://github.com/actions/github-script/archive/refs/tags/v6.4.1.tar.gz | tar -xz && node github-script*/$(cat github-script*/action.yml | python -c "import sys, pathlib, json, yaml; print(json.dumps(yaml.safe_load(sys.stdin)))" | jq -r ".runs.main")'
```

- https://github.com/cncf/sandbox/issues/47#issuecomment-1726431147
  - YES! KCP approved for CNCF sandbox ~1 week ago
  - > Welcome aboard! We're very excited to get you onboarded as a CNCF sandbox project! Here's the link to your onboarding checklist: cncf/toc#1173

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)