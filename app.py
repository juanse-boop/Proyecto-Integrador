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
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(8px);
    border-radius: 28px;
    padding: 22px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    border: 1px solid rgba(255,255,255,0.5);
    text-align:center;
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
    background: rgba(255,255,255,0.45);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 18px;
    border-left: 6px solid #d4b293;
    box-shadow: 0px 5px 14px rgba(0,0,0,0.05);
}

/* TABLA */
.stDataFrame {
    background: rgba(232, 221, 209, 0.85);
    border-radius: 20px;
    padding: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
}

/* ENCABEZADO TABLA */
thead tr th {
    background-color: #a98467 !important;
    color: #fffaf5 !important;
    text-align:center !important;
    font-size: 14px !important;
}

/* FILAS */
tbody tr:nth-child(even) {
    background-color: #f6ede4 !important;
}

tbody tr:nth-child(odd) {
    background-color: #efe2d3 !important;
}

/* TEXTO TABLA */
tbody td {
    color: #8b6f5a !important;
    text-align:center !important;
    font-weight: 500 !important;
}

/* GRAFICA */
.element-container:has(canvas) {
    background: rgba(255,255,255,0.3);
    border-radius: 18px;
    padding: 10px;
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

</style>
""", unsafe_allow_html=True)

# -------------------------------
# ESTADO ACTUAL DEL AMBIENTE
# -------------------------------
ultima_fila = df.iloc[-1]

col1, col2, col3 = st.columns(3)

# -------------------------------
# HUMEDAD
# -------------------------------
with col1:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/4148/4148460.png">
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

# -------------------------------
# TEMPERATURA
# -------------------------------
with col2:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/869/869869.png">
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

# -------------------------------
# LUZ
# -------------------------------
with col3:

    st.markdown("""
    <div class="card">
        <img class="icon-img" src="https://cdn-icons-png.flaticon.com/512/3103/3103446.png">
        <h3>Luz Inteligente</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">💡 Estado de la luz</div>
            <div class="info-value" style="font-size:22px;">
                {ultima_fila['intensidad_luz']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# FRASE RELAJANTE
# -------------------------------
st.markdown("""
<div class="frase-yoga">
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

fig, ax = plt.subplots(figsize=(5, 2.2))

fig.patch.set_facecolor('#faf7f2')
ax.set_facecolor('#fffaf6')

ax.plot(
    df["_time"],
    df["temperature"],
    label="Temperatura",
    linewidth=2,
    marker='o',
    color="#f29b77"
)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(alpha=0.15)

ax.tick_params(axis='x', labelsize=6, colors="#8b6f5a")
ax.tick_params(axis='y', labelsize=6, colors="#8b6f5a")

ax.legend(fontsize=6)

st.pyplot(fig)
