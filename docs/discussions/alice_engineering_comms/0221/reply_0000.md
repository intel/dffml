## 2023-03-28 @pdxjohnny Engineering Logs

- https://github.com/google/data-transfer-project/releases/tag/v1.0.0
- https://github.com/google/data-transfer-project/blob/master/Documentation/RunningLocally.md#running-dtp-locally
- https://github.com/CycloneDX/specification/pull/194
- https://github.com/intel/dffml/issues/43
- https://protobuf.dev/getting-started/gotutorial/

```console
purism@hat-0 ~ $ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 40
purism@hat-0 ~ $ curl -sfLOC - https://go.dev/dl/go1.20.2.linux-arm64.tar.gz
purism@hat-0 ~ $ sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.20.2.linux-arm64.tar.gz
purism@hat-0 ~ $ python --version
Python 3.9.2
purism@hat-0 ~ $ go version
go version go1.20.2 linux/arm64
$ curl -fLCO - https://github.com/protocolbuffers/protobuf/releases/download/v22.2/protoc-22.2-linux-aarch_64.zip
$ unzip protoc-22.2-linux-aarch_64.zip
$ mv bin/protoc /usr/local/bin/protoc
$ go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
```

- Clone CycloneDX dataflow related pull request

```console
$ git clone https://github.com/CycloneDX/specification -b v1.5-dev-service-dataflows
$ protoc -I=schema -I=include --go_out=build_golang schema/bom-1.5.proto
protoc-gen-go: unable to determine Go import path for "bom-1.5.proto"

Please specify either:
        • a "go_package" option in the .proto source file, or
        • a "M" argument on the command line.

See https://protobuf.dev/reference/go/go-generated#package for more information.

--go_out: protoc-gen-go: Plugin failed with status code 1.
$ mkdir build_golang
$ ln -s ~/Downloads/include/ include
$ protoc -I=schema -I=include --go_out=build_golang schema/bom-1.5.proto
```

- https://github.com/CycloneDX/specification/issues/31#issuecomment-1289505136
  - There is mention of event driven architectures
  - https://github.com/CycloneDX/specification/pull/198
    - https://github.com/CycloneDX/specification/pull/198#discussion_r1148268346
      - Steve notes that PR 198 is part of issue 31

[![asciicast](https://asciinema.org/a/571584.svg)](https://asciinema.org/a/571584)