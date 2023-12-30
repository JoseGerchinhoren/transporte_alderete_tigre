import streamlit as st
from datetime import datetime
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
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
            df_total = pd.DataFrame(columns=['idRevision', 'coche', 'fechaHoraInicial', 'fechaHoraFinal'])

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        id_revision = len(df_total)

        # Crear un diccionario con la información de la revisión
        nueva_revision = {'idRevision': id_revision,
                          'coche': data['coche'],
                          'fechaHoraInicial': data['fechaHoraInicial'],
                          'fechaHoraFinal': data['fechaHoraFinal']}

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

        # Guardar localmente también
        df_total.to_csv("revisiones.csv", index=False)

        st.success("Información guardada exitosamente en S3!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información en S3: {e}")

def guardar_revision(coche, fecha_hora_inicial, fecha_hora_final, datos):
    try:
        # Crear un diccionario con la información de la revisión
        data = {'coche': coche,
                'fechaHoraInicial': fecha_hora_inicial.strftime('%Y-%m-%d %H:%M:%S'),
                'fechaHoraFinal': fecha_hora_final.strftime('%Y-%m-%d %H:%M:%S'),
                'datos': datos}

        # Guardar la revisión en S3
        guardar_revision_en_s3(data, 'revisiones.csv')

        st.success("Información guardada exitosamente en S3 y localmente!")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")
        
def main():
    # Configuración inicial
    st.title("Ingresar Nueva Revisión en Fosa")

    # Ingreso de Coche
    coche = st.text_input("Coche:")

    # Validar que se haya ingresado un nombre o número de coche
    if not coche:
        st.warning("Por favor, ingrese un nombre o número de coche para continuar.")
        return

    # Inicializar la variable fecha_hora_inicial solo si no está ya inicializada
    if 'fecha_hora_inicial' not in st.session_state:
        st.session_state.fecha_hora_inicial = None

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now()

    # Botón para comenzar la revisión
    if st.button("Comenzar Revisión"):
        # Almacenar la fecha y hora de inicio en la sesión
        st.session_state.fecha_hora_inicial = fecha_hora_actual
        st.success(f"Revisión iniciada a las {fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')} para el coche {coche}")

    # Mostrar la fecha y hora de inicio solo si ya se inició la revisión
    if st.session_state.fecha_hora_inicial:
        st.subheader(f"Revisión iniciada a las {st.session_state.fecha_hora_inicial.strftime('%Y-%m-%d %H:%M:%S')} para el coche {coche}")

        # Definición de posiciones
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
            "Posición 3, Frenos parte delantera": [
                "Espesor de cintas de freno Delantero",
                "Indicar la medida actual de la cinta Delantera",
                "Indicar la medida próxima de la cinta Delantera",
                "Estado de la campana Delantera Izquierda",
                "Estado de la campana Delantera Derecha",
                "Estado de cajas reguladoras delantera izquierda (engrase /sujeción)",
                "Estado de cajas reguladoras delantera Derecha (engrase/ sujeción)",
                "Pulmón de freno Delantero Izquierdo (perdida)",
                "Pulmón de freno Delantero Derecho (perdida)",
                "Protector de chapa para cinta de freno Delantero Izquierdo",
                "Protector de chapa para cinta de freno Delantero Derecho"
            ],
            "Posición 4, Puente de cardan": [
                "Primer tramo estado",
                "Segundo tramo estado",
                "Tercer tramo estado"
            ],
            "Posición 5, Inspección parta baje tren trasero": [
                "Bujes de barra trasera",
                "Hojas de elásticos traseros (fisuras)",
                "Bieletas de barra trasera (ajuste)",
                "Bujes de elásticos traseros (desgaste)"
            ],
            "Posición 6, Frenos parte trasera": [
                "Espesor de cintas de freno trasera",
                "Indicar la medida actual de la cinta trasera",
                "Indicar la medida próxima de la cinta trasera",
                "Estado de la campana trasera Izquierda",
                "Estado de la campana trasera Derecha",
                "Estado de cajas reguladoras trasera Izquierda (engrase/ sujeción)",
                "Estado de cajas reguladoras trasera Derecha (engrase/ sujeción)",
                "Pulmón de freno trasero Izquierdo (perdida)",
                "Pulmón de freno trasero Derecho (perdida)",
                "Protector de chapa para cinta de freno trasero Izquierdo",
                "Protector de chapa para cinta de freno trasero Derecho",
                "Estado del freno de mano"
            ],
            "Posición 7, Fluidos (estanqueidad=perdidas)": [
                "Estanqueidad de líquido hidráulico",
                "Estanqueidad de líquido refrigerante",
                "Estanqueidad aceite motor",
                "Estanqueidad aceite caja",
                "Estanqueidad aceite diferencial",
                "Estanqueidad líquido treno embrague(buses), freno y embrague (Sprinter)"
            ],
            "Posición 8, Carrocería": [
                "Estado en general en cuanto a oxidación en laterales",
                "Estado general en cuanto a roturas en teleras (estructurales)"
            ],
            "Posición 9, Conductos y cableados": [
                "Estados de soportes de sujeción",
                "Mangueras de aire precintadas",
                "Mangueras de combustible",
                "Conexiones de aire en válvulas",
                "Conexiones de aire en pulmones",
                "Conexiones de cañerías de gasoil en racord's",
                "Estado de ramales de cableados",
                "Estado de grampas sujetadoras de ramales de cableado y mangueras"
            ],
            "Posición 10, Inspección básica sobre la unión": [
                "Estado de correas (inspección visual)",
                "Ruidos en general al poner en marcha",
                "Niveles de fluidos",
                "Liquido de freno",
                "Liquido hidráulico",
                "Aceite motor",
                "Control de luces exteriores",
                "Control luces Interiores",
                "Control de estado de asientos (visión general)",
                "Estado de pisos (visión general)"
            ],
            "Posición 11, Tablero de instrumentos": [
                "Estado de indicadores por reloj",
                "Estado de indicadores por luz",
                "Estado de indicadores sonoros",
                "Estado de comandos llave general de luces y botoneras",
                "Función de bocina y limpiaparabrisas"
            ],
            "Posición 12, Neumáticos": [
                "Estado de dibujo neumáticos izquierdo delantero",
                "Estado de dibujo neumáticos derecho delantero",
                "Estado general neumáticos izquierdo delantero",
                "Estado general neumáticos derecho delantero",
                "Estado casco externo neumático izquierdo delantero",
                "Estado casco externo neumático derecho delantero",
                "Estado de dibujo neumáticos izquierdo trasero",
                "Estado de dibujo neumáticos derecho trasero",
                "Estado general neumáticos izquierdo trasero",
                "Estado general neumáticos derecho trasero",
                "Estado casco externo neumático izquierdo trasero",
                "Estado casco externo neumático derecho trasero"
            ],
            "Posición 13, Inspección general": [
                "Estado de la batería",
                "Estado de los bornes",
                "¿El coche tiene cortacorriente?",
                "Estado del arranque",
                "Estado del alternador",
                "Estado de correas",
                "Estado del filtro de aire",
                "Engrase en puntos de lubricación",
                "Control de limpia parabrisas"
            ],
        }

        # Almacenar los datos de la revisión en un diccionario
        datos_revision = {}

        # Loop a través de las posiciones
        for nombre_posicion, puntos_inspeccion in posiciones.items():
            st.header(nombre_posicion)

            # Loop a través de los puntos de inspección
            for nombre_punto in puntos_inspeccion:
                opciones_estado = ['Bueno', 'Regular', 'Malo']
                estado, repuesto, cantidad = generar_interfaz_punto_inspeccion(nombre_punto, opciones_estado)
                datos_revision[nombre_punto] = (estado, repuesto, cantidad)

        # Botón para guardar la revisión
        if st.button("Guardar Revisión"):
            # Obtener la fecha y hora final de la revisión
            fecha_hora_final = datetime.now()
            st.success(f"Revisión finalizada a las {fecha_hora_final.strftime('%Y-%m-%d %H:%M:%S')} para el coche {coche}")

            # Guardar la información en el archivo CSV
            guardar_revision(coche, st.session_state.fecha_hora_inicial, fecha_hora_final, datos_revision)
            # Limpiar la variable fecha_hora_inicial después de guardar la revisión
            st.session_state.fecha_hora_inicial = None

if __name__ == "__main__":
    main()