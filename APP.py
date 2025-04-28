import os
import sqlite3
import pandas as pd
import streamlit as st

# Conexión a la base de datos SQLite
def crear_conexion():
    try:
        conexion = sqlite3.connect('madi.db', check_same_thread=False)
        return conexion
    except sqlite3.Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Crear las tablas si no existen
def crear_tablas(cursor):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                correo TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datos_matricula (
                año INTEGER,
                institucion TEXT,
                programa TEXT,
                semestre TEXT,
                sexo TEXT,
                matriculados INTEGER
            )
        ''')

        cursor.connection.commit()
    except sqlite3.Error as e:
        st.error(f"Error al crear tablas: {e}")

# Función para verificar usuario
def verificar_usuario(correo, password, cursor):
    try:
        cursor.execute('SELECT correo, password, rol FROM usuarios WHERE correo = ?', (correo,))
        user = cursor.fetchone()
        if user and user[1] == password:
            return user[2]
    except sqlite3.Error as e:
        st.error(f"Error al verificar usuario: {e}")
    return None

# Función para registrar usuario con rol
def registrar_usuario(correo, password, rol, cursor):
    if not correo or not password or not rol:
        return False  # No permitir campos vacíos
    try:
        # Verificar si el correo ya está registrado
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE correo = ?', (correo,))
        if cursor.fetchone()[0] > 0:
            return False  # El correo ya está registrado

        # Si el correo no existe, proceder a insertar el nuevo usuario
        cursor.execute('INSERT INTO usuarios (correo, password, rol) VALUES (?, ?, ?)', (correo, password, rol))
        cursor.connection.commit()
        return True
    except sqlite3.Error as e:
        # Si ocurre un error, hacer un rollback y mostrar el error
        cursor.connection.rollback()
        st.error(f"❌ Error al registrar el usuario: {e}")
        return False

# Crear usuario administrador por defecto si no existe
def crear_usuario_admin(cursor):
    try:
        cursor.execute('SELECT * FROM usuarios WHERE correo = ?', ('admin@madi.com',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO usuarios (correo, password, rol) VALUES (?, ?, ?)', ('admin@madi.com', 'admin123', 'Administrador'))
            cursor.connection.commit()
    except sqlite3.Error as e:
        st.error(f"Error al crear el usuario administrador: {e}")

# Estilos personalizados
st.markdown("""
    <style>
    body {
        background-color: #f3e5f5;
    }
    .stButton>button {
        background-color: #8e24aa;
        color: white;
        font-weight: bold;
    }
    .stSelectbox, .stTextInput, .stFileUploader, .stDataFrame {
        background-color: #f8bbd0;
        border: 2px solid #8e24aa;
        border-radius: 5px;
    }
    h1, h3, p, h4 {
        color: #6a1b9a;
    }
    .stSidebar .sidebar-content {
        background-color: #f3e5f5;
    }
    .stTextInput input {
        color: #8e24aa;
    }
    .stButton>button:hover {
        background-color: #6a1b9a;
    }
    </style>
""", unsafe_allow_html=True)

# Pantalla de inicio
st.markdown("""
    <h1 style='text-align:center;'>📊 MADI</h1>
    <h3 style='text-align:center;'>Módulo de Análisis de Datos Institucionales</h3>
    <p style='text-align:center;'>Visualiza y analiza datos de matrículas universitarias en Colombia</p>
""", unsafe_allow_html=True)

# Conexión a la base de datos
conexion = crear_conexion()
if conexion:
    cursor = conexion.cursor()

    # Crear tablas si no existen
    crear_tablas(cursor)

    # Crear usuario administrador por defecto si no existe
    crear_usuario_admin(cursor)

    # Variables de sesión
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.rol = None

    # Menú de la barra lateral
    menu = st.sidebar.radio("📋 Menú", ["Iniciar sesión", "Registrarse"])

    # Registro de usuarios
    if menu == "Registrarse":
        st.sidebar.subheader("📝 Crear una cuenta")
        nuevo_correo = st.sidebar.text_input("📧 Correo electrónico")
        nueva_clave = st.sidebar.text_input("🔒 Contraseña", type="password")
        rol = st.sidebar.selectbox("🎖️ Selecciona rol", ["Usuario", "Administrador"])
        boton_registro = st.sidebar.button("Registrarse")

        if boton_registro:
            if nuevo_correo.strip() == "" or nueva_clave.strip() == "":
                st.sidebar.warning("⚠️ Por favor completa todos los campos.")
            elif registrar_usuario(nuevo_correo.strip(), nueva_clave.strip(), rol, cursor):
                st.sidebar.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")
            else:
                st.sidebar.warning("⚠️ Este correo ya está registrado.")

    # Inicio de sesión
    if menu == "Iniciar sesión":
        st.sidebar.subheader("🔐 Iniciar sesión")
        correo = st.sidebar.text_input("📧 Correo electrónico", key="login_email")
        clave = st.sidebar.text_input("🔒 Contraseña", type="password", key="login_password")
        iniciar = st.sidebar.button("Iniciar sesión")

        if iniciar:
            rol = verificar_usuario(correo.strip(), clave.strip(), cursor)
            if rol:
                st.session_state.autenticado = True
                st.session_state.usuario = correo
                st.session_state.rol = rol
                st.success(f"Bienvenido {correo} ({rol})")
            else:
                st.sidebar.error("❌ Correo o contraseña incorrectos.")

    if not st.session_state.autenticado:
        st.stop()

    # Zona de administración
    if st.session_state.rol == "Administrador":
        st.subheader("🛠️ Zona de administración")
        archivos = st.file_uploader("📄 Subir archivos Excel", type=["xlsx"], accept_multiple_files=True)

        if archivos:
            columnas_deseadas = [
                "AÑO", "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)",
                "PROGRAMA ACADÉMICO", "SEMESTRE", "SEXO", "MATRICULADOS"
            ]

            dfs = []
            for archivo in archivos:
                try:
                    df = pd.read_excel(archivo)
                    df.columns = df.columns.str.strip().str.upper()
                    columnas_encontradas = [col for col in columnas_deseadas if col in df.columns]

                    if len(columnas_encontradas) >= 4:
                        df_filtrado = df[columnas_encontradas].rename(columns={
                            "AÑO": "Año",
                            "INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)": "Institución de Educación Superior (IES)",
                            "PROGRAMA ACADÉMICO": "Programa Académico",
                            "SEMESTRE": "Semestre",
                            "SEXO": "Sexo",
                            "MATRICULADOS": "Número de Matriculados"
                        })
                        dfs.append(df_filtrado)
                    else:
                        st.warning(f"⚠️ El archivo '{archivo.name}' no tiene suficientes columnas requeridas.")
                except Exception as e:
                    st.error(f"❌ Error leyendo el archivo '{archivo.name}': {e}")

            if dfs:
                df_consolidado = pd.concat(dfs, ignore_index=True)
                st.success("✅ Datos cargados exitosamente.")
                st.dataframe(df_consolidado.head(), use_container_width=True)

    # Zona de usuario
    elif st.session_state.rol == "Usuario":
        st.subheader("🔍 Consulta interactiva de matrículas")

        # Cargar los datos desde la base de datos
        df = pd.read_sql_query('SELECT * FROM datos_matricula', conexion)

        if df.empty:
            st.info("📊 No hay datos disponibles aún.")
        else:
            with st.expander("🔎 Filtros de búsqueda", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    año = st.selectbox("📅 Año", sorted(df["año"].dropna().unique()))
                with col2:
                    institucion = st.selectbox("🏫 Institución", sorted(df["institucion"].dropna().unique()))
                with col3:
                    programa = st.selectbox("📚 Programa", sorted(df["programa"].dropna().unique()))
                semestre = st.selectbox("📆 Semestre", sorted(df["semestre"].dropna().unique()))

            filtro = (
                (df["año"] == año) &
                (df["institucion"] == institucion) &
                (df["programa"] == programa) &
                (df["semestre"] == semestre)
            )
            resultado = df[filtro]

            st.subheader("📊 Resultados")
            if not resultado.empty:
                total = resultado["matriculados"].sum()
                st.markdown(f"<h4 style='color:#2e7d32;'>👩‍🎓 Total de matriculados: <strong>{int(total):,}</strong></h4>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)
            else:
                st.warning("❌ No se encontraron resultados para los filtros aplicados.")

    # Pie de página
    st.markdown("""
        <hr style='border:1px solid #ccc;'>
        <p style='text-align:center; font-size:14px;'>Desarrollado por Diana Sandoval & Maria Pulido • Proyecto MADI © 2025</p>
    """, unsafe_allow_html=True)
