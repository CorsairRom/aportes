import pandas as pd
import xml.etree.ElementTree as ET

# Cargar el archivo Excel proporcionado
file_path = 'tarja.xlsm'
df = pd.read_excel(file_path, sheet_name='tarja')

list_fundo = df['FUNDO'].unique()

# Crear la estructura base del XML
root = ET.Element("odoo")
data_element = ET.SubElement(root, "data", noupdate="1")

COUNT=0

def add_farm(farm_id, model,  description, COUNT):
    code = f"farm_{COUNT}"
    record_element = ET.SubElement(data_element, "record", id=farm_id, model=model)
    ET.SubElement(record_element, "field", name="name").text = code #code
    ET.SubElement(record_element, "field", name="description").text = description
    ET.SubElement(record_element, "field", name="company_id", ref='company_demo_101')
    COUNT+=1

