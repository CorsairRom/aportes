import xml.etree.ElementTree as ET
import json

# Datos JSON (parte del archivo ya cargado)
json_file_path = 'result_interna.json'
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Crear la estructura base del XML
root = ET.Element("odoo")
data_element = ET.SubElement(root, "data", noupdate="1")

# Función para agregar causas
def agregar_causa(causa_id, origin, family_ref, name):
    record_element = ET.SubElement(data_element, "record", id=causa_id, model="contract.operations.causeslt")
    ET.SubElement(record_element, "field", name="origin").text = origin
    ET.SubElement(record_element, "field", name="family_id", ref=family_ref)
    ET.SubElement(record_element, "field", name="name").text = name
    ET.SubElement(record_element, "field", name="description").text = f"Causa de pérdida de tiempo del mandante: {name}"

# Agregar causas internas
for machine_type, causes in data["INTERNA"].items():
    family_id = causes[0]["ID"]  # ID de la familia de la máquina
    for idx, cause in enumerate(causes[1:], start=1):
        cause_name = cause["causal"]
        agregar_causa(f"causatp_internal_{machine_type}_{idx}", "internal", family_id, cause_name)

# Agregar causas del mandante
for machine_type, causes in data["MANDANTE"].items():
    family_id = causes[0]["ID"]  # ID de la familia de la máquina
    for idx, cause in enumerate(causes[1:], start=1):
        cause_name = cause["causal"]
        agregar_causa(f"causatp_client_{machine_type}_{idx}", "client", family_id, cause_name)

# Convertir a string con formato XML
tree = ET.ElementTree(root)
ET.indent(tree, space="    ", level=0)  # Para mejor formato
tree_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

# Guardar el XML generado en un archivo
output_path = "causeslt_data2.xml"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(tree_str)

output_path  # Mostrar el path del archivo generado
