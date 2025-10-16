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

    # FOR TESTS
# def main():
#     try:
#         data = compound_interest_calculator(865, 123, "monthly", 7.5, 12)
#         print("Resultados del cálculo de interés compuesto:")
#         for year_data in data:
#             print(f"Año {year_data['year']}: Balance = ${year_data['balance']:.2f}, "
#                   f"initial_balance = ${year_data['initial_balance']:.2f}, "
#                   f"Depósitos totales = ${year_data['total_deposit']:.2f}, "
#                   f"Intereses totales = ${year_data['total_interest']:.2f}")
                  
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     main()
