"""
Script de Verificación Integral de EcoNorma Perú
Comprueba integridad de la base de datos, relaciones de normas, parámetros y consultas.
"""
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database import init_db, get_db_connection, search_parameters, get_system_stats, get_norm_by_code
from backend.app.config import DB_PATH

def run_checks():
    print("=" * 60)
    print("INICIANDO PRUEBAS DE INTEGRIDAD ECONORMA PERÚ")
    print("=" * 60)

    # 1. Inicializar base de datos
    print("[1/5] Inicializando base de datos y cargando seeds...")
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Verificar conteos
    cursor.execute("SELECT COUNT(*) as c FROM norms;")
    norms_count = cursor.fetchone()["c"]
    cursor.execute("SELECT COUNT(*) as c FROM parameters;")
    params_count = cursor.fetchone()["c"]

    print(f" -> Normas registradas: {norms_count}")
    print(f" -> Parámetros ambientales registrados: {params_count}")
    assert norms_count > 0, "No se registraron normas"
    assert params_count > 0, "No se registraron parámetros"

    # 3. Validar integridad referencial
    print("[2/5] Comprobando integridad referencial y campos obligatorios...")
    cursor.execute("""
    SELECT p.id, p.parameter_name, p.norm_code
    FROM parameters p
    LEFT JOIN norms n ON p.norm_code = n.code
    WHERE n.code IS NULL;
    """)
    orphan_params = cursor.fetchall()
    if orphan_params:
        print(f"ALERTA: {len(orphan_params)} parámetros tienen códigos de norma no encontrados:")
        for op in orphan_params[:5]:
            print(f"  - ID {op['id']}: {op['parameter_name']} -> {op['norm_code']}")
        assert len(orphan_params) == 0, "Existen parámetros huérfanos sin norma registrada"
    else:
        print(" -> Todos los parámetros están correctamente vinculados a una norma oficial existente.")

    # 4. Probar consultas requeridas por el usuario
    print("[3/5] Probando búsquedas clave requeridas por el usuario...")
    test_terms = [
        "arsénico", "plomo", "mercurio", "cadmio", "DBO5", "DQO", "pH", "PM10", "PM2.5", "ruido"
    ]
    for term in test_terms:
        res, count = search_parameters(query=term, page=1, page_size=10)
        print(f" -> Búsqueda '{term}': {count} resultados encontrados.")
        assert count > 0, f"Búsqueda obligatoria '{term}' no arrojó resultados!"

    # 5. Probar detalles de normas
    print("[4/5] Probando recuperación de normas y sus parámetros...")
    test_norms = ["D.S. 004-2017-MINAM", "D.S. 003-2017-MINAM", "D.S. 011-2017-MINAM", "D.S. 010-2019-VIVIENDA"]
    for code in test_norms:
        norm = get_norm_by_code(code)
        assert norm is not None, f"Norma {code} no encontrada"
        p_len = len(norm.get("parameters", []))
        print(f" -> Norma {code}: {p_len} parámetros vinculados.")
        assert p_len > 0, f"Norma {code} no tiene parámetros asociados!"

    # 6. Estadísticas dinámicas
    print("[5/5] Probando endpoint de estadísticas dinámicas...")
    stats = get_system_stats()
    print(f" -> Estadísticas: Total {stats['total_parameters']} params en {stats['total_sectors']} sectores.")
    
    conn.close()
    print("=" * 60)
    print("¡TODAS LAS PRUEBAS DE INTEGRIDAD PASARON CON ÉXITO! (100% OK)")
    print("=" * 60)

if __name__ == "__main__":
    run_checks()
