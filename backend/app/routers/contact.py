"""
Router de Contacto y Reporte de Observaciones para EcoNorma Perú
Recibe mensajes de retroalimentación, observaciones normativas y sugerencias.
"""
from fastapi import APIRouter, HTTPException
from ..models import ContactSubmission
from ..database import save_inquiry

router = APIRouter(prefix="/api/contact", tags=["Contacto"])

@router.post("")
def submit_contact(submission: ContactSubmission):
    if not submission.name or not submission.email or not submission.message:
        raise HTTPException(status_code=400, detail="Los campos Nombre, Correo y Mensaje son obligatorios.")
    
    inquiry_id = save_inquiry(
        name=submission.name.strip(),
        email=submission.email.strip(),
        inquiry_type=submission.inquiry_type,
        subject=submission.subject.strip(),
        message=submission.message.strip()
    )
    
    return {
        "success": True,
        "message": "Tu consulta u observación ha sido registrada exitosamente. Muchas gracias por contribuir a la confiabilidad de EcoNorma Perú.",
        "inquiry_id": inquiry_id
    }
