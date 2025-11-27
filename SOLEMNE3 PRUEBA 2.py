# app.py
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Análisis de Países en Español", layout="wide")

# ==========================
# 1. CARGA DE DATOS DESDE API CON MANEJO DE ERRORES
# ==========================
@st.cache_data
def cargar_datos():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,area,languages,currencies"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        # Verificar que sea JSON
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
        # Capital segura
        capital = pais.get("capital")
        if capital and len(capital) > 0:
            capital = capital[0]
        else:
            capital = "No existe"

        lista.append({
            "Nombre": pais.get("name", {}).get("common", "No existe"),
            "Población": pais.get("population", 0),
            "Área (km²)": pais.get("area", 0),
            "Región": pais.get("region", "No existe"),
            "Subregión": pais.get("subregion", "No existe"),
            "Capital": capital,
            "Idioma(s)": ", ".join(pais.get("languages", {}).values()) if pais.get("languages") else "No existe",
            "Moneda(s)": ", ".join([v.get("name", "No existe") for v in pais.get("currencies", {}).values()]) if pais.get("currencies") else "No existe"
        })
    df = pd.DataFrame(lista)
    return df

df = cargar_datos()
if df.empty:
    st.stop()  # Detiene la app si no hay datos

st.title("Análisis de países del mundo (datos en español)")

# ==========================
# 2. COMPONENTES DE FILTRO
# ==========================
st.sidebar.header("Filtros")

region_sel = st.sidebar.selectbox(
    "Selecciona región",
    options=["Todas"] + list(df["Región"].dropna().unique()) if "Región" in df.columns else ["Todas"]
)

subregion_sel = st.sidebar.multiselect(
    "Selecciona subregión",
    options=df["Subregión"].dropna().unique() if "Subregión" in df.columns else []
)

poblacion_min, poblacion_max = st.sidebar.slider(
    "Rango de población",
    int(df["Población"].min()), int(df["Población"].max()),
    (int(df["Población"].min()), int(df["Población"].max()))
)

# Aplicar filtros
df_filtrado = df.copy()
if region_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Región"] == region_sel]
if subregion_sel:
    df_filtrado = df_filtrado[df_filtrado["Subregión"].isin(subregion_sel)]
df_filtrado = df_filtrado[(df_filtrado["Población"] >= poblacion_min) & (df_filtrado["Población"] <= poblacion_max)]

st.write(f"Se muestran {len(df_filtrado)} países tras aplicar los filtros")
st.dataframe(df_filtrado)

# ==========================
# 3. GRÁFICOS
# ==========================
st.subheader("Visualizaciones")

# --- 1. Barra de población por país (Top 10) ---
st.markdown("**Población por país (Top 10)**")
top10 = df_filtrado.sort_values("Población", ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x="Población", y="Nombre", data=top10, palette="viridis")
plt.xlabel("Población")
plt.ylabel("País")
st.pyplot(plt)
plt.clf()

# --- 2. Histograma de áreas ---
st.markdown("**Distribución de área (km²)**")
plt.figure(figsize=(10,6))
sns.histplot(df_filtrado["Área (km²)"], bins=20, kde=True, color="skyblue")
plt.xlabel("Área (km²)")
plt.ylabel("Cantidad de países")
st.pyplot(plt)
plt.clf()

# --- 3. Pie de regiones ---
st.markdown("**Distribución por región**")
if "Región" in df_filtrado.columns and not df_filtrado["Región"].empty:
    reg_counts = df_filtrado["Región"].value_counts()
    plt.figure(figsize=(6,6))
    plt.pie(reg_counts, labels=reg_counts.index, autopct="%1.1f%%", startangle=140)
    st.pyplot(plt)
    plt.clf()
else:
    st.write("No hay datos para mostrar el pie de regiones.")

# --- 4. Scatter: Área vs Población ---
st.markdown("**Relación entre área y población**")
plt.figure(figsize=(10,6))
sns.scatterplot(
    x="Área (km²)",
    y="Población",
    hue="Región" if "Región" in df_filtrado.columns else None,
    data=df_filtrado,
    palette="tab10",
    s=100
)
plt.xlabel("Área (km²)")
plt.ylabel("Población")
st.pyplot(plt)
plt.clf()

# ==========================
# 4. RESUMEN Y CONCLUSIONES
# ==========================
st.subheader("Resumen y conclusiones")
st.markdown("""
- Los gráficos permiten comparar población, área y distribución por región de manera visual.
- El histograma muestra que la mayoría de los países tiene áreas relativamente pequeñas comparadas con unos pocos gigantes.
- La relación entre área y población no siempre es proporcional: algunos países muy grandes tienen poca población y viceversa.
- Con estos filtros y gráficos interactivos, se puede explorar la información por región, subregión y rango de población.
""")

# ==========================
# 5. EXPLORACIÓN ADICIONAL
# ==========================
st.subheader("Exploración de un país")
if not df_filtrado.empty:
    pais_sel = st.selectbox("Selecciona un país para ver detalles", options=df_filtrado["Nombre"].sort_values())
    info_pais = df_filtrado[df_filtrado["Nombre"] == pais_sel].iloc[0]

    st.write(f"**Nombre:** {info_pais.get('Nombre', 'No existe')}")
    st.write(f"**Capital:** {info_pais.get('Capital', 'No existe')}")
    st.write(f"**Región / Subregión:** {info_pais.get('Región', 'No existe')} / {info_pais.get('Subregión', 'No existe')}")
    st.write(f"**Población:** {info_pais.get('Población', 'No existe')}")
    st.write(f"**Área (km²):** {info_pais.get('Área (km²)', 'No existe')}")
    st.write(f"**Idiomas:** {info_pais.get('Idioma(s)', 'No existe')}")
    st.write(f"**Monedas:** {info_pais.get('Moneda(s)', 'No existe')}")
else:
    st.write("No hay países que cumplan con los filtros seleccionados.")
