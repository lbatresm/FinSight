import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Langchain basics
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, trim_messages
from langchain_core.tools import tool

# Langgraph basics
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

# Memory
from langgraph.checkpoint.memory import InMemorySaver

# Messages as state and reducers
from typing import Annotated, List

# Modules
from state import DeepAgentState
# from tools.math_tools import
from utils import format_messages, show_prompt
from prompts import RESEARCHER_INSTRUCTIONS, WRITE_TODOS_DESCRIPTION, TODO_USAGE_INSTRUCTIONS, FILE_USAGE_INSTRUCTIONS, SUBAGENT_USAGE_INSTRUCTIONS
from tools.todo_tools import write_todos, read_todos
from tools.file_tools import ls, read_file, write_file
from tools.task_tool import _create_task_tool
from tools.research_tools import tavily_search, get_today_str


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


# # ----Mock data----
# # Mock search result
# search_result = """The Model Context Protocol (MCP) is an open standard protocol developed 
# by Anthropic to enable seamless integration between AI models and external systems like 
# tools, databases, and other services. It acts as a standardized communication layer, 
# allowing AI models to access and utilize data from various sources in a consistent and 
# efficient manner. Essentially, MCP simplifies the process of connecting AI assistants 
# to external services by providing a unified language for data exchange. """

# # Mock search tool
# @tool(parse_docstring=True)
# def web_search(
#     query: str,
# ):
#     """Search the web for information on a specific topic.

#     This tool performs web searches and returns relevant results
#     for the given query. Use this when you need to gather information from
#     the internet about any topic.

#     Args:
#         query: The search query string. Be specific and clear about what
#                information you're looking for.

#     Returns:
#         Search results from search engine.

#     Example:
#         web_search("machine learning applications in healthcare")
#     """
#     return search_result

# # Add mock research instructions
# SIMPLE_RESEARCH_INSTRUCTIONS = """You are a researcher. Research the topic provided to you. If you need to do a web search, call the web_search tool once and use the result provided to answer the user"""

# ----Code----
# Configurations
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# Limits
max_concurrent_research_units = 3
max_researcher_iterations = 3

# Tools
built_in_tools = [ls, read_file, write_file, write_todos, read_todos]
sub_agent_tools = [tavily_search]

# Create research subagent
research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
    "prompt": RESEARCHER_INSTRUCTIONS.format(date=get_today_str),
    "tools": ["tavily_search"],
}

# Create task tool to delegate tasks to sub-agents
task_tool = _create_task_tool(
    sub_agent_tools, [research_sub_agent], model, DeepAgentState
)

# Delegation tools
delegation_tools = [task_tool]
all_tools = sub_agent_tools + built_in_tools + delegation_tools # search available to main agent for trivial cases

# Build prompt for all subagents
SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
    max_concurrent_research_units=max_concurrent_research_units,
    max_researcher_iterations=max_researcher_iterations,
    date=get_today_str,
)
# show_prompt(SUBAGENT_INSTRUCTIONS)

# Build prompt for main agent
INSTRUCTIONS = (
    "# TODO MANAGEMENT\n"
    + TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# FILE SYSTEM USAGE\n"
    + FILE_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# SUB-AGENT DELEGATION\n"
    + SUBAGENT_INSTRUCTIONS
)
# show_prompt(INSTRUCTIONS)

# Initialize built-in react agent abstraction
agent = create_react_agent(
    model, 
    all_tools,
    prompt=INSTRUCTIONS,
    state_schema=DeepAgentState,
).with_config({"recursion_limit": 20})

# Print graph mermaid diagram in png
# output_path = os.path.join("src", "app", "graph_mermaid_image.png")
# with open(output_path, "wb") as f:
#         f.write(agent.get_graph(xray=True).draw_mermaid_png())

# ---- Run ----
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Give me an overview of Model Context Protocol (MCP).",
                "files": {},
                "todos": [],
            }
        ],
    }
)
format_messages(result["messages"])
