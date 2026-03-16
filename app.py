import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Primax - Control de Cuotas", layout="wide")
st.title("⛽ Sistema de Gestión de Cuotas - White Pumpers")

# 2. BASE DE DATOS INICIAL (Simulando tu Excel)
if 'df_pedidos' not in st.session_state:
    data = {
        'Fecha': ['16-Mar', '16-Mar', '16-Mar', '16-Mar'],
        'Asesor': ['LIZZY VILLALON', 'CARLOS BALTA', 'ESPECIALES', 'SUR'],
        'Cliente': ['NICANOR', 'SHALOM', 'ENERGIGAS S.A.C.', 'SUR'],
        'Diesel': [1000, 2000, 6000, 7000],
        'G-Regular': [1000, 2000, 3000, 0],
        'Status': ['PENDIENTE', 'PENDIENTE', 'PENDIENTE / ESPECIALES', 'POR CONFIRMAR']
    }
    st.session_state.df_pedidos = pd.DataFrame(data)

# 3. DEFINICIÓN DE CUOTAS MÁXIMAS (La "Bolsa Valero")
BOLSA_DIESEL = 241940
BOLSA_REGULAR = 79490

# 4. CÁLCULO DE CONSUMO EN TIEMPO REAL
consumo_diesel = st.session_state.df_pedidos['Diesel'].sum()
consumo_reg = st.session_state.df_pedidos['G-Regular'].sum()

# 5. HEADER VISUAL (Semáforos de Planta)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bolsa DIESEL", f"{BOLSA_DIESEL - consumo_diesel:,} Gls", "Disponible")
    st.progress(min(consumo_diesel / BOLSA_DIESEL, 1.0))
with col2:
    st.metric("Bolsa G-REGULAR", f"{BOLSA_REGULAR - consumo_reg:,} Gls", "Disponible")
    st.progress(min(consumo_reg / BOLSA_REGULAR, 1.0))
with col3:
    st.info("⚠️ **MODO CRISIS ACTIVO**: Control estricto de cuotas por planta.")

st.divider()

# 6. TABLA DINÁMICA EDITABLE (El corazón de la App)
st.subheader("📝 Registro de Pedidos Diario")
df_editable = st.data_editor(
    st.session_state.df_pedidos,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Estado",
            options=["FACTURADO", "PENDIENTE", "AUTORIZADO", "RECHAZADO"],
            required=True,
        ),
        "Diesel": st.column_config.NumberColumn("Diesel (Gls)", min_value=0),
        "G-Regular": st.column_config.NumberColumn("G-Regular (Gls)", min_value=0),
    },
    num_rows="dynamic"
)

# 7. BOTÓN DE CIERRE Y GUARDADO
if st.button("💾 Guardar y Validar Cuotas"):
    st.session_state.df_pedidos = df_editable
    # Lógica de validación
    if consumo_diesel > BOLSA_DIESEL:
        st.error(f"¡ALERTA! Se ha superado la cuota de DIESEL por {consumo_diesel - BOLSA_DIESEL} galones.")
    else:
        st.success("Sincronización exitosa. Pedidos validados bajo cuota.")

# 8. PANEL DE AUDITORÍA PARA GERENCIA
with st.expander("🔍 Ver Resumen de Auditoría"):
    resumen = st.session_state.df_pedidos.groupby('Asesor').sum(numeric_only=True)
    st.table(resumen)
