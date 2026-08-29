"""
Router de Normas Ambientales para EcoNorma Perú
Biblioteca normativa, buscador por número de norma y visualización de parámetros asociados.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..database import get_all_norms, get_norm_by_code

router = APIRouter(prefix="/api/norms", tags=["Normas"])

@router.get("")
def list_norms(
    q: Optional[str] = Query(None, description="Buscar por número (ej. 004-2017, 010-2019), título o entidad"),
    instrument: Optional[str] = Query(None, description="ECA / LMP / VMA"),
    sector: Optional[str] = Query(None, description="Sector regulado"),
    year: Optional[int] = Query(None, description="Año"),
    status: Optional[str] = Query(None, description="VIGENTE / MODIFICADO / DEROGADO")
):
    norms = get_all_norms(query=q, instrument=instrument, sector=sector, year=year, status=status)
    return {
        "total": len(norms),
        "norms": norms
    }

@router.get("/{code}")
def norm_detail(code: str):
    norm = get_norm_by_code(code)
    if not norm:
        raise HTTPException(status_code=404, detail="Norma ambiental no encontrada")
    return norm
