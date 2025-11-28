import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Análisis de países del mundo", layout="wide")
@st.cache_data
def cargar_datos():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,area,languages,currencies"
    try:
        resp = requests.get(url, timeout=10)

        # 🔁 Reemplazo de resp.raise_for_status() → Opción 1
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
