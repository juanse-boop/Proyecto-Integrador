# -------------------------------
# IMPORTS
# -------------------------------
import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt
from datetime import datetime
import random

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

# ICONO ZEN
st.markdown("""
<div style='
text-align:center;
font-size:70px;
margin-top:-10px;
margin-bottom:10px;
'>
🪷
</div>
""", unsafe_allow_html=True)

# SUBTITULO
st.markdown("""
<div style="
    text-align:center;
    margin-top:10px;
    margin-bottom:20px;
    color:#8b6f5a;
    font-size:28px;
    font-weight:700;
    font-family:'Quicksand', sans-serif;
">
Equilibrio entre temperatura, humedad y bienestar 🌿
</div>
""", unsafe_allow_html=True)

# HORA ACTUAL
zona_colombia = pytz.timezone("America/Bogota")
hora_actual = datetime.now().strftime("%I:%M:%S %p")

st.markdown(f"""
<div style="
text-align:center;
color:#9b7b65;
font-size:18px;
margin-bottom:35px;
">
🕒 Hora actual del sistema: {hora_actual}
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

ultima_fila = df.iloc[-1]

# -------------------------------
# COLOR DINAMICO LUZ
# -------------------------------
estado = ultima_fila['intensidad_luz']

if "🔴" in estado:
    color_luz = "#e7b8b8"

elif "🟡" in estado:
    color_luz = "#e8d8a8"

elif "🟢" in estado:
    color_luz = "#bfd8c1"

else:
    color_luz = "#c7d5e5"

# -------------------------------
# FRASES ALEATORIAS
# -------------------------------
frases = [
    "✨ Tu cuerpo escucha cada respiración",
    "🪷 El equilibrio comienza en el ambiente",
    "🌿 Respira y conecta contigo",
    "☁️ Un espacio tranquilo transforma la mente"
]

# -------------------------------
# ESTILOS
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

/* TARJETAS */
.card {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(14px);
    border-radius: 28px;
    padding: 22px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    border: 1px solid rgba(255,255,255,0.5);
    text-align:center;
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-6px);
}

/* ICONOS */
.icon-img {
    width: 85px;
    margin-bottom: 10px;
}

/* RECUADROS VARIABLES */
.info-box {
    background: linear-gradient(
        145deg,
        #fffaf5,
        #f3e5d7
    );
    border: 2px solid #d8b89c;
    border-radius: 24px;
    padding: 18px;
    margin-top: 15px;
    text-align: center;
    box-shadow: 0px 6px 16px rgba(0,0,0,0.06);
}

/* TITULO DENTRO DEL RECUADRO */
.info-title {
    font-size: 18px;
    font-weight: 700;
    color: #7b5e4b !important;
}

/* VALORES */
.info-value {
    font-size: 30px;
    font-weight: 800;
    color: #5f4636 !important;
    margin-top: 10px;
}

/* HISTORIAL */
.bloque-historial {
    background: #f4e7da;
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 18px;
    border-left: 6px solid #c89f7a;
    box-shadow: 0px 6px 14px rgba(0,0,0,0.05);
    color: #7b5e4b !important;
    transition: 0.3s ease;
}

.bloque-historial:hover {
    transform: scale(1.01);
}

/* TABLA */
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

/* GRAFICA */
.element-container:has(canvas) {
    background: rgba(255,255,255,0.45);
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
}

/* TEXTO RELAJANTE */
.frase-yoga {
    text-align:center;
    margin-top:40px;
    margin-bottom:40px;
    font-size:32px;
    font-weight:700;
    color:#8b6f5a;
}

/* OCULTAR STREAMLIT */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# ESTADO ACTUAL DEL AMBIENTE
# -------------------------------
col1, col2, col3 = st.columns(3)

# HUMEDAD
with col1:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/728/728093.png">
        <h3>Humedad</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">💧 Nivel de humedad</div>
            <div class="info-value">{ultima_fila['humidity']:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# TEMPERATURA
with col2:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/1684/1684375.png">
        <h3>Temperatura</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">🌡️ Temperatura actual</div>
            <div class="info-value">{ultima_fila['temperature']:.2f}°C</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# LUZ
with col3:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/427/427735.png">
        <h3>Luz Inteligente</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-box" style="background:{color_luz};">
            <div class="info-title">💡 Estado de la luz</div>
            <div class="info-value" style="font-size:22px;">
                {ultima_fila['intensidad_luz']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# BARRA BIENESTAR
# -------------------------------
st.progress(85)

st.markdown("""
<div style="
text-align:center;
color:#8b6f5a;
font-size:18px;
font-weight:600;
margin-top:10px;
">
Nivel de bienestar del ambiente: 85%
</div>
""", unsafe_allow_html=True)

# -------------------------------
# FRASE RELAJANTE
# -------------------------------
st.markdown(f"""
<div class="frase-yoga">
{random.choice(frases)}
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SEPARADOR
# -------------------------------
st.markdown("""
<hr style="
border: 1px solid #d9bfa9;
margin-top:40px;
margin-bottom:40px;
opacity:0.4;
">
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
# TABLA
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("📊 Registro del Ambiente")

st.dataframe(
    df,
    use_container_width=True,
    height=180
)

# -------------------------------
# GRAFICA PEQUEÑA
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("📈 Tendencia del Ambiente")

col1, col2, col3 = st.columns([1.5, 2, 1.5])

with col2:

    fig, ax = plt.subplots(figsize=(2.8, 1.4))

    fig.patch.set_facecolor('#faf7f2')
    ax.set_facecolor('#fffaf6')

    ax.plot(
        df["_time"],
        df["temperature"],
        linewidth=1.8,
        marker='o',
        color="#f29b77"
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.grid(alpha=0.10)

    ax.tick_params(axis='x', labelsize=4, colors="#8b6f5a")
    ax.tick_params(axis='y', labelsize=4, colors="#8b6f5a")

    st.pyplot(fig)
