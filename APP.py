import streamlit as st
import pandas as pd
import hashlib

st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="📊",
    layout="wide"
)

# Inicialización de usuarios
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "admin@madi.com": {"password": "admin123", "rol": "Administrador"}
    }

# Función para hash de contraseñas (puedes usar más adelante si deseas seguridad adicional)
def hashear(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

# Autenticación
st.markdown("""
    <h1 style='color:#6a1b9a;text-align:center;'>📊 MADI</h1>
    <h3 style='text-align:center;'>Módulo de Análisis de Datos Institucionales</h3>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Menú", ["Iniciar sesión", "Registrarse"])

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

if menu == "Registrarse":
    st.sidebar.subheader("📝 Registro")
    email = st.sidebar.text_input("Correo")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Registrarse"):
        if email in st.session_state.usuarios:
            st.sidebar.warning("⚠️ Este usuario ya existe.")
        else:
            st.session_state.usuarios[email] = {"password": password, "rol": "Usuario"}
            st.sidebar.success("✅ Registro exitoso.")

if menu == "Iniciar sesión":
    st.sidebar.subheader("🔐 Iniciar sesión")
    correo = st.sidebar.text_input("Correo electrónico")
    clave = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Entrar"):
        if correo in st.session_state.usuarios and clave == st.session_state.usuarios[correo]["password"]:
            st.session_state.autenticado = True
            st.session_state.usuario = correo
            st.session_state.rol = st.session_state.usuarios[correo]["rol"]
            st.success(f"Bienvenido {correo}")
        else:
            st.sidebar.error("Credenciales incorrectas")

if not st.session_state.autenticado:
    st.stop()

if "datos" not in st.session_state:
    st.session_state["datos"] = pd.DataFrame()

# Subida de múltiples archivos
if st.session_state.rol == "Administrador":
    st.subheader("🛠️ Zona de administración")
    archivos = st.file_uploader("📥 Subir archivos Excel", type=["xlsx"], accept_multiple_files=True)

    if archivos:
        dfs = []
        columnas_deseadas = [
            "AÑO",
            "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)",
            "PROGRAMA ACADÉMICO",
            "SEMESTRE",
            "SEXO",
            "MATRICULADOS"
        ]

        for archivo in archivos:
            try:
                df = pd.read_excel(archivo)
                df.columns = [c.upper().strip() for c in df.columns]
                columnas_encontradas = [col for col in columnas_deseadas if col in df.columns]
                df = df[columnas_encontradas]
                df = df.rename(columns={
                    "AÑO": "Año",
                    "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)": "Universidad",
                    "PROGRAMA ACADÉMICO": "Programa",
                    "SEMESTRE": "Semestre",
                    "SEXO": "Sexo",
                    "MATRICULADOS": "Número de matriculados"
                })
                dfs.append(df)
            except Exception as e:
                st.error(f"❌ Error en archivo: {e}")

        if dfs:
            datos_consolidados = pd.concat(dfs, ignore_index=True)
            st.session_state["datos"] = datos_consolidados
            st.success("✅ Archivos cargados exitosamente")
            st.dataframe(datos_consolidados.head(), use_container_width=True)

# Usuario
elif st.session_state.rol == "Usuario":
    st.subheader("🔍 Consulta interactiva")

    if st.session_state["datos"].empty:
        st.info("Esperando a que el administrador suba archivos.")
    else:
        df = st.session_state["datos"]

        with st.expander("🔎 Filtros"):
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

        st.subheader("📊 Resultados")
        if not resultado.empty:
            total = resultado["Número de matriculados"].sum()
            st.markdown(f"<h4 style='color:#2e7d32;'>👥 Total matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("No se encontraron datos para esa combinación.")

# Footer
st.markdown("""
<hr>
<p style='text-align:center;'>🔧 Desarrollado por Diana Sandoval & Maria Pulido | Proyecto MADI © 2025</p>
""", unsafe_allow_html=True)
