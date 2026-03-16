import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Primax Control - Administrador", layout="wide")

# Credenciales
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. INICIALIZACIÓN DE DATOS (Estado de Sesión)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_tipo = None

# Estructura de Cuotas por Planta y Producto
if 'cuotas_matriz' not in st.session_state:
    plantas = ['Conchan', 'Callao', 'Valero', 'Pampilla']
    productos = ['Diesel', 'Regular', 'Premium']
    # Creamos un DataFrame para manejar las cuotas
    st.session_state.cuotas_matriz = pd.DataFrame(
        0, index=plantas, columns=productos
    )

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'
    ])

# 3. LOGIN
if not st.session_state.autenticado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Primax_logo.svg/1200px-Primax_logo.svg.png", width=150)
    st.sidebar.title("🔐 Acceso Primax")
    user_input = st.sidebar.text_input("Usuario")
    pass_input = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Ingresar"):
        if USUARIOS.get(user_input) == pass_input:
            st.session_state.autenticado = True
            st.session_state.usuario_tipo = user_input
            st.rerun()
        else:
            st.sidebar.error("Credenciales incorrectas")
    st.stop()

# Botón Salir
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# 4. PANELES SEGÚN ROL
st.title(f"⛽ Panel de Control - {st.session_state.usuario_tipo.upper()}")

# --- VISTA ADMINISTRADOR ---
if st.session_state.usuario_tipo == "admin":
    tab1, tab2 = st.tabs(["📊 Gestión de Cuotas", "📝 Edición de Listas (Pedidos)"])

    with tab1:
        st.header("Modificar Cuotas por Planta y Producto")
        st.info("Haga doble clic en una celda para cambiar la cuota asignada.")
        
        # Tabla editable para las cuotas
        st.session_state.cuotas_matriz = st.data_editor(
            st.session_state.cuotas_matriz,
            use_container_width=True
        )
        
        # Resumen visual
        st.subheader("Resumen Global de Disponibilidad")
        col_d, col_r, col_p = st.columns(3)
        col_d.metric("Total Diesel", f"{st.session_state.cuotas_matriz['Diesel'].sum():,} Gls")
        col_r.metric("Total Regular", f"{st.session_state.cuotas_matriz['Regular'].sum():,} Gls")
        col_p.metric("Total Premium", f"{st.session_state.cuotas_matriz['Premium'].sum():,} Gls")

    with tab2:
        st.header("Control Maestro de Pedidos")
        st.write("Como administrador, puedes agregar, eliminar o modificar cualquier pedido aquí.")
        
        # Tabla de pedidos totalmente editable para el admin
        df_edit_admin = st.data_editor(
            st.session_state.pedidos,
            num_rows="dynamic", # Permite agregar filas (botón + abajo de la tabla)
            column_config={
                "Planta": st.column_config.SelectboxColumn("Planta", options=['Conchan', 'Callao', 'Valero', 'Pampilla']),
                "Estado": st.column_config.SelectboxColumn("Estado", options=['EN COLA', 'FACTURADO', 'RECHAZADO', 'OBSERVADO']),
            },
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Guardar Cambios en Lista de Pedidos"):
            st.session_state.pedidos = df_edit_admin
            st.success("Lista de pedidos actualizada correctamente.")

# --- VISTA JEFE DE ZONA ---
elif st.session_state.usuario_tipo == "jefe_zona":
    st.header("📝 Registrar Nuevo Pedido")
    with st.form("registro_jefe"):
        f_planta = st.selectbox("Seleccione Planta", ['Conchan', 'Callao', 'Valero', 'Pampilla'])
        f_cliente = st.text_input("Cliente")
        c1, c2, c3 = st.columns(3)
        f_d = c1.number_input("Diesel (Gls)", min_value=0)
        f_r = c2.number_input("Regular (Gls)", min_value=0)
        f_p = c3.number_input("Premium (Gls)", min_value=0)
        
        if st.form_submit_button("Enviar Pedido"):
            nuevo_p = pd.DataFrame([{
                'Fecha': pd.Timestamp.now().strftime("%d/%m %H:%M"),
                'Planta': f_planta,
                'Asesor': 'Jefe Zona',
                'Cliente': f_cliente,
                'Diesel': f_d, 'Regular': f_r, 'Premium': f_p,
                'Obs_Terminal': '', 'Estado': 'EN COLA'
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_p], ignore_index=True)
            st.success("Pedido enviado.")

# --- VISTA TERMINAL ---
elif st.session_state.usuario_tipo == "terminal":
    st.header("🚛 Validación de Despacho")
    df_term = st.data_editor(
        st.session_state.pedidos,
        disabled=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'],
        use_container_width=True,
        hide_index=True
    )
    if st.button("Guardar Observaciones"):
        st.session_state.pedidos = df_term
        st.success("Datos guardados.")
