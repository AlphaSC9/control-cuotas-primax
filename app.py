import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Primax - Dashboard de Crisis", layout="wide")

# 1. CREDENCIALES Y LISTAS
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}
PLANTAS = ['Conchan', 'Callao', 'Valero', 'Pampilla']
JEFES_ZONA = ['CARLOS BALTA', 'JORGE LIZARRAGA', 'JC RODRIGUEZ', 'LIZZY VILLALON', 'FREDY LINARES', 'NATHALIE HERRERA', 'SEIDA COTRINA']
ESPECIALES_ZONAS = ['Energigas', 'Petrosur', 'Consorcio', 'MCP', 'Sur', 'Norte']
TODOS_LOS_ASESORES = ESPECIALES_ZONAS + JEFES_ZONA
PRODUCTOS = ['Diesel', 'Regular', 'Premium']

# 2. INICIALIZACIÓN DE DATOS
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['Fecha', 'Planta', 'Asesor', 'Cliente', 'Diesel', 'Regular', 'Premium', 'Estado'])
if 'cuotas_vendedores' not in st.session_state:
    st.session_state.cuotas_vendedores = pd.DataFrame(0.0, index=TODOS_LOS_ASESORES, columns=PRODUCTOS)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# 3. LOGIN
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

# 4. PANEL ADMINISTRADOR
if st.session_state.user == "admin":
    st.title("⛽ Gestión Integral de Combustible")
    
    tab1, tab2, tab3 = st.tabs(["⚙️ Configuración y Registro", "📈 Dashboards de Control", "🚛 Vista Terminal"])

    with tab1:
        st.subheader("Configurar Límites y Registrar Pedidos")
        st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="cuotas_edit")
        st.divider()
        df_temp = st.data_editor(st.session_state.pedidos, num_rows="dynamic", use_container_width=True, key="pedidos_edit",
                                 column_config={"Asesor": st.column_config.SelectboxColumn(options=TODOS_LOS_ASESORES, required=True)})
        
        if st.button("💾 Validar y Guardar Cambios"):
            df_temp[['Diesel', 'Regular', 'Premium']] = df_temp[['Diesel', 'Regular', 'Premium']].fillna(0).astype(float)
            errores = [a for a in TODOS_LOS_ASESORES if df_temp[df_temp['Asesor']==a]['Diesel'].sum() > st.session_state.cuotas_vendedores.loc[a, 'Diesel']]
            if errores:
                for a in errores: st.error(f"⚠️ {a}: Estás excediendo la cuota asignada, por favor validar")
            else:
                st.session_state.pedidos = df_temp
                st.success("✅ Cambios guardados.")

    with tab2:
        st.header("📊 Avance de Cuotas en Tiempo Real")
        
        # --- CÁLCULOS PARA EL DASHBOARD ---
        df_resumen = []
        for a in TODOS_LOS_ASESORES:
            utilizado = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == a]['Diesel'].sum()
            maximo = st.session_state.cuotas_vendedores.loc[a, 'Diesel']
            disponible = maximo - utilizado
            df_resumen.append({"Asesor": a, "Utilizado": utilizado, "Máximo": maximo, "Disponible": disponible})
        
        df_dash = pd.DataFrame(df_resumen)

        # MÉTRICAS GENERALES
        c1, c2, c3 = st.columns(3)
        total_u = df_dash['Utilizado'].sum()
        total_m = df_dash['Máximo'].sum()
        c1.metric("Total Diesel Utilizado", f"{total_u:,.0f} Gls")
        c2.metric("Total Cuota Asignada", f"{total_m:,.0f} Gls")
        c3.metric("Saldo Global", f"{total_m - total_u:,.0f} Gls", delta_color="normal")

        st.divider()

        # GRÁFICO 1: COMPARATIVA POR JEFE DE ZONA
        st.subheader("⛽ Utilizado vs Cuota Máxima por Asesor (Diesel)")
        fig = px.bar(df_dash, x="Asesor", y=["Utilizado", "Disponible"], 
                     title="Distribución de Consumo",
                     color_discrete_map={"Utilizado": "#EF553B", "Disponible": "#00CC96"},
                     barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

        # GRÁFICO 2: AVANCE GENERAL (PIE CHART)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📈 Avance de Consumo General")
            fig_pie = px.pie(values=[total_u, total_m - total_u], names=['Consumido', 'Disponible'],
                             color_discrete_sequence=['#EF553B', '#00CC96'], hole=0.4)
            st.plotly_chart(fig_pie)
        
        with col_b:
            st.subheader("📋 Tabla de Cumplimiento")
            df_dash['% Avance'] = (df_dash['Utilizado'] / df_dash['Máximo'] * 100).fillna(0)
            st.dataframe(df_dash[['Asesor', 'Utilizado', 'Máximo', '% Avance']].style.format({"% Avance": "{:.1f}%"}))

    with tab3:
        st.header("🚛 Validación Terminal Pisco")
        st.dataframe(st.session_state.pedidos)

else:
    st.title("Vista Consulta")
    st.dataframe(st.session_state.pedidos)
