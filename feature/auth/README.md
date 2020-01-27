# DFFML auth Features

auth description.

## Usage

Example usage

```console
$ dffml operations repo \
  -sources memory=nill \
  -log debug \
  -keys feedface \
  -repo-def UnhashedPassword \
  -ops scrypt get_single \
  -opimpn-memory-opimps scrypt get_single \
  -remap get_single.ScryptPassword=scrypt \
  -output-specs '["ScryptPassword"]=get_single_spec'
[
    {
        "extra": {},
        "features": {
            "scrypt": {
                "hashed":
"322e95513218f1b70c34cc8af4eafdc18c44946c51b5b7cfd4c0258047d38942dd153822ad118fe908cfa15a1b315402772ea33608bcaf20f6a5e32dc4891a50",
                "salt":
"e78f23e1a05165211d50652e7a07e769ade1192c126d049b022a10d5b8ff1a3ff474666824915c9e318b2f06a37d52ff1dfcc8e9f56873d0b083ee2d43f7b9c7"
            }
        },
        "last_updated": "2019-05-10T15:58:19Z",
        "key": "feedface"
    }
]
```

## License

DFFML DFFML auth are distributed under the
[MIT License](LICENSE).
