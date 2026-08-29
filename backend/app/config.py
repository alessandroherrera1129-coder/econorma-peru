"""
Configuración Global de la Plataforma EcoNorma Perú
Permite modificar el branding, títulos, datos de contacto y parámetros del sistema
desde un solo lugar sin alterar componentes individuales.
"""
import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "backend" / "app" / "econorma.db"))

# Branding y Textos Principales
APP_NAME = os.environ.get("APP_NAME", "EcoNorma Perú")
APP_TAGLINE = os.environ.get("APP_TAGLINE", "Plataforma de Consulta de Estándares Ambientales del Perú")
APP_SUBTITLE = os.environ.get("APP_SUBTITLE", "Sistematización y consulta rápida de ECA, LMP y VMA vigentes en el Perú")
APP_VERSION = "1.0.0"

# Identidad del Proyecto y Contacto
PROJECT_AUTHOR = os.environ.get("PROJECT_AUTHOR", "Alessandro Piero Herrera Balladares")
PROJECT_PHONE = os.environ.get("PROJECT_PHONE", "+51 981520990")
PROJECT_EMAIL = os.environ.get("PROJECT_EMAIL", "alessandroherrera1129@gmail.com")
PROJECT_LOCATION = "Lima, Perú"

# Aviso Legal Obligatorio
LEGAL_DISCLAIMER = (
    "EcoNorma Perú es una herramienta independiente de consulta y sistematización "
    "de información normativa ambiental. No constituye una plataforma oficial del Estado Peruano. "
    "Ante cualquier discrepancia, prevalece el texto publicado en la fuente oficial correspondiente."
)

COMPARATOR_DISCLAIMER = (
    "El resultado mostrado constituye una herramienta de consulta y no sustituye la evaluación "
    "normativa realizada por un profesional competente."
)

# Seguridad y Administración
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "econorma_admin_secure_key_2026")

# Metadatos del Sistema
DEFAULT_PAGE_SIZE = 50
MAX_SEARCH_RESULTS = 200
