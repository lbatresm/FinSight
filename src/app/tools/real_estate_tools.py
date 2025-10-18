"""
Real Estate profitability computation tools for LLMs
"""

from typing import Annotated, List, Literal, Union, Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from langgraph.prebuilt.chat_agent_executor import AgentState

from pydantic import BaseModel, Field, computed_field, model_validator

# Create a class for tool function inputs. This introduces types and values validation.
class RealEstateProfitabilityInput(BaseModel):

    """Parametros vivienda"""
    precio_compraventa: int = Field(...)
    comunidad_autonoma: Literal["Andalucía", "Aragón", "Asturias", "Islas Baleares", "Canarias",
    "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña", "Comunidad Valenciana", 
    "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja",
    "Ceuta", "Melilla"
    ] = Field(..., description = "La comunidad autonoma determina el ITP")
    coste_notaria: int = Field(...)
    coste_registro: int = Field(...)
    coste_reforma: int = Field(...)
    comision_agencia: int = Field(...)

    """Gastos hipoteca"""
    coste_gestoria_hipoteca: int = Field(...)
    coste_tasacion_hipoteca: int = Field(...)
    
    """Alquiler"""
    renta_mensual: int = Field(...)

    """Estimacion gastos anuales"""
    cuota_comunidad: int = Field(...)
    seguro_hogar: int = Field(...)
    seguro_vida_hipoteca: Optional[int] # Optional field
    hay_seguro_impago: Literal ["Y", "N"] = Field(..., )
    seguro_impago: Optional[float] = Field(None, description="Importe del seguro de impago (si aplica)")
    ibi: int = Field(...)
    periodos_vacantes: Optional[float] = Field(None, description="Margen por vacantes (por defecto 5%)")

    """IRPF"""
    salario_bruto_anual: int = Field(..., description="Salario bruto anual del propietario")
    tipo_irpf: Optional[float] = Field(None, description="Porcentaje de retención IRPF según el salario")

    """Financiación"""
    porcentaje_financiado: float = Field(..., ge=0, le=1, description="Porcentaje financiado expresado en decimal (ej. 0.90 = 90%)")
    plazo_años: int = Field(..., ge=5, le=40)
    tipo_hipoteca: Literal["fijo", "variable"] = Field(..., description="Tipo de hipoteca")
    diferencial_hipoteca: Optional[float] = Field(None, description="Diferencial de la hipoteca, si es variable")
    euribor: Optional[float] = Field(None, description="Euribor, si es variable")
    interes_tipo_fijo: Optional[float] = Field(None, description="Interés tipo fijo, si es fijo")

    @model_validator(mode="after")
    def calcular_campos_automaticos(self):
        # Calcular seguro de impago si aplica
        if self.hay_seguro_impago == "Y":
            self.seguro_impago = self.renta_mensual * 12 * 0.05

        # Calcular periodos vacantes por defecto
        if self.periodos_vacantes is None:
            self.periodos_vacantes = 0.05 * 12 * self.renta_mensual

        # Calcular tramo de IRPF
        salario = self.salario_bruto_anual
        if salario <= 12450:
            self.tipo_irpf = 0.19
        elif salario <= 20199:
            self.tipo_irpf = 0.24
        elif salario <= 35199:
            self.tipo_irpf = 0.30
        elif salario <= 59999:
            self.tipo_irpf = 0.37
        elif salario <= 299999:
            self.tipo_irpf = 0.45
        else:
            self.tipo_irpf = 0.47

        # Validar coherencia de los datos de financiación
        if self.tipo_hipoteca == "variable":
            if self.diferencial_hipoteca is None or self.euribor is None:
                raise ValueError(
                    "Si el tipo de hipoteca es 'variable', deben especificarse 'diferencial_hipoteca' y 'euribor'."
                )
        elif self.tipo_hipoteca == "fijo":
            if self.interes_tipo_fijo is None:
                raise ValueError(
                    "Si el tipo de hipoteca es 'fijo', debe especificarse 'interes_tipo_fijo'."
                )

        return self

