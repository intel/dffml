## 2024-04-11 @pdxjohnny Engineering Logs

- https://github.com/nus-apr/auto-code-rover
- https://github.com/langgenius/dify
- https://github.com/crazywoola/dify-extensions-worker
  - We can do an all node policy engine or see if we can call rust python from v8
- https://github.com/kubeedge/sedna/blob/main/docs/proposals/federated-learning.md#proposal
  - > We propose using Kubernetes Custom Resource Definitions (CRDs) to describe the federated learning specification/status and a controller to synchronize these updates between edge and cloud.
- https://github.com/enarx/enarx
- https://enarx.dev/docs/quickstart
  - https://enarx.dev/docs/Clouds

```bash
wget https://github.com/enarx/enarx/releases/download/v0.7.1/enarx-x86_64-unknown-linux-musl
sudo install -m 4755 -o root enarx-x86_64-unknown-linux-musl /usr/bin/enarx
wget https://github.com/enarx/enarx/releases/download/v0.7.1/enarx-x86_64-unknown-linux-musl.sig
sudo install -D -m 444 -o root -g root enarx-x86_64-unknown-linux-musl.sig /usr/lib/enarx/enarx.sig
wget https://enarx.dev/hello-world.wasm
enarx run hello-world.wasm
```

- https://enarx.dev/docs/WebAssembly/Python
- https://docs.wasmtime.dev/cli-install.html

```bash
$ cat > fib.py << 'EOF'
from functools import cache
import sys

@cache
def fib(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

args = sys.argv[1:]

if len(args) == 0:
    print("Please pass one or more numbers as arguments to the program")
else:
    for arg in args:
        idx = int(arg)
        print(f"Fibonacci sequence number at index {idx} is {fib(idx)}")
EOF
```

```bash
git clone https://github.com/singlestore-labs/python-wasi/ && \
cd python-wasi && \
docker build -f docker/Dockerfile -t wasi-build:latest docker

docker run -it -u $(id -u):$(id -g) --rm -v $(pwd):$(pwd):z -w $(pwd) wasi-build:latest bash -xec 'bash -xe ./run.sh && wasmtime run --mapdir=$(pwd)/opt::opt -- opt/wasi-python/bin/python3.wasm -c "$(cat $(pwd)/fib.py)"'
```