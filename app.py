import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Primax Control Maestro", layout="wide")

# Credenciales de acceso
USUARIOS = {
    "admin": "primax2024",
    "jefe_zona": "zona123",
    "terminal": "pisco01"
}

# 2. INICIALIZACIÓN DE ESTADOS (Persistencia en sesión)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.user = None

# Listas maestras
PLANTAS = ['Conchan', 'Callao', 'Valero', 'Pampilla']
PRODUCTOS = ['Diesel', 'Regular', 'Premium']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
JEFES_ZONA = [
    'CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 
    'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA'
]

# Tablas de datos
if 'cuota_general' not in st.session_state:
    st.session_state.cuota_general = pd.DataFrame(0.0, index=['TOTAL GENERAL'], columns=PRODUCTOS)
if 'cuotas_especiales' not in st.session_state:
    st.session_state.cuotas_especiales = pd.DataFrame(0.0, index=ESPECIALES_ZONAS, columns=PRODUCTOS)
if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=JEFES_ZONA, columns=PRODUCTOS)
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'
    ])

# 3. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Primax_logo.svg/1200px-Primax_logo.svg.png", width=150)
    st.sidebar.title("🔐 Acceso Sistema")
    u = st.sidebar.text_input("Usuario")
    p = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if USUARIOS.get(u) == p:
            st.session_state.autenticado = True
            st.session_state.user = u
            st.rerun()
        else:
            st.sidebar.error("Datos incorrectos")
    st.stop()

# Botón Salir
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# 4. PANEL DE ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("🎮 Panel Maestro de Distribución y Cuotas")
    
    # --- SECCIÓN 1: CUOTA GENERAL ---
    st.subheader("1️⃣ Configurar Cuota General (Techo Total)")
    st.session_state.cuota_general = st.data_editor(st.session_state.cuota_general, key="ed_gen")
    
    st.divider()

    # --- SECCIÓN 2: CLIENTES ESPECIALES Y ZONAS ---
    st.subheader("2️⃣ Asignación Especiales / MCP / Zonas")
    st.session_state.cuotas_especiales = st.data_editor(st.session_state.cuotas_especiales, key="ed_esp", use_container_width=True)
    
    # LÓGICA DE CÁLCULO (CASCADA)
    # Diesel
    total_d = st.session_state.cuota_general.at['TOTAL GENERAL', 'Diesel']
    esp_d = st.session_state.cuotas_especiales['Diesel'].sum()
    disponible_vendedores_d = total_d - esp_d
    
    # Regular
    total_r = st.session_state.cuota_general.at['TOTAL GENERAL', 'Regular']
    esp_r = st.session_state.cuotas_especiales['Regular'].sum()
    disponible_vendedores_r = total_r - esp_r

    # Premium
    total_p = st.session_state.cuota_general.at['TOTAL GENERAL', 'Premium']
    esp_p = st.session_state.cuotas_especiales['Premium'].sum()
    disponible_vendedores_p = total_p - esp_p

    # --- MOSTRAR DISPONIBILIDAD PARA REGULARES ---
    st.info(f"💡 **Saldo para Clientes Regulares (Jefes de Zona):** Diesel: {disponible_vendedores_d:,.0f} | Regular: {disponible_vendedores_r:,.0f} | Premium: {disponible_vendedores_p:,.0f}")
    
    st.divider()

    # --- SECCIÓN 3: JEFES DE ZONA ---
    st.subheader("3️⃣ Cuotas por Jefe de Zona (Regulares)")
    st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="ed_vend", use_container_width=True)
    
    # Alerta de exceso
    if st.session_state.cuotas_vendedores['Diesel'].sum() > disponible_vendedores_d:
        st.error(f"🚨 EXCESO EN DIESEL: Has asignado {st.session_state.cuotas_vendedores['Diesel'].sum() - disponible_vendedores_d:,.0f} Gls de más.")

    st.divider()

    # --- SECCIÓN 4: TABLA DE PEDIDOS ---
    st.subheader("📝 Lista Maestra de Pedidos (Editable)")
    st.session_state.pedidos = st.data_editor(
        st.session_state.pedidos,
        num_rows="dynamic",
        column_config={
            "Planta": st.column_config.SelectboxColumn(options=PLANTAS),
            "Asesor": st.column_config.SelectboxColumn(options=ESPECIALES_ZONAS + JEFES_ZONA),
            "Estado": st.column_config.SelectboxColumn(options=['EN COLA', 'FACTURADO', 'OBSERVADO', 'RECHAZADO'])
        },
        use_container_width=True
    )

# --- PANEL JEFE DE ZONA ---
elif st.session_state.user == "jefe_zona":
    st.title("📝 Registro de Pedidos")
    with st.form("nuevo_pedido"):
        planta = st.selectbox("Planta", PLANTAS)
        cliente = st.text_input("Cliente")
        vendedor = st.selectbox("Tu Nombre (Jefe de Zona)", JEFES_ZONA)
        c1, c2, c3 = st.columns(3)
        d = c1.number_input("Diesel (Gls)", min_value=0.0)
        r = c2.number_input("Regular (Gls)", min_value=0.0)
        p = c3.number_input("Premium (Gls)", min_value=0.0)
        
        if st.form_submit_button("Registrar Pedido"):
            nuevo = pd.DataFrame([{
                'Fecha': pd.Timestamp.now().strftime("%d/%m %H:%M"),
                'Planta': planta, 'Asesor': vendedor, 'Cliente': cliente,
                'Diesel': d, 'Regular': r, 'Premium': p,
                'Obs_Terminal': '', 'Estado': 'EN COLA'
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo], ignore_index=True)
            st.success("Pedido enviado correctamente.")

# --- PANEL TERMINAL ---
elif st.session_state.user == "terminal":
    st.title("🚛 Validación Planta")
    df_t = st.data_editor(
        st.session_state.pedidos,
        disabled=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'],
        use_container_width=True
    )
    if st.button("Actualizar Observaciones"):
        st.session_state.pedidos = df_t
        st.success("Datos guardados.")
