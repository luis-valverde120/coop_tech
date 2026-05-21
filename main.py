import pandas as pd
import glob

def read_csv_flexible(path: str) -> pd.DataFrame:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, on_bad_lines="skip", low_memory=False, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, on_bad_lines="skip", low_memory=False, encoding="latin-1", errors="replace")

# ==========================================
# 1. CONSOLIDAR AHORROS
# ==========================================
print("Consolidando Ahorros...")
archivos_ahorro = glob.glob("datos/DatsSabanaAhorro*.csv")
df_ahorro = pd.concat((read_csv_flexible(f) for f in archivos_ahorro), ignore_index=True)

# RENOMBRAR EL CAMPO CLAVE
df_ahorro = df_ahorro.rename(columns={'v_ah_cliente': 'id_cliente'})

# Nos quedamos con el último registro de cada cliente (asumiendo que están ordenados cronológicamente)
df_ahorro = df_ahorro.drop_duplicates(subset=['id_cliente'], keep='last')


# ==========================================
# 2. CONSOLIDAR CRÉDITOS
# ==========================================
print("Consolidando Créditos...")
archivos_credito = glob.glob('datos/DataSabanaCred*.xls')
df_credito = pd.concat((pd.read_excel(f) for f in archivos_credito), ignore_index=True)

# RENOMBRAR EL CAMPO CLAVE
df_credito = df_credito.rename(columns={'nro_cliente': 'id_cliente'})

# En créditos, un cliente puede tener varios préstamos (varias filas).
# Para simplificar en la hackathon, si hay duplicados, sumamos el saldo de sus créditos o nos quedamos con el peor estado.
# Por ahora, nos quedaremos con el registro más reciente para tener una fila por cliente:
df_credito = df_credito.drop_duplicates(subset=['id_cliente'], keep='last')


# ==========================================
# 3. CONSOLIDAR Y RESUMIR TRANSACCIONES
# ==========================================
print("Procesando Transacciones...")
archivos_trns = glob.glob('datos/Trns*.csv')
df_trns = pd.concat((read_csv_flexible(f) for f in archivos_trns), ignore_index=True)

# RENOMBRAR EL CAMPO CLAVE
df_trns = df_trns.rename(columns={'cliente': 'id_cliente'})

# Resumimos las transacciones por cliente
# Nota: Viendo tu imagen, la columna del monto se llama 'valor_trn'
df_trns_resumen = df_trns.groupby('id_cliente').agg(
    total_transaccionado=('valor_trn', 'sum'),
    cantidad_transacciones=('valor_trn', 'count'),
    promedio_transaccion=('valor_trn', 'mean')
).reset_index()


# ==========================================
# 4. EL GRAN CRUCE (Crear la Tabla Maestra)
# ==========================================
print("Creando DataFrame Maestro...")

# Empezamos con la base de Créditos, porque ahí es donde nos interesa saber quién paga y quién no
df_master = df_credito.merge(df_ahorro, on='id_cliente', how='left')

# Luego le pegamos el resumen de sus transacciones
df_master = df_master.merge(df_trns_resumen, on='id_cliente', how='left')

print(f"¡Listo! DataFrame Maestro creado con {df_master.shape[0]} filas.")