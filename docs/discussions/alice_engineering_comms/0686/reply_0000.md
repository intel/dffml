## 2024-08-11 @pdxjohnny Engineering Logs

- https://copr.fedorainfracloud.org/coprs/
- https://medium.com/happy-blockchains/navigating-the-crossroads-of-legacy-and-innovation-in-self-sovereign-identifier-solutions-d7724f157283
- https://trustoverip.org/blog/2024/03/21/authentic-chained-data-containers-acdc-task-force-announces-public-review/
- https://medium.com/happy-blockchains/keri-is-not-complex-or-complicated-instead-it-simplifies-da285b20a7db


> These are the known and unintended simplifications so far that KERI, ACDC, and CESR have brought to the world:
>
> - 1. KERI’s novel pre-rotating mechanism (intended) means private keys are quantum-attack resistant via a clever trick (spin-off).
>
> - 2. KERI has cut out intermediaries (intended) from the equation in binding between the controller, private, and public keys. The purely cryptographic nature of these bindings simplifies them: they are all cryptographically strong and end-to-end verifiable (spin-off).
>
> - 3. KERI is omnipresent and trust-spanning (intended). Simplification: No blockchain silos with a need to build and maintain interoperability forever (spin-off).
>
> - 4. CESR (needed) has ended the streaming encoding wars between CBOR, JSON, and MSGPACK; it handles them all (spin-off).
>
> - 5. CESR has round-robin composability between text and binary (intended). This eliminates the need to prove the consistency and authenticity of readable legal digital documents when sent over the Internet (spin-off).
>
> - 6. In ACDCs, the system guides you to sign everything* at rest (KERI’s KEL and TEL) and in motion (CESR). You don’t have to ask yourself whether this is signed off. It is always, anywhere, by anyone or anything.
>
> > * Most verifiable credentialing systems sign at rest. ACDCs bind the issuance to the key state at the time of issuance. They are bound or sealed at rest to the key state, and that key state is signed. The ACDCs themselves are not signed but have Seals anchored in TELS which in turn have Seals anchored in KELS.
>
> KERI solves the problem of having to reissue all issuances (it’s necessary) every time you rotate keys.
>
> - 7. The all-encompassing non-repudiability and duplicity evidence of operations that seal, bind, or anchor (synonyms in KERI) actions to the controller of the current signing key of a KEL simplifies life substantially: IT personnel can’t “get away” anymore with acting maliciously. Until today, in systems without KERI, a system administrator can easily obfuscate his actions. Any external party cannot do a risk assessment. Often, only weeks or months later, malicious actors with root user rights can be demasked. KERI makes life easier.
>
> If you now consider that KERI is, just “maybe,” a bit complicated while delivering these overwhelming spin-off simplifications, then my work is all but done.
>
> Conclusion
> KERI is “AND and AND”:
>
> It’s predictable, therefore at the maximum complicated, instead of complex) AND Although KERI’s features and code and interrelations between components aren’t reducible as such (next article), its complicatedness can be reduced by black-boxing KERI AND KERI’s killer feature is that it simplifies the Identity space by combining planned and unforeseen characteristics. Cliff hanger Critics only perceive KERI in the narrow definition of complicated. We can and will further reduce KERI’s complication by working on 5W’s: Wallet, Witness, Watchers, Web, and Wizard.
>
> Would we ever reduce complications by throwing essential parts out?'
>
> And if we could throw out non-essential parts, would we have complied with our own minimal-sufficient-solution rule in the first place?
>
> Twice, the answer is ‘no.’ For those still puzzled and thinking, ‘How can you reduce complications if you don’t throw anything out?’ ->
>
> That’s the topic of another article.

- https://github.com/trustoverip/tswg-cesr-specification

![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png) 

- https://github.com/WebOfTrust/cesr-test-vectors/tree/3dd1317ed174899d72f026c12cc55a926ad31d0b/example_payloads/keripy_tests/v2/CBOR
- https://github.com/trustoverip/tswg-cesr-specification/issues/85#issuecomment-2098527117
- https://github.com/WebOfTrust/keripy/pull/838/files#diff-cfa87ed0aa63854523a9bd01528b8c47c45f1c7712e9eb0bd3d789ef813748fd
- https://keripy.readthedocs.io/en/latest/_modules/keri/peer/exchanging/#exchange
- https://github.com/SmithSamuelM/Papers/blob/f9d3b91d3313e13bccd84180a3c99657882af2f9/whitepapers/SustainablePrivacy.pdf
- https://github.com/SmithSamuelM/Papers/blob/f9d3b91d3313e13bccd84180a3c99657882af2f9/whitepapers/SustainablePrivacy.pdf
- https://www.trustoverip.org/blog/2023/01/05/the-toip-trust-spanning-protocol/#Forerunners%20for%20the%20ToIP%20Trust%20Spanning%20Protocol