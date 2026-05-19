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
url = st.secrets["INFLUX_URL"]
token = st.secrets["INFLUX_TOKEN"]
org = st.secrets["INFLUX_ORG"]
bucket = st.secrets["INFLUX_BUCKET"]

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
# -------------------------------
# ESTILO GENERAL - YOGA STUDIO
# -------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #f5efe6, #e8dccf);
        color: #4b3f35;
        font-family: 'Trebuchet MS', sans-serif;
    }

    h1, h2, h3 {
        color: #6d5c4d;
        font-weight: 600;
    }

    .stDataFrame {
        background-color: rgba(255,255,255,0.6);
        border-radius: 15px;
        padding: 10px;
    }

    div[data-testid="metric-container"] {
        background-color: rgba(255,255,255,0.65);
        border: 1px solid #d8c3a5;
        padding: 20px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
    }

    div[data-testid="metric-container"] label {
        color: #7a6855;
        font-size: 16px;
    }

    div[data-testid="metric-container"] div {
        color: #4b3f35;
    }

    .bloque-historial {
        background-color: rgba(255,255,255,0.55);
        padding: 18px;
        border-radius: 16px;
        margin-bottom: 15px;
        border-left: 6px solid #c8a97e;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
    }

    .titulo-luz {
        background-color: rgba(255,255,255,0.55);
        padding: 12px;
        border-radius: 15px;
        text-align: center;
        font-size: 24px;
        color: #7a5c3e;
        margin-top: 10px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# VISUALIZACIÓN
# -------------------------------
st.subheader("🧘 Datos Promedio del Ambiente")

st.dataframe(df, use_container_width=True)

# -------------------------------
# GRÁFICA
# -------------------------------
st.subheader("🌿 Temperatura y Humedad del Salón")

fig, ax = plt.subplots(figsize=(10, 5))

fig.patch.set_facecolor('#f5efe6')
ax.set_facecolor('#fffaf5')

ax.plot(
    df["_time"],
    df["temperature"],
    label="Temperatura",
    linewidth=3,
    marker='o'
)

ax.plot(
    df["_time"],
    df["humidity"],
    label="Humedad",
    linewidth=3,
    marker='o'
)

ax.set_xlabel("Tiempo")
ax.set_ylabel("Valores")

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(alpha=0.2)

ax.legend()

st.pyplot(fig)

# -------------------------------
# ESTADO ACTUAL DE LA LUZ
# -------------------------------
st.subheader("🪷 Estado Actual del Ambiente")

ultima_fila = df.iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🌡️ Temperatura actual",
        f"{ultima_fila['temperature']:.2f} °C"
    )

with col2:
    st.metric(
        "💧 Humedad actual",
        f"{ultima_fila['humidity']:.2f} %"
    )

st.markdown(
    f"""
    <div class="titulo-luz">
        💡 {ultima_fila['intensidad_luz']}
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# HISTORIAL POR PERIODOS
# -------------------------------
st.subheader("🕯️ Historial de Decisiones")

for i, row in df.iterrows():
    st.markdown(
        f"""
        <div class="bloque-historial">
            <b>⏱️ Periodo:</b> {row['_time']} <br><br>
            🌡️ <b>Temperatura:</b> {row['temperature']:.2f} °C <br>
            💧 <b>Humedad:</b> {row['humidity']:.2f} % <br>
            💡 <b>Luz:</b> {row['intensidad_luz']}
        </div>
        """,
        unsafe_allow_html=True
    )
