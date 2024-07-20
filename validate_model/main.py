import os
import ast
import psycopg2
from dotenv import load_dotenv
from colorama import init, Fore, Style
from os import system
system("clear")

# Inicializa colorama
init(autoreset=True)

class ModelFieldVisitor(ast.NodeVisitor):
    def __init__(self):
        self.models = {}

    def visit_ClassDef(self, node):
        if any(self.is_model_base(base) for base in node.bases):
            model_name = None
            fields = []
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
                    if stmt.targets[0].id == '_name':
                        model_name = ast.literal_eval(stmt.value)
                    else:
                        field_name = stmt.targets[0].id
                        if not field_name.startswith('_'):
                            fields.append(field_name)
            if model_name:
                self.models[model_name] = fields

        self.generic_visit(node)

    def is_model_base(self, base):
        if isinstance(base, ast.Name):
            return base.id == 'Model'
        elif isinstance(base, ast.Attribute):
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
    existing_columns = [row[0] for row in rows]

    fields_exist = [col for col in columns if col in existing_columns]
    no_fields = [col for col in columns if col not in existing_columns]

    return fields_exist, no_fields

def get_module_path():
    base_path = os.getenv("BASE_PATH")
    versions = ["12", "13", "14", "15", "16", "17"]
    types = ["basemodules", "nexemodules"]

    # Select Odoo version
    print("Select Odoo version:")
    for idx, version in enumerate(versions):
        print(f"{idx}: {version}")
    version_idx = int(input("Enter the number for Odoo version: "))
    selected_version = versions[version_idx]

    # Select module type
    print("Select module type:")
    for idx, type_ in enumerate(types):
        print(f"{idx}: {type_}")
    type_idx = int(input("Enter the number for module type: "))
    selected_type = types[type_idx]

    # List modules in the selected directory
    module_base_path = os.path.join(base_path, f"custom_{selected_version}/src/{selected_type}/")
    modules = [name for name in os.listdir(module_base_path) if os.path.isdir(os.path.join(module_base_path, name))]
    modules.sort()
    
    print("Select module:")
    for idx, module in enumerate(modules):
        print(f"{idx}: {module}")
    module_idx = int(input("Enter the number for module: "))
    selected_module = modules[module_idx]

    # Clear the console
    os.system('clear' if os.name == 'posix' else 'cls')
    len_text =f"{Style.BRIGHT}{Fore.GREEN}Module review: {Fore.YELLOW}{selected_module}"
    real_len = len(len_text.replace(Style.BRIGHT, "").replace(Fore.GREEN, "").replace(Fore.YELLOW, ""))

    # Print selected information with color and decoration
    print("#" * real_len)
    print(f"{Style.BRIGHT}{Fore.GREEN}Review version odoo: {Fore.YELLOW}{selected_version}")
    print(f"{Style.BRIGHT}{Fore.GREEN}Type module: {Fore.YELLOW}{selected_type}")
    print(len_text)
    print("#" * real_len)
    print("")
    
    # Complete path to the models directory
    models_path = os.path.join(module_base_path, selected_module, "models/")
    return models_path

def process_models_in_directory(models_path, connection):
    for root, _, files in os.walk(models_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                models_data = extract_models_info(file_path)
                for model_name, variable_names in models_data.items():
                    table_name = model_name.replace('.', '_')
                    fields_exist, no_fields = check_columns_in_table(table_name, variable_names, connection)

                    print(f"Nombre del modelo: {model_name}")
                    print(f"Nombre de la tabla: {table_name}")
                    print("Variables encontradas:")
                    for field in fields_exist:
                        print(f"  - {field}")
                    print(f"{Style.BRIGHT}{Fore.YELLOW}Variables no encontradas:{Style.RESET_ALL}")
                    for field in no_fields:
                        print(f"  - {Style.BRIGHT}{Fore.MAGENTA}{field}{Style.RESET_ALL}")
                    print(f"Total encontradas: {len(fields_exist)}")
                    print(f"{Style.BRIGHT}{Fore.RED}Total no encontradas: {len(no_fields)}{Style.RESET_ALL}")
                    print("\n")

def main():
    load_dotenv()

    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")

    models_path = get_module_path()

    connection = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    process_models_in_directory(models_path, connection)

    connection.close()

if __name__ == "__main__":
    main()
