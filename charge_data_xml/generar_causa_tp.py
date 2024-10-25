import pandas as pd

# Cargar el archivo Excel proporcionado
file_path = 'causas.xlsx'
df_interna = pd.read_excel(file_path, sheet_name='Interna')

# Crear un diccionario basado en la estructura solicitada
# Agrupar por 'RESPONSABLE DE CAUSAL', 'TIPO EQUIPO', y 'CAUSAL INTERNA'

result = {}

# Iterar sobre las filas del DataFrame
for index, row in df_interna.iterrows():
    responsable_causal = row['RESPONSABLE DE CAUSAL']
    tipo_maquina = row['TIPO EQUIPO']
    causal = row['CAUSAL INTERNA']
    
    if responsable_causal not in result:
        result[responsable_causal] = {}
        
    if tipo_maquina not in result[responsable_causal]:
        result[responsable_causal][tipo_maquina] = []
    
    result[responsable_causal][tipo_maquina].append({"causal": causal})

# Mostrar una vista previa del diccionario generado
print(result)
import json

# Convertir el diccionario al formato JSON
json_output = json.dumps(result, indent=4, ensure_ascii=False)

# Guardar el JSON en un archivo local
with open('result_interna.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)
