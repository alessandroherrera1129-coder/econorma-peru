"""
Router del Comparador Ambiental de Cumplimiento Normativo
Permite contrastar resultados analíticos de laboratorio/monitoreo contra los límites normativos aplicables.
"""
from fastapi import APIRouter, HTTPException
from ..models import CompareRequest, CompareResponse
from ..database import get_parameter_by_id
from ..config import COMPARATOR_DISCLAIMER

router = APIRouter(prefix="/api/comparator", tags=["Comparador"])

@router.post("/evaluate", response_model=CompareResponse)
def evaluate_result(req: CompareRequest):
    param = get_parameter_by_id(req.parameter_id)
    if not param:
        raise HTTPException(status_code=404, detail="El parámetro normativo especificado no existe.")

    min_val = param.get("min_value")
    max_val = param.get("max_value")
    val = req.measured_value
    
    is_compliant = True
    percentage = None
    evaluation_text = ""

    # Caso 1: Rango (e.g. pH entre min_val y max_val)
    if min_val is not None and max_val is not None:
        if val < min_val:
            is_compliant = False
            evaluation_text = f"El valor {val} {param['unit']} es inferior al límite mínimo permitido de {min_val} {param['unit']}."
        elif val > max_val:
            is_compliant = False
            evaluation_text = f"El valor {val} {param['unit']} supera el límite máximo permitido de {max_val} {param['unit']}."
        else:
            is_compliant = True
            evaluation_text = f"El valor {val} {param['unit']} se encuentra dentro del rango normativo permitido [{min_val} - {max_val} {param['unit']}]."

    # Caso 2: Solo límite mínimo (e.g. Oxígeno Disuelto >= min_val)
    elif min_val is not None and max_val is None:
        if val < min_val:
            is_compliant = False
            percentage = round((val / min_val) * 100, 2)
            evaluation_text = f"El valor {val} {param['unit']} no alcanza el valor mínimo requerido de {min_val} {param['unit']} ({percentage}% del mínimo)."
        else:
            is_compliant = True
            percentage = round((val / min_val) * 100, 2)
            evaluation_text = f"El valor {val} {param['unit']} cumple con el requerimiento mínimo de {min_val} {param['unit']} ({percentage}% del mínimo)."

    # Caso 3: Solo límite máximo (e.g. Arsénico <= max_val)
    elif max_val is not None and min_val is None:
        if max_val > 0:
            percentage = round((val / max_val) * 100, 2)
        if val > max_val:
            is_compliant = False
            evaluation_text = f"El valor {val} {param['unit']} supera el límite máximo permitido de {max_val} {param['unit']} (representa el {percentage}% del límite normativo)."
        else:
            is_compliant = True
            evaluation_text = f"El valor {val} {param['unit']} cumple con el estándar y se encuentra dentro del límite máximo de {max_val} {param['unit']} (representa el {percentage}% del límite normativo)."

    else:
        # Sin valores numéricos computables directamente
        evaluation_text = f"Parámetro normativo cualitativo o descriptivo: {param.get('value_text', 'N/A')}."

    status_label = "Dentro del valor establecido" if is_compliant else "Supera el valor establecido"

    return CompareResponse(
        parameter_id=param["id"],
        parameter_name=param["parameter_name"],
        instrument=param["instrument"],
        category=param["category"],
        subcategory=param.get("subcategory"),
        norm_code=param["norm_code"],
        unit=param["unit"],
        min_value=min_val,
        max_value=max_val,
        measured_value=val,
        is_compliant=is_compliant,
        status_label=status_label,
        percentage_of_limit=percentage,
        evaluation_text=evaluation_text,
        disclaimer=COMPARATOR_DISCLAIMER
    )
