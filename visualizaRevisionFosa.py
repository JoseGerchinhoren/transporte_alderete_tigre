import streamlit as st
import boto3
import io
import pandas as pd
from config import cargar_configuracion
import datetime

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)


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

def visualizar_revisiones_en_fosa():

    st.title("Visualizar Revisiones en Fosa")

    # Cargar el archivo revisiones.csv desde S3
    s3_csv_key = 'revisiones.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    revisiones_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()))

    # Filtrar las columnas deseadas
    columnas_deseadas = ['idRevision', 'coche', 'fechaHoraInicial', 'fechaHoraFinal', 'usuario', 'estado']
    revisiones_df_columnas_deseadas = revisiones_df[columnas_deseadas]

    # Ordenar el DataFrame por la columna 'idRevision' de forma descendente
    revisiones_df_columnas_deseadas = revisiones_df_columnas_deseadas.sort_values(by='idRevision', ascending=False)

    # Convertir la columna "idRevision" a tipo cadena y eliminar las comas
    revisiones_df_columnas_deseadas['idRevision'] = revisiones_df_columnas_deseadas['idRevision'].astype(str).str.replace(',', '')
    revisiones_df['idRevision'] = revisiones_df['idRevision'].astype(str).str.replace(',', '')

    # Agregar un widget de selección de estado
    estado_seleccionado = st.selectbox("Filtrar por Estado:", ['Todos', 'activo', 'cancelado'])

    if estado_seleccionado == 'Todos':
        st.dataframe(revisiones_df_columnas_deseadas)

    else:
        # Filtrar el DataFrame por el estado seleccionado
        filtro_estado = revisiones_df_columnas_deseadas['estado'] == estado_seleccionado
        revisiones_df_filtrado = revisiones_df_columnas_deseadas[filtro_estado]

        # Muestra el dataframe de revisiones en fosa
        st.dataframe(revisiones_df_filtrado)

    st.header("Detalles de Revisiones en Fosa")

    # Agregar un widget de búsqueda por idRevision
    id_revision_buscado = st.text_input("Ingrese idRevision para ver detalles:")

    if id_revision_buscado:
        # Filtrar el DataFrame por el idRevision ingresado
        filtro_id_revision = revisiones_df['idRevision'] == id_revision_buscado
        resultado_busqueda = revisiones_df[filtro_id_revision]

        # Mostrar los resultados de la búsqueda en formato de DataFrames
        for index, row in resultado_busqueda.iterrows():
            mostrar_detalles_revision(row, estado_seleccionado)

    st.header("Editar Estado de Revision en Fosa")

    # Agregar un widget de búsqueda por idRevision
    id_revision_editar_estado = st.text_input("Ingrese idRevision para editar:")

    # Botón para editar el estado de la revisión
    if st.button("Editar Estado"):
        # Validar si el usuario tiene permisos de administrador (debes tener una lógica para determinar esto)
        es_administrador = True  # Reemplaza esto con tu lógica de verificación de administrador

        # Verificar si la hora actual es antes de las 24:00 para usuarios no administradores
        if not es_administrador and datetime.now().hour >= 24:
            st.warning("No puedes editar el estado después de las 24:00 como usuario no administrador.")
        else:
            nuevo_estado = st.selectbox("Nuevo Estado:", ['activo', 'cancelado', 'otro_estado'])
            # Aquí debes agregar la lógica para actualizar el estado en el DataFrame y en tu fuente de datos

def mostrar_detalles_revision(row, estado_seleccionado):
    st.header(f"Detalles de la revisión")
    st.subheader(f"ID Revisión: {row['idRevision']}")
    st.subheader(f"Coche: {row['coche']}")
    st.subheader(f"Fecha Inicial: {row['fechaHoraInicial']}")
    st.subheader(f"Fecha Final: {row['fechaHoraFinal']}")
    st.subheader(f"Usuario que cargó la revisión en fosa: {row['usuario']}")

    st.header('Detalle de Posiciones')
    estado_seleccionado = st.selectbox("Filtrar por Estado:", ['Todos', 'Bueno', 'Regular', 'Malo'])

    # Obtener y mostrar la información adicional utilizando el diccionario de posiciones
    for posicion, columnas in posiciones.items():
        st.subheader(posicion)

        # Crear un DataFrame para la posición actual
        df_posicion = pd.DataFrame(columns=['Nombre de Punto', 'Estado', 'Repuestos', 'Cantidad', 'Dias aprox para cambio'])

        for columna in columnas:
            estado = row[f'estado_{columna}']
            repuestos_columna = f'repuestos_{columna}'
            cantidad_columna = f'cantidad_{columna}'
            dias_cambio = f'dias_cambio_{columna}'

            # Agregar fila al DataFrame de la posición actual
            df_posicion.loc[len(df_posicion)] = [columna, estado, row[repuestos_columna], row[cantidad_columna], row[dias_cambio]]

        if estado_seleccionado == 'Todos':
            st.dataframe(df_posicion)

        else:
            # Filtrar el DataFrame por el estado seleccionado
            filtro_estado = df_posicion['Estado'] == estado_seleccionado
            df_posicion_filtrado = df_posicion[filtro_estado]

            # Mostrar DataFrame de la posición actual después de aplicar el filtro
            st.dataframe(df_posicion_filtrado)

if __name__ == "__main__":
    visualizar_revisiones_en_fosa()