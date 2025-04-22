import streamlit as st
import pandas as pd

st.set_page_config(page_title="MADI – Módulo de Análisis de Datos Institucionales")

st.title("📊 MADI – Módulo de Análisis de Datos Institucionales")
st.write("Consulta de datos de matrículas en universidades colombianas.")

# Simulación de rol: Admin o Usuario
rol = st.sidebar.radio("Seleccione su rol:", ["Usuario", "Administrador"])

# Variable para almacenar datos cargados por el administrador
if "datos" not in st.session_state:
    st.session_state["datos"] = None

# Vista del administrador: cargar archivo
if rol == "Administrador":
    st.subheader("🔐 Zona de administrador")
    archivo = st.file_uploader("📥 Subir archivo Excel con datos de matriculados", type=["xlsx"])
    
    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            columnas_requeridas = ["Año", "Universidad", "Programa", "Número de matriculados", "Semestre"]
            if all(col in df.columns for col in columnas_requeridas):
                st.session_state["datos"] = df
                st.success("✅ Archivo cargado correctamente. Los usuarios ya pueden consultar la información.")
                st.dataframe(df.head())
            else:
                st.error("❌ El archivo no contiene todas las columnas requeridas.")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

# Vista del usuario: consultar información
elif rol == "Usuario":
    st.subheader("👥 Consulta de información")

    if st.session_state["datos"] is None:
        st.warning("⚠️ Aún no se ha cargado ningún archivo. Espera a que el administrador suba los datos.")
    else:
        df = st.session_state["datos"]

        # Filtros
        año = st.selectbox("Selecciona el año:", sorted(df["Año"].dropna().unique()))
        universidad = st.selectbox("Selecciona la universidad:", sorted(df["Universidad"].dropna().unique()))
        programa = st.selectbox("Selecciona el programa:", sorted(df["Programa"].dropna().unique()))
        semestre = st.selectbox("Selecciona el semestre:", sorted(df["Semestre"].dropna().unique()))

        # Filtrar datos
        filtro = (
            (df["Año"] == año) &
            (df["Universidad"] == universidad) &
            (df["Programa"] == programa) &
            (df["Semestre"] == semestre)
        )
        datos_filtrados = df[filtro]

        st.subheader("📈 Resultados de la consulta")
        if not datos_filtrados.empty:
            total = datos_filtrados["Número de matriculados"].sum()
            st.success(f"Total de matriculados: **{int(total):,}**")
            st.dataframe(datos_filtrados)
        else:
            st.warning("No se encontraron datos con los filtros seleccionados.")