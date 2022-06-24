Technically, Alice is herself a system context.

A system context which contains

- DataFlows for interacting with her via various channels
- Shared configs which build the foundations of the instances of plugins which might be used within 
  - If a config reload would happen ask what to do and if hot reload then great 
  - Check for this based on changes to items where we look at locality to determine if data needs to be transferred to parallel agents 
  - Static content such as trained models or defined input sets (`.csv` files).