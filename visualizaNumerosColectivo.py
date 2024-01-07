import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from config import cargar_configuracion

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "numerosColectivos.csv"

def obtener_numeros_colectivos():
    try:
        # Leer el archivo CSV desde S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
            df_numeros_colectivos = pd.read_csv(response['Body'])
        except s3.exceptions.NoSuchKey:
            df_numeros_colectivos = pd.DataFrame(columns=['NumeroColectivo'])

        return df_numeros_colectivos

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")
        return None

def visualizar_numeros_colectivos():
    df_numeros_colectivos = obtener_numeros_colectivos()

    if df_numeros_colectivos is not None and not df_numeros_colectivos.empty:
        st.subheader("Números de Colectivo Registrados:")
        st.dataframe(df_numeros_colectivos)
    else:
        st.warning("No hay números de colectivo registrados.")

def main():
    st.title("Visualizar y Eliminar Números de Colectivo")

    # Visualizar números de colectivo
    visualizar_numeros_colectivos()

if __name__ == "__main__":
    main()
