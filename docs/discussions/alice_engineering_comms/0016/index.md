# 2022-09-01 Engineering Logs

- Community
  - “Heros are not giant statues framed against a red sky. They are people who say this is my community, and it’s my responsibility to make it better.” [Oregon Governor Tom McCall]
- WebUI
  - https://jsoncrack.com/editor
    - We could leverage JSON Crack to provide easy editing of seed data
    - Cloud fork and extend the JSON Crack project to add support for visualizing dataflows
      - Previously when using react-flow (https://github.com/wbkd/react-flow) we had used mermaid output SVG cords to find where to place nodes, we could probably just pull that code out of mermaid
    - We could do something like the Intuitive and Accessible Documentation Editing GSoC 2022 project where we swap out the mermaid diagram for the extended version of the JSON Crack editor to make the operations in the nodes editable. This is helpful when using operations such as `run_dataflow()` which can have alternate inputs. Any operation defined as a class `OperationImplementation`/`OperationImplementationContext` within the `run()` method of the context we can take the inputs as a dictionary as an argument.

![image](https://user-images.githubusercontent.com/5950433/187969698-2d572d99-9f20-4618-b1bb-086add503f7e.png)

![image](https://user-images.githubusercontent.com/5950433/187969864-3b38fcb4-de02-4e47-b57e-f8a62f0f8f11.png)

![image](https://user-images.githubusercontent.com/5950433/187970084-ab027823-efce-4d42-8146-6b7caf12f328.png)