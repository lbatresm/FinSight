"""
Real Estate profitability computation tools for LLMs
"""

from re import A
from typing import Annotated, List, Literal, Union, Optional

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
    autonomous_community: Literal["Andalucía", "Aragón", "Asturias", "Islas Baleares", "Canarias",
    "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña", "Comunidad Valenciana", 
    "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja",
    "Ceuta", "Melilla"
    ] = Field(..., description = "The autonomous community determines the ITP")
    notary_cost: int = Field(...)
    registry_cost: int = Field(...)
    renovation_cost: int = Field(...)
    agency_commission: int = Field(...)

    """Mortgage expenses"""
    mortgage_management_cost: int = Field(...)
    mortgage_appraisal_cost: int = Field(...)
    
    """Rental"""
    monthly_rent: int = Field(...)

    """Annual expenses estimation"""
    community_fee: int = Field(...)
    home_insurance: int = Field(...)
    mortgage_life_insurance: Optional[int] # Optional field
    has_non_payment_insurance: Literal ["Y", "N"] = Field(..., )
    non_payment_insurance: Optional[float] = Field(None, description="Amount of non-payment insurance (if applicable)")
    ibi_tax: int = Field(...)
    vacant_periods: Optional[float] = Field(None, description="Vacancy margin (default 5%)")

    """Income tax (IRPF)"""
    annual_gross_salary: int = Field(..., description="Property owner's annual gross salary")
    irpf_tax: Optional[float] = Field(None, description="IRPF tax withholding percentage based on salary")

    """Financing"""
    financed_percentage: float = Field(..., ge=0, le=1, description="Financed percentage expressed as decimal (e.g. 0.90 = 90%)")
    loan_term_years: int = Field(..., ge=5, le=40)
    mortgage_type: Literal["fixed", "variable"] = Field(..., description="Mortgage type")
    mortgage_spread: Optional[float] = Field(None, description="Mortgage spread, if variable")
    euribor: Optional[float] = Field(None, description="Euribor, if variable")
    fixed_interest_rate: Optional[float] = Field(None, description="Fixed interest rate, if fixed")

    @model_validator(mode="after")
    def calculate_automatic_fields(self):
        # Calculate non-payment insurance if applicable
        if self.has_non_payment_insurance == "Y":
            self.non_payment_insurance = self.monthly_rent * 12 * 0.05

        # Calculate vacant periods by default
        if self.vacant_periods is None:
            self.vacant_periods = 0.05 * 12 * self.monthly_rent

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
            if self.mortgage_spread is None or self.euribor is None:
                raise ValueError(
                    "If mortgage type is 'variable', 'mortgage_spread' and 'euribor' must be specified."
                )
        elif self.mortgage_type == "fixed":
            if self.fixed_interest_rate is None:
                raise ValueError(
                    "If mortgage type is 'fixed', 'fixed_interest_rate' must be specified."
                )

        return self


@tool(args_schema=RealEstateProfitabilityInput)
def real_estate_profitability_calculator(
    purchase_price: int,
    autonomous_community: Literal["Andalucía", "Aragón", "Asturias", "Islas Baleares", "Canarias",
    "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña", "Comunidad Valenciana", 
    "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja",
    "Ceuta", "Melilla"
    ],
    notary_cost: int,
    registry_cost: int,
    renovation_cost: int,
    agency_commission: int,
    mortgage_management_cost: int,
    mortgage_appraisal_cost: int,
    monthly_rent: int,
    community_fee: int,
    home_insurance: int,
    mortgage_life_insurance: Optional[int],
    has_non_payment_insurance: Literal ["Y", "N"],
    non_payment_insurance: Optional[float],
    ibi_tax: int,
    vacant_periods: Optional[float],
    annual_gross_salary: int,
    irpf_tax: Optional[float],
    financed_percentage: float,
    loan_term_years: int,
    mortgage_type: Literal["fixed", "variable"],
    mortgage_spread: Optional[float],
    euribor: Optional[float],
    fixed_interest_rate: Optional[float]) -> list:
 

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
            raise ValueError(f"The autonomous community {autonomous_community} is not in the list.")
        
        itp_rate = ITP_BY_COMMUNITY[autonomous_community] / 100 # % to decimal
        itp_to_pay = purchase_price * itp_rate / 100
        return itp_rate, itp_to_pay

    # Compute ITP tax to pay
    itp_rate, itp_to_pay = calculate_itp(autonomous_community) #TODO: Try to compute this in class validators

    # Compute annual rent
    annual_rent = monthly_rent * 12

    # Compute annual costs
    manteinance_costs = 0.1 * annual_rent
    total_annual_costs = community_fee + manteinance_costs + home_insurance + mortgage_life_insurance + non_payment_insurance + ibi_tax + monthly_mortgage_interests + vacant_periods

    # Compute earnings
    ebta = annual_rent - total_annual_costs
    yearly_amortization = 0.03 * (0.3 * purchase_price + 0.5 * (itp_to_pay + notary_cost + registry_cost) + agency_commission)
    taxes = (ebta - yearly_amortization) * (1 - 0.05) * irpf_tax
    net_income_after_tax  = ebta - taxes

    # Compute financing






    