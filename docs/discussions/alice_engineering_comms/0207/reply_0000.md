Hello!

- [yuzutech/kroki](https://github.com/yuzutech/kroki)
  - Sometimes I just post miscellaneous possibly helpful links / stared repos within my daily engineering logs. This one might be helpful for rendering graphics that can't be rendered natively if they need to be communicated somewhere. For example, mermaid just introduced mind map functionality which could be useful for our use case. However, that functionality is not present within the version of mermaidjs that GitHub uses in their markdown rendering ruby gem. If we wanted to help Alice render mind maps, we'd have to deploy a rendering service such as kroki, convert to a format like SVG or PNG, and then use that within the markdown body.
- https://simonwillison.net/2023/Mar/13/alpaca/
  - This link was posted related to "depth of field mapping" (there is probably a better term for this, similar to [our risk mapping](https://github.com/intel/dffml/blob/11fea2bb0dd0aec3c19533e61d15d894c8112d25/docs/tutorials/rolling_alice/0001_coach_alice/0007_cartographer_extraordinaire.md)), meaning the act of mapping out the research in the aligned space. Since DFFML is all about wrapping existing models and ensuring [plumbing](https://www.techopedia.com/definition/31509/plumbing) is in place to use existing models easily, we're always posting links here for machine learning models that might be helpful. We also try to post the path we took to find those links, as we'll want to ensure we can automate this process so that Alice can also find the most recent research, to use as a base from which she'll hypothesize novel approaches. Whenever we get to that part of the project, we'll probably end up doing something like what's been done with the folks who have hooked up GPT-3 to search engines. We'll use our previous experiences as logged in this thread to understand how to fine tune the prioritizer as Alice surfs the web by making urlrequests. We'll work to ensure she looks for aligned research in as helpful a way as possible, prioritizing feeding the active execution loop with links that when added to the corpus of data are producing hypothesizes which have high alignment scores to whatever that active execution loop's strategic plans and principles are.
  - There are a variety of things that make a link "of interest" within the aligned problem space
    - Novel research, results, or approach to a problem
    - Strong community support
      - Strong publishing org support (aka they will support it going forward or build something new which we could migrate to if we decided to start using the N-1 version)
    - Permissive licensing
      - BSD, MIT, Apache-2.0, public domain, etc.
    - Optimization
      - Running on low cost hardware (aka not requiring large clusters or resources only companies or large institutions have access to)
  - Alpaca is of interest because of
    - Permissive licensing
      - Apache-2.0
    - Optimization
      - https://simonwillison.net/2023/Mar/11/llama/
        - > Large language models are having their Stable Diffusion moment
          >
          > The open release of the Stable Diffusion image generation model back in August 2022 was a key moment. I wrote how [Stable Diffusion is a really big deal](https://simonwillison.net/2022/Aug/29/stable-diffusion/) at the time.
          >
          > People could now generate images from text on their own hardware!
          >
          > More importantly, developers could mess around with the guts of what was going on.

Thank you,
John