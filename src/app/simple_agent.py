"""
https://docs.langchain.com/oss/python/langchain/supervisor
"""


from langgraph.prebuilt import create_react_agent

from tools.financial_tools import compound_interest_calculator
from tools.real_estate_tools import real_estate_profitability_calculator
from utils import pretty_print_messages

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LANGCHAIN_API_KEY = os.environ['LANGCHAIN_API_KEY']
LANGSMITH_API_KEY = os.environ['LANGCHAIN_API_KEY']
LANGSMITH_TRACING = os.environ['LANGSMITH_TRACING']
LANGSMITH_ENDPOINT = os.environ['LANGSMITH_ENDPOINT']
LANGSMITH_PROJECT = os.environ['LANGSMITH_PROJECT']


financial_system_prompt = """
You are FinAssist, an intelligent financial subagent.

Your purpose is to help users understand and calculate financial concepts, including:
- Investments, interest, loans, savings, and financial planning
- Basic accounting and budgeting
- Economic and market concepts

You can use tools when numerical computation is required.

Guidelines:
- Be clear, concise, and accurate.
- When calculations are requested (like compound interest or ROI), call the appropriate tool.
- If the question is conceptual, explain it in plain language.
- Always provide the reasoning or formula behind any result.
- Never provide investment advice; only explain or calculate.

"""

financial_agent = create_react_agent(
    model = "openai:gpt-4o-mini",
    tools = [compound_interest_calculator],
    prompt = financial_system_prompt,
    name = "financial_agent",
)

real_estate_system_prompt = """
You are REA, an expert real estate investment analyst specialized in Spanish properties.

Your role:
- Analyze and explain property investment profitability in Spain.
- Use the `real_estate_profitability_calculator` tool whenever users mention purchase price, rent, mortgage, or yields.
- If details are missing (e.g. rate, salary, region), ask for them before calculating.

Guidelines:
1. **Be analytical:** When data is given, call the tool to compute metrics (yields, ROI, cash flow, etc.).
2. **Be clear:** Explain results step-by-step in simple terms after the tool output.
3. **Be specific:** Use Spanish tax and mortgage context (IRPF, ITP, etc.).
4. **Stay neutral:** Never give investment advice — only objective analysis.
5. **Formatting:** Present results clearly, grouped by:
   - Acquisition cost
   - Mortgage summary
   - Income & expenses
   - Profitability metrics
   - Interpretation

Example queries:
- “Calculate the yield of a flat in Madrid bought for 250,000 € and rented for 1,200 €/month.”
- “Compare profitability between Barcelona and Valencia.”
- “Estimate ROI for a 25-year mortgage at 3.5%.”

If computation is required, use the tool, then summarize findings clearly.
"""

real_estate_agent = create_react_agent(
    model = "openai:gpt-4o-mini",
    tools = [real_estate_profitability_calculator],
    prompt = real_estate_system_prompt,
    name = "real_estate_agent",
)


query1 = ("Can you tell me how much money will I get if I start with an initial balance of 2000 euros"
        "and invest 350 euros monthly for 8 years at an interest rate of 7.5%?")

query2 = ("Please compute the gross rental yield of a property in Madrid bought for 150,000 euros"
          "that needs a 30,000 euro renovation and will be rented for 1,000 euros monthly."
          "My yearly gross salary is 32,000 euros and I want the mortgage term to be 25 years,"
          "fixed rate at 2.5%.")

for chunk in financial_agent.stream(
    {"messages": [{"role": "user", "content": query1}]}
):
    pretty_print_messages(chunk)

# for chunk in real_estate_agent.stream(
#     {"messages": [{"role": "user", "content": query2}]}
# ):
#     pretty_print_messages(chunk)
