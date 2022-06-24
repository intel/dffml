Technically, Alice is herself a system context.

A system context which contains

- DataFlows for interacting with her via various channels
  - All the data collection flows, called from appropriate scope based on channel / trigger
    - These can be more easily shared via shared configs
    - PyPi package event? (listening for created releases)
      - Run Python package relevant data collectors
        - Trigger strategic plans which take data collector outputs or structured logged data as inputs.
- Shared configs which build the foundations of the instances of plugins which might be used within 
  - If a config reload would happen ask what to do and if hot reload then great 
  - Check for this based on changes to items where we look at locality to determine if data needs to be transferred to parallel agents 
  - Static content such as trained models or defined input sets (`.csv` files).