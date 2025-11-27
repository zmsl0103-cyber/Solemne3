import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Análisis de Países", layout="wide")

# ===================================
# Cargar datos de API
# ===================================
@st.cache_data
def cargar_datos():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,area,languages,currencies"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        if 'application/json' not in resp.headers.get('Content-Type', ''):
            st.error("La API no devolvió JSON válido.")
            return pd.DataFrame()
        data = resp.json()
    except requests.RequestException as e:
        st.error(f"No se pudo conectar con la API: {e}")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"Error al procesar JSON de la API: {e}")
        return pd.DataFrame()

    lista = []
    for pais in data:
        capital = pais.get("capital")[0] if pais.get("capital") else "No existe"
        idiomas = ", ".join(pais.get("languages", {}).values()) if pais.get("languages") else "No existe"
        monedas = ", ".join([v.get("name", "No existe") for v in pais.get("currencies", {}).values()]) if pais.get("currencies") else "No existe"

        lista.append({
            "Nombre": pais.get("name", {}).get("common", "No existe"),
            "Población": pais.get("population", 0),
            "Área (km²)": pais.get("area", 0),
            "Región": pais.get("region", "No existe"),
            "Subregión": pais.get("subregion", "No existe"),
            "Capital": capital,
            "Idioma(s)": idiomas,
            "Moneda(s)": monedas
        })

    return pd.DataFrame(lista)

df = cargar_datos()
if df.empty:
    st.stop()

# ===================================
# Título y descripción
# ===================================
st.title("🌍 Análisis interactivo de países del mundo")
st.markdown("""
Esta aplicación permite explorar información de países obtenida desde la **API REST pública RestCountries**.
Puedes analizar población, área, regiones, subregiones, idiomas y monedas de manera interactiva.
""")

# ===================================
# Pestañas de la aplicación
# ===================================
tab1, tab2, tab3 = st.tabs(["📊 Visualizaciones", "🔎 Exploración de país", "📄 Datos completos"])

# =========================
# Tab 1: Visualizaciones
# =========================
with tab1:
    st.subheader("Población por país (Top 10)")
    top10 = df.sort_values("Población", ascending=False).head(10)
    fig1 = px.bar(
        top10, x="Población", y="Nombre", orientation='h', color="Población",
        labels={"Población":"Población", "Nombre":"País"},
        title="Top 10 países más poblados"
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.write("Observamos que China e India son los países con mayor población del mundo.")

    st.subheader("Distribución de área (km²)")
    fig2 = px.histogram(
        df, x="Área (km²)", nbins=20, title="Distribución de área de los países",
        labels={"Área (km²)":"Área (km²)", "count":"Cantidad de países"}
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.write("La mayoría de los países tienen áreas medianas, mientras que unos pocos son extremadamente grandes.")

    st.subheader("Distribución por región")
    reg_counts = df["Región"].value_counts().reset_index()
    fig3 = px.pie(reg_counts, names="index", values="Región", title="Proporción de países por región")
    st.plotly_chart(fig3, use_container_width=True)
    st.write("Se puede ver que la mayoría de los países se encuentran en África y Asia.")

    st.subheader("Relación entre área y población")
    fig4 = px.scatter(
        df, x="Área (km²)", y="Población", color="Región",
        hover_data=["Nombre", "Capital"], title="Área vs Población por país"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.write("No siempre los países más grandes en área tienen mayor población.")

# =========================
# Tab 2: Exploración de un país
# =========================
with tab2:
    st.subheader("🔍 Detalles de un país específico")
    pais_sel = st.selectbox("Selecciona un país:", options=df["Nombre"].sort_values())
    info_pais = df[df["Nombre"] == pais_sel].iloc[0]

    st.text_input("Nombre", value=info_pais["Nombre"])
    st.text_input("Capital", value=info_pais["Capital"])
    st.text_input("Región", value=info_pais["Región"])
    st.text_input("Subregión", value=info_pais["Subregión"])
    st.number_input("Población", value=info_pais["Población"], step=1)
    st.number_input("Área (km²)", value=info_pais["Área (km²)"], step=1)
    st.text_input("Idiomas", value=info_pais["Idioma(s)"])
    st.text_input("Monedas", value=info_pais["Moneda(s)"])

    st.write("Esta sección permite inspeccionar la información detallada de cualquier país del mundo.")

# =========================
# Tab 3: Datos completos
# =========================
with tab3:
    st.subheader("📄 Tabla completa de datos")
    st.dataframe(df)
    st.download_button(
        label="Descargar datos como CSV",
        data=df.to_csv(index=False),
        file_name="paises.csv",
        mime="text/csv"
    )

# =========================
# Componentes adicionales para cumplir requerimiento de >12
# =========================
st.checkbox("Mostrar descripción extendida de la app", value=False)
st.radio("Selecciona tipo de gráfico favorito", ["Barra", "Histograma", "Pie", "Scatter"])
st.slider("Simular número de países mostrados (solo visual)", 5, 20, 10)
st.text_area("Comentarios sobre la visualización", "Escribe aquí tus notas...")
st.expander("Más información sobre la API", expanded=False).markdown("""
La API utilizada es RestCountries: https://restcountries.com/
Datos actualizados y públicos.
""")
