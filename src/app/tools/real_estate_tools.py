"""
Real Estate profitability computation tools for LLMs
"""

from ast import main
from typing import Annotated, List, Literal, Union, Optional
import numpy_financial as npf

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from langgraph.prebuilt.chat_agent_executor import AgentState

from pydantic import BaseModel, Field, computed_field, model_validator

# Create a class for tool function inputs. This introduces types and values validation.
class RealEstateProfitabilityInput(BaseModel):

    """Property parameters"""
    purchase_price: int = Field(...)
    autonomous_community: Literal[
        "Andalucía", "Aragón", "Asturias", "Islas Baleares", "Canarias",
        "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña",
        "Comunidad Valenciana", "Extremadura", "Galicia",
        "Comunidad de Madrid", "Murcia", "Navarra", "País Vasco",
        "La Rioja", "Ceuta", "Melilla"
    ] = Field(
        ...,
        description="The autonomous community determines the ITP"
    )
    notary_cost: int = Field(...)
    registry_cost: int = Field(...)
    renovation_cost: int = Field(...)
    agency_commission: int = Field(...)

    """Mortgage expenses"""
    mortgage_management_cost: int = Field(...)
    mortgage_appraisal_cost: int = Field(...)
    
    """Rental Income"""
    monthly_rental_income: int = Field(..., description="Monthly rental income expected")

    """Annual Operating Expenses"""
    maintenance_cost: Optional[float] = Field(
        None,
        description="Annual maintenance cost (default 10% of gross rental income)"
    )
    homeowners_association_fee: int = Field(
        ...,
        description="Monthly HOA/community fees (annualized)"
    )
    property_insurance: int = Field(
        ...,
        description="Annual property insurance premium"
    )
    mortgage_life_insurance: Optional[int] = Field(
        None,
        description="Annual mortgage life insurance premium"
    )
    has_rental_protection_insurance: Literal["Y", "N"] = Field(
        ...,
        description="Whether rental protection insurance is included"
    )
    rental_protection_insurance: Optional[float] = Field(
        None,
        description="Annual rental protection insurance premium"
    )
    property_tax_ibi: int = Field(
        ...,
        description="Annual property tax (IBI)"
    )
    vacancy_allowance: Optional[float] = Field(
        None,
        description="Annual vacancy allowance (default 5% of gross rental income)"
    )

    """Income tax (IRPF)"""
    annual_gross_salary: int = Field(
        ...,
        description="Property owner's annual gross salary"
    )
    irpf_tax: Optional[float] = Field(
        None,
        description="IRPF tax withholding percentage based on salary"
    )

    """Mortgage Financing"""
    loan_to_value_ratio: float = Field(
        ...,
        ge=0,
        le=1,
        description="Financed percentage expressed as decimal (e.g. 0.80 = 80% LTV)"
    )
    loan_term_years: int = Field(
        ...,
        ge=5,
        le=40,
        description="Mortgage term in years"
    )
    mortgage_type: Literal["fixed", "variable"] = Field(
        ...,
        description="Mortgage interest rate type"
    )
    mortgage_margin: Optional[float] = Field(
        None,
        description="Mortgage margin over Euribor for variable rate mortgages"
    )
    euribor_rate: Optional[float] = Field(
        None,
        description="Current Euribor rate for variable mortgages"
    )
    fixed_interest_rate: Optional[float] = Field(
        None,
        description="Fixed interest rate (annual percentage)"
    )
    variable_interest_rate: Optional[float] = Field(
        None,
        description="Variable interest rate (annual percentage)"
    )

    @model_validator(mode="after")
    def calculate_automatic_fields(self):
        # Calculate rental protection insurance if applicable
        if self.has_rental_protection_insurance == "Y":
            self.rental_protection_insurance = (
                self.monthly_rental_income * 12 * 0.05
            )

        # Calculate maintenance cost if not provided
        if self.maintenance_cost is None:
            self.maintenance_cost = 0.10 * self.monthly_rental_income * 12

        # Calculate vacancy allowance by default
        if self.vacancy_allowance is None:
            self.vacancy_allowance = 0.05 * 12 * self.monthly_rental_income

        # Calculate income tax bracket
        salary = self.annual_gross_salary
        if salary <= 12450:
            self.irpf_tax = 0.19
        elif salary <= 20199:
            self.irpf_tax = 0.24
        elif salary <= 35199:
            self.irpf_tax = 0.30
        elif salary <= 59999:
            self.irpf_tax = 0.37
        elif salary <= 299999:
            self.irpf_tax = 0.45
        else:
            self.irpf_tax = 0.47

        # Validate financing data consistency
        if self.mortgage_type == "variable":
            if (self.mortgage_margin is None or
                    self.euribor_rate is None):
                raise ValueError(
                    "If mortgage type is 'variable', "
                    "'mortgage_margin' and 'euribor_rate' "
                    "must be specified."
                )
            else:
                self.variable_interest_rate = (
                    self.mortgage_margin + self.euribor_rate
                )
        elif self.mortgage_type == "fixed":
            if self.fixed_interest_rate is None:
                raise ValueError(
                    "If mortgage type is 'fixed', "
                    "'fixed_interest_rate' must be specified."
                )
           

        return self


@tool(args_schema=RealEstateProfitabilityInput)
def real_estate_profitability_calculator(
    purchase_price: int,
    autonomous_community: Literal[
        "Andalucía", "Aragón", "Asturias", "Islas Baleares", "Canarias",
        "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña",
        "Comunidad Valenciana", "Extremadura", "Galicia",
        "Comunidad de Madrid", "Murcia", "Navarra", "País Vasco",
        "La Rioja", "Ceuta", "Melilla"
    ],
    notary_cost: int,
    registry_cost: int,
    renovation_cost: int,
    agency_commission: int,
    mortgage_management_cost: int,
    mortgage_appraisal_cost: int,
    monthly_rental_income: int,
    homeowners_association_fee: int,
    maintenance_cost: Optional[float],
    property_insurance: int,
    mortgage_life_insurance: Optional[int],
    has_rental_protection_insurance: Literal["Y", "N"],
    rental_protection_insurance: Optional[float],
    property_tax_ibi: int,
    vacancy_allowance: Optional[float],
    annual_gross_salary: int,
    irpf_tax: Optional[float],
    loan_to_value_ratio: float,
    loan_term_years: int,
    mortgage_type: Literal["fixed", "variable"],
    mortgage_margin: Optional[float],
    euribor_rate: Optional[float],
    fixed_interest_rate: Optional[float],
    variable_interest_rate: Optional[float]
) -> list:
    """
    Calculate comprehensive profitability and financial analysis for Spanish 
    real estate rental property investments.
    
    This tool performs exhaustive real estate investment analysis considering
    all acquisition costs, annual operating expenses, mortgage financing,
    Spanish taxes (IRPF and ITP by autonomous community), and generates
    key profitability metrics.
    
    Args:
        purchase_price: Property purchase price
        autonomous_community: Spanish autonomous community (determines ITP rate)
        notary_cost: Notary fees
        registry_cost: Property registry fees
        renovation_cost: Renovation/refurbishment costs
        agency_commission: Real estate agency commission
        mortgage_management_cost: Mortgage management fees
        mortgage_appraisal_cost: Property appraisal cost
        monthly_rental_income: Expected monthly rental income
        homeowners_association_fee: HOA/community fees (annualized)
        maintenance_cost: Annual maintenance cost (default 10% of gross rental income)
        property_insurance: Annual property insurance premium
        mortgage_life_insurance: Mortgage-linked life insurance
        has_rental_protection_insurance: Whether rental protection insurance included ("Y"/"N")
        rental_protection_insurance: Annual rental protection insurance premium
        property_tax_ibi: Annual property tax (IBI)
        vacancy_allowance: Vacancy allowance (default 5% of gross rental income)
        annual_gross_salary: Property owner's annual gross salary (for IRPF calculation)
        irpf_tax: IRPF tax bracket (automatically calculated)
        loan_to_value_ratio: Loan-to-value ratio (0.80 = 80% LTV)
        loan_term_years: Mortgage term in years
        mortgage_type: Mortgage type ("fixed" or "variable")
        mortgage_margin: Euribor margin for variable rate mortgages
        euribor_rate: Current Euribor rate for variable mortgages
        fixed_interest_rate: Fixed interest rate (for fixed mortgages)
        variable_interest_rate: Variable interest rate (calculated)
    
    Returns:
        List of dictionaries with categorized analysis:
        - Property Acquisition Analysis: Acquisition costs breakdown
        - Annual Income & Operating Expenses: Income and operating expenses
        - Mortgage Financing Details: Mortgage financing details
        - Profitability Metrics: Key profitability ratios
        - Cash Flow Analysis: Cash flow analysis
    
    Calculated Metrics:
        - Gross Rental Yield: Gross rental return on investment
        - Net Rental Yield: Net rental return (conservative and optimistic)
        - Cash-on-Cash Return: Return on invested capital
        - Net Operating Income (NOI): Net operating income
        - Annual Cash Flow: Annual cash flow after debt service
    
    Example:
        >>> result = real_estate_profitability_calculator(
        ...     purchase_price=200000,
        ...     autonomous_community="Comunidad de Madrid",
        ...     monthly_rental_income=1200,
        ...     loan_to_value_ratio=0.80,
        ...     mortgage_type="fixed",
        ...     fixed_interest_rate=3.5,
        ...     ...
        ... )
    """
 
    def calculate_itp(autonomous_community):
        ITP_BY_COMMUNITY = {
            "Andalucía": 7.0,
            "Aragón": 8.0,
            "Asturias": 8.0,
            "Islas Baleares": 8.0,
            "Canarias": 6.5,
            "Cantabria": 9.0,
            "Castilla-La Mancha": 9.0,
            "Castilla y León": 8.0,
            "Cataluña": 10.0,
            "Ceuta": 6.0,
            "Comunidad de Madrid": 6.0,
            "Comunidad Valenciana": 10.0,
            "Extremadura": 8.0,
            "Galicia": 8.0,
            "La Rioja": 7.0,
            "Melilla": 6.0,
            "Murcia": 8.0,
            "Navarra": 6.0,
            "País Vasco": 7.0,
        }

        if autonomous_community not in ITP_BY_COMMUNITY:
            raise ValueError(
                f"Autonomous community {autonomous_community} "
                "is not in the list."
            )
        
        itp_rate = ITP_BY_COMMUNITY[autonomous_community] / 100
        itp_to_pay = purchase_price * itp_rate
        return itp_rate, itp_to_pay

    # Compute ITP tax to pay
    itp_rate, itp_to_pay = calculate_itp(autonomous_community)
    # TODO: Try to compute this in class validators

    # Compute total acquisition cost (including mortgage management and appraisal costs)
    total_acquisition_cost = (
        purchase_price + itp_to_pay + notary_cost + registry_cost +
        renovation_cost + agency_commission + mortgage_management_cost + mortgage_appraisal_cost
    )

    # Compute annual gross rental income
    annual_gross_rental_income = monthly_rental_income * 12

    # Compute mortgage financing
    mortgage_loan_amount = purchase_price * loan_to_value_ratio
    down_payment = purchase_price - mortgage_loan_amount
    
    if mortgage_type == "variable":
        variable_interest_rate = variable_interest_rate / 100
        monthly_interest_rate = variable_interest_rate / 12
    elif mortgage_type == "fixed":
        fixed_interest_rate = fixed_interest_rate / 100
        monthly_interest_rate = fixed_interest_rate / 12

    # PMT = Payment: Compute periodic payment for loan based on
    # constant payments and constant interest rates
    number_of_payments = loan_term_years * 12  # Monthly payments
    monthly_mortgage_payment = abs(npf.pmt(
        monthly_interest_rate, number_of_payments, mortgage_loan_amount
    ))
    total_mortgage_payments = number_of_payments * monthly_mortgage_payment
    total_interest_over_life = total_mortgage_payments - mortgage_loan_amount
    annual_mortgage_payment = monthly_mortgage_payment * 12
    
    # Calculate first year interest expense
    # (more accurate than dividing total by years)
    remaining_principal_balance = mortgage_loan_amount
    first_year_interest_expense = 0
    
    for month in range(12):
        monthly_interest_expense = (
            remaining_principal_balance * monthly_interest_rate
        )
        principal_payment = (
            monthly_mortgage_payment - monthly_interest_expense
        )
        remaining_principal_balance -= principal_payment
        first_year_interest_expense += monthly_interest_expense

    # Compute annual operating expenses
    # Property management and maintenance (typically 8-12% of gross rental income)
    property_management_fee = 0.10 * annual_gross_rental_income
    
    total_annual_operating_expenses = (
        homeowners_association_fee + 
        maintenance_cost + 
        property_insurance + 
        (mortgage_life_insurance or 0) + 
        (rental_protection_insurance or 0) + 
        property_tax_ibi + 
        first_year_interest_expense + 
        (vacancy_allowance or 0)
    )

    # Compute net operating income (NOI)
    net_operating_income = annual_gross_rental_income - total_annual_operating_expenses
    
    # Calculate depreciation expense
    # (typically 2-3% of property value annually)
    annual_depreciation_expense = 0.025 * purchase_price
    
    # Tax calculation for rental income in Spain
    # Rental income is taxed at marginal IRPF rate,
    # with depreciation deductions allowed
    taxable_rental_income = (
        net_operating_income - annual_depreciation_expense
    )
    # Only tax positive income
    income_tax_on_rental = max(0, taxable_rental_income) * irpf_tax
    
    net_income_after_taxes = net_operating_income - income_tax_on_rental
    
    # Compute profitability metrics
    gross_rental_yield = annual_gross_rental_income / total_acquisition_cost
    net_rental_yield_conservative = (
        net_income_after_taxes / total_acquisition_cost
    )
    net_rental_yield_optimistic = (
        (net_income_after_taxes + (vacancy_allowance or 0) +
         maintenance_cost) / total_acquisition_cost
    )
    
    # Cash flow analysis
    # Principal payment = total mortgage payment - interest payment
    annual_principal_payment = (
        annual_mortgage_payment - first_year_interest_expense
    )
    
    # Cash flow = money remaining after paying mortgage principal
    annual_cash_flow_conservative = (
        net_income_after_taxes - annual_principal_payment
    )
    annual_cash_flow_optimistic = (
        annual_cash_flow_conservative +
        (vacancy_allowance or 0) + maintenance_cost
    )
    
    # ROCE (Return on Capital Employed)
    total_upfront_cost = total_acquisition_cost - mortgage_loan_amount
    roce_conservative = (
        annual_cash_flow_conservative / total_upfront_cost
    )
    roce_optimistic = (
        annual_cash_flow_optimistic / total_upfront_cost
    )
    
    # Return comprehensive analysis results
    return [
        {
            "analysis_category": "Property Acquisition Analysis",
            "purchase_price": purchase_price,
            "itp_tax_amount": itp_to_pay,
            "total_acquisition_cost": total_acquisition_cost,
            "down_payment": down_payment,
            "mortgage_loan_amount": mortgage_loan_amount
        },
        {
            "analysis_category": "Annual Income & Operating Expenses",
            "annual_gross_rental_income": annual_gross_rental_income,
            "first_year_interest_expense": first_year_interest_expense,
            "total_annual_operating_expenses": total_annual_operating_expenses,
            "net_operating_income": net_operating_income,
            "income_tax_on_rental": income_tax_on_rental,
            "net_income_after_taxes": net_income_after_taxes
        },
        {
            "analysis_category": "Mortgage Financing Details",
            "monthly_mortgage_payment": monthly_mortgage_payment,
            "annual_mortgage_payment": annual_mortgage_payment,
            "first_year_interest_expense": first_year_interest_expense, #Or yearly interest for fixed rates
            "annual_principal_payment": annual_principal_payment,
        },
        {
            "analysis_category": "Profitability Metrics",
            "gross_rental_yield": gross_rental_yield,
            "net_rental_yield_conservative": net_rental_yield_conservative,
            "net_rental_yield_optimistic": net_rental_yield_optimistic,
            "annual_cash_flow_conservative": annual_cash_flow_conservative,
            "annual_cash_flow_optimistic": annual_cash_flow_optimistic,
            "roce_conservative": roce_conservative,
            "roce_optimistic": roce_optimistic
        },
        {
            "analysis_category": "Cash Flow Analysis",
            "annual_cash_flow_conservative": annual_cash_flow_conservative,
            "annual_cash_flow_optimistic": annual_cash_flow_optimistic
        }
    ]