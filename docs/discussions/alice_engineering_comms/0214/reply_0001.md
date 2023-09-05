## 2023-03-21 WECAN

> Lost track of who said what, see recording for who said what.

- https://us02web.zoom.us/postattendee?mn=DAWtOh4M0fbHBk3YDwrk_QYNhNn_DH7iYCTt.b-AoRt7JwG7EPfOq
- https://github.com/ucan-wg/spec/pull/132
- Need to agree on a hash alg (sha256 seems reasonable)
  - Some people think it's safer that sha3
  - How do we want to encode that?
  - Do we need the CID header?
  - Do we want to have a methodology that requires reencoding?
     - Other WGs seem to avoid recoding
  - If you're in the browser then base32 is good, if you're low in the stack binary encoding is good
  - Should we just go: This hash algo, this base, call it good?
  - Alan: Just had field, unique ID, up to you to decide what that is
    - Minimizes numebr of things we have to agree one (sounds like the VC thing we just talked about)
  - Currently everything is contenta ddressed, instead of guid we use hash of token itself
    - You only end up with a colisiosn if you have th same token, which is signed
    - We just want to figure out how to most qucikly decode that
  - bengo: multihashes, multibases are relavent here in minimzign the base of the CID
  - Irakli
    - Coudl say, we expect base64 but if you see base32 it's not a big deal obviously
    - IPLD version could be in DAG-JSON or DAG-CBOR
      - Base encoding you can't reencode on the fly to see which ones are revoked
      - Revokation is always a big problem, this is why KERI's duplicity checking is nice
  - CID already has content type information in it
- Irakli: https://github.com/ipld/js-dag-ucan
  - UCAN invokation spec asn capabilitesi and params
  - Proofs and signature
  - CID of thing would be static regardless of representation, then that coul dbe used as a key, outter layer would be distinct, would be issuers decissions if revokation of you can do this (outer layer)

> ```typescript
> const ucan = UCAN.parse(jwt)
> ucan.issuer.did() // did:key:z6Mkk89bC3JrVqKie71YEcc5M1SMVxuCgNx6zLZ8SYJsxALi
> ```

- In order to check for revokation you have to pull down the inner layer
  - Take the UCAN, gernate JWT payload, get each hash, check if each has been revoked
  - Could take UCAN encoded as JWT, encode as DAG-JSON, but that would end up requiring revokation to transcode into all the different forms that might need to be checked to be revoked
- Core UCAN spec is JWT, lots of this work keeps leaning towards IPLD
- Easy to plug in UCAN within wherever if it's just JWT
  - You could make it YAML!
    - But we have standards because we want interop
      - Extra structures and wrappers drifts away from interop
- The moment you support alternate ecodings, then you have to just start adding more encodings to your system
  - The metadata is captured within the CID, so each system just needs to keep supporting more encoding
  - Irakli points out again that this opens us up to more revokation based attacks, because you have to rencode into 
  - Invoation of the payload
- Is bluesky using UCANs?
  - It's in the plan
- Idividual CID for the exact invoaktion isn't usually what you want to do, you just want to revoke based on the public key (PKI) associted with those verifiable credentials
- Alan with a great point: When you delegate you should deligate to one off keys
  - Military wants this
    - Privacy conerns mitigated
  - Issuers responsibility to map key sisued to to whatever credential
  - Sometimes we have to deal with whatever key is already there
    - However, then the revokation can't just say revoke everything tied to one key
    - Do we need revokation by key?
      - It's that you're precluding the prefered practice
    - Revoking by audiance key pair only revokes that one UCAN
- Key by public key or VC and not by the UCAN
  - You can always find all the related if you've been indexing, you have to maintain that index if you care about revokation
- It might be useful to standaredize the revokation multihash, sign one CID to revoke it
- Only the request comes into the service provider do you have to check to see if it's revoked, does anyone else need to maintain those indexes?
- How gets to revoke the key?
  - With UCAN whoever issued can revoke
  - Application level you might also allow delgation for who can revoke
- Blocking the actor
  - Service can do that
- Revoking specific delgation
  - #1400
- One needs to track context around why a capbiltiy was issued enables application level to say am I revoking the key or the capability
- Simpliest is revoke by CID
  - However, how do you map that back to keys? THat's the recoding problem
- How can you revoke all the delgations you've given to a principle?
  - How can you know the principle if every UCAN gets issued to a one off key?
    - revokation index chould be keyed off public key or hash of the VC, and what context is being revoked
- Revokation by CID in spec currently assumes JWT of UCAN
  - If UCAN was in non-JWT you have to translate
- Let's just pick an encoding and call that the CID
- Can we just say native link? Then encoding becomes transport problem
  - Native IPLD would be DAG-CBOR for the wire format
  - We want CBOR for DICE interop 🐢🐢🐢🐢🐢
    - https://github.com/ipld/js-dag-ucan/pull/4
- For each encoding type, there could be one canonical CID
  - No, don't encode as JSON
  - Encode as IPLD, then we get into native links, then it's guidaded by the representation
    - This sounds like that one-way converstaion on VC encoding, ref recent meeting with Sam
- Recoding to check if content id is revoked is non-ideal for some
- 7 extra chars per CID and alignment is achived