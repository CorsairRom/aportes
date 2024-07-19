import ast
import psycopg2
from dotenv import load_dotenv
import os

class ModelFieldVisitor(ast.NodeVisitor):
    def __init__(self):
        self.models = {}

    def visit_ClassDef(self, node):
        # Detectar la clase de modelo
        if any(self.is_model_base(base) for base in node.bases):
            model_name = None
            fields = []

            # Extraer el nombre del modelo
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    if isinstance(stmt.targets[0], ast.Name):
                        if stmt.targets[0].id == '_name':
                            model_name = ast.literal_eval(stmt.value)

            # Extraer los campos
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
                    field_name = stmt.targets[0].id
                    if not field_name.startswith('_'):
                        fields.append(field_name)

            if model_name:
                self.models[model_name] = fields

        self.generic_visit(node)

    def is_model_base(self, base):
        """Verifica si la base es `models.Model`"""
        if isinstance(base, ast.Name):
            return base.id == 'Model'  # Asume que el módulo `models` ya ha sido importado y se refiere simplemente a `Model`
        elif isinstance(base, ast.Attribute):
            # Verifica si el nombre del módulo es `models`
            return (isinstance(base.value, ast.Name) and base.value.id == 'models' and base.attr == 'Model')
        return False

def extract_models_info(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)
    
    visitor = ModelFieldVisitor()
    visitor.visit(tree)
    return visitor.models

def check_columns_in_table(table_name, columns, connection):
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table_name,))

    rows = cursor.fetchall()
    existing_columns = [row[0] for row in rows]  # Aplanar la lista de tuplas

    fields_exist = [col for col in columns if col in existing_columns]
    no_fields = [col for col in columns if col not in existing_columns]

    return fields_exist, no_fields

def main():
    # Cargar variables de entorno desde .env
    load_dotenv()

    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")

    file_path = '/home/rromero/dev/NEXE/openupgrade-tools/odoo/custom/custom_13/src/nexemodules/weather_station/models/weather_data_models.py'  # Reemplaza esto con la ruta a tu archivo modelo.py

    models_data = extract_models_info(file_path)

    # Configura tu conexión a la base de datos usando variables de entorno
    connection = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    for model_name, variable_names in models_data.items():
        table_name = model_name.replace('.', '_')
        fields_exist, no_fields = check_columns_in_table(table_name, variable_names, connection)

        print(f"Nombre del modelo: {model_name}")
        print(f"Nombre de la tabla: {table_name}")
        print("Variables encontradas:")
        for field in fields_exist:
            print(f"  - {field}")
        print("Variables no encontradas:")
        for field in no_fields:
            print(f"  - {field}")
        print(f"Total encontradas: {len(fields_exist)}")
        print(f"Total no encontradas: {len(no_fields)}")
        print("\n")

    connection.close()

if __name__ == "__main__":
    main()
