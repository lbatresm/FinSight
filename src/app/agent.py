import os
import asyncio
from dotenv import load_dotenv

# Langchain basics
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, trim_messages

# Langgraph basics
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

# Memory
from langgraph.checkpoint.memory import InMemorySaver

# Messages as state and reducers
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages

# Trim and filter messages
from langchain_core.messages import trim_messages

# Modules
import tools.math as math

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
CO_API_KEY = os.environ['CO_API_KEY']
LANGCHAIN_API_KEY = os.environ['LANGCHAIN_API_KEY']

# Set langsmith for tracing
LANGSMITH_API_KEY = os.environ['LANGSMITH_API_KEY']
LANGSMITH_TRACING = os.environ['LANGSMITH_TRACING']
LANGSMITH_ENDPOINT = os.environ['LANGSMITH_ENDPOINT']
LANGSMITH_PROJECT = os.environ['LANGSMITH_PROJECT']


# Configurations
tools = [math.add, math.subtract, math.multiply, math.divide]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# Short term memory
checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Use messages as state with add reduce
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# Node
def assistant(state: State):
    messages = trim_messages(state["messages"],
        max_tokens=500, 
        strategy="last", 
        token_counter=ChatOpenAI(model="gpt-4o"), 
        allow_partial=False,
    )
    return {"messages": [llm_with_tools.invoke(messages)]}

# ---- Graph ----
builder = StateGraph(State)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile(checkpointer=checkpointer)

# ---- Run ----
mode = "debug" # Choose streaming or debug

messages = [
        sys_msg,  # Use SystemMessage!
        HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5."),
    ]

if mode == "debug":
    def main():
        results = react_graph.invoke({"messages": messages}, config)
        for r in results['messages']:
            r.pretty_print()
elif mode == "streaming":
    async def main():
        node_to_stream = "assistant"

        async for event in react_graph.astream_events(
            {"messages": messages}, 
            config, 
            version="v2"
        ):
            if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node", "") == node_to_stream:
                data = event["data"]
                print(data["chunk"].content, end="")


if __name__ == "__main__":
    if mode == "debug":
        main()
    elif mode == "streaming":
        asyncio.run(main()) #coroutine