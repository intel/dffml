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
  - https://www.biscuitsec.org/
  - fission is also working on this but does not require
    - They are also looking at identiy aware context
- IPLD has more of a strict structure
- Can always reencode
- IPDL is the next level of leaning into this stuff
- There are extentions that do AD Oauth
  - https://docs.microsoft.com/en-us/azure/active-directory/verifiable-credentials/decentralized-identifier-overview
- Use case Caviats are solving
  - Benjamin: SOmeone has the ability to delicate to a bucket of data, they want 
  - Can be expested in the second capability, you don't need the second

```
Biscuit for reference 
https://www.biscuitsec.org/

From Brooklyn Zelenka (@expede) to Everyone 10:44 AM
Just looking at the clock, we should probably move on to ADG shortly
From Gordon to Everyone 10:48 AM
Analogous: HTTP header spec has a specification for the header syntax itself, but deliberately does not specify header body field.
There are separate specs for body fields.
From Benjamin Goering to Everyone 10:48 AM
dereference proof id to some well defined definition of ‘proof’. comparing well defined proof syntax https://medium.com/mattr-global/jwt-vs-linked-data-proofs-comparing-vc-assertion-formats-a2a4e6671d57
From Brooklyn Zelenka (@expede) to Everyone 10:49 AM
It's a literal block chain
From Boris Mann to Everyone 10:51 AM
This is an emerging phrasing https://en.wikipedia.org/wiki/Inner_source
Flow chart from John -> https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNpVUsFuwjAM_RUr53GBWw-TtnUMpE1CA7ZDiqqkMW1Em1ZNsglR_n1uCqNcEj_n-fklzolltUIWscTkrWgK2MSJsV4O4BfllH-jhOkuMQC5doWX_E27hZchUzjXpBbbH2z5YrNZwTrEdIZG3QvNgtAslGWF0Ia_9OuVmpi9LpHPaaGUJ81U8C1t8HTFcsDPuysbJpNHGKghHLnpKSPYH3fbz_cOlFapqjMeL-MI5kEECENWG0d2LBArNLgQg3Dwm5iw3ZrKnjZEQX9pLDaZA6tzo00OjZelzuCAxw7Ig94f0wqtFTnyrwBBHqGs60NP9s2ITwbuC0LT7uMClHDiZniYCmjVXUIa5ZDqiwbRlET56l8frKtbVEC3uQzz7la3O42flD2wCttKaEXf5dSPMWGuwAoTFlGoRHtI6BudiecbsoivSlMbFu1FafGBCe_q9dFkLHKtxysp1oK-SDUkz3_lcuq1
From Philipp Krüger to Everyone 10:54 AM
This is what AD refers to, right? v
https://en.wikipedia.org/wiki/Active_Directory
From Benjamin Goering to Everyone 10:55 AM
EEE
From Philipp Krüger to Everyone 10:55 AM
Blogpost incoming? :P
From Benjamin Goering to Everyone 10:56 AM
https://docs.microsoft.com/en-us/azure/active-directory/verifiable-credentials/decentralized-identifier-overview
From Philipp Krüger to Everyone 10:56 AM
https://en.wikipedia.org/wiki/Active_Directory#Certificate_Services
From Me to Everyone 10:57 AM
Just yesterday!
Thank you!
From Dmitri Zagidulin (@XR_Engine) to Everyone 10:57 AM
question for the group (that I'd love to ask on the next call) - has the option of /not/ using caveats been discussed previously?  
From Sergey Ukustov to Everyone 10:57 AM
Can we validate a capability chain, if an end consumer have no idea about an attached proof format?
From Dmitri Zagidulin (@XR_Engine) to Everyone 10:57 AM
(the context for asking that is just - so the zCap spec started out with caveats, but  ended up not needing them (target url narrowing is sufficient) and is deprecating them)
From Hugo @hugomrdias to Everyone 10:57 AM
please save the chat somewhere
From Brooklyn Zelenka (@expede) to Everyone 10:58 AM
We'll post it!
```