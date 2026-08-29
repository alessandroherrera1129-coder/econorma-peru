"""
Router de Estadísticas e Información del Sistema para EcoNorma Perú
Retorna conteos calculados dinámicamente desde la base de datos y la configuración global de branding.
"""
from fastapi import APIRouter
from ..database import get_system_stats
from ..config import (
    APP_NAME, APP_TAGLINE, APP_SUBTITLE, APP_VERSION,
    PROJECT_AUTHOR, PROJECT_PHONE, PROJECT_EMAIL, PROJECT_LOCATION,
    LEGAL_DISCLAIMER, COMPARATOR_DISCLAIMER
)

router = APIRouter(prefix="/api/stats", tags=["Estadísticas"])

@router.get("")
def stats():
    dynamic_stats = get_system_stats()
    dynamic_stats["version"] = APP_VERSION
    return dynamic_stats

@router.get("/info")
def system_info():
    return {
        "app_name": APP_NAME,
        "tagline": APP_TAGLINE,
        "subtitle": APP_SUBTITLE,
        "version": APP_VERSION,
        "author": PROJECT_AUTHOR,
        "phone": PROJECT_PHONE,
        "email": PROJECT_EMAIL,
        "location": PROJECT_LOCATION,
        "legal_disclaimer": LEGAL_DISCLAIMER,
        "comparator_disclaimer": COMPARATOR_DISCLAIMER
    }
