"""
Router Administrativo Seguro para EcoNorma Perú
Permite la gestión CRUD integral de parámetros, normas oficiales, resolución y prueba de URLs,
auditoría de cambios, detección de duplicados y copias de seguridad.
"""
from fastapi import APIRouter, HTTPException, Header, Query, UploadFile, File
from typing import Optional, List, Dict, Any
import json
import csv
import io
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
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Acceso no autorizado al panel de administración.")
    return True

@router.post("/login")
def admin_login(payload: Dict[str, str]):
    token = payload.get("token")
    if token == ADMIN_TOKEN:
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

@router.post("/import")
async def import_data(file: UploadFile = File(...), x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    content = await file.read()
    filename = file.filename or "data.json"
    
    records = []
    if filename.endswith(".json"):
        try:
            records = json.loads(content.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al decodificar JSON: {str(e)}")
    elif filename.endswith(".csv"):
        try:
            csv_text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                records.append(row)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al procesar CSV: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Debe ser archivo .json o .csv")

    validation_errors = []
    valid_records = []
    
    required_fields = ["instrument", "environmental_medium", "category", "parameter_name", "unit", "norm_code"]
    
    for idx, rec in enumerate(records, start=1):
        missing = [f for f in required_fields if not rec.get(f)]
        if missing:
            validation_errors.append(f"Fila {idx}: Faltan campos obligatorios: {', '.join(missing)}")
            continue
        
        inst = rec.get("instrument", "").upper()
        if inst not in ["ECA", "LMP", "VMA"]:
            validation_errors.append(f"Fila {idx}: Instrumento inválido '{inst}'. Debe ser ECA, LMP o VMA.")
            continue
            
        valid_records.append(rec)

    inserted_count = 0
    for rec in valid_records:
        try:
            create_parameter(rec, admin_user="Administrador (Importador)")
            inserted_count += 1
        except Exception as e:
            validation_errors.append(f"Error al insertar parámetro {rec.get('parameter_name')}: {str(e)}")

    return {
        "success": True,
        "total_received": len(records),
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
