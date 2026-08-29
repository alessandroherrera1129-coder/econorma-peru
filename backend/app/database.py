"""
Manejador de Base de Datos Relacional SQLite para EcoNorma Perú
Implementa persistencia estructurada, carga de seeds, indexación y búsquedas normalizadas.
"""
import sqlite3
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .config import DB_PATH

def normalize_text(text: Optional[str]) -> str:
    """Normaliza texto eliminando tildes, signos y pasando a minúsculas para búsqueda robusta."""
    if not text:
        return ""
    # Quitar tildes y caracteres especiales
    nfkd = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return clean.lower().strip()

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas relacionales e índices si no existen, y carga datos semilla."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabla de Normas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS norms (
        code TEXT PRIMARY KEY,
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
        summary TEXT,
        last_verified_date TEXT
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
        min_value REAL,
        max_value REAL,
        value_text TEXT,
        unit TEXT NOT NULL,
        evaluation_period TEXT,
        frequency TEXT,
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
        official_url TEXT NOT NULL,
        publication_date TEXT,
        effective_date TEXT,
        status TEXT NOT NULL DEFAULT 'VIGENTE',
        modifying_norm TEXT,
        derogating_norm TEXT,
        last_verified_date TEXT,
        verification_status TEXT NOT NULL DEFAULT 'VERIFICADO',
        search_tokens TEXT,
        FOREIGN KEY (norm_code) REFERENCES norms (code)
    );
    """)

    # 3. Tabla de Mensajes / Consultas de Contacto
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

    # 4. Tabla de Auditoría / Modificaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Índices para búsquedas ultra rápidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_name ON parameters(parameter_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_inst ON parameters(instrument);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_med ON parameters(environmental_medium);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_cat ON parameters(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_norm ON parameters(norm_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_param_status ON parameters(status);")

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
        str(p.get("norm_code") or "")
    ]
    raw = " ".join(parts)
    return normalize_text(raw)

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
            code, norm_number, title, issuing_entity, instrument,
            environmental_medium, sector, year, publication_date, effective_date,
            status, modifying_norm, derogating_norm, official_url, summary, last_verified_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            n["code"], n["norm_number"], n["title"], n["issuing_entity"], n["instrument"],
            n.get("environmental_medium"), n.get("sector"), n["year"], n.get("publication_date"),
            n.get("effective_date"), n.get("status", "VIGENTE"), n.get("modifying_norm"),
            n.get("derogating_norm"), n["official_url"], n.get("summary"), n.get("last_verified_date")
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
            cas_number, min_value, max_value, value_text, unit,
            evaluation_period, frequency, method_criteria, observations,
            norm_code, norm_name, year, annex, table_ref, article_ref, page_ref,
            issuing_entity, official_url, publication_date, effective_date,
            status, modifying_norm, derogating_norm, last_verified_date,
            verification_status, search_tokens
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?
        );
        """, (
            p["instrument"], p["environmental_medium"], p.get("sector"), p.get("subsector"), p.get("activity"),
            p["category"], p.get("subcategory"), p["parameter_name"], p.get("alternative_names"), p.get("symbol"),
            p.get("cas_number"), p.get("min_value"), p.get("max_value"), p.get("value_text"), p["unit"],
            p.get("evaluation_period"), p.get("frequency"), p.get("method_criteria"), p.get("observations"),
            p["norm_code"], p["norm_name"], p["year"], p.get("annex"), p.get("table_ref"), p.get("article_ref"), p.get("page_ref"),
            p["issuing_entity"], p["official_url"], p.get("publication_date"), p.get("effective_date"),
            p.get("status", "VIGENTE"), p.get("modifying_norm"), p.get("derogating_norm"), p.get("last_verified_date"),
            p.get("verification_status", "VERIFICADO"), search_tokens
        ))
    conn.commit()

# --- Funciones de Consulta y Búsqueda ---

def search_parameters(
    query: Optional[str] = None,
    instrument: Optional[str] = None,
    environmental_medium: Optional[str] = None,
    sector: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    status: Optional[str] = None,
    norm_code: Optional[str] = None,
    issuing_entity: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[Dict[str, Any]], int]:
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if query:
        norm_q = normalize_text(query)
        words = norm_q.split()
        for w in words:
            conditions.append("search_tokens LIKE ?")
            params.append(f"%{w}%")

    if instrument and instrument != "TODOS":
        conditions.append("instrument = ?")
        params.append(instrument)

    if environmental_medium and environmental_medium != "TODOS":
        conditions.append("environmental_medium = ?")
        params.append(environmental_medium)

    if sector and sector != "TODOS":
        conditions.append("sector LIKE ?")
        params.append(f"%{sector}%")

    if category and category != "TODOS":
        conditions.append("category LIKE ?")
        params.append(f"%{category}%")

    if subcategory and subcategory != "TODOS":
        conditions.append("subcategory LIKE ?")
        params.append(f"%{subcategory}%")

    if status and status != "TODOS":
        conditions.append("status = ?")
        params.append(status)

    if norm_code and norm_code != "TODOS":
        conditions.append("norm_code = ?")
        params.append(norm_code)

    if issuing_entity and issuing_entity != "TODOS":
        conditions.append("issuing_entity = ?")
        params.append(issuing_entity)

    if year:
        conditions.append("year = ?")
        params.append(year)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Contar total
    count_sql = f"SELECT COUNT(*) as total FROM parameters{where_clause};"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()["total"]

    # Obtener registros paginados
    offset = (page - 1) * page_size
    data_sql = f"""
    SELECT * FROM parameters
    {where_clause}
    ORDER BY 
        CASE instrument WHEN 'ECA' THEN 1 WHEN 'LMP' THEN 2 WHEN 'VMA' THEN 3 ELSE 4 END,
        parameter_name ASC, category ASC
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
    WHERE search_tokens LIKE ?
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
    cursor.execute("SELECT * FROM parameters WHERE id = ?;", (param_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_parameters_for_comparison(param_name: str) -> List[Dict[str, Any]]:
    """Obtiene todas las ocurrencias de un parámetro en diferentes medios/sectores para comparar entre categorías."""
    norm_name = normalize_text(param_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM parameters
    WHERE search_tokens LIKE ? OR parameter_name LIKE ?
    ORDER BY instrument, environmental_medium, category, subcategory;
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

    # Contar parámetros asociados a cada norma
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
    # Obtener parámetros vinculados
    cursor.execute("SELECT * FROM parameters WHERE norm_code = ? ORDER BY category, subcategory, parameter_name;", (norm_dict["code"],))
    norm_dict["parameters"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return norm_dict

def get_system_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM parameters;")
    total_params = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM norms;")
    total_norms = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(DISTINCT sector) as count FROM parameters WHERE sector IS NOT NULL AND sector != '';")
    total_sectors = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(DISTINCT category) as count FROM parameters;")
    total_categories = cursor.fetchone()["count"]

    cursor.execute("SELECT instrument, COUNT(*) as count FROM parameters GROUP BY instrument;")
    instruments = {r["instrument"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("SELECT environmental_medium, COUNT(*) as count FROM parameters GROUP BY environmental_medium;")
    media = {r["environmental_medium"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("SELECT MAX(last_verified_date) as last_date FROM parameters;")
    last_date = cursor.fetchone()["last_date"] or "2026-08-28"

    conn.close()
    return {
        "total_parameters": total_params,
        "total_norms": total_norms,
        "total_sectors": total_sectors,
        "total_categories": total_categories,
        "instruments_breakdown": instruments,
        "media_breakdown": media,
        "last_database_update": last_date
    }

def get_filter_options() -> Dict[str, List[str]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT instrument FROM parameters ORDER BY instrument;")
    instruments = [r["instrument"] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT environmental_medium FROM parameters ORDER BY environmental_medium;")
    media = [r["environmental_medium"] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT sector FROM parameters WHERE sector IS NOT NULL AND sector != '' ORDER BY sector;")
    sectors = [r["sector"] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT category FROM parameters ORDER BY category;")
    categories = [r["category"] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT issuing_entity FROM parameters ORDER BY issuing_entity;")
    entities = [r["issuing_entity"] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT norm_code FROM parameters ORDER BY norm_code;")
    norm_codes = [r["norm_code"] for r in cursor.fetchall()]

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

# --- Operaciones Administrativas ---

def create_parameter(param_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    search_tokens = compute_search_tokens(param_data)
    cursor.execute("""
    INSERT INTO parameters (
        instrument, environmental_medium, sector, subsector, activity,
        category, subcategory, parameter_name, alternative_names, symbol,
        cas_number, min_value, max_value, value_text, unit,
        evaluation_period, frequency, method_criteria, observations,
        norm_code, norm_name, year, annex, table_ref, article_ref, page_ref,
        issuing_entity, official_url, publication_date, effective_date,
        status, modifying_norm, derogating_norm, last_verified_date,
        verification_status, search_tokens
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        param_data["instrument"], param_data["environmental_medium"], param_data.get("sector"), param_data.get("subsector"), param_data.get("activity"),
        param_data["category"], param_data.get("subcategory"), param_data["parameter_name"], param_data.get("alternative_names"), param_data.get("symbol"),
        param_data.get("cas_number"), param_data.get("min_value"), param_data.get("max_value"), param_data.get("value_text"), param_data["unit"],
        param_data.get("evaluation_period"), param_data.get("frequency"), param_data.get("method_criteria"), param_data.get("observations"),
        param_data["norm_code"], param_data["norm_name"], param_data["year"], param_data.get("annex"), param_data.get("table_ref"), param_data.get("article_ref"), param_data.get("page_ref"),
        param_data["issuing_entity"], param_data["official_url"], param_data.get("publication_date"), param_data.get("effective_date"),
        param_data.get("status", "VIGENTE"), param_data.get("modifying_norm"), param_data.get("derogating_norm"), param_data.get("last_verified_date"),
        param_data.get("verification_status", "VERIFICADO"), search_tokens
    ))
    conn.commit()
    pid = cursor.lastrowid
    conn.close()
    return pid

def update_parameter(param_id: int, updates: dict) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parameters WHERE id = ?;", (param_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        return False
    current_dict = dict(current)
    current_dict.update(updates)
    current_dict["search_tokens"] = compute_search_tokens(current_dict)
    
    fields = [k for k in updates.keys() if k != "id"] + ["search_tokens"]
    set_clauses = [f"{k} = ?" for k in fields]
    vals = [current_dict[k] for k in fields] + [param_id]
    
    cursor.execute(f"UPDATE parameters SET {', '.join(set_clauses)} WHERE id = ?;", vals)
    conn.commit()
    conn.close()
    return True

def delete_parameter(param_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parameters WHERE id = ?;", (param_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_all_raw_parameters() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parameters ORDER BY id ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
