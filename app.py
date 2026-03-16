import streamlit as st
import pandas as pd

st.set_page_config(page_title="Primax - Control Maestro", layout="wide")

# 1. BASE DE DATOS DE USUARIOS
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. INICIALIZACIÓN DE ESTADOS
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'])

# Listas de configuración
PLANTAS = ['Conchan', 'Callao', 'Valero', 'Pampilla']
PRODUCTOS = ['Diesel', 'Regular', 'Premium']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
VENDEDORES = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']

# Inicializar Cuotas si no existen
if 'cuota_general' not in st.session_state:
    st.session_state.cuota_general = pd.DataFrame(0, index=['TOTAL GENERAL'], columns=PRODUCTOS)
if 'cuotas_especiales' not in st.session_state:
    st.session_state.cuotas_especiales = pd.DataFrame(0, index=ESPECIALES_ZONAS, columns=PRODUCTOS)
if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0, index=VENDEDORES, columns=PRODUCTOS)

# 3. LOGIN
if not st.session_state.autenticado:
    st.sidebar.title("🔐 Acceso Primax")
    u = st.sidebar.text_input("Usuario")
    p = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if USUARIOS.get(u) == p:
            st.session_state.autenticado = True
            st.session_state.user = u
            st.rerun()
    st.stop()

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# 4. PANEL DE ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("🎮 Panel Maestro de Distribución")
    
    # --- SECCIÓN 1: CUOTA GENERAL ---
    st.subheader("1. Cuota General de Planta (Techo Máximo)")
    st.session_state.cuota_general = st.data_editor(st.session_state.cuota_general, key="gen")
    
    # --- SECCIÓN 2: ASIGNACIÓN ESTRATÉGICA ---
    st.subheader("2. Asignación a Especiales y Zonas (Energigas, Petrosur, etc.)")
    st.session_state.cuotas_especiales = st.data_editor(st.session_state.cuotas_especiales, key="esp")
    
    # --- CÁLCULO DE LÓGICA DE CASCADA ---
    # Calculamos cuánto queda para los Regulares
    total_diesel = st.session_state.cuota_general.at['TOTAL GENERAL', 'Diesel']
    reservado_diesel = st.session_state.cuotas_especiales['Diesel'].sum()
    disponible_regulares_diesel = total_diesel - reservado_diesel
    
    total_reg = st.session_state.cuota_general.at['TOTAL GENERAL', 'Regular']
    reservado_reg = st.session_state.cuotas_especiales['Regular'].sum()
    disponible_regulares_reg = total_reg - reservado_reg

    # --- MOSTRAR SALDOS DISPONIBLES ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        color = "green" if disponible_regulares_diesel >= 0 else "red"
        st.markdown(f"### Disponible para Regulares (Diesel): :{color}[{disponible_regulares_diesel:,} Gls]")
    with c2:
        color_r = "green" if disponible_regulares_reg >= 0 else "red"
        st.markdown(f"### Disponible para Regulares (Regular): :{color_r}[{disponible_regulares_reg:,} Gls]")
    
    # --- SECCIÓN 3: DISTRIBUCIÓN POR VENDEDOR ---
    st.subheader("3. Cuotas por Jefe de Zona (Regulares)")
    st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="vend")
    
    # Validación final
    asignado_vendedores = st.session_state.cuotas_vendedores['Diesel'].sum()
    if asignado_vendedores > disponible_regulares_diesel:
        st.error(f"⚠️ ¡Error de Distribución! Has asignado {asignado_vendedores - disponible_regulares_diesel:,} Gls de más en Diesel.")

    # --- SECCIÓN 4: TABLA DE PEDIDOS ---
    st.divider()
    st.subheader("📝 Registro Maestro de Pedidos")
    st.session_state.pedidos = st.data_editor(
        st.session_state.pedidos, 
        num_rows="dynamic",
        column_config={
            "Planta": st.column_config.SelectboxColumn(options=PLANTAS),
            "Asesor": st.column_config.SelectboxColumn(options=ESPECIALES_ZONAS + VENDEDORES),
            "Estado": st.column_config.SelectboxColumn(options=['EN COLA', 'FACTURADO', 'RECHAZADO'])
        },
        use_container_width=True
    )

# --- VISTAS OTROS ROLES (Simplificadas para brevedad) ---
else:
    st.title(f"Vista: {st.session_state.user.upper()}")
    st.write("Contenido de ingreso y validación activo.")
    st.dataframe(st.session_state.pedidos)
