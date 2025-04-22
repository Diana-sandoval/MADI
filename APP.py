import streamlit as st
import pandas as pd
import hashlib

st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="📊",
    layout="wide"
)

# Simulación de base de datos de usuarios
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "admin@madi.com": {"password": "admin123", "rol": "Administrador"}
    }

# Función para hashear contraseñas (opcional, puedes usarla si quieres encriptar)
def hashear(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

# Pantalla de inicio
st.markdown("""
    <h1 style='color:#6a1b9a;text-align:center;'>📊 MADI</h1>
    <h3 style='text-align:center;'>Módulo de Análisis de Matrículas Universitarias</h3>
    <p style='text-align:center;'>Visualiza y analiza datos de matrículas universitarias en Colombia</p>
""", unsafe_allow_html=True)

# Autenticación y registro
menu = st.sidebar.radio("Selecciona una opción", ["Iniciar sesión", "Registrarse"])

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

if menu == "Registrarse":
    st.sidebar.subheader("📝 Crear una cuenta")
    nuevo_correo = st.sidebar.text_input("Correo electrónico")
    nueva_clave = st.sidebar.text_input("Contraseña", type="password")
    boton_registro = st.sidebar.button("Registrarse")

    if boton_registro:
        if nuevo_correo in st.session_state.usuarios:
            st.sidebar.warning("⚠️ Este correo ya está registrado.")
        else:
            st.session_state.usuarios[nuevo_correo] = {
                "password": nueva_clave,
                "rol": "Usuario"
            }
            st.sidebar.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")

if menu == "Iniciar sesión":
    st.sidebar.subheader("🔑 Iniciar sesión")
    correo = st.sidebar.text_input("Correo electrónico")
    clave = st.sidebar.text_input("Contraseña", type="password")
    iniciar = st.sidebar.button("Iniciar sesión")

    if iniciar:
        if correo in st.session_state.usuarios and clave == st.session_state.usuarios[correo]["password"]:
            st.session_state.autenticado = True
            st.session_state.usuario = correo
            st.session_state.rol = st.session_state.usuarios[correo]["rol"]
            st.success(f"Bienvenido {correo} ({st.session_state.rol})")
        else:
            st.sidebar.error("Correo o contraseña incorrectos")

if not st.session_state.autenticado:
    st.stop()

if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Administrador: subir múltiples archivos Excel
if st.session_state.rol == "Administrador":
    st.subheader("🛠️ Zona de administración")
    archivos = st.file_uploader("📄 Subir uno o más archivos Excel con datos de matrícula", type=["xlsx"], accept_multiple_files=True)

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
                df.columns = df.columns.str.strip().str.upper()
                columnas_encontradas = [col for col in columnas_deseadas if col in df.columns]
                if len(columnas_encontradas) >= 4:
                    df_filtrado = df[columnas_encontradas]
                    df_filtrado = df_filtrado.rename(columns={
                        "AÑO": "Año",
                        "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)": "Universidad",
                        "PROGRAMA ACADÉMICO": "Programa",
                        "SEMESTRE": "Semestre",
                        "SEXO": "Sexo",
                        "MATRICULADOS": "Número de matriculados"
                    })
                    dfs.append(df_filtrado)
                else:
                    st.warning(f"⚠️ El archivo '{archivo.name}' no contiene suficientes columnas requeridas.")
            except Exception as e:
                st.error(f"❌ Error al leer el archivo '{archivo.name}': {e}")

        if dfs:
            df_consolidado = pd.concat(dfs, ignore_index=True)
            st.session_state["datos"] = df_consolidado
            st.success("✅ Archivos cargados y consolidados correctamente")
            st.dataframe(df_consolidado.head(), use_container_width=True)

# Usuario: consulta interactiva
elif st.session_state.rol == "Usuario":
    st.subheader("🔍 Consulta interactiva de matrículas")

    if st.session_state["datos"] is None:
        st.info("📉 Aún no se han cargado datos. Espera a que el administrador suba el archivo.")
    else:
        df = st.session_state["datos"]

        with st.expander("🔎 Filtros de búsqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.selectbox("📅 Año", sorted(df["Año"].dropna().unique()))
            with col2:
                universidad = st.selectbox("🏫 Universidad", sorted(df["Universidad"].dropna().unique()))
            with col3:
                programa = st.selectbox("🎓 Programa", sorted(df["Programa"].dropna().unique()))
            semestre = st.selectbox("📚 Semestre", sorted(df["Semestre"].dropna().unique()))

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
            st.markdown(f"<h4 style='color:#2e7d32;'>👨‍🎓 Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("❌ No se encontraron resultados con esos filtros.")

# Pie de página
st.markdown("""
    <hr style='border:1px solid #ccc;'>
    <p style='text-align:center; font-size:14px;'>Desarrollado por Diana Sandoval & Maria Pulido • Proyecto MADI © 2025</p>
""", unsafe_allow_html=True)
