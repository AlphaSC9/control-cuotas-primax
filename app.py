import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Primax Control - Administrador", layout="wide")

# Credenciales
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. INICIALIZACIÓN DE DATOS
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_tipo = None

# Matriz de Cuotas por Planta
if 'cuotas_matriz' not in st.session_state:
    plantas = ['Conchan', 'Callao', 'Valero', 'Pampilla']
    productos = ['Diesel', 'Regular', 'Premium']
    st.session_state.cuotas_matriz = pd.DataFrame(0, index=plantas, columns=productos)

# NUEVA: Cuotas Clientes Especiales
if 'cuotas_especiales' not in st.session_state:
    clientes_esp = ['Energigas', 'Petrosur', 'Consorcio']
    productos = ['Diesel', 'Regular', 'Premium']
    st.session_state.cuotas_especiales = pd.DataFrame(0, index=clientes_esp, columns=productos)

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'
    ])

# 3. LOGIN (Barra Lateral)
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

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# 4. PANELES SEGÚN ROL
st.title(f"⛽ Panel de Control - {st.session_state.usuario_tipo.upper()}")

# --- VISTA ADMINISTRADOR ---
if st.session_state.usuario_tipo == "admin":
    tab1, tab2, tab3 = st.tabs(["📊 Cuotas Generales (Plantas)", "🏆 Clientes Especiales", "📝 Edición de Pedidos"])

    with tab1:
        st.header("Modificar Cuota General por Planta")
        st.session_state.cuotas_matriz = st.data_editor(st.session_state.cuotas_matriz, use_container_width=True)
        
    with tab2:
        st.header("Asignación de Cuotas: Clientes Especiales")
        st.info("Define aquí el límite exclusivo para los clientes de gran volumen.")
        # Tabla para Energigas, Petrosur y Consorcio
        st.session_state.cuotas_especiales = st.data_editor(
            st.session_state.cuotas_especiales,
            use_container_width=True
        )
        
        # Resumen de consumo de especiales
        st.subheader("Estado de Cuotas Especiales")
        for cliente in st.session_state.cuotas_especiales.index:
            consumido = st.session_state.pedidos[st.session_state.pedidos['Cliente'] == cliente]['Diesel'].sum()
            total = st.session_state.cuotas_especiales.loc[cliente, 'Diesel']
            if total > 0:
                st.write(f"**{cliente} (Diesel):** {consumido:,} / {total:,} Gls")
                st.progress(min(consumido/total, 1.0))

    with tab3:
        st.header("Control Maestro de Pedidos")
        df_edit_admin = st.data_editor(
            st.session_state.pedidos,
            num_rows="dynamic",
            column_config={
                "Planta": st.column_config.SelectboxColumn("Planta", options=['Conchan', 'Callao', 'Valero', 'Pampilla']),
                "Cliente": st.column_config.TextColumn("Cliente"),
                "Estado": st.column_config.SelectboxColumn("Estado", options=['EN COLA', 'FACTURADO', 'RECHAZADO', 'OBSERVADO']),
            },
            use_container_width=True, hide_index=True
        )
        if st.button("Guardar Cambios en Lista"):
            st.session_state.pedidos = df_edit_admin
            st.success("Lista actualizada.")

# --- VISTA JEFE DE ZONA ---
elif st.session_state.usuario_tipo == "jefe_zona":
    st.header("📝 Registrar Nuevo Pedido")
    with st.form("registro_jefe"):
        f_planta = st.selectbox("Seleccione Planta", ['Conchan', 'Callao', 'Valero', 'Pampilla'])
        # Sugerir Clientes Especiales o dejar escribir
        f_cliente = st.selectbox("Cliente", ['Energigas', 'Petrosur', 'Consorcio', 'Otro...'])
        if f_cliente == 'Otro...':
            f_cliente = st.text_input("Especifique Cliente")
            
        c1, c2, c3 = st.columns(3)
        f_d = c1.number_input("Diesel (Gls)", min_value=0)
        f_r = c2.number_input("Regular (Gls)", min_value=0)
        f_p = c3.number_input("Premium (Gls)", min_value=0)
        
        if st.form_submit_button("Enviar Pedido"):
            # Validar contra cuota especial si corresponde
            if f_cliente in st.session_state.cuotas_especiales.index:
                limite = st.session_state.cuotas_especiales.loc[f_cliente, 'Diesel']
                actual = st.session_state.pedidos[st.session_state.pedidos['Cliente'] == f_cliente]['Diesel'].sum()
                if (actual + f_d) > limite:
                    st.warning(f"⚠️ ¡Atención! {f_cliente} está superando su cuota asignada.")

            nuevo_p = pd.DataFrame([{
                'Fecha': pd.Timestamp.now().strftime("%d/%m %H:%M"),
                'Planta': f_planta, 'Asesor': 'Jefe Zona', 'Cliente': f_cliente,
                'Diesel': f_d, 'Regular': f_r, 'Premium': f_p,
                'Obs_Terminal': '', 'Estado': 'EN COLA'
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_p], ignore_index=True)
            st.success("Pedido registrado.")

# --- VISTA TERMINAL ---
elif st.session_state.usuario_tipo == "terminal":
    st.header("🚛 Validación de Despacho (Terminal)")
    df_term = st.data_editor(
        st.session_state.pedidos,
        disabled=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'],
        use_container_width=True, hide_index=True
    )
    if st.button("Guardar Observaciones"):
        st.session_state.pedidos = df_term
        st.success("Datos guardados.")
