### 2022-05-25 UCAN Community Meeting

- 10:00 AM PDT
  - https://lu.ma/ucan
  - https://github.com/ucan-wg/spec/discussions/66
- I think that the topic to start is about ensuring there is consensus amongst implementers about what fields exist within JWT so that it's UCAN standard
  - Spec says, this is the minimum
    - There are further specs, however the downside is:
      - If someone doesn't like the existing implementation
  - Pure IPDL is deterministic
- Irakli
  - Sign with wallet key
  - CLient side genreate key pair
  - Root issuer of cap is a service, doesn't have to be, sometimes is self issued, they are a claim, the resource is yours
  - Looking at doing keybase style signing
- Boris Mann
  - Says that 50 millions accounts will be able to sign on if this works using this
- Sergey Ukstov
  - CWAY (Sign in with Etherium)
  - Sign in with everything
  - Signing using keys, no blockchain transaction happens
  - Blockchain wallets are the latest PKI, we don't have to solve key management
  - Once you sign, you are restricted to a single tab (due to metamask being a per tab thing)
  - Would you like to give this website/ application to get these permissions for this set of actions
    - That effectively creates a very basic capability chain
    - Ephemeral session key created for each sign in
    - Could do this with COCAO, but then you have a whole different world behind that browser tab (k8s, JWT, JWS style stuff)
      - Why not use JWT, JWS
      - For this to work, this delegation, we need to reference the parent capability
        - This need to access the parent capability as signed by the wallet is the topic of discussion
        - Main issue is the JWT algo
          - Need to support secp256k1 and BLS
          - There are JWS signing inputs which are needed
          - Irakli Gozalighvili: You could derive JWT form out of data to be signed, then just sign with other key?
          - JOT (aka JWT) and UCAN are strikingly similar but incompatible
            - Key ordering, key duplication, whitespace (all permitted by the JWT spec)
              - We're 
- IPLD structure ideally would not generate the JWT to sign
  - We are moving to proofs
  - Boris: "SIWE is attempting to standardize and get this into all wallet clients"
  - If you go from IPLD to JWT you can deterministically generate
    - If you can't deterministically generate with JWT you can do with CBOR
- PR 67 IPLD schema
  - https://github.com/ucan-wg/spec/pull/67
- Boris going IPFS
  - IPLD work is not what Boris is really focused on
- Biscuts reuqires you adopt data log
- IPLD has more of a strict structure
- Can always reencode

---

```
What about ed/x25519 shared key?
From Brooklyn Zelenka (@expede) to Everyone 10:14 AM
They need things like secp256k1
And BLS
From Me to Everyone 10:14 AM
Thank you!
From Philipp Krüger to Everyone 10:16 AM
I think part of the problem *may* be you can't quite sign arbitrary data in wallet clients (https://eips.ethereum.org/EIPS/eip-191)
From Benjamin Goering to Everyone 10:17 AM
at least the pronunciation is not a MUST
From Boris Mann to Everyone 10:17 AM
@philipp that's a separate issue 🙂
From Brooklyn Zelenka (@expede) to Everyone 10:17 AM
😉
From Boris Mann to Everyone 10:17 AM
And SIWE is attempting to standardize and get this into all wallet clients
From Philipp Krüger to Everyone 10:18 AM
Ok :+1:
From Benjamin Goering to Everyone 10:23 AM
👀 https://identity.foundation/JcsEd25519Signature2020/#jcs-ed25519-signature-2020
shoutout also to this for deterministic canonicalization/hashing https://w3c.github.io/rch-wg-charter/
From Me to Everyone 10:26 AM
+1 to that
From Benjamin Goering to Everyone 10:26 AM
ucan should beat the drum on "grand tradition (from WAAY back in the SAML and WS-* days) of the Interoperability Plug-Fest”
https://lists.w3.org/Archives/Public/public-credentials/2020Apr/0198.html
From Boris Mann to Everyone 10:26 AM
@Benjamin -- exactly
From Charles E. Lehner to Everyone 10:26 AM
🤙
From Me to Everyone 10:31 AM
Looking at doing this with GitHub with ssh keys and ed/x25519 keys
This is the simple case with the shared key, one can extend it to do what Irakli talked about by using distinct roots to act as VCs and adding in layers of dids allowing for rotation
From Charles E. Lehner to Everyone 10:31 AM
Take it to Internet Identity Workshop :D
From Benjamin Goering to Everyone 10:32 AM
+1 CEL
From Me to Everyone 10:33 AM
https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNpVUsFuwjAM_RUr53GBWw-TtjEG0iahAdshRVXSuG1Em1ZNsglR_n1uWgZcEr_k5fk59omltUIWsdjkrWgK2M5jY70cwC_KKf9GCdN9bABy7Qov-Zt2Sy_DSeFck1hsf7Dly-12DZsQ0x0adS80C0Kz8CwthDb8pV8v1NhkukS-oIWOPGkmgu9og6cLlgN-3l_YMJk8wkAN4Y2bnnID--tu9_negdIqUXXK56t5BIsgAoQhrY0jOxaIFRKMxCAc_MYmbNeksqcNUdBfGYtN6sDq3GiTQ-NlqVM44LED8qCzY1KhtSJH_hUgyCOUdX3oyb654ZOB-wchafcxAiWcuBoeugJadWNIrRyO-keDaEKifP2vD9bVLSqgasZm3lV1ren2S9kDq7CthFY0Lqe-jTFzBVYYs4hChZnwpYtpks5E9Q25xFelKROLMlFafGDCu3pzNCmLXOvxQpprQVNSjazzH5-i7EM
From Benjamin Goering to Everyone 10:36 AM
link to Gordon on evolution?
From Boris Mann to Everyone 10:37 AM
All of his writing here https://subconscious.substack.com/
From Benjamin Goering to Everyone 10:37 AM
ty
From Boris Mann to Everyone 10:37 AM
UCAN announced here https://subconscious.substack.com/p/layered-protocols?s=r
From Gordon to Everyone 10:37 AM
@Benjamin this might be what Boris was referencing https://subconscious.substack.com/p/exapt-existing-infrastructure
From Benjamin Goering to Everyone 10:38 AM
ty
From Boris Mann to Everyone 10:39 AM
wg/spec/pull/67
```