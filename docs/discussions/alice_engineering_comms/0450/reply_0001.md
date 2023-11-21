## 2023-11-13 SCITT Community List Ned on OAuth ADCR and SCITT

On Mon, Nov 13, 2023 at 10:00 AM Smith, Ned <ned.smith@intel.com> wrote:
>
> > From: John Andersen <johnandersenpdx@gmail.com>
> > Date: Monday, November 13, 2023 at 7:42 AM
> > To: "scitt-community@groups.io" <scitt-community@groups.io>
> > Cc: "Melara, Marcela" <marcela.melara@intel.com>, "Smith, Ned" <ned.smith@intel.com>
> > Subject: Re: [scitt-community] Standalone version of scitt-emulator client create-statement
> >
> > IMHO we move towards farther towards decentralized trust when we combine build metadata referenced in statements to federated instances with OAuth ADCR approach. As TS + policy engine would have the information it needs to act as a RATS Verifier, where the passport is a receipt.
>
>  
>
> I’m not sure I agree in principle that an OAuth “Attestation Provider” (i.e., RATS Verifier) has the same semantics as a SCITT TS. I think the desire is for a TS receipt to say: “I witnessed this signature operation”. In a RATS Verifier, the TS watches the RATs Verifier use its key to sign the Attestation Results. In a TPM, it watches the Attester sign Evidence.
>
>  
>
> I’m still not convinced that the SCITT TS can say this however, unless it is tightly integrated with the signer in such a way that it can observe the signing operation directly (but without observing the key material or other secrets). I don’t know of any technology that does this! Hence, the TS isn’t saying “I witnessed this signature operation”, it can only say “I witnessed this signature”. There is a big difference IMHO. The latter just means the signed artifact was logged (and the signer identity was checked, maybe signer authorization was checked, and the artifact was logged with a range of transparency from nil to fully disclosed).
>
>  
>
> A physical-world notary observes the signer as they sign the document. The SCITT TS doesn’t do this. It is closer to: The signer signs the document at home, drives to the notary, presents the signed document to the notary, the notary looks at the signature and assess that it looks like the signers handwriting or maybe assess that the ink is still relatively fresh, or something along these lines. I just think “Notary” is misleading (and don’t believe it should exist in the SCITT architecture).
>
>  
>
> Back to the OAuth ADCR use case. The Attestation Provider asserts that the container that the AS wants to provision the Client software + identity into is valid (based on AS policy). The role of a TS possibly adds value if it aims to detect duplicitous AP behavior. For example, If the Client (Attester) asserts it is a tomato but the AP (RATS Verifier) asserts to the AS that the Attester is a grape (after having asserted it was a tomato earlier). A TS might flag this as duplicitous under the assumption that once a tomato always a tomato. But even this isn’t always true. A device can be remanufactured to become a different type of device. FPGAs and VMs are designed to make this easy.
>
>  
>
> At best the second “T” in SCITT should be a little “t”. The first “T” might also be a little “t” depending on policies for selective disclosure.
>
>  
>
> Cheers,
>
> Ned