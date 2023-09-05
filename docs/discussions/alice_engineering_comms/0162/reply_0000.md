## 2023-01-29 @pdxjohnny Engineering Logs

- Alice helps us see risk over time and relationship to our security lifecycle posture
- For #1247 webhook PAT for runner adding could send activitypub message with new request for runner token to SECURITY_TXT actor (or similar), then can send runner token over webrtc data channel (this avoids risk of end-to-end encrypted data being cached and broken in the future
  - http://blog.printf.net/articles/2013/05/17/webrtc-without-a-signaling-server/
- https://socialhub.activitypub.rocks/t/clarify-relation-of-socialhub-versus-fep-repository/2909
- https://socialhub.activitypub.rocks/t/fep-c390-identity-proofs/2726
  - DID and VC alignment
    - > Identity proof is a JSON document that represents a verifiable bi-directional link between a [Decentralized Identifier 1](https://www.w3.org/TR/did-core/) and an ActivityPub actor.
    - https://socialhub.activitypub.rocks/t/fep-c390-identity-proofs/2726/8