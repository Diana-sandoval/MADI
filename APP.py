import streamlit as st
import pandas as pd
import hashlib

st.set_page_config(
    page_title="MADI – Módulo de Análisis de Datos Institucionales",
    page_icon="\ud83d\udcc8",
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
    <h1 style='color:#6a1b9a;text-align:center;'>\ud83d\udcc8 MADI</h1>
    <h3 style='text-align:center;'>M\u00f3dulo de An\u00e1lisis de Datos Institucionales</h3>
    <p style='text-align:center;'>Visualiza y analiza datos de matr\u00edculas universitarias en Colombia</p>
""", unsafe_allow_html=True)

# Autenticaci\u00f3n y registro
menu = st.sidebar.radio("Selecciona una opci\u00f3n", ["Iniciar sesi\u00f3n", "Registrarse"])

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

if menu == "Registrarse":
    st.sidebar.subheader("\ud83d\udcdd Crear una cuenta")
    nuevo_correo = st.sidebar.text_input("Correo electr\u00f3nico")
    nueva_clave = st.sidebar.text_input("Contrase\u00f1a", type="password")
    boton_registro = st.sidebar.button("Registrarse")

    if boton_registro:
        if nuevo_correo in st.session_state.usuarios:
            st.sidebar.warning("\u26a0\ufe0f Este correo ya est\u00e1 registrado.")
        else:
            st.session_state.usuarios[nuevo_correo] = {
                "password": nueva_clave,
                "rol": "Usuario"
            }
            st.sidebar.success("\u2705 Registro exitoso. Ahora puedes iniciar sesi\u00f3n.")

if menu == "Iniciar sesi\u00f3n":
    st.sidebar.subheader("\ud83d\udd10 Iniciar sesi\u00f3n")
    correo = st.sidebar.text_input("Correo electr\u00f3nico")
    clave = st.sidebar.text_input("Contrase\u00f1a", type="password")
    iniciar = st.sidebar.button("Iniciar sesi\u00f3n")

    if iniciar:
        if correo in st.session_state.usuarios and clave == st.session_state.usuarios[correo]["password"]:
            st.session_state.autenticado = True
            st.session_state.usuario = correo
            st.session_state.rol = st.session_state.usuarios[correo]["rol"]
            st.success(f"Bienvenido {correo} ({st.session_state.rol})")
        else:
            st.sidebar.error("Correo o contrase\u00f1a incorrectos")

if not st.session_state.autenticado:
    st.stop()

if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Administrador: subir m\u00faltiples archivos Excel
if st.session_state.rol == "Administrador":
    st.subheader("\ud83d\udee0\ufe0f Zona de administraci\u00f3n")
    archivos = st.file_uploader("\ud83d\udcc4 Subir uno o m\u00e1s archivos Excel con datos de matr\u00edcula", type=["xlsx"], accept_multiple_files=True)

    if archivos:
        dfs = []
        columnas_deseadas = [
            "A\u00d1O",
            "INSTITUCI\u00d3N DE EDUCACI\u00d3N SUPERIOR (IES)",
            "PROGRAMA ACAD\u00c9MICO",
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
                        "A\u00d1O": "A\u00f1o",
                        "INSTITUCI\u00d3N DE EDUCACI\u00d3N SUPERIOR (IES)": "Universidad",
                        "PROGRAMA ACAD\u00c9MICO": "Programa",
                        "SEMESTRE": "Semestre",
                        "SEXO": "Sexo",
                        "MATRICULADOS": "N\u00famero de matriculados"
                    })
                    dfs.append(df_filtrado)
                else:
                    st.warning(f"\u26a0\ufe0f El archivo '{archivo.name}' no contiene suficientes columnas requeridas.")
            except Exception as e:
                st.error(f"\u274c Error al leer el archivo '{archivo.name}': {e}")

        if dfs:
            df_consolidado = pd.concat(dfs, ignore_index=True)
            st.session_state["datos"] = df_consolidado
            st.success("\u2705 Archivos cargados y consolidados correctamente")
            st.dataframe(df_consolidado.head(), use_container_width=True)

# Usuario: consulta interactiva
elif st.session_state.rol == "Usuario":
    st.subheader("\ud83d\udd0d Consulta interactiva de matr\u00edculas")

    if st.session_state["datos"] is None:
        st.info("\ud83d\udcc1 A\u00fan no se han cargado datos. Espera a que el administrador suba el archivo.")
    else:
        df = st.session_state["datos"]

        with st.expander("\ud83d\udd0e Filtros de b\u00fasqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.selectbox("\ud83d\udcc5 A\u00f1o", sorted(df["A\u00f1o"].dropna().unique()))
            with col2:
                universidad = st.selectbox("\ud83c\udfdb\ufe0f Universidad", sorted(df["Universidad"].dropna().unique()))
            with col3:
                programa = st.selectbox("\ud83c\udf93 Programa", sorted(df["Programa"].dropna().unique()))
            semestre = st.selectbox("\ud83d\udcd8\ufe0f Semestre", sorted(df["Semestre"].dropna().unique()))

        filtro = (
            (df["A\u00f1o"] == año) &
            (df["Universidad"] == universidad) &
            (df["Programa"] == programa) &
            (df["Semestre"] == semestre)
        )
        resultado = df[filtro]

        st.subheader("\ud83d\udcc8 Resultados")
        if not resultado.empty:
            total = resultado["N\u00famero de matriculados"].sum()
            st.markdown(f"<h4 style='color:#2e7d32;'>\ud83d\udc65 Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("\u274c No se encontraron resultados con esos filtros.")

# Pie de p\u00e1gina
st.markdown("""
    <hr style='border:1px solid #ccc;'>
    <p style='text-align:center; font-size:14px;'>Desarrollado por Diana Sandoval & Maria Pulido • Proyecto MADI © 2025</p>
""", unsafe_allow_html=True)
