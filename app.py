import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Primax Control Maestro", layout="wide")

# Credenciales
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. INICIALIZACIÓN DE ESTADOS
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'])

JEFES_ZONA = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
PRODUCTOS = ['Diesel', 'Regular', 'Premium']

if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=JEFES_ZONA, columns=PRODUCTOS)
if 'cuota_general' not in st.session_state:
    st.session_state.cuota_general = pd.DataFrame(0.0, index=['TOTAL GENERAL'], columns=PRODUCTOS)
if 'cuotas_especiales' not in st.session_state:
    st.session_state.cuotas_especiales = pd.DataFrame(0.0, index=ESPECIALES_ZONAS, columns=PRODUCTOS)

# 3. LOGIN
if not st.session_state.autenticado:
    st.sidebar.title("🔐 Acceso Sistema")
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

# 4. LÓGICA DE ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("🎮 Panel Maestro de Distribución")
    
    tab1, tab2 = st.tabs(["📊 Configuración de Cuotas", "📝 Lista de Pedidos"])
    
    with tab1:
        st.subheader("1. Techo Total General")
        st.session_state.cuota_general = st.data_editor(st.session_state.cuota_general)
        
        st.subheader("2. Cuotas Especiales / Zonas")
        st.session_state.cuotas_especiales = st.data_editor(st.session_state.cuotas_especiales)
        
        st.subheader("3. Cuotas Individuales Jefes de Zona")
        st.info("Define aquí el límite exacto para cada vendedor.")
        st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores)

    with tab2:
        st.session_state.pedidos = st.data_editor(st.session_state.pedidos, num_rows="dynamic", use_container_width=True)

# 5. LÓGICA DE JEFE DE ZONA (CON VALIDACIÓN DE BLOQUEO)
elif st.session_state.user == "jefe_zona":
    st.title("📝 Registro de Pedidos")
    
    with st.form("form_registro"):
        vendedor = st.selectbox("Seleccione su Nombre", JEFES_ZONA)
        planta = st.selectbox("Planta", ['Conchan', 'Callao', 'Valero', 'Pampilla'])
        cliente = st.text_input("Cliente")
        
        c1, c2, c3 = st.columns(3)
        d_p = c1.number_input("Diesel (Gls)", min_value=0.0)
        r_p = c2.number_input("Regular (Gls)", min_value=0.0)
        p_p = c3.number_input("Premium (Gls)", min_value=0.0)
        
        if st.form_submit_button("Validar y Enviar Pedido"):
            # --- CÁLCULO DE VALIDACIÓN ---
            # 1. Obtener la cuota asignada por el admin para este vendedor
            cuota_d = st.session_state.cuotas_vendedores.loc[vendedor, 'Diesel']
            cuota_r = st.session_state.cuotas_vendedores.loc[vendedor, 'Regular']
            cuota_p = st.session_state.cuotas_vendedores.loc[vendedor, 'Premium']
            
            # 2. Sumar lo que ya ha pedido hoy
            ya_pedido_d = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == vendedor]['Diesel'].sum()
            ya_pedido_r = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == vendedor]['Regular'].sum()
            ya_pedido_p = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == vendedor]['Premium'].sum()
            
            # 3. Verificar excesos
            exceso_d = (ya_pedido_d + d_p) > cuota_d
            exceso_r = (ya_pedido_r + r_p) > cuota_r
            exceso_p = (ya_pedido_p + p_p) > cuota_p
            
            if exceso_d or exceso_r or exceso_p:
                st.error(f"🚫 **PEDIDO RECHAZADO**: Estás superando tu cuota asignada.")
                if exceso_d: st.write(f"- Diesel: Tienes {cuota_d - ya_pedido_d:,.0f} Gls disponibles.")
                if exceso_r: st.write(f"- Regular: Tienes {cuota_r - ya_pedido_r:,.0f} Gls disponibles.")
                if exceso_p: st.write(f"- Premium: Tienes {cuota_p - ya_pedido_p:,.0f} Gls disponibles.")
            else:
                # Si todo está bien, se guarda
                nuevo = pd.DataFrame([{
                    'Fecha': pd.Timestamp.now().strftime("%d/%m %H:%M"),
                    'Planta': planta, 'Asesor': vendedor, 'Cliente': cliente,
                    'Diesel': d_p, 'Regular': r_p, 'Premium': p_p,
                    'Obs_Terminal': '', 'Estado': 'APROBADO'
                }])
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo], ignore_index=True)
                st.success(f"✅ Pedido de {vendedor} registrado exitosamente.")

# 6. VISTA TERMINAL
elif st.session_state.user == "terminal":
    st.title("🚛 Despacho")
    st.data_editor(st.session_state.pedidos, disabled=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'])
