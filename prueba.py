import streamlit as st

def page_info_general():
    st.title("Ingresar Nueva Revisión en Fosa")

    coche = st.text_input("Coche:")
    fecha = st.date_input("Fecha:")
    hora = st.time_input("Hora:")

    if st.button("Siguiente"):
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
    
    if estado in ['Regular',  'Malo']:
        repuesto = st.text_input(f"Repuestos a cambiar para {nombre_punto}:")
        cantidad = st.number_input(f"Cantidad de repuestos para {nombre_punto}:", min_value=0, value=0, step=1)
    else:
        repuesto = ""
        cantidad = 0

    return estado, repuesto, cantidad

def page_posicion_1():
    st.title("Posición 1 - Inspección parte baja tren delantero")

    puntos_inspeccion_posicion_1 = [
        "Bujes de barra delantera",
        "Hojas de elásticos delanteros (fisuras)",
        "Bieletas de barra delantera (ajuste)",
        "Bujes de elásticos delanteros (desgaste)"
    ]

    # Iterar sobre los puntos de inspección
    for punto in puntos_inspeccion_posicion_1:
        opciones_estado = ['Bueno', 'Regular', 'Malo']
        estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(punto, opciones_estado)

    col1, col2 = st.columns(2)

    # Utilizamos col1.button para evitar el error
    back_button_clicked = col1.button("Atrás")
    next_button_clicked = col2.button("Siguiente")

    if back_button_clicked:
        st.session_state.page = 'info_general'
        st.rerun()
    elif next_button_clicked:
        st.session_state.posicion_1 = {
            'estado_bujes': estado,
            'repuestos_bujes': repuesto,
            'cantidad_bujes': cantidad
        }
        st.session_state.page = 'posicion_2'
        st.rerun()

def page_posicion_2():
    st.title("Posición 2 - Dirección")

    puntos_inspeccion_posicion_2 = [
        "Extr, de barra larga y larga (juego)",
        "Crucetas de columna de dirección",
        "Estado de caja derribadora (juego perdidas)"
    ]

    # Iterar sobre los puntos de inspección de la Posición 2
    for punto in puntos_inspeccion_posicion_2:
        opciones_estado = ['Bueno', 'Regular', 'Malo']
        estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(punto, opciones_estado)

    col1, col2 = st.columns(2)

    # Utilizamos col1.button para evitar el error
    back_button_clicked = col1.button("Atrás")
    next_button_clicked = col2.button("Siguiente")

    if back_button_clicked:
        st.session_state.page = 'posicion_1'
        st.rerun()
    elif next_button_clicked:
        st.session_state.posicion_2 = {
            'estado_direccion': estado,
            'repuestos_direccion': repuesto,
            'cantidad_direccion': cantidad
        }
        # Cambiamos la página a la siguiente (puedes ajustar el nombre según sea necesario)
        st.session_state.page = 'posicion_3'
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
    elif st.session_state.page == 'posicion_2':
        page_posicion_2()

if __name__ == "__main__":
    main()
