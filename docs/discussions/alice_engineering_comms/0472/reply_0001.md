## 2023-12-05 Ben/Demetri/John

![such-alignment](https://user-images.githubusercontent.com/5950433/226707682-cfa8dbff-0908-4a34-8540-de729c62512f.png)

- Bengo
- Demetri
  - https://solid.github.io/specification/protocol
- Equity, w3c credential community
  - envolope data model recording which descisions were made by whom, when
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79#issuecomment-1797016940
  - Events of new statements inserted
  - Events of new transparent statements to be offered by other instances
- Policy engines/instance as CI/CD jobs
- On/off chain smart contracts
  - Manual
  - Turing complete
- ActivityPub CWT authorization profile

```console
$ curl -sL -H 'Content-Type: application/json' https://socialweb.coop | jq
```

```json
{
  "type": "Organization",
  "outbox": {
    "type": "OrderedCollection"
  },
  "inbox": {
    "type": "OrderedCollection"
  }
}
```

- Ben
  - SCITT instances could directly ping Actors involved in payload contents, i.e. Alice created an OpenVEX statement about BobSoftware. Ping Bob's Actor or BobSoftware repo's Actor, our decentralized review system
- TODO
  - [ ] Add socialweb.coop Actor URI to startup of unstable instance
    - [ ] Auto feed Follow / Accept event on start