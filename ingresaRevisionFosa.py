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
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Carga los datos existentes desde el archivo CSV
        df_total = pd.read_csv(csv_filename) if st.session_state.get('s3_file_exists') else pd.DataFrame()

        # Obtiene el último idRevision si hay registros, o establece 0 si no hay registros
        ultimo_id = df_total['idRevision'].max() if not df_total.empty else 0

        # Agrega un idRevision único al nuevo dato
        data['idRevision'] = int(ultimo_id) + 1

        # Agrega el nombre del usuario al nuevo dato
        data['user_name'] = user_name

        # Almacena el idRevision generado en la variable de sesión
        st.session_state.last_id_revision = data['idRevision']

        # Actualiza el DataFrame total con los nuevos datos
        if not df_total.empty:
            for key, value in data.items():
                if key not in df_total.columns:
                    df_total[key] = None  # Agrega la columna si no existe
                df_total.at[df_total.index[-1], key] = value
        else:
            df_total = pd.DataFrame([data])

        # Reorganiza las columnas según el nuevo orden deseado
        column_order = ['idRevision', 'coche', 'fecha', 'hora', 'user_name']

        # Itera sobre las columnas relacionadas con los puntos de inspección y agréguelas al orden
        for col in df_total.columns:
            if col not in column_order:
                column_order.append(col)

        # Organiza todas las columnas
        df_total = df_total[column_order]

        # Guarda el DataFrame actualizado en el archivo CSV y sube el archivo a S3
        df_total.to_csv(csv_filename, index=False)
        s3.upload_file(csv_filename, bucket_name, csv_filename)

        # Establece una bandera para indicar que el archivo en S3 ahora existe
        st.session_state.s3_file_exists = True

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')

def eliminar_registro_csv():
    try:
        # Descarga el archivo CSV desde el bucket de S3
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Carga los datos existentes desde el archivo CSV
        df_total = pd.read_csv(csv_filename)

        # Elimina el registro con el idRevision correspondiente
        df_total = df_total[df_total['idRevision'] != st.session_state.last_id_revision]

        # Guarda el DataFrame actualizado en el archivo CSV y sube el archivo a S3
        df_total.to_csv(csv_filename, index=False)
        s3.upload_file(csv_filename, bucket_name, csv_filename)

        # Establece la bandera para indicar que el archivo en S3 ahora existe
        st.session_state.s3_file_exists = True

        # Elimina la variable de sesión que almacena el último idRevision
        del st.session_state.last_id_revision

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')

def cargar_desde_s3():
    try:
        # Descarga el archivo CSV desde el bucket de S3
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Carga los datos desde el archivo CSV
        df = pd.read_csv(csv_filename)
        return df.to_dict()

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')
        return None

def cancelar_revision():
    # Elimina el registro generado en el archivo CSV
    eliminar_registro_csv()
    # Reiniciar las variables de sesión
    st.session_state.info_general = {}
    st.session_state.page = 'info_general'
    st.success("Revisión cancelada exitosamente!")

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

def page_info_general():
    st.title("Ingresar Nueva Revisión en Fosa")

    coche = st.text_input("Coche:", key="coche_input")
    if coche == "":
        st.warning("Por favor, ingresa el nombre del coche.")
        return

    if st.button("Comenzar Revisión de Fosa"):
        fecha_hora_actual = obtener_fecha_argentina()
        fecha = fecha_hora_actual.strftime("%Y-%m-%d")
        hora = fecha_hora_actual.strftime("%H:%M")

        st.subheader("Información del Coche:")
        st.write(f"Coche: {coche}")
        st.write(f"Fecha: {fecha}")
        st.write(f"Hora: {hora}")
        st.write(f"Usuario: {st.session_state.user_nombre_apellido}")
        st.write("")

        data = {'coche': coche, 'fecha': fecha, 'hora': hora, 'user_name': st.session_state.user_nombre_apellido}
        guardar_en_s3(data)
        st.session_state.info_general = data  # Almacena los datos en la variable de sesión
        st.session_state.page = 'posiciones'
        st.rerun()

def page_posiciones():
    st.title("Inspección de Fosa")

    # Mostrar información del coche
    info_general = st.session_state.info_general
    if info_general:
        st.subheader("Información de comienzo de revision:")
        st.write(f"Coche: {info_general['coche']}")
        st.write(f"Fecha: {info_general['fecha']}")
        st.write(f"Hora: {info_general['hora']}")
        st.write(f"Usuario: {info_general['user_name']}")
        st.write("")

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

    # Iterar sobre las posiciones y sus puntos de inspección
    data = st.session_state.info_general.copy() if 'info_general' in st.session_state else {}
    for posicion, puntos_inspeccion_posicion in posiciones.items():
        st.subheader(posicion)
        for punto in puntos_inspeccion_posicion:
            opciones_estado = ['Bueno', 'Regular', 'Malo']
            estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(punto, opciones_estado)
            data[f'estado_{punto}'] = estado
            data[f'repuestos_{punto}'] = repuesto
            data[f'cantidad_{punto}'] = cantidad

    if st.button("Guardar Información"):
        guardar_en_s3(data)
        st.success("Información guardada exitosamente!")

    if st.button("Cancelar Revisión de Fosa"):
        cancelar_revision()

def main():
    # Inicializa las variables de sesión si no existen
    if 'info_general' not in st.session_state:
        st.session_state.info_general = {}
    if 'page' not in st.session_state:
        st.session_state.page = 'info_general'  # Inicializa 'page' aquí

    if 's3_file_exists' not in st.session_state:
        st.session_state.s3_file_exists = False

    if st.session_state.page == 'info_general':
        page_info_general()
    elif st.session_state.page == 'posiciones':
        page_posiciones()

if __name__ == "__main__":
    main()
