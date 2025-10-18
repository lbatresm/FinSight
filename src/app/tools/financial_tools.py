"""
Quantitative finance tools for LLMs
"""

from typing import Annotated, List, Literal, Union

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from langgraph.prebuilt.chat_agent_executor import AgentState

from pydantic import BaseModel, Field

# Create a class for tool function inputs. This introduces types and values validation.
class CompoundInterestInput(BaseModel):
    """Input for compound interest calculator."""
    initial_balance: float = Field(..., description = "Initial deposit or balance in the account.")
    periodic_deposit: float = Field(..., description = "Deposit made at the end of each period")
    deposit_frequency: Literal["weekly", "monthly", "annually"] = Field(default="annually",
        description="Deposit frequency: 'weekly', 'monthly', or 'annually'")
    interest_rate: float = Field(..., description="Annual interest rate as a percentage (e.g., 7.5 for 7.5%)")
    years: int = Field(..., description="Number of years to calculate")
    
@tool(args_schema=CompoundInterestInput)
def compound_interest_calculator(
    initial_balance: float,
    periodic_deposit: float,
    interest_rate: float,
    years: int,
    deposit_frequency: str = "annually") -> list:
    """
    Compound interest calculator tool.
    
    Args:
        initial_balance (float): Initial balance
        periodic_deposit (float): Periodic deposit made at end of period
        interest_rate (float): Annual interest rate (as percentage, eg: 7.5 para 7.5%)
        years (int): Number of years
        deposit_frequency (str): Deposit frequency ("weekly", "monthly", "annually")

    Returns:
        list: List of dictionaries with yearly data
    
    Example:
        compound_interest(1000, 100, "monthly", 7.5, 5)
    """
    # Convert % interest rate to decimal
    interest_rate = interest_rate / 100
    
    if deposit_frequency == "weekly":
        n = 52
    elif deposit_frequency == "monthly":
        n = 12
    elif deposit_frequency == "annually":
        n = 1
    else:
        raise ValueError(f"Invalid deposit frequency: {deposit_frequency}. Use 'weekly', 'monthly', or 'annually'")
    
    # cf = (initial_balance * (1 + interest_rate / n) ** (n * years)
    # + periodic_deposit * (((1 + interest_rate / n) ** (n * years) - 1) / (interest_rate / n)))

    data = []
    acc_deposit = 0
    acc_interest = 0
    balance = initial_balance

    for year in range(1, years + 1):
        for period in range (n): # Each period, we make a deposit and apply interests over them
            interest = balance * (interest_rate / n)
            balance = balance + periodic_deposit + interest 
            acc_deposit += periodic_deposit
            acc_interest += interest

        data.append({
            "year": year,
            "initial_balance" : initial_balance,
            "total_deposit" : acc_deposit,
            "total_interest" : acc_interest,
            "balance" : balance
        })
    
    return data


