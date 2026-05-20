# -------------------------------
# DASHBOARD PRINCIPAL
# -------------------------------
col1, col2 = st.columns([1.2, 1])

# -------------------------------
# PANEL IZQUIERDO
# -------------------------------
with col1:

    st.markdown(
        """
        <div style="
            background: rgba(255,255,255,0.35);
            backdrop-filter: blur(14px);
            border-radius: 32px;
            padding: 35px;
            text-align:center;
            box-shadow: 0px 10px 20px rgba(0,0,0,0.06);
            border:1px solid rgba(255,255,255,0.4);
        ">

            <img 
            src="https://cdn-icons-png.flaticon.com/512/2647/2647625.png"
            width="250">

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
        <div style="
            background: rgba(255,255,255,0.45);
            border-radius:26px;
            padding:24px;
            margin-bottom:20px;
            text-align:center;
            box-shadow:0px 8px 16px rgba(0,0,0,0.05);
        ">

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
        <div style="
            background: rgba(255,255,255,0.45);
            border-radius:26px;
            padding:24px;
            margin-bottom:20px;
            text-align:center;
            box-shadow:0px 8px 16px rgba(0,0,0,0.05);
        ">

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
