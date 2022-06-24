- https://github.com/facebookresearch/Generic-Grouping
  - This is good stuff for our 2x2 encoded strategic plan output to feature mapping
- Zeroith draft of RFC: a9bdd580fe250582db61ab8ba321a9daf110c7c7
  - https://raw.githubusercontent.com/intel/dffml/a9bdd580fe250582db61ab8ba321a9daf110c7c7/docs/rfcs/0000-Open-Architecture.txt
- Vadim has cool https://github.com/rfprod/rust-workspace automation
- Its time to re-open binsec scanning of distros (let's fire a broadside down distrowatch do some static analysis and see how they stack up ;)

![Man the cannons! Fire broadsides down distrowatch line](https://upload.wikimedia.org/wikipedia/commons/6/6a/Battleship1.jpg)

- Were off to see the wizards. The wonderful wizards of working groups. What OpenSSF working group Open Architecture might fit under, or if this effort already has been completed or exists in progress.

![image](https://user-images.githubusercontent.com/5950433/168154171-fc283ca3-bc2e-4f9c-8646-00900d747544.gif)

- RBAC on DIDs via provenance and dynamic trust relationships
- Failure Mode Analysis
  - For each compoeent of infra srcutrue you use you define failure modes as strategic plans outputs
    - Attah to each failure mode obseravabiltiy metrics via consuming them via strategic plans
      - Based on those observiablity metrics you desgign mittiations via strategic plans
-  https://github.com/dalek-cryptography/x25519-dalek/issues/67#issuecomment-806490225
  - > We do not recommend you do this. If you can at all escape from doing this, you absolutely should. You should never be reusing keys for both authentication and encryption. You especially should not be doing this without a very strong understanding of potential ramifications in the protocol you're working on. I'm sorry, I feel like I'm being a jerk here, but we've already spelled it out pretty explicitly how to accomplish this with our public API, and also that we don't support people doing it. I'm refusing to provide copy/paste code to further facilitate potentially bad practices.
    - https://github.com/hyperledger/ursa/blob/92d752100e6c8afde48e3406eaa585e1cb02b954/libursa/src/signatures/ed25519.rs#L288-L299
    - Okay no we are tabling this.
- WE shold be looking at stable of DIDComm https://github.com/sicpa-dlab/didcomm-python/tree/stable
  - https://github.com/sicpa-dlab/didcomm-python/tree/stable#2-build-an-unencrypted-but-signed-didcomm-message
    - This is what we want to start