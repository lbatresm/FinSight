# test_tools.py

from src.app.tools.financial_tools import compound_interest_calculator

def test_compound_interest():
    data = compound_interest_calculator.invoke({
        "initial_balance": 865,
        "periodic_deposit": 123,
        "deposit_frequency": "monthly",
        "interest_rate": 7.5,
        "years": 12
    })
    final_balance = data[-1]["balance"]
    assert round(final_balance, 2) == 30711.21
