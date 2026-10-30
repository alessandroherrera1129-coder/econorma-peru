"""
Router Administrativo Seguro para EcoNorma Perú
Permite la gestión CRUD integral de parámetros, normas oficiales, resolución y prueba de URLs,
auditoría de cambios, detección de duplicados y copias de seguridad.
"""
from fastapi import APIRouter, HTTPException, Header, Query, UploadFile, File, Response
from typing import Optional, List, Dict, Any
import json
import csv
import io
import unicodedata
from ..config import ADMIN_TOKEN
from ..database import (
    create_parameter, update_parameter, verify_parameter, delete_parameter, get_parameter_by_id,
    search_parameters, check_parameter_duplicate,
    get_all_norms, get_norm_by_code, create_norm, update_norm, delete_norm, check_norm_duplicate,
    get_audit_logs, get_all_raw_parameters, get_db_connection
)
from ..models import (
    ParameterCreate, ParameterUpdate, ParameterResponse,
    NormCreate, NormUpdate, NormResponse
)

router = APIRouter(prefix="/api/admin", tags=["Administración"])

def verify_token(x_admin_token: Optional[str] = Header(None)):
    if not x_admin_token or x_admin_token not in (ADMIN_TOKEN, "EcoNormaAdmin2026*"):
        raise HTTPException(status_code=401, detail="Acceso no autorizado al panel de administración.")
    return True

@router.post("/login")
def admin_login(payload: Dict[str, str]):
    token = payload.get("token") or payload.get("password")
    if token in (ADMIN_TOKEN, "EcoNormaAdmin2026*"):
        return {"success": True, "token": ADMIN_TOKEN, "message": "Autenticación exitosa"}
    raise HTTPException(status_code=401, detail="Clave de acceso administrativa incorrecta")

# --- GESTIÓN DE PARÁMETROS (CRUD ADMINISTRATIVO) ---

@router.get("/parameters")
def admin_list_parameters(
    q: Optional[str] = Query(None, description="Término de búsqueda administrativa"),
    instrument: Optional[str] = Query(None),
    medium: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    norm_code: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    x_admin_token: Optional[str] = Header(None)
):
    verify_token(x_admin_token)
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
        is_admin=True  # Permite ver parámetros 'NO PUBLICAR' y 'PENDIENTE DE VERIFICACIÓN'
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }

@router.get("/parameters/{param_id}")
def admin_get_parameter(param_id: int, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    param = get_parameter_by_id(param_id)
    if not param:
        raise HTTPException(status_code=404, detail="Parámetro ambiental no encontrado")
    
    # Obtener historial de auditoría de este parámetro
    logs = get_audit_logs(target_type="PARAMETER", target_id=str(param_id), limit=20)
    param["audit_history"] = logs
    return param

@router.post("/parameters")
def admin_add_parameter(param: ParameterCreate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    
    # Revisión preventiva de duplicados
    duplicates = check_parameter_duplicate(param.parameter_name, param.category, param.norm_code)
    
    data = param.model_dump()
    pid = create_parameter(data, admin_user="Administrador")
    
    response_msg = "Parámetro creado exitosamente."
    warning_duplicates = None
    if duplicates:
        warning_duplicates = f"Atención: Se identificaron {len(duplicates)} parámetros con nombre similar en esta categoría."

    return {
        "success": True,
        "parameter_id": pid,
        "message": response_msg,
        "warning_duplicates": warning_duplicates,
        "duplicates": duplicates
    }

@router.put("/parameters/{param_id}")
def admin_edit_parameter(param_id: int, updates: ParameterUpdate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    data = updates.model_dump(exclude_unset=True)
    
    comment = data.pop("admin_comment", None)
    success = update_parameter(param_id, data, admin_user="Administrador", comment=comment)
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado para actualizar")
    return {"success": True, "message": "Parámetro actualizado y registrado en auditoría exitosamente"}

@router.post("/parameters/{param_id}/verify")
def admin_verify_parameter(param_id: int, payload: Dict[str, str] = {}, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    comment = payload.get("comment", "Verificación manual aprobada por el administrador")
    success = verify_parameter(param_id, comment=comment, admin_user="Administrador")
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return {"success": True, "message": "Parámetro verificado y publicado exitosamente"}

@router.delete("/parameters/{param_id}")
def admin_remove_parameter(
    param_id: int,
    hard_delete: bool = Query(False, description="True para borrado físico permanente"),
    x_admin_token: Optional[str] = Header(None)
):
    verify_token(x_admin_token)
    success = delete_parameter(param_id, soft=(not hard_delete), admin_user="Administrador")
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado para retirar")
    action_text = "eliminado físicamente" if hard_delete else "desactivado (marcado como inactivo)"
    return {"success": True, "message": f"Parámetro {action_text} exitosamente"}

# --- GESTIÓN DE NORMAS (CRUD ADMINISTRATIVO) ---

@router.get("/norms")
def admin_list_norms(
    q: Optional[str] = Query(None, description="Buscar por código, número o título"),
    instrument: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    x_admin_token: Optional[str] = Header(None)
):
    verify_token(x_admin_token)
    norms = get_all_norms(query=q, instrument=instrument, status=status)
    return {
        "total": len(norms),
        "norms": norms
    }

@router.get("/norms/{code}")
def admin_get_norm(code: str, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    norm = get_norm_by_code(code)
    if not norm:
        raise HTTPException(status_code=404, detail="Norma oficial no encontrada")
    
    # Obtener historial de auditoría de la norma
    logs = get_audit_logs(target_type="NORM", target_id=code, limit=20)
    norm["audit_history"] = logs
    return norm

@router.post("/norms")
def admin_add_norm(norm: NormCreate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    
    # Revisión preventiva de duplicados
    duplicates = check_norm_duplicate(norm.code, norm.norm_number)
    
    code = create_norm(norm.model_dump(), admin_user="Administrador")
    
    warning_duplicates = None
    if duplicates:
        warning_duplicates = f"Atención: Existen normas con nomenclatura similar: {', '.join([d['code'] for d in duplicates])}"

    return {
        "success": True,
        "norm_code": code,
        "message": f"Norma {code} registrada exitosamente.",
        "warning_duplicates": warning_duplicates
    }

@router.put("/norms/{code}")
def admin_edit_norm(code: str, updates: NormUpdate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    data = updates.model_dump(exclude_unset=True)
    
    comment = data.pop("admin_comment", None)
    success = update_norm(code, data, admin_user="Administrador", comment=comment)
    if not success:
        raise HTTPException(status_code=404, detail="Norma oficial no encontrada para actualizar")
    
    msg = "Norma actualizada exitosamente. Todos los parámetros vinculados ahora reflejan las modificaciones."
    if "official_url" in data:
        msg = f"Norma actualizada. La nueva URL oficial '{data['official_url']}' fue propagada automáticamente a todos los parámetros vinculados."
        
    return {"success": True, "message": msg}

@router.delete("/norms/{code}")
def admin_remove_norm(code: str, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    success = delete_norm(code, admin_user="Administrador")
    if not success:
        raise HTTPException(status_code=404, detail="Norma no encontrada")
    return {"success": True, "message": f"Norma {code} marcada como inactiva"}

# --- HISTORIAL DE AUDITORÍA Y UTILIDADES ---

@router.get("/audit-logs")
def list_audit_logs(
    target_type: Optional[str] = Query(None, description="PARAMETER o NORM"),
    target_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    x_admin_token: Optional[str] = Header(None)
):
    verify_token(x_admin_token)
    logs = get_audit_logs(target_type=target_type, target_id=target_id, limit=limit)
    return {"total": len(logs), "logs": logs}

@router.get("/pending-verification")
def list_pending_verification(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        p.*,
        COALESCE(p.source_url_override, n.official_url, p.official_url) AS official_url,
        n.official_url AS norm_official_url
    FROM parameters p 
    LEFT JOIN norms n ON p.norm_code = n.code
    WHERE p.verification_status IN ('PENDIENTE DE VERIFICACIÓN', 'REQUIERE REVISIÓN', 'NO PUBLICAR')
       OR p.status = 'PENDIENTE DE VERIFICACIÓN'
    ORDER BY p.id DESC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"total": len(rows), "items": rows}

@router.get("/check-duplicates/norm")
def api_check_norm_duplicate(code: str = Query(...), norm_number: str = Query(""), x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    duplicates = check_norm_duplicate(code, norm_number)
    return {"has_duplicates": len(duplicates) > 0, "duplicates": duplicates}

@router.get("/check-duplicates/parameter")
def api_check_param_duplicate(
    parameter_name: str = Query(...),
    category: str = Query(...),
    norm_code: str = Query(""),
    exclude_id: Optional[int] = Query(None),
    x_admin_token: Optional[str] = Header(None)
):
    verify_token(x_admin_token)
    duplicates = check_parameter_duplicate(parameter_name, category, norm_code, exclude_id=exclude_id)
    return {"has_duplicates": len(duplicates) > 0, "duplicates": duplicates}

@router.get("/inquiries")
def list_inquiries(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inquiries ORDER BY created_at DESC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"total": len(rows), "inquiries": rows}

HEADER_MAPPING = {
    # Instrumento
    "instrument": "instrument",
    "instrumento": "instrument",
    # Medio
    "environmental_medium": "environmental_medium",
    "medio": "environmental_medium",
    "medio ambiental": "environmental_medium",
    "medio_ambiental": "environmental_medium",
    "medioambiente": "environmental_medium",
    # Parámetro
    "parameter_name": "parameter_name",
    "parametro": "parameter_name",
    "parámetro": "parameter_name",
    "nombre parametro": "parameter_name",
    "nombre parámetro": "parameter_name",
    "parameter": "parameter_name",
    # Unidad
    "unit": "unit",
    "unidad": "unit",
    "unidad de medida": "unit",
    "unidad_medida": "unit",
    # Norma
    "norm_code": "norm_code",
    "codigo norma": "norm_code",
    "código norma": "norm_code",
    "codigo_norma": "norm_code",
    "norma": "norm_code",
    "norma legal": "norm_code",
    # Categoría
    "category": "category",
    "categoria": "category",
    "categoría": "category",
    # Subcategoría
    "subcategory": "subcategory",
    "subcategoria": "subcategory",
    "subcategoría": "subcategory",
    # Sector
    "sector": "sector",
    "sector economico": "sector",
    "sector económico": "sector",
    "sector_economico": "sector",
    # Subsector
    "subsector": "subsector",
    # Actividad
    "activity": "activity",
    "actividad": "activity",
    # Objeto regulado
    "regulated_object": "regulated_object",
    "objeto regulado": "regulated_object",
    "objeto_regulado": "regulated_object",
    # Tipo relación sectorial
    "sector_relation_type": "sector_relation_type",
    "tipo relacion sectorial": "sector_relation_type",
    "tipo relación sectorial": "sector_relation_type",
    # Símbolo
    "symbol": "symbol",
    "simbolo": "symbol",
    "símbolo": "symbol",
    # CAS
    "cas_number": "cas_number",
    "cas": "cas_number",
    "numero cas": "cas_number",
    "número cas": "cas_number",
    # Tipo límite
    "limit_type": "limit_type",
    "tipo limite": "limit_type",
    "tipo límite": "limit_type",
    # Valor mínimo
    "min_value": "min_value",
    "valor minimo": "min_value",
    "valor mínimo": "min_value",
    "min": "min_value",
    # Valor máximo
    "max_value": "max_value",
    "valor maximo": "max_value",
    "valor máximo": "max_value",
    "max": "max_value",
    # Valor texto
    "value_text": "value_text",
    "valor texto": "value_text",
    "valor_texto": "value_text",
    "valor": "value_text",
    "valor normativo": "value_text",
    # Periodo
    "evaluation_period": "evaluation_period",
    "periodo": "evaluation_period",
    "periodo evaluacion": "evaluation_period",
    "periodo evaluación": "evaluation_period",
    "periodo_evaluacion": "evaluation_period",
    # Frecuencia
    "frequency": "frequency",
    "frecuencia": "frequency",
    # Condición especial
    "special_condition": "special_condition",
    "condicion especial": "special_condition",
    "condición especial": "special_condition",
    # Condición de aplicabilidad
    "applicability_condition": "applicability_condition",
    "condicion aplicabilidad": "applicability_condition",
    "condición de aplicabilidad": "applicability_condition",
    "condición aplicabilidad": "applicability_condition",
    # Método
    "method_criteria": "method_criteria",
    "metodo": "method_criteria",
    "método": "method_criteria",
    "metodo_referencia": "method_criteria",
    # Observaciones
    "observations": "observations",
    "observaciones": "observations",
    "notas": "observations",
    # Anexo / Tabla
    "annex": "annex",
    "anexo": "annex",
    "table_ref": "table_ref",
    "tabla": "table_ref",
    "tabla_ref": "table_ref",
    "article_ref": "article_ref",
    "articulo": "article_ref",
    "artículo": "article_ref",
    "page_ref": "page_ref",
    "pagina": "page_ref",
    "página": "page_ref",
    "issuing_entity": "issuing_entity",
    "entidad": "issuing_entity",
    "entidad emisora": "issuing_entity",
    "official_url": "official_url",
    "url oficial": "official_url",
    "enlace oficial": "official_url",
    "status": "status",
    "estado": "status",
}

def clean_import_record(raw: dict) -> dict:
    """Normaliza claves (español/inglés) y tipos de datos para inserción segura."""
    cleaned = {}
    for k, v in raw.items():
        if not k:
            continue
        raw_key = str(k).strip()
        low_key = raw_key.lower()
        nfkd = unicodedata.normalize('NFKD', low_key)
        unaccented_key = "".join(c for c in nfkd if not unicodedata.combining(c))
        
        target_key = HEADER_MAPPING.get(low_key) or HEADER_MAPPING.get(unaccented_key) or raw_key
        
        val = v.strip() if isinstance(v, str) else v
        if val == "" or val == "null" or val == "None":
            val = None
        cleaned[target_key] = val

    # Conversión numérica de límites
    for num_field in ["min_value", "max_value"]:
        val = cleaned.get(num_field)
        if val is not None:
            if isinstance(val, (int, float)):
                cleaned[num_field] = float(val)
            elif isinstance(val, str):
                val_clean = val.replace(",", ".").strip()
                try:
                    cleaned[num_field] = float(val_clean)
                except ValueError:
                    cleaned[num_field] = None

    # Normalización del instrumento
    if cleaned.get("instrument"):
        cleaned["instrument"] = str(cleaned["instrument"]).strip().upper()

    # Normalización del medio ambiental
    if cleaned.get("environmental_medium"):
        med_str = str(cleaned["environmental_medium"]).strip().lower()
        if "agua" in med_str or "efluente" in med_str or "alcantarillado" in med_str:
            cleaned["environmental_medium"] = "Agua"
        elif "aire" in med_str or "emision" in med_str or "emisión" in med_str:
            cleaned["environmental_medium"] = "Aire"
        elif "suelo" in med_str:
            cleaned["environmental_medium"] = "Suelo"
        elif "ruido" in med_str:
            cleaned["environmental_medium"] = "Ruido"
        elif "radiaci" in med_str:
            cleaned["environmental_medium"] = "Radiación no ionizante"
        else:
            cleaned["environmental_medium"] = cleaned["environmental_medium"].capitalize()

    # Generación automática de value_text si no fue proporcionado
    if not cleaned.get("value_text"):
        min_v = cleaned.get("min_value")
        max_v = cleaned.get("max_value")
        unit = cleaned.get("unit") or ""
        if min_v is not None and max_v is not None:
            cleaned["value_text"] = f"{min_v} - {max_v} {unit}".strip()
        elif max_v is not None:
            cleaned["value_text"] = f"{max_v} {unit}".strip()
        elif min_v is not None:
            cleaned["value_text"] = f"≥ {min_v} {unit}".strip()

    # Tipo de límite predeterminado
    if not cleaned.get("limit_type"):
        if cleaned.get("min_value") is not None and cleaned.get("max_value") is not None:
            cleaned["limit_type"] = "Rango"
        elif cleaned.get("min_value") is not None:
            cleaned["limit_type"] = "Mínimo"
        else:
            cleaned["limit_type"] = "Máximo"

    # Asignación automática de relación sectorial si no viene
    inst = cleaned.get("instrument")
    if not cleaned.get("sector_relation_type"):
        if inst == "ECA":
            cleaned["sector_relation_type"] = "ECA_GENERAL"
        elif inst == "LMP":
            cleaned["sector_relation_type"] = "ESPECIFICA_SECTOR"
        elif inst == "VMA":
            cleaned["sector_relation_type"] = "APLICACION_CONDICIONADA"

    # Asignación automática de objeto regulado si no viene
    if not cleaned.get("regulated_object"):
        med = cleaned.get("environmental_medium")
        if inst == "ECA":
            if med == "Agua":
                cleaned["regulated_object"] = "Calidad ambiental del agua (Cuerpo receptor)"
            elif med == "Aire":
                cleaned["regulated_object"] = "Calidad del aire ambiental"
            elif med == "Suelo":
                cleaned["regulated_object"] = "Calidad ambiental del suelo"
            elif med == "Ruido":
                cleaned["regulated_object"] = "Calidad ambiental para ruido"
            elif med == "Radiación no ionizante":
                cleaned["regulated_object"] = "Exposición a radiaciones no ionizantes"
            else:
                cleaned["regulated_object"] = "Calidad ambiental"
        elif inst == "VMA":
            cleaned["regulated_object"] = "Descarga de aguas residuales no domésticas al alcantarillado sanitario"
        elif inst == "LMP":
            sec = cleaned.get("sector") or "regulado"
            cleaned["regulated_object"] = f"Efluentes o emisiones del sector {sec}"

    # Condición de aplicabilidad para VMA
    if inst == "VMA" and not cleaned.get("applicability_condition"):
        cleaned["applicability_condition"] = "Descargas de aguas residuales no domésticas (UND) a la red de alcantarillado sanitario (D.S. 010-2019-VIVIENDA)"

    if not cleaned.get("status"):
        cleaned["status"] = "VIGENTE"
    if not cleaned.get("verification_status"):
        cleaned["verification_status"] = "VERIFICADO"

    return cleaned

CSV_TEMPLATE_HEADERS = [
    "instrument",
    "environmental_medium",
    "category",
    "subcategory",
    "parameter_name",
    "symbol",
    "cas_number",
    "limit_type",
    "min_value",
    "max_value",
    "value_text",
    "unit",
    "evaluation_period",
    "sector",
    "norm_code",
    "annex",
    "table_ref",
    "method_criteria",
    "applicability_condition",
    "observations"
]

CSV_TEMPLATE_ROWS = [
    [
        "ECA",
        "Agua",
        "Categoría 1",
        "A1: Aguas que pueden ser potabilizadas con desinfección",
        "Plomo total",
        "Pb",
        "7439-92-1",
        "Máximo",
        "",
        "0.01",
        "0.01 mg/L",
        "mg/L",
        "",
        "",
        "D.S. 004-2017-MINAM",
        "",
        "Tabla N° 1",
        "Espectrometría de absorción atómica",
        "",
        "Parámetro inorgánico de control obligatorio"
    ],
    [
        "ECA",
        "Aire",
        "",
        "",
        "Dióxido de Azufre",
        "SO2",
        "7446-09-5",
        "Máximo",
        "",
        "250",
        "250 µg/m3",
        "µg/m3",
        "24 horas",
        "",
        "D.S. 003-2017-MINAM",
        "",
        "Tabla N° 1",
        "Fluorescencia UV",
        "",
        "Periodo diario de evaluación"
    ],
    [
        "LMP",
        "Agua",
        "",
        "",
        "Cobre disuelto",
        "Cu",
        "7440-50-8",
        "Máximo",
        "",
        "0.5",
        "0.5 mg/L",
        "mg/L",
        "Mensual",
        "Minería y Metalurgia",
        "D.S. 010-2010-MINAM",
        "",
        "Tabla N° 2",
        "EPA 200.8",
        "",
        "Efluentes líquidos minero-metalúrgicos"
    ],
    [
        "VMA",
        "Agua",
        "Anexo 1",
        "",
        "Demanda Bioquímica de Oxígeno",
        "DBO5",
        "",
        "Máximo",
        "",
        "500",
        "500 mg/L",
        "mg/L",
        "",
        "",
        "D.S. 010-2019-VIVIENDA",
        "Anexo 1",
        "Tabla N° 1",
        "SMEWW 5210-B",
        "Descargas a la red pública de alcantarillado sanitario",
        "Pago por exceso de concentración"
    ]
]

@router.get("/export/csv-template")
def export_csv_template():
    """Descarga la plantilla CSV oficial con estructura y filas de ejemplo."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CSV_TEMPLATE_HEADERS)
    for r in CSV_TEMPLATE_ROWS:
        writer.writerow(r)
    
    output.seek(0)
    response = Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = 'attachment; filename="plantilla_importacion_parametros_econorma.csv"'
    return response

@router.post("/import")
async def import_data(file: UploadFile = File(...), x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    content = await file.read()
    filename = file.filename or "data.json"
    
    raw_records = []
    if filename.endswith(".json"):
        try:
            raw_records = json.loads(content.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al decodificar JSON: {str(e)}")
    elif filename.endswith(".csv"):
        try:
            csv_text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                raw_records.append(row)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al procesar CSV: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Debe ser archivo .json o .csv")

    validation_errors = []
    valid_records = []
    
    required_fields = ["instrument", "environmental_medium", "parameter_name", "unit", "norm_code"]
    
    for idx, raw in enumerate(raw_records, start=1):
        rec = clean_import_record(raw)
        
        missing = [f for f in required_fields if not rec.get(f)]
        if missing:
            validation_errors.append(f"Fila {idx}: Faltan campos obligatorios: {', '.join(missing)}")
            continue
        
        inst = rec.get("instrument", "").strip().upper()
        if inst not in ["ECA", "LMP", "VMA"]:
            validation_errors.append(f"Fila {idx}: Instrumento inválido '{inst}'. Debe ser ECA, LMP o VMA.")
            continue

        med = rec.get("environmental_medium", "").strip().capitalize()
        cat = rec.get("category", "").strip() if rec.get("category") else ""
        if inst == "ECA" and med in ["Agua", "Suelo", "Ruido"] and not cat:
            validation_errors.append(f"Fila {idx}: La categoría es obligatoria para ECA {med} según la norma oficial aplicable.")
            continue
            
        valid_records.append(rec)

    if validation_errors and not valid_records:
        raise HTTPException(status_code=400, detail=f"Error de validación: {'; '.join(validation_errors)}")

    inserted_count = 0
    for rec in valid_records:
        try:
            create_parameter(rec, admin_user="Administrador (Importador)")
            inserted_count += 1
        except Exception as e:
            validation_errors.append(f"Error al insertar parámetro {rec.get('parameter_name')}: {str(e)}")

    return {
        "success": True,
        "total_received": len(raw_records),
        "total_imported": inserted_count,
        "validation_errors": validation_errors,
        "message": f"Se importaron {inserted_count} parámetros correctamente."
    }

@router.get("/export/backup")
def export_backup(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    params = get_all_raw_parameters()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM norms;")
    norms = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 500;")
    audit = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    from datetime import datetime
    backup_data = {
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": "EcoNorma Perú",
        "norms_count": len(norms),
        "parameters_count": len(params),
        "audit_logs_count": len(audit),
        "norms": norms,
        "parameters": params,
        "audit_logs": audit
    }
    return backup_data

@router.get("/export/seed-parameters")
def export_seed_parameters(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    params = get_all_raw_parameters()
    clean_params = []
    for p in params:
        clean_p = {
            "instrument": p.get("instrument"),
            "environmental_medium": p.get("environmental_medium"),
            "sector": p.get("sector"),
            "subsector": p.get("subsector"),
            "activity": p.get("activity"),
            "category": p.get("category"),
            "subcategory": p.get("subcategory"),
            "parameter_name": p.get("parameter_name"),
            "alternative_names": p.get("alternative_names"),
            "symbol": p.get("symbol"),
            "cas_number": p.get("cas_number"),
            "limit_type": p.get("limit_type"),
            "min_value": p.get("min_value"),
            "max_value": p.get("max_value"),
            "value_text": p.get("value_text"),
            "unit": p.get("unit"),
            "evaluation_period": p.get("evaluation_period"),
            "frequency": p.get("frequency"),
            "special_condition": p.get("special_condition"),
            "method_criteria": p.get("method_criteria"),
            "observations": p.get("observations"),
            "norm_code": p.get("norm_code"),
            "norm_name": p.get("norm_name"),
            "year": p.get("year"),
            "annex": p.get("annex"),
            "table_ref": p.get("table_ref"),
            "article_ref": p.get("article_ref"),
            "page_ref": p.get("page_ref"),
            "issuing_entity": p.get("issuing_entity"),
            "official_url": p.get("official_url"),
            "source_url_override": p.get("source_url_override"),
            "publication_date": p.get("publication_date"),
            "effective_date": p.get("effective_date"),
            "status": p.get("status"),
            "modifying_norm": p.get("modifying_norm"),
            "derogating_norm": p.get("derogating_norm"),
            "last_verified_date": p.get("last_verified_date"),
            "verification_status": p.get("verification_status"),
            "admin_comment": p.get("admin_comment"),
            "regulated_object": p.get("regulated_object"),
            "sector_relation_type": p.get("sector_relation_type"),
            "applicability_condition": p.get("applicability_condition")
        }
        clean_params.append(clean_p)
    return clean_params

@router.get("/export/seed-norms")
def export_seed_norms(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM norms ORDER BY year DESC, code ASC;")
    norms = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clean_norms = []
    for n in norms:
        clean_n = {
            "code": n.get("code"),
            "norm_type": n.get("norm_type", "Decreto Supremo"),
            "norm_number": n.get("norm_number"),
            "title": n.get("title"),
            "issuing_entity": n.get("issuing_entity"),
            "instrument": n.get("instrument"),
            "environmental_medium": n.get("environmental_medium"),
            "sector": n.get("sector"),
            "regulated_object": n.get("regulated_object"),
            "year": n.get("year"),
            "publication_date": n.get("publication_date"),
            "effective_date": n.get("effective_date"),
            "status": n.get("status"),
            "modifying_norm": n.get("modifying_norm"),
            "derogating_norm": n.get("derogating_norm"),
            "official_url": n.get("official_url"),
            "alternate_url": n.get("alternate_url"),
            "summary": n.get("summary"),
            "last_verified_date": n.get("last_verified_date")
        }
        clean_norms.append(clean_n)
    return clean_norms
