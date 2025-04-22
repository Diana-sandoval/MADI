import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <h1 style='color:#6a1b9a;'>📊 MADI – Módulo de Análisis de Datos Institucionales</h1>
    <p style='font-size:18px;'>Consulta interactiva y visualización de datos de matrícula en universidades colombianas.</p>
""", unsafe_allow_html=True)

# Autenticación básica
rol = st.sidebar.radio("Selecciona tu rol", ["Usuario", "Administrador"], index=0)

if rol == "Administrador":
    clave = st.sidebar.text_input("Contraseña de administrador", type="password")
    if clave != "admin123":  # puedes cambiar esta clave
        st.sidebar.error("Contraseña incorrecta. Acceso restringido.")
        st.stop()

# Inicializar datos en la sesión si no existen
if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Funcionalidad para el administrador
if rol == "Administrador":
    st.subheader("🔧 Zona de administración")
    archivo = st.file_uploader("📂 Subir archivo Excel con datos de matrícula", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            columnas_deseadas = ["Año", "Universidad", "Programa", "Semestre", "Sexo", "Número de matriculados"]
            columnas_encontradas = [col for col in columnas_deseadas if col in df.columns]

            if len(columnas_encontradas) >= 4:
                df = df[columnas_encontradas]  # Filtrar solo las columnas importantes
                st.session_state["datos"] = df
                st.success("✅ Archivo cargado correctamente.")
                st.dataframe(df.head(), use_container_width=True)
            else:
                st.error("⚠️ El archivo no contiene suficientes columnas requeridas para su análisis.")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

# Funcionalidad para el usuario
elif rol == "Usuario":
    st.subheader("🔍 Consulta de información de matrículas")

    if st.session_state["datos"] is None:
        st.info("⚠️ Aún no se han cargado datos. Espera a que el administrador suba el archivo.")
    else:
        df = st.session_state["datos"]

        with st.expander("🧮 Aplicar filtros", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.selectbox("📅 Año", sorted(df["Año"].dropna().unique()))
            with col2:
                universidad = st.selectbox("🏛️ Universidad", sorted(df["Universidad"].dropna().unique()))
            with col3:
                programa = st.selectbox("🎓 Programa", sorted(df["Programa"].dropna().unique()))
            col4 = st.selectbox("📘 Semestre", sorted(df["Semestre"].dropna().unique()))

        # Aplicar filtros
        filtro = (
            (df["Año"] == año) &
            (df["Universidad"] == universidad) &
            (df["Programa"] == programa) &
            (df["Semestre"] == col4)
        )
        resultado = df[filtro]

        st.subheader("📈 Resultados de la consulta")
        if not resultado.empty:
            total = resultado["Número de matriculados"].sum()
            st.markdown(f"<h4 style='color:#388e3c;'>Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("No se encontraron datos con esos filtros. Prueba con otros criterios.")
