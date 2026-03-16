import streamlit as st
import pandas as pd

st.set_page_config(page_title="Primax Control Maestro", layout="wide")

# 1. CREDENCIALES
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# 2. LISTAS MAESTRAS
PLANTAS = ['Conchan', 'Callao', 'Valero', 'Pampilla']
JEFES_ZONA = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
TODOS_LOS_ASESORES = ESPECIALES_ZONAS + JEFES_ZONA
PRODUCTOS = ['Diesel', 'Regular', 'Premium']

# 3. INICIALIZACIÓN DE DATOS
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'])

if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=TODOS_LOS_ASESORES, columns=PRODUCTOS)

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

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
    
    # --- SECCIÓN 1: DEFINIR CUOTAS ---
    st.subheader("⚙️ 1. Configuración de Límites (Cuotas)")
    # Forzamos que la tabla de cuotas siempre tenga números
    st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="cuotas_edit")
    
    st.divider()

    # --- SECCIÓN 2: REGISTRO DE PEDIDOS ---
    st.subheader("📝 2. Registro de Pedidos Actuales")
    
    # Cargamos los pedidos actuales para editar
    df_temp = st.data_editor(
        st.session_state.pedidos,
        num_rows="dynamic",
        column_config={
            "Asesor": st.column_config.SelectboxColumn("Asesor", options=TODOS_LOS_ASESORES, required=True),
            "Planta": st.column_config.SelectboxColumn("Planta", options=PLANTAS),
            "Diesel": st.column_config.NumberColumn(format="%d"),
            "Regular": st.column_config.NumberColumn(format="%d"),
            "Premium": st.column_config.NumberColumn(format="%d"),
            "Estado": st.column_config.SelectboxColumn("Estado", options=['EN COLA', 'FACTURADO', 'RECHAZADO'])
        },
        use_container_width=True,
        key="pedidos_edit"
    )

    # --- BOTÓN DE VALIDACIÓN AGRESIVA ---
    if st.button("💾 VALIDAR Y GUARDAR CAMBIOS"):
        # Aseguramos que los valores vacíos sean 0 y los tipos sean numéricos
        df_temp[['Diesel', 'Regular', 'Premium']] = df_temp[['Diesel', 'Regular', 'Premium']].fillna(0).astype(float)
        
        errores_encontrados = []
        
        for asesor in TODOS_LOS_ASESORES:
            # 1. Obtener límites definidos en la tabla superior
            lim_d = float(st.session_state.cuotas_vendedores.loc[asesor, 'Diesel'])
            lim_r = float(st.session_state.cuotas_vendedores.loc[asesor, 'Regular'])
            lim_p = float(st.session_state.cuotas_vendedores.loc[asesor, 'Premium'])
            
            # 2. Sumar lo que el usuario escribió en la tabla inferior
            suma_d = df_temp[df_temp['Asesor'] == asesor]['Diesel'].sum()
            suma_r = df_temp[df_temp['Asesor'] == asesor]['Regular'].sum()
            suma_p = df_temp[df_temp['Asesor'] == asesor]['Premium'].sum()
            
            # 3. Comparación estricta
            if suma_d > lim_d or suma_r > lim_r or suma_p > lim_p:
                errores_encontrados.append(asesor)
        
        if len(errores_encontrados) > 0:
            for asesor_con_error in errores_encontrados:
                st.error(f"⚠️ {asesor_con_error}: Estás excediendo la cuota asignada, por favor validar")
            st.warning("❌ No se guardaron los cambios. Corrija los valores excedentes.")
        else:
            st.session_state.pedidos = df_temp
            st.success("✅ ¡Perfecto! Cuotas validadas. Cambios guardados exitosamente.")

# --- VISTA OTROS ---
else:
    st.title("Panel de Consulta")
    st.dataframe(st.session_state.pedidos)
