- We'll have TCB levels for tool use
- https://python.langchain.com/docs/use_cases/tool_use/agents
- https://python.langchain.com/docs/use_cases/graph/semantic

```python
import json
from operator import itemgetter
from typing import Union

from langchain_core.tools import tool
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.output_parsers import JsonOutputToolsParser
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
from langchain_openai import ChatOpenAI

import snoop


@tool
def forcast(historical_stock_prices: str) -> str:
    "Make forcast given historical stock prices"
    historical_stock_prices = json.loads(historical_stock_prices)
    year, month, day = historical_stock_prices[-1][0].split("-")
    return json.dumps(
        [
            (
                "-".join([year, month, str(int(day) + (i + 1))]),
                historical_stock_prices[-1][1] + ((i + 1) * 10.0),
            )
            for i, (key, value) in enumerate(historical_stock_prices)
        ]
    )


@tool
def historical_stock_prices(ticker: str) -> str:
    "Get the historical stock prices for a stock ticker"
    return json.dumps(
        [
            ("2024-03-22", 42.0),
            ("2024-03-23", 52.0),
            ("2024-03-24", 62.0),
        ]
    )


# @snoop
def main():
    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/openai-tools-agent")

    # Choose the LLM that will drive the agent
    # Only certain models support this
    model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

    # Pass tools available for model use
    tools = [forcast, historical_stock_prices]
    model_with_tools = model.bind_tools(tools)
    tool_map = {tool.name: tool for tool in tools}

    # Create an auto chain caller, so that one functions output can feed others
    def call_tool(tool_invocation: dict) -> Union[str, Runnable]:
        """Function for dynamically constructing the end of the chain based on the model-selected tool."""
        tool = tool_map[tool_invocation["type"]]
        return RunnablePassthrough.assign(output=itemgetter("args") | tool)
    call_tool_list = RunnableLambda(call_tool).map()
    chain = model_with_tools | JsonOutputToolsParser() | call_tool_list

    snoop.pp(chain.invoke("What is the forcast for INTC?"))

    # Construct the OpenAI Tools agent
    agent = create_openai_tools_agent(model, tools, prompt)

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke(
        {
            "input": "What is the forcast for INTC?",
        }
    )


if __name__ == "__main__":
    main()
```