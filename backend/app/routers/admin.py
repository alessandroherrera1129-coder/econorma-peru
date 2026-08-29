"""
Router Administrativo Seguro para EcoNorma Perú
Permite la gestión integral de parámetros, normas, importación masiva con validación y copias de seguridad.
"""
from fastapi import APIRouter, HTTPException, Header, Query, UploadFile, File
from typing import Optional, List, Dict, Any
import json
import csv
import io
from ..config import ADMIN_TOKEN
from ..database import (
    create_parameter, update_parameter, delete_parameter, get_parameter_by_id,
    get_all_raw_parameters, get_db_connection, compute_search_tokens
)
from ..models import ParameterCreate, ParameterUpdate

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

@router.get("/pending-verification")
def list_pending_verification(x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM parameters 
    WHERE verification_status = 'PENDIENTE DE VERIFICACIÓN' OR status = 'PENDIENTE DE VERIFICACIÓN'
    ORDER BY id DESC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"total": len(rows), "items": rows}

@router.post("/parameters")
def add_parameter(param: ParameterCreate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    pid = create_parameter(param.model_dump())
    return {"success": True, "parameter_id": pid, "message": "Parámetro creado exitosamente"}

@router.put("/parameters/{param_id}")
def edit_parameter(param_id: int, updates: ParameterUpdate, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    data = {k: v for k, v in updates.model_dump().items() if v is not None}
    success = update_parameter(param_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado para actualizar")
    return {"success": True, "message": "Parámetro actualizado exitosamente"}

@router.delete("/parameters/{param_id}")
def remove_parameter(param_id: int, x_admin_token: Optional[str] = Header(None)):
    verify_token(x_admin_token)
    success = delete_parameter(param_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado para eliminar")
    return {"success": True, "message": "Parámetro eliminado exitosamente"}

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

    # Validación previa rigurosa
    validation_errors = []
    valid_records = []
    
    required_fields = ["instrument", "environmental_medium", "category", "parameter_name", "unit", "norm_code"]
    
    for idx, rec in enumerate(records, start=1):
        missing = [f for f in required_fields if not rec.get(f)]
        if missing:
            validation_errors.append(f"Fila {idx}: Faltan campos obligatorios: {', '.join(missing)}")
            continue
        
        # Validar tipo de instrumento
        inst = rec.get("instrument", "").upper()
        if inst not in ["ECA", "LMP", "VMA"]:
            validation_errors.append(f"Fila {idx}: Instrumento inválido '{inst}'. Debe ser ECA, LMP o VMA.")
            continue
            
        valid_records.append(rec)

    # Inserción de registros válidos
    inserted_count = 0
    for rec in valid_records:
        try:
            create_parameter(rec)
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
    conn.close()
    
    backup_data = {
        "export_date": "2026-08-28",
        "system": "EcoNorma Perú",
        "norms_count": len(norms),
        "parameters_count": len(params),
        "norms": norms,
        "parameters": params
    }
    return backup_data
