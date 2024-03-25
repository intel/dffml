## 2024-03-15 @pdxjohnny Engineering Logs

- https://medium.com/@boredgeeksociety/finally-7b-parameter-model-beats-gpt-4-732cb0f3321d
- https://github.com/cc-api/confidential-cloud-native-primitives/blob/09211d24906bf9ec35bbc5e9b9a4dcf413f649ab/.github/workflows/image-rewriter.yaml#L26-L36
  - https://github.com/cc-api/confidential-cloud-native-primitives/blob/09211d24906bf9ec35bbc5e9b9a4dcf413f649ab/tools/cvm-image-rewriter/README.md
  - Finally someone scripted up the qemu-nbd stuff needed to customize and image with cloud init
- https://github.com/intel/Multi-llms-Chatbot-CloudNative-LangChain/blob/e5b61c07787e7d451cb1d6ce915ee92c4b2d97e5/2__LLMs_Proxy/server.py#L13-L34
  - Kubernetes native service discovery
    - `namespace = pathlib.Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read_text()`

![chaos-for-the-chaos-god](https://github.com/intel/dffml/assets/5950433/636969a1-1f0f-4c96-8812-f10fa403e79c)

- https://colab.research.google.com/drive/1z4rmOEiFkxkMiecAWeTUlPl0OmKgfEu7#scrollTo=4iBKg6Rmmpnw
  - SQL model
- https://sched.co/1aQWE
  - CloudEvents talk
- https://github.com/pdxjohnny/Multi-llms-Chatbot-CloudNative-LangChain/tree/scitt-validated-tool-use
- scitt-api-emulator `jsonld` branch + `policy_engine` branch gets us closer to federation.
  - PolicyEngineRequest can be made into a transparent receipt and ontologies for workflows via [`model_json_schema`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_json_schema)
  - https://docs.pydantic.dev/latest/examples/secrets/