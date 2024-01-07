import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from io import StringIO
from config import cargar_configuracion

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "numerosColectivos.csv"

def guardar_numero_colectivo(numero_colectivo):
    try:
        # Leer el archivo CSV desde S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
            df_numeros_colectivos = pd.read_csv(response['Body'])
        except s3.exceptions.NoSuchKey:
            df_numeros_colectivos = pd.DataFrame(columns=['NumeroColectivo'])

        # Agregar el nuevo número de colectivo al DataFrame
        df_numeros_colectivos = pd.concat([df_numeros_colectivos, pd.DataFrame({'NumeroColectivo': [numero_colectivo]})], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with st.spinner("Guardando el número de colectivo en S3..."):
            # Convertir a formato CSV
            csv_data = df_numeros_colectivos.to_csv(index=False)

            # Crear un objeto de BytesIO
            csv_buffer = StringIO(csv_data)

            # Cargar el archivo CSV en S3
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_filename)

        st.success("Número de colectivo guardado exitosamente en S3!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar el número de colectivo en S3: {e}")

def main():
    st.title("Agregar Número de Colectivo")

    # Ingreso del nuevo número de colectivo
    numero_colectivo = st.text_input("Ingrese el número de colectivo:")

    # Botón para guardar el número de colectivo
    if st.button("Guardar Número de Colectivo"):
        if numero_colectivo:
            guardar_numero_colectivo(numero_colectivo)
        else:
            st.warning("Por favor, ingrese un número de colectivo válido.")

if __name__ == "__main__":
    main()
