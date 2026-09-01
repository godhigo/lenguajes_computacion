## Instrucciones para Clonar, Ejecutar y Probar el Proyecto

Para probar el servicio web y ejecutar la solución de los ejercicios solicitados, sigue los pasos descritos a continuación. Se requiere el uso de dos terminales abiertas simultáneamente: una para mantener corriendo el servidor API y otra para ejecutar el script de pruebas.

---

### 1. Clonar el Repositorio e Instalar Dependencias

Abre una terminal y clona el repositorio privado en tu equipo:

```bash
git clone https://github.com/godhigo/lenguajes_computacion.git
cd project
```

**Crea y activa un entorno virtual de Python:**
```bash
# En Windows (PowerShell / CMD)
python -m venv venv
venv\Scripts\activate

# En macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Instala las dependencias del proyecto desde el archivo** `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Terminal 1 - Levantar API REST
**En la primera terminal** (con el entorno virtual activado), inicia el servidor de FastAPI:
```bash
fastapi run main.py
```

El servidor quedará ejecutándose localmente en http://127.0.0.1:8000
Puedes verificar e interactuar con la documentación Swagger UI en tu navegador accediendo a http://127.0.0.1:8000/docs

### 3. Terminal 2 - Ejecutar los Ejercicios Prácticos
Abre una segunda terminal en VS Code (o en tu sistema), navega a la carpeta del proyecto y activa el entorno virtual:
```bash
# En Windows
venv\Scripts\activate

# En macOS / Linux
source venv/bin/activate
```

Ejecuta el script de Python que consume los endpoints de la API y realiza las operaciones teóricas:

```bash
python ejercicios.py
```

Este script enviará las peticiones HTTP a la API local en http://127.0.0.1:8000 e imprimirá en consola los resultados formateados de cada una de las operaciones sobre cadenas y lenguajes.