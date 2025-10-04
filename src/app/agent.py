import os
from dotenv import load_dotenv

# Langchain basics
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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
   return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Graph
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

# --- Run ---
messages = [
    sys_msg,  # Use SystemMessage!
    HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5."),
]

results = react_graph.invoke({"messages": messages}, config)

for r in results['messages']:
    r.pretty_print()

