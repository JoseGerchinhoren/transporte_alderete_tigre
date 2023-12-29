import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "revisiones.csv"

# Cargar el archivo CSV desde S3
def cargar_desde_s3():
    try:
        # Descargar el archivo CSV desde el bucket de S3
        s3.download_file(bucket_name, csv_filename, csv_filename)

        # Cargar los datos desde el archivo CSV
        df = pd.read_csv(csv_filename)
        return df

    except NoCredentialsError as e:
        st.error(f'Error de credenciales: {e}')
        return None

# Visualizar los registros en una tabla
def visualizar_registros(df):
    st.subheader('Registros de Revisiones')
    # Mostrar solo las columnas deseadas
    columns_to_display = ['idRevision', 'coche', 'fecha', 'hora', 'user_name']
    st.dataframe(df[columns_to_display].set_index('idRevision'))

# Mostrar detalles de una revisión específica
def mostrar_detalles_por_id(df, id_revision):
    st.subheader(f'Detalles de la revisión con idRevision: {id_revision}')

    # Filtrar el DataFrame por el idRevision especificado
    detalles = df[df['idRevision'] == id_revision]

    # Iterar sobre las posiciones de inspección
    for position in ['Posición 1', 'Posición 2', 'Posición 3', 'Otra posición según sea necesario']:
        st.title(position)

        # Mostrar detalles para cada posición
        if position == 'Posición 1':
            st.write(f"**Estado de Bujes de barra delantera:** {detalles['estado_bujes'].values[0]}")
            st.write(f"**Repuestos para Bujes de barra delantera:** {detalles['repuestos_bujes'].values[0]}")
            st.write(f"**Cantidad para Bujes de barra delantera:** {detalles['cantidad_bujes'].values[0]}")
            # Agregar más detalles según sea necesario para la Posición 1
        elif position == 'Posición 2':
            st.write(f"**Estado de Otra cosa para Posición 2:** {detalles['estado_otra_posicion2'].values[0]}")
            st.write(f"**Repuestos para Otra cosa para Posición 2:** {detalles['repuestos_otra_posicion2'].values[0]}")
            st.write(f"**Cantidad para Otra cosa para Posición 2:** {detalles['cantidad_otra_posicion2'].values[0]}")
            # Agregar más detalles según sea necesario para la Posición 2
        elif position == 'Posición 3':
            st.write(f"**Estado de Otra cosa para Posición 3:** {detalles['estado_otra_posicion3'].values[0]}")
            st.write(f"**Repuestos para Otra cosa para Posición 3:** {detalles['repuestos_otra_posicion3'].values[0]}")
            st.write(f"**Cantidad para Otra cosa para Posición 3:** {detalles['cantidad_otra_posicion3'].values[0]}")
            # Agregar más detalles según sea necesario para la Posición 3
        # Agregar más posiciones según sea necesario

def main():
    # Cargar datos desde S3
    df = cargar_desde_s3()

    if df is not None:
        # Visualizar registros en una tabla
        visualizar_registros(df)

        # Obtener el idRevision desde el usuario
        id_revision = st.text_input('Ingrese el idRevision para ver detalles:')

        # Mostrar detalles si se ingresó un idRevision válido
        if st.button('Mostrar detalles') and id_revision:
            mostrar_detalles_por_id(df, int(id_revision))

if __name__ == "__main__":
    main()
