import xml.etree.ElementTree as ET
import pandas as pd

# Rutas de los archivos
path_xlsx = "tablas_maestras.xlsx"
crew_data = "crew_data.xml"

# Cargar el XML y extraer los tipos de especialidades
tree = ET.parse(crew_data)
root = tree.getroot()

# Diccionario para almacenar las especialidades y sus IDs
crew_types = {}

# Extraer la información de las especialidades y sus IDs del XML
for record in root.findall(".//record"):
    crew_type = record.find("field[@name='name']").text
    crew_id = record.get("id")
    crew_types[crew_type] = crew_id

# Cargar el Excel y agregar la columna de IDs de especialidades
df_operadores = pd.read_excel(path_xlsx, sheet_name='Operadores')
df_operadores['crew_id'] = df_operadores['Especialidad'].map(crew_types)

# Función para crear el XML
def generar_xml(df, archivo_salida='salida.xml'):
    # Crear el elemento raíz 'odoo'
    root = ET.Element("odoo")
    
    # Crear el subelemento 'data' con el atributo noupdate="1"
    data_element = ET.SubElement(root, "data", noupdate="1")
    
    # Iterar sobre las filas del DataFrame y crear un 'record' para cada operador
    for i, row in df.iterrows():
        nombre = row['Nombre Operador']
        id_especialidad = row['crew_id']  # Obtener el ID de la especialidad ya mapeado
        
        # Crear el elemento 'record' con su id único
        record_element = ET.SubElement(data_element, "record", id=f"crew_{100 + i}", model="struct.crew")
        
        # Agregar el nombre del operador
        ET.SubElement(record_element, "field", name="name").text = nombre
        
        # Agregar el tipo de especialidad si existe
        if id_especialidad:
            ET.SubElement(record_element, "field", name="type_ids", eval=f"[Command.link(ref('{id_especialidad}'))]")
        
        # Agregar el campo de la empresa de referencia
        ET.SubElement(record_element, "field", name="company_id", ref="company_demo_100")

    # Convertir el árbol en una cadena de texto XML
    tree = ET.ElementTree(root)
    
    # Guardar el XML en el archivo especificado
    tree.write(archivo_salida, encoding="utf-8", xml_declaration=True)
    
    print(f"XML generado correctamente en {archivo_salida}")

# Llamar a la función para generar el XML
generar_xml(df_operadores)
