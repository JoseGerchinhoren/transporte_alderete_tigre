import streamlit as st
from datetime import datetime
import pandas as pd

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

def guardar_revision(coche, fecha_hora_inicial, fecha_hora_final, datos):
    # Cargar el archivo CSV existente o crear uno nuevo si no existe
    try:
        df = pd.read_csv('revisiones.csv')
    except FileNotFoundError:
        columnas = ['idRevision', 'coche', 'fechaHoraInicial', 'fechaHoraFinal']
        for punto in datos:
            columnas.extend([f'estado_{punto}', f'repuestos_{punto}', f'cantidad_{punto}'])
        df = pd.DataFrame(columns=columnas)

    # Obtener el ID de la revisión (longitud actual del DataFrame)
    id_revision = len(df)

    # Crear un diccionario con la información de la revisión
    nueva_revision = {'idRevision': id_revision,
                      'coche': coche,
                      'fechaHoraInicial': fecha_hora_inicial.strftime('%Y-%m-%d %H:%M'),
                      'fechaHoraFinal': fecha_hora_final.strftime('%Y-%m-%d %H:%M')}

    for punto, (estado, repuesto, cantidad) in datos.items():
        nueva_revision[f'estado_{punto}'] = estado
        nueva_revision[f'repuestos_{punto}'] = repuesto
        nueva_revision[f'cantidad_{punto}'] = cantidad

    # Convertir el diccionario en un DataFrame
    nueva_df = pd.DataFrame([nueva_revision])

    # Concatenar el nuevo DataFrame con el existente
    df = pd.concat([df, nueva_df], ignore_index=True)

    # Guardar el DataFrame actualizado en el archivo CSV
    df.to_csv('revisiones.csv', index=False)

def main():
    # Configuración inicial
    st.title("Ingresar Nueva Revisión en Fosa")

    # Ingreso de Coche
    coche = st.text_input("Coche:")

    # Validar que se haya ingresado un nombre o número de coche
    if not coche:
        st.warning("Por favor, ingrese un nombre o número de coche antes de continuar.")
        return

    # Inicializar la variable fecha_hora_inicial con un valor predeterminado
    if 'fecha_hora_inicial' not in st.session_state:
        st.session_state.fecha_hora_inicial = None

    # Botón para comenzar la revisión
    if st.button("Comenzar Revisión"):
        # Obtener la fecha y hora actual
        st.session_state.fecha_hora_inicial = datetime.now()
        st.subheader(f"Revisión iniciada a las {st.session_state.fecha_hora_inicial.strftime('%Y-%m-%d %H:%M')} para el coche {coche}")

    # Definición de posiciones
    posiciones = {
        "Bujes de barra delantera": [
            "Bujes de barra delantera",
            "Hojas de elásticos delanteros (fisuras)",
            "Bieletas de barra delantera (ajuste)",
            "Bujes de elásticos delanteros (desgaste)"
        ],
        "Extr, de barra larga y larga (juego)": [
            "Extr, de barra larga y larga (juego)",
            "Crucetas de columna de dirección",
            "Estado de caja derribadora (juego perdidas)"
        ],
        # Puedes agregar más posiciones aquí
    }

    # Almacenar los datos de la revisión en un diccionario
    datos_revision = {}

    # Loop a través de las posiciones
    for nombre_posicion, puntos_inspeccion in posiciones.items():
        st.header(nombre_posicion)

        # Loop a través de los puntos de inspección
        for nombre_punto in puntos_inspeccion:
            opciones_estado = ['Bueno', 'Regular', 'Malo']
            estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado)
            datos_revision[nombre_punto] = (estado, repuesto, cantidad)

    # Botón para guardar la revisión
    if st.button("Guardar Revisión"):
        # Verificar que la variable fecha_hora_inicial haya sido inicializada
        if st.session_state.fecha_hora_inicial:
            # Obtener la fecha y hora actual
            fecha_hora_guardado = datetime.now()
            st.success(f"Revisión guardada a las {fecha_hora_guardado.strftime('%Y-%m-%d %H:%M')} para el coche {coche}")

            # Guardar la información en el archivo CSV
            guardar_revision(coche, st.session_state.fecha_hora_inicial, fecha_hora_guardado, datos_revision)
        else:
            st.warning("Por favor, inicie una revisión antes de intentar guardarla.")

if __name__ == "__main__":
    main()
