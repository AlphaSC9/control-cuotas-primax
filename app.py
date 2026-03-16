import streamlit as st
import pandas as pd

st.set_page_config(page_title="Primax Control Maestro", layout="wide")

# 1. BASE DE DATOS DE USUARIOS
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. LISTAS MAESTRAS
PLANTAS = ['Conchan', 'Callao', 'Valero', 'Pampilla']
JEFES_ZONA = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
TODOS_LOS_ASESORES = ESPECIALES_ZONAS + JEFES_ZONA
PRODUCTOS = ['Diesel', 'Regular', 'Premium']

# 3. INICIALIZACIÓN DE DATOS
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'])
if 'cuotas_vendedores' not in st.session_state:
    # Inicializamos con ceros para evitar errores de referencia
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=TODOS_LOS_ASESORES, columns=PRODUCTOS)

# 4. LOGIN
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

# 5. PANEL ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("🎮 Panel Administrador - Control de Cuotas")
    
    # --- SECCIÓN CUOTAS ---
    st.subheader("⚙️ 1. Definir Cuotas Límites")
    st.info("Escriba aquí los límites permitidos para cada asesor/zona.")
    st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="ed_cuotas_v")
    
    st.divider()

    # --- SECCIÓN PEDIDOS ---
    st.subheader("📝 2. Registro de Pedidos")
    st.warning("Nota: Después de editar, debe hacer clic en el botón 'Validar y Guardar'.")
    
    # Capturamos la edición en una variable temporal
    df_input = st.data_editor(
        st.session_state.pedidos,
        num_rows="dynamic",
        column_config={
            "Asesor": st.column_config.SelectboxColumn("Asesor", options=TODOS_LOS_ASESORES, required=True),
            "Planta": st.column_config.SelectboxColumn("Planta", options=PLANTAS),
            "Estado": st.column_config.SelectboxColumn("Estado", options=['EN COLA', 'FACTURADO', 'RECHAZADO'])
        },
        use_container_width=True,
        key="ed_pedidos_v"
    )

    # --- BOTÓN DE VALIDACIÓN CRÍTICA ---
    if st.button("💾 Validar y Guardar Cambios"):
        hay_error = False
        
        # Revisamos cada asesor para ver si se pasó de su cuota
        for asesor in TODOS_LOS_ASESORES:
            # Cuotas definidas
            limite_d = st.session_state.cuotas_vendedores.loc[asesor, 'Diesel']
            limite_r = st.session_state.cuotas_vendedores.loc[asesor, 'Regular']
            limite_p = st.session_state.cuotas_vendedores.loc[asesor, 'Premium']
            
            # Suma de lo ingresado en la tabla
            suma_d = df_input[df_input['Asesor'] == asesor]['Diesel'].sum()
            suma_r = df_input[df_input['Asesor'] == asesor]['Regular'].sum()
            suma_p = df_input[df_input['Asesor'] == asesor]['Premium'].sum()
            
            # Validación
            if suma_d > limite_d or suma_r > limite_r or suma_p > limite_p:
                st.error(f"⚠️ {asesor}: Estás excediendo la cuota asignada, por favor validar")
                hay_error = True
        
        if not hay_error:
            st.session_state.pedidos = df_input
            st.success("✅ Datos guardados correctamente. Cuotas respetadas.")
        else:
            st.warning("🛑 No se guardaron los cambios. Corrija las cantidades en rojo.")

# --- VISTA OTROS ROLES ---
else:
    st.title(f"Vista {st.session_state.user.upper()}")
    st.dataframe(st.session_state.pedidos)
    if st.sidebar.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()
