- https://github.com/jart/blink/releases/tag/1.0.0
- Grabbing a single file from a given tag or commit from GitHub API

```bash
gh api --jq .content https://api.github.com/repos/intel/dffml/contents/scripts/gitpod.Dockerfile?ref=0.4.0 \
  | base64 -d \
  | docker build \
      -f - \
      -t dffml-gitpod:0.4.0 \
      --progress plain \
      /dev/null
```

```console
$ cat container_build.manifest.json | jq ".include[0]" | jq -r '"--context git://github.com/" + .owner + "/" + .repository + ".git#refs/heads/" + .branch + "#" + .commit + " --dockerfile " + .dockerfile + " --destination dffml.registry.digitalocean.com/dffml/" + .image_name'
```