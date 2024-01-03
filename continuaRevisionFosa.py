import streamlit as st
import pandas as pd
from datetime import datetime
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "revisiones.csv"

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

def guardar_revision_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            df_total = pd.DataFrame(columns=['idRevision', 'coche', 'fechaHoraInicial', 'fechaHoraFinal', 'usuario', 'estadoRevision', 'posicionGuardada'])

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        id_revision = len(df_total)

        # Crear un diccionario con la información de la revisión
        nueva_revision = {'idRevision': id_revision,
                          'coche': data['coche'],
                          'fechaHoraInicial': data['fechaHoraInicial'],
                          'fechaHoraFinal': data['fechaHoraFinal'],
                          'usuario': data['usuario'],
                          'estadoRevision': data['estadoRevision'],
                          'posicionGuardada': data['posicionGuardada']}

        for punto, (estado, repuesto, cantidad) in data['datos'].items():
            nueva_revision[f'estado_{punto}'] = estado
            nueva_revision[f'repuestos_{punto}'] = repuesto
            nueva_revision[f'cantidad_{punto}'] = cantidad

        # Convertir el diccionario en un DataFrame
        nueva_df = pd.DataFrame([nueva_revision])

        # Concatenar el nuevo DataFrame con el existente
        df_total = pd.concat([df_total, nueva_df], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        st.success("Información guardada exitosamente en S3!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información en S3: {e}")

def guardar_revision(coche, fecha_hora_inicial, fecha_hora_final, usuario, estadoRevision, posicion_guardada, datos):
    try:
        # Crear un diccionario con la información de la revisión
        data = {'coche': coche,
                'fechaHoraInicial': fecha_hora_inicial.strftime('%Y-%m-%d %H:%M:%S'),
                'fechaHoraFinal': fecha_hora_final.strftime('%Y-%m-%d %H:%M:%S'),
                'usuario': usuario,
                'estadoRevision': estadoRevision,
                'posicionGuardada': posicion_guardada,
                'datos': datos}

        # Guardar la revisión en S3
        guardar_revision_en_s3(data, csv_filename)

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

def main():
    # Resto del código...

    # Loop a través de las posiciones
    for nombre_posicion, puntos_inspeccion in posiciones.items():
        st.header(nombre_posicion)

        # Obtener el número de la posición para la columna posicionGuardada
        posicion_guardada = int(nombre_posicion.split()[1])

        # Loop a través de los puntos de inspección
        for nombre_punto in puntos_inspeccion:
            opciones_estado = ['Bueno', 'Regular', 'Malo']
            estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado)
            datos_revision[nombre_punto] = (estado, repuesto, cantidad)

        if st.button(f"Guardar Revisión hasta {nombre_posicion}"):
            # Obtener la fecha y hora final de la revisión
            fecha_hora_final = datetime.now()
            # Guardar la información en el archivo CSV
            guardar_revision(coche, st.session_state.fecha_hora_inicial, fecha_hora_final, usuario, estadoRevision, posicion_guardada, datos_revision)
            st.success(f"Revisión guardada a las {fecha_hora_final.strftime('%Y-%m-%d %H:%M:%S')} para el coche {coche}")

    # Resto del código...

if __name__ == "__main__":
    main()
