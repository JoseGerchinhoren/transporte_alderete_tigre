import streamlit as st
import boto3
import pandas as pd
import io
from datetime import datetime
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para insertar una venta en la base de datos
def insertarRevisionFosa(producto, precio, metodo_pago, nombre_usuario):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'ventas.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Forzar el tipo de dato de la columna 'precio' a enteros
        ventas_df['precio'] = ventas_df['precio'].astype(int, errors='ignore')

        # Obtener el último idVenta
        ultimo_id = ventas_df['idVenta'].max()

        # Si no hay registros, asignar 1 como idVenta, de lo contrario, incrementar el último idVenta
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Obtener la fecha actual en Argentina
        fecha_actual_argentina = obtener_fecha_argentina()
        fecha_str = fecha_actual_argentina.strftime("%Y-%m-%d")

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idVenta': nuevo_id, 'fecha': fecha_str, 'productoVendido': producto, 'precio': precio, 'metodoPago': metodo_pago, 'nombreUsuario': nombre_usuario}

        # Convertir el diccionario a DataFrame y concatenarlo al DataFrame existente
        ventas_df = pd.concat([ventas_df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en S3
        with io.StringIO() as csv_buffer:
            ventas_df.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

        st.success("Venta registrada exitosamente")

    except Exception as e:
        st.error(f"Error al registrar la venta: {e}")

def revisionFosa(nombre_usuario):
    st.title("""Ingresar Nueva Revisión en Fosa \n * Complete los campos. \n* Presione 'Registrar Revisión' para guardar la información de la nueva revisión.""")

    # Campos para ingresar los datos de la revision
    coche = st.text_input("Coche:")
    

    # Botón para registrar la venta
    if st.button("Registrar Revision"):
        if producto and precio > 0 and metodo_pago:
            insertar_venta(producto, precio, metodo_pago, nombre_usuario)
        else:
            st.warning("Por favor, complete todos los campos.")

if __name__ == "__main__":
    revisionFosa()