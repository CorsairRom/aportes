## Crear ASSETS
Este script crea un diccionario de assets importando el módulo manifest, busca la vista de templates.xml, busca las importaciones de estáticos y las reúne en un diccionario llamado assets, el cual está listo para pegarse en el nuevo manifest.

## Funcionamiento
Ejecución desde la consola con argumento
Puedes ejecutar el script proporcionando la ruta al archivo manifest directamente desde la consola:

```sh
python3 auto.py [ruta/a/manifest.py]
```

### Ejecución interactiva
Si ejecutas el script sin argumentos, te pedirá la ruta al archivo manifest por consola:

```sh
python3 auto.py
```

Luego, ingresa la ruta cuando se te solicite:

```sh
> Ingrese la ruta del manifest: ruta/a/manifest.py
```

### Comportamiento del script

1. **Verificación de la ruta:**

- Si la ruta especificada no existe, el script solicitará ingresar nuevamente la ruta hasta que sea válida.

2. **Validación del manifest:**

- El script abre y lee el contenido del manifest.

- Comprueba que el manifest contenga la clave data. Si no, el script se cierra y muestra el mensaje "No hay data".

3. **Búsqueda de templates:**

- Busca en la clave data para ver si alguna ruta contiene la palabra "templates". Si no se encuentra, el script se cierra y muestra el mensaje "No hay templates".

4. **Extracción y almacenamiento de assets:**

- Procesa cada ruta en data que apunte a un archivo .xml, extrayendo las rutas CSS y JS.

- Carga estas rutas en el diccionario assets.

- Genera un archivo JSON con el diccionario assets y lo guarda en el mismo directorio del manifest.

## Ejemplo de uso

1. **Ejecución con argumento:**

```sh
python3 auto.py /ruta/al/manifest.py
```

2. **Ejecución interactiva:**

```sh
python3 auto.py
```

Luego ingresa la ruta cuando se te solicite:

```sh
> Ingrese la ruta del manifest: /ruta/al/manifest.py
```

### Salida

El script generará un archivo JSON llamado [nombre_del_manifest]_assets.json en el mismo directorio donde se encuentra el manifest. Este archivo JSON contendrá el diccionario assets con las rutas de los templates extraídas, listo para ser agregado al nuevo manifest.