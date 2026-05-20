import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt

# -------------------------------
# CONFIGURACIÓN STREAMLIT
# -------------------------------
st.set_page_config(
    page_title="Smart Yoga Studio",
    layout="wide"
)

# -------------------------------
# TITULO PRINCIPAL
# -------------------------------
st.markdown("""
<h1 style='
    text-align: center;
    color: #8b6f5a;
    font-size: 52px;
    font-weight: 700;
    margin-bottom: 0;
    font-family: "Quicksand", sans-serif;
'>
Smart Yoga Studio
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    margin-top:10px;
    margin-bottom:40px;
    color:#8b6f5a;
    font-size:28px;
    font-weight:700;
    font-family:'Quicksand', sans-serif;
">
Equilibrio entre temperatura, humedad y bienestar 🌿
</div>
""", unsafe_allow_html=True)

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
# FUNCIÓN DE LUZ
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
# QUERY A INFLUXDB
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

df["intensidad_luz"] = df.apply(
    lambda row: intensidad_luz(row["temperature"], row["humidity"]),
    axis=1
)

# -------------------------------
# ESTILO GENERAL - YOGA STUDIO
# -------------------------------
st.markdown("""
<style>

    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
        color: #8b6f5a !important;
    }

    /* FONDO */
    .stApp {
        background: linear-gradient(
            180deg,
            #faf7f2 0%,
            #f2e5d8 45%,
            #e8d7c5 100%
        );
    }

    /* TITULOS */
    h1, h2, h3 {
        color: #8b6f5a !important;
        font-weight: 700;
    }

    /* TABLAS */
    .stDataFrame {
        background: #f4e6d8 !important;
        border-radius: 22px;
        padding: 12px;
        box-shadow: 0px 5px 12px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.5);
    }

    /* ENCABEZADO TABLA */
    thead tr th {
        background-color: #c49a7a !important;
        color: #fffaf5 !important;
        text-align: center !important;
        font-size: 14px !important;
    }

    /* FILAS */
    tbody tr:nth-child(even) {
        background-color: #fff8f1 !important;
    }

    tbody tr:nth-child(odd) {
        background-color: #f7eadc !important;
    }

    /* TEXTO */
    tbody td {
        color: #7b5e4b !important;
        text-align: center !important;
        font-weight: 600 !important;
    }

    /* METRICAS */
    div[data-testid="metric-container"] {
        background: linear-gradient(
            145deg,
            rgba(255,255,255,0.7),
            rgba(245,236,224,0.85)
        );
        border: 1px solid rgba(255,255,255,0.5);
        padding: 25px;
        border-radius: 22px;
        text-align: center;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    }

    /* HISTORIAL */
    .bloque-historial {
        background: linear-gradient(
            145deg,
            rgba(255, 248, 240, 0.95),
            rgba(240, 224, 208, 0.95)
        );
        border-radius: 22px;
        padding: 18px;
        margin-bottom: 18px;
        border-left: 6px solid #c89f7a;
        box-shadow: 0px 6px 14px rgba(0,0,0,0.05);
        color: #7b5e4b !important;
    }

    /* CAJA LUZ */
    .titulo-luz {
        background: linear-gradient(
            135deg,
            #f8ede3,
            #e8d5c4
        );
        padding: 18px;
        border-radius: 22px;
        text-align: center;
        font-size: 26px;
        color: #7a5c3e;
        margin-top: 15px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.08);
        font-weight: 600;
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

fig.patch.set_facecolor('#f6f1eb')
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
