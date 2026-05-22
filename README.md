# CoopTech - Tulcaniza | devIAlabs 🏦📊

Bienvenido al repositorio de **CoopTech**, una plataforma avanzada de análisis de riesgo crediticio diseñada para instituciones financieras y cooperativas (específicamente adaptada para Tulcán). El sistema utiliza Machine Learning e Inteligencia Artificial Generativa (LLM) para evaluar, predecir y mitigar los riesgos de morosidad en la cartera de clientes.

## 🚀 Características Principales

1. **Motor de Riesgo (Machine Learning):**
   - Procesamiento robusto de datos transaccionales, de crédito y ahorros.
   - Algoritmos de clustering (K-Means) para identificar patrones de comportamiento.
   - Modelo predictivo basado en **LightGBM** para calcular la probabilidad exacta de mora de cada cliente.

2. **Escáner Masivo de Cartera:**
   - Clasificación de toda la cartera activa mediante un sistema de "Semáforo de Riesgo":
     - 🔴 **RIESGO ALTO** (Probabilidad > 70%)
     - 🟡 **RIESGO MEDIO** (Probabilidad entre 30% y 70%)
     - 🟢 **RIESGO BAJO** (Probabilidad < 30%)
   - Generación de estrategias de cobranza automáticas usando Inteligencia Artificial (Gemma 4).

3. **Dashboard Analítico (Streamlit):**
   - Panel de control interactivo con KPIs en tiempo real de la salud de la cartera.
   - Directorio y buscador de clientes con paginación y filtros de riesgo.
   - Análisis Forense Individual con reportes cognitivos generados por IA.
   - Sistema de Alertas Críticas para el Call Center.

4. **API Backend (FastAPI):**
   - Endpoints RESTful para la integración con otras interfaces (ej. React).
   - Análisis de impacto macroeconómico: Cruce de noticias recientes (Web Scraping) con las actividades económicas de los clientes para predecir impactos indirectos.

## 📁 Estructura del Proyecto

- `main.py`: Script principal de entrenamiento. Extrae datos crudos de la carpeta `/datos`, realiza ingeniería de características (feature engineering), entrena el modelo predictivo LightGBM y exporta el modelo entrenado (`modelo_riesgo.pkl`).
- `escaner_masivo.py`: Utiliza el modelo pre-entrenado para evaluar a los clientes actuales (que no están en mora), genera el `reporte_semaforo_riesgo.csv` y consulta a la IA (Ollama/Gemma) para obtener un plan de acción para casos críticos.
- `app.py`: Interfaz visual en **Streamlit** (El Dashboard Principal). Provee toda la experiencia de usuario (UX) para visualizar los niveles de riesgo y los análisis generados.
- `backend.py`: Servidor **FastAPI** que expone la lógica de negocio y las predicciones a través de una API. Incluye endpoints para KPIs, directorio, alertas y análisis de impacto de noticias.
- `scraper_noticias.py`: Módulo auxiliar de Web Scraping para obtener titulares de noticias relevantes y medir su impacto en los clientes de la cooperativa.
- `pyproject.toml` / `uv.lock`: Archivos de configuración de dependencias del proyecto.

## 🛠 Tecnologías y Herramientas Utilizadas

- **Lenguaje:** Python 3.12+
- **Machine Learning:** Scikit-Learn, LightGBM
- **Procesamiento de Datos:** Pandas, Numpy
- **Visualización:** Streamlit, Plotly, Matplotlib, Seaborn
- **Backend / API:** FastAPI, Uvicorn
- **Inteligencia Artificial (LLM):** Ollama (Modelo local `gemma4`)
- **Web Scraping:** BeautifulSoup4, Requests

## ⚙️ Instalación y Uso

1. **Requisitos Previos:**
   - Asegúrate de tener Python instalado (versión 3.12 o superior).
   - Necesitas tener instalado **Ollama** en tu máquina con el modelo `gemma4` descargado (`ollama run gemma4` o similar dependiendo del tag exacto que uses).

2. **Instalación de Dependencias:**
   El proyecto utiliza un entorno moderno (gestión mediante `uv` y `pyproject.toml`). Puedes instalar las dependencias con:
   ```bash
   pip install -r requirements.txt
   # O utilizando la herramienta uv:
   uv pip install -e .
   ```
   *(También puedes usar herramientas estándar según lo definido en el `pyproject.toml`)*

3. **Flujo de Ejecución:**
   
   - **Paso 1: Entrenar el Modelo**
     Ejecuta el script principal para procesar los datos de la carpeta `datos/` y generar el modelo de IA.
     ```bash
     python main.py
     ```
   
   - **Paso 2: Escanear la Cartera Actual**
     Analiza a los clientes activos y genera el reporte de semáforo.
     ```bash
     python escaner_masivo.py
     ```
   
   - **Paso 3: Levantar la Interfaz (Dashboard)**
     Abre el panel de control interactivo en tu navegador.
     ```bash
     streamlit run app.py
     ```
   
   - **(Opcional) Levantar el Backend FastAPI:**
     Si necesitas consumir la API desde otro frontend o aplicación móvil.
     ```bash
     uvicorn backend:app --reload
     ```

## 🔐 Notas Importantes
- **Privacidad y Seguridad:** El sistema utiliza Ollama para correr modelos de IA de forma **local**. Esto asegura que los datos financieros sensibles de los clientes nunca salgan de la infraestructura de la institución hacia la nube de terceros (como OpenAI).
- **Archivos de Datos:** Los archivos de datos transaccionales, créditos y ahorros crudos deben estar ubicados en la carpeta `datos/` con el formato esperado en `main.py` (`DataSabanaCred*.xls`, `DatsSabanaAhorro*.csv`, `Trns*.csv`).