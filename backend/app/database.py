"""
Manejador de Base de Datos Relacional SQLite para EcoNorma Perú
Implementa persistencia estructurada, migraciones no destructivas, auditoría de cambios,
resolución dinámica de URLs normativas y consultas optimizadas.
"""
import sqlite3
import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .config import DB_PATH

def normalize_text(text: Optional[str]) -> str:
    """Normaliza texto eliminando tildes, signos y pasando a minúsculas para búsqueda robusta."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return clean.lower().strip()

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas relacionales e índices, aplica migraciones no destructivas y carga seeds si es necesario."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabla de Normas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS norms (
        code TEXT PRIMARY KEY,
        norm_type TEXT DEFAULT 'Decreto Supremo',
        norm_number TEXT NOT NULL,
        title TEXT NOT NULL,
        issuing_entity TEXT NOT NULL,
        instrument TEXT NOT NULL,
        environmental_medium TEXT,
        sector TEXT,
        year INTEGER NOT NULL,
        publication_date TEXT,
        effective_date TEXT,
        status TEXT NOT NULL DEFAULT 'VIGENTE',
        modifying_norm TEXT,
        derogating_norm TEXT,
        official_url TEXT NOT NULL,
        alternate_url TEXT,
        summary TEXT,
        last_verified_date TEXT,
        last_verified_at TIMESTAMP,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """)

    # 2. Tabla de Parámetros
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument TEXT NOT NULL,
        environmental_medium TEXT NOT NULL,
        sector TEXT,
        subsector TEXT,
        activity TEXT,
        category TEXT NOT NULL,
        subcategory TEXT,
        parameter_name TEXT NOT NULL,
        alternative_names TEXT,
        symbol TEXT,
        cas_number TEXT,
        limit_type TEXT,
        min_value REAL,
        max_value REAL,
        value_text TEXT,
        unit TEXT NOT NULL,
        evaluation_period TEXT,
        frequency TEXT,
        special_condition TEXT,
        method_criteria TEXT,
        observations TEXT,
        norm_code TEXT NOT NULL,
        norm_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        annex TEXT,
        table_ref TEXT,
        article_ref TEXT,
        page_ref TEXT,
        issuing_entity TEXT NOT NULL,
        official_url TEXT,
        source_url_override TEXT,
        publication_date TEXT,
        effective_date TEXT,
        status TEXT NOT NULL DEFAULT 'VIGENTE',
        modifying_norm TEXT,
        derogating_norm TEXT,
        last_verified_date TEXT,
        last_verified_at TIMESTAMP,
        verification_status TEXT NOT NULL DEFAULT 'VERIFICADO',
        admin_comment TEXT,
        search_tokens TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (norm_code) REFERENCES norms (code)
    );
    """)

    # 3. Tabla de Auditoría / Historial de Modificaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        target_name TEXT,
        action TEXT NOT NULL,
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        admin_user TEXT DEFAULT 'Administrador',
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Tabla de Mensajes / Consultas de Contacto
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        inquiry_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'NUEVO'
    );
    """)

    # --- MIGRACIONES NO DESTRUCTIVAS DE COLUMNAS (Conservan todos los datos existentes) ---
    def add_column_if_missing(table: str, column: str, col_type: str):
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [r["name"] for r in cursor.fetchall()]
        if column not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")

    add_column_if_missing("norms", "norm_type", "TEXT")
    add_column_if_missing("norms", "alternate_url", "TEXT")
    add_column_if_missing("norms", "last_verified_at", "TIMESTAMP")
    add_column_if_missing("norms", "created_at", "TIMESTAMP")
    add_column_if_missing("norms", "updated_at", "TIMESTAMP")

    add_column_if_missing("parameters", "source_url_override", "TEXT")
    add_column_if_missing("parameters", "limit_type", "TEXT")
    add_column_if_missing("parameters", "special_condition", "TEXT")
    add_column_if_missing("parameters", "admin_comment", "TEXT")
    add_column_if_missing("parameters", "last_verified_at", "TIMESTAMP")
    add_column_if_missing("parameters", "created_at", "TIMESTAMP")
    add_column_if_missing("parameters", "updated_at", "TIMESTAMP")

    add_column_if_missing("audit_logs", "target_name", "TEXT")
    add_column_if_missing("audit_logs", "field_name", "TEXT")
    add_column_if_missing("audit_logs", "old_value", "TEXT")
    add_column_if_missing("audit_logs", "new_value", "TEXT")
    add_column_if_missing("audit_logs", "admin_user", "TEXT")
    add_column_if_missing("audit_logs", "comment", "TEXT")

    # Índices para rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_name ON parameters(parameter_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_inst ON parameters(instrument);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_med ON parameters(environmental_medium);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_cat ON parameters(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_norm ON parameters(norm_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_status ON parameters(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_verif ON parameters(verification_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_logs(target_type, target_id);")

    conn.commit()

    # Cargar Seeds si la base está vacía
    cursor.execute("SELECT COUNT(*) as count FROM norms;")
    norms_count = cursor.fetchone()["count"]
    if norms_count == 0:
        load_seed_norms(conn)

    cursor.execute("SELECT COUNT(*) as count FROM parameters;")
    params_count = cursor.fetchone()["count"]
    if params_count == 0:
        load_seed_parameters(conn)

    conn.close()

def compute_search_tokens(p: dict) -> str:
    parts = [
        str(p.get("parameter_name") or ""),
        str(p.get("alternative_names") or ""),
        str(p.get("symbol") or ""),
        str(p.get("cas_number") or ""),
        str(p.get("category") or ""),
        str(p.get("subcategory") or ""),
        str(p.get("sector") or ""),
        str(p.get("environmental_medium") or ""),
        str(p.get("instrument") or ""),
        str(p.get("norm_code") or ""),
        str(p.get("norm_name") or ""),
        str(p.get("issuing_entity") or "")
    ]
    raw = " ".join(parts)
    return normalize_text(raw)

def log_audit(
    target_type: str,
    target_id: str,
    target_name: str,
    action: str,
    field_name: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    admin_user: str = "Administrador",
    comment: Optional[str] = None
):
    """Registra una entrada en el historial de modificaciones del sistema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (
        target_type, target_id, target_name, action, field_name,
        old_value, new_value, admin_user, comment, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'));
    """, (
        target_type, str(target_id), str(target_name), action, field_name,
        str(old_value) if old_value is not None else None,
        str(new_value) if new_value is not None else None,
        admin_user, comment
    ))
    conn.commit()
    conn.close()

def load_seed_norms(conn: sqlite3.Connection):
    data_dir = Path(__file__).resolve().parent / "data"
    norms_file = data_dir / "seed_norms.json"
    if not norms_file.exists():
        return
    with open(norms_file, "r", encoding="utf-8") as f:
        norms = json.load(f)
    cursor = conn.cursor()
    for n in norms:
        cursor.execute("""
        INSERT OR REPLACE INTO norms (
            code, norm_type, norm_number, title, issuing_entity, instrument,
            environmental_medium, sector, year, publication_date, effective_date,
            status, modifying_norm, derogating_norm, official_url, alternate_url,
            summary, last_verified_date, last_verified_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'));
        """, (
            n["code"], n.get("norm_type", "Decreto Supremo"), n["norm_number"], n["title"], n["issuing_entity"], n["instrument"],
            n.get("environmental_medium"), n.get("sector"), n["year"], n.get("publication_date"),
            n.get("effective_date"), n.get("status", "VIGENTE"), n.get("modifying_norm"),
            n.get("derogating_norm"), n["official_url"], n.get("alternate_url"), n.get("summary"), n.get("last_verified_date")
        ))
    conn.commit()

def load_seed_parameters(conn: sqlite3.Connection):
    data_dir = Path(__file__).resolve().parent / "data"
    params_file = data_dir / "seed_parameters.json"
    if not params_file.exists():
        return
    with open(params_file, "r", encoding="utf-8") as f:
        params = json.load(f)
    cursor = conn.cursor()
    for p in params:
        search_tokens = compute_search_tokens(p)
        cursor.execute("""
        INSERT INTO parameters (
            instrument, environmental_medium, sector, subsector, activity,
            category, subcategory, parameter_name, alternative_names, symbol,
            cas_number, limit_type, min_value, max_value, value_text, unit,
            evaluation_period, frequency, special_condition, method_criteria, observations,
            norm_code, norm_name, year, annex, table_ref, article_ref, page_ref,
            issuing_entity, official_url, source_url_override, publication_date, effective_date,
            status, modifying_norm, derogating_norm, last_verified_date, last_verified_at,
            verification_status, admin_comment, search_tokens
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, datetime('now', 'localtime'),
            ?, ?, ?
        );
        """, (
            p["instrument"], p["environmental_medium"], p.get("sector"), p.get("subsector"), p.get("activity"),
            p["category"], p.get("subcategory"), p["parameter_name"], p.get("alternative_names"), p.get("symbol"),
            p.get("cas_number"), p.get("limit_type", "Máximo"), p.get("min_value"), p.get("max_value"), p.get("value_text"), p["unit"],
            p.get("evaluation_period"), p.get("frequency"), p.get("special_condition"), p.get("method_criteria"), p.get("observations"),
            p["norm_code"], p["norm_name"], p["year"], p.get("annex"), p.get("table_ref"), p.get("article_ref"), p.get("page_ref"),
            p["issuing_entity"], p.get("official_url"), p.get("source_url_override"), p.get("publication_date"), p.get("effective_date"),
            p.get("status", "VIGENTE"), p.get("modifying_norm"), p.get("derogating_norm"), p.get("last_verified_date"),
            p.get("verification_status", "VERIFICADO"), p.get("admin_comment"), search_tokens
        ))
    conn.commit()

# --- Funciones de Consulta y Búsqueda con Resolución Dinámica de URLs ---

PARAM_SELECT_FIELDS = """
    p.id,
    p.instrument,
    p.environmental_medium,
    p.sector,
    p.subsector,
    p.activity,
    p.category,
    p.subcategory,
    p.parameter_name,
    p.alternative_names,
    p.symbol,
    p.cas_number,
    p.limit_type,
    p.min_value,
    p.max_value,
    p.value_text,
    p.unit,
    p.evaluation_period,
    p.frequency,
    p.special_condition,
    p.method_criteria,
    p.observations,
    p.norm_code,
    p.norm_name,
    p.year,
    p.annex,
    p.table_ref,
    p.article_ref,
    p.page_ref,
    p.issuing_entity,
    COALESCE(NULLIF(p.source_url_override, ''), n.official_url, p.official_url) AS official_url,
    p.source_url_override,
    p.publication_date,
    p.effective_date,
    p.status,
    p.modifying_norm,
    p.derogating_norm,
    p.last_verified_date,
    p.last_verified_at,
    p.verification_status,
    p.admin_comment,
    p.search_tokens,
    p.created_at,
    p.updated_at,
    n.official_url AS norm_official_url,
    n.alternate_url AS norm_alternate_url,
    n.title AS norm_title_rel
"""

def search_parameters(
    query: Optional[str] = None,
    instrument: Optional[str] = None,
    environmental_medium: Optional[str] = None,
    sector: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    norm_code: Optional[str] = None,
    issuing_entity: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    is_admin: bool = False
) -> Tuple[List[Dict[str, Any]], int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = []
    params = []

    # Filtro de privacidad para la web pública
    if not is_admin:
        conditions.append("(p.verification_status != 'NO PUBLICAR' AND p.status NOT IN ('INACTIVO', 'INACTIVA'))")

    if query:
        norm_q = normalize_text(query)
        words = norm_q.split()
        for w in words:
            conditions.append("p.search_tokens LIKE ?")
            params.append(f"%{w}%")

    if instrument and instrument != "TODOS":
        conditions.append("p.instrument = ?")
        params.append(instrument)

    if environmental_medium and environmental_medium != "TODOS":
        conditions.append("p.environmental_medium = ?")
        params.append(environmental_medium)

    if sector and sector != "TODOS":
        conditions.append("p.sector LIKE ?")
        params.append(f"%{sector}%")

    if category and category != "TODOS":
        conditions.append("p.category LIKE ?")
        params.append(f"%{category}%")

    if subcategory and subcategory != "TODOS":
        conditions.append("p.subcategory LIKE ?")
        params.append(f"%{subcategory}%")

    if status and status != "TODOS":
        conditions.append("p.status = ?")
        params.append(status)

    if verification_status and verification_status != "TODOS":
        conditions.append("p.verification_status = ?")
        params.append(verification_status)

    if norm_code and norm_code != "TODOS":
        conditions.append("p.norm_code = ?")
        params.append(norm_code)

    if issuing_entity and issuing_entity != "TODOS":
        conditions.append("p.issuing_entity = ?")
        params.append(issuing_entity)

    if year:
        conditions.append("p.year = ?")
        params.append(year)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    count_sql = f"""
    SELECT COUNT(*) as total 
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    {where_clause};
    """
    cursor.execute(count_sql, params)
    total = cursor.fetchone()["total"]

    offset = (page - 1) * page_size
    data_sql = f"""
    SELECT 
        {PARAM_SELECT_FIELDS}
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    {where_clause}
    ORDER BY 
        CASE p.instrument WHEN 'ECA' THEN 1 WHEN 'LMP' THEN 2 WHEN 'VMA' THEN 3 ELSE 4 END,
        p.parameter_name ASC, p.category ASC
    LIMIT ? OFFSET ?;
    """
    cursor.execute(data_sql, params + [page_size, offset])
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows, total

def get_autocomplete_suggestions(prefix: str, limit: int = 10) -> List[Dict[str, Any]]:
    if not prefix or len(prefix.strip()) < 1:
        return []
    norm_p = normalize_text(prefix)
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    SELECT DISTINCT parameter_name, symbol, instrument, environmental_medium
    FROM parameters
    WHERE search_tokens LIKE ? AND verification_status != 'NO PUBLICAR' AND status NOT IN ('INACTIVO', 'INACTIVA')
    ORDER BY parameter_name ASC
    LIMIT ?;
    """
    cursor.execute(sql, (f"%{norm_p}%", limit))
    results = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return results

def get_parameter_by_id(param_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT 
        {PARAM_SELECT_FIELDS}
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    WHERE p.id = ?;
    """, (param_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_parameters_for_comparison(param_name: str) -> List[Dict[str, Any]]:
    norm_name = normalize_text(param_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT 
        {PARAM_SELECT_FIELDS}
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    WHERE (p.search_tokens LIKE ? OR p.parameter_name LIKE ?)
      AND p.verification_status != 'NO PUBLICAR' AND p.status NOT IN ('INACTIVO', 'INACTIVA')
    ORDER BY p.instrument, p.environmental_medium, p.category, p.subcategory;
    """, (f"%{norm_name}%", f"%{param_name}%"))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_norms(
    query: Optional[str] = None,
    instrument: Optional[str] = None,
    sector: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = []
    params = []

    if query:
        norm_q = normalize_text(query)
        conditions.append("(code LIKE ? OR norm_number LIKE ? OR title LIKE ? OR issuing_entity LIKE ?)")
        params.extend([f"%{norm_q}%", f"%{norm_q}%", f"%{norm_q}%", f"%{norm_q}%"])

    if instrument and instrument != "TODOS":
        conditions.append("instrument = ?")
        params.append(instrument)

    if sector and sector != "TODOS":
        conditions.append("sector LIKE ?")
        params.append(f"%{sector}%")

    if year:
        conditions.append("year = ?")
        params.append(year)

    if status and status != "TODOS":
        conditions.append("status = ?")
        params.append(status)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"SELECT * FROM norms{where_clause} ORDER BY year DESC, code ASC;"
    cursor.execute(sql, params)
    norms = [dict(r) for r in cursor.fetchall()]

    for n in norms:
        cursor.execute("SELECT COUNT(*) as p_count FROM parameters WHERE norm_code = ?;", (n["code"],))
        n["parameters_count"] = cursor.fetchone()["p_count"]

    conn.close()
    return norms

def get_norm_by_code(code: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM norms WHERE code = ? OR norm_number = ?;", (code, code))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    norm_dict = dict(row)
    cursor.execute("""
    SELECT 
        p.*,
        COALESCE(p.source_url_override, ?, p.official_url) AS official_url
    FROM parameters p 
    WHERE p.norm_code = ? 
    ORDER BY p.category, p.subcategory, p.parameter_name;
    """, (norm_dict["official_url"], norm_dict["code"]))
    norm_dict["parameters"] = [dict(r) for r in cursor.fetchall()]
    norm_dict["parameters_count"] = len(norm_dict["parameters"])
    conn.close()
    return norm_dict

def get_system_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM parameters WHERE verification_status != 'NO PUBLICAR' AND status NOT IN ('INACTIVO', 'INACTIVA');")
    total_params = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM norms WHERE status NOT IN ('INACTIVO', 'INACTIVA');")
    total_norms = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(DISTINCT sector) as count FROM parameters WHERE sector IS NOT NULL AND sector != '' AND verification_status != 'NO PUBLICAR';")
    total_sectors = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(DISTINCT category) as count FROM parameters WHERE verification_status != 'NO PUBLICAR';")
    total_categories = cursor.fetchone()["count"]

    cursor.execute("SELECT instrument, COUNT(*) as count FROM parameters WHERE verification_status != 'NO PUBLICAR' GROUP BY instrument;")
    instruments = {r["instrument"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("SELECT environmental_medium, COUNT(*) as count FROM parameters WHERE verification_status != 'NO PUBLICAR' GROUP BY environmental_medium;")
    media = {r["environmental_medium"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("SELECT MAX(COALESCE(last_verified_date, date(last_verified_at))) as last_date FROM parameters;")
    last_date = cursor.fetchone()["last_date"] or datetime.now().strftime("%Y-%m-%d")

    conn.close()
    return {
        "total_parameters": total_params,
        "total_norms": total_norms,
        "total_sectors": total_sectors,
        "total_categories": total_categories,
        "instruments_breakdown": instruments,
        "media_breakdown": media,
        "last_database_update": last_date,
        "version": "1.1.0"
    }

def get_filter_options() -> Dict[str, List[str]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT instrument FROM parameters ORDER BY instrument;")
    instruments = [r["instrument"] for r in cursor.fetchall() if r["instrument"]]

    cursor.execute("SELECT DISTINCT environmental_medium FROM parameters ORDER BY environmental_medium;")
    media = [r["environmental_medium"] for r in cursor.fetchall() if r["environmental_medium"]]

    cursor.execute("SELECT DISTINCT sector FROM parameters WHERE sector IS NOT NULL AND sector != '' ORDER BY sector;")
    sectors = [r["sector"] for r in cursor.fetchall() if r["sector"]]

    cursor.execute("SELECT DISTINCT category FROM parameters ORDER BY category;")
    categories = [r["category"] for r in cursor.fetchall() if r["category"]]

    cursor.execute("SELECT DISTINCT issuing_entity FROM parameters ORDER BY issuing_entity;")
    entities = [r["issuing_entity"] for r in cursor.fetchall() if r["issuing_entity"]]

    cursor.execute("SELECT code FROM norms ORDER BY code;")
    norm_codes = [r["code"] for r in cursor.fetchall() if r["code"]]

    conn.close()
    return {
        "instruments": instruments,
        "environmental_media": media,
        "sectors": sectors,
        "categories": categories,
        "issuing_entities": entities,
        "norm_codes": norm_codes
    }

def save_inquiry(name: str, email: str, inquiry_type: str, subject: str, message: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO inquiries (name, email, inquiry_type, subject, message)
    VALUES (?, ?, ?, ?, ?);
    """, (name, email, inquiry_type, subject, message))
    conn.commit()
    inquiry_id = cursor.lastrowid
    conn.close()
    return inquiry_id

# --- Operaciones Administrativas: Parámetros ---

def check_parameter_duplicate(parameter_name: str, category: str, norm_code: str, exclude_id: Optional[int] = None) -> List[Dict[str, Any]]:
    norm_name = normalize_text(parameter_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    SELECT id, parameter_name, category, subcategory, norm_code, unit, value_text 
    FROM parameters 
    WHERE (search_tokens LIKE ? OR parameter_name LIKE ?) AND category = ?
    """
    params = [f"%{norm_name}%", f"%{parameter_name}%", category]
    if exclude_id:
        sql += " AND id != ?"
        params.append(exclude_id)
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def create_parameter(param_data: dict, admin_user: str = "Administrador") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    search_tokens = compute_search_tokens(param_data)
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO parameters (
        instrument, environmental_medium, sector, subsector, activity,
        category, subcategory, parameter_name, alternative_names, symbol,
        cas_number, limit_type, min_value, max_value, value_text, unit,
        evaluation_period, frequency, special_condition, method_criteria, observations,
        norm_code, norm_name, year, annex, table_ref, article_ref, page_ref,
        issuing_entity, official_url, source_url_override, publication_date, effective_date,
        status, modifying_norm, derogating_norm, last_verified_date, last_verified_at,
        verification_status, admin_comment, search_tokens, created_at, updated_at
    ) VALUES (
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?
    );
    """, (
        param_data["instrument"], param_data["environmental_medium"], param_data.get("sector"), param_data.get("subsector"), param_data.get("activity"),
        param_data["category"], param_data.get("subcategory"), param_data["parameter_name"], param_data.get("alternative_names"), param_data.get("symbol"),
        param_data.get("cas_number"), param_data.get("limit_type", "Máximo"), param_data.get("min_value"), param_data.get("max_value"), param_data.get("value_text"), param_data["unit"],
        param_data.get("evaluation_period"), param_data.get("frequency"), param_data.get("special_condition"), param_data.get("method_criteria"), param_data.get("observations"),
        param_data["norm_code"], param_data.get("norm_name", param_data["norm_code"]), param_data.get("year", datetime.now().year), param_data.get("annex"), param_data.get("table_ref"), param_data.get("article_ref"), param_data.get("page_ref"),
        param_data.get("issuing_entity", "MINAM"), param_data.get("official_url"), param_data.get("source_url_override"), param_data.get("publication_date"), param_data.get("effective_date"),
        param_data.get("status", "VIGENTE"), param_data.get("modifying_norm"), param_data.get("derogating_norm"), param_data.get("last_verified_date", datetime.now().strftime("%Y-%m-%d")), now_ts,
        param_data.get("verification_status", "VERIFICADO"), param_data.get("admin_comment"), search_tokens, now_ts, now_ts
    ))
    conn.commit()
    pid = cursor.lastrowid
    conn.close()

    log_audit(
        target_type="PARAMETER",
        target_id=str(pid),
        target_name=param_data["parameter_name"],
        action="CREATE",
        comment=f"Parámetro creado en categoría {param_data['category']} con norma {param_data['norm_code']}",
        admin_user=admin_user
    )
    return pid

def update_parameter(param_id: int, updates: dict, admin_user: str = "Administrador", comment: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parameters WHERE id = ?;", (param_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        return False
    current_dict = dict(current)

    changes = []
    for k, new_v in updates.items():
        if k in ("id", "search_tokens", "created_at", "updated_at"):
            continue
        old_v = current_dict.get(k)
        if str(old_v) != str(new_v):
            changes.append((k, old_v, new_v))

    current_dict.update(updates)
    current_dict["search_tokens"] = compute_search_tokens(current_dict)
    current_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "verification_status" in updates and updates["verification_status"] == "VERIFICADO":
        current_dict["last_verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_dict["last_verified_date"] = datetime.now().strftime("%Y-%m-%d")

    fields = [k for k in updates.keys() if k not in ("id", "search_tokens", "created_at")] + ["search_tokens", "updated_at"]
    if "last_verified_at" in current_dict and "last_verified_at" not in fields:
        fields.append("last_verified_at")
    if "last_verified_date" in current_dict and "last_verified_date" not in fields:
        fields.append("last_verified_date")

    set_clauses = [f"{k} = ?" for k in fields]
    vals = [current_dict[k] for k in fields] + [param_id]

    cursor.execute(f"UPDATE parameters SET {', '.join(set_clauses)} WHERE id = ?;", vals)
    conn.commit()
    conn.close()

    param_name = current_dict.get("parameter_name", f"ID {param_id}")
    for f_name, old_val, new_val in changes:
        log_audit(
            target_type="PARAMETER",
            target_id=str(param_id),
            target_name=param_name,
            action="UPDATE",
            field_name=f_name,
            old_value=old_val,
            new_value=new_val,
            admin_user=admin_user,
            comment=comment or updates.get("admin_comment")
        )
    return True

def verify_parameter(param_id: int, comment: Optional[str] = None, admin_user: str = "Administrador") -> bool:
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")
    return update_parameter(
        param_id,
        {
            "verification_status": "VERIFICADO",
            "last_verified_at": now_ts,
            "last_verified_date": today_str,
            "admin_comment": comment or "Verificación manual realizada por el administrador"
        },
        admin_user=admin_user,
        comment=comment or "Marcado como verificado"
    )

def delete_parameter(param_id: int, soft: bool = True, admin_user: str = "Administrador") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT parameter_name FROM parameters WHERE id = ?;", (param_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    param_name = row["parameter_name"]

    if soft:
        cursor.execute("UPDATE parameters SET status = 'INACTIVO', verification_status = 'NO PUBLICAR' WHERE id = ?;", (param_id,))
        log_audit("PARAMETER", str(param_id), param_name, "STATUS_CHANGE", field_name="status", old_value="VIGENTE", new_value="INACTIVO", admin_user=admin_user, comment="Desactivado (Soft delete)")
    else:
        cursor.execute("DELETE FROM parameters WHERE id = ?;", (param_id,))
        log_audit("PARAMETER", str(param_id), param_name, "DELETE", admin_user=admin_user, comment="Eliminado permanentemente")
    
    conn.commit()
    conn.close()
    return True

# --- Operaciones Administrativas: Normas ---

def check_norm_duplicate(code: str, norm_number: str) -> List[Dict[str, Any]]:
    clean_code = normalize_text(code).replace(".", "").replace(" ", "").replace("-", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, norm_number, title, issuing_entity, official_url FROM norms;")
    all_norms = [dict(r) for r in cursor.fetchall()]
    conn.close()

    duplicates = []
    for n in all_norms:
        existing_clean = normalize_text(n["code"]).replace(".", "").replace(" ", "").replace("-", "")
        if clean_code in existing_clean or existing_clean in clean_code or (norm_number and norm_number in n["norm_number"]):
            duplicates.append(n)
    return duplicates

def create_norm(norm_data: dict, admin_user: str = "Administrador") -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO norms (
        code, norm_type, norm_number, title, issuing_entity, instrument,
        environmental_medium, sector, year, publication_date, effective_date,
        status, modifying_norm, derogating_norm, official_url, alternate_url,
        summary, last_verified_date, last_verified_at, created_at, updated_at
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?
    );
    """, (
        norm_data["code"], norm_data.get("norm_type", "Decreto Supremo"), norm_data["norm_number"], norm_data["title"], norm_data["issuing_entity"], norm_data["instrument"],
        norm_data.get("environmental_medium"), norm_data.get("sector"), norm_data["year"], norm_data.get("publication_date"), norm_data.get("effective_date"),
        norm_data.get("status", "VIGENTE"), norm_data.get("modifying_norm"), norm_data.get("derogating_norm"), norm_data["official_url"], norm_data.get("alternate_url"),
        norm_data.get("summary"), norm_data.get("last_verified_date", datetime.now().strftime("%Y-%m-%d")), now_ts, now_ts, now_ts
    ))
    conn.commit()
    conn.close()

    log_audit(
        target_type="NORM",
        target_id=norm_data["code"],
        target_name=norm_data["title"],
        action="CREATE",
        comment=f"Norma {norm_data['code']} registrada con URL oficial: {norm_data['official_url']}",
        admin_user=admin_user
    )
    return norm_data["code"]

def update_norm(code: str, updates: dict, admin_user: str = "Administrador", comment: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM norms WHERE code = ?;", (code,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        return False
    current_dict = dict(current)

    changes = []
    for k, new_v in updates.items():
        if k in ("code", "created_at", "updated_at"):
            continue
        old_v = current_dict.get(k)
        if str(old_v) != str(new_v):
            changes.append((k, old_v, new_v))

    current_dict.update(updates)
    current_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_dict["last_verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_dict["last_verified_date"] = datetime.now().strftime("%Y-%m-%d")

    fields = [k for k in updates.keys() if k not in ("code", "created_at")] + ["updated_at", "last_verified_at", "last_verified_date"]
    set_clauses = [f"{k} = ?" for k in fields]
    vals = [current_dict[k] for k in fields] + [code]

    cursor.execute(f"UPDATE norms SET {', '.join(set_clauses)} WHERE code = ?;", vals)

    if "title" in updates or "issuing_entity" in updates:
        cursor.execute("""
        UPDATE parameters 
        SET norm_name = COALESCE(?, norm_name), issuing_entity = COALESCE(?, issuing_entity)
        WHERE norm_code = ?;
        """, (updates.get("title"), updates.get("issuing_entity"), code))

    conn.commit()
    conn.close()

    norm_title = current_dict.get("title", code)
    for f_name, old_val, new_val in changes:
        log_audit(
            target_type="NORM",
            target_id=code,
            target_name=norm_title,
            action="UPDATE",
            field_name=f_name,
            old_value=old_val,
            new_value=new_val,
            admin_user=admin_user,
            comment=comment or updates.get("admin_comment")
        )
    return True

def delete_norm(code: str, admin_user: str = "Administrador") -> bool:
    return update_norm(code, {"status": "INACTIVA"}, admin_user=admin_user, comment="Norma desactivada por el administrador")

def get_audit_logs(target_type: Optional[str] = None, target_id: Optional[str] = None, limit: int = 150) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = []
    params = []

    if target_type:
        conditions.append("target_type = ?")
        params.append(target_type)
    if target_id:
        conditions.append("target_id = ?")
        params.append(str(target_id))

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"SELECT * FROM audit_logs{where_clause} ORDER BY id DESC LIMIT ?;"
    cursor.execute(sql, params + [limit])
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_raw_parameters() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT 
        {PARAM_SELECT_FIELDS}
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    ORDER BY p.id ASC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
