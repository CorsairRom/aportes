import os
import ast
import psycopg2
from dotenv import load_dotenv, find_dotenv
from colorama import init, Fore, Style
from os import system

system("clear")

# Inicializa colorama
init(autoreset=True)


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Imprime la ruta del archivo .env encontrado
print(f"Archivo .env encontrado en: {dotenv_path}")

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
                    elif stmt.targets[0].id == '_inherit' and model_name is None:
                        model_name = ast.literal_eval(stmt.value)
                    else:
                        field_name = stmt.targets[0].id
                        field_type, is_related = self.get_field_type(stmt.value)
                        if not field_name.startswith('_'):
                            fields.append((field_name, field_type, is_related))
            if model_name:
                self.models[model_name] = fields

        self.generic_visit(node)

    def is_model_base(self, base):
        if isinstance(base, ast.Name):
            return base.id == 'Model'
        elif isinstance(base, ast.Attribute):
            return (isinstance(base.value, ast.Name) and base.value.id == 'models' and base.attr == 'Model')
        return False

    def get_field_type(self, node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            field_type = node.func.attr
            is_related = any(
                isinstance(keyword, ast.keyword) and (keyword.arg == 'related' or keyword.arg == 'compute')
                for keyword in node.keywords
            )
            return field_type, is_related
        return None, False

def extract_models_info(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)
    
    visitor = ModelFieldVisitor()
    visitor.visit(tree)
    return visitor.models

def check_columns_in_table(table_name, columns, connection):
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table_name,))

    rows = cursor.fetchall()
    existing_columns = {row[0]: row[1] for row in rows}

    fields_exist = [col for col in columns if col[0] in existing_columns and not col[2]]
    no_fields = [col for col in columns if col[0] not in existing_columns and not col[2]]
    related_fields = [col for col in columns if col[0].endswith('_ids')]
    
    # Verificar tipo de datos
    wrong_type_fields = []
    for col in fields_exist:
        field_name, expected_type, _ = col
        actual_type = existing_columns[field_name]
        if not is_type_matching(expected_type, actual_type):
            wrong_type_fields.append((field_name, expected_type, actual_type))
    
    return fields_exist, no_fields, wrong_type_fields, related_fields

def is_type_matching(expected_type, actual_type):
    # Mapa de equivalencias de tipos de datos entre Odoo y PostgreSQL
    type_map = {
        'Float': 'double precision',
        'Integer': 'integer',
        'Datetime': 'timestamp without time zone',
        'Boolean': 'boolean',
        'Char': 'character varying',
        'Text': 'text',
        'Selection': 'character varying',
        'Many2one': 'integer',
        'One2many': 'integer',
        'Html': 'text',
        #'Many2many': 'integer[]'
        # Agrega más equivalencias aquí según sea necesario
    }
    return type_map.get(expected_type) == actual_type

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
    len_text = f"{Style.BRIGHT}{Fore.GREEN}Module review: {Fore.YELLOW}{selected_module}"
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
                    fields_exist, no_fields, wrong_type_fields, related_fields = check_columns_in_table(table_name, variable_names, connection)

                    print(f"Nombre del modelo: {model_name}")
                    print(f"Nombre de la tabla: {table_name}")
                    print("Variables encontradas:")
                    for field in fields_exist:
                        print(f"  - {field[0]}")
                    print(f"{Style.BRIGHT}{Fore.YELLOW}Variables no encontradas:{Style.RESET_ALL}")
                    for field in no_fields:
                        print(f"  - {Style.BRIGHT}{Fore.MAGENTA}{field[0]}{Style.RESET_ALL}")
                    print(f"{Style.BRIGHT}{Fore.CYAN}Variables con tipo de dato incorrecto:{Style.RESET_ALL}")
                    for field in wrong_type_fields:
                        print(f"  - {Style.BRIGHT}{Fore.MAGENTA}{field[0]}{Style.RESET_ALL} (esperado: {field[1]}, actual: {field[2]})")
                    print(f"{Style.BRIGHT}{Fore.BLUE}Campos relacionados:{Style.RESET_ALL}")
                    for field in related_fields:
                        print(f"  - {Style.BRIGHT}{Fore.BLUE}{field[0]}{Style.RESET_ALL}")
                    print("\n")
                    print(f"Total encontradas: {len(fields_exist)}")
                    print(f"{Style.BRIGHT}{Fore.RED}Total no encontradas: {len(no_fields)}{Style.RESET_ALL}")
                    print(f"{Style.BRIGHT}{Fore.CYAN}Total con tipo de dato incorrecto: {len(wrong_type_fields)}{Style.RESET_ALL}")
                    print(f"{Style.BRIGHT}{Fore.BLUE}Total campos relacionados: {len(related_fields)}{Style.RESET_ALL}")
                    
                    # Pausar si hay campos que no se encuentran o tienen tipo de dato incorrecto
                    if no_fields or wrong_type_fields:
                        input(f"{Fore.RED}Por favor, revise los problemas y luego presione Enter para continuar...{Style.RESET_ALL}")
                    
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
