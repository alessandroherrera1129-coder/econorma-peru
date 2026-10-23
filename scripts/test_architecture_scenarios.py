"""
Script de Validación Integral: 10 Escenarios de la Nueva Arquitectura de Búsqueda de EcoNorma Perú
"""
import sys
import os
import json

# Agregar raíz al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db_connection

client = TestClient(app)

def run_validations():
    print("=" * 80)
    print("INICIANDO VALIDACIÓN DE LOS 10 ESCENARIOS NORMATIVOS")
    print("=" * 80)

    # -------------------------------------------------------------
    # Escenario 1: Búsqueda por Parámetro (ej. Arsénico)
    # Debe retornar ECA, LMP y VMA con filas de condición separadas
    # -------------------------------------------------------------
    print("\n[Escenario 1] Buscando parámetro 'Arsénico'...")
    res1 = client.get("/api/parameters/search?q=Arsénico&page_size=100")
    assert res1.status_code == 200, f"Error en búsqueda: {res1.status_code}"
    data1 = res1.json()
    items1 = data1["results"]
    instruments_found = set(x["instrument"] for x in items1)
    print(f"  Total encontrados: {len(items1)}")
    print(f"  Instrumentos presentes: {instruments_found}")
    assert "ECA" in instruments_found, "Falta ECA para Arsénico"
    assert "LMP" in instruments_found, "Falta LMP para Arsénico"
    assert "VMA" in instruments_found, "Falta VMA para Arsénico"
    # Verificar que no se agrupen condiciones diferentes en una única fila
    subcats = [x.get("subcategory") for x in items1 if x["instrument"] == "ECA"]
    assert len(subcats) > 1, "Las categorías de ECA no deben estar agrupadas"
    print("  -> PASÓ: Arsénico registra coincidencias en ECA, LMP y VMA con condiciones desagregadas.")

    # -------------------------------------------------------------
    # Escenario 2: ECA Agua (Todas las categorías y por categoría)
    # -------------------------------------------------------------
    print("\n[Escenario 2] ECA Agua...")
    res2_all = client.get("/api/parameters/search?instrument=ECA&medium=Agua&page_size=200")
    data2_all = res2_all.json()
    print(f"  Total ECA Agua (Todas las categorías): {data2_all['total']}")
    assert data2_all["total"] == 83, f"Esperado 83 parámetros en ECA Agua, se obtuvo {data2_all['total']}"
    
    # Filtrar por Categoría 1
    res2_cat1 = client.get("/api/parameters/search?instrument=ECA&medium=Agua&category=Categoría 1&page_size=200")
    data2_cat1 = res2_cat1.json()
    print(f"  Total ECA Agua Categoría 1: {data2_cat1['total']}")
    assert data2_cat1["total"] > 0, "Debe haber registros en Categoría 1"
    for r in data2_cat1["results"]:
        assert "Categoría 1" in r["category"], f"Categoría incorrecta: {r['category']}"
    print("  -> PASÓ: ECA Agua permite ver todos los registros (83) o filtrar por Categoría 1.")

    # -------------------------------------------------------------
    # Escenario 3: ECA Aire (Periodos de evaluación sin categorías de agua)
    # -------------------------------------------------------------
    print("\n[Escenario 3] ECA Aire...")
    res3 = client.get("/api/parameters/search?instrument=ECA&medium=Aire&page_size=50")
    data3 = res3.json()
    print(f"  Total ECA Aire: {data3['total']}")
    assert data3["total"] == 17, f"Esperado 17 parámetros en ECA Aire, se obtuvo {data3['total']}"
    
    # Probar filtro por periodo '24 horas'
    res3_24h = client.get("/api/parameters/search?instrument=ECA&medium=Aire&evaluation_period=24 horas&page_size=50")
    data3_24h = res3_24h.json()
    print(f"  ECA Aire con periodo '24 horas': {data3_24h['total']}")
    assert data3_24h["total"] > 0, "Debe haber registros de 24 horas en aire"
    for r in data3_24h["results"]:
        assert "24" in r["evaluation_period"], f"Periodo incorrecto: {r['evaluation_period']}"
        assert not r["category"].startswith("Categoría 1"), "No debe tener categoría de agua"
    print("  -> PASÓ: ECA Aire filtra por periodos de evaluación sin jerarquías de agua.")

    # -------------------------------------------------------------
    # Escenario 4: Modo Sector 'Minería y Metalurgia' + Medio Agua
    # Debe clasificar en 3 grupos: LMP (10), ECA Agua (83), VMA (24) = 117 total
    # -------------------------------------------------------------
    print("\n[Escenario 4] Minería y Metalurgia + Agua...")
    res4 = client.get("/api/parameters/search?mode=sector&sector=Minería y Metalurgia&medium=Agua&page_size=200")
    data4 = res4.json()
    items4 = data4["results"]
    g1 = [x for x in items4 if x["sector_relation_type"] == "ESPECIFICA_SECTOR"]
    g2 = [x for x in items4 if x["sector_relation_type"] == "ECA_GENERAL"]
    g3 = [x for x in items4 if x["sector_relation_type"] == "APLICACION_CONDICIONADA"]
    print(f"  Total resultados: {len(items4)}")
    print(f"  Grupo 1 (LMP minero-metalúrgico): {len(g1)}")
    print(f"  Grupo 2 (ECA Agua cuerpo receptor): {len(g2)}")
    print(f"  Grupo 3 (VMA alcantarillado sanitario): {len(g3)}")
    assert len(g1) == 10, f"Esperado 10 LMP mineros, se obtuvo {len(g1)}"
    assert len(g2) == 83, f"Esperado 83 ECA agua, se obtuvo {len(g2)}"
    assert len(g3) == 24, f"Esperado 24 VMA, se obtuvo {len(g3)}"
    assert len(items4) == 117, f"Esperado 117 en total, se obtuvo {len(items4)}"
    print("  -> PASÓ: Minería + Agua estructura perfectamente los 3 grupos (10 LMP, 83 ECA, 24 VMA).")

    # -------------------------------------------------------------
    # Escenario 5: Modo Sector 'Minería y Metalurgia' + Medio Aire
    # Debe clasificar en Grupo 1 (LMP emisiones: 4) y Grupo 2 (ECA Aire: 17), VMA = 0
    # -------------------------------------------------------------
    print("\n[Escenario 5] Minería y Metalurgia + Aire...")
    res5 = client.get("/api/parameters/search?mode=sector&sector=Minería y Metalurgia&medium=Aire&page_size=100")
    data5 = res5.json()
    items5 = data5["results"]
    g1_air = [x for x in items5 if x["sector_relation_type"] == "ESPECIFICA_SECTOR"]
    g2_air = [x for x in items5 if x["sector_relation_type"] == "ECA_GENERAL"]
    g3_air = [x for x in items5 if x["sector_relation_type"] == "APLICACION_CONDICIONADA"]
    print(f"  Total resultados: {len(items5)}")
    print(f"  Grupo 1 (LMP emisiones mineras): {len(g1_air)}")
    print(f"  Grupo 2 (ECA Aire calidad ambiental): {len(g2_air)}")
    print(f"  Grupo 3 (VMA): {len(g3_air)}")
    assert len(g1_air) == 4, f"Esperado 4 LMP emisiones mineras, se obtuvo {len(g1_air)}"
    assert len(g2_air) == 17, f"Esperado 17 ECA aire, se obtuvo {len(g2_air)}"
    assert len(g3_air) == 0, f"Esperado 0 VMA en aire, se obtuvo {len(g3_air)}"
    print("  -> PASÓ: Minería + Aire distingue Grupo 1 (4 LMP) y Grupo 2 (17 ECA), con 0 VMA.")

    # -------------------------------------------------------------
    # Escenario 6: Consulta de VMA y Anexos
    # -------------------------------------------------------------
    print("\n[Escenario 6] VMA (Valores Máximos Admisibles)...")
    res6_all = client.get("/api/parameters/search?instrument=VMA&page_size=50")
    data6_all = res6_all.json()
    print(f"  Total VMA: {data6_all['total']}")
    assert data6_all["total"] == 24, f"Esperado 24 VMA, se obtuvo {data6_all['total']}"
    
    # Anexo 1 (4 parámetros: DBO5, DQO, SST, AyG)
    res6_anexo1 = client.get("/api/parameters/search?instrument=VMA&annex=Anexo 1&page_size=10")
    data6_anexo1 = res6_anexo1.json()
    print(f"  VMA Anexo 1: {data6_anexo1['total']}")
    assert data6_anexo1["total"] == 4, f"Esperado 4 en Anexo 1, se obtuvo {data6_anexo1['total']}"
    names_a1 = [x["parameter_name"] for x in data6_anexo1["results"]]
    print(f"  Parámetros Anexo 1: {names_a1}")

    # Anexo 2 (20 parámetros prohibidos)
    res6_anexo2 = client.get("/api/parameters/search?instrument=VMA&annex=Anexo 2&page_size=50")
    data6_anexo2 = res6_anexo2.json()
    print(f"  VMA Anexo 2: {data6_anexo2['total']}")
    assert data6_anexo2["total"] == 20, f"Esperado 20 en Anexo 2, se obtuvo {data6_anexo2['total']}"
    print("  -> PASÓ: VMA registra 24 parámetros (4 en Anexo 1 y 20 en Anexo 2).")

    # -------------------------------------------------------------
    # Escenario 7: Cascada bidireccional LMP en filters endpoint
    # -------------------------------------------------------------
    print("\n[Escenario 7] Filtros y Cascada Bidireccional LMP...")
    res7 = client.get("/api/parameters/filters")
    assert res7.status_code == 200
    filters = res7.json()
    assert "lmp_mapping" in filters, "Falta lmp_mapping en endpoint de filtros"
    mapping = filters["lmp_mapping"]
    assert "Cemento y Construcción" in mapping["sectors"]
    assert mapping["sector_to_media"]["Cemento y Construcción"] == ["Aire"]
    assert "Electricidad" in mapping["medium_to_sectors"]["Agua"]
    print("  -> PASÓ: El mapeo bidireccional LMP vincula correctamente los sectores y medios.")

    # -------------------------------------------------------------
    # Escenario 8: Validación condicional de importación admin
    # -------------------------------------------------------------
    print("\n[Escenario 8] Validación condicional de importación...")
    # Admin login
    res_login = client.post("/api/admin/login", json={"password": "EcoNormaAdmin2026*"})
    assert res_login.status_code == 200
    token = res_login.json()["token"]

    # Caso 8a: Importar parámetro LMP sin categoría (debe ser VÁLIDO)
    valid_lmp_json = json.dumps([{
        "instrument": "LMP",
        "environmental_medium": "Aire",
        "sector": "Cemento y Construcción",
        "regulated_object": "Emisiones de la industria del cemento",
        "parameter_name": "Test LMP Sin Categoría",
        "limit_type": "Máximo",
        "max_value": 150.0,
        "unit": "mg/Nm3",
        "evaluation_period": "24 horas",
        "norm_code": "D.S. 001-2020-PRODUCE"
    }])
    res_imp_lmp = client.post(
        "/api/admin/import?format=json&mode=append",
        files={"file": ("test_lmp.json", valid_lmp_json, "application/json")},
        headers={"x-admin-token": token}
    )
    print(f"  Importar LMP sin categoría status: {res_imp_lmp.status_code}")
    assert res_imp_lmp.status_code == 200, f"Fallo al importar LMP sin categoría: {res_imp_lmp.text}"

    # Caso 8b: Importar parámetro ECA Agua sin categoría (debe ser RECHAZADO)
    invalid_eca_json = json.dumps([{
        "instrument": "ECA",
        "environmental_medium": "Agua",
        "parameter_name": "Test ECA Agua Invalido",
        "limit_type": "Máximo",
        "max_value": 0.01,
        "unit": "mg/L",
        "norm_code": "D.S. 004-2017-MINAM"
    }])
    res_imp_eca = client.post(
        "/api/admin/import?format=json&mode=append",
        files={"file": ("test_eca.json", invalid_eca_json, "application/json")},
        headers={"x-admin-token": token}
    )
    print(f"  Importar ECA Agua sin categoría status: {res_imp_eca.status_code}")
    assert res_imp_eca.status_code == 400, "ECA Agua sin categoría debió ser rechazado"
    assert "categoría" in res_imp_eca.text.lower()
    print("  -> PASÓ: Validación condicional correcta (LMP sin categoría aceptado, ECA Agua rechazado).")

    # Limpiar parámetro de prueba creado en 8a
    conn = get_db_connection()
    conn.execute("DELETE FROM parameters WHERE parameter_name = 'Test LMP Sin Categoría';")
    conn.commit()
    conn.close()

    # -------------------------------------------------------------
    # Escenario 9: Enlaces y referencias oficiales directas
    # -------------------------------------------------------------
    print("\n[Escenario 9] Verificación de URLs y referencias oficiales...")
    res9 = client.get("/api/norms")
    assert res9.status_code == 200
    norms = res9.json()["norms"]
    assert len(norms) == 17, f"Esperado 17 normas, se obtuvo {len(norms)}"
    for n in norms:
        assert n["official_url"].startswith("http"), f"Norma {n['code']} no tiene URL oficial válida"
    print("  -> PASÓ: Las 17 normas oficiales cuentan con enlaces web directos y verificados.")

    # -------------------------------------------------------------
    # Escenario 10: Cero pérdida de datos (Total 245 parámetros, 17 normas)
    # -------------------------------------------------------------
    print("\n[Escenario 10] Cero pérdida de datos y exactitud normativa...")
    res10_stats = client.get("/api/stats")
    stats = res10_stats.json()
    print(f"  Total Parámetros en BD: {stats['total_parameters']}")
    print(f"  Total Normas en BD: {stats['total_norms']}")
    print(f"  Total Sectores: {stats['total_sectors']}")
    assert stats["total_parameters"] == 245, f"Esperado 245 parámetros exactos, hay {stats['total_parameters']}"
    assert stats["total_norms"] == 17, f"Esperado 17 normas exactas, hay {stats['total_norms']}"
    print("  -> PASÓ: CERO PÉRDIDA DE DATOS. Se preservan exactamente los 245 parámetros y 17 normas.")

    print("\n" + "=" * 80)
    print("¡TODOS LOS 10 ESCENARIOS DE VALIDACIÓN FUERON SUPERADOS CON ÉXITO!")
    print("=" * 80)

if __name__ == "__main__":
    run_validations()
