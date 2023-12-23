import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import pandas as pd
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "revisiones.csv"

def guardar_en_s3(data):
    user_name = st.session_state.user_nombre_apellido

    try:
        # Descarga el archivo CSV desde el bucket de S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Carga los datos existentes desde el archivo CSV
        df_total = pd.read_csv(csv_filename) if st.session_state.get('s3_file_exists') else pd.DataFrame()

        # Obtiene el último idRevision si hay registros, o establece 0 si no hay registros
        ultimo_id = df_total['idRevision'].max() if not df_total.empty else 0

        # Agrega un idRevision único al nuevo dato
        data['idRevision'] = int(ultimo_id) + 1

        # Agrega el nombre del usuario al nuevo dato
        data['user_name'] = user_name

        # Crea un DataFrame con el nuevo dato
        df_nuevo = pd.DataFrame([data])

        # Concatena el DataFrame al DataFrame existente
        df_total = pd.concat([df_total, df_nuevo], ignore_index=True)

        # Guarda el DataFrame actualizado en el archivo CSV y sube el archivo a S3
        s3.upload_file(csv_filename, bucket_name, csv_filename)

        # Establece una bandera para indicar que el archivo en S3 ahora existe
        st.session_state.s3_file_exists = True

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')

def cargar_desde_s3():
    try:
        # Descarga el archivo CSV desde el bucket de S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Carga los datos desde el archivo CSV
        df = pd.read_csv(csv_filename)
        return df.to_dict()

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')
        return None

def page_info_general():
    st.title("Ingresar Nueva Revisión en Fosa")

    coche = st.text_input("Coche:")
    fecha = st.date_input("Fecha:")
    hora = st.time_input("Hora:")

    if st.button("Siguiente"):
        data = {
            'coche': coche,
            'fecha': fecha,
            'hora': hora
        }
        guardar_en_s3(data)
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
        data = {
            'estado_bujes': estado,
            'repuestos_bujes': repuesto,
            'cantidad_bujes': cantidad
        }
        guardar_en_s3(data)
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
        data = {
            'estado_direccion': estado,
            'repuestos_direccion': repuesto,
            'cantidad_direccion': cantidad
        }
        # Cambiamos la página a la siguiente (puedes ajustar el nombre según sea necesario)
        guardar_en_s3(data)
        st.session_state.page = 'posicion_3'
        st.rerun()

def main():
    # Inicializa las variables de sesión si no existen
    if 'info_general' not in st.session_state:
        st.session_state.info_general = {}
    if 'posicion_1' not in st.session_state:
        st.session_state.posicion_1 = {}
    if 'page' not in st.session_state:
        st.session_state.page = 'info_general'  # Inicializa 'page' aquí

    if 's3_file_exists' not in st.session_state:
        st.session_state.s3_file_exists = False

    if st.session_state.page == 'info_general':
        page_info_general()
    elif st.session_state.page == 'posicion_1':
        page_posicion_1()
    elif st.session_state.page == 'posicion_2':
        page_posicion_2()

if __name__ == "__main__":
    main()
