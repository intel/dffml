# DFFML ffmpeg Operations

ffmpeg description.

## Usage

Example usage

```console
export OPIMPS="calc_add calc_mult calc_parse_line associate"
dffml operations all \
  -sources nill=memory \
  -source-keys 'multiply 10 and 42' \
  -repo-def calc_string \
  -dff-memory-operation-network-ops $OPIMPS \
  -dff-memory-opimp-network-opimps $OPIMPS \
  -output-specs '["calc_string", "result"]=associate_spec' \
  -remap associate.result=result \
  -log debug
```

## License

DFFML ffmpeg is distributed under the [MIT License](LICENSE).
