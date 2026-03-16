import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Primax Control", layout="wide")

# Credenciales
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# Listas Maestras
JEFES_ZONA = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']
ESPECIALES = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
TODOS = ESPECIALES + JEFES_ZONA
PRODUCTOS = ['Diesel', 'Regular', 'Premium']

# 2. INICIALIZAR SESIÓN (Evita errores de variables no encontradas)
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'])

if 'cuotas' not in st.session_state:
    st.session_state.cuotas = pd.DataFrame(0.0, index=TODOS, columns=PRODUCTOS)

if 'auth' not in st.session_state:
    st.session_state.auth = False

# 3. LOGIN SIMPLE
if not st.session_state.auth:
    st.sidebar.title("⛽ Acceso Primax")
    u = st.sidebar.text_input("Usuario")
    p = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if USUARIOS.get(u) == p:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
    st.stop()

# 4. PANEL ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("🎮 Panel Maestro")
    
    t1, t2, t3 = st.tabs(["⚙️ Cuotas y Pedidos", "📊 Dashboards", "🚛 Terminal"])

    with t1:
        st.subheader("1. Configurar Límites")
        st.session_state.cuotas = st.data_editor(st.session_state.cuotas, key="c_edit")
        
        st.divider()
        st.subheader("2. Registrar Pedidos")
        df_input = st.data_editor(st.session_state.pedidos, num_rows="dynamic", key="p_edit", use_container_width=True,
                                  column_config={"Asesor": st.column_config.SelectboxColumn(options=TODOS)})
        
        if st.button("💾 VALIDAR Y GUARDAR"):
            # Limpiar datos para evitar errores de suma
            df_clean = df_input.copy()
            for prod in PRODUCTOS:
                df_clean[prod] = pd.to_numeric(df_clean[prod]).fillna(0)
            
            error_msg = []
            for asesor in TODOS:
                for prod in PRODUCTOS:
                    limite = float(st.session_state.cuotas.loc[asesor, prod])
                    consumo = df_clean[df_clean['Asesor'] == asesor][prod].sum()
                    if consumo > limite:
                        error_msg.append(f"⚠️ {asesor}: Estás excediendo la cuota asignada en {prod}, por favor validar")
            
            if error_msg:
                for m in error_msg: st.error(m)
            else:
                st.session_state.pedidos = df_clean
                st.success("✅ ¡Guardado con éxito!")

    with t2:
        st.header("📈 Avance de Consumo")
        
        # Crear tabla de resumen para gráficos
        resumen = []
        for a in TODOS:
            cons = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == a]['Diesel'].sum()
            lim = st.session_state.cuotas.loc[a, 'Diesel']
            resumen.append({"Asesor": a, "Consumido": cons, "Disponible": max(0, lim - cons)})
        
        df_res = pd.DataFrame(resumen).set_index("Asesor")
        
        # Métricas rápidas
        c1, c2 = st.columns(2)
        c1.metric("Total Diesel Pedido", f"{df_res['Consumido'].sum():,.0f} Gls")
        c2.metric("Total Cuota Disponible", f"{df_res['Disponible'].sum():,.0f} Gls")

        # Gráfico de barras nativo (sin Plotly para evitar errores)
        st.subheader("Consumo de Diesel por Asesor")
        st.bar_chart(df_res[['Consumido', 'Disponible']])

    with t3:
        st.subheader("🚛 Lista para Planta")
        st.dataframe(st.session_state.pedidos)

# BOTÓN CERRAR SESIÓN
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()
