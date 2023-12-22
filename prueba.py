import streamlit as st

def page_info_general():
    st.title("Ingresar Nueva Revisión en Fosa")

    with st.form(key='info_general_form'):
        coche = st.text_input("Coche:")
        fecha = st.date_input("Fecha:")
        hora = st.time_input("Hora:")

        next_button_clicked = st.form_submit_button("Siguiente")

        if next_button_clicked:
            st.session_state.info_general = {
                'coche': coche,
                'fecha': fecha,
                'hora': hora
            }
            st.session_state.page = 'posicion_1'
            st.rerun()

def generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado):
    st.subheader(nombre_punto)
    estado = st.selectbox(f"Estado de {nombre_punto}:", opciones_estado)
    repuesto = st.text_input(f"Repuestos a cambiar para {nombre_punto} (si es necesario):")
    cantidad = st.number_input(f"Cantidad de repuestos para {nombre_punto}:", min_value=0, value=0, step=1)
    
    return estado, repuesto, cantidad

def page_posicion_1():
    st.title("Posición 1 - Inspección parte baja tren delantero")

    puntos_inspeccion_posicion_1 = [
        "Bujes de barra delantera",
        "Hojas de elásticos delanteros (fisuras)",
        "Bieletas de barra delantera (ajuste)",
        "Bujes de elásticos delanteros (desgaste)"
    ]

    # Crear un formulario para la posición 1
    with st.form(key='posicion_1_form'):
        # Iterar sobre los puntos de inspección
        for punto in puntos_inspeccion_posicion_1:
            opciones_estado = ['Bueno', 'Malo']  # Puedes personalizar las opciones según sea necesario
            estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(punto, punto, opciones_estado)

        col1, col2 = st.columns(2)

        # Utilizamos col1.form_submit_button para evitar el error
        back_button_clicked = col1.form_submit_button("Atrás")
        next_button_clicked = col2.form_submit_button("Siguiente")

        if back_button_clicked:
            st.session_state.page = 'info_general'
            st.rerun()
        elif next_button_clicked:
            st.session_state.page = 'posicion_2'
            st.rerun()

def main():
    if 'info_general' not in st.session_state:
        st.session_state.info_general = {}
    if 'posicion_1' not in st.session_state:
        st.session_state.posicion_1 = {}
    if 'page' not in st.session_state:
        st.session_state.page = 'info_general'

    if st.session_state.page == 'info_general':
        page_info_general()
    elif st.session_state.page == 'posicion_1':
        page_posicion_1()

if __name__ == "__main__":
    main()
