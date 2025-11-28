import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análisis de países", layout="wide")

# Datos API
@st.cache_data
def cargar_datos():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,area,languages,currencies"
    try:
        resp = requests.get(url, timeout=10)
# manejo de error URL
        if resp.status_code != 200:
            st.error(f"Error HTTP {resp.status_code}: No se pudo obtener la información.")
            return pd.DataFrame()

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


df["Región"] = df["Región"].replace({
    "Americas": "América",
    "Europe": "Europa",
    "Antarctic": "Antártica",
    "Africa":   "África",
    "Oceania":  "Oceanía"
})

# Título y descripción
st.title("Análisis de países")
st.markdown("""
Esta aplicación permite explorar información de países obtenida desde la **API REST pública RestCountries**.
Se pueden analizar población, área, regiones, subregiones, idiomas y monedas de manera interactiva.
""")

# Pestañas
tab1, tab2 = st.tabs([" Visualizaciones", "Datos completos"])

# visualizaciones
with tab1:
    st.subheader("Población por país (Top 10)")
    top10 = df.sort_values("Población", ascending=False).head(10)
    
    width = st.sidebar.slider("plot width", 0.1, 25., 3.)
    height = st.sidebar.slider("plot height", 0.1, 25., 1.)

    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.barh(top10["Nombre"], top10["Población"])
    ax.set_xlabel("Población")
    ax.set_ylabel("País")
    ax.set_title("Top 10 países más poblados")
    plt.tight_layout()
    st.pyplot(fig)

    st.write("China e India son los países con mayor población del mundo.")

    st.subheader("Distribución de área (km²)")

    regiones = df["Región"].unique()
    mapa_colores = {region: color for region, color in zip(regiones, plt.cm.tab20.colors)}
    df_sorted = df.sort_values("Área (km²)")

    fig, ax = plt.subplots(figsize=(13, 5))

    for region in regiones:
        sub = df_sorted[df_sorted["Región"] == region]
        ax.plot(
            sub["Área (km²)"].values,
            marker="o",
            linestyle="-",
            label=region,
            color=mapa_colores[region]
        )

    ax.set_xlabel("Índice de continentes (ordenado por área)")
    ax.set_ylabel("Área (km²)")
    ax.set_title("Distribución de área de los continentes")
    ax.legend(title="Continentes")

    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Distribución por Continentes")
    reg_counts = df["Región"].value_counts()

    fig, ax = plt.subplots(figsize=(width, height))
    ax.pie(reg_counts.values, labels=reg_counts.index, autopct='%1.1f%%')
    ax.set_title("Proporción de países por Continentes")
    st.pyplot(fig)

    st.subheader("Relación entre área y población")
    fig, ax = plt.subplots(figsize=(10, 6))

    for region in regiones:
        subset = df[df["Región"] == region]
        ax.scatter(
            subset["Área (km²)"],
            subset["Población"],
            color=mapa_colores[region],
            label=region
        )

    ax.set_xlabel("Área (km²)")
    ax.set_ylabel("Población")
    ax.set_title("Área vs Población por país")
    ax.legend(title="Continentes")

    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("Tabla completa de datos")
    st.dataframe(df)
    st.download_button(
        label="Descargar datos como CSV",
        data=df.to_csv(index=False),
        file_name="paises.csv",
        mime="text/csv"
    )


















