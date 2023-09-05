## 2022-12-06 @pdxjohnny Engineering Logs

Closing duplicates

```console
$ gh issue list --search "Recommended Community Standard:" --json title,number,url -R intel/dffml | tee test.json
$ python -c 'import sys, json; manifest = json.loads(sys.stdin.read()); superset = set([i["number"] for i in manifest]); duplicates = list(set({i["title"]: i["number"] for i in manifest}.values()).symmetric_difference(superset)); print("\n".join([i["url"] for i in manifest if i["number"] in duplicates]))' < test.json
```

- TOOD
  - [ ] Just script everything and have the AI refactor, genericize, and package learning from the asciinema sessions
    - grep markov, terminal dev
  - [ ] `alice please log todos` Fix duplicate issue issue
  - [ ] `alice please log todos` overlays with basic templated body content
    - [ ] Required input of feedback/false positive DID/URL/location


![image](https://user-images.githubusercontent.com/5950433/205970630-d9c069dc-531e-4980-9b97-5e39d18d6e4f.png)


![provenance_for_the_chaos_God](https://user-images.githubusercontent.com/5950433/205970518-be789441-d9a2-4ef9-84cb-c54d5438689e.jpg)
