- Open Architecture RFC
  - data, compute, ML
    - firefly (ODAP), kcp (k8s API), dffml (open architecture)
    - `Input` objects stored in `ODAP` format
    - ODAP gateway cold storage save load via operation to be on/ramp offramp to ODAP as data highway (infrastructure, commodity)
- https://www.gartner.com/en/information-technology/glossary/open-architecture
  - > Open architecture is a technology infrastructure with specifications that are public as opposed to proprietary. This includes officially approved standards as well as privately designed architectures, the specifications of which are made public by their designers.
- What are we going to do? Immediate next steps community wise.
  - Propose that the format which can be used to describe any system architecture be called the Open Architecture (aka Universal Blueprint, DataFlow, System Context). The Open Architecture describes assets using the [Open Digital Asset Protocol](https://datatracker.ietf.org/doc/html/draft-hargreaves-odap-03). One option for definition of a system architecture via the Open Architecture is to link via directed graphs, component domain specific architectures, i.e. hardware, software, digital, physical, business process, or any combination thereof.
  - TODO look in more detail at SPARTA(?) work from facebook research.
- Below is an example of an open architecture encoded to a YAML document which is a manifest (per conformance to manifest interface outlined: https://github.com/intel/dffml/discussions/1369#discussioncomment-2603269).
  - In this example, we are hypothesizing that an open architecture document could at a minimum be a single domain specific representation. In this case, a dataflow.

```yaml
$schema: https://intel.github.io/dffml/open-architecture.0.0.1.schema.json
plugin: dataflow
config:
  ... a saved dataflow ...
```

---

- https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/
- https://www.hjp.at/doc/rfc/rfc7491.html#ref_ONF
  - Interesting network traffic architecture deployment / execution environment