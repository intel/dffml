## 2023-02-18 @pdxjohnny Engineering Logs

- https://github.com/TBD54566975/dwn-aggregator/blob/4269041795f004fe819a4f1d9cdd3a13d979be0d/examples/pubsub.js
  - We may bail on ActivityPub for now and jump right into DIDs now that this has push/pull websocket support. TBD (LOL).
- https://www.npmjs.com/package/@tbd54566975/dwn-sdk-js
- TODO
  - [ ] Hybridize SCITT DWN
    - [ ] Auto PR repos with security.txt contact of url which gets translated into did web of a way for them to deploy DWN SCITT so as to secure their releases. Bootstrap decentralized N SCITT instances. Bootstraps our outofband comms for post release or vcs push ActivityPub security txt style
      - Start with model transformers
      - Can do separate endor style repo for basic SCITT, then just need to deploy DWNs somewhere for notifications, could leverage POC relays from their aggregator README to start