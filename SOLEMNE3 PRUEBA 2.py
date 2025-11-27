import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Análisis de Países en Español", layout="wide")

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

st.title("Análisis de países del mundo (datos en español)")
st.dataframe(df)

st.subheader("Visualizaciones")

# Población por país (Top 10)
top10 = df.sort_values("Población", ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x="Población", y="Nombre", data=top10, palette="viridis")
st.pyplot(plt)
plt.clf()

# Distribución de área
plt.figure(figsize=(10,6))
sns.histplot(df["Área (km²)"], bins=20, kde=True, color="skyblue")
st.pyplot(plt)
plt.clf()

# Distribución por región
if not df["Región"].empty:
    reg_counts = df["Región"].value_counts()
    plt.figure(figsize=(6,6))
    plt.pie(reg_counts, labels=reg_counts.index, autopct="%1.1f%%", startangle=140)
    st.pyplot(plt)
    plt.clf()

# Relación área vs población
plt.figure(figsize=(10,6))
sns.scatterplot(
    x="Área (km²)",
    y="Población",
    hue="Región",
    data=df,
    palette="tab10",
    s=100
)
st.pyplot(plt)
plt.clf()

# Exploración de un país
st.subheader("Exploración de un país")
pais_sel = st.selectbox("Selecciona un país para ver detalles", options=df["Nombre"].sort_values())
info_pais = df[df["Nombre"] == pais_sel].iloc[0]
st.write(info_pais.to_dict())
