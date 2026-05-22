import streamlit as st
import pandas as pd
import plotly.express as px
import ollama
import json
import os
import math

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS (Blanco, Verde, Tomate)
# ==========================================
st.set_page_config(page_title="Cooperativa Tulcán | devIAlabs", page_icon="🏦", layout="wide")

# CSS Avanzado para imitar React y la paleta de Tulcán
st.markdown("""
    <style>
    /* Fondo general blanco */
    .stApp { background-color: #FFFFFF; }
    
    /* Sidebar con fondo gris ultra claro */
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #EAECEF; }
    
    /* Tarjetas de Métricas Institucionales */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-top: 5px solid #008A4B; /* Verde Cooperativa */
        border-bottom: 1px solid #EAECEF;
        border-left: 1px solid #EAECEF;
        border-right: 1px solid #EAECEF;
    }
    
    /* El valor numérico de la métrica en color Tomate */
    div[data-testid="metric-value"] { color: #F26522; font-weight: 700; font-size: 2rem !important; }
    
    /* Estilo para los botones principales (Color Tomate) */
    .stButton>button {
        background-color: #F26522;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #D9531E;
        box-shadow: 0 4px 12px rgba(242, 101, 34, 0.3);
    }
    
    /* Estilo para botones secundarios (Verde) en el sidebar */
    .btn-nav>button {
        background-color: transparent !important;
        color: #333333 !important;
        border: 1px solid #EAECEF !important;
        justify-content: flex-start !important;
    }
    .btn-nav>button:hover {
        border-color: #008A4B !important;
        color: #008A4B !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ESTADOS DE SESIÓN (Enrutamiento tipo React)
# ==========================================
# Controlan en qué página estamos y qué cliente estamos viendo
if 'vista_actual' not in st.session_state:
    st.session_state['vista_actual'] = "Dashboard"
if 'cliente_seleccionado' not in st.session_state:
    st.session_state['cliente_seleccionado'] = None

def cambiar_vista(vista, cliente_id=None):
    st.session_state['vista_actual'] = vista
    if cliente_id is not None:
        st.session_state['cliente_seleccionado'] = cliente_id

# ==========================================
# 3. CARGA DE DATOS
# ==========================================
@st.cache_data
def cargar_datos():
    if not os.path.exists('reporte_semaforo_riesgo.csv'):
        return None
    return pd.read_csv('reporte_semaforo_riesgo.csv')

df = cargar_datos()

if df is None:
    st.error("⚠️ No se encontró la base de datos. Ejecuta el escaner_masivo.py primero.")
    st.stop()

# ==========================================
# 4. SIDEBAR PROFESIONAL
# ==========================================
st.sidebar.markdown(f"<h2 style='color:#008A4B; text-align:center;'>🏦 CoopTech</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; color:#888; margin-top:-15px;'>by devIAlabs</p>", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.markdown("**Menú Principal**")
# Botones de navegación lateral
if st.sidebar.button("📊 Dashboard General", use_container_width=True): cambiar_vista("Dashboard")
if st.sidebar.button("👥 Directorio de Clientes", use_container_width=True): cambiar_vista("Directorio")
if st.sidebar.button("⚠️ Sistema de Alertas", use_container_width=True): cambiar_vista("Alertas")

# Mostrar pestaña de detalles solo si hay un cliente seleccionado
if st.session_state['cliente_seleccionado']:
    st.sidebar.divider()
    st.sidebar.markdown("**Análisis Forense**")
    if st.sidebar.button(f"🔍 Cliente #{st.session_state['cliente_seleccionado']}", use_container_width=True): 
        cambiar_vista("Detalles")

st.sidebar.divider()
st.sidebar.caption("🟢 IA en línea | Gemma 4 Activo")


# ==========================================
# VISTA: DASHBOARD GENERAL
# ==========================================
if st.session_state['vista_actual'] == "Dashboard":
    st.markdown("<h2 style='color:#333;'>Dashboard de Riesgo Crediticio</h2>", unsafe_allow_html=True)
    
    # KPIs Generales (Las tarjetas verdes y tomate)
    total_clientes = len(df)
    riesgo_alto = len(df[df['semaforo'] == '🔴 RIESGO ALTO'])
    riesgo_medio = len(df[df['semaforo'] == '🟡 RIESGO MEDIO'])
    riesgo_bajo = len(df[df['semaforo'] == '🟢 RIESGO BAJO'])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Usuarios Totales", f"{total_clientes:,}")
    k2.metric("Alto Riesgo (Mora)", f"{riesgo_alto}", f"{(riesgo_alto/total_clientes)*100:.1f}%", delta_color="inverse")
    k3.metric("Riesgo Medio", f"{riesgo_medio}")
    k4.metric("Cartera Sana", f"{riesgo_bajo}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("#### Composición de la Cartera")
        conteo = df['semaforo'].value_counts().reset_index()
        conteo.columns = ['Nivel', 'Cantidad']
        colores_semaforo = {'🔴 RIESGO ALTO': '#ef4444', '🟡 RIESGO MEDIO': '#f59e0b', '🟢 RIESGO BAJO': '#008A4B'} # El verde sano es el corporativo
        fig = px.pie(conteo, values='Cantidad', names='Nivel', color='Nivel', color_discrete_map=colores_semaforo, hole=0.6)
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFF', width=2)))
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Resumen Ejecutivo Estratégico")
        st.info("💡 Haz clic en el botón inferior para generar un reporte global con Inteligencia Artificial.")
        if st.button("Generar Reporte Global con Gemma", type="primary"):
            with st.spinner("Analizando macro-tendencias de la cooperativa..."):
                prompt = f"Eres el gerente de riesgos. Tenemos {riesgo_alto} clientes en mora inminente, {riesgo_medio} en precaución y {riesgo_bajo} sanos. Redacta un reporte ejecutivo de 2 párrafos sobre la salud de la cooperativa."
                res = ollama.chat(model='gemma4', messages=[{'role': 'user', 'content': prompt}])
                st.write(res['message']['content'])


# ==========================================
# VISTA: DIRECTORIO DE CLIENTES (LISTA Y CLIC)
# ==========================================
elif st.session_state['vista_actual'] == "Directorio":
    st.markdown("<h2 style='color:#333;'>Directorio y Puntuación de Clientes</h2>", unsafe_allow_html=True)
    
    # Buscador y filtros
    col_busq, col_filtro = st.columns([3, 1])
    busqueda = col_busq.text_input("🔍 Buscar por ID de Cliente:", "")
    filtro_riesgo = col_filtro.selectbox("Filtrar por Riesgo:", ["Todos", "🔴 RIESGO ALTO", "🟡 RIESGO MEDIO", "🟢 RIESGO BAJO"])
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if busqueda: df_filtrado = df_filtrado[df_filtrado['id_cliente'].astype(str).str.contains(busqueda)]
    if filtro_riesgo != "Todos": df_filtrado = df_filtrado[df_filtrado['semaforo'] == filtro_riesgo]
    
    # Paginación Profesional
    filas_por_pagina = 15
    total_paginas = math.ceil(len(df_filtrado) / filas_por_pagina)
    
    if total_paginas > 0:
        pagina_actual = st.slider("Página de resultados", min_value=1, max_value=total_paginas, value=1)
        inicio = (pagina_actual - 1) * filas_por_pagina
        fin = inicio + filas_por_pagina
        df_mostrar = df_filtrado.iloc[inicio:fin]
        
        st.dataframe(
            df_mostrar[['id_cliente', 'semaforo', 'probabilidad_mora', 'saldo_disponible', 'ingresos']],
            column_config={
                "id_cliente": "ID Cliente", "semaforo": "Estado",
                "probabilidad_mora": st.column_config.ProgressColumn("Probabilidad de Mora", format="%.2f%%", min_value=0, max_value=100),
                "saldo_disponible": st.column_config.NumberColumn("Saldo Actual", format="$%d")
            },
            hide_index=True, use_container_width=True
        )
        
        # EL FLUJO DE "CLIC" -> Ir a Detalles
        st.markdown("### 🔍 Analizar a un cliente específico de esta lista:")
        col_select, col_btn = st.columns([3, 1])
        id_a_analizar = col_select.selectbox("Seleccione el ID para realizar el análisis forense:", df_mostrar['id_cliente'].tolist())
        
        if col_btn.button("Abrir Expediente", use_container_width=True, type="primary"):
            cambiar_vista("Detalles", id_a_analizar)
            st.rerun() # Esto recarga la página instantáneamente y abre la vista de detalles
            
    else:
        st.warning("No se encontraron resultados.")


# ==========================================
# VISTA: DETALLES DEL CLIENTE (ANÁLISIS LLM)
# ==========================================
elif st.session_state['vista_actual'] == "Detalles":
    cliente_id = st.session_state['cliente_seleccionado']
    st.markdown(f"<h2 style='color:#333;'>Expediente de Riesgo: Cliente #{cliente_id}</h2>", unsafe_allow_html=True)
    
    if st.button("⬅ Volver al Directorio"): 
        cambiar_vista("Directorio")
        st.rerun()
        
    datos_cliente = df[df['id_cliente'] == cliente_id].iloc[0]
    
    st.markdown("#### Perfil Financiero")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Probabilidad de Mora", f"{datos_cliente['probabilidad_mora']:.1f}%", f"{datos_cliente['semaforo']}", delta_color="off")
    k2.metric("Saldo Disponible", f"${datos_cliente['saldo_disponible']}")
    k3.metric("Ingresos", f"${datos_cliente['ingresos']}")
    k4.metric("Egresos", f"${datos_cliente['egresos']}")
    
    st.divider()
    
    # Análisis automático al entrar a esta vista
    st.markdown(f"#### 🤖 Análisis Cognitivo del Riesgo (Gemma)")
    with st.spinner("Leyendo patrones financieros y redactando informe..."):
        prompt = f"Actúa como analista senior de riesgo. El cliente {cliente_id} tiene {datos_cliente['probabilidad_mora']:.1f}% de riesgo de mora. Ingresos: ${datos_cliente['ingresos']}, Egresos: ${datos_cliente['egresos']}, Saldo en cuenta: ${datos_cliente['saldo_disponible']}. Explica por qué es riesgoso basándote en la relación de su liquidez y da 3 pasos sobre cómo el banco debe tratarlo."
        respuesta = ollama.chat(model='gemma4', messages=[{'role': 'user', 'content': prompt}])
        st.success(respuesta['message']['content'])


# ==========================================
# VISTA: SISTEMA DE ALERTAS
# ==========================================
elif st.session_state['vista_actual'] == "Alertas":
    st.markdown("<h2 style='color:#ef4444;'>⚠️ Sistema de Alertas Críticas</h2>", unsafe_allow_html=True)
    st.markdown("Listado de clientes cuya probabilidad de mora es inminente (Top 15 casos más graves de la cooperativa). El Call Center debe contactarlos hoy.")
    
    top_criticos = df[df['semaforo'] == '🔴 RIESGO ALTO'].head(15)
    
    # Renderizamos las alertas como "tarjetas" visuales
    for index, row in top_criticos.iterrows():
        with st.expander(f"🔴 ALERTA: Cliente #{row['id_cliente']} | Riesgo: {row['probabilidad_mora']:.1f}%"):
            cols = st.columns(3)
            cols[0].write(f"**Saldo Actual:** ${row['saldo_disponible']}")
            cols[1].write(f"**Ingresos:** ${row['ingresos']}")
            cols[2].write(f"**Egresos:** ${row['egresos']}")
            
            if st.button(f"Abrir Expediente Completo", key=f"btn_{row['id_cliente']}", type="secondary"):
                cambiar_vista("Detalles", row['id_cliente'])
                st.rerun()