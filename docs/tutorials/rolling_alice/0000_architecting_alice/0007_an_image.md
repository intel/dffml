# Volume 0: Chapter 7: An Image

We'll leverage JSON Web Keys and Python packages embedded into images
of source code as a reliable distrobution mechanism. Image data can be
transmitted over a multitude of existing channels.

![alice-image-manifest-svg-draft](https://satori-syntax-highlighter.vercel.app/api/highlighter?code=upstream%3A%20%22did%3Aweb%3Agithub.com%3Aintel%3Adffml%3Aentites%3Aalice%22&background=%23E36FB7&lang=yaml&fontSize=16)

- Context
  - We need a way to distribute software anywhere and everywhere.
- Goals
  - We want to be able to embed Alice in an image and install her
    from it.
- Actions
  - We are going build off of didme.me v2
- Future work
  - Videos and streams, Alice commited to a rolling release.
  - Provenance via SCITT
- References
  - This tutorial is covered in `TODO` **TODO** Update with link to recording once made.
  - The resulting commit from completion of this tutorial was: **TODO**
- Feedback
  - Please provide feedback / thoughts for extension / improvement about this tutorial in the following discussion thread: https://github.com/intel/dffml/discussions/1419

## Notes

- In relation to the manifest encoded as a "screenshot as universal API"
  - https://twitter.com/mattrickard/status/1577321709350268928
  - https://twitter.com/David3141593/status/1584462389977939968
    - > TIL python's pip will execute a setup .py directly from a ZIP archive from a web URL, with mime sniffing. This allows for a nice lolbin oneliner, with payload hosted on Twitter's CDN (or anywhere else really) `$ pip install "https://pbs"."twimg"."com/media/Ff0iwcvXEAAQDZ3.png"` (or $ pip install https://t"."co/uPXauf8eTg`)
      > ![image](https://user-images.githubusercontent.com/5950433/197549602-f1f98e38-5f34-4d04-b64c-94d49264d189.png)
      > ![source_code zip](https://user-images.githubusercontent.com/5950433/197549941-b915f643-4c29-4442-bf88-2a1ad604e877.png)
    - Sounds like we finally have ourselves a reliable distribution mechanism! :)
  - need parity with text as universal API
  - screenshots as operations
    - YAML for dataflow
    - encourages short functions :P
    - Everything effectively a manifest instance, operation plus metadata
    - https://satori-syntax-highlighter.vercel.app/
    - https://twitter.com/shuding_/status/1581358324569645056
    - https://satori-syntax-highlighter.vercel.app/api/highlighter?code=let%20alice%20%3D%20new%20Alice()&background=%23E36FB7&lang=js&fontSize=16
    - https://satori-syntax-highlighter.vercel.app/api/highlighter?code=upstream%3A%20%22did%3Aweb%3Agithub.com%3Aintel%3Adffml%3Aentites%3Aalice%22&background=%23E36FB7&lang=yaml&fontSize=16
    - https://pypi.org/project/svglib/
      - https://github.com/deeplook/svglib/blob/9472e067d88920debfbf6daefed32045025bf039/scripts/svg2pdf#L36-L45
      - https://github.com/deeplook/svglib/blob/9472e067d88920debfbf6daefed32045025bf039/svglib/svglib.py#L1402-L1414
      - https://github.com/deeplook/svglib/blob/9472e067d88920debfbf6daefed32045025bf039/svglib/svglib.py#L1438-L1447
  - It's just a screenshot of code
  - You just take a bunch of screenshots and put them together and that's your overlays
    - You can always trampoline and use one as a manifest or wrapper to resolution via a next phase storage medium.
  - didme.mev2
  - https://github.com/transmute-industries/did-jwk-pqc
- https://twitter.com/amasad/status/1584327997695283200/photo/1
- We'll proxy the registry off all these images

```console
$ python -m pip install svglib defusedxml
```

```console
$ curl -sfL "https://satori-syntax-highlighter.vercel.app/api/highlighter?code=let%20alice%20%3D%20new%20Alice()&background=%23E36FB7&lang=js&fontSize=16" \
  | python -c 'import svglib, reportlab.graphics, sys, etree; reportlab.graphics.renderPM.drawToFile(SvgRenderer().render(etree.XMLParser(remove_comments=True, recover=True, resolve_entities=False).parse(sys.stdin, parser=parser).getroot()), "alice.png", fmt="PNG")'
```

```console
$ curl -sfLo alice.svg "https://satori-syntax-highlighter.vercel.app/api/highlighter?code=upstream%3A%20%22did%3Aweb%3Agithub.com%3Aintel%3Adffml%3Aentites%3Aalice%22&background=%23E36FB7&lang=yaml&fontSize=16"
$ python -c 'import pyvips; pyvips.Image.new_from_file("alice.svg", dpi=300).write_to_file("alice.png")'

ModuleNotFoundError: No module named '_libvips'
OSError: cannot load library 'libvips.so.42': libvips.so.42: cannot open shared object file: No such file or directory.  Additionally, ctypes.util.find_library() did not manage to locate a library called 'libvips.so.42'
```

- Future
  - Streaming? Solved! Video streaming APIs :P
    - Play with lossy encoding and adherance to strategic principles stuff (`grep -i DNA`)  
  - Generate an image of Alice with all her source code packaged
    - pip install of image
  - Eventually generate videos
  - Container registry service endpoint can build container images or manifest images / instances
