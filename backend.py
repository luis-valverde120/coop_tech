from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import ollama
import math
import random

app = FastAPI(title="CoopTech Backend")

# Habilitar CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_data():
    """Lee el reporte final generado por el escaner masivo (incluye todas las columnas)."""
    try:
        df = pd.read_csv('reporte_semaforo_riesgo.csv')
        return df, pd.DataFrame() # Devolvemos un DF vacío como segundo valor para no romper compatibilidad
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

@app.get("/api/dashboard/kpis")
def get_kpis():
    df, _ = get_data()
    if df.empty:
        raise HTTPException(status_code=500, detail="No se pudieron cargar los datos")
        
    total_activos = len(df)
    riesgo_alto = len(df[df['semaforo'] == '🔴 RIESGO ALTO'])
    riesgo_medio = len(df[df['semaforo'] == '🟡 RIESGO MEDIO'])
    riesgo_bajo = len(df[df['semaforo'] == '🟢 RIESGO BAJO'])
    
    # Como el dashboard ahora es exclusivamente predictivo (sin incluir los ya morosos)
    total_en_mora = 0
    
    portafolio_total = df['saldo_disponible'].sum() if 'saldo_disponible' in df else 4820000
    if pd.isna(portafolio_total): portafolio_total = 4820000

    return {
        "creditos_activos": total_activos,
        "en_mora": total_en_mora,
        "porcentaje_mora": 0,
        "en_riesgo": riesgo_alto + riesgo_medio,
        "recuperados": 12, # Dato simulado temporalmente
        "portafolio": f"${portafolio_total / 1000000:.2f}M",
        "tendencia_mora": [
            {"mes": "Dic", "valor": 5.2},
            {"mes": "Ene", "valor": 5.8},
            {"mes": "Feb", "valor": 6.1},
            {"mes": "Mar", "valor": 6.8},
            {"mes": "Abr", "valor": 7.4},
            {"mes": "May", "valor": 8.03}
        ],
        "distribucion_riesgo": {
            "Bajo": riesgo_bajo,
            "Medio": riesgo_medio,
            "Alto": riesgo_alto,
            "Critico": total_en_mora
        }
    }

@app.get("/api/socios")
def get_socios(riesgo: str = "Todos", search: str = "", page: int = 1, limit: int = 15):
    df, _ = get_data()
    
    # Filtros
    if search:
        df = df[df['id_cliente'].astype(str).str.contains(search)]
        
    if riesgo != "Todos":
        # Mapeamos los filtros visuales a los valores del ML
        mapeo = {
            "Critico": '🔴 RIESGO ALTO', # Simplificación
            "Alto": '🔴 RIESGO ALTO',
            "Medio": '🟡 RIESGO MEDIO',
            "Bajo": '🟢 RIESGO BAJO'
        }
        val_buscado = mapeo.get(riesgo)
        if val_buscado:
            df = df[df['semaforo'] == val_buscado]
            
    # Paginación
    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    df_pag = df.iloc[start:end]
    
    socios = []
    for _, row in df_pag.iterrows():
        # Generar letras aleatorias para simular las iniciales que se ven en el mockup
        iniciales = f"{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}"
        
        estado = "Bajo"
        if row['semaforo'] == '🔴 RIESGO ALTO': estado = "Crítico" if row['probabilidad_mora'] > 85 else "Alto"
        elif row['semaforo'] == '🟡 RIESGO MEDIO': estado = "Medio"
        
        val_credito = row['credito'] if pd.notna(row['credito']) else row.get('saldo_disponible', 0)
        if pd.isna(val_credito): val_credito = 0
            
        socios.append({
            "id_cliente": int(row['id_cliente']),
            "iniciales": iniciales,
            "credito": float(val_credito),
            "dias_atraso": int(row['dias_mora']) if pd.notna(row['dias_mora']) else 0,
            "riesgo": estado,
            "score": float(round(row['probabilidad_mora'], 0))
        })
        
    return {
        "data": socios,
        "total": total,
        "page": page,
        "total_pages": math.ceil(total / limit)
    }

@app.get("/api/socios/{id_cliente}")
def get_socio_detalle(id_cliente: int):
    df, df_master = get_data()
    
    socio_data = df[df['id_cliente'] == id_cliente]
    if socio_data.empty:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
        
    row = socio_data.iloc[0]
    
    estado = "Bajo"
    if row['semaforo'] == '🔴 RIESGO ALTO': estado = "Crítico" if row['probabilidad_mora'] > 85 else "Alto"
    elif row['semaforo'] == '🟡 RIESGO MEDIO': estado = "Medio"
    
    # Simulamos el historial usando el ID como semilla para que sea constante
    random.seed(id_cliente)
    historial = []
    meses = ['Nov', 'Dic', 'Ene', 'Feb', 'Mar', 'Abr']
    for mes in meses:
        historial.append({
            "mes": mes,
            "pago": random.choice([True, True, True, False]) # 75% chance de haber pagado
        })
    
    val_credito = row['credito'] if pd.notna(row['credito']) else row.get('saldo_disponible', 0)
    if pd.isna(val_credito): val_credito = 0
    
    val_saldo = row.get('saldo_disponible', 0)
    if pd.isna(val_saldo): val_saldo = 0
    
    return {
        "id_cliente": int(row['id_cliente']),
        "iniciales": f"{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}",
        "score": float(round(row['probabilidad_mora'], 0)),
        "estado": estado,
        "credito": float(val_credito),
        "saldo_pendiente": float(val_saldo) * 0.15, # Simulado
        "dias_atraso": int(row['dias_mora']) if pd.notna(row['dias_mora']) else (14 if estado == "Crítico" else 0),
        "ultimo_pago": "2026-04-30" if random.random() > 0.5 else "2026-05-10",
        "historial": historial,
        "ingresos": float(row.get('ingresos', 0)) if pd.notna(row.get('ingresos')) else 0.0,
        "egresos": float(row.get('egresos', 0)) if pd.notna(row.get('egresos')) else 0.0
    }

@app.get("/api/alertas")
def get_alertas():
    df, _ = get_data()
    
    # Top de clientes más críticos
    top_criticos = df[df['semaforo'] == '🔴 RIESGO ALTO'].head(15)
    
    alertas = []
    for _, row in top_criticos.iterrows():
        score = round(row['probabilidad_mora'], 0)
        
        tipo = "Crítico" if score > 85 else "Alto"
        motivo = "Segundo pago consecutivo vencido" if score > 85 else "Saldo promedio cayó en los últimos días"
        
        alertas.append({
            "id": int(row['id_cliente']),
            "id_cliente": int(row['id_cliente']),
            "tipo": tipo,
            "motivo": motivo,
            "fecha": "2026-05-21",
            "cuota": round(row['saldo_disponible'] * 0.05, 2)
        })
        
    return {
        "criticas": len([a for a in alertas if a['tipo'] == 'Crítico']),
        "altas": len([a for a in alertas if a['tipo'] == 'Alto']),
        "medias": 2, # Fijo para completar UI
        "alertas": alertas
    }

@app.post("/api/socios/{id_cliente}/analisis")
def analizar_socio(id_cliente: int):
    df, _ = get_data()
    socio = df[df['id_cliente'] == id_cliente]
    if socio.empty:
         raise HTTPException(status_code=404, detail="Socio no encontrado")
         
    datos = socio.iloc[0]
    try:
        prompt = f"""Actúa como el Gerente de Riesgos de la Cooperativa CoopTech. 
Analiza detalladamente a este cliente (ID: {id_cliente}).
Datos actuales: 
- Score de Riesgo (Probabilidad de mora): {datos['probabilidad_mora']:.1f}%
- Ingresos mensuales: ${datos['ingresos']}
- Egresos mensuales: ${datos['egresos']}
- Saldo en cuenta disponible: ${datos['saldo_disponible']}
- Crédito total otorgado: ${datos['credito']}

Tu tarea es redactar un informe ejecutivo rápido pero muy perspicaz estructurado en 3 partes:
1. Diagnóstico: ¿Cuál es su situación financiera actual basada en estos números?
2. Hipótesis de Riesgo: ¿Por qué el modelo de IA le asigna esta probabilidad de mora? (Genera hipótesis lógicas basadas en su flujo de caja, liquidez o sobreendeudamiento).
3. Recomendaciones: Proporciona 2 acciones claras y directas que el equipo de cobranzas o negocios debe tomar AHORA MISMO con este cliente.

Usa un tono profesional, claro y sin introducciones robóticas. Separa cada sección claramente."""
        respuesta = ollama.chat(model='gemma4', messages=[{'role': 'user', 'content': prompt}])
        return {"analisis": respuesta['message']['content']}
    except Exception as e:
        return {"analisis": f"No se pudo conectar con el modelo Gemma local. Error: {str(e)}"}

