import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="📊",
    layout="wide"
)

st.markdown("<h1 style='color:#6a1b9a;'>MADI – Módulo de Análisis de Datos Institucionales</h1>", unsafe_allow_html=True)
st.markdown("Consulta y visualización de datos sobre matrículas en universidades colombianas.")

# Autenticación básica
rol = st.sidebar.selectbox("Selecciona tu rol", ["Usuario", "Administrador"])

if rol == "Administrador":
    clave = st.sidebar.text_input("Contraseña de administrador", type="password")
    if clave != "admin123":  # puedes cambiar esta clave
        st.warning("Contraseña incorrecta. Acceso restringido.")
        st.stop()

# Inicializar datos si no existen en la sesión
if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Funcionalidad según el rol
if rol == "Administrador":
    st.subheader("Zona de administración")
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            columnas_requeridas = ["Año", "Universidad", "Programa", "Número de matriculados", "Semestre"]
            if all(col in df.columns for col in columnas_requeridas):
                st.session_state["datos"] = df
                st.success("Archivo cargado correctamente.")
                st.dataframe(df.head())
            else:
                st.error("El archivo no contiene todas las columnas requeridas.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

elif rol == "Usuario":
    st.subheader("Consulta de información")

    if st.session_state["datos"] is None:
        st.info("Aún no se han cargado datos. Espera a que el administrador suba el archivo.")
    else:
        df = st.session_state["datos"]

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            año = st.selectbox("Año", sorted(df["Año"].dropna().unique()))
            programa = st.selectbox("Programa", sorted(df["Programa"].dropna().unique()))
        with col2:
            universidad = st.selectbox("Universidad", sorted(df["Universidad"].dropna().unique()))
            semestre = st.selectbox("Semestre", sorted(df["Semestre"].dropna().unique()))

        # Filtrar datos
        filtro = (
            (df["Año"] == año) &
            (df["Universidad"] == universidad) &
            (df["Programa"] == programa) &
            (df["Semestre"] == semestre)
        )
        resultado = df[filtro]

        st.subheader("Resultados de la consulta")
        if not resultado.empty:
            total = resultado["Número de matriculados"].sum()
            st.markdown(f"<h4 style='color:#6a1b9a;'>Total de matriculados: {int(total):,}</h4>", unsafe_allow_html=True)
            st.dataframe(resultado)
        else:
            st.warning("No se encontraron datos con esos filtros.")
