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

    /* FUENTE GENERAL */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* FONDO GENERAL */
    .stApp {
        background: linear-gradient(
            180deg,
            #f6f1eb 0%,
            #efe4d6 35%,
            #e2d4c2 100%
        );
        color: #4e4035;
    }

    /* TITULOS */
    h1, h2, h3 {
        color: #6b5b4d;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* SUBHEADERS */
    .stSubheader {
        background-color: rgba(255,255,255,0.35);
        padding: 10px 18px;
        border-radius: 15px;
        backdrop-filter: blur(5px);
    }

    /* TABLAS */
    .stDataFrame {
        background: rgba(255,255,255,0.45);
        border-radius: 18px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }

    /* TABLA INTERNA */
    table {
        border-collapse: collapse !important;
        border-radius: 14px;
        overflow: hidden;
    }

    thead tr th {
        background-color: #b08968 !important;
        color: white !important;
        font-size: 15px !important;
        text-align: center !important;
        border: none !important;
    }

    tbody tr:nth-child(even) {
        background-color: #f7efe7 !important;
    }

    tbody tr:nth-child(odd) {
        background-color: #fffaf5 !important;
    }

    tbody td {
        color: #5b4b3d !important;
        text-align: center !important;
        border: none !important;
        font-size: 14px !important;
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

    div[data-testid="metric-container"] label {
        color: #7a6756;
        font-size: 16px;
        font-weight: 500;
    }

    div[data-testid="metric-container"] div {
        color: #4b3f35;
    }

    /* HISTORIAL */
    .bloque-historial {
        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.6),
            rgba(247,239,231,0.9)
        );
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 18px;
        border-left: 7px solid #c8a27a;
        box-shadow: 0px 5px 14px rgba(0,0,0,0.06);
        transition: 0.3s;
    }

    .bloque-historial:hover {
        transform: scale(1.01);
    }

    /* CAJA DE LUZ */
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
