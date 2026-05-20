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
# ESTILOS
# -------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Quicksand', sans-serif;
    color: #6f5442 !important;
}

/* FONDO */
.stApp {
    background: linear-gradient(
        180deg,
        #faf6f1 0%,
        #f1e2d3 100%
    );
}

/* TITULOS */
h1, h2, h3 {
    color: #6f5442 !important;
    text-align: center;
}

/* TARJETAS */
.card {
    background: #f3e4d6;
    border-radius: 25px;
    padding: 25px;
    text-align: center;
    border: 1px solid #d9bea8;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* HISTORIAL */
.historial-box {
    background: #f3e4d6;
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.04);
    color: #6f5442 !important;
    text-align: center;
}

/* TABLA */
.stDataFrame {
    background: #f3e4d6 !important;
    border-radius: 20px;
    padding: 10px;
    border: 1px solid #e0c7b2;
}

/* HEADER TABLA */
thead tr th {
    background-color: #c49a7a !important;
    color: white !important;
    text-align: center !important;
}

/* FILAS */
tbody tr:nth-child(even) {
    background-color: #fff8f1 !important;
}

tbody tr:nth-child(odd) {
    background-color: #f9eee3 !important;
}

/* TEXTO TABLA */
tbody td {
    color: #6f5442 !important;
    text-align: center !important;
    font-weight: 600 !important;
}

/* FRASE */
.frase {
    text-align: center;
    color: #7b5e4b;
    font-size: 30px;
    font-weight: 700;
    margin-top: 35px;
    margin-bottom: 35px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITULO
# -------------------------------
st.markdown("""
<h1 style="
    text-align:center;
    color:#7b5e4b;
    font-size:55px;
    font-weight:700;
">
Smart Yoga Studio
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    color:#8b6f5a;
    font-size:28px;
    font-weight:700;
    margin-top:10px;
    margin-bottom:40px;
">
Equilibrio entre temperatura, humedad y bienestar 🌿
</div>
""", unsafe_allow_html=True)

# -------------------------------
# CONFIGURACIÓN INFLUXDB
# -------------------------------
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = "TU_TOKEN_AQUI"
org = "miguelcmo"
bucket = "iot_telemetry_data"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

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

# -------------------------------
# APLICAR LÓGICA
# -------------------------------
df["intensidad_luz"] = df.apply(
    lambda row: intensidad_luz(
        row["temperature"],
        row["humidity"]
    ),
    axis=1
)

ultima_fila = df.iloc[-1]

# -------------------------------
# TARJETAS PRINCIPALES
# -------------------------------
col1, col2, col3 = st.columns(3)

# TEMPERATURA
with col1:

    st.markdown(f"""
    <div class="card">

        <img src="https://cdn-icons-png.flaticon.com/512/4814/4814268.png" width="90">

        <h2>Temperatura</h2>

        <div style="
            font-size:38px;
            font-weight:700;
            color:#6f5442;
            margin-top:10px;
        ">
            {ultima_fila['temperature']:.2f} °C
        </div>

    </div>
    """, unsafe_allow_html=True)

# HUMEDAD
with col2:

    st.markdown(f"""
    <div class="card">

        <img src="https://cdn-icons-png.flaticon.com/512/728/728093.png" width="90">

        <h2>Humedad</h2>

        <div style="
            font-size:38px;
            font-weight:700;
            color:#6f5442;
            margin-top:10px;
        ">
            {ultima_fila['humidity']:.2f} %
        </div>

    </div>
    """, unsafe_allow_html=True)

# LUZ
with col3:

    st.markdown(f"""
    <div class="card">

        <img src="https://cdn-icons-png.flaticon.com/512/3103/3103446.png" width="90">

        <h2>Luz Inteligente</h2>

        <div style="
            font-size:22px;
            font-weight:700;
            color:#6f5442;
            margin-top:12px;
        ">
            {ultima_fila['intensidad_luz']}
        </div>

    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# FRASE
# -------------------------------
st.markdown("""
<div class="frase">
🪷 Respira profundo, tu espacio está en equilibrio 🪷
</div>
""", unsafe_allow_html=True)

# -------------------------------
# HISTORIAL
# -------------------------------
st.subheader("🌿 Registro del Ambiente")

for i, row in df.iterrows():

    st.markdown(
        f"""
        <div class="historial-box">

            <b>⏱️ Periodo:</b> {row['_time']} <br><br>

            🌡️ <b>Temperatura:</b>
            {row['temperature']:.2f} °C <br><br>

            💧 <b>Humedad:</b>
            {row['humidity']:.2f} % <br><br>

            💡 <b>Luz:</b>
            {row['intensidad_luz']}

        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# TABLA
# -------------------------------
st.subheader("📋 Tabla de Datos")

st.dataframe(
    df,
    use_container_width=True
)

# -------------------------------
# GRAFICA PEQUEÑA
# -------------------------------
st.subheader("📈 Tendencia del Ambiente")

col_g1, col_g2, col_g3 = st.columns([1.8, 2, 1.8])

with col_g2:

    fig, ax = plt.subplots(figsize=(3.5, 2))

    fig.patch.set_facecolor('#faf6f1')
    ax.set_facecolor('#fffaf5')

    ax.plot(
        df["_time"],
        df["temperature"],
        linewidth=2,
        marker='o',
        color="#d08b5b",
        label="Temp"
    )

    ax.plot(
        df["_time"],
        df["humidity"],
        linewidth=2,
        marker='o',
        color="#8bb9d9",
        label="Hum"
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.grid(alpha=0.15)

    ax.tick_params(axis='x', labelsize=5, colors="#6f5442")
    ax.tick_params(axis='y', labelsize=5, colors="#6f5442")

    ax.legend(fontsize=5)

    st.pyplot(fig)
