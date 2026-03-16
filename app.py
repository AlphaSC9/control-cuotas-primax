import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Primax Control Maestro", layout="wide")

# Credenciales
USUARIOS = {"admin": "primax2024", "jefe_zona": "zona123", "terminal": "pisco01"}

# Listas Maestras
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
    st.title("⛽ Sistema de Control de Cuotas")
    
    tab1, tab2 = st.tabs(["📝 Gestión y Registro", "📊 Dashboards de Avance"])

    with tab1:
        st.subheader("Configuración de Cuotas y Pedidos")
        # Editor de Cuotas
        st.session_state.cuotas_vendedores = st.data_editor(st.session_state.cuotas_vendedores, key="edit_cuotas_v3")
        
        st.divider()
        
        # Editor de Pedidos
        df_temp = st.data_editor(
            st.session_state.pedidos,
            num_rows="dynamic",
            column_config={
                "Asesor": st.column_config.SelectboxColumn("Asesor", options=TODOS_LOS_ASESORES, required=True),
                "Planta": st.column_config.SelectboxColumn("Planta", options=PLANTAS)
            },
            use_container_width=True,
            key="edit_pedidos_v3"
        )
        
        if st.button("💾 Validar y Guardar"):
            # Limpieza y validación
            df_temp[['Diesel', 'Regular', 'Premium']] = df_temp[['Diesel', 'Regular', 'Premium']].fillna(0).astype(float)
            errores = []
            for asesor in TODOS_LOS_ASESORES:
                limite = float(st.session_state.cuotas_vendedores.loc[asesor, 'Diesel'])
                consumo = df_temp[df_temp['Asesor'] == asesor]['Diesel'].sum()
                if consumo > limite:
                    errores.append(asesor)
            
            if errores:
                for a in errores:
                    st.error(f"⚠️ {a}: Estás excediendo la cuota asignada, por favor validar")
            else:
                st.session_state.pedidos = df_temp
                st.success("✅ Datos guardados correctamente.")

    with tab2:
        st.header("📈 Visualización de Consumo")
        
        # Preparar datos para gráficos
        datos_grafico = []
        for a in TODOS_LOS_ASESORES:
            utilizado = st.session_state.pedidos[st.session_state.pedidos['Asesor'] == a]['Diesel'].sum()
            cuota = st.session_state.cuotas_vendedores.loc[a, 'Diesel']
            datos_grafico.append({"Asesor": a, "Estado": "Consumido", "Cantidad": utilizado})
            datos_grafico.append({"Asesor": a, "Estado": "Disponible", "Cantidad": max(0, cuota - utilizado)})
        
        df_plot = pd.DataFrame(datos_grafico)

        # Gráfico de Barras
        fig = px.bar(df_plot, x="Asesor", y="Cantidad", color="Estado", 
                     title="Consumo de Diesel por Jefe de Zona / Especiales",
                     color_discrete_map={"Consumido": "#FF4B4B", "Disponible": "#00CC96"},
                     barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla resumen
        st.subheader("Resumen de Cumplimiento")
        resumen_final = pd.DataFrame({
            "Cuota Total": st.session_state.cuotas_vendedores['Diesel'],
            "Consumido": [st.session_state.pedidos[st.session_state.pedidos['Asesor']==a]['Diesel'].sum() for a in TODOS_LOS_ASESORES]
        })
        resumen_final['% Avance'] = (resumen_final['Consumido'] / resumen_final['Cuota Total'] * 100).fillna(0)
        st.dataframe(resumen_final.style.format("{:.1f}%", subset=["% Avance"]))

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
