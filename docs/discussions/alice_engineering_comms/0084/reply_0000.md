## 2022-11-12 @pdxjohnny Engineering Logs

- 🛼 security 🤔
  - Twitter conversation with Dan resulted only in roller coaster bogie (boh-gee) lock idea.
  - Roller skate security play on words?
    - Roll’r fast, roll’r tight, roll’r clean, secure rolling releases with Alice.
      - Content addressable with context aware caching
        - See recent 
      - Minimal attack surface
        - See unikernel in thread
      - No vulns or policy violations
        - Development future aligned with principles strategic principles
      - *Gif of Alice on roller skates throwing a bowling ball which is a software vuln, strike, she frontflips throwing knife style throws the pins into pull requests. We zoom out and see her just doing this over and over again around the Entity Analysis Trinity. Intent/LTM is where the throwing board is. Bowling alley is static analysis and the end of the bowling ally where she frontflips over (through hoop of CI/CD fire?) is where she pics up the pins and throws them as pull request (titles and numbers maybe, pulls/1401 style maybe?) knives into the board at the top which is the LTM and codebase. Then from top, LTM to static analysis where bowling alley starts shes in the lab, cooking up the vuln or maybe out looking for it. Or maybe refactoring after pull requests!*
- https://arstechnica.com/gadgets/2022/10/everything-we-know-about-the-white-houses-iot-security-labeling-effort/
- https://github.com/shirayu/whispering
  - couldn’t make it work

```console
$ sudo dnf install -y portaudio-devel
$ pip install -U git+https://github.com/shirayu/whispering.git@v0.6.4
$ whispering --language en --model medium
Using cache found in /home/pdxjohnny/.cache/torch/hub/snakers4_silero-vad_master
[2022-11-14 07:23:58,140] cli.transcribe_from_mic:56 INFO -> Ready to transcribe
Analyzing/home/pdxjohnny/.local/lib/python3.10/site-packages/torch/nn/modules/module.py:1130: UserWarning: operator() profile_node %668 : int[] = prim::profile_ivalue(%666)
 does not have profile information (Triggered internally at  ../torch/csrc/jit/codegen/cuda/graph_fuser.cpp:104.)
  return forward_call(*input, **kwargs)
```

```console
$ set -x; for file in $(ls If*.m4a); do python -uc 'import sys, whisper; print(whisper.load_model("medium.en").transcribe(sys.argv[-1])["text"])' "${file}" 2>&1 | tee "${file}.log"; done
```

- TODO
  - [ ] https://github.com/CycloneDX/bom-examples/tree/master/OBOM/Example-1-Decoupled
    - this as system context inputs for validity check
  - [ ] VDR
  - [ ] VEX
    - Payload (system context, see did as service endpoint architecting alice streams) goes in `detail`
    - https://github.com/CycloneDX/bom-examples/blob/83248cbf7cf0d915acf0d50b12bac75b50ad9081/VEX/Use-Cases/Case-1/vex.json#L47