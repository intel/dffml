## 2024-03-24 @pdxjohnny Engineering Logs

- https://python.langchain.com/docs/use_cases/tool_use/agents
  - https://python.langchain.com/docs/use_cases/tool_use/parallel
  - > Chains are great when we know the specific sequence of tool usage needed for any user input. But for certain use cases, how many times we use tools depends on the input. In these cases, we want to let the model itself decide how many times to use tools and in what order. Agents let us do just this.
    >
    > LangChain comes with a number of built-in agents that are optimized for different use cases. Read about all the agent types here.
    >
    >As an example, let’s try out the OpenAI tools agent, which makes use of the new OpenAI tool-calling API (this is only available in the latest OpenAI models, and differs from function-calling in that the model can return multiple function invocations at once).
- https://platform.openai.com/docs/quickstart?context=python
  - > First, create an [OpenAI account](https://platform.openai.com/signup) or [sign in](https://platform.openai.com/login). Next, navigate to the [API key page](https://platform.openai.com/account/api-keys) and "Create new secret key", optionally naming the key. Make sure to save this somewhere safe and do not share it with anyone.

[![asciicast](https://asciinema.org/a/648919.svg)](https://asciinema.org/a/648919)

```python
import os
import sys
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


# These functions are our tools


@tool
def forecast(historical_stock_prices: str) -> str:
    "Make forecast given historical stock prices"
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
    model = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        temperature=0,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_api_base=os.environ.get("OPENAI_API_BASE"),
    )

    # Pass tools available for model use
    tools = [forecast, historical_stock_prices]
    model_with_tools = model.bind_tools(tools)
    tool_map = {tool.name: tool for tool in tools}

    # Create an auto chain caller, so that one functions output can feed others
    def call_tool(tool_invocation: dict) -> Union[str, Runnable]:
        """Function for dynamically constructing the end of the chain based on the model-selected tool."""
        tool = tool_map[tool_invocation["type"]]
        return RunnablePassthrough.assign(output=itemgetter("args") | tool)

    call_tool_list = RunnableLambda(call_tool).map()
    chain = model_with_tools | JsonOutputToolsParser() | call_tool_list

    # Construct the OpenAI Tools agent
    agent = create_openai_tools_agent(model, tools, prompt)

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Get the query from the command line
    query = " ".join(sys.argv[1:])
    snoop.pp(query)

    for step in agent_executor.iter({"input": query}):
        snoop.pp(step)
        if messages := step.get("messages"):
            for message in messages:
                print(message.content)
        elif intermediate_steps := step.get("intermediate_step"):
            allow_action_call = True
            for action, action_arguments in intermediate_steps:
                # TODO Check for ClearForTakeOff for this tool (later within
                # this context)
                # if not transparent_statement_for_tcb_eval_present(
                #     action,
                #     action_arguments,
                # ):
                if False:
                    allow_action_call = False
            if not allow_action_call:
                break


if __name__ == "__main__":
    main()
```

- We'll have TCB levels for tool use
- https://python.langchain.com/docs/use_cases/graph/semantic
- Need to patch llmproxy to do function calling on 2nd party
  - Look up `AgentExecutor` langchain class to determine protocol decoding train of thought so that we can Entity In The Middle (EITM) function calling / tool usage, We'll check SCITT for TCB ClearForTakeOff. The receipt the relying party is looking at to determine token issuance for workload identity.
  - https://github.com/search?q=repo%3Alangchain-ai/langchain%20AgentExecutor&type=code
  - Second result is the same class with `Iterator` suffix. Checked that to see what it is, searched for it and found docs.
  - https://github.com/search?q=repo%3Alangchain-ai/langchain%20AgentExecutorIterator&type=code
  - https://github.com/langchain-ai/langchain/blob/b617085af0d14468d5418176d4235229c2c12ffa/docs/docs/modules/agents/how_to/agent_iter.ipynb#L12
    - > Ask user if they want to continue
    - This looks like what we're looking for
- Active branch roll call for current system context (train of thought)
  - https://github.com/ietf-scitt/use-cases/pull/18
    - https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
  - https://github.com/pdxjohnny/scitt-api-emulator/tree/policy_engine
    - https://github.com/pdxjohnny/scitt-api-emulator/tree/policy_engine_cwt_rebase
      - This is most active branch, incorperates hopefully soon to be merged changed from https://github.com/scitt-community/scitt-api-emulator/pull/39
  - https://github.com/pdxjohnny/Multi-llms-Chatbot-CloudNative-LangChain/tree/scitt-validated-tool-use
  - https://github.com/pdxjohnny/litellm/tree/scitt-validated-tool-use
- Breakpointed litellm on where it dumps messages which contain tools to call.
  - `where/w` to stack trace to determine caller code paths, so we can insert the SCITT transparent statement ClearForTakeOff acquisition.
  - Within litellm proxy up the stack from here we should submit a manifest with context, tool to call, and inputs maybe to SCITT. If it passes the policy engine for this subject (schema for AI tool use, schema for this manifest URN of transparent statement).
  - If we get a transparent receipt (passes policy engine eval), then we've acquired our ClearForTakeOff.
  - litellm proxy will need workload identity

```
23:42:10 - LiteLLM:DEBUG: utils.py:831 - token_counter messages received: [{'content': 'You are a helpful assistant', 'role': 'system'}, {'content': 'What is the forecast for INTC?', 'role': 'user'}]
> /home/pdxjohnny/Documents/python/litellm/litellm/utils.py(3537)token_counter()
-> text = ""
> /home/pdxjohnny/Documents/python/litellm/litellm/utils.py(3537)token_counter()
-> text = ""
(Pdb) w
(Pdb)   /home/pdxjohnny/.local/.venv/bin/litellm(8)<module>()
-> sys.exit(run_server())
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/click/core.py(1157)__call__()
-> return self.main(*args, **kwargs)
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/click/core.py(1078)main()
-> rv = self.invoke(ctx)
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/click/core.py(1434)invoke()
-> return ctx.invoke(self.callback, **ctx.params)
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/click/core.py(783)invoke()
-> return __callback(*args, **kwargs)
  /home/pdxjohnny/Documents/python/litellm/litellm/proxy/proxy_cli.py(521)run_server()
-> uvicorn.run(app, host=host, port=port)  # run uvicorn
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/uvicorn/main.py(578)run()
-> server.run()
  /home/pdxjohnny/.local/.venv/lib64/python3.11/site-packages/uvicorn/server.py(61)run()
-> return asyncio.run(self.serve(sockets=sockets))
  /usr/lib64/python3.11/asyncio/runners.py(190)run()
-> return runner.run(main)
  /usr/lib64/python3.11/asyncio/runners.py(118)run()
-> return self._loop.run_until_complete(task)
  /home/pdxjohnny/Documents/python/litellm/litellm/utils.py(1769)async_success_handler()
-> complete_streaming_response = litellm.stream_chunk_builder(
  /home/pdxjohnny/Documents/python/litellm/litellm/main.py(3968)stream_chunk_builder()
-> response["usage"]["prompt_tokens"] = token_counter(
> /home/pdxjohnny/Documents/python/litellm/litellm/utils.py(3537)token_counter()
-> text = ""
```

- Thinking `async_success_handler()` is a good candidate for addition of our SCITT ClearForTakeOff acquisition
  - We can take this receipt and get a token from the relying party, and pass that token to the tool so that it has workload based identity for it's context

```diff
diff --git a/litellm/utils.py b/litellm/utils.py
index 2179a34c..f556cca2 100644
--- a/litellm/utils.py
+++ b/litellm/utils.py
@@ -1765,6 +1765,14 @@ class Logging:
             if result.choices[0].finish_reason is not None:  # if it's the last chunk
                 self.streaming_chunks.append(result)
                 # verbose_logger.debug(f"final set of received chunks: {self.streaming_chunks}")
+                try:
+                    # TODO SCITT submit statement and get receipt
+                except Exception as e:
+                    verbose_logger.debug(
+                        f"Error occurred building stream chunk: {traceback.format_exc()}"
+                    )
+                    complete_streaming_response = None
+
                 try:
                     complete_streaming_response = litellm.stream_chunk_builder(
                         self.streaming_chunks,
```

- https://console.cloud.intel.com/docs/guides/get_started.html


```
$ litellm --model gpt-3.5-turbo-1106 --debug --detailed_debug 2>&1 | tee logs.txt
$ grep 'tool_call = \[' logs.txt
00:33:53.62 .............. tool_call = [{'id': 'call_BwSpvV9FFUZ7whChqqYS3o4R', 'function': {'arguments': '{"ticker":"INTC"}', 'name': 'historical_stock_prices'}, 'type': 'function'}]
00:33:55.57 .............. tool_call = [{'id': 'call_K760oMiZiz6dsxTfUAsdnZSp', 'function': {'arguments': '{"historical_stock_prices":"[[\\"2024-03-22\\", 42...[\\"2024-03-23\\", 52.0], [\\"2024-03-24\\", 62.0]]"}', 'name': 'forecast'}, 'type': 'function'}]
00:34:15.93 .............. tool_call = [{'id': 'call_tE6e6A93Vkf77uiJo1bKjk1E', 'function': {'arguments': '{"ticker":"INTC"}', 'name': 'historical_stock_prices'}, 'type': 'function'}]
00:34:18.05 .............. tool_call = [{'id': 'call_k98HPuu2KRSyl2YTZS7bceef', 'function': {'arguments': '{"historical_stock_prices":"[[\\"2024-03-22\\", 42...[\\"2024-03-23\\", 52.0], [\\"2024-03-24\\", 62.0]]"}', 'name': 'forecast'}, 'type': 'function'}]
```

- TODO
  - [ ] To initiate bootstrapping statement is sent from notary to SCITT with upstream source URL and SHA of a repo.
    - [ ] Policy engine triggers workflows for subject
    - [ ] If all workflows triggered pass, statement is admitted.
      - [ ] Watch new transparent statements via federation (of git repos)
      - [ ] Run an instance of the policy engine which is standalone instance from the one running within SCITT
      - [ ] This policy engine is a standin for the CI/CD orchestrator within the forge.
      - [ ] We dispatch / trigger workflows based off same subject style routing to workflow `on` triggers.
  - [x] SCITT OIDC MUST be combined with policy engine `subject`. OIDC tokens should be issued of receipt chains
    - [x] `subject` of workload identity token is URN of transparent statement for `request.yml`
  - [ ] Tools as policy engine workflows
  - [ ] Rebase cwt onto federation and re-deploy (`did:jwk` changes)
  - [ ] Find the place in the llmproxy where raising exceptions for tool use / function calling can happen from. Currently our instrumentation is within logging code which doesn't stop ship if we need it to.
    - https://github.com/BerriAI/litellm/commit/e516f004da78136f00e414efc6af655ec7f11076
      - Workload identity for AI agents