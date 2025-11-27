import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests

st.title("Gasto Municipal en Chile")

# Cargar datos desde API
url = "https://presupuestoabierto.gob.cl/municipalities"
resp = requests.get(url)
data = resp.json()

# Convertir JSON a DataFrame
df = pd.DataFrame(data)

# Muestra de datos
st.subheader("Datos")
st.dataframe(df)

# Columns del dataset
col_año = "year"
col_region = "region"
col_nombre = "commune"
col_cant = "amount"

# Widgets en la barra lateral
años = sorted(df[col_año].unique())
regions = sorted(df[col_region].unique())

año_sel = st.sidebar.selectbox("Año", años)
region_sel = st.sidebar.selectbox("Región", regions)

df_seleccion = df[df[col_año] == año_sel]
df_seleccion = df_seleccion[df_seleccion[col_region] == region_sel]

municipalidades = sorted(df_seleccion[col_nombre].unique())
municip_sel = st.sidebar.selectbox("Municipalidad", municipalidades)

df_seleccion = df_seleccion[df_seleccion[col_nombre] == municipal_sel]

# Monto seleccionado
cantidad = df_seleccion[col_cant].values[0]
st.sidebar.markdown(f"### Gasto: ${cantidad:,.0f}")

# Gráfico simple
st.subheader("Gasto por Año")

df_gasto_annual = df[df[col_nombre] == municipal_sel]

fig, ax = plt.subplots()
ax.plot(df_gasto_annual[col_año], df_gasto_annual[col_cant], marker="o")
ax.set_xlabel("Año")
ax.set_ylabel("Gasto")
st.pyplot(fig)
