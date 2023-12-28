import streamlit as st

def generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado):
    st.subheader(nombre_punto)

    estado = st.selectbox(f"Estado de {nombre_punto}:", opciones_estado)

    if estado in ['Regular', 'Malo']:
        repuesto = st.text_input(f"Repuestos a cambiar para {nombre_punto}:")
        cantidad = st.number_input(f"Cantidad de repuestos para {nombre_punto}:", min_value=0, value=0, step=1)
    else:
        repuesto = ""
        cantidad = 0

    return estado, repuesto, cantidad

def main():
    # Configuración inicial
    st.title("Ingresar Nueva Revisión en Fosa")

    # Ingreso de Coche
    coche = st.text_input("Coche:")

    # Definición de posiciones
    posiciones = {
        "Posición 1, Inspección parte baja tren delantero": [
            "Bujes de barra delantera",
            "Hojas de elásticos delanteros (fisuras)",
            "Bieletas de barra delantera (ajuste)",
            "Bujes de elásticos delanteros (desgaste)"
        ],
        "Posición 2, Dirección": [
            "Extr, de barra larga y larga (juego)",
            "Crucetas de columna de dirección",
            "Estado de caja derribadora (juego perdidas)"
        ],
        # Puedes agregar más posiciones aquí
    }

    # Loop a través de las posiciones
    for nombre_posicion, puntos_inspeccion in posiciones.items():
        st.header(nombre_posicion)

        # Loop a través de los puntos de inspección
        for nombre_punto in puntos_inspeccion:
            opciones_estado = ['Bueno', 'Regular', 'Malo']
            estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado)

    # Botón para comenzar la revisión
    if st.button("Comenzar Revisión"):
        # Aquí puedes procesar la información recopilada
        st.success("Revisión completada con éxito!")

if __name__ == "__main__":
    main()
