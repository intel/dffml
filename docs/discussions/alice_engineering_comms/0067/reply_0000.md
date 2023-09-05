## 2022-10-26 @sedihglow Engineering Logs

- https://github.com/sedihglow/red_black_tree
- https://gist.github.com/sedihglow/770ed4e472935c5ab302d069b64280a8
  - How Python's builtin `sorted()` works
  - https://docs.python.org/3/library/functions.html#sorted
- References
  - http://www.microhowto.info/howto/convert_from_html_to_formatted_plain_text.html
    - `$ lynx -dump -display_charset UTF-8 "https://docs.docker.com/engine/install/ubuntu/"`
  - https://unix.stackexchange.com/questions/336253/how-to-find-gnome-terminal-currently-used-profile-with-cmd-line
    - `--save-config` has been removed
- Docker
  - https://github.com/pdxjohnny/dockerfiles/blob/406f0b94838f7dcd1792c394061a2ee18c4f7487/sshd/Dockerfile
- https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst#cloning-the-repo
- Vim
  - Exit insert mode `Ctrl-[`

```console
$ git clone -b alice https://github.com/intel/dffml
$ cd dffml/entities/alice
$ python -m pip install \
    -e .[dev] \
    -e ../../ \
    -e ../../examples/shouldi/ \
    -e ../../feature/git/ \
    -e ../../operations/innersource/ \
    -e ../../configloader/yaml/
```