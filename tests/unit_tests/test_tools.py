# test_tools.py

from src.app.tools.financial_tools import compound_interest_calculator
from src.app.tools.real_estate_tools import real_estate_profitability_calculator

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


def test_real_estate_profitability_calculator():
    
    test_data = {
        "purchase_price": 150000,
        "autonomous_community": "Comunidad de Madrid",
        "notary_cost": 500,
        "registry_cost": 250,
        "renovation_cost": 30000,
        "agency_commission": 3000,
        "mortgage_management_cost": 300,
        "mortgage_appraisal_cost": 200,
        "monthly_rental_income": 1000,
        "homeowners_association_fee": 600,  # annualized
        "maintenance_cost": None, # Will be calculated automatically as 10% rental income
        "property_insurance": 100,
        "mortgage_life_insurance": 150,
        "has_rental_protection_insurance": "Y",
        "rental_protection_insurance": None,  # Will be calculated automatically
        "property_tax_ibi": 160,
        "vacancy_allowance": None,  # Will be calculated automatically (5%)
        "annual_gross_salary": 38928,
        "irpf_tax": None,  # Will be calculated automatically
        "loan_to_value_ratio": 0.80,  # 80% LTV
        "loan_term_years": 25,
        "mortgage_type": "fixed",
        "mortgage_margin": None,
        "euribor_rate": None,
        "fixed_interest_rate": 2.5,
        "variable_interest_rate": None
    }
    
    # Execute the calculation
    result = real_estate_profitability_calculator.invoke(test_data)
    
    # Verify result structure
    assert isinstance(result, list)
    assert len(result) == 5  # Should have 5 analysis categories
    
    # Extract categories for easier testing
    categories = {item["analysis_category"]: item for item in result}
    
    # Test Property Acquisition Analysis
    acquisition = categories["Property Acquisition Analysis"]
    assert acquisition["purchase_price"] == 150000
    assert acquisition["itp_tax_amount"] == 9000  # 6% of purchase price in Madrid
    assert acquisition["total_acquisition_cost"] == 193250
    assert acquisition["down_payment"] == 30000  # 20% of purchase price (80% LTV)
    assert acquisition["mortgage_loan_amount"] == 120000  # 80% of 250000
    
    # Test Annual Income & Operating Expenses
    income_expenses = categories["Annual Income & Operating Expenses"]
    assert income_expenses["annual_gross_rental_income"] == 12000  # 1000 * 12
    assert int(income_expenses["first_year_interest_expense"]) == 2960
    assert int(income_expenses["total_annual_operating_expenses"]) == 6370
    assert round(income_expenses["net_operating_income"], 0) == 5630
    assert round(income_expenses["income_tax_on_rental"], 0) == 696
    assert round(income_expenses["net_income_after_taxes"], 0) == 4934

    # Test Mortgage Financing Details
    mortgage = categories["Mortgage Financing Details"]
    assert int(mortgage["monthly_mortgage_payment"]) == 538
    assert int(mortgage["annual_mortgage_payment"]) ==  6460
    assert int(mortgage["first_year_interest_expense"]) == 2960
    assert int(mortgage["annual_principal_payment"]) == 3500
    
    # Test Profitability Metrics
    profitability = categories["Profitability Metrics"]
    assert profitability["gross_rental_yield"] > 0
    
    # Test Cash Flow Analysis
    cash_flow = categories["Cash Flow Analysis"]
    assert "annual_cash_flow_conservative" in cash_flow
    assert "annual_cash_flow_optimistic" in cash_flow
    
    # Verify specific calculations
    # Gross rental yield should be 8% (12000/150000)
    assert abs(profitability["gross_rental_yield"] - 0.08) < 0.001
    
    # ITP tax should be 6% for Madrid
    assert acquisition["itp_tax_amount"] == 9000
    
    # Down payment should be 20% (1 - 0.80 LTV)
    assert acquisition["down_payment"] == 30000
    
    print("\n[PASS] All real estate profitability calculator tests passed!")
    print(f"Gross Rental Yield: {profitability['gross_rental_yield']:.2%}")
    print(f"Monthly Mortgage Payment: €{mortgage['monthly_mortgage_payment']:.2f}")
    print(f"Net Operating Income: €{income_expenses['net_operating_income']:.2f}")


def test_real_estate_profitability_calculator_variable_mortgage():
    """Test the calculator with variable rate mortgage."""
    
    test_data = {
        "purchase_price": 200000,
        "autonomous_community": "Cataluña",
        "notary_cost": 1200,
        "registry_cost": 600,
        "renovation_cost": 8000,
        "agency_commission": 4000,
        "mortgage_management_cost": 600,
        "mortgage_appraisal_cost": 300,
        "monthly_rental_income": 1000,
        "homeowners_association_fee": 960,  # 80€/month annualized
        "maintenance_cost": None,  # Will be calculated automatically
        "property_insurance": 250,
        "mortgage_life_insurance": 500,
        "has_rental_protection_insurance": "N",
        "rental_protection_insurance": None,
        "property_tax_ibi": 1000,
        "vacancy_allowance": None,
        "annual_gross_salary": 35000,
        "irpf_tax": None,
        "loan_to_value_ratio": 0.75,  # 75% LTV
        "loan_term_years": 20,
        "mortgage_type": "variable",
        "mortgage_margin": 1.5,
        "euribor_rate": 2.0,
        "fixed_interest_rate": None,
        "variable_interest_rate": None  # Will be calculated (1.5 + 2.0 = 3.5%)
    }
    
    result = real_estate_profitability_calculator.invoke(test_data)
    
    # Verify result structure
    assert isinstance(result, list)
    assert len(result) == 5
    
    # Extract categories
    categories = {item["analysis_category"]: item for item in result}
    
    # Test specific values for variable mortgage
    acquisition = categories["Property Acquisition Analysis"]
    assert acquisition["purchase_price"] == 200000
    assert acquisition["itp_tax_amount"] == 20000  # 10% for Cataluña
    assert acquisition["down_payment"] == 50000  # 25% of 200000
    assert acquisition["mortgage_loan_amount"] == 150000  # 75% of 200000
    
    # Test profitability metrics
    profitability = categories["Profitability Metrics"]
    assert profitability["gross_rental_yield"] == 0.06  # 12000/200000 = 6%
    
    print("\n[PASS] Variable mortgage test passed!")
    print(f"ITP Tax (Cataluna): {acquisition['itp_tax_amount']}")
    print(f"Gross Rental Yield: {profitability['gross_rental_yield']:.2%}")
