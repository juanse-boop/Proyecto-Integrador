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
