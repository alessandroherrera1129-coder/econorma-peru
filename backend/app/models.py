"""
Modelos de Datos Pydantic para EcoNorma Perú
Define esquemas relacionales, validación de campos normativos y estructuras de respuesta.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class NormBase(BaseModel):
    code: str = Field(..., description="Código oficial (e.g. D.S. 004-2017-MINAM)")
    norm_number: str = Field(..., description="Número de norma (e.g. 004-2017)")
    title: str = Field(..., description="Título completo de la norma")
    issuing_entity: str = Field(..., description="Entidad emisora (MINAM, PRODUCE, etc.)")
    instrument: str = Field(..., description="ECA / LMP / VMA")
    environmental_medium: Optional[str] = Field(None, description="Agua, Aire, Suelo, Ruido, etc.")
    sector: Optional[str] = Field(None, description="Sector regulado cuando aplique")
    year: int = Field(..., description="Año de publicación")
    publication_date: Optional[str] = Field(None, description="Fecha de publicación")
    effective_date: Optional[str] = Field(None, description="Fecha de entrada en vigencia")
    status: str = Field("VIGENTE", description="VIGENTE / MODIFICADO / DEROGADO / PENDIENTE DE VERIFICACIÓN")
    modifying_norm: Optional[str] = None
    derogating_norm: Optional[str] = None
    official_url: str = Field(..., description="Enlace oficial en gob.pe, El Peruano, MINAM o SINIA")
    summary: Optional[str] = Field(None, description="Resumen descriptivo de la norma")
    last_verified_date: Optional[str] = None

class ParameterBase(BaseModel):
    instrument: str = Field(..., description="ECA / LMP / VMA")
    environmental_medium: str = Field(..., description="Agua, Aire, Suelo, Ruido, RNI, Efluentes, Emisiones")
    sector: Optional[str] = Field(None, description="Minería, Hidrocarburos, Pesquería, PTAR, etc.")
    subsector: Optional[str] = None
    activity: Optional[str] = None
    category: str = Field(..., description="Categoría o Uso normativo")
    subcategory: Optional[str] = Field(None, description="Subcategoría específica")
    parameter_name: str = Field(..., description="Nombre oficial del parámetro")
    alternative_names: Optional[str] = Field(None, description="Sinónimos o nombres alternativos")
    symbol: Optional[str] = Field(None, description="Símbolo químico o abreviación")
    cas_number: Optional[str] = Field(None, description="Número de registro CAS")
    min_value: Optional[float] = Field(None, description="Valor mínimo permitido")
    max_value: Optional[float] = Field(None, description="Valor máximo o límite normativo")
    value_text: Optional[str] = Field(None, description="Representación en texto del valor")
    unit: str = Field(..., description="Unidad de medida (mg/L, µg/m³, dBA, mg/kg MS, etc.)")
    evaluation_period: Optional[str] = Field(None, description="Periodo (24h, 1h, Anual, Diurno, etc.)")
    frequency: Optional[str] = None
    method_criteria: Optional[str] = Field(None, description="Método de análisis o criterio")
    observations: Optional[str] = Field(None, description="Notas técnicas, excepciones o condiciones")
    norm_code: str = Field(..., description="Código de la norma vinculada")
    norm_name: str = Field(..., description="Nombre de la norma")
    year: int = Field(..., description="Año de la norma")
    annex: Optional[str] = Field(None, description="Anexo correspondiente")
    table_ref: Optional[str] = Field(None, description="Tabla o numeral")
    article_ref: Optional[str] = None
    page_ref: Optional[str] = None
    issuing_entity: str = Field(..., description="Entidad emisora")
    official_url: str = Field(..., description="URL oficial de la norma")
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    status: str = Field("VIGENTE", description="VIGENTE / MODIFICADO / DEROGADO / PENDIENTE DE VERIFICACIÓN")
    modifying_norm: Optional[str] = None
    derogating_norm: Optional[str] = None
    last_verified_date: Optional[str] = None
    verification_status: str = Field("VERIFICADO", description="VERIFICADO / PENDIENTE DE VERIFICACIÓN")

class ParameterCreate(ParameterBase):
    pass

class ParameterUpdate(BaseModel):
    instrument: Optional[str] = None
    environmental_medium: Optional[str] = None
    sector: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    parameter_name: Optional[str] = None
    alternative_names: Optional[str] = None
    symbol: Optional[str] = None
    cas_number: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    evaluation_period: Optional[str] = None
    observations: Optional[str] = None
    norm_code: Optional[str] = None
    status: Optional[str] = None
    verification_status: Optional[str] = None

class ParameterResponse(ParameterBase):
    id: int

class SearchQuery(BaseModel):
    query: Optional[str] = None
    instrument: Optional[str] = None
    environmental_medium: Optional[str] = None
    sector: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    status: Optional[str] = None
    norm_code: Optional[str] = None
    entity: Optional[str] = None
    year: Optional[int] = None
    page: int = 1
    page_size: int = 50

class CompareRequest(BaseModel):
    parameter_id: int
    measured_value: float

class CompareResponse(BaseModel):
    parameter_id: int
    parameter_name: str
    instrument: str
    category: str
    subcategory: Optional[str]
    norm_code: str
    unit: str
    min_value: Optional[float]
    max_value: Optional[float]
    measured_value: float
    is_compliant: bool
    status_label: str  # "Dentro del valor establecido" / "Supera el valor establecido"
    percentage_of_limit: Optional[float]
    evaluation_text: str
    disclaimer: str

class ContactSubmission(BaseModel):
    name: str
    email: str
    inquiry_type: str  # Corrección de información / Norma nueva / Actualización normativa / Recomendación de mejora / Consulta general
    subject: str
    message: str

class SystemStats(BaseModel):
    total_parameters: int
    total_norms: int
    total_sectors: int
    total_categories: int
    instruments_breakdown: Dict[str, int]
    media_breakdown: Dict[str, int]
    last_database_update: str
    version: str
