- https://www.youtube.com/watch?v=4D4rGDDh7Q0&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK&index=33&t=1083
- Alice co maintain this distro package, or this set of distro packages
- mermaid to operations based on dataflow which does best guess fuzzy find for pulling operations from inventories (could be accessed via DIDs)
- Given YAML or JSON examples, build dataclasses with correct observed types
- https://github.com/decentralized-identity/decentralized-web-node/issues/136#issuecomment-1085832891
  - > There is no custom tbDEX interface, tbDEX is just a set of schema'd objects sent over Threads and data objects fetchable in Collections. The point of this tech is specifically that you don't create new interfaces or API surfaces, your messages are your own API that you get by simply defining their schemas and how to handle them. You'll never see a tbDEX-specific feature, because tbDEX is literally just a set of message types that are defined independently
  - > Jack, I'm not sure, but I think you may again be twisting up Decentralized Identifiers with Verifiable Credentials. No one issues DIDs, users just have them, and Issuers issue credentials. That said, you can tell which Issuers can issue which credentials by looking for Credential Manifest objects present in their Collections. Credential Manifests are schema'd objects that define what credentials an Issuer can issue.
  - https://github.com/decentralized-identity/decentralized-web-node/issues/136#issuecomment-1107530144
- https://dffml.github.io/dffml-pre-image-removal/master/concepts/dataflow.html
  - Worked through drawing out dataflow on paper combined with tbDEX flow.

```mermaid
flowchart TD
    subgraph tbDEX
      Ask --> |Bob| COND_OFFER[Conditional Offer]
      COND_OFFER --> |Alice| OFFER_ACCEPT[Offer Accept]
      OFFER_ACCEPT --> |Bob| IDV_REQ[IDV Request]
      IDV_REQ ---> |Alice| IDV_SUB[IDV Submission]
      IDV_SUB --> |Bob| IDV_REQ
      IDV_SUB --> |Bob| SETTL_REQ[Settlement Request]
      SETTL_REQ --> |Alice| SETTL_DETAIL[Settlement Details]
      SETTL_DETAIL --> |Bob| IDV_REQ
      SETTL_DETAIL ---> |Bob| SETTL_REQ
      SETTL_DETAIL --> |Bob| SETTL_RECEIPT[Settlement Receipt]
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

      alice_operation_system_context_run[system_context_run operation]
      alice_operation_prioritizer_check_bids[prioritizer_check_bids operation]
      alice_operation_prioritizer_check_bids_trigger[prioritizer_check_bids_trigger operation]
      alice_operation_call_for_bids[call_for_bids operation]

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

      subgraph alice_get_bids[Get Bids on System Context Execution]
        alice_opimpctx_run_operation --> alice_operation_system_context_run
        alice_opimpctx_run_operation --> alice_operation_evaluate_conditional_offer

        alice_operation_system_context_run --> alice_prioritizer
        alice_prioritizer -->|Determins we want to<br>wait for bids before executing<br>set trigger to go with best bid<br>on timeout or other condition| alice_operation_prioritizer_check_bids_trigger
        alice_operation_prioritizer_check_bids_trigger --> alice_operation_prioritizer_check_bids

        alice_operation_prioritizer_check_bids_trigger_timeout --> alice_operation_prioritizer_check_bids_trigger
        Ask --> alice_operation_prioritizer_check_bids_trigger

        alice_operation_prioritizer_check_bids -->|If time is up or good enough offer threshold meet| COND_OFFER

        alice_prioritizer --> OFFER_ACCEPT
      end
    end

    subgraph bob_open_architecture_dataflow[Bob - Open Architecture DataFlow]
      bob_inputs[New Inputs]
      bob_operations[Operations]
      bob_opimps[Operation Implementations]
      bob_prioritizer[Prioritizer]

      bob_ictx[Input Network]
      bob_opctx[Operation Network]
      bob_opimpctx[Operation Implementation Network]
      bob_rctx[Redundency Checker]
      bob_lctx[Lock Network]


      bob_opctx_operations[Determine which Operations may have new parameter sets]
      bob_ictx_gather_inputs[Generate Operation parameter set pairs]
      bob_opimpctx_dispatch[Dispatch operation for running]
      bob_opimpctx_run_operation[Run an operation using given parameter set as inputs]

      bob_inputs --> bob_ictx

      bob_operations -->|Register With| bob_opctx
      bob_opimps -->|Register With| bob_opimpctx

      bob_ictx --> bob_opctx_operations
      bob_opctx --> bob_opctx_operations

      bob_opctx_operations --> bob_ictx_gather_inputs
      bob_ictx_gather_inputs --> bob_rctx
      bob_rctx --> |If operation has not been run with given parameter set before| bob_opimpctx_dispatch

      bob_opimpctx_dispatch --> bob_opimpctx

      bob_opimpctx --> bob_lctx

      bob_lctx --> |Lock any inputs that can't be used at the same time| bob_prioritizer
      
      bob_prioritizer -->|Execute on prioritizer go ahead| bob_opimpctx_run_operation

      bob_opimpctx_run_operation --> |Outputs of Operation become inputs to other operations| bob_inputs
    end

    subgraph web3
      input_to_did[Encode Every Input to DID/DID Doc]
      input_to_chain[Send DID/DID Doc to Chain]

      alice_ictx --> input_to_did
      bob_ictx --> input_to_did

      input_to_did --> input_to_chain

      input_to_chain --> alice_inputs
      input_to_chain --> bob_inputs
    end

    Ask --> alice_ictx

    alice_opimpctx_run_operation --> evaluate_conditional_offer

    note[Create offer - aka bid on job<br>respond with proposed<br>DID of to be executed system context<br>given as sourceCurrency]

    run_system_context_operation_get_bids[run_system_context operation get bids]

    alice_opimpctx_run_operation -->|Alice Strategic Plan Suggests New Sytem Context<br>and Wants Bids to Execute| run_system_context_operation_get_bids

    run_system_context_operation_get_bids --> Ask

```