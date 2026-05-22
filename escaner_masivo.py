import joblib
import pandas as pd
import numpy as np
import json
import ollama

print("--- 🔍 INICIANDO ESCÁNER DE CARTERA (SEMÁFORO) ---")

# ==========================================
# 1. CARGAR DATOS Y EL MOTOR YA ENTRENADO
# ==========================================
# Cargamos el motor que fabricamos en main.py
motor = joblib.load('modelo_riesgo.pkl')
molde_columnas = joblib.load('columnas_entrenamiento.pkl')

# Cargamos los datos limpios (así nos saltamos todo el cruce de archivos)
df_master = pd.read_csv('df_master_limpio.csv', low_memory=False)

# Filtramos: Solo queremos analizar a los clientes que HOY están al día (es_moroso == 0)
clientes_actuales = df_master[df_master['es_moroso'] == 0].copy()


# ==========================================
# 2. PREPARAR LOS DATOS PARA EL MOTOR
# ==========================================
# Aplicamos One-Hot Encoding
X_actuales = pd.get_dummies(clientes_actuales, drop_first=True)

# Alineamos las columnas para que encajen perfecto en el motor
for col in molde_columnas:
    if col not in X_actuales.columns:
        X_actuales[col] = 0
X_actuales = X_actuales[molde_columnas]


# ==========================================
# 3. PREDICCIÓN Y SEMÁFORO
# ==========================================
print("Calculando probabilidades de riesgo...")
clientes_actuales['probabilidad_mora'] = motor.predict_proba(X_actuales)[:, 1] * 100

condiciones = [
    (clientes_actuales['probabilidad_mora'] >= 70),
    (clientes_actuales['probabilidad_mora'] >= 30) & (clientes_actuales['probabilidad_mora'] < 70),
    (clientes_actuales['probabilidad_mora'] < 30)
]
etiquetas_semaforo = ['🔴 RIESGO ALTO', '🟡 RIESGO MEDIO', '🟢 RIESGO BAJO']

clientes_actuales['semaforo'] = np.select(condiciones, etiquetas_semaforo, default='Desconocido')

# Ordenamos a los más peligrosos arriba
reporte_completo = clientes_actuales.sort_values('probabilidad_mora', ascending=False)

# Exportamos la lista para que la interfaz web de la app la pueda mostrar
columnas_exportar = ['id_cliente', 'probabilidad_mora', 'semaforo', 'saldo_disponible', 'ingresos', 'egresos']
reporte_completo[columnas_exportar].to_csv('reporte_semaforo_riesgo.csv', index=False)
print("✅ Archivo 'reporte_semaforo_riesgo.csv' generado.")


# ==========================================
# 4. PASAR LOS CASOS CRÍTICOS A GEMMA
# ==========================================
print("\n--- 🤖 PREPARANDO DATOS PARA GEMMA 4 ---")
conteo_semaforo = reporte_completo['semaforo'].value_counts().to_dict()

# Sacamos solo a los 10 más peligrosos para no saturar a Gemma
top_10_criticos = reporte_completo[reporte_completo['semaforo'] == '🔴 RIESGO ALTO'].head(10)
datos_criticos_json = top_10_criticos[['id_cliente', 'probabilidad_mora', 'saldo_disponible', 'ingresos', 'egresos']].to_dict(orient='records')

prompt_gemma = f"""
Eres el asesor estratégico de cobranzas de nuestra cooperativa en Tulcán.
Nuestro modelo de IA escaneó la cartera y generó este semáforo de riesgo:
- 🔴 RIESGO ALTO (>70% prob): {conteo_semaforo.get('🔴 RIESGO ALTO', 0)} clientes
- 🟡 RIESGO MEDIO (30-70% prob): {conteo_semaforo.get('🟡 RIESGO MEDIO', 0)} clientes
- 🟢 RIESGO BAJO (<30% prob): {conteo_semaforo.get('🟢 RIESGO BAJO', 0)} clientes

Detalle de los 10 clientes con mayor riesgo inminente:
{json.dumps(datos_criticos_json, indent=2)}

Tu tarea:
Diseña un plan de acción para el Call Center enfocado en estos 10 clientes de la zona ROJA, considerando sus niveles de liquidez. No generes código, redacta como un experto financiero.
"""

print("Consultando a Gemma localmente... (Ollama)")
respuesta = ollama.chat(model='gemma4', messages=[
  {'role': 'user', 'content': prompt_gemma}
])

print("\n--- 📝 INFORME DE ESTRATEGIA (GEMMA) ---")
print(respuesta['message']['content'])