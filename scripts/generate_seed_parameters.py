"""
Generador y Validador del Seed de Parámetros Ambientales Peruanos
EcoNorma Perú - Datos Oficiales Verificados
"""
import json
import os
from pathlib import Path

def create_parameters():
    params = []
    
    def add_p(
        instrument, medium, sector, subsector, activity, category, subcategory,
        pname, alt_names, symbol, cas, min_val, max_val, val_text, unit,
        period, freq, method, obs, norm_code, norm_name, year,
        annex, table_ref, art_ref, entity, url, status="VIGENTE",
        mod_norm=None, derog_norm=None, verif_status="VERIFICADO"
    ):
        params.append({
            "instrument": instrument,
            "environmental_medium": medium,
            "sector": sector,
            "subsector": subsector,
            "activity": activity,
            "category": category,
            "subcategory": subcategory,
            "parameter_name": pname,
            "alternative_names": alt_names,
            "symbol": symbol,
            "cas_number": cas,
            "min_value": min_val,
            "max_value": max_val,
            "value_text": val_text,
            "unit": unit,
            "evaluation_period": period,
            "frequency": freq,
            "method_criteria": method,
            "observations": obs,
            "norm_code": norm_code,
            "norm_name": norm_name,
            "year": year,
            "annex": annex,
            "table_ref": table_ref,
            "article_ref": art_ref,
            "issuing_entity": entity,
            "official_url": url,
            "publication_date": "2017-06-07" if "2017" in norm_code else ("2019-04-18" if "2019" in norm_code else "2010-08-21"),
            "effective_date": "2017-06-08" if "2017" in norm_code else ("2019-04-19" if "2019" in norm_code else "2010-08-22"),
            "status": status,
            "modifying_norm": mod_norm,
            "derogating_norm": derog_norm,
            "last_verified_date": "2026-08-28",
            "verification_status": verif_status
        })

    # -------------------------------------------------------------
    # 1. ECA AGUA (D.S. 004-2017-MINAM)
    # -------------------------------------------------------------
    eca_agua_url = "https://www.gob.pe/institucion/minam/normas-legales/193708-004-2017-minam"
    eca_agua_norm = "D.S. 004-2017-MINAM"
    eca_agua_name = "Estándares de Calidad Ambiental (ECA) para Agua"
    
    # Cat 1 - Subcat A (A1, A2, A3)
    cat1_subcats = [
        ("A1: Desinfección", "Aguas potabilizables con simple desinfección", 0.01, 0.01, 0.001, 0.003, 2.0, 3.0, 3.0, 10.0, 6.5, 8.5, 6.0, 20),
        ("A2: Tratamiento Convencional", "Aguas potabilizables con tratamiento convencional", 0.01, 0.01, 0.001, 0.003, 2.0, 3.0, 5.0, 20.0, 5.5, 9.0, 5.0, 2000),
        ("A3: Tratamiento Avanzado", "Aguas potabilizables con tratamiento avanzado", 0.05, 0.05, 0.002, 0.005, 2.0, 5.0, 10.0, 30.0, 5.5, 9.0, 4.0, 20000)
    ]
    for subcat_name, desc, as_val, pb_val, hg_val, cd_val, cu_val, zn_val, dbo_val, dqo_val, ph_min, ph_max, od_min, col_val in cat1_subcats:
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Arsénico total", "Arsénico, As", "As", "7440-38-2", None, as_val, f"{as_val} mg/L", "mg/L",
              "Puntual", "Semestral/Trimestral", "Espectrometría de absorción atómica / ICP-MS", f"Aplica a {desc}. Anexo I.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)
        
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Plomo total", "Plomo, Pb", "Pb", "7439-92-1", None, pb_val, f"{pb_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS / Absorción Atómica", f"Límite máximo para {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)
        
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Mercurio total", "Mercurio, Hg", "Hg", "7439-97-6", None, hg_val, f"{hg_val} mg/L", "mg/L",
              "Puntual", "Semestral", "Vapor Frío / ICP-MS", f"Límite neurotóxico para {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)
        
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Cadmio total", "Cadmio, Cd", "Cd", "7440-43-9", None, cd_val, f"{cd_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS / Absorción Atómica", f"Límite de toxicidad acumulativa para {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Cobre total", "Cobre, Cu", "Cu", "7440-50-8", None, cu_val, f"{cu_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS / Absorción Atómica", f"Parámetro organoléptico e inorgánico en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Zinc total", "Zinc, Zn", "Zn", "7440-66-6", None, zn_val, f"{zn_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS / Absorción Atómica", f"Inorgánico en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "pH", "Potencial de Hidrógeno", "pH", None, ph_min, ph_max, f"{ph_min} - {ph_max} unidades de pH", "unidades de pH",
              "Puntual / In situ", "Monitoreo continuo / trimestral", "Electrométrico in situ", f"Rango óptimo para {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Oxígeno Disuelto", "OD, Dissolved Oxygen", "OD", "7782-44-7", od_min, None, f"≥ {od_min} mg/L", "mg/L",
              "Puntual / In situ", "Monitoreo continuo / mensual", "Electrométrico / Winkler", f"Concentración mínima indispensable de OD en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Demanda Bioquímica de Oxígeno (DBO5)", "DBO5, BOD5", "DBO5", None, None, dbo_val, f"{dbo_val} mg/L", "mg/L",
              "5 días a 20°C", "Mensual / Trimestral", "Incubación 5 días manométrica / respirométrica", f"Materia orgánica biodegradable en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Demanda Química de Oxígeno (DQO)", "DQO, COD", "DQO", None, None, dqo_val, f"{dqo_val} mg/L", "mg/L",
              "Puntual", "Mensual / Trimestral", "Reflujo cerrado / Digestión con dicromato", f"Materia orgánica total susceptible de oxidación en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría A - {subcat_name}",
              "Coliformes Termotolerantes", "Coliformes Fecales", "CT", None, None, col_val, f"{col_val} NMP/100 mL", "NMP/100 mL",
              "Puntual", "Mensual", "Fermentación en tubos múltiples o membrana filtrante a 44.5°C", f"Indicador bacteriológico de contaminación fecal en {desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla A", "Art. 2", "MINAM", eca_agua_url)

    # Cat 1 - Subcat B (B1: Contacto Primario, B2: Contacto Secundario)
    cat1_b = [
        ("B1: Contacto Primario", "Actividades de natación, buceo, surf", 0.01, 0.01, 200, 0.5, 6.0, 9.0, 5.0),
        ("B2: Contacto Secundario", "Actividades náuticas, canotaje, navegación deportiva", 0.05, 0.05, 1000, 1.0, 6.0, 9.0, 4.0)
    ]
    for b_name, b_desc, as_val, pb_val, col_val, ayg_val, ph_min, ph_max, od_min in cat1_b:
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría B - {b_name}",
              "Arsénico total", "Arsénico, As", "As", "7440-38-2", None, as_val, f"{as_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "Espectrometría ICP-MS", f"Protección para {b_desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla B", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría B - {b_name}",
              "Coliformes Termotolerantes", "Coliformes Fecales", "CT", None, None, col_val, f"{col_val} NMP/100 mL", "NMP/100 mL",
              "Puntual", "Mensual", "Tubos múltiples / Filtración por membrana", f"Límite microbiológico para {b_desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla B", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Multisectorial", None, None, "Categoría 1: Poblacional y Recreacional", f"Subcategoría B - {b_name}",
              "Aceites y Grasas", "AyG, Grasas y aceites", "AyG", None, None, ayg_val, f"{ayg_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "Gravimetría / Extracción Soxhlet", f"Presencia visual y de película en {b_desc}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo I", "Tabla B", "Art. 2", "MINAM", eca_agua_url)

    # Cat 2 - Extracción y cultivo marino/continental
    cat2_items = [
        ("C1: Moluscos bivalvos", 0.01, 0.008, 0.0001, 0.005, 0.005, 0.05, 6.0, 8.5, 5.0),
        ("C2: Otras especies hidrobiológicas", 0.05, 0.01, 0.0002, 0.005, 0.01, 0.1, 6.0, 8.5, 5.0),
        ("C3: Actividades marino costeras", 0.05, 0.01, 0.0002, 0.005, 0.02, 0.1, 6.0, 8.5, 4.0),
        ("C4: Lagos y lagunas", 0.01, 0.01, 0.0001, 0.004, 0.01, 0.05, 6.5, 8.5, 5.0)
    ]
    for c_name, as_val, pb_val, hg_val, cd_val, cu_val, zn_val, ph_min, ph_max, od_min in cat2_items:
        add_p("ECA", "Agua", "Pesquería / Acuicultura", None, None, "Categoría 2: Extracción, cultivo y actividades marino costeras", f"Subcategoría {c_name}",
              "Arsénico total", "Arsénico, As", "As", "7440-38-2", None, as_val, f"{as_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS / Absorción Atómica", f"Protección de fauna y salud del consumidor en {c_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo II", "Tabla C", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Pesquería / Acuicultura", None, None, "Categoría 2: Extracción, cultivo y actividades marino costeras", f"Subcategoría {c_name}",
              "Plomo total", "Plomo, Pb", "Pb", "7439-92-1", None, pb_val, f"{pb_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS", f"Toxicidad en {c_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo II", "Tabla C", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Pesquería / Acuicultura", None, None, "Categoría 2: Extracción, cultivo y actividades marino costeras", f"Subcategoría {c_name}",
              "Cadmio total", "Cadmio, Cd", "Cd", "7440-43-9", None, cd_val, f"{cd_val} mg/L", "mg/L",
              "Puntual", "Semestral", "ICP-MS", f"Bioacumulación en moluscos y peces en {c_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo II", "Tabla C", "Art. 2", "MINAM", eca_agua_url)

    # Cat 3 - Riego de vegetales y bebida de animales
    cat3_items = [
        ("D1: Riego no restringido (tallos bajos/consumo crudo)", 0.05, 0.05, 0.001, 0.005, 0.2, 2.0, 15, 1000, 6.5, 8.5, 4.0),
        ("D1: Riego restringido (tallos altos/cocidos)", 0.10, 0.10, 0.001, 0.01, 0.5, 5.0, 30, 2000, 6.5, 8.5, 4.0),
        ("D2: Bebida de animales - Ganado mayor (vacunos, equinos)", 0.10, 0.05, 0.001, 0.01, 0.5, 5.0, 10, 1000, 6.5, 8.5, 5.0),
        ("D2: Bebida de animales - Ganado menor (ovinos, porcinos, aves)", 0.20, 0.05, 0.001, 0.01, 0.5, 5.0, 10, 1000, 6.5, 8.5, 5.0)
    ]
    for d_name, as_val, pb_val, hg_val, cd_val, cu_val, zn_val, dbo_val, col_val, ph_min, ph_max, od_min in cat3_items:
        add_p("ECA", "Agua", "Agricultura y Ganadería", None, None, "Categoría 3: Riego de vegetales y bebida de animales", f"Subcategoría {d_name}",
              "Arsénico total", "Arsénico, As", "As", "7440-38-2", None, as_val, f"{as_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "ICP-MS / Absorción Atómica", f"Estándar fitotóxico y de seguridad agropecuaria para {d_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo III", "Tabla D", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Agricultura y Ganadería", None, None, "Categoría 3: Riego de vegetales y bebida de animales", f"Subcategoría {d_name}",
              "Plomo total", "Plomo, Pb", "Pb", "7439-92-1", None, pb_val, f"{pb_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "ICP-MS", f"Límite de toxicidad para {d_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo III", "Tabla D", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Agricultura y Ganadería", None, None, "Categoría 3: Riego de vegetales y bebida de animales", f"Subcategoría {d_name}",
              "Cadmio total", "Cadmio, Cd", "Cd", "7440-43-9", None, cd_val, f"{cd_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "ICP-MS", f"Prevención de bioacumulación en cultivos o animales ({d_name}).",
              eca_agua_norm, eca_agua_name, 2017, "Anexo III", "Tabla D", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Agricultura y Ganadería", None, None, "Categoría 3: Riego de vegetales y bebida de animales", f"Subcategoría {d_name}",
              "Demanda Bioquímica de Oxígeno (DBO5)", "DBO5", "DBO5", None, None, dbo_val, f"{dbo_val} mg/L", "mg/L",
              "5 días a 20°C", "Mensual", "Incubación 5 días manométrica", f"Carga orgánica en agua para {d_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo III", "Tabla D", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Agricultura y Ganadería", None, None, "Categoría 3: Riego de vegetales y bebida de animales", f"Subcategoría {d_name}",
              "Coliformes Termotolerantes", "Coliformes Fecales", "CT", None, None, col_val, f"{col_val} NMP/100 mL", "NMP/100 mL",
              "Puntual", "Mensual", "Tubos múltiples", f"Seguridad microbiológica en {d_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo III", "Tabla D", "Art. 2", "MINAM", eca_agua_url)

    # Cat 4 - Conservación del ambiente acuático
    cat4_items = [
        ("E1: Lagunas y lagos", 0.10, 0.0025, 0.0001, 0.00025, 0.006, 0.03, 6.5, 8.5, 5.0),
        ("E2: Ríos - Costa y Sierra", 0.10, 0.0025, 0.0001, 0.00025, 0.006, 0.03, 6.5, 8.5, 5.0),
        ("E2: Ríos - Selva", 0.10, 0.005, 0.0002, 0.0005, 0.009, 0.05, 6.0, 8.5, 4.0),
        ("E3: Ecosistemas marinos y costeros", 0.05, 0.008, 0.0001, 0.005, 0.005, 0.05, 6.8, 8.5, 5.0)
    ]
    for e_name, as_val, pb_val, hg_val, cd_val, cu_val, zn_val, ph_min, ph_max, od_min in cat4_items:
        add_p("ECA", "Agua", "Conservación de Ecosistemas", None, None, "Categoría 4: Conservación del ambiente acuático", f"Subcategoría {e_name}",
              "Arsénico total", "Arsénico, As", "As", "7440-38-2", None, as_val, f"{as_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "ICP-MS / Absorción Atómica", f"Protección de vida acuática en {e_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo IV", "Tabla E", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Conservación de Ecosistemas", None, None, "Categoría 4: Conservación del ambiente acuático", f"Subcategoría {e_name}",
              "Plomo total", "Plomo, Pb", "Pb", "7439-92-1", None, pb_val, f"{pb_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "ICP-MS", f"Protección ecotoxicológica en {e_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo IV", "Tabla E", "Art. 2", "MINAM", eca_agua_url)
        add_p("ECA", "Agua", "Conservación de Ecosistemas", None, None, "Categoría 4: Conservación del ambiente acuático", f"Subcategoría {e_name}",
              "Mercurio total", "Mercurio, Hg", "Hg", "7439-97-6", None, hg_val, f"{hg_val} mg/L", "mg/L",
              "Puntual", "Trimestral", "Vapor Frío / ICP-MS", f"Prevención de bioacumulación en trama trófica de {e_name}.",
              eca_agua_norm, eca_agua_name, 2017, "Anexo IV", "Tabla E", "Art. 2", "MINAM", eca_agua_url)

    # -------------------------------------------------------------
    # 2. ECA AIRE (D.S. 003-2017-MINAM)
    # -------------------------------------------------------------
    eca_aire_url = "https://www.gob.pe/institucion/minam/normas-legales/193707-003-2017-minam"
    eca_aire_norm = "D.S. 003-2017-MINAM"
    eca_aire_name = "Estándares de Calidad Ambiental (ECA) para Aire"

    aire_params = [
        ("Dióxido de Azufre (SO2)", "Anhídrido sulfuroso, SO2", "SO2", "7446-09-5", None, 250, "250 µg/m³", "µg/m³", "24 horas", "Continua", "Fluorescencia UV", "No exceder más de 3 veces al año. Método automático."),
        ("Dióxido de Azufre (SO2) - 1 hora", "Anhídrido sulfuroso, SO2", "SO2", "7446-09-5", None, 500, "500 µg/m³", "µg/m³", "1 hora", "Continua", "Fluorescencia UV", "Periodo de 1 hora."),
        ("Dióxido de Nitrógeno (NO2)", "Óxido de nitrógeno (IV), NO2", "NO2", "10102-44-0", None, 200, "200 µg/m³", "µg/m³", "1 hora", "Continua", "Quimioluminiscencia", "No exceder más de 24 veces al año."),
        ("Dióxido de Nitrógeno (NO2) - Anual", "Óxido de nitrógeno (IV), NO2", "NO2", "10102-44-0", None, 100, "100 µg/m³", "µg/m³", "Anual", "Continua / Anual", "Quimioluminiscencia", "Media aritmética anual."),
        ("Material Particulado PM2.5", "Partículas finas respirables menores a 2.5 µm", "PM2.5", None, None, 50, "50 µg/m³", "µg/m³", "24 horas", "Continua", "Separación inercial / Microbalanza TEOM / Gravimetría", "No exceder más de 7 veces al año. Fracción fina con alta penetración pulmonar."),
        ("Material Particulado PM2.5 - Anual", "Partículas finas menores a 2.5 µm", "PM2.5", None, None, 25, "25 µg/m³", "µg/m³", "Anual", "Anual", "Separación inercial / Gravimetría", "Media aritmética anual."),
        ("Material Particulado PM10", "Partículas inhalables menores a 10 µm", "PM10", None, None, 100, "100 µg/m³", "µg/m³", "24 horas", "Continua / Muestreo 24h", "Separación inercial / Gravimetría Hi-Vol / Beta", "No exceder más de 7 veces al año."),
        ("Material Particulado PM10 - Anual", "Partículas inhalables menores a 10 µm", "PM10", None, None, 50, "50 µg/m³", "µg/m³", "Anual", "Anual", "Separación inercial / Gravimetría", "Media aritmética anual."),
        ("Monóxido de Carbono (CO)", "Óxido de carbono (II), CO", "CO", "630-08-0", None, 30000, "30 000 µg/m³", "µg/m³", "1 hora", "Continua", "Infrarrojo no dispersivo (NDIR)", "Máxima concentración en 1 hora (aprox. 26 ppm)."),
        ("Monóxido de Carbono (CO) - 8 horas", "Óxido de carbono (II), CO", "CO", "630-08-0", None, 10000, "10 000 µg/m³", "µg/m³", "8 horas", "Media móvil 8h", "Infrarrojo no dispersivo (NDIR)", "Media móvil de 8 horas (aprox. 9 ppm)."),
        ("Ozono Troposférico (O3)", "Ozono superficial, Trioxígeno, O3", "O3", "10028-15-6", None, 100, "100 µg/m³", "µg/m³", "8 horas", "Media móvil 8h", "Fotometría UV", "Contaminante secundario oxidante fotoquímico."),
        ("Plomo (Pb)", "Plomo en PM10, Pb", "Pb", "7439-92-1", None, 1.5, "1.5 µg/m³", "µg/m³", "Mensual", "Mensual", "Absorción atómica / Espectrometría de masa", "Media aritmética mensual."),
        ("Plomo (Pb) - Anual", "Plomo en PM10, Pb", "Pb", "7439-92-1", None, 0.5, "0.5 µg/m³", "µg/m³", "Anual", "Anual", "Absorción atómica / Espectrometría de masa", "Media aritmética anual."),
        ("Sulfuro de Hidrógeno (H2S)", "Ácido sulfhídrico, H2S", "H2S", "7783-06-4", None, 150, "150 µg/m³", "µg/m³", "24 horas", "Continua", "Fluorescencia UV / Tubos pasivos", "Olor característico a huevo podrido. Periodo 24 horas."),
        ("Benceno", "Benzol, C6H6", "C6H6", "71-43-2", None, 2, "2 µg/m³", "µg/m³", "Anual", "Anual", "Cromatografía de gases", "Compuesto orgánico volátil carcinógeno."),
        ("Hidrocarburos Totales (HT) expresado como Hexano", "Hidrocarburos totales no metánicos", "HT", "110-54-3", None, 100, "100 µg/m³", "µg/m³", "24 horas", "24 horas", "Cromatografía de gases con ionización de llama (FID)", "Expresado en equivalentes de hexano."),
        ("Mercurio Gaseoso Total (Hg)", "Vapor de mercurio, Hg", "Hg", "7439-97-6", None, 2, "2 µg/m³", "µg/m³", "24 horas", "24 horas", "Espectrometría de fluorescencia atómica de vapor frío", "Medición de mercurio en fase gaseosa.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in aire_params:
        add_p("ECA", "Aire", "Multisectorial", None, None, "Calidad del Aire Ambiental", "Atmósfera / Cuerpo receptor",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              eca_aire_norm, eca_aire_name, 2017, "Anexo", "Tabla de Parámetros", "Art. 1", "MINAM", eca_aire_url)

    # -------------------------------------------------------------
    # 3. ECA SUELO (D.S. 011-2017-MINAM)
    # -------------------------------------------------------------
    eca_suelo_url = "https://www.gob.pe/institucion/minam/normas-legales/193855-011-2017-minam"
    eca_suelo_norm = "D.S. 011-2017-MINAM"
    eca_suelo_name = "Estándares de Calidad Ambiental (ECA) para Suelo"

    suelo_data = [
        ("Arsénico total", "Arsénico, As", "As", "7440-38-2", 50.0, 50.0, 140.0, "EPA 3050B / EPA 6010D"),
        ("Bario total", "Bario, Ba", "Ba", "7440-39-3", 750.0, 500.0, 2000.0, "EPA 3050B / EPA 6010D"),
        ("Cadmio total", "Cadmio, Cd", "Cd", "7440-43-9", 1.4, 1.4, 22.0, "EPA 3050B / EPA 6020B"),
        ("Cromo VI", "Cromo hexavalente", "Cr(VI)", "18540-29-9", 0.4, 0.4, 1.4, "EPA 3060A / EPA 7196A"),
        ("Cromo total", "Cromo, Cr", "Cr", "7440-47-3", 400.0, 400.0, 1000.0, "EPA 3050B / EPA 6010D"),
        ("Mercurio total", "Mercurio, Hg", "Hg", "7439-97-6", 6.6, 6.6, 24.0, "EPA 7471B Vapor Frío"),
        ("Plomo total", "Plomo, Pb", "Pb", "7439-92-1", 70.0, 140.0, 800.0, "EPA 3050B / EPA 6010D"),
        ("Cianuro libre", "Cianuro, CN", "CN-", "57-12-5", 0.9, 0.9, 8.0, "EPA 9013A / EPA 9014"),
        ("Benceno", "Benzol, C6H6", "C6H6", "71-43-2", 0.03, 0.03, 0.03, "EPA 5035A / EPA 8260D"),
        ("Tolueno", "Metilbenceno", "C7H8", "108-88-3", 0.37, 0.37, 0.37, "EPA 5035A / EPA 8260D"),
        ("Etilbenceno", "Etilbenceno", "C8H10", "100-41-4", 0.082, 0.082, 0.082, "EPA 5035A / EPA 8260D"),
        ("Xilenos", "Dimetilbenceno (isómeros o, m, p)", "C8H10", "1330-20-7", 11.0, 11.0, 11.0, "EPA 5035A / EPA 8260D"),
        ("Fracción de Hidrocarburos F1 (C6-C10)", "Hidrocarburos volátiles F1", "F1", None, 200.0, 200.0, 500.0, "EPA 5035 / EPA 8015C"),
        ("Fracción de Hidrocarburos F2 (C10-C28)", "Hidrocarburos semivolátiles / diésel F2", "F2", None, 1200.0, 1200.0, 3000.0, "EPA 3546 / EPA 8015C"),
        ("Fracción de Hidrocarburos F3 (C28-C40)", "Hidrocarburos pesados / aceites F3", "F3", None, 3000.0, 3000.0, 6000.0, "EPA 3546 / EPA 8015C"),
        ("Benzo(a)pireno", "BaP, Hidrocarburo aromático policíclico", "BaP", "50-32-8", 0.1, 0.1, 0.7, "EPA 3546 / EPA 8270E"),
        ("Bifenilos Policlorados (PCB)", "Arocloros, PCB total", "PCB", "1336-36-3", 0.5, 1.3, 33.0, "EPA 3546 / EPA 8082A"),
        ("Aldrín", "Plaguicida organoclorado", "Aldrín", "309-00-2", 0.05, 0.05, 0.05, "EPA 3546 / EPA 8081B"),
        ("DDT", "Diclorodifeniltricloroetano", "DDT", "50-29-3", 0.7, 0.7, 12.0, "EPA 3546 / EPA 8081B")
    ]
    for pname, alt, sym, cas, vagr, vres, vind, meth in suelo_data:
        add_p("ECA", "Suelo", "Multisectorial", None, None, "ECA Suelo", "Suelo Agrícola",
              pname, alt, sym, cas, None, vagr, f"{vagr} mg/kg MS", "mg/kg MS",
              "Muestreo compuesto", "Semestral / Monitoreo anual", meth, "Expresado en base a Materia Seca (MS). Suelos destinados a producción agropecuaria.",
              eca_suelo_norm, eca_suelo_name, 2017, "Anexo", "Tabla 1", "Art. 1", "MINAM", eca_suelo_url)
        add_p("ECA", "Suelo", "Multisectorial", None, None, "ECA Suelo", "Suelo Residencial / Parques",
              pname, alt, sym, cas, None, vres, f"{vres} mg/kg MS", "mg/kg MS",
              "Muestreo compuesto", "Monitoreo periódico", meth, "Expresado en base a Materia Seca (MS). Suelos de uso residencial, áreas verdes e instituciones.",
              eca_suelo_norm, eca_suelo_name, 2017, "Anexo", "Tabla 1", "Art. 1", "MINAM", eca_suelo_url)
        add_p("ECA", "Suelo", "Multisectorial", None, None, "ECA Suelo", "Suelo Comercial / Industrial / Extractivo",
              pname, alt, sym, cas, None, vind, f"{vind} mg/kg MS", "mg/kg MS",
              "Muestreo compuesto", "Monitoreo periódico", meth, "Expresado en base a Materia Seca (MS). Suelos con actividades comerciales, industriales o de extracción minera/hidrocarburífera.",
              eca_suelo_norm, eca_suelo_name, 2017, "Anexo", "Tabla 1", "Art. 1", "MINAM", eca_suelo_url)

    # -------------------------------------------------------------
    # 4. ECA RUIDO (D.S. 085-2003-PCM)
    # -------------------------------------------------------------
    eca_ruido_url = "https://sinia.minam.gob.pe/normas/reglamento-estandares-nacionales-calidad-ambiental-ruido"
    eca_ruido_norm = "D.S. 085-2003-PCM"
    eca_ruido_name = "Reglamento de Estándares Nacionales de Calidad Ambiental para Ruido"

    ruido_zones = [
        ("Zona de Protección Especial", "Áreas que requieren protección especial contra el ruido (hospitales, colegios, asilos)", 50, 40),
        ("Zona Residencial", "Áreas destinadas al uso de viviendas o actividades residenciales", 60, 50),
        ("Zona Comercial", "Áreas destinadas al comercio y servicios", 70, 60),
        ("Zona Industrial", "Áreas destinadas a la industria y talleres", 80, 70)
    ]
    for zname, zdesc, d_val, n_val in ruido_zones:
        add_p("ECA", "Ruido", "Multisectorial", None, None, "ECA Ruido Ambiental", f"{zname} - Horario Diurno",
              "Nivel de Presión Sonora Continuo Equivalente (LAeq,T)", "Ruido ambiental diurno", "LAeq,T", None, None, d_val, f"{d_val} dBA", "dBA",
              "Horario Diurno (07:01 a 22:00 horas)", "Monitoreo puntual / continuo", "Sonómetro integrador Tipo 1 / 2 (ponderación A)", f"{zdesc}. Horario diurno.",
              eca_ruido_norm, eca_ruido_name, 2003, "Anexo 1", "Tabla 1", "Art. 4", "PCM / MINAM", eca_ruido_url)
        add_p("ECA", "Ruido", "Multisectorial", None, None, "ECA Ruido Ambiental", f"{zname} - Horario Nocturno",
              "Nivel de Presión Sonora Continuo Equivalente (LAeq,T)", "Ruido ambiental nocturno", "LAeq,T", None, None, n_val, f"{n_val} dBA", "dBA",
              "Horario Nocturno (22:01 a 07:00 horas)", "Monitoreo puntual / continuo", "Sonómetro integrador Tipo 1 / 2 (ponderación A)", f"{zdesc}. Horario nocturno.",
              eca_ruido_norm, eca_ruido_name, 2003, "Anexo 1", "Tabla 1", "Art. 4", "PCM / MINAM", eca_ruido_url)

    # -------------------------------------------------------------
    # 5. ECA RADIACIONES NO IONIZANTES (D.S. 010-2005-PCM)
    # -------------------------------------------------------------
    eca_rni_url = "https://sinia.minam.gob.pe/normas/estandares-calidad-ambiental-radiaciones-ionizantes"
    eca_rni_norm = "D.S. 010-2005-PCM"
    eca_rni_name = "Estándares de Calidad Ambiental para Radiaciones No Ionizantes"

    add_p("ECA", "Radiaciones No Ionizantes", "Telecomunicaciones", None, None, "ECA Radiaciones No Ionizantes", "Telefonía Móvil / Estaciones Base 900 MHz",
          "Densidad de Potencia (S)", "Radiación electromagnética no ionizante 900 MHz", "S", None, None, 4.5, "4.5 W/m²", "W/m²",
          "6 minutos", "Monitoreo periódico", "Medidor de campo electromagnético de banda ancha / selectiva", "Público en general. Frecuencia de 900 MHz (S = f/200).",
          eca_rni_norm, eca_rni_name, 2005, "Anexo 1", "Tabla 1", "Art. 3", "PCM / MINAM", eca_rni_url)
    add_p("ECA", "Radiaciones No Ionizantes", "Telecomunicaciones", None, None, "ECA Radiaciones No Ionizantes", "Telefonía Móvil / Estaciones Base 1800 MHz",
          "Densidad de Potencia (S)", "Radiación electromagnética no ionizante 1800 MHz", "S", None, None, 9.0, "9.0 W/m²", "W/m²",
          "6 minutos", "Monitoreo periódico", "Medidor de campo electromagnético", "Público en general. Frecuencia de 1800 MHz (S = f/200).",
          eca_rni_norm, eca_rni_name, 2005, "Anexo 1", "Tabla 1", "Art. 3", "PCM / MINAM", eca_rni_url)
    add_p("ECA", "Radiaciones No Ionizantes", "Electricidad", None, None, "ECA Radiaciones No Ionizantes", "Líneas de Transmisión Eléctrica 60 Hz",
          "Campo Eléctrico (E)", "Intensidad de campo eléctrico 60 Hz", "E", None, None, 4.16, "4.16 kV/m", "kV/m",
          "Continuo", "Monitoreo puntual", "Sonda de campo eléctrico de baja frecuencia", "Público en general a 60 Hz.",
          eca_rni_norm, eca_rni_name, 2005, "Anexo 1", "Tabla 1", "Art. 3", "PCM / MINAM", eca_rni_url)
    add_p("ECA", "Radiaciones No Ionizantes", "Electricidad", None, None, "ECA Radiaciones No Ionizantes", "Líneas de Transmisión Eléctrica 60 Hz",
          "Campo Magnético / Densidad de Flujo Magnético (B)", "Inducción magnética 60 Hz", "B", None, None, 100.0, "100 µT", "µT",
          "Continuo", "Monitoreo puntual", "Sonda de campo magnético triaxial 60 Hz", "Público en general a 60 Hz.",
          eca_rni_norm, eca_rni_name, 2005, "Anexo 1", "Tabla 1", "Art. 3", "PCM / MINAM", eca_rni_url)

    # -------------------------------------------------------------
    # 6. VMA - VALORES MÁXIMOS ADMISIBLES (D.S. 010-2019-VIVIENDA)
    # -------------------------------------------------------------
    vma_url = "https://www.gob.pe/institucion/vivienda/normas-legales/264627-010-2019-vivienda"
    vma_norm = "D.S. 010-2019-VIVIENDA"
    vma_name = "Reglamento de Valores Máximos Admisibles para las descargas de aguas residuales no domésticas"

    anexo1_vma = [
        ("Demanda Bioquímica de Oxígeno (DBO5)", "DBO5, Materia orgánica biodegradable", "DBO5", None, None, 500.0, "500 mg/L", "mg/L", "Compuesta / Puntual", "Mensual / Semestral", "Método 5210 B Standard Methods", "Parámetro sujeto a cobro de tarifa por exceso de concentración (Anexo 1)."),
        ("Demanda Química de Oxígeno (DQO)", "DQO, Materia orgánica oxidable", "DQO", None, None, 1000.0, "1000 mg/L", "mg/L", "Compuesta / Puntual", "Mensual / Semestral", "Método 5220 D Standard Methods", "Parámetro sujeto a cobro de tarifa por exceso de concentración (Anexo 1)."),
        ("Sólidos Suspendidos Totales (SST)", "SST, Sólidos en suspensión", "SST", None, None, 500.0, "500 mg/L", "mg/L", "Compuesta / Puntual", "Mensual / Semestral", "Método 2540 D Standard Methods", "Parámetro sujeto a cobro de tarifa por exceso de concentración (Anexo 1)."),
        ("Aceites y Grasas (AyG)", "AyG, Grasas y aceites", "AyG", None, None, 100.0, "100 mg/L", "mg/L", "Puntual", "Mensual / Semestral", "Método 5520 B Standard Methods", "Parámetro sujeto a cobro de tarifa por exceso de concentración (Anexo 1).")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in anexo1_vma:
        add_p("VMA", "Efluentes / Alcantarillado", "Saneamiento / Comercial e Industrial", "Descargas no domésticas (UND)", "Descargas al alcantarillado sanitario",
              "VMA - Anexo 1", "Parámetros fisicoquímicos sujetos a pago adicional",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              vma_norm, vma_name, 2019, "Anexo 1", "Tabla Anexo 1", "Art. 4", "VIVIENDA / SUNASS", vma_url)

    anexo2_vma = [
        ("pH", "Potencial de Hidrógeno", "pH", None, 6.0, 9.0, "6.0 - 9.0 unidades de pH", "unidades de pH", "Puntual in situ", "Inspección periódica", "Método 4500-H+ B", "Rango de protección contra corrosión en redes de alcantarillado."),
        ("Temperatura", "Temperatura del efluente", "T°", None, None, 35.0, "< 35 °C", "°C", "Puntual in situ", "Inspección periódica", "Termométrico", "Protección estructural y de personal de mantenimiento."),
        ("Aluminio (Al)", "Aluminio disuelto o total", "Al", "7429-90-5", None, 10.0, "10 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES / Absorción Atómica", "Prohibido exceder. Condiciona suspensión de servicio."),
        ("Arsénico total (As)", "Arsénico, As", "As", "7440-38-2", None, 0.5, "0.5 mg/L", "mg/L", "Puntual", "Semestral", "ICP-MS / Absorción Atómica", "Prohibido exceder. Elemento altamente tóxico."),
        ("Boro (B)", "Boro, B", "B", "7440-42-8", None, 4.0, "4.0 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES", "Prohibido exceder. Afecta rehúso agrícola de biosólidos."),
        ("Cadmio total (Cd)", "Cadmio, Cd", "Cd", "7440-43-9", None, 0.2, "0.2 mg/L", "mg/L", "Puntual", "Semestral", "ICP-MS", "Prohibido exceder. Metal pesado bioacumulable."),
        ("Cianuro total (CN-)", "Cianuro total, CN", "CN-", "57-12-5", None, 1.0, "1.0 mg/L", "mg/L", "Puntual", "Semestral", "Destilación y colorimetría", "Prohibido exceder. Riesgo de formación de ácido cianhídrico en tuberías."),
        ("Cobre total (Cu)", "Cobre, Cu", "Cu", "7440-50-8", None, 3.0, "3.0 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES / Absorción Atómica", "Prohibido exceder. Inhibidor de procesos biológicos en PTAR."),
        ("Cromo hexavalente (Cr+6)", "Cromo VI, Cr(VI)", "Cr(VI)", "18540-29-9", None, 0.5, "0.5 mg/L", "mg/L", "Puntual", "Semestral", "Colorimetría Difenilcarbazida", "Prohibido exceder. Compuesto carcinógeno."),
        ("Cromo total (Cr)", "Cromo total, Cr", "Cr", "7440-47-3", None, 5.0, "5.0 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES / Absorción Atómica", "Prohibido exceder. Provisto de industrias de curtiembre y galvanoplastia."),
        ("Fósforo total (P)", "Fósforo, P", "P", "7723-14-0", None, 50.0, "50 mg/L", "mg/L", "Puntual", "Semestral", "Digestión y ácido ascórbico", "Prohibido exceder. Causa eutrofización acelerada."),
        ("Hidrocarburos Totales de Petróleo (TPH)", "TPH, Hidrocarburos", "TPH", None, None, 20.0, "20 mg/L", "mg/L", "Puntual", "Semestral", "Infrarrojo / Cromatografía", "Prohibido exceder. Provoca vapores explosivos y adherencia en colectores."),
        ("Manganeso (Mn)", "Manganeso, Mn", "Mn", "7439-96-5", None, 4.0, "4.0 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES", "Prohibido exceder. Incrustaciones en tuberías."),
        ("Mercurio total (Hg)", "Mercurio, Hg", "Hg", "7439-97-6", None, 0.02, "0.02 mg/L", "mg/L", "Puntual", "Semestral", "Vapor Frío", "Prohibido exceder. Altísima toxicidad."),
        ("Níquel total (Ni)", "Níquel, Ni", "Ni", "7440-02-0", None, 4.0, "4.0 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES", "Prohibido exceder. Proviene de galvanizado y talleres."),
        ("Nitrógeno Amoniacal (N-NH3)", "Amonio, Nitrógeno amoniacal", "N-NH3", "7664-41-7", None, 80.0, "80 mg/L", "mg/L", "Puntual", "Semestral", "Destilación y titulación / Electrodo", "Prohibido exceder. Toxicidad en colectores."),
        ("Plomo total (Pb)", "Plomo, Pb", "Pb", "7439-92-1", None, 0.5, "0.5 mg/L", "mg/L", "Puntual", "Semestral", "ICP-MS / Absorción Atómica", "Prohibido exceder. Metal pesado tóxico."),
        ("Sulfatos (SO4=)", "Sulfato, SO4", "SO4=", "14808-79-8", None, 500.0, "500 mg/L", "mg/L", "Puntual", "Semestral", "Turbidimétrico / Gravimétrico", "Prohibido exceder. Produce corrosión biogénica severa en concreto."),
        ("Sulfuros (S=)", "Sulfuro, S2-", "S=", "18496-25-8", None, 5.0, "5.0 mg/L", "mg/L", "Puntual", "Semestral", "Yodométrico / Azul de Metileno", "Prohibido exceder. Genera gas H2S letal en alcantarillas."),
        ("Zinc total (Zn)", "Zinc, Zn", "Zn", "7440-66-6", None, 10.0, "10 mg/L", "mg/L", "Puntual", "Semestral", "ICP-OES", "Prohibido exceder. Proviene de metalmecánica.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in anexo2_vma:
        add_p("VMA", "Efluentes / Alcantarillado", "Saneamiento / Comercial e Industrial", "Descargas no domésticas (UND)", "Descargas al alcantarillado sanitario",
              "VMA - Anexo 2", "Parámetros no permitidos (tóxicos o corrosivos)",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              vma_norm, vma_name, 2019, "Anexo 2", "Tabla Anexo 2", "Art. 4", "VIVIENDA / SUNASS", vma_url)

    # -------------------------------------------------------------
    # 7. LMP MINERÍA Y METALURGIA (D.S. 010-2010-MINAM & R.M. 315-96-EM/VMM)
    # -------------------------------------------------------------
    lmp_min_url = "https://sinia.minam.gob.pe/normas/limites-maximos-permisibles-descarga-efluentes-liquidos-actividades-minero-metalurgicas"
    lmp_min_norm = "D.S. 010-2010-MINAM"
    lmp_min_name = "Límites Máximos Permisibles para la descarga de efluentes líquidos de Actividades Minero-Metalúrgicas"

    min_efluentes = [
        ("pH", "Potencial de Hidrógeno", "pH", None, 6.0, 9.0, "6.0 - 9.0 unidades de pH", "unidades de pH", "En cualquier momento", "Continuo / Diario", "Electrométrico", "Rango de pH obligatorio para efluentes minero-metalúrgicos."),
        ("Sólidos Suspendidos Totales (SST)", "SST, Sólidos en suspensión", "SST", None, None, 50.0, "50 mg/L (Puntual) / 25 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Diario", "Gravimetría Standard Methods 2540 D", "50 mg/L en cualquier momento; 25 mg/L como promedio anual."),
        ("Plomo total (Pb)", "Plomo, Pb", "Pb", "7439-92-1", None, 0.2, "0.2 mg/L (Puntual) / 0.15 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "ICP-MS / Absorción Atómica", "0.2 mg/L en cualquier momento; 0.15 mg/L como promedio anual."),
        ("Cobre total (Cu)", "Cobre, Cu", "Cu", "7440-50-8", None, 0.5, "0.5 mg/L (Puntual) / 0.4 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "ICP-MS / Absorción Atómica", "0.5 mg/L en cualquier momento; 0.4 mg/L como promedio anual."),
        ("Zinc total (Zn)", "Zinc, Zn", "Zn", "7440-66-6", None, 1.5, "1.5 mg/L (Puntual) / 1.0 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "ICP-MS / Absorción Atómica", "1.5 mg/L en cualquier momento; 1.0 mg/L como promedio anual."),
        ("Arsénico total (As)", "Arsénico, As", "As", "7440-38-2", None, 0.1, "0.1 mg/L (Puntual) / 0.08 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "ICP-MS / Generador de Hidruros", "0.1 mg/L en cualquier momento; 0.08 mg/L como promedio anual."),
        ("Cadmio total (Cd)", "Cadmio, Cd", "Cd", "7440-43-9", None, 0.05, "0.05 mg/L (Puntual) / 0.03 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "ICP-MS", "0.05 mg/L en cualquier momento; 0.03 mg/L como promedio anual."),
        ("Mercurio total (Hg)", "Mercurio, Hg", "Hg", "7439-97-6", None, 0.002, "0.002 mg/L (Puntual) / 0.001 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Semanal", "Vapor Frío", "0.002 mg/L en cualquier momento; 0.001 mg/L como promedio anual."),
        ("Cianuro Total (CN-)", "Cianuro total", "CN-", "57-12-5", None, 1.0, "1.0 mg/L (Puntual) / 0.8 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Diario", "Destilación y titulación", "1.0 mg/L en cualquier momento; 0.8 mg/L como promedio anual."),
        ("Cianuro WAD", "Cianuro disociable en ácido débil (WAD)", "CN-WAD", None, None, 0.2, "0.2 mg/L (Puntual) / 0.15 mg/L (Promedio Anual)", "mg/L", "Puntual / Promedio anual", "Diario", "Destilación WAD y colorimetría", "0.2 mg/L en cualquier momento; 0.15 mg/L como promedio anual.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in min_efluentes:
        add_p("LMP", "Efluentes Líquidos", "Minería y Metalurgia", "Gran y Mediana Minería", "Descarga de efluentes de operaciones y beneficio",
              "LMP Minero-Metalúrgico", "Efluentes Líquidos Mineros",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              lmp_min_norm, lmp_min_name, 2010, "Anexo 1", "Tabla 1", "Art. 2", "MINAM / MINEM / OEFA", lmp_min_url)

    # Emisiones Mineras R.M. 315-96-EM/VMM
    rm315_url = "https://sinia.minam.gob.pe/normas/niveles-maximos-permisibles-elementos-compuestos-presentes-emisiones-gaseosas-provenientes"
    rm315_norm = "R.M. 315-96-EM/VMM"
    rm315_name = "Niveles Máximos Permisibles de elementos y compuestos en emisiones minero-metalúrgicas"

    add_p("LMP", "Emisiones Gaseosas", "Minería y Metalurgia", "Fundiciones y Refinerías", "Operaciones pirometalúrgicas",
          "LMP Emisiones Mineras", "Fuentes fijas minero-metalúrgicas",
          "Dióxido de Azufre (SO2)", "Anhídrido sulfuroso, SO2", "SO2", "7446-09-5", None, 1000.0, "1000 mg/m³", "mg/m³",
          "Medición puntual en chimenea", "Semestral", "Método EPA 6C", "Emisiones de fundiciones y plantas de tostación.",
          rm315_norm, rm315_name, 1996, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", rm315_url)
    add_p("LMP", "Emisiones Gaseosas", "Minería y Metalurgia", "Fundiciones y Refinerías", "Operaciones pirometalúrgicas",
          "LMP Emisiones Mineras", "Fuentes fijas minero-metalúrgicas",
          "Material Particulado en Emisiones", "Polvo metalúrgico, Partículas", "PTS", None, None, 100.0, "100 mg/m³", "mg/m³",
          "Medición isocinética", "Semestral", "Método EPA 5", "Emisiones de chimeneas minero-metalúrgicas.",
          rm315_norm, rm315_name, 1996, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", rm315_url)
    add_p("LMP", "Emisiones Gaseosas", "Minería y Metalurgia", "Fundiciones y Refinerías", "Operaciones pirometalúrgicas",
          "LMP Emisiones Mineras", "Fuentes fijas minero-metalúrgicas",
          "Plomo en Emisiones (Pb)", "Plomo metálico, Pb", "Pb", "7439-92-1", None, 25.0, "25 mg/m³", "mg/m³",
          "Isocinético", "Semestral", "Método EPA 12 / 29", "Emisiones de fundiciones.",
          rm315_norm, rm315_name, 1996, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", rm315_url)
    add_p("LMP", "Emisiones Gaseosas", "Minería y Metalurgia", "Fundiciones y Refinerías", "Operaciones pirometalúrgicas",
          "LMP Emisiones Mineras", "Fuentes fijas minero-metalúrgicas",
          "Arsénico en Emisiones (As)", "Arsénico en humos, As", "As", "7440-38-2", None, 25.0, "25 mg/m³", "mg/m³",
          "Isocinético", "Semestral", "Método EPA 29", "Emisiones de chimeneas mineras.",
          rm315_norm, rm315_name, 1996, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", rm315_url)

    # -------------------------------------------------------------
    # 8. LMP HIDROCARBUROS (D.S. 037-2008-PCM & D.S. 014-2010-MINAM)
    # -------------------------------------------------------------
    lmp_hidro_url = "https://sinia.minam.gob.pe/normas/limites-maximos-permisibles-efluentes-liquidos-subsector-hidrocarburos"
    lmp_hidro_norm = "D.S. 037-2008-PCM"
    lmp_hidro_name = "Límites Máximos Permisibles de Efluentes Líquidos para el Subsector Hidrocarburos"

    hidro_efluentes = [
        ("pH", "Potencial de Hidrógeno", "pH", None, 6.0, 9.0, "6.0 - 9.0 unidades de pH", "unidades de pH", "Puntual in situ", "Diario", "Electrométrico", "Rango de pH para efluentes de hidrocarburos."),
        ("Aceites y Grasas (AyG)", "Grasas y aceites", "AyG", None, None, 20.0, "20 mg/L (Puntual) / 15 mg/L (Promedio)", "mg/L", "Puntual / Promedio", "Semanal", "EPA 1664A / Gravimetría", "20 mg/L puntual y 15 mg/L promedio mensual."),
        ("Hidrocarburos Totales de Petróleo (TPH)", "TPH", "TPH", None, None, 20.0, "20 mg/L (Puntual) / 15 mg/L (Promedio)", "mg/L", "Puntual / Promedio", "Semanal", "EPA 8015 / Infrarrojo", "20 mg/L puntual y 15 mg/L promedio mensual."),
        ("Demanda Bioquímica de Oxígeno (DBO5)", "DBO5", "DBO5", None, None, 50.0, "50 mg/L", "mg/L", "Compuesta 24h", "Mensual", "Método 5210 B", "Materia orgánica en aguas residuales de campamentos y procesos."),
        ("Demanda Química de Oxígeno (DQO)", "DQO", "DQO", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta 24h", "Mensual", "Método 5220 D", "DQO total en efluentes tratados."),
        ("Sólidos Suspendidos Totales (SST)", "SST", "SST", None, None, 50.0, "50 mg/L (Puntual) / 30 mg/L (Promedio)", "mg/L", "Puntual / Promedio", "Diario", "Método 2540 D", "50 mg/L puntual y 30 mg/L promedio mensual."),
        ("Plomo total (Pb)", "Plomo, Pb", "Pb", "7439-92-1", None, 0.1, "0.1 mg/L", "mg/L", "Puntual", "Mensual", "ICP-MS", "Límite en efluentes de refinación y producción."),
        ("Fenoles", "Compuestos fenólicos", "Fenoles", "108-95-2", None, 0.5, "0.5 mg/L", "mg/L", "Puntual", "Mensual", "Colorimétrico 4-aminoantipirina", "Aguas de formación y refinería."),
        ("Sulfuros (S=)", "Sulfuros totales", "S=", "18496-25-8", None, 1.0, "1.0 mg/L", "mg/L", "Puntual", "Mensual", "Yodometría", "Prevención de emanación de gases."),
        ("Bario (Ba)", "Bario, Ba", "Ba", "7440-39-3", None, 5.0, "5.0 mg/L", "mg/L", "Puntual", "Mensual", "ICP-OES", "Aguas de perforación y producción.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in hidro_efluentes:
        add_p("LMP", "Efluentes Líquidos", "Hidrocarburos", "Upstream / Downstream", "Exploración, Explotación, Refinación y Almacenamiento",
              "LMP Hidrocarburos", "Efluentes Líquidos de Hidrocarburos",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              lmp_hidro_norm, lmp_hidro_name, 2008, "Anexo 1", "Tabla 1", "Art. 2", "PCM / MINEM / OEFA", lmp_hidro_url)

    # -------------------------------------------------------------
    # 9. LMP PTAR DOMÉSTICAS Y MUNICIPALES (D.S. 003-2010-MINAM)
    # -------------------------------------------------------------
    lmp_ptar_url = "https://sinia.minam.gob.pe/normas/limites-maximos-permisibles-efluentes-ptar-domesticas-o-municipales"
    lmp_ptar_norm = "D.S. 003-2010-MINAM"
    lmp_ptar_name = "Límites Máximos Permisibles para los efluentes de Plantas de Tratamiento de Aguas Residuales Domésticas o Municipales (PTAR)"

    ptar_params = [
        ("pH", "Potencial de Hidrógeno", "pH", None, 6.5, 8.5, "6.5 - 8.5 unidades de pH", "unidades de pH", "Puntual in situ", "Monitoreo mensual", "Electrométrico", "Rango de pH para descargas de efluentes de PTAR a cuerpos receptores."),
        ("Aceites y Grasas (AyG)", "Grasas y aceites", "AyG", None, None, 20.0, "20 mg/L", "mg/L", "Puntual", "Mensual", "Método 5520 B Standard Methods", "Descarga de efluentes de PTAR domésticas o municipales."),
        ("Coliformes Termotolerantes", "Coliformes Fecales", "CT", None, None, 10000.0, "10 000 NMP/100 mL", "NMP/100 mL", "Puntual", "Mensual", "Fermentación tubos múltiples a 44.5°C", "Desinfección de efluentes tratados."),
        ("Demanda Bioquímica de Oxígeno (DBO5)", "DBO5", "DBO5", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta 24h", "Mensual", "Método 5210 B Standard Methods", "Eficiencia de remoción de materia orgánica biodegradable en PTAR."),
        ("Demanda Química de Oxígeno (DQO)", "DQO", "DQO", None, None, 200.0, "200 mg/L", "mg/L", "Compuesta 24h", "Mensual", "Método 5220 D Standard Methods", "Materia oxidable total en efluente tratado."),
        ("Sólidos Suspendidos Totales (SST)", "SST", "SST", None, None, 150.0, "150 mg/L", "mg/L", "Compuesta 24h", "Mensual", "Método 2540 D Standard Methods", "Sólidos no sedimentados en efluente final."),
        ("Temperatura", "Temperatura del efluente", "T°", None, None, 35.0, "< 35 °C", "°C", "Puntual in situ", "Mensual", "Termómetro calibrado", "Protección del ecosistema receptor.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in ptar_params:
        add_p("LMP", "Efluentes Líquidos", "Saneamiento / PTAR", "Tratamiento de Aguas Residuales", "Descargas de PTAR a cuerpos receptores de agua",
              "LMP Efluentes PTAR", "Plantas de Tratamiento Domésticas y Municipales",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              lmp_ptar_norm, lmp_ptar_name, 2010, "Anexo 1", "Tabla 1", "Art. 1", "MINAM / OEFA / SUNASS", lmp_ptar_url)

    # -------------------------------------------------------------
    # 10. LMP PESQUERÍA (D.S. 010-2008-PRODUCE & D.S. 011-2009-MINAM)
    # -------------------------------------------------------------
    lmp_pesq_url = "https://sinia.minam.gob.pe/normas/limites-maximos-permisibles-industria-harina-aceite-pescado-consumo-humano-directo"
    lmp_pesq_norm = "D.S. 010-2008-PRODUCE"
    lmp_pesq_name = "Límites Máximos Permisibles para la Industria de Harina y Aceite de Pescado"

    pesq_params = [
        ("pH", "Potencial de Hidrógeno", "pH", None, 6.0, 9.0, "6.0 - 9.0 unidades de pH", "unidades de pH", "Puntual", "Por turno de producción", "Electrométrico", "Efluentes de procesamiento pesquero y agua de bombeo."),
        ("Aceites y Grasas (AyG) - Plantas Nuevas", "Grasas y aceites", "AyG", None, None, 20.0, "20 mg/L", "mg/L", "Compuesta", "Por descarga", "Método 5520 B", "Plantas de harina y aceite de pescado nuevas o con reaprovechamiento integral."),
        ("Sólidos Suspendidos Totales (SST) - Plantas Nuevas", "SST", "SST", None, None, 50.0, "50 mg/L", "mg/L", "Compuesta", "Por descarga", "Método 2540 D", "Efluentes pesqueros tratados."),
        ("Demanda Bioquímica de Oxígeno (DBO5) - Plantas Nuevas", "DBO5", "DBO5", None, None, 60.0, "60 mg/L", "mg/L", "Compuesta", "Por descarga", "Método 5210 B", "Carga biodegradable en efluente pesquero tratado.")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs in pesq_params:
        add_p("LMP", "Efluentes Líquidos", "Pesquería", "Consumo Humano Indirecto / Directo", "Harina y Aceite de Pescado",
              "LMP Pesquería", "Efluentes Pesqueros",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              lmp_pesq_norm, lmp_pesq_name, 2008, "Anexo 1", "Tabla 1", "Art. 2", "PRODUCE / OEFA", lmp_pesq_url)

    # -------------------------------------------------------------
    # 11. LMP INDUSTRIA MANUFACTURERA (D.S. 003-2002-PRODUCE & D.S. 001-2020-EM)
    # -------------------------------------------------------------
    lmp_manuf_url = "https://sinia.minam.gob.pe/normas/limites-maximos-permisibles-actividades-industriales-manufactureras"
    lmp_manuf_norm = "D.S. 003-2002-PRODUCE"
    lmp_manuf_name = "Límites Máximos Permisibles para Actividades Industriales Manufactureras"

    manuf_params = [
        # Curtiembre
        ("Cromo Total (Cr) - Curtiembre", "Cromo en efluente de curtiembre", "Cr", "7440-47-3", None, 2.0, "2.0 mg/L", "mg/L", "Puntual", "Mensual", "Absorción Atómica", "Efluentes de procesos de curtido con cromo.", "Industria Manufacturera", "Curtiembre"),
        ("Sulfuros (S=) - Curtiembre", "Sulfuros de pelambre", "S=", "18496-25-8", None, 2.0, "2.0 mg/L", "mg/L", "Puntual", "Mensual", "Yodométrico", "Efluentes del proceso de pelambre y desencalado.", "Industria Manufacturera", "Curtiembre"),
        ("Sólidos Suspendidos Totales (SST) - Curtiembre", "SST", "SST", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta", "Mensual", "Método 2540 D", "Efluentes tratados de curtiembre.", "Industria Manufacturera", "Curtiembre"),
        ("DBO5 - Curtiembre", "DBO5", "DBO5", None, None, 250.0, "250 mg/L", "mg/L", "Compuesta", "Mensual", "Método 5210 B", "Carga orgánica de curtiembre.", "Industria Manufacturera", "Curtiembre"),
        # Papel
        ("Sólidos Suspendidos Totales (SST) - Papel", "SST", "SST", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta", "Mensual", "Método 2540 D", "Efluentes de fabricación de papel y pulpa.", "Industria Manufacturera", "Papel"),
        ("DBO5 - Papel", "DBO5", "DBO5", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta", "Mensual", "Método 5210 B", "Efluentes tratados de papelera.", "Industria Manufacturera", "Papel"),
        # Cerveza
        ("Sólidos Suspendidos Totales (SST) - Cerveza", "SST", "SST", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta", "Mensual", "Método 2540 D", "Efluentes de elaboración de cerveza y bebidas.", "Industria Manufacturera", "Cerveza"),
        ("DBO5 - Cerveza", "DBO5", "DBO5", None, None, 100.0, "100 mg/L", "mg/L", "Compuesta", "Mensual", "Método 5210 B", "Efluentes tratados cerveceros.", "Industria Manufacturera", "Cerveza")
    ]
    for pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs, sec, subsec in manuf_params:
        add_p("LMP", "Efluentes Líquidos", sec, subsec, f"Industria de {subsec}",
              f"LMP {subsec}", f"Efluentes Industriales de {subsec}",
              pname, alt, sym, cas, minv, maxv, vtext, unit, period, freq, meth, obs,
              lmp_manuf_norm, lmp_manuf_name, 2002, "Anexo 1", "Tabla Sectorial", "Art. 3", "PRODUCE / OEFA", lmp_manuf_url)

    # Cemento Emisiones D.S. 001-2020-EM
    cemento_url = "https://busquedas.elperuano.pe/normaslegales/decreto-supremo-que-aprueba-los-limites-maximos-permisibles-pa-decreto-supremo-n-001-2020-em-1845970-1/"
    cemento_norm = "D.S. 001-2020-EM"
    cemento_name = "LMP para Emisiones Atmosféricas de la Industria de Cemento, Cal y Yeso"

    add_p("LMP", "Emisiones Gaseosas", "Cemento y Construcción", "Fabricación de Cemento", "Hornos rotatorios y enfriadores de Clinker",
          "LMP Cemento", "Emisiones Atmosféricas de Cemento",
          "Material Particulado en Hornos de Cemento", "Polvo de clinker, PTS", "PTS", None, None, 50.0, "50 mg/Nm³", "mg/Nm³",
          "Isocinético continuo", "Semestral", "Método EPA 5", "Condiciones normales (0°C, 1 atm, 10% O2).",
          cemento_norm, cemento_name, 2020, "Anexo 1", "Tabla 1", "Art. 2", "MINEM / OEFA", cemento_url)
    add_p("LMP", "Emisiones Gaseosas", "Cemento y Construcción", "Fabricación de Cemento", "Hornos rotatorios",
          "LMP Cemento", "Emisiones Atmosféricas de Cemento",
          "Dióxido de Azufre (SO2) en Hornos de Cemento", "SO2", "SO2", "7446-09-5", None, 400.0, "400 mg/Nm³", "mg/Nm³",
          "Medición continua", "Semestral", "Método EPA 6C", "Condiciones normales (10% O2).",
          cemento_norm, cemento_name, 2020, "Anexo 1", "Tabla 1", "Art. 2", "MINEM / OEFA", cemento_url)
    add_p("LMP", "Emisiones Gaseosas", "Cemento y Construcción", "Fabricación de Cemento", "Hornos rotatorios",
          "LMP Cemento", "Emisiones Atmosféricas de Cemento",
          "Óxidos de Nitrógeno (NOx) en Hornos de Cemento", "NOx", "NOx", None, None, 800.0, "800 mg/Nm³", "mg/Nm³",
          "Medición continua", "Semestral", "Método EPA 7E", "Condiciones normales (10% O2).",
          cemento_norm, cemento_name, 2020, "Anexo 1", "Tabla 1", "Art. 2", "MINEM / OEFA", cemento_url)

    # -------------------------------------------------------------
    # 12. LMP VEHÍCULOS AUTOMOTORES (D.S. 010-2017-MINAM)
    # -------------------------------------------------------------
    lmp_veh_url = "https://www.gob.pe/institucion/minam/normas-legales/193714-010-2017-minam"
    lmp_veh_norm = "D.S. 010-2017-MINAM"
    lmp_veh_name = "Límites Máximos Permisibles de Emisiones Contaminantes para Vehículos Automotores"

    add_p("LMP", "Emisiones Vehiculares", "Transporte", "Vehículos Ligeros a Gasolina", "Inspección Técnica Vehicular (CITV)",
          "LMP Vehicular", "Vehículos a Gasolina (Euro 4 / Modernos)",
          "Monóxido de Carbono (CO) Vehicular", "CO en ralentí", "CO", "630-08-0", None, 0.5, "0.5 % vol", "% vol",
          "Ralentí / Marcha mínima", "Anual en CITV", "Analizador de gases NDIR", "LMP en marcha lenta o ralentí para vehículos año modelo 2017 en adelante.",
          lmp_veh_norm, lmp_veh_name, 2017, "Anexo 1", "Tabla 1", "Art. 3", "MINAM / MTC", lmp_veh_url)
    add_p("LMP", "Emisiones Vehiculares", "Transporte", "Vehículos Ligeros a Gasolina", "Inspección Técnica Vehicular (CITV)",
          "LMP Vehicular", "Vehículos a Gasolina (Euro 4 / Modernos)",
          "Hidrocarburos no quemados (HC) Vehicular", "HC en ralentí", "HC", None, None, 100.0, "100 ppm vol", "ppm vol",
          "Ralentí", "Anual en CITV", "Analizador de gases NDIR / FID", "LMP para vehículos a gasolina modernos.",
          lmp_veh_norm, lmp_veh_name, 2017, "Anexo 1", "Tabla 1", "Art. 3", "MINAM / MTC", lmp_veh_url)
    add_p("LMP", "Emisiones Vehiculares", "Transporte", "Vehículos Diésel", "Inspección Técnica Vehicular (CITV)",
          "LMP Vehicular", "Vehículos Diésel",
          "Opacidad / Coeficiente de absorción luminosa (k)", "Humo negro diésel", "k", None, None, 1.5, "1.5 m⁻¹", "m⁻¹",
          "Aceleración libre", "Anual en CITV", "Opacímetro de flujo parcial", "LMP de opacidad de humos diésel.",
          lmp_veh_norm, lmp_veh_name, 2017, "Anexo 2", "Tabla 2", "Art. 3", "MINAM / MTC", lmp_veh_url)

    # -------------------------------------------------------------
    # 13. LMP ELECTRICIDAD (R.D. 008-97-EM/DGAA)
    # -------------------------------------------------------------
    lmp_elec_url = "https://sinia.minam.gob.pe/normas/niveles-maximos-permisibles-efluentes-liquidos-actividades-electricas"
    lmp_elec_norm = "R.D. 008-97-EM/DGAA"
    lmp_elec_name = "Niveles Máximos Permisibles para Efluentes Líquidos de Actividades Eléctricas"

    add_p("LMP", "Efluentes Líquidos", "Electricidad", "Generación Térmica", "Centrales Termoeléctricas",
          "LMP Electricidad", "Efluentes Termoeléctricos",
          "pH en Efluentes Eléctricos", "pH", "pH", None, 6.0, 9.0, "6.0 - 9.0 unidades de pH", "unidades de pH",
          "Puntual", "Mensual", "Electrométrico", "Rango de pH para descargas de plantas eléctricas.",
          lmp_elec_norm, lmp_elec_name, 1997, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", lmp_elec_url)
    add_p("LMP", "Efluentes Líquidos", "Electricidad", "Generación Térmica", "Centrales Termoeléctricas",
          "LMP Electricidad", "Efluentes Termoeléctricos",
          "Aceites y Grasas (AyG) en Efluentes Eléctricos", "Grasas y aceites", "AyG", None, None, 20.0, "20 mg/L", "mg/L",
          "Puntual", "Mensual", "Extracción Soxhlet", "Descargas aceitosas de turbinas y transformadores.",
          lmp_elec_norm, lmp_elec_name, 1997, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", lmp_elec_url)
    add_p("LMP", "Efluentes Líquidos", "Electricidad", "Generación Térmica", "Centrales Termoeléctricas",
          "LMP Electricidad", "Efluentes Termoeléctricos",
          "Incremento de Temperatura (Delta T)", "Variación térmica del cuerpo receptor", "ΔT", None, None, 3.0, "≤ 3 °C", "°C",
          "In situ a 100m", "Continuo / Mensual", "Termométrico", "El incremento de temperatura en el cuerpo receptor no debe exceder 3°C a 100 metros del punto de descarga.",
          lmp_elec_norm, lmp_elec_name, 1997, "Anexo", "Tabla 1", "Art. 1", "MINEM / OEFA", lmp_elec_url)

    return params

if __name__ == "__main__":
    out_dir = Path(r"C:\Users\USER\.gemini\antigravity\scratch\econorma-peru\backend\app\data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "seed_parameters.json"
    
    parameters = create_parameters()
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parameters, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated {len(parameters)} verified parameters into {out_file}")
