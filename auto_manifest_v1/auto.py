import re
import xml.etree.ElementTree as ET
import json
import ast
import os

assets = {
    "assets": {
        "web.assets_backend": [],
        "web.qunit_suite_tests": []
    }
}

def load_data_backend(_imports):
    """ Load data for assets backend. """
    for data in _imports:
        assets["assets"]["web.assets_backend"].append(data)
    return assets

def extract_assets_paths(xml_file):
    css_paths = []
    js_paths = []
    # Parsea el archivo XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Verifica si el archivo XML contiene el template con id="assets_backend"
    assets_template = root.find('.//template[@id="assets_backend"]')
    if assets_template is None:
        # Si no se encuentra el template, no hay nada que procesar
        return css_paths, js_paths

    # Si se encuentra el template, extrae las rutas de CSS y JS
    for link in assets_template.findall('.//link'):
        href = link.get('href')
        if href:
            css_paths.append(href)

    for script in assets_template.findall('.//script'):
        src = script.get('src')
        if src:
            js_paths.append(src)

    return css_paths, js_paths

def main():
    import sys

    while True:
        if len(sys.argv) > 1:
            path_manifest = sys.argv[1]
            name_json = path_manifest.split("/")[-1]
            path_manifest = path_manifest+"/__manifest__.py"
        else:
            path_manifest = input("Ingrese la ruta del manifest: ")
            name_json = path_manifest.split("/")[-1]
            path_manifest = path_manifest+"/__manifest__.py"

        if not os.path.isfile(path_manifest):
            print("Ruta no encontrada. Por favor, ingrese una ruta válida.")
            sys.argv = []  # Reset sys.argv to ensure the loop continues to prompt
            continue

        manifest_dir = os.path.dirname(path_manifest)

        with open(path_manifest, 'r', encoding='utf-8') as f:
            file_content = f.read()

        try:
            module_manifest = ast.literal_eval(file_content)
        except Exception as e:
            print(f"Error al leer el manifest: {e}")
            sys.argv = []  # Reset sys.argv to ensure the loop continues to prompt
            continue

        if 'data' not in module_manifest:
            print("No hay clave 'data' en el manifest.")
            sys.exit(1)

        path_data = module_manifest['data']

        if not any('templates' in path for path in path_data):
            print("No hay 'templates' en la clave 'data'.")
            sys.exit(1)

        #name_json = os.path.basename(path_manifest).split("/")[-1]

        for path in path_data:
            if '.xml' in path:
                xml_path = os.path.join(manifest_dir, path)
                if not os.path.isfile(xml_path):
                    print(f"Archivo {xml_path} no encontrado.")
                    continue

                try:
                    css_paths, js_paths = extract_assets_paths(xml_path)
                    complete_files = css_paths + js_paths
                    if complete_files:
                        load_data_backend(complete_files)
                except Exception as e:
                    print(f"Error al procesar {path}: {e}")
                    continue

        idented = json.dumps(assets, indent=4, ensure_ascii=False)

        with open(f"{name_json}_assets.json", 'w', encoding='utf-8') as file:
            file.write(idented)

        print(f"Archivo {name_json}_assets.json generado con éxito.")
        break

if __name__ == "__main__":
    main()
