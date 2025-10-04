import os
import asyncio
from dotenv import load_dotenv

# Langchain basics
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, trim_messages

# Langgraph basics
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState


# Memory
from langgraph.checkpoint.memory import InMemorySaver

# Messages as state and reducers
from typing import Annotated, List

# Modules
import tools.math as math
from utils import format_messages, reduce_list

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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [math.calculator_wstate]


# Short term memory
checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")



# Initialize built-in react agent abstraction
agent = create_react_agent(
    llm,
    tools,
    prompt = sys_msg,
    state_schema=math.CalcState
).with_config({"recursion_limit":20}) # Limits number of steps agent will run

# Print graph mermaid diagram in png
output_path = os.path.join("src", "app", "graph_mermaid_image.png")
with open(output_path, "wb") as f:
        f.write(agent.get_graph(xray=True).draw_mermaid_png())

# ---- Run ----
result = agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":"What is 3.1 * 4.2?"
            }
        ]
    }
)

format_messages(result["messages"])