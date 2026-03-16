import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Primax - Control de Crisis", layout="wide")

# Simulación de Base de Datos de Usuarios
Usuarios = {
    "admin": "primax2024",
    "jefe_zona": "zona123",
    "terminal": "pisco01"
}

# 2. LOGIN EN LA BARRA LATERAL
st.sidebar.title("🔐 Acceso al Sistema")
user = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")

if password == Usuarios.get(user):
    st.sidebar.success(f"Conectado como: {user.upper()}")
    
    # --- BASE DE DATOS TEMPORAL (En la vida real esto vendría de un Excel/DB) ---
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Asesor', 'Cliente', 'Diesel', 'G-Regular', 'Obs_Terminal', 'Estado'])
    if 'cuotas' not in st.session_state:
        st.session_state.cuotas = {"Diesel": 241940, "G-Regular": 79490}

    # ---------------------------------------------------------
    # PERFIL 1: ADMINISTRADOR (Modifica Cuotas y Gestión Total)
    # ---------------------------------------------------------
    if user == "admin":
        st.header("⚙️ Panel de Control de Cuotas (Admin)")
        
        col1, col2 = st.columns(2)
        with col1:
            nueva_c_diesel = st.number_input("Configurar Bolsa Diesel Total", value=st.session_state.cuotas["Diesel"])
        with col2:
            nueva_c_reg = st.number_input("Configurar Bolsa G-Regular Total", value=st.session_state.cuotas["G-Regular"])
        
        if st.button("Actualizar Cuotas Maestras"):
            st.session_state.cuotas = {"Diesel": nueva_c_diesel, "G-Regular": nueva_c_reg}
            st.success("Cuotas actualizadas para toda la gerencia.")

        st.divider()
        st.subheader("Lista Global de Pedidos")
        st.write(st.session_state.pedidos)

    # ---------------------------------------------------------
    # PERFIL 2: JEFE DE ZONA (Ingreso de Pedidos)
    # ---------------------------------------------------------
    elif user == "jefe_zona":
        st.header("📝 Registro de Pedidos - Jefe de Zona")
        
        with st.form("form_pedido"):
            f_cliente = st.text_input("Nombre del Cliente")
            f_diesel = st.number_input("Diesel (Gls)", min_value=0)
            f_reg = st.number_input("G-Regular (Gls)", min_value=0)
            enviar = st.form_submit_button("Registrar Pedido")
            
            if enviar:
                nuevo_p = {
                    'Fecha': pd.Timestamp.now().strftime("%d-%m"),
                    'Asesor': 'JEFE_ZONA_1',
                    'Cliente': f_cliente,
                    'Diesel': f_diesel,
                    'G-Regular': f_reg,
                    'Obs_Terminal': '',
                    'Estado': 'PENDIENTE'
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.success("Pedido enviado al Terminal.")

    # ---------------------------------------------------------
    # PERFIL 3: TERMINAL (Validación y Observación)
    # ---------------------------------------------------------
    elif user == "terminal":
        st.header("🚛 Panel de Despacho (Terminal)")
        st.info("Solo edite la columna 'Obs_Terminal' para confirmar atención.")
        
        # El terminal solo puede editar la observación
        df_terminal = st.data_editor(
            st.session_state.pedidos,
            disabled=['Fecha', 'Asesor', 'Cliente', 'Diesel', 'G-Regular', 'Estado'],
            hide_index=True
        )
        
        if st.button("Confirmar Atención de Planta"):
            st.session_state.pedidos = df_terminal
            st.success("Registros de terminal actualizados.")

else:
    st.warning("Por favor, ingrese sus credenciales en la barra lateral.")
    st.info("Credenciales de prueba:\n- admin / primax2024\n- jefe_zona / zona123\n- terminal / pisco01")
