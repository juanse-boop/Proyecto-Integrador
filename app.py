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
    text-align:center;
    color:#8b6f5a;
    font-size:58px;
    font-weight:700;
    margin-top:10px;
    margin-bottom:0px;
    font-family:"Quicksand", sans-serif;
'>
🧘 Smart Yoga Studio
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    margin-top:15px;
    margin-bottom:40px;
    color:#8b6f5a;
    font-size:32px;
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
  |> filter(fn: (r) =>
      r["_field"] == "temperature" or
      r["_field"] == "humidity"
  )
  |> aggregateWindow(
      every: 30m,
      fn: mean,
      createEmpty: false
  )
  |> pivot(
      rowKey:["_time"],
      columnKey: ["_field"],
      valueColumn: "_value"
  )
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

df = df[[
    "_time",
    "temperature",
    "humidity"
]]

df["intensidad_luz"] = df.apply(
    lambda row: intensidad_luz(
        row["temperature"],
        row["humidity"]
    ),
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
}

/* PANEL PRINCIPAL */
.main-card {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(14px);
    border-radius: 32px;
    padding: 35px;
    text-align:center;
    box-shadow: 0px 10px 20px rgba(0,0,0,0.06);
    border:1px solid rgba(255,255,255,0.4);
}

/* TARJETAS */
.info-card {
    background: rgba(255,255,255,0.45);
    border-radius:26px;
    padding:24px;
    margin-bottom:20px;
    text-align:center;
    box-shadow:0px 8px 16px rgba(0,0,0,0.05);
}

/* HISTORIAL */
.bloque-historial {
    background: linear-gradient(
        145deg,
        #fff7ef,
        #f5e5d5
    );
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 18px;
    border-left: 6px solid #c89f7a;
    box-shadow: 0px 6px 14px rgba(0,0,0,0.05);
    color: #7b5e4b !important;
}

/* TABLA */
.stDataFrame {
    background: #f7ecdf !important;
    border-radius: 20px;
    padding: 12px;
    border: 1px solid #ead8c7;
}

/* ENCABEZADOS */
thead tr th {
    background-color: #c8a27a !important;
    color: white !important;
    text-align:center !important;
}

/* FILAS */
tbody tr:nth-child(even) {
    background-color: #fffaf5 !important;
}

tbody tr:nth-child(odd) {
    background-color: #f8ede3 !important;
}

/* TEXTO TABLA */
tbody td {
    color: #7b5e4b !important;
    font-weight: 600 !important;
    text-align:center !important;
}

/* FRASE */
.frase-yoga {
    text-align:center;
    margin-top:35px;
    margin-bottom:35px;
    font-size:34px;
    font-weight:700;
    color:#8b6f5a;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# DATOS ACTUALES
# -------------------------------
ultima_fila = df.iloc[-1]

# COLOR DINÁMICO
if "tenue" in ultima_fila["intensidad_luz"]:
    color_luz = "#f3ddd4"

elif "intensa" in ultima_fila["intensidad_luz"]:
    color_luz = "#f6e8b1"

elif "ideal" in ultima_fila["intensidad_luz"]:
    color_luz = "#dcebd7"

else:
    color_luz = "#dce6f2"

# -------------------------------
# DASHBOARD
# -------------------------------
col1, col2 = st.columns([1.2, 1])

# -------------------------------
# PANEL IZQUIERDO
# -------------------------------
with col1:

    st.markdown(
        """
        <div class="main-card">

            <img
            src="https://cdn-icons-png.flaticon.com/512/2647/2647625.png"
            width="240">

            <h2 style="
                color:#8b6f5a;
                margin-top:20px;
                font-size:34px;
                font-weight:700;
            ">
            Wellness Environment
            </h2>

            <p style="
                color:#9c7e67;
                font-size:20px;
                margin-top:10px;
                line-height:1.6;
            ">
            Ambiente inteligente diseñado para equilibrio,
            relajación y bienestar corporal.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# PANEL DERECHO
# -------------------------------
with col2:

    # HUMEDAD
    st.markdown(
        f"""
        <div class="info-card">

            <img
            src="https://cdn-icons-png.flaticon.com/512/728/728093.png"
            width="75">

            <h3 style="
                color:#8b6f5a;
                margin-top:10px;
                font-size:24px;
            ">
            Humedad
            </h3>

            <div style="
                font-size:38px;
                font-weight:700;
                color:#6f5442;
                margin-top:10px;
            ">
            {ultima_fila['humidity']:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # TEMPERATURA
    st.markdown(
        f"""
        <div class="info-card">

            <img
            src="https://cdn-icons-png.flaticon.com/512/4814/4814268.png"
            width="75">

            <h3 style="
                color:#8b6f5a;
                margin-top:10px;
                font-size:24px;
            ">
            Temperatura
            </h3>

            <div style="
                font-size:38px;
                font-weight:700;
                color:#6f5442;
                margin-top:10px;
            ">
            {ultima_fila['temperature']:.2f}°C
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # LUZ
    st.markdown(
        f"""
        <div style="
            background:{color_luz};
            border-radius:26px;
            padding:24px;
            margin-bottom:20px;
            text-align:center;
            box-shadow:0px 8px 16px rgba(0,0,0,0.05);
        ">

            <img
            src="https://cdn-icons-png.flaticon.com/512/3103/3103446.png"
            width="75">

            <h3 style="
                color:#8b6f5a;
                margin-top:10px;
                font-size:24px;
            ">
            Luz Inteligente
            </h3>

            <div style="
                font-size:20px;
                font-weight:700;
                color:#6f5442;
                margin-top:12px;
            ">
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

            🌡️ <b>Temperatura:</b>
            {row['temperature']:.2f} °C <br>

            💧 <b>Humedad:</b>
            {row['humidity']:.2f} % <br>

            💡 <b>Luz:</b>
            {row['intensidad_luz']}

        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# TABLA
# -------------------------------
st.subheader("📋 Registro del Ambiente")

st.dataframe(
    df,
    use_container_width=True
)

# -------------------------------
# GRAFICA PEQUEÑA
# -------------------------------
st.subheader("📈 Tendencia del Ambiente")

col_g1, col_g2, col_g3 = st.columns([1.5, 2, 1.5])

with col_g2:

    fig, ax = plt.subplots(
        figsize=(3.2, 1.8)
    )

    fig.patch.set_facecolor('#faf7f2')
    ax.set_facecolor('#fffaf6')

    ax.plot(
        df["_time"],
        df["temperature"],
        linewidth=1.8,
        marker='o',
        color="#f29b77",
        label="Temperatura"
    )

    ax.plot(
        df["_time"],
        df["humidity"],
        linewidth=1.8,
        marker='o',
        color="#8bb9d9",
        label="Humedad"
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.grid(alpha=0.10)

    ax.tick_params(
        axis='x',
        labelsize=5,
        colors="#8b6f5a"
    )

    ax.tick_params(
        axis='y',
        labelsize=5,
        colors="#8b6f5a"
    )

    ax.legend(fontsize=5)

    st.pyplot(fig)
