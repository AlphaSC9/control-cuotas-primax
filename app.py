import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Primax Control", layout="wide")

# Base de datos de usuarios
USUARIOS = {
    "admin": "primax2024",
    "jefe_zona": "zona123",
    "terminal": "pisco01"
}

# Inicializar estados de sesión
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_tipo = None
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Asesor', 'Cliente', 'Diesel', 'G-Regular', 'Obs_Terminal', 'Estado'])
if 'cuotas' not in st.session_state:
    st.session_state.cuotas = {"Diesel": 241940, "G-Regular": 79490}

# 2. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Primax_logo.svg/1200px-Primax_logo.svg.png", width=150)
    st.sidebar.title("🔐 Login Primax")
    user_input = st.sidebar.text_input("Usuario")
    pass_input = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Ingresar al Sistema"):
        if USUARIOS.get(user_input) == pass_input:
            st.session_state.autenticado = True
            st.session_state.usuario_tipo = user_input
            st.rerun() # Reinicia la app para mostrar el contenido
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")
            
    st.warning("⚠️ Inicie sesión en la barra lateral para continuar.")
    st.stop() # Detiene la ejecución aquí si no está logueado

# 3. BOTÓN DE SALIR (Una vez logueado)
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario_tipo = None
    st.rerun()

# 4. CONTENIDO SEGÚN ROL
st.title(f"⛽ Panel {st.session_state.usuario_tipo.upper()}")

# --- VISTA ADMINISTRADOR ---
if st.session_state.usuario_tipo == "admin":
    st.header("⚙️ Gestión de Cuotas")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.cuotas["Diesel"] = st.number_input("Cuota Diesel", value=st.session_state.cuotas["Diesel"])
    with c2:
        st.session_state.cuotas["G-Regular"] = st.number_input("Cuota G-Regular", value=st.session_state.cuotas["G-Regular"])
    
    st.subheader("Control Global de Pedidos")
    st.dataframe(st.session_state.pedidos, use_container_width=True)

# --- VISTA JEFE DE ZONA ---
elif st.
