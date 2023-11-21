## 2023-11-16 @pdxjohnny Engineering Logs

- https://grotto-networking.com/blog/posts/DID_Key.html#did%3Akey
  - Unmaintained
    - https://pypi.org/project/py-multibase/
    - https://pypi.org/project/py-multicodec/
  - Mentions a bug with leading 0 decode, but then it looks like the keys in [w3c-ccg/did-method-key.git/test-vectors/nist-curves.json](https://raw.githubusercontent.com/w3c-ccg/did-method-key/main/test-vectors/nist-curves.json) rely on that for proper decode?
    - [2023-11-16-did-key-multicodec-header-issues.ndjson.xz.txt](https://github.com/intel/dffml/files/13385986/2023-11-16-did-key-multicodec-header-issues.ndjson.xz.txt)
      - `python -m asciinema play -s 15 <(cat 2023-11-16-did-key-multicodec-header-issues.ndjson.xz.txt | xz -d -)`

```console
$ python -c 'print(int(0x1201))'
4609
$ python -c 'import sys, base58, multibase, multicodec; multicodec_value = base58.b58decode(sys.argv[-1]); multicodec.get_codec(multicodec_value); raw_public_key_bytes = multicodecremove_prefix(multicodec_value);' z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54
Traceback (most recent call last):
  File "/home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/multicodec/multicodec.py", line 73, in get_codec
    return CODE_TABLE[prefix]
           ~~~~~~~~~~^^^^^^^^
KeyError: 109902829

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/multicodec/multicodec.py", line 75, in get_codec
    raise ValueError('Prefix {} not present in the lookup table'.format(prefix))
ValueError: Prefix 109902829 not present in the lookup table
$ python -c 'import sys, base58, multibase, multicodec; multicodec_value = multibase.decode(sys.argv[-1]); multicodec.get_codec(multicodec_value); raw_public_key_bytes = multicodecremove_prefix(multicodec_value);' z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54
Traceback (most recent call last):
  File "/home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/multicodec/multicodec.py", line 73, in get_codec
    return CODE_TABLE[prefix]
           ~~~~~~~~~~^^^^^^^^
KeyError: 4609

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/multicodec/multicodec.py", line 75, in get_codec
    raise ValueError('Prefix {} not present in the lookup table'.format(prefix))
ValueError: Prefix 4609 not present in the lookup table
```

- TODO
  - [x] https://github.com/scitt-community/scitt-api-emulator/pull/39
    - [ ] PR approvals
      - [x] Orie