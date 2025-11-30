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
    opciones = ["Población por país (Top 10)", "Distribución de área (km²)", "Distribución de paises por Continentes", "Área vs Población por país"]
    selection = st.pills("Elija el grafico para Visualizar", opciones, selection_mode="single")

    if selection == "Población por país (Top 10)" :
        st.subheader("Población por país (Top 10)")
        
        top10 = df.sort_values("Población", ascending=False).head(10)
    
        fig, ax = plt.subplots(figsize=(10, 3))
        bars = ax.barh(top10["Nombre"], top10["Población"])
        
        on = st.toggle("Mostrar valores numericos.")
        if on:
            ax.bar_label(bars, label_type='center', padding = 2, fontsize=6)
        
        ax.set_xlabel("Población")
        ax.set_ylabel("País")
        ax.set_title("Top 10 países más poblados")
        plt.tight_layout()
        st.pyplot(fig)

 
    if selection == "Distribución de área (km²)" :
        st.subheader("Distribución de área (km²)")
    
        regiones = df["Región"].unique()
        mapa_colores = {region: color for region, color in zip(regiones, plt.cm.tab20.colors)}
        df_sorted = df.sort_values("Área (km²)")
        
        fig, ax = plt.subplots(figsize=(13, 5))
        v = st.slider("Elije estilo de lineas.", 1, 4, 1,1)
        if v == 1:
            styleL = "-"
            styleM = "."
        elif v == 2:
            styleL = "--"
            styleM = "s"
        elif v == 3:
            styleL = "-."
            styleM = "x"
        elif v == 4:
            styleL = ":"
            styleM = "o"
            
        for region in regiones:
            sub = df_sorted[df_sorted["Región"] == region]
            ax.plot(
                sub["Área (km²)"].values,
                marker=styleM,
                linestyle=styleL,
                label=region,
                color=mapa_colores[region]
            )
        ax.set_xlabel("Índice de continentes (ordenado por área)")
        ax.set_ylabel("Área (km²)")
        ax.set_title("Distribución de área de los continentes")
        ax.legend(title="Continentes")
        plt.tight_layout()
        st.pyplot(fig)

 
    if selection == "Distribución de paises por Continentes" :
        st.subheader("Distribución de paises por Continentes")
        reg_counts = df["Región"].value_counts()
    
        fig, ax = plt.subplots(figsize=(2, 8))
        pies = ax.pie(reg_counts.values, labels=reg_counts.index, textprops={'fontsize': 4}, autopct='%1.1f%%')
        ax.set_title("Proporción de países por Continentes", fontdict={'fontsize': 15})
        st.pyplot(fig)

    if selection == "Área vs Población por país" :
        st.subheader("Relación entre área y población")
        regiones = df["Región"].unique()
        mapa_colores = {region: color for region, color in zip(regiones, plt.cm.tab20.colors)}
        fig, ax = plt.subplots(figsize=(8.5, 4))
        continente = st.selectbox(
            "Continente Especifico",
            ("Ninguno", "Home phone", "Mobile phone"),
        )
        for region in regiones:
            if continente != "Ninguno":
                if region != continente:
                    continue
                else:
                    subset = df[df["Región"] == region]
                    ax.scatter(
                        subset["Área (km²)"],
                        subset["Población"],
                        color=mapa_colores[region],
                        label=region
                    )
            else:
                subset = df[df["Región"] == region]
                ax.scatter(
                        subset["Área (km²)"],
                        subset["Población"],
                        color=mapa_colores[region],
                        label=region
                )
        
        ax.set_xlabel("Área (km²)")
        ax.set_ylabel("Población")
        ax.set_title("Área vs Población de cada país por Continente")
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



































































