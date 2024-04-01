## 2024-03-28 @pdxjohnny Engineering Logs

- Online cloning
  - from cattle to pets

**config.yaml**

```yaml
model_list:
  - model_name: gpt-3.5-turbo-1106
    litellm_params:
      model: gpt-3.5-turbo-1106

litellm_settings:
  callbacks: scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse
  callback_params_cls: scitt_validated_tool_use.LiteLLMSCITTValidatedToolUseParams
  callback_params:
    scrapi_instances:
    # - url: 'https://scitt.unstable.chadig.com'
    - url: 'http://localhost:8000'
```


```bash
export OPENAI_API_KEY=$(python -m keyring get $USER openai.api.key)
scitt-emulator server --workspace workspace/ --tree-alg CCF &
nodemon -e py --exec "clear; litellm --config config.yaml --debug --detailed_debug 2>&1 | tee logs.txt; test 1"
```

```
INFO:     Started server process [19685]
INFO:     Waiting for application startup.
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:1839 - Loaded config YAML (api_key and environment_variables are not shown):
{
  "model_list": [
    {
      "model_name": "gpt-3.5-turbo-1106",
      "litellm_params": {
        "model": "gpt-3.5-turbo-1106"
      }
    }
  ],
  "litellm_settings": {
    "callbacks": "scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse",
    "callback_params_cls": "scitt_validated_tool_use.LiteLLMSCITTValidatedToolUseParams",
    "callback_params": {
      "scrapi_instances": [
        {
          "url": "http://localhost:8000"
        }
      ]
    }
  }
}
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: utils.py:33 - value: scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: utils.py:33 - value: scitt_validated_tool_use.LiteLLMSCITTValidatedToolUseParams
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2040 - [94m Initialized Callbacks - [<scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse object at 0x7f5cf075ff10>] [0m
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2110 - [94m setting litellm.callback_params_cls=scitt_validated_tool_use.LiteLLMSCITTValidatedToolUseParams[0m
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2110 - [94m setting litellm.callback_params={'scrapi_instances': [{'url': 'http://localhost:8000'}]}[0m
[92m11:11:45 - LiteLLM Router:DEBUG[0m: router.py:1941 - Initializing OpenAI Client for gpt-3.5-turbo-1106, Api Base:None, Api Key:None
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - set cache: key: 4b7dcae1-73e3-43c8-9e6f-0d92c606e941_async_client; value: <openai.AsyncOpenAI object at 0x7f5cf0773290>
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - InMemoryCache: set_cache
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - set cache: key: 4b7dcae1-73e3-43c8-9e6f-0d92c606e941_client; value: <openai.OpenAI object at 0x7f5cf078ad10>
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - InMemoryCache: set_cache
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - set cache: key: 4b7dcae1-73e3-43c8-9e6f-0d92c606e941_stream_async_client; value: <openai.AsyncOpenAI object at 0x7f5cf0791b90>
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - InMemoryCache: set_cache
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - set cache: key: 4b7dcae1-73e3-43c8-9e6f-0d92c606e941_stream_client; value: <openai.OpenAI object at 0x7f5cf07a08d0>
[92m11:11:45 - LiteLLM:DEBUG[0m: caching.py:21 - InMemoryCache: set_cache
[92m11:11:45 - LiteLLM Router:DEBUG[0m: router.py:2094 - 
Initialized Model List [{'model_name': 'gpt-3.5-turbo-1106', 'litellm_params': {'model': 'gpt-3.5-turbo-1106'}, 'model_info': {'id': '4b7dcae1-73e3-43c8-9e6f-0d92c606e941'}}]
[92m11:11:45 - LiteLLM Router:DEBUG[0m: router.py:289 - Intialized router with Routing strategy: simple-shuffle

[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: utils.py:33 - INITIALIZING LITELLM CALLBACKS!
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <bound method Router.deployment_callback_on_failure of <litellm.router.Router object at 0x7f5cf459fb10>>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <bound method Router.deployment_callback_on_failure of <litellm.router.Router object at 0x7f5cf6caf150>>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse object at 0x7f5cf075ff10>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <litellm.proxy.hooks.parallel_request_limiter._PROXY_MaxParallelRequestsHandler object at 0x7f5cf590bb10>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <litellm.proxy.hooks.max_budget_limiter._PROXY_MaxBudgetLimiter object at 0x7f5cf590bb50>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <bound method ProxyLogging.response_taking_too_long_callback of <litellm.proxy.utils.ProxyLogging object at 0x7f5cf590ba90>>
[92m11:11:45 - LiteLLM:DEBUG[0m: utils.py:831 - callback: <litellm.proxy.hooks.cache_control_check._PROXY_CacheControlCheck object at 0x7f5cf590bb90>
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2790 - prisma client - None
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2794 - custom_db_client client - None
[92m11:11:45 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:2845 - custom_db_client client None. Master_key: None
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
[92m11:11:49 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:3131 - Request Headers: Headers({'host': 'localhost:4000', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'accept': 'application/json', 'content-type': 'application/json', 'user-agent': 'OpenAI/Python 1.14.2', 'x-stainless-lang': 'python', 'x-stainless-package-version': '1.14.2', 'x-stainless-os': 'Linux', 'x-stainless-arch': 'x64', 'x-stainless-runtime': 'CPython', 'x-stainless-runtime-version': '3.11.8', 'authorization': 'Bearer sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'x-stainless-async': 'false', 'content-length': '819'})
[92m11:11:49 - LiteLLM Proxy:DEBUG[0m: proxy_server.py:3137 - receiving data: {'messages': [{'content': 'You are a helpful assistant', 'role': 'system'}, {'content': 'What is the forecast for INTC?', 'role': 'user'}], 'model': 'gpt-3.5-turbo-1106', 'n': 1, 'stream': True, 'temperature': 0.0, 'tools': [{'type': 'function', 'function': {'name': 'forecast', 'description': 'forecast(historical_stock_prices: str) -> str - Make forecast given historical stock prices', 'parameters': {'type': 'object', 'properties': {'historical_stock_prices': {'type': 'string'}}, 'required': ['historical_stock_prices']}}}, {'type': 'function', 'function': {'name': 'historical_stock_prices', 'description': 'historical_stock_prices(ticker: str) -> str - Get the historical stock prices for a stock ticker', 'parameters': {'type': 'object', 'properties': {'ticker': {'type': 'string'}}, 'required': ['ticker']}}}], 'proxy_server_request': {'url': 'http://localhost:4000/chat/completions', 'method': 'POST', 'headers': {'host': 'localhost:4000', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'accept': 'application/json', 'content-type': 'application/json', 'user-agent': 'OpenAI/Python 1.14.2', 'x-stainless-lang': 'python', 'x-stainless-package-version': '1.14.2', 'x-stainless-os': 'Linux', 'x-stainless-arch': 'x64', 'x-stainless-runtime': 'CPython', 'x-stainless-runtime-version': '3.11.8', 'authorization': 'Bearer sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'x-stainless-async': 'false', 'content-length': '819'}, 'body': {'messages': [{'content': 'You are a helpful assistant', 'role': 'system'}, {'content': 'What is the forecast for INTC?', 'role': 'user'}], 'model': 'gpt-3.5-turbo-1106', 'n': 1, 'stream': True, 'temperature': 0.0, 'tools': [{'type': 'function', 'function': {'name': 'forecast', 'description': 'forecast(historical_stock_prices: str) -> str - Make forecast given historical stock prices', 'parameters': {'type': 'object', 'properties': {'historical_stock_prices': {'type': 'string'}}, 'required': ['historical_stock_prices']}}}, {'type': 'function', 'function': {'name': 'historical_stock_prices', 'description': 'historical_stock_prices(ticker: str) -> str - Get the historical stock prices for a stock ticker', 'parameters': {'type': 'object', 'properties': {'ticker': {'type': 'string'}}, 'required': ['ticker']}}}]}}}
[92m11:11:49 - LiteLLM Proxy:DEBUG[0m: utils.py:33 - Inside Proxy Logging Pre-call hook!
11:11:49.19 >>> Enter with block in LiteLLMSCITTValidatedToolUse.async_pre_call_hook in File "/home/pdxjohnny/Documents/python/litellm/scitt_validated_tool_use.py", line 348
11:11:49.19 .............. self = <scitt_validated_tool_use.LiteLLMSCITTValidatedToolUse object at 0x7f5cf075ff10>
11:11:49.19 .............. user_api_key_dict = UserAPIKeyAuth(token='AAAAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', user_role=None)
11:11:49.19 .............. cache = <litellm.caching.DualCache object at 0x7f5cf590ad90>
11:11:49.19 .............. data = {'messages': [{'content': 'You are a helpful assistant', 'role': 'system'}, {'content': 'What is the forecast for INTC?', 'role': 'user'}], 'model': 'gpt-3.5-turbo-1106', 'n': 1, 'stream': True, ...}
11:11:49.19 .............. len(data) = 9
11:11:49.19 .............. call_type = 'completion'
11:11:49.19  349 |             snoop.pp(data)
11:11:49.19 LOG:
11:11:49.42 .... data = {'messages': [{'content': 'You are a helpful assistant', 'role': 'system'},
11:11:49.42                           {'content': 'What is the forecast for INTC?', 'role': 'user'}],
11:11:49.42              'metadata': {'endpoint': 'http://localhost:4000/chat/completions',
11:11:49.42                           'headers': {'accept': 'application/json',
11:11:49.42                                       'accept-encoding': 'gzip, deflate',
11:11:49.42                                       'connection': 'keep-alive',
11:11:49.42                                       'content-length': '819',
11:11:49.42                                       'content-type': 'application/json',
11:11:49.42                                       'host': 'localhost:4000',
11:11:49.42                                       'user-agent': 'OpenAI/Python 1.14.2',
11:11:49.42                                       'x-stainless-arch': 'x64',
11:11:49.42                                       'x-stainless-async': 'false',
11:11:49.42                                       'x-stainless-lang': 'python',
11:11:49.42                                       'x-stainless-os': 'Linux',
11:11:49.42                                       'x-stainless-package-version': '1.14.2',
11:11:49.42                                       'x-stainless-runtime': 'CPython',
11:11:49.42                                       'x-stainless-runtime-version': '3.11.8'},
11:11:49.42                           'user_api_key': 'sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
11:11:49.42                           'user_api_key_alias': None,
11:11:49.42                           'user_api_key_metadata': {},
11:11:49.42                           'user_api_key_team_id': None,
11:11:49.42                           'user_api_key_user_id': None},
11:11:49.42              'model': 'gpt-3.5-turbo-1106',
11:11:49.42              'n': 1,
11:11:49.42              'proxy_server_request': {'body': {'messages': [{'content': 'You are a helpful '
11:11:49.42                                                                         'assistant',
11:11:49.42                                                              'role': 'system'},
11:11:49.42                                                             {'content': 'What is the '
11:11:49.42                                                                         'forecast for '
11:11:49.42                                                                         'INTC?',
11:11:49.42                                                              'role': 'user'}],
11:11:49.42                                                'model': 'gpt-3.5-turbo-1106',
11:11:49.42                                                'n': 1,
11:11:49.42                                                'stream': True,
11:11:49.42                                                'temperature': 0.0,
11:11:49.42                                                'tools': [{'function': {'description': 'forecast(historical_stock_prices: '
11:11:49.42                                                                                       'str) '
11:11:49.42                                                                                       '-> '
11:11:49.42                                                                                       'str '
11:11:49.42                                                                                       '- '
11:11:49.42                                                                                       'Make '
11:11:49.42                                                                                       'forecast '
11:11:49.42                                                                                       'given '
11:11:49.42                                                                                       'historical '
11:11:49.42                                                                                       'stock '
11:11:49.42                                                                                       'prices',
11:11:49.42                                                                        'name': 'forecast',
11:11:49.42                                                                        'parameters': {'properties': {'historical_stock_prices': {'type': 'string'}},
11:11:49.42                                                                                       'required': ['historical_stock_prices'],
11:11:49.42                                                                                       'type': 'object'}},
11:11:49.42                                                           'type': 'function'},
11:11:49.42                                                          {'function': {'description': 'historical_stock_prices(ticker: '
11:11:49.42                                                                                       'str) '
11:11:49.42                                                                                       '-> '
11:11:49.42                                                                                       'str '
11:11:49.42                                                                                       '- '
11:11:49.42                                                                                       'Get '
11:11:49.42                                                                                       'the '
11:11:49.42                                                                                       'historical '
11:11:49.42                                                                                       'stock '
11:11:49.42                                                                                       'prices '
11:11:49.42                                                                                       'for '
11:11:49.42                                                                                       'a '
11:11:49.42                                                                                       'stock '
11:11:49.42                                                                                       'ticker',
11:11:49.42                                                                        'name': 'historical_stock_prices',
11:11:49.42                                                                        'parameters': {'properties': {'ticker': {'type': 'string'}},
11:11:49.42                                                                                       'required': ['ticker'],
11:11:49.42                                                                                       'type': 'object'}},
11:11:49.42                                                           'type': 'function'}]},
11:11:49.42                                       'headers': {'accept': 'application/json',
11:11:49.42                                                   'accept-encoding': 'gzip, deflate',
11:11:49.42                                                   'authorization': 'Bearer '
11:11:49.42                                                                    'sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
11:11:49.42                                                   'connection': 'keep-alive',
11:11:49.42                                                   'content-length': '819',
11:11:49.42                                                   'content-type': 'application/json',
11:11:49.42                                                   'host': 'localhost:4000',
11:11:49.42                                                   'user-agent': 'OpenAI/Python 1.14.2',
11:11:49.42                                                   'x-stainless-arch': 'x64',
11:11:49.42                                                   'x-stainless-async': 'false',
11:11:49.42                                                   'x-stainless-lang': 'python',
11:11:49.42                                                   'x-stainless-os': 'Linux',
11:11:49.42                                                   'x-stainless-package-version': '1.14.2',
11:11:49.42                                                   'x-stainless-runtime': 'CPython',
11:11:49.42                                                   'x-stainless-runtime-version': '3.11.8'},
11:11:49.42                                       'method': 'POST',
11:11:49.42                                       'url': 'http://localhost:4000/chat/completions'},
11:11:49.42              'request_timeout': 600,
11:11:49.42              'stream': True,
11:11:49.42              'temperature': 0.0,
11:11:49.42              'tools': [{'function': {'description': 'forecast(historical_stock_prices: '
11:11:49.42                                                     'str) -> str - Make forecast given '
11:11:49.42                                                     'historical stock prices',
11:11:49.42                                      'name': 'forecast',
11:11:49.42                                      'parameters': {'properties': {'historical_stock_prices': {'type': 'string'}},
11:11:49.42                                                     'required': ['historical_stock_prices'],
11:11:49.42                                                     'type': 'object'}},
11:11:49.42                         'type': 'function'},
11:11:49.42                        {'function': {'description': 'historical_stock_prices(ticker: str) '
11:11:49.42                                                     '-> str - Get the historical stock '
11:11:49.42                                                     'prices for a stock ticker',
11:11:49.42                                      'name': 'historical_stock_prices',
11:11:49.42                                      'parameters': {'properties': {'ticker': {'type': 'string'}},
11:11:49.42                                                     'required': ['ticker'],
11:11:49.42                                                     'type': 'object'}},
11:11:49.42                         'type': 'function'}]}
```

- https://github.com/langchain-ai/langchain/blob/e1f10a697e48be33ec10cdb8f27a38dc6d504b12/libs/langchain/tests/unit_tests/agents/test_agent.py#L420-L667
- https://docs.litellm.ai/docs/proxy/model_management#add-a-new-model
  - > ```bash
    > curl -X POST "http://0.0.0.0:4000/model/new" \
    >      -H "accept: application/json" \
    >      -H "Content-Type: application/json" \
    >      -d '{ "model_name": "azure-gpt-turbo", "litellm_params": {"model": "azure/gpt-3.5-turbo", "api_key": "os.environ/AZURE_API_KEY", "api_base": "my-azure-api-base"} }'
    > ```