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
# CONFIGURACIÓN STREAMLIT
# -------------------------------
st.set_page_config(
    page_title="Dashboard IoT Luz Inteligente",
    layout="wide"
)

st.title("🧘 Smart Yoga Studio")

st.markdown("""
<div style="
    text-align:center;
    margin-top:-10px;
    margin-bottom:30px;
    color:#7a6855;
    font-size:18px;
    font-family:'Poppins', sans-serif;
">
Equilibrio entre temperatura, humedad y bienestar 🌿
</div>
""", unsafe_allow_html=True)

# -------------------------------
# ESTILO GENERAL
# -------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Quicksand', sans-serif;
}

/* FONDO */
.stApp {
    background: linear-gradient(
        180deg,
        #f8f5f1 0%,
        #efe3d3 40%,
        #e4d4c2 100%
    );
    color: #5d4d42;
}

/* TITULOS */
h1, h2, h3 {
    color: #6b5a4f;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* SUBTITULOS */
.stSubheader {
    color: #7c6757;
}

/* TARJETAS */
.card {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(8px);
    border-radius: 25px;
    padding: 25px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.07);
    border: 1px solid rgba(255,255,255,0.4);
    text-align:center;
}

/* METRICAS */
div[data-testid="metric-container"] {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.75),
        rgba(248,239,228,0.95)
    );
    border-radius: 25px;
    padding: 25px;
    border: none;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.07);
}

div[data-testid="metric-container"] label {
    color: #826b58;
    font-size: 18px;
    font-weight: 600;
}

div[data-testid="metric-container"] div {
    color: #5a4a40;
}

/* ESTADO LUZ */
.luz-box {
    background: linear-gradient(
        135deg,
        #f8ede3,
        #ecd7c4
    );
    border-radius: 25px;
    padding: 20px;
    text-align:center;
    font-size: 28px;
    font-weight: 700;
    color: #7a5b3f;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
}

/* HISTORIAL */
.bloque-historial {
    background: rgba(255,255,255,0.45);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 18px;
    border-left: 6px solid #d0ab83;
    box-shadow: 0px 5px 14px rgba(0,0,0,0.05);
}

/* TABLA PEQUEÑA */
.stDataFrame {
    background: rgba(255,255,255,0.35);
    border-radius: 15px;
    padding: 8px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.04);
}

/* TABLA INTERNA */
thead tr th {
    background-color: #ccb39a !important;
    color: white !important;
    text-align:center !important;
}

tbody tr:nth-child(even) {
    background-color: #f8f2eb !important;
}

tbody tr:nth-child(odd) {
    background-color: #fffaf5 !important;
}

/* GRAFICA */
.element-container:has(canvas) {
    background: rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 10px;
    margin-top: 10px;
}

/* ICONOS */
.icon-img {
    width: 95px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# ESTADO ACTUAL DEL AMBIENTE
# -------------------------------
st.subheader("🌿 Estado Actual del Ambiente")

ultima_fila = df.iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/1684/1684375.png">
        <h3 style="color:#7a6855;">Humedad</h3>
    </div>
    """, unsafe_allow_html=True)

    st.metric(
        "💧 Humedad actual",
        f"{ultima_fila['humidity']:.2f} %"
    )

with col2:
    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/4814/4814268.png">
        <h3 style="color:#7a6855;">Temperatura</h3>
    </div>
    """, unsafe_allow_html=True)

    st.metric(
        "🌡️ Temperatura actual",
        f"{ultima_fila['temperature']:.2f} °C"
    )

with col3:
    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/4341/4341139.png">
        <h3 style="color:#7a6855;">Luz Inteligente</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="luz-box">
            {ultima_fila['intensidad_luz']}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# FRASE RELAJANTE
# -------------------------------
st.markdown("""
<div style="
    text-align:center;
    margin-top:35px;
    margin-bottom:35px;
    font-size:22px;
    color:#826b58;
    font-weight:600;
">
🪷 Respira profundo, tu espacio está en equilibrio 🪷
</div>
""", unsafe_allow_html=True)

# -------------------------------
# HISTORIAL
# -------------------------------
st.subheader("🕯️ Historial del Ambiente")

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

# -------------------------------
# TABLA Y GRAFICA AL FINAL
# -------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.subheader("📊 Registro del Ambiente")

st.dataframe(
    df,
    use_container_width=True,
    height=200
)

# -------------------------------
# GRAFICA PEQUEÑA
# -------------------------------
st.subheader("📈 Tendencia del Ambiente")

fig, ax = plt.subplots(figsize=(7, 3))

fig.patch.set_facecolor('#f8f5f1')
ax.set_facecolor('#fffaf8')

ax.plot(
    df["_time"],
    df["temperature"],
    label="Temperatura",
    linewidth=2,
    marker='o',
    color="#ef8f6f"
)

ax.plot(
    df["_time"],
    df["humidity"],
    label="Humedad",
    linewidth=2,
    marker='o',
    color="#7bb6d9"
)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(alpha=0.2)

ax.tick_params(axis='x', labelsize=8)
ax.tick_params(axis='y', labelsize=8)

ax.legend()

st.pyplot(fig)
