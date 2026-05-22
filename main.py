import pandas as pd
import glob
from datetime import datetime

def leer_datos_robusto(patron_archivo):
    archivos = glob.glob(patron_archivo)
    lista_dfs = []
    for f in archivos:
        try:
            df = pd.read_csv(f, on_bad_lines="skip", low_memory=False, encoding="latin-1")
            lista_dfs.append(df)
        except Exception:
            df = pd.read_excel(f)
            lista_dfs.append(df)
    return pd.concat(lista_dfs, ignore_index=True) if lista_dfs else pd.DataFrame()

# ==========================================
# 1. TABLA DE CRÉDITOS (El Motor)
# ==========================================
print("Procesando Créditos...")
df_credito = leer_datos_robusto("datos/DataSabanaCred*.*")

# Renombrar clave y columnas clave requeridas
df_credito = df_credito.rename(columns={
    'nro_cliente': 'id_cliente',
    'monto_credito': 'credito',
    'saldo_capital': 'saldo_disponible',
    'ingresos_socio': 'ingresos',
    'egresos_socio': 'egresos'
})
df_credito['id_cliente'] = df_credito['id_cliente'].astype(str)

# 1.1 Calcular la Edad (Ingeniería de variables)
# Asumimos que la columna origen se llama 'fecha_nacimiento'
if 'fecha_nacimiento' in df_credito.columns:
    df_credito['fecha_nacimiento'] = pd.to_datetime(df_credito['fecha_nacimiento'], errors='coerce')
    df_credito['edad'] = (pd.Timestamp.now() - df_credito['fecha_nacimiento']).dt.days // 365
    df_credito['edad'] = df_credito['edad'].fillna(df_credito['edad'].median()) # Rellenamos sin edad con la media

# 1.2 CREAR LA VARIABLE OBJETIVO (es_moroso)
# REGLA: Si tiene días de mora (> 0), es moroso (1), si no, es buen pagador (0).
if 'dias_mora' in df_credito.columns:
    df_credito['es_moroso'] = (df_credito['dias_mora'] > 0).astype(int)

# 1.3 Filtrar estrictamente las columnas que pediste
columnas_credito_keeper = [
    'id_cliente', 'es_moroso', 'dias_mora', 'nro_cuotas_atra', 'ingresos', 'egresos', 
    'val_morad', 'val_int_mora', 'calificacion', 'tipo_cartera', 'plazo', 
    'tasas_int_con', 'garantias', 'sexo', 'estado_civil', 'nivel_educa', 'tipo_vivien', 'edad',
    'credito', 'saldo_disponible'
]
# Solo nos quedamos con las que realmente existen en el archivo
columnas_presentes_cred = [col for col in columnas_credito_keeper if col in df_credito.columns]
df_credito = df_credito[columnas_presentes_cred]
df_credito = df_credito.drop_duplicates(subset=['id_cliente'], keep='last')


# ==========================================
# 2. TABLA DE AHORROS (Liquidez)
# ==========================================
print("Procesando Ahorros...")
df_ahorro = leer_datos_robusto("datos/DatsSabanaAhorro*.csv")

# Renombrar clave
df_ahorro = df_ahorro.rename(columns={'v_ah_cliente': 'id_cliente'})
df_ahorro['id_cliente'] = df_ahorro['id_cliente'].astype(str)

# 2.1 Calcular Antigüedad en meses
if 'fecha_aper' in df_ahorro.columns:
    df_ahorro['fecha_aper'] = pd.to_datetime(df_ahorro['fecha_aper'], errors='coerce')
    df_ahorro['antiguedad_meses_ahorro'] = (pd.Timestamp.now() - df_ahorro['fecha_aper']).dt.days // 30
    df_ahorro['antiguedad_meses_ahorro'] = df_ahorro['antiguedad_meses_ahorro'].fillna(0)

# 2.2 Filtrar estrictamente las columnas que pediste
columnas_ahorro_keeper = [
    'id_cliente', 'antiguedad_meses_ahorro', 'tarjetas', 'int_acumula', 'saldo_int_decim'
]
columnas_presentes_ahorro = [col for col in columnas_ahorro_keeper if col in df_ahorro.columns]
df_ahorro = df_ahorro[columnas_presentes_ahorro]
df_ahorro = df_ahorro.drop_duplicates(subset=['id_cliente'], keep='last')


# ==========================================
# 3. TABLA DE TRANSACCIONES (Comportamiento)
# ==========================================
print("Procesando Transacciones...")
df_trns = leer_datos_robusto("datos/Trns*.csv")

# Renombrar clave
df_trns = df_trns.rename(columns={'cliente': 'id_cliente'})
df_trns['id_cliente'] = df_trns['id_cliente'].astype(str)
df_trns['valor_trn'] = pd.to_numeric(df_trns['valor_trn'], errors='coerce').fillna(0)

# 3.1 ¡EL TRUCO ESTRELLA! Separar Ingresos de Egresos según 'signo_nc_nd'
# Filtramos y agrupamos los depósitos (Créditos)
ingresos_tx = df_trns[df_trns['signo_nc_nd'] == 'C'].groupby('id_cliente')['valor_trn'].sum().reset_index(name='total_ingresos_tx')
# Filtramos y agrupamos los retiros (Débitos)
egresos_tx = df_trns[df_trns['signo_nc_nd'] == 'D'].groupby('id_cliente')['valor_trn'].sum().reset_index(name='total_egresos_tx')

# 3.2 Extraer el último saldo contable y disponible del mes
# Ordenamos por fecha para asegurarnos de tomar el saldo final de mes
# 3.2 Extraer el último saldo contable y disponible del mes
if 'fecha_trn' in df_trns.columns:
    # 1. Forzamos a texto para que no pelee con los NaNs
    # 2. Convertimos a fecha real (los errores o vacíos se vuelven NaT - Not a Time)
    df_trns['fecha_trn'] = pd.to_datetime(df_trns['fecha_trn'].astype(str), errors='coerce')
    # 3. Ahora sí, ordenamos cronológicamente
    df_trns = df_trns.sort_values('fecha_trn')
    
saldos_finales = df_trns.groupby('id_cliente')[['saldo_contable', 'saldo_disponible']].last().reset_index()
# Para no confundir con el saldo_disponible de la tabla de ahorro, renombramos
saldos_finales = saldos_finales.rename(columns={'saldo_disponible': 'saldo_disponible_tx'})

# 3.3 Calcular cantidad de transacciones totales y causales únicas
frecuencia_tx = df_trns.groupby('id_cliente').agg(
    cantidad_transacciones=('valor_trn', 'count'),
    tipos_movimientos_distintos=('causal_trn', 'nunique') # ¿Hace transferencias, cajero, pagos?
).reset_index()

# Unimos todo el comportamiento transaccional en un solo DataFrame
df_trns_resumen = ingresos_tx.merge(egresos_tx, on='id_cliente', how='outer')
df_trns_resumen = df_trns_resumen.merge(saldos_finales, on='id_cliente', how='outer')
df_trns_resumen = df_trns_resumen.merge(frecuencia_tx, on='id_cliente', how='outer')
df_trns_resumen = df_trns_resumen.fillna(0)


# ==========================================
# 4. EL GRAN CRUCE (Creación de la Tabla Maestra)
# ==========================================
print("Cruzando datos...")

df_master = df_credito.copy()
df_master = df_master.merge(df_ahorro, on='id_cliente', how='left')
df_master = df_master.merge(df_trns_resumen, on='id_cliente', how='left')

# Asegurar que no queden valores nulos en columnas numéricas clave tras el cruce
columnas_rellenar_cero = [
    'saldo_disponible', 'ingresos', 'egresos', 'credito', 'val_morad',
    'total_ingresos_tx', 'total_egresos_tx', 'saldo_contable', 'saldo_disponible_tx',
    'cantidad_transacciones', 'tipos_movimientos_distintos'
]
for col in columnas_rellenar_cero:
    if col in df_master.columns:
        df_master[col] = pd.to_numeric(df_master[col], errors='coerce').fillna(0)

# Convertir columnas de texto a categorías para LightGBM
columnas_texto = df_master.select_dtypes(include=['object']).columns
for col in columnas_texto:
    if col != 'id_cliente':
        df_master[col] = df_master[col].astype('category')

print(f"✅ ¡Dataframe Maestro listo! Filas: {df_master.shape[0]}, Columnas: {df_master.shape[1]}")
# --- AGREGAR ESTA LÍNEA ---
df_master.to_csv('df_master_limpio.csv', index=False)

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
import numpy as np

print("\n--- INICIANDO PREPROCESAMIENTO AVANZADO ---")

# ==========================================
# 1. IDENTIFICACIÓN DE PATRONES (Clustering / K-Means)
# ==========================================
print("1. Buscando patrones ocultos (K-Means)...")

# Variables numéricas que definen el comportamiento del cliente
columnas_comportamiento = [
    'saldo_disponible', 'antiguedad_meses_ahorro', 'ingresos', 'egresos',
    'total_ingresos_tx', 'total_egresos_tx', 'cantidad_transacciones', 'tipos_movimientos_distintos'
]
cols_cluster = [col for col in columnas_comportamiento if col in df_master.columns]

# K-Means exige datos sin nulos y estandarizados
df_clustering = df_master[cols_cluster].fillna(0)
scaler = StandardScaler()
datos_escalados = scaler.fit_transform(df_clustering)

# Identificamos 4 grupos (clústeres) de comportamiento
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_master['grupo_patron'] = kmeans.fit_predict(datos_escalados)

print(f"Clientes agrupados por patrón de comportamiento:\n{df_master['grupo_patron'].value_counts()}")


# ==========================================
# 2. LIMPIEZA DE FUGA DE DATOS (Data Leakage)
# ==========================================
print("\n2. Eliminando variables trampa...")

y = df_master['es_moroso']

# Columnas que el modelo NO debe ver porque revelan el futuro
columnas_prohibidas = [
    'id_cliente', 'es_moroso', 'dias_mora', 'nro_cuotas_atra', 
    'val_morad', 'val_int_mora', 'calificacion'
]
X = df_master.drop(columns=[col for col in columnas_prohibidas if col in df_master.columns])


# ==========================================
# 3. ONE-HOT ENCODING (Codificación de Variables)
# ==========================================
print("\n3. Aplicando One-Hot Encoding...")

# Identificamos qué columnas son texto (categóricas)
# Incluimos 'grupo_patron' porque aunque sea un número (0,1,2,3), representa una categoría
columnas_texto = X.select_dtypes(include=['object', 'category']).columns.tolist()
if 'grupo_patron' not in columnas_texto:
    columnas_texto.append('grupo_patron')

# Aplicamos One-Hot Encoding usando Pandas
# drop_first=True evita la multicolinealidad (una buena práctica estadística)
X = pd.get_dummies(X, columns=columnas_texto, drop_first=True)

# get_dummies genera columnas booleanas (True/False), las pasamos a 1 y 0
X = X.astype(float)

print(f"Dimensiones después de One-Hot Encoding: {X.shape[1]} variables predictoras.")


# ==========================================
# 4. GRUPOS SEPARADOS PARA ENTRENAMIENTO Y PRUEBA
# ==========================================
print("\n4. Creando grupos separados (Train / Test Split)...")

# Dividimos el dataset: 80% para entrenar al modelo, 20% para aislarlo y probarlo.
# stratify=y GARANTIZA que si hay un 10% de morosos en total, 
# habrá exactamente un 10% de morosos en el grupo de entrenamiento y 10% en el de prueba.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y 
)

print("✅ Preprocesamiento completado y listo para Machine Learning.")
print(f"🔸 Grupo de Entrenamiento: {X_train.shape[0]} clientes.")
print(f"🔸 Grupo de Evaluación (Aislado): {X_test.shape[0]} clientes.")

import lightgbm as lgb
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

print("\n--- 🧠 ENTRENANDO EL CEREBRO DE PREDICCIÓN ---")

# ==========================================
# 1. CONFIGURACIÓN Y ENTRENAMIENTO
# ==========================================
# n_estimators: Cantidad de árboles de decisión que construirán el modelo
# learning_rate: Qué tan rápido aprende (más bajo = más preciso pero tarda más)
# n_jobs=-1: Le dice a tu laptop que use todos los núcleos del procesador para ir a máxima velocidad
modelo_lgb = lgb.LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    class_weight='balanced', 
    random_state=42,
    n_jobs=-1 
)

print("Entrenando LightGBM con los datos de entrenamiento...")
modelo_lgb.fit(X_train, y_train)


# ==========================================
# 2. EL EXAMEN FINAL (PREDICCIONES)
# ==========================================
print("\nEvaluando el modelo con los datos aislados (Test)...")
# El modelo escupe un 1 (Moroso) o 0 (Buen Pagador)
y_pred = modelo_lgb.predict(X_test)
# También le pedimos la "probabilidad" exacta (ej. 85% de riesgo) para el AUC-ROC
y_prob = modelo_lgb.predict_proba(X_test)[:, 1] 


# ==========================================
# 3. MÉTRICAS DE NEGOCIO (Lo que le importa al jurado)
# ==========================================
print("\n--- 📊 RESULTADOS DEL MODELO ---")

# AUC-ROC: Mide la capacidad del modelo para separar a los buenos de los malos
auc = roc_auc_score(y_test, y_prob)
print(f"🏆 Puntuación AUC-ROC: {auc:.4f} (1.0 es perfecto, > 0.75 es muy bueno para riesgo)")

print("\nReporte de Clasificación:")
print(classification_report(y_test, y_pred, target_names=['Buen Pagador (0)', 'Moroso (1)']))


# ==========================================
# 4. VISUALIZACIÓN PARA EL PITCH (Gráficos)
# ==========================================
fig, ax = plt.subplots(1, 2, figsize=(15, 6))

# Gráfico 1: Matriz de Confusión
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax[0], cbar=False)
ax[0].set_title('Matriz de Confusión (Aciertos vs Errores)')
ax[0].set_ylabel('Realidad')
ax[0].set_xlabel('Predicción de devIAlabs')

# Gráfico 2: Importancia de Variables
lgb.plot_importance(modelo_lgb, max_num_features=12, ax=ax[1], title='Top 12 Variables que definen la Morosidad', importance_type='gain')
plt.tight_layout()
plt.show()

import joblib

print("\n--- 📦 EXPORTANDO EL MOTOR PARA PRODUCCIÓN ---")
joblib.dump(modelo_lgb, 'modelo_riesgo.pkl')
joblib.dump(X_train.columns.tolist(), 'columnas_entrenamiento.pkl')
print("✅ Motor guardado. ¡El trabajo en main.py ha terminado!")