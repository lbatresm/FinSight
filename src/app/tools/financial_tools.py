"""
Quantitative finance tools for LLMs
"""

from typing import Annotated, List, Literal, Union

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from langgraph.prebuilt.chat_agent_executor import AgentState

@tool
def compound_interest(
    initial_balance: float,
    periodic_deposit: float,
    deposit_frequency: str,
    interest_rate: float,
    years: int):
    """
    Compound interest calculator tool.
    
    Args:
        initial_balance (float): Initial balance
        periodic_deposit (float): Periodic deposit made at end of period
        deposit_frequency (str): Deposit frequency ("weekly", "monthly", "annually")
        interest_rate (float): Annual interest rate (as percentage, eg: 7.5 para 7.5%)
        years (int): Number of years
    
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
        raise ValueError(f"Unvalid deposit frequency: {deposit_frequency}. Use 'weekly', 'monthly', o 'annually'")
    
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

        
def main():
    try:
        data = compound_interest(865, 123, "monthly", 7.5, 12)
        print("Resultados del cálculo de interés compuesto:")
        for year_data in data:
            print(f"Año {year_data['year']}: Balance = ${year_data['balance']:.2f}, "
                  f"initial_balance = ${year_data['initial_balance']:.2f}, "
                  f"Depósitos totales = ${year_data['total_deposit']:.2f}, "
                  f"Intereses totales = ${year_data['total_interest']:.2f}")
                  
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
