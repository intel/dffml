# Rolling Alice: Architecting Alice: An Image

> Moved to: https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0007_an_image.md

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
$ curl -sfL "https://satori-syntax-highlighter.vercel.app/api/highlighter?code=let%20alice%20%3D%20new%20Alice()&background=%23E36FB7&lang=js&fontSize=16" | 
```

- Future
  - Streaming? Solved! Video streaming APIs :P
  - Generate an image of Alice with all her source code packaged
    - pip install of image
  - Eventually generate videos
  - Container registry service endpoint can build container images or manifest images / instances