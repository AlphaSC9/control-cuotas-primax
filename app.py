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
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Obs_Terminal', 'Estado'])
if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=JEFES_ZONA, columns=PRODUCTOS)

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
    st.title("🎮 Panel Administrador")
    
    # --- SECCIÓN CUOTAS ---
    st.subheader("⚙️ Configuración de Cuotas Máximas")
    st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="editor_cuotas")
    
    st.divider()

    # --- SECCIÓN PEDIDOS CON LISTA DESPLEGABLE ---
    st.subheader("📝 Lista Maestra de Pedidos")
    st.info("Para agregar un pedido, use la última fila. Seleccione el ASESOR de la lista desplegable.")
    
    df_editado = st.data_editor(
        st.session_state.pedidos,
        num_rows="dynamic",
        column_config={
            "Asesor": st.column_config.SelectboxColumn("Asesor", options=TODOS_LOS_ASESORES, required=True),
            "Planta": st.column_config.SelectboxColumn("Planta", options=PLANTAS),
            "Estado": st.column_config.SelectboxColumn("Estado", options=['EN COLA', 'FACTURADO', 'RECHAZADO'])
        },
        use_container_width=True,
        key="editor_pedidos"
    )

    # --- BOTÓN DE VALIDACIÓN Y GUARDADO ---
    if st.button("💾 Validar y Guardar Cambios"):
        errores = []
        # Revisar cada jefe de zona
        for jefe in JEFES_ZONA:
            cuota_max = st.session_state.cuotas_vendedores.loc[jefe, 'Diesel']
            total_pedido = df_editado[df_editado['Asesor'] == jefe]['Diesel'].sum()
            
            if total_pedido > cuota_max:
                errores.append(f"❌ {jefe}: Pedido total ({total_pedido:,}) supera cuota ({cuota_max:,})")
        
        if errores:
            for e in errores:
                st.error(e)
            st.warning("Los cambios NO se han guardado permanentemente debido a los excesos.")
        else:
            st.session_state.pedidos = df_editado
            st.success("✅ ¡Validación exitosa! Todos los pedidos están dentro de la cuota.")

# --- VISTA JEFE DE ZONA (PARA PRUEBAS) ---
elif st.session_state.user == "jefe_zona":
    st.title("Vista Jefe de Zona")
    st.write("Usted solo puede ver los pedidos actuales.")
    st.dataframe(st.session_state.pedidos)
