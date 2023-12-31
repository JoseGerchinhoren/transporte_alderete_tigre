import streamlit as st
import boto3
import io
import pandas as pd
from config import cargar_configuracion

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualizar_revisiones_en_fosa():
    st.title("Visualizar Revisiones en Fosa")

    # Cargar el archivo revisiones.csv desde S3
    s3_csv_key = 'revisiones.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    revisiones_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()))

    # Filtrar las columnas deseadas
    columnas_deseadas = ['idRevision', 'coche', 'fechaHoraInicial', 'fechaHoraFinal']

    revisiones_df_columnas_deseadas = revisiones_df[columnas_deseadas]

    # Ordenar el DataFrame por la columna 'idRevision' de forma descendente
    revisiones_df_columnas_deseadas = revisiones_df_columnas_deseadas.sort_values(by='idRevision', ascending=False)

    # Convertir la columna "idRevision" a tipo cadena y eliminar las comas
    revisiones_df_columnas_deseadas['idRevision'] = revisiones_df_columnas_deseadas['idRevision'].astype(str).str.replace(',', '')

    # Convertir la columna "idRevision" a tipo cadena y eliminar las comas
    revisiones_df['idRevision'] = revisiones_df['idRevision'].astype(str).str.replace(',', '')

    # Mostrar la tabla de revisiones en fosa
    st.dataframe(revisiones_df_columnas_deseadas)

    # Agregar un widget de búsqueda por idRevision
    id_revision_buscado = st.text_input("Buscar por idRevision:")
    
    if id_revision_buscado:
        # Filtrar el DataFrame por el idRevision ingresado
        filtro_id_revision = revisiones_df['idRevision'] == id_revision_buscado
        resultado_busqueda = revisiones_df[filtro_id_revision]

        # Mostrar los resultados de la búsqueda en formato de texto
        st.header("Resultado de la búsqueda:")

        for index, row in resultado_busqueda.iterrows():
            st.subheader(f"Id de Revision: {row['idRevision']}")
            st.subheader(f"Coche: {row['coche']}")
            st.subheader(f"Fecha Inicial: {row['fechaHoraInicial']}")
            st.subheader(f"Fecha Final: {row['fechaHoraFinal']}")

            # Obtener y mostrar la información adicional
            posiciones_columnas = [col for col in revisiones_df.columns if col.startswith('estado_')]
            for posicion_columna in posiciones_columnas:
                estado = row[posicion_columna]
                repuestos_columna = f'repuestos_{posicion_columna[7:]}'
                cantidad_columna = f'cantidad_{posicion_columna[7:]}'

                st.subheader(f"{posicion_columna[7:]}: {estado} ({row[repuestos_columna]}, {row[cantidad_columna]})")

if __name__ == "__main__":
    visualizar_revisiones_en_fosa()
