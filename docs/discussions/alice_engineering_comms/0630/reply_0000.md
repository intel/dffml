## 2024-05-20 @pdxjohnny Engineering Logs

- LLM schema based communication
  - JSON
    - `@lice`: All of your responses MUST return only a JSON object. Your response will cause catastrophic failure if you fail to return anything other than valid JSON. It is extremely important you follow the aforementioned protocol from now on. The JSON object you return MUST always have only four top level key value pairs. The objects within the three top level values will be arbitrary objects which are generic and descriptive and appropriate to the context, thread data, and any function calls. The keys and details on what their values should be are as follows.
      - `@context`: contains JSON schema to codegen or dynamically define classes and interfaces (types python module, protobufs as well?. `@context` also contains recommended format object as an array of objects at the top level in order of preference, values are similar to these examples: types and dataclasses python modules, pydantic, protobufs, ORM generators. 
      - `payload`: The relevant data which the LLM is being asked to generate
  - COSE - CBOR (base64 encoded)
    - dito but use CDL markdown or mermaid and LLM generated schema for definition of pycose calls and their arguments which are serializeable to JSON.
      - Have the LLM generate the code we need to add to the [manifest `shim.py`](https://github.com/intel/dffml/blob/474478442ad7293d84c387be094b70881ec2165b/dffml/util/testing/manifest/shim.py). This code will parse the top level object and use the JSON schema to codegen or dynamically define classes and interfaces (types python module, protobufs as well? Should we put a recommended format section as an array of objects at the top level.
        - `@lice`: PPlease think step by step and write me a program which captures all audio on fedora linux and streams it via standard web elements using an HTTP server which streams it's machines audio and serves an HTML page using only standard elements and no javascript at the root of the site. Write all these steps as a bash script which uses the tee command to write the various files. Please incudle the execution of a python script which uses subprocess to execute ffmpeg and avoid the use of `subprocess.PIPE`, instead, pass `self.wfile` as the fileobj to Popen's stdin kwarg on request to the root path. Please ensure that ffmpeg is terminated in the event of any errors.
          - Generic: Given a repo, clone it and attach files to Alice with retrieval enabled. Optionally create a fork of the repo. Create a new branch which is under 200 characters and describes the user provided modification request (json schema for this stuff). 
    - https://github.com/intel/dffml/commit/5da7864deac143c900ddcf2d02ab524894b60b23
    - https://github.com/intel/dffml/pull/1454
    - https://github.com/intel/dffml/pull/1450
    - https://github.com/intel/dffml/pull/1273
    - https://github.com/intel/dffml/pull/1207
    - https://github.com/intel/dffml/pull/1061
- TODO
  - [ ] Ask [`@lice`](https://github.com/lice) if they are still using that account as we could trigger actions on mention if we had that handle.