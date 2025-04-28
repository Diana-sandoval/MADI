import os
import sqlite3
import pandas as pd
import streamlit as st

# Conexión a la base de datos SQLite
conexion = sqlite3.connect('madi.db', check_same_thread=False)
cursor = conexion.cursor()

# Crear tablas si no existen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        correo TEXT PRIMARY KEY,
        password TEXT,
        rol TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos_matricula (
        año INTEGER,
        universidad TEXT,
        programa TEXT,
        semestre TEXT,
        sexo TEXT,
        numero_matriculados INTEGER
    )
''')

conexion.commit()

# Función para verificar usuario
def verificar_usuario(correo, password):
    cursor.execute('SELECT correo, password, rol FROM usuarios WHERE correo = ?', (correo,))
    user = cursor.fetchone()
    if user and user[1] == password:
        return user[2]  # rol
    return None

# Función para registrar usuario
def registrar_usuario(correo, password):
    try:
        cursor.execute('INSERT INTO usuarios (correo, password, rol) VALUES (?, ?, ?)', (correo, password, 'Usuario'))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Crear usuario administrador si no existe
cursor.execute('SELECT * FROM usuarios WHERE correo = ?', ('admin@madi.com',))
if not cursor.fetchone():
    cursor.execute('INSERT INTO usuarios (correo, password, rol) VALUES (?, ?, ?)', ('admin@madi.com', 'admin123', 'Administrador'))
    conexion.commit()

# Pantalla de inicio
st.markdown("""
    <h1 style='color:#6a1b9a;text-align:center;'>📊 MADI</h1>
    <h3 style='text-align:center;'>Módulo de Análisis de Datos Institucionales</h3>
    <p style='text-align:center;'>Visualiza y analiza datos de matrículas universitarias en Colombia</p>
""", unsafe_allow_html=True)

# Variables de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

# Menú de la barra lateral
menu = st.sidebar.radio("Selecciona una opción", ["Iniciar sesión", "Registrarse"])

# Registro
if menu == "Registrarse":
    st.sidebar.subheader("📝 Crear una cuenta")
    nuevo_correo = st.sidebar.text_input("Correo electrónico")
    nueva_clave = st.sidebar.text_input("Contraseña", type="password")
    boton_registro = st.sidebar.button("Registrarse")

    if boton_registro:
        if registrar_usuario(nuevo_correo, nueva_clave):
            st.sidebar.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")
        else:
            st.sidebar.warning("⚠️ Este correo ya está registrado.")

# Inicio de sesión
if menu == "Iniciar sesión":
    st.sidebar.subheader("🔐 Iniciar sesión")
    correo = st.sidebar.text_input("Correo electrónico")
    clave = st.sidebar.text_input("Contraseña", type="password")
    iniciar = st.sidebar.button("Iniciar sesión")

    if iniciar:
        rol = verificar_usuario(correo, clave)
        if rol:
            st.session_state.autenticado = True
            st.session_state.usuario = correo
            st.session_state.rol = rol
            st.success(f"Bienvenido {correo} ({rol})")
        else:
            st.sidebar.error("Correo o contraseña incorrectos.")

if not st.session_state.autenticado:
    st.stop()

# Función para cargar datos en la base
def cargar_datos(df):
    for _, fila in df.iterrows():
        cursor.execute('''
            INSERT INTO datos_matricula (año, universidad, programa, semestre, sexo, numero_matriculados)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fila['Año'], fila['Universidad'], fila['Programa'], fila['Semestre'], fila['Sexo'], fila['Número de matriculados']))
    conexion.commit()

# Zona de administración
if st.session_state.rol == "Administrador":
    st.subheader("🛠️ Zona de administración")
    archivos = st.file_uploader("📄 Subir uno o más archivos Excel con datos de matrícula", type=["xlsx"], accept_multiple_files=True)

    if archivos:
        columnas_deseadas = [
            "AÑO",
            "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)",
            "PROGRAMA ACADÉMICO",
            "SEMESTRE",
            "SEXO",
            "MATRICULADOS"
        ]

        dfs = []
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
                    st.warning(f"⚠️ El archivo '{archivo.name}' no tiene suficientes columnas.")
            except Exception as e:
                st.error(f"❌ Error leyendo el archivo '{archivo.name}': {e}")

        if dfs:
            df_consolidado = pd.concat(dfs, ignore_index=True)
            cargar_datos(df_consolidado)
            st.success("✅ Datos cargados exitosamente.")
            st.dataframe(df_consolidado.head(), use_container_width=True)

# Zona de usuario
elif st.session_state.rol == "Usuario":
    st.subheader("🔍 Consulta interactiva de matrículas")

    # Cargar los datos desde la base
    df = pd.read_sql_query('SELECT * FROM datos_matricula', conexion)

    if df.empty:
        st.info("📊 No hay datos disponibles aún.")
    else:
        with st.expander("🔎 Filtros de búsqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.selectbox("📅 Año", sorted(df["año"].dropna().unique()))
            with col2:
                universidad = st.selectbox("🏫 Universidad", sorted(df["universidad"].dropna().unique()))
            with col3:
                programa = st.selectbox("📚 Programa", sorted(df["programa"].dropna().unique()))
            semestre = st.selectbox("📅 Semestre", sorted(df["semestre"].dropna().unique()))

        filtro = (
            (df["año"] == año) &
            (df["universidad"] == universidad) &
            (df["programa"] == programa) &
            (df["semestre"] == semestre)
        )
        resultado = df[filtro]

        st.subheader("📊 Resultados")
        if not resultado.empty:
            total = resultado["numero_matriculados"].sum()
            st.markdown(f"<h4 style='color:#2e7d32;'>👩‍🎓 Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("❌ No se encontraron resultados con esos filtros.")

# Pie de página
st.markdown("""
    <hr style='border:1px solid #ccc;'>
    <p style='text-align:center; font-size:14px;'>Desarrollado por Diana Sandoval & Maria Pulido • Proyecto MADI © 2025</p>
""", unsafe_allow_html=True)
