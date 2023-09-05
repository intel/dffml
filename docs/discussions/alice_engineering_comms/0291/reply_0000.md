- https://github.com/neonbjb/tortoise-tts
- https://github.com/salesforce/UniControl

```console
$ (echo -e 'HTTP 1.0\n200 OK\n' && dffml service dev export alice.cli:ALICE_COLLECTOR_DATAFLOW | dffml dataflow diagram -simple -configloader json /dev/stdin) | socat - TCP-LISTEN:8080,fork,reuseaddr
```