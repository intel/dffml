- Dumping links while closing tabs
- https://github.com/bluesky-social/adx/blob/main/architecture.md#personal-data-repositories
- https://fastapi.tiangolo.com/advanced/graphql/?h=graphql
- https://strawberry.rocks/docs/general/subscriptions
- https://github.com/pdxjohnny/dffml/tree/manifest/entities/alice
- https://github.com/ostreedev/ostree
- https://github.com/giampaolo/psutil
- https://netboot.xyz/docs/quick-start/
- https://rich.readthedocs.io/en/stable/markdown.html
  - `$ python -m rich.markdown README.md`
- https://github.com/intel/dffml/discussions/1382
  - https://github.com/dffml/active-directory-verifiable-credentials-python
- https://github.com/intel/dffml/discussions/1383
- Abstract submission deadline Jun. 24, 2022
  - Intel Security Conference (iSecCon) 2022 Call for Papers
  - https://easychair.org/account/signin
  - [U.S. iSecCon 2022_submission_instructions.pdf](https://github.com/intel/dffml/files/8884245/U.S.iSecCon.2022_submission_instructions.pdf)
- https://www.thethingsindustries.com/docs/devices/adding-devices/
- https://github.com/ipld/ipld/
  - https://ipld.io/docs/intro/hello-world/
- https://localhost.run
- https://identity.foundation/credential-manifest/
- https://github.com/intel/cve-bin-tool
- https://github.com/johnlwhiteman/living-threat-models
  - https://github.com/johnlwhiteman/living-threat-models/issues/1
  - https://github.com/intel/cve-bin-tool/pull/1698
- https://github.com/pdxjohnny/pdxjohnny.github.io/blob/dev/content/posts/tricks.md

---

- Below doesn't work, need to diff with other version in Volume 0 and update there if appropriate.

```

flowchart TD
    subgraph notes[Notes]
      tbDEX_all_messages_communicated_via_chain[All tbDEX Messages]
    end

    subgraph web3
      input_to_did[Encode Every Input to DID/DID Doc]
      input_to_chain[Send DID/DID Doc to Chain]

      subgraph tbDEX
        Ask --> |PFI| COND_OFFER[Conditional Offer]
        COND_OFFER --> |Alice| OFFER_ACCEPT[Offer Accept]
        OFFER_ACCEPT --> |PFI| IDV_REQ[IDV Request]
        IDV_REQ ---> |Alice| IDV_SUB[IDV Submission]
        IDV_SUB --> |PFI| IDV_REQ
        IDV_SUB --> |PFI| SETTL_REQ[Settlement Request]
        SETTL_REQ --> |Alice| SETTL_DETAIL[Settlement Details]
        SETTL_DETAIL --> |PFI| IDV_REQ
        SETTL_DETAIL ---> |PFI| SETTL_REQ
        SETTL_DETAIL --> |PFI| SETTL_RECEIPT[Settlement Receipt]
      end
    end

    subgraph pfi_open_architecture_dataflow[PFI - Open Architecture DataFlow]
      pfi_inputs[New Inputs]
      pfi_operations[Operations]
      pfi_opimps[Operation Implementations]

      pfi_ictx[Input Network]
      pfi_opctx[Operation Network]
      pfi_opimpctx[Operation Implementation Network]
      pfi_rctx[Redundency Checker]
      pfi_lctx[Lock Network]

      pfi_opctx_operations[Determine which Operations may have new parameter sets]
      pfi_ictx_gather_inputs[Generate Operation parameter set pairs]
      pfi_opimpctx_dispatch[Dispatch operation for running]
      pfi_opimpctx_run_operation[Run an operation using given parameter set as inputs]

      pfi_operation_system_context_run[system_context_run operation]
      pfi_operation_prioritizer_check_aligned_system_contexts[prioritizer_check_aligned_system_contexts operation]
      pfi_operation_prioritizer_check_aligned_system_contexts_trigger[prioritizer_check_aligned_system_contexts_trigger operation]
      pfi_operation_call_for_aligned_system_contexts[call_for_aligned_system_contexts operation]

      pfi_inputs --> pfi_ictx

      pfi_operations -->|Register With| pfi_opctx
      pfi_opimps -->|Register With| pfi_opimpctx

      pfi_ictx --> pfi_opctx_operations
      pfi_opctx --> pfi_opctx_operations

      pfi_opctx_operations --> pfi_ictx_gather_inputs
      pfi_ictx_gather_inputs --> pfi_rctx
      pfi_rctx --> |If operation has not been run with given parameter set before| pfi_opimpctx_dispatch

      pfi_opimpctx_dispatch --> pfi_opimpctx

      pfi_opimpctx --> pfi_lctx

      pfi_lctx --> |Lock any inputs that can't be used at the same time| pfi_prioritizer

      pfi_opimpctx_run_operation --> |Outputs of Operation become inputs to other operations| pfi_inputs

      subgraph pfi_subgraph_prioritizer[Prioritization]
        pfi_prioritizer[Prioritizer]
        pfi_new_system_context[New System Context]
        pfi_execute_system_context[PFI Execute System Context]
        pfi_get_aligned_system_contexts[Get Aligned System Contexts on System Context Execution]
        pfi_ensure_context_on_chain[Get Aligned System Contexts on System Context Execution]
        pfi_check_on_aligned_system_contexts[Check on Aligned System Contexts]

        pfi_prioritizer -->|New System Context Executed In House| pfi_execute_system_context
        pfi_prioritizer -->|New System Context Explore Collaberation Oppertunities| pfi_get_aligned_system_contexts
        pfi_prioritizer -->|System Context Aligned System Context Recieved| pfi_check_on_aligned_system_contexts
        pfi_prioritizer -->|Timeout for System Context Aligned System Context Selection| pfi_check_on_aligned_system_contexts

        pfi_get_aligned_system_contexts -->|Ensure System Context on chain and<br>clearly broadcasted request for aligned system contexts to chain| pfi_ensure_context_on_chain

        pfi_ensure_context_on_chain --> input_to_chain

        pfi_opimpctx_run_operation --> pfi_operation_system_context_run
        pfi_opimpctx_run_operation --> pfi_operation_evaluate_conditional_offer

        pfi_operation_system_context_run --> pfi_prioritizer
        pfi_prioritizer -->|Determins we want to<br>wait for aligned system contexts before executing<br>set trigger to go with best aligned_system_context<br>on timeout or other condition| pfi_operation_prioritizer_check_aligned_system_contexts_trigger
        pfi_operation_prioritizer_check_aligned_system_contexts_trigger --> pfi_operation_prioritizer_check_aligned_system_contexts

        pfi_operation_prioritizer_check_aligned_system_contexts_trigger_timeout --> pfi_operation_prioritizer_check_aligned_system_contexts_trigger

        pfi_operation_prioritizer_check_aligned_system_contexts -->|If time is up or good enough offer threshold meet| COND_OFFER

        pfi_prioritizer --> OFFER_ACCEPT
      end

      pfi_execute_system_context -->|Execute on prioritizer go ahead| pfi_opimpctx_run_operation
    end

    subgraph alice_open_architecture_dataflow[Alice - Open Architecture DataFlow]
      alice_inputs[New Inputs]
      alice_operations[Operations]
      alice_opimps[Operation Implementations]
      alice_prioritizer[Prioritizer]

      alice_ictx[Input Network]
      alice_opctx[Operation Network]
      alice_opimpctx[Operation Implementation Network]
      alice_rctx[Redundency Checker]
      alice_lctx[Lock Network]

      alice_opctx_operations[Determine which Operations may have new parameter sets]
      alice_ictx_gather_inputs[Generate Operation parameter set pairs]
      alice_opimpctx_dispatch[Dispatch operation for running]
      alice_opimpctx_run_operation[Run an operation using given parameter set as inputs]

      alice_inputs --> alice_ictx

      alice_operations -->|Register With| alice_opctx
      alice_opimps -->|Register With| alice_opimpctx

      alice_ictx --> alice_opctx_operations
      alice_opctx --> alice_opctx_operations

      alice_opctx_operations --> alice_ictx_gather_inputs
      alice_ictx_gather_inputs --> alice_rctx
      alice_rctx --> |If operation has not been run with given parameter set before| alice_opimpctx_dispatch

      alice_opimpctx_dispatch --> alice_opimpctx

      alice_opimpctx --> alice_lctx

      alice_lctx --> |Lock any inputs that can't be used at the same time| alice_prioritizer

      alice_prioritizer -->|Execute on prioritizer go ahead| alice_opimpctx_run_operation

      alice_opimpctx_run_operation --> |Outputs of Operation become inputs to other operations| alice_inputs

      subgraph alice_subgraph_prioritizer[Prioritization]
        alice_prioritizer[Prioritizer]
        alice_new_system_context[New System Context]
        alice_execute_system_context[Alice Execute System Context]

        alice_prioritizer -->|New System Context From External Entity<br>Create offer by creating a DID for an aligned system context.<br>Determine set of valid system contexts<br>given top level system context and assets at disposal.<br>Ensure provenance information / reviews submitted up front with aligned system context as proposal/ASK for acceptable execution, rememberence, or hypothesis of aligned system context<br>Respond with proposed<br>DID of the aligned system context<br>given as sourceCurrency| Ask

        alice_ensure_context_on_chain --> input_to_chain

        alice_opimpctx_run_operation --> alice_operation_system_context_run
        alice_opimpctx_run_operation --> alice_operation_evaluate_conditional_offer

        alice_operation_system_context_run --> alice_prioritizer
        alice_prioritizer -->|Determins we want to<br>wait for aligned system contexts before executing<br>set trigger to go with best aligned_system_context<br>on timeout or other condition| alice_operation_prioritizer_check_aligned_system_contexts_trigger
        alice_operation_prioritizer_check_aligned_system_contexts_trigger --> alice_operation_prioritizer_check_aligned_system_contexts

        alice_operation_prioritizer_check_aligned_system_contexts_trigger_timeout --> alice_operation_prioritizer_check_aligned_system_contexts_trigger

        alice_operation_prioritizer_check_aligned_system_contexts -->|If time is up or good enough offer threshold meet| COND_OFFER

        alice_prioritizer --> OFFER_ACCEPT
      end

      alice_execute_system_context -->|Execute on prioritizer go ahead| alice_opimpctx_run_operation
    end

    pfi_ictx --> input_to_did
    alice_ictx --> input_to_did

    input_to_did --> input_to_chain

    input_to_chain --> pfi_inputs
    input_to_chain --> alice_inputs

    pfi_opimpctx_run_operation --> evaluate_conditional_offer

    run_system_context_operation_get_aligned_system_contexts[run_system_context operation get aligned system contexts]

    pfi_opimpctx_run_operation -->|Alice Strategic Plan Suggests New Sytem Context<br>and Wants Aligned System Contexts to Execute| run_system_context_operation_get_aligned_system_contexts

    tbDEX_all_messages_communicated_via_chain -->|Communicated via Chain for POC| input_to_did


    
```