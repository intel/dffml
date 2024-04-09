r"""
# DFFML LangGraph Agenic RAG

## Install Dependencies

```bash
python -m pip install langchain_community tiktoken langchain-openai langchainhub chromadb langchain langgraph langchain-community unstructured[markdown] cachier pgvector psycopg2-binary pymongo
```

## Usage

python dffml_docs.py "Please write a whitepaper on the data centric fail safe architecture for artificial general intelligence known as the Open Architecture. Please include how SCITT and federation help multiple instances communicate securely."

## References

- https://python.langchain.com/docs/integrations/vectorstores/pgvector/
- https://langchain-doc.readthedocs.io/en/latest/modules/indexes/chain_examples/vector_db_qa_with_sources.html
- https://github.com/pgvector/pgvector?tab=readme-ov-file#dockerq


LangGraph Retrieval Agent
Retrieval Agents are useful when we want to make decisions about whether to retrieve from an index.

To implement a retrieval agent, we simple need to give an LLM access to a retriever tool.

We can incorperate this into LangGraph.

Retriever
First, we index 3 blog posts.
"""
import sys
import pathlib
import snoop
import textwrap
import urllib.parse

snoop = snoop()
snoop.__enter__()

# https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/markdown.html#retain-elements
from langchain_community.document_loaders import UnstructuredMarkdownLoader


class UnstructuredMarkdownLoaderRetainElements(UnstructuredMarkdownLoader):
    def __init__(self, *args, **kwargs):
        kwargs["mode"] = "elements"
        super().__init__(*args, **kwargs)


# Path to root of dffml monorepo
DFFML_GIT_REPO_ROOT_PATH = pathlib.Path(__file__).parents[4]
DFFML_DOCS_PATH = DFFML_GIT_REPO_ROOT_PATH.joinpath("docs")

# https://langchain-doc.readthedocs.io/en/latest/modules/document_loaders/examples/directory_loader.html#change-loader-class
from langchain_community.document_loaders import DirectoryLoader
from cachier import cachier


@cachier(pickle_reload=False)
def load_docs_dffml():
    loader = DirectoryLoader(
        DFFML_DOCS_PATH.resolve(),
        glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoaderRetainElements,
    )
    docs = loader.load()
    return docs


docs = load_docs_dffml()
print("Number of dffml docs:", len(docs))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# TODO Embeddings for all links referenced in docs
"""
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]
snoop.pp(docs_list[0])

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs_list)
"""
import openai
from langchain_community.vectorstores.pgvector import PGVector

embeddings = OpenAIEmbeddings()

from langchain.retrievers import ParentDocumentRetriever
from langchain_community.storage import MongoDBStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# This text splitter is used to create the parent documents
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
# This text splitter is used to create the child documents
# It should create documents smaller than the parent
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# The storage layer for the parent documents
# docker run --name mongo-docstores-dffml-docs -d --restart=always -e MONGO_INITDB_ROOT_USERNAME=user -e MONGO_INITDB_ROOT_PASSWORD=password -v $HOME/docstores/mongo-data:/data/db:z -p 127.0.0.1:27017:27017 mongo:7
MONGODB_USERNAME = "user"
MONGODB_PASSWORD = "password"
# @{urllib.parse.quote_plus(socket_path)}
MONGODB_CONNECTION_STRING = f"mongodb://{urllib.parse.quote_plus(MONGODB_USERNAME)}:{urllib.parse.quote_plus(MONGODB_PASSWORD)}@localhost:27017"
MONGODB_DATABASE_NAME = "docs"
MONGODB_COLLECTION_NAME = "ai_alice_dffml"
docstore = MongoDBStore(
    connection_string=MONGODB_CONNECTION_STRING,
    db_name=MONGODB_DATABASE_NAME,
    collection_name=MONGODB_COLLECTION_NAME,
)

# docker run --name postgres-embeddings-dffml-docs -d --restart=always -e POSTGRES_DB=docs_ai_alice_dffml -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -v $HOME/embeddings/openai/var-lib-postgresq-data:/var/lib/postgresql/data:z -p 127.0.0.1:5432:5432 pgvector/pgvector:pg16
POSTGRESQL_CONNECTION_STRING = "postgresql+psycopg2://user:password@localhost:5432/docs_ai_alice_dffml"

# cachier does not work with PGVector @cachier(pickle_reload=False)
def load_retriever():
    # Add to vectorDB
    global docs
    vectorstore = PGVector(
        collection_name="rag-docs-ai-alice-dffml-for-parent-document-retriever",
        connection_string=POSTGRESQL_CONNECTION_STRING,
        embedding_function=embeddings,
        use_jsonb=True,
    )
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    # TODO If no docs from search then add, only uncomment next line on fresh db
    # retriever.add_documents(docs)
    return retriever

    # TODO If using Chroma chunk add_texts args into batches of 5,460
    # https://github.com/chroma-core/chroma/issues/1079
    vectorstore = Chroma(
        "rag-chroma",
        OpenAIEmbeddings(),
    )
    # retriever.add_documents(docs)
    return vectorstore

# TODO https://python.langchain.com/docs/integrations/retrievers/merger_retriever/
retriever = load_retriever()

"""
Then we create a retriever tool.
"""
from langchain.tools.retriever import create_retriever_tool

from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# base_retriever defined somewhere above...

compressor = LLMChainExtractor.from_llm(OpenAI(temperature=0))
compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=compression_retriever, llm=llm
)

# Set logging for the queries
import logging

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

"""
# TODO Recursive
query = "Open Architecture Alice"
docs = retriever_from_llm.get_relevant_documents(query)

first = True
docs_iter = docs.copy()
while first or (len(docs) != len(docs_iter)):
    first = False
    for doc in docs_iter:
        snoop.pp(doc.page_content, doc.metadata)
        if "parent_id" in doc.metadata:
            docs.append(docstore.mget([doc.metadata["parent_id"]]))
    docs_iter = docs.copy()
"""

# sys.exit(0)

retriever_tool_ai_alice_dffml_docs = create_retriever_tool(
    # retriever,
    retriever_from_llm,
    "retrieve_ai_alice_dffml_docs",
    "Search and return information about AI, Alice, and DFFML.",
)

tools = [retriever_tool_ai_alice_dffml_docs]

from langgraph.prebuilt import ToolExecutor

tool_executor = ToolExecutor(tools)

"""
Agent state
We will defined a graph.

A state object that it passes around to each node.

Our state will be a list of messages.

Each node in our graph will append to it.
"""

import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


"""
Nodes and Edges
We can lay out an agentic RAG graph like this:

The state is a set of messages
Each node will update (append to) state
Conditional edges decide which node to visit next
Screenshot 2024-02-14 at 3.43.58 PM.png
"""

import json
import operator
from typing import Annotated, Sequence, TypedDict

from langchain import hub
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.messages import BaseMessage, FunctionMessage
from langchain.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolInvocation
from langchain_core.output_parsers import StrOutputParser


@cachier(pickle_reload=False)
def cached_hub_pull(*args, **kwargs):
    return hub.pull(*args, **kwargs)


### Edges


def should_retrieve(state):
    """
    Decides whether the agent should retrieve more information or end the process.

    This function checks the last message in the state for a function call. If a function call is
    present, the process continues to retrieve information. Otherwise, it ends the process.

    Args:
        state (messages): The current state

    Returns:
        str: A decision to either "continue" the retrieval process or "end" it
    """

    print("---DECIDE TO RETRIEVE---")
    messages = state["messages"]
    last_message = messages[-1]

    # If there is no function call, then we finish
    if "function_call" not in last_message.additional_kwargs:
        print("---DECISION: DO NOT RETRIEVE / DONE---")
        return "end"
    # Otherwise there is a function call, so we continue
    else:
        print("---DECISION: RETRIEVE---")
        return "continue"


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the documents are relevant or not
    """

    print("---CHECK RELEVANCE---")

    # Data model
    class grade(BaseModel):
        """Binary score for relevance check."""

        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM
    model = ChatOpenAI(
        temperature=0, model="gpt-4-0125-preview", streaming=True
    )

    # Tool
    grade_tool_oai = convert_to_openai_tool(grade)

    # LLM with tool and enforce invocation
    llm_with_tool = model.bind(
        tools=[grade_tool_oai],
        tool_choice={"type": "function", "function": {"name": "grade"}},
    )

    # Parser
    parser_tool = PydanticToolsParser(tools=[grade])

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
        input_variables=["context", "question"],
    )

    # Chain
    chain = prompt | llm_with_tool | parser_tool

    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    score = chain.invoke({"question": question, "context": docs})

    grade = score[0].binary_score

    if grade == "yes":
        print("---DECISION: DOCS RELEVANT---")
        return "yes"

    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        print(grade)
        return "no"


### Nodes


def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response apended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    model = ChatOpenAI(
        temperature=0, streaming=True, model="gpt-4-0125-preview"
    )
    functions = [convert_to_openai_function(t) for t in tools]
    model = model.bind_functions(functions)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


@snoop
def retrieve(state):
    """
    Uses tool to execute retrieval.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with retrieved docs
    """
    print("---EXECUTE RETRIEVAL---")
    messages = state["messages"]
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(
            last_message.additional_kwargs["function_call"]["arguments"]
        ),
    )
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    function_message = FunctionMessage(content=str(response), name=action.tool)

    # We return a list, because this will get added to the existing list
    return {"messages": [function_message]}


def rewrite(state):
    """
    Transform the query to produce a better question.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with re-phrased question
    """

    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    msg = [
        HumanMessage(
            content=f""" \n
    Look at the input and try to reason about the underlying semantic intent / meaning. \n
    Here is the initial question:
    \n ------- \n
    {question}
    \n ------- \n
    Formulate an improved question: """,
        )
    ]

    # Grader
    model = ChatOpenAI(
        temperature=0, model="gpt-4-0125-preview", streaming=True
    )
    response = model.invoke(msg)
    return {"messages": [response]}


def generate(state):
    """
    Generate answer

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    # Prompt
    prompt = cached_hub_pull("rlm/rag-prompt")

    # LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True)

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}


"""
Graph
Start with an agent, call_model
Agent make a decision to call a function
If so, then action to call tool (retriever)
Then call agent with the tool output added to messages (state)
"""

from langgraph.graph import END, StateGraph

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("rewrite", rewrite)  # retrieval
workflow.add_node("generate", generate)  # retrieval
# Call agent node to decide to retrieve or not
workflow.set_entry_point("agent")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    should_retrieve,
    {
        # Call tool node
        "continue": "retrieve",
        "end": END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
    {
        "yes": "generate",
        "no": "rewrite",
    },
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

# Compile
app = workflow.compile()
import pprint
from langchain_core.messages import HumanMessage

query = " ".join(sys.argv[1:])
if not query.strip():
    query = "Please write a whitepaper on the data centric fail safe architecture for artificial general intelligence known as the Open Architecture. Please include how SCITT and federation help multiple instances communicate securely."

inputs = {
    "messages": [
        HumanMessage(
            content=query,
        )
    ]
}

# for doc in vectorstore.similarity_search_with_score("alice"):
#     snoop.pp(doc)

# sys.exit(0)
import rich.console
import rich.markdown

rich_console = rich.console.Console(width=80)

chat_log = []

for output in app.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
        for message in value.get("messages", []):
            content = message
            if hasattr(message, "content"):
                content = message.content
            rich_console.print(rich.markdown.Markdown(content))
            chat_log.append(content)
    pprint.pprint("\n---\n")

import pathlib
pathlib.Path("~/chat-log.txt").expanduser().write_text("\n\n".join(chat_log))
