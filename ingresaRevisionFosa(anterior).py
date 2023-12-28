import streamlit as st
import boto3
import pandas as pd
import io
from botocore.exceptions import NoCredentialsError
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "revisiones.csv"

def guardar_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        df_total = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Verificar si el DataFrame está vacío
        if df_total.empty:
            # Si está vacío, inicializamos la columna 'id' y las demás
            df_total = pd.DataFrame(columns=['idRevison', 'coche', 'inicio_revision', 'fin_revision'])

        # Agregar las columnas faltantes si no existen
        for col in data.keys():
            if col not in df_total.columns:
                df_total[col] = ''

        # Agrega un id único al nuevo dato
        data['idRevison'] = df_total['idRevison'].max() + 1 if not df_total.empty else 1

        # Crea un DataFrame con el nuevo dato
        new_data_df = pd.DataFrame([data])

        # Concatena el nuevo DataFrame con los datos existentes
        df_total = pd.concat([df_total, new_data_df], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        # Guardar localmente también
        df_total.to_csv(filename, index=False)

        st.success("Información guardada exitosamente en S3 y localmente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

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
    st.title("Ingresar Nueva Revisión en Fosa")

    # Verificar si estamos en la primera ejecución
    if 'data' not in st.session_state:
        st.session_state.data = {'coche': '', 'inicio_revision': '', 'fin_revision': ''}

    coche = st.text_input("Coche:", key="coche_input")
    if coche == "":
        st.warning("Por favor, ingresa el nombre del coche.")
        return

    if st.button("Comenzar Revisión"):
        fecha_hora_inicio = obtener_fecha_argentina()
        inicio_revision = fecha_hora_inicio.strftime("%Y-%m-%d %H:%M")

        # Almacenar en la sesión el inicio de la revisión y el coche
        st.session_state.data['inicio_revision'] = inicio_revision
        st.session_state.data['coche'] = coche

        st.subheader("Información de comienzo de revisión:")
        st.write(f"Coche: {st.session_state.data['coche']}")
        st.write(f"Inicio de revisión: {st.session_state.data['inicio_revision']}")
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

        for posicion, puntos_inspeccion_posicion in posiciones.items():
            st.header(posicion)
            for punto in puntos_inspeccion_posicion:
                opciones_estado = ['Bueno', 'Regular', 'Malo']
                estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(punto, opciones_estado)
                st.session_state.data[f'estado_{punto}'] = estado
                st.session_state.data[f'repuestos_{punto}'] = repuesto
                st.session_state.data[f'cantidad_{punto}'] = cantidad

        if st.button("Guardar Información"):
            # Guardar el tiempo de finalización cuando se presiona el botón "Guardar Información"
            fecha_hora_fin = obtener_fecha_argentina()
            fin_revision = fecha_hora_fin.strftime("%Y-%m-%d %H:%M")
            st.session_state.data['fin_revision'] = fin_revision
            guardar_en_s3(st.session_state.data, csv_filename)

if __name__ == "__main__":
    main()
