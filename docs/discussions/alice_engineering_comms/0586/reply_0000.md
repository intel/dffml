## 2024-04-06 @pdxjohnny Engineering Logs

- https://python.langchain.com/docs/integrations/tools/
  - https://python.langchain.com/docs/integrations/tools/chatgpt_plugins/
- https://huggingface.co/docs/transformers/v4.29.0/en/custom_tools
  - https://huggingface.co/docs/transformers/v4.29.0/en/transformers_agents#a-curated-set-of-tools
  - https://python.langchain.com/docs/integrations/tools/gradio_tools/
- https://langchain-doc.readthedocs.io/en/latest/modules/chat/examples/agent.html
- https://edge-runtime.vercel.app/features/available-apis#addressing-the-runtime
- https://github.com/wintercg/admin/blob/main/charter.md
- https://v8.dev/blog/sandbox
  - Policy engine is already python, can embed V8, just missing docker actions

![chaos-for-the-chaos-god](https://github.com/intel/dffml/assets/5950433/636969a1-1f0f-4c96-8812-f10fa403e79c)

- https://python.langchain.com/docs/langgraph/
  - https://python.langchain.com/docs/langgraph/#define-the-graph
    - Policy engine workflows as langgraph
- https://github.com/langchain-ai/langgraph/blob/main/examples/time-travel.ipynb
- https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_adaptive_rag_local.ipynb
- https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_agentic_rag.ipynb
- https://github.com/langchain-ai/langgraph/pull/268
  - Failsafe
- https://github.com/langchain-ai/langgraph/blob/main/examples/llm-compiler/LLMCompiler.ipynb
  - > LLMCompiler is an agent architecture designed to speed up the execution of agentic tasks by eagerly-executed tasks within a DAG. It also saves costs on redundant token usage by reducing the number of calls to the LLM.
    > - The planner output parsing format is fragile if your function requires more than 1 or 2 arguments. We could make it more robust by using streaming tool calling.
    > - Variable substitution is fragile in the example above. It could be made more robust by using a fine-tuned model and a more robust syntax (using e.g., Lark or a tool calling schema)
    > - The state can grow quite long if you require multiple re-planning runs. To handle, you could add a message compressor once you go above a certain token limit.
- https://python.langchain.com/docs/integrations/tools/ddg/
  - Duck Duck Go search
- https://lilianweng.github.io/posts/2023-06-23-agent/#component-one-planning
  - Mentions chain of thoughts, we want to explore more into graph of thoughts
- https://langchain-doc.readthedocs.io/en/latest/modules/indexes/chain_examples/graph_qa.html
- https://langchain-doc.readthedocs.io/en/latest/modules/indexes/examples/hyde.html
- https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/readthedocs_documentation.html
- https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/directory_loader.html
- https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/markdown.html#retain-elements
- https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/copypaste.html
- https://langchain-doc.readthedocs.io/en/latest/modules/indexes/chain_examples/chat_vector_db.html

```
docker run --rm -e POSTGRES_HOST_AUTH_METHOD=trust -v $HOME/embeddings/openai/var-lib-postgresq-data:/var/lib/postgresql/data:z pgvector/pgvector:pg16
```

- https://github.com/chroma-core/chroma/issues/1079
  - Hit this
- Text-embedding-ada-002-v2
  - API requests: 751
  - Tokens: 1,675,736
  - Cost: $0.17
- TODO
  - [ ] https://github.com/intel/dffml/pull/1550