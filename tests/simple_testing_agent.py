from dotenv import load_dotenv
import os
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

import sys
from pathlib import Path

# Ensure project root is on sys.path so that 'src' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.app.tools.financial_tools as ft

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

# Testing agent
tools=[ft.compound_interest_calculator]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
system_prompt = "You are a helpful agent that solves financial questions using tools."

agent = create_react_agent(
    model,
    tools,
    prompt=system_prompt,
)

question = "Can you tell me how much money will I get if I start with an initial balance of 100 euros, and invest 50 euros monthly for 3 years at an interest rate of 8%?"

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()