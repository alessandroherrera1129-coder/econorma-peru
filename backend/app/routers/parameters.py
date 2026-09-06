"""
Router de Parámetros Ambientales para EcoNorma Perú
Endpoints para búsqueda rápida, autocompletado, filtros dinámicos, ficha técnica y exportación CSV.
"""
from fastapi import APIRouter, Query, HTTPException, Response
from typing import Optional, List
import io
import csv
from ..database import (
    search_parameters, get_autocomplete_suggestions, get_parameter_by_id,
    get_parameters_for_comparison, get_filter_options, get_all_raw_parameters
)
from ..models import ParameterResponse

router = APIRouter(prefix="/api/parameters", tags=["Parámetros"])

@router.get("/search")
def search_params(
    q: Optional[str] = Query(None, description="Término de búsqueda (ej. Arsénico, DBO5, PM2.5, pH)"),
    instrument: Optional[str] = Query(None, description="ECA / LMP / VMA"),
    medium: Optional[str] = Query(None, description="Agua, Aire, Suelo, Ruido, etc."),
    sector: Optional[str] = Query(None, description="Minería, Hidrocarburos, Pesquería, etc."),
    category: Optional[str] = Query(None, description="Categoría normativa"),
    subcategory: Optional[str] = Query(None, description="Subcategoría específica"),
    status: Optional[str] = Query(None, description="VIGENTE / MODIFICADO / DEROGADO"),
    verification_status: Optional[str] = Query(None),
    norm_code: Optional[str] = Query(None, description="Código de la norma"),
    entity: Optional[str] = Query(None, description="Entidad emisora"),
    year: Optional[int] = Query(None, description="Año de la norma"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500)
):
    results, total = search_parameters(
        query=q,
        instrument=instrument,
        environmental_medium=medium,
        sector=sector,
        category=category,
        subcategory=subcategory,
        status=status,
        verification_status=verification_status,
        norm_code=norm_code,
        issuing_entity=entity,
        year=year,
        page=page,
        page_size=page_size,
        is_admin=False  # Búsqueda pública: excluye 'NO PUBLICAR' e 'INACTIVO'
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }

@router.get("/autocomplete")
def autocomplete(q: str = Query(..., min_length=1)):
    suggestions = get_autocomplete_suggestions(q, limit=12)
    return {"suggestions": suggestions}

@router.get("/filters")
def filter_options():
    return get_filter_options()

@router.get("/compare-categories")
def compare_categories(param_name: str = Query(..., description="Nombre del parámetro para comparar")):
    items = get_parameters_for_comparison(param_name)
    return {
        "parameter_name": param_name,
        "count": len(items),
        "items": items
    }

@router.get("/export/csv")
def export_csv(
    q: Optional[str] = None,
    instrument: Optional[str] = None,
    medium: Optional[str] = None,
    sector: Optional[str] = None,
    category: Optional[str] = None
):
    results, _ = search_parameters(
        query=q,
        instrument=instrument,
        environmental_medium=medium,
        sector=sector,
        category=category,
        page=1,
        page_size=10000,
        is_admin=False
    )
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    headers = [
        "ID", "Instrumento", "Medio Ambiental", "Sector", "Subsector", "Categoría",
        "Subcategoría", "Parámetro", "Símbolo", "CAS", "Tipo Límite", "Valor Mínimo", "Valor Máximo",
        "Valor Texto", "Unidad", "Periodo", "Condición Especial", "Método", "Observaciones",
        "Código Norma", "Nombre Norma", "Año", "Anexo", "Tabla", "Entidad Emisora",
        "Estado", "Estado Verificación", "URL Oficial"
    ]
    writer.writerow(headers)
    
    for r in results:
        writer.writerow([
            r["id"], r["instrument"], r["environmental_medium"], r.get("sector") or "", r.get("subsector") or "",
            r["category"], r.get("subcategory") or "", r["parameter_name"], r.get("symbol") or "", r.get("cas_number") or "",
            r.get("limit_type") or "",
            r["min_value"] if r.get("min_value") is not None else "",
            r["max_value"] if r.get("max_value") is not None else "",
            r.get("value_text") or "", r["unit"], r.get("evaluation_period") or "",
            r.get("special_condition") or "",
            r.get("method_criteria") or "", r.get("observations") or "",
            r["norm_code"], r.get("norm_name") or "", r.get("year") or "", r.get("annex") or "", r.get("table_ref") or "",
            r.get("issuing_entity") or "", r.get("status") or "", r.get("verification_status") or "",
            r.get("official_url") or ""
        ])
    
    output.seek(0)
    response = Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv"
    )
    filename = f"econorma_parametros_{q or 'todos'}.csv"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

@router.get("/{param_id}")
def get_param_detail(param_id: int):
    param = get_parameter_by_id(param_id)
    if not param:
        raise HTTPException(status_code=404, detail="Parámetro ambiental no encontrado")
    return param
