import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt

# -------------------------------
# CONFIGURACIÓN STREAMLIT
# -------------------------------
st.set_page_config(page_title="Dashboard IoT Luz Inteligente", layout="wide")

st.title("💡 Dashboard IoT - Control de Luz Inteligente")

# -------------------------------
# CONFIGURACIÓN INFLUXDB
# -------------------------------
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = "JoKdx3OFaBCFPmYQgiVWE8hjrtJ0lDkjwWZzT9djWJlvg98rtTgF9iRgKhQtAkKIA2UQsU6zsrJlv1BH6lfsVw=="
org = "miguelcmo"
bucket = "iot_telemetry_data"

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# -------------------------------
# FUNCIÓN DE LUZ (LA TUYA)
# -------------------------------
def intensidad_luz(temp, hum):

    if temp >= 26 and hum >= 70:
        return "🔴 Luz tenue (relajación profunda)"
    
    elif temp <= 20 and hum <= 30:
        return "🟡 Luz intensa (activar energía)"
    
    elif 20 <= temp <= 26 and 30 <= hum <= 70:
        return "🟢 Luz ideal (equilibrio)"
    
    else:
        return "🔵 Luz neutra"

# -------------------------------
# QUERY A INFLUXDB (90 MIN)
# -------------------------------
query = f'''
from(bucket: "{bucket}")
  |> range(start: -90m)
  |> filter(fn: (r) => r["_measurement"] == "environment")
  |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "humidity")
  |> aggregateWindow(every: 30m, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

result = query_api.query_data_frame(query)

# -------------------------------
# PROCESAMIENTO
# -------------------------------
if isinstance(result, list):
    df = pd.concat(result)
else:
    df = result

df["_time"] = pd.to_datetime(df["_time"])
df = df.sort_values("_time")
df = df[["_time", "temperature", "humidity"]]

# Aplicar lógica de luz
df["intensidad_luz"] = df.apply(
    lambda row: intensidad_luz(row["temperature"], row["humidity"]),
    axis=1
)

# -------------------------------
# VISUALIZACIÓN
# -------------------------------
st.subheader("📊 Datos Promedio (cada 30 min)")
st.dataframe(df)

# -------------------------------
# GRÁFICA
# -------------------------------
st.subheader("📈 Temperatura y Humedad")

fig, ax = plt.subplots()

ax.plot(df["_time"], df["temperature"], label="Temperatura")
ax.plot(df["_time"], df["humidity"], label="Humedad")

ax.set_xlabel("Tiempo")
ax.set_ylabel("Valores")
ax.legend()

st.pyplot(fig)

# -------------------------------
# ESTADO ACTUAL DE LA LUZ
# -------------------------------
st.subheader("💡 Estado actual de la luz")

ultima_fila = df.iloc[-1]

st.metric("Temperatura actual", f"{ultima_fila['temperature']:.2f} °C")
st.metric("Humedad actual", f"{ultima_fila['humidity']:.2f} %")
st.markdown(f"### {ultima_fila['intensidad_luz']}")

# -------------------------------
# HISTORIAL POR PERIODOS
# -------------------------------
st.subheader("⏱️ Historial de decisiones")

for i, row in df.iterrows():
    st.write(f"""
    **Periodo:** {row['_time']}  
    🌡️ Temp: {row['temperature']:.2f} °C  
    💧 Hum: {row['humidity']:.2f} %  
    💡 Luz: {row['intensidad_luz']}  
    ---
    """)
