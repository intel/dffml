## 2022-11-07 @pdxjohnny Engineering Logs

- KCP Edge
  - https://github.com/kcp-dev/edge-mc
  - Goal: bridge with DID / DWN / serviceEndpoint / DIDComm / Data Flows for arbitrary comms.
  - > edge-mc is a subproject of kcp focusing on concerns arising from edge multicluster use cases:
    > - Hierarchy, infrastructure & platform, roles & responsibilities, integration architecture, security issues
    > - Runtime in[ter]dependence: An edge location may need to operate independently of the center and other edge locations​
    > - Non-namespaced objects: need general support
    > - Cardinality of destinations: A source object may propagate to many thousands of destinations. ​ 
  - Released 3-4 days ago? Chaos smiles on us again :)
  - Perfect for EDEN (vol 0: traveler of the edge)
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_preface.md#volume-0-architecting-alice
  - We want to bridge KCP edge-mc with 
- https://sohl-dickstein.github.io/2022/11/06/strong-Goodhart.html
- System Context
  - Stumbled upon "valid system context" stuff (I/O must existing / be mapped)
    - https://youtu.be/m0TO9IOqRfQ?t=3812&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
    - https://github.com/intel/dffml/blob/1d4d6b2f817cd987ceff94b4984ce909b7aa3c7f/dffml/df/system_context/system_context.py#L101-L103
- https://atproto.com/guides/data-repos
  - We will serialize to ATP when available / more Python
   support / obvious what is happening there.
- RosettaNet
  - https://github.com/MicrosoftDocs/biztalk-docs/tree/main/biztalk/adapters-and-accelerators/accelerator-rosettanet
  - https://github.com/MicrosoftDocs/biztalk-docs/blob/main/biztalk/adapters-and-accelerators/accelerator-rosettanet/TOC.md
  - https://github.com/Azure/logicapps/blob/master/templates/rosettanet-encode-response.json
    - This looks like it would be good for CI/CD test status in DID land
    - As a bridge to tbDEX
- Hitachi if truly powering good is aligned
- https://github.com/SchemaStore/schemastore
- GitHub Actions
  - https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#discussion_comment
  - https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
  - https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#available-events
- Flan T5
  - https://colab.research.google.com/drive/1Hl0xxODGWNJgcbvSDsD5MN4B2nz3-n7I?usp=sharing#scrollTo=GDlskFoGYDVt
  - Paid $9.99 to have access to high memory environment (12GB was not enough for the first import code block)
  - It won't generate long form answers :(
    - [2022-11-06 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4068656)
    - Summary of the following (Alice thread) in the style of a avxrh or whatever paper
    - Commit messages from patch diffs

```python
input_text = """
Write a peer reviewed scientific paper on the Eiffel Tower:
"""

def generate_long(input_text):
  input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
  output = model.generate(input_ids, max_new_tokens=100000000)
  return [tokenizer.decode(i, skip_special_tokens=True) for i in output]

generate_long(input_text)
```

- TODO
  - [ ] Enable detection of recommended community standards in `docs` and `.github`
    - https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-support-resources-to-your-project
  - [x] Headphones
    - [x] Craigslist $50: Bose QuietComfort 15
      - I've been wanting these headphones for, what, 12+ years,
        turns out I could have just gone on craigslist at any point.
    - [x] [STRFKR - Open Your Eyes](https://www.youtube.com/watch?v=mkeOoWquAqk&list=RDEMwZ9tKHt9iT5CWajVqMu11w)
    - [x] CHADIG
  - [ ] JavaScript GitHub Actions runner idea still good for use case of automating communications via client side execution of runner / flows.
    - [ ] Implemented via extension or script or console copy/paste or background service worker or something. This allows you to do the incremental addition to the Extensible Dynamic Edge Network (EDEN).
      - Just remembered I found out about solar punk semi-recently
      - didme.me
      - DWN looks similar to this? REally unclear where impelmentation is at or what hooks are