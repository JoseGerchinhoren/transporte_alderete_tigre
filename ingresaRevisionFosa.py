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

# def revisionFosa(nombre_usuario):
#     st.title("""Ingresar Nueva Revisión en Fosa \n * Complete los campos. \n* Presione 'Registrar Revisión' para guardar la información de la nueva revisión.""")

#     # Campos para ingresar los datos de la revision
#     coche = st.text_input("Coche:")
#     fecha = st.text_input("Fecha:")
#     hora = st.text_input("Hora:")

#     opciones_estado = ["Bueno", "Regular", "Malo"]

#     st.header("Posición 1 - Inspección parte baja tren delantero")
#     st.subheader("Bujes de barra delantera")
#     estado_bujes_barra_delantera = st.selectbox("Estado de Bujes de barra delantera:", opciones_estado)
#     repuesto_bujes_barra_delantera = st.text_input("Repuestos a cambiar para Bujes de barra delantera (si es necesario):")
#     cantidad_bujes_barra_delantera = st.number_input("Cantidad:", min_value=0, value=0, step=1)
    

#     # # Botón para registrar la venta
#     # if st.button("Registrar Revision"):
#     #     if producto and precio > 0 and metodo_pago:
#     #         insertar_venta(producto, precio, metodo_pago, nombre_usuario)
#     #     else:
#     #         st.warning("Por favor, complete todos los campos.")

# if __name__ == "__main__":
#     revisionFosa()
        

def generar_interfaz_punto_inspeccion(nombre_posicion, nombre_punto, opciones_estado):
    st.subheader(nombre_punto)
    estado = st.selectbox(f"Estado de {nombre_punto}:", opciones_estado)
    repuesto = st.text_input(f"Repuestos a cambiar para {nombre_punto} (si es necesario):")
    cantidad = st.number_input(f"Cantidad de repuestos para {nombre_punto}:", min_value=0, value=0, step=1)
    
    return estado, repuesto, cantidad

def agregar_puntos_inspeccion(posicion, puntos_inspeccion, opciones_estado):
    st.header(f"{posicion}")
    for punto in puntos_inspeccion:
        generar_interfaz_punto_inspeccion(posicion, punto, opciones_estado)

def revisionFosa(nombre_usuario):
    opciones_estado = ["Bueno", "Regular", "Malo"]
    
    st.title("Ingresar Nueva Revisión en Fosa")
    st.write("Complete los campos y la tabla de inspección, luego presione 'Registrar Revisión' para guardar la información.")

    # Campos para ingresar los datos generales de la revisión
    coche = st.text_input("Coche:")
    fecha = st.text_input("Fecha:")
    hora = st.text_input("Hora:")

    # Definir los puntos de inspección de la posición 1
    puntos_inspeccion_posicion_1 = [
        "Bujes de barra delantera",
        "Hojas de elásticos delanteros (fisuras)",
        "Bieletas de barra delantera (ajuste)",
        "Bujes de elásticos delanteros (desgaste)"
    ]

    # Definir los puntos de inspección de la posición 2
    puntos_inspeccion_posicion_2 = [
        "Extr, de barra larga y larga (juego)",
        "Crucetas de columna de dirección",
        "Estado de caja derribadora (juego perdidas)"
    ]

    # Definir los puntos de inspección de la posición 3
    puntos_inspeccion_posicion_3 = [
        "Espesor de cintas de freno Delantero",
        "Indicar la medida actual de la cinta Delantera",
        "Indicar la medida próxima de la cinta Delantera",
        "Estado de la campana Delantera Izquierda",
        "Estado de la campana Delantera Derecha",
        "Estado de cajas reguladoras delantera izquierda (engrase / sujeción)",
        "Estado de cajas reguladoras delantera Derecha (engrase/ sujeción)",
        "Pulmón de freno Delantero Izquierdo (perdida)",
        "Pulmón de freno Delantero Derecho (perdida)",
        "Protector de chapa para cinta de freno Delantero Izquierdo",
        "Protector de chapa para cinta de freno Delantero Derecho"
    ]

    # Definir los puntos de inspección de la posición 4
    puntos_inspeccion_posicion_4 = [
        "Primer tramo estado",
        "Segundo tramo estado",
        "Tercer tramo estado"
    ]

    # Definir los puntos de inspección de la posición 5
    puntos_inspeccion_posicion_5 = [
        "Bujes de barra trasera",
        "Hojas de elásticos traseros (fisuras)",
        "Bieletas de barra trasera (ajuste)",
        "Bujes de elásticos traseros (desgaste)"
    ]

    # Definir los puntos de inspección de la posición 6
    puntos_inspeccion_posicion_6 = [
        "Espesor de cintas de freno trasera",
        "Indicar la medida actual de la cinta trasera",
        "Indicar la medida próxima de la cinta trasera",
        "Estado de la campana trasera Izquierda",
        "Estado de la campana trasera Derecha",
        "Estado de cajas reguladoras trasera Izquierda (engrase/ sujeción)",
        "Estado de cajas reguladoras trasera Derecha (engrase/ sujeción)",
        "Pulmón de freno trasero Izquierdo (perdida)",
        "Pulmón de freno trasero Derecho (perdida)",
        "Protector de chapa para cinta de frena trasero Izquierdo",
        "Protector de chapa para cinta de freno trasero Derecho",
        "Estado del freno de mano"
    ]



    # Iterar sobre los puntos de inspección de la posición 1
    agregar_puntos_inspeccion("Posición 1 - Inspección parte baja tren delantero", puntos_inspeccion_posicion_1, opciones_estado)

    # Iterar sobre los puntos de inspección de la posición 2
    agregar_puntos_inspeccion("Posición 2 - Dirección", puntos_inspeccion_posicion_2, opciones_estado)

    # Iterar sobre los puntos de inspección de la posición 3
    agregar_puntos_inspeccion("Posición 3 - Frenos parte delantera", puntos_inspeccion_posicion_3, opciones_estado)

    # Iterar sobre los puntos de inspección de la posición 4
    agregar_puntos_inspeccion("Posición 4 - Puente de cardan", puntos_inspeccion_posicion_4, opciones_estado)

    # Iterar sobre los puntos de inspección de la posición 5
    agregar_puntos_inspeccion("Posición 5 - Inspección parte baja tren trasero", puntos_inspeccion_posicion_5, opciones_estado)

    # Iterar sobre los puntos de inspección de la posición 6
    agregar_puntos_inspeccion("Posición 6 - Frenos parte trasera", puntos_inspeccion_posicion_6, opciones_estado)

    datos_tabla = []

    # No incluyo la tabla en este código, como lo has solicitado.

    # Botón para registrar la revisión
    if st.button("Registrar Revisión"):
        # Aquí puedes implementar la lógica para guardar la revisión en una base de datos o archivo.
        st.success("Revisión registrada exitosamente!")

if __name__ == "__main__":
    revisionFosa("Nombre de Usuario")