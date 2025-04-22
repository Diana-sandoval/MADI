import streamlit as st
import pandas as pd
import hashlib

# Configuración general de la página
st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="📊",
    layout="wide"
)

# Base de usuarios simulada (puede conectarse con una base real si se desea)
usuarios = {
    "admin@madi.com": {"password": "admin123", "rol": "Administrador"},
    "usuario@madi.com": {"password": "usuario123", "rol": "Usuario"}
}

# Función para hashear contraseñas (simulación básica)
def hashear(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

# Interfaz de inicio de sesión
st.markdown("""
    <h1 style='color:#6a1b9a;text-align:center;'>📊 MADI</h1>
    <h3 style='text-align:center;'>Módulo de Análisis de Datos Institucionales</h3>
    <p style='text-align:center;'>Visualiza y analiza datos de matrículas universitarias en Colombia</p>
""", unsafe_allow_html=True)

st.sidebar.title("🔐 Inicio de sesión")
correo = st.sidebar.text_input("Correo electrónico")
clave = st.sidebar.text_input("Contraseña", type="password")
iniciar = st.sidebar.button("Iniciar sesión")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

if iniciar:
    if correo in usuarios and clave == usuarios[correo]["password"]:
        st.session_state.autenticado = True
        st.session_state.rol = usuarios[correo]["rol"]
        st.success(f"Bienvenido {correo} ({st.session_state.rol})")
    else:
        st.error("Correo o contraseña incorrectos")

# Si no está autenticado, se detiene todo
if not st.session_state.autenticado:
    st.stop()

# Inicializar datos en sesión
if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Funcionalidad para el Administrador
if st.session_state.rol == "Administrador":
    st.subheader("🛠️ Zona de administración")
    archivo = st.file_uploader("📤 Subir archivo Excel con datos de matrícula", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            columnas_deseadas = ["Año", "Universidad", "Programa", "Semestre", "Sexo", "Número de matriculados"]
            columnas_encontradas = [col for col in columnas_deseadas if col in df.columns]
            if len(columnas_encontradas) >= 4:
                df = df[columnas_encontradas]
                st.session_state["datos"] = df
                st.success("✅ Archivo cargado correctamente")
                st.dataframe(df.head(), use_container_width=True)
            else:
                st.error("⚠️ El archivo no contiene suficientes columnas requeridas.")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

# Funcionalidad para el Usuario
elif st.session_state.rol == "Usuario":
    st.subheader("🔍 Consulta interactiva de matrículas")

    if st.session_state["datos"] is None:
        st.info("📁 Aún no se han cargado datos. Espera a que el administrador suba el archivo.")
    else:
        df = st.session_state["datos"]

        with st.expander("🔎 Filtros de búsqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.selectbox("📅 Año", sorted(df["Año"].dropna().unique()))
            with col2:
                universidad = st.selectbox("🏛️ Universidad", sorted(df["Universidad"].dropna().unique()))
            with col3:
                programa = st.selectbox("🎓 Programa", sorted(df["Programa"].dropna().unique()))
            semestre = st.selectbox("📘 Semestre", sorted(df["Semestre"].dropna().unique()))

        filtro = (
            (df["Año"] == año) &
            (df["Universidad"] == universidad) &
            (df["Programa"] == programa) &
            (df["Semestre"] == semestre)
        )
        resultado = df[filtro]

        st.subheader("📈 Resultados")
        if not resultado.empty:
            total = resultado["Número de matriculados"].sum()
            st.markdown(f"<h4 style='color:#2e7d32;'>👥 Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("❌ No se encontraron resultados con esos filtros.")

# Pie de página personalizado
st.markdown("""
    <hr style='border:1px solid #ccc;'>
    <p style='text-align:center; font-size:14px;'>Desarrollado por Diana Sandoval & Maria Pulido • Proyecto MADI © 2025</p>
""", unsafe_allow_html=True)
