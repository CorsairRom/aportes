import xml.etree.ElementTree as ET
from os import system
system('clear')
# Cargar y parsear el archivo XML
tree = ET.parse('response_fleet.xml')
root = tree.getroot()

# Espacio de nombres para trabajar con los elementos
namespace = {'ns': 'http://standards.iso.org/iso/15143/-3'}
count=0
# Recorrer cada equipo en la flota
for equipment in root.findall('ns:Equipment', namespace):
    header = equipment.find('ns:EquipmentHeader', namespace)
    location = equipment.find('ns:Location', namespace)
    
    # Extraer datos relevantes
    model = header.find('ns:Model', namespace).text
    equipment_id = header.find('ns:EquipmentID', namespace).text
    
    if location is not None:
        latitude = location.find('ns:Latitude', namespace).text
        longitude = location.find('ns:Longitude', namespace).text
        print(f'Ubicación: Latitud {latitude}, Longitud {longitude}')
        print(f'{latitude},{longitude}')
    else:
        print('Ubicación: No disponible')
    count+=1

    print(f'Modelo: {model}')
    print(f'ID del Equipo: {equipment_id}')
    print('---')

print(f'Número de equipos: {count}')