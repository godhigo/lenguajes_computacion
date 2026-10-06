# Actividad 11. Analizador de complejidad

## Objetivo

Esta actividad amplía el backend desarrollado previamente para evaluación de autómatas AFD y AFN. Se agregaron dos endpoints que reciben un archivo de código fuente, analizan su complejidad algorítmica mediante un modelo local de Ollama y devuelven un nuevo archivo con comentarios de complejidad línea por línea y un resumen final.

Los análisis disponibles son:

- **Big-O:** peor caso.
- **Big-Omega (Ω):** mejor caso.

El modelo utilizado por defecto es `llama3.2`.

---

## Estructura actual del repositorio

```text
lenguajes_computacion/
├── Actividad_11/
│   ├── ACTIVIDAD_11.md
│   ├── main.py
│   └── ejemplos/
│       └── clases-1.cpp
├── requirements.txt
├── README.md
├── ejercicios.py
└── .gitignore
```

> Importante: `requirements.txt` está en la raíz del repositorio, un nivel arriba de `Actividad_11/`. Por esa razón, cuando se instala desde la carpeta `Actividad_11`, se usa `../requirements.txt`.

---

## Endpoints disponibles

El backend conserva los endpoints anteriores:

```http
POST /afd
POST /afn
```

Y agrega los endpoints de esta actividad:

```http
POST /complejidad/big-o
POST /complejidad/big-omega
```

La documentación interactiva de FastAPI se puede consultar en:

```text
http://127.0.0.1:8000/docs
```

---

# Ejecución paso a paso

## 1. Clonar el repositorio

```bash
git clone https://github.com/godhigo/lenguajes_computacion.git
cd lenguajes_computacion/Actividad_11
```

Todos los siguientes comandos, salvo que se indique lo contrario, se ejecutan desde:

```text
lenguajes_computacion/Actividad_11
```

---

## 2. Crear un entorno virtual de Python

En Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Si el entorno se activó correctamente, la terminal normalmente mostrará algo similar a:

```text
(.venv)
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 3. Instalar las dependencias de Python

Como `requirements.txt` está un nivel arriba de `Actividad_11/`, ejecutar:

```bash
python -m pip install -r ../requirements.txt
```

Esto instala, entre otras dependencias, FastAPI y las herramientas necesarias para ejecutar el backend.

Para comprobar que FastAPI quedó disponible:

```bash
fastapi --version
```

---

# Configuración de Ollama

El analizador utiliza Ollama de forma local en:

```text
http://127.0.0.1:11434
```

## 4. Comprobar si Ollama está instalado

```bash
ollama --version
```

Si aparece `command not found`, Ollama debe instalarse.

### Instalación de Ollama en Linux

Comando oficial:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Después verificar:

```bash
ollama --version
```

---

## 5. Descargar el modelo llama3.2

```bash
ollama pull llama3.2
```

La descarga puede tardar dependiendo de la conexión a Internet.

Después comprobar que el modelo está instalado:

```bash
ollama list
```

Debe aparecer una entrada similar a:

```text
NAME               ID              SIZE
llama3.2:latest    ...             ...
```

---

## 6. Comprobar que Ollama está ejecutándose

Antes de intentar iniciar otro proceso de Ollama, comprobar la API local:

```bash
curl http://127.0.0.1:11434/api/tags
```

Si Ollama está funcionando, se recibirá un JSON que contiene los modelos instalados. Por ejemplo:

```json
{
  "models": [
    {
      "name": "llama3.2:latest"
    }
  ]
}
```

En ese caso **no es necesario ejecutar `ollama serve`**, porque el servicio ya está activo.

Si el comando anterior no logra conectarse, iniciar Ollama manualmente:

```bash
ollama serve
```

Esta terminal debe permanecer abierta mientras se utiliza la API.

### Mensaje `address already in use`

Si al ejecutar:

```bash
ollama serve
```

aparece un mensaje parecido a:

```text
Error: listen tcp 127.0.0.1:11434: bind: address already in use
```

normalmente significa que Ollama **ya está ejecutándose** en el puerto `11434`.

Se puede confirmar nuevamente con:

```bash
curl http://127.0.0.1:11434/api/tags
```

Si responde correctamente, no se debe iniciar otra instancia.

---

# Iniciar FastAPI

## 7. Ejecutar el backend

Con el entorno virtual activado y dentro de `Actividad_11/`:

```bash
fastapi dev main.py
```

La terminal debería mostrar algo similar a:

```text
Server started at http://127.0.0.1:8000
Documentation at http://127.0.0.1:8000/docs
```

También puede ejecutarse con:

```bash
uvicorn main:app --reload
```

Mientras el servidor esté ejecutándose, esa terminal debe permanecer abierta.

Para detenerlo:

```text
CTRL+C
```

> Un `404` para `/favicon.ico` en los logs del servidor no representa un error de la API y puede ignorarse.

---

# Probar la API desde Swagger

## 8. Abrir Swagger UI

Con FastAPI ejecutándose, abrir en el navegador:

```text
http://127.0.0.1:8000/docs
```

Deben aparecer, entre otros, estos endpoints:

```text
POST /afd
POST /afn
POST /complejidad/big-o
POST /complejidad/big-omega
```

---

## 9. Probar Big-O

En Swagger:

1. Abrir `POST /complejidad/big-o`.
2. Presionar **Try it out**.
3. En el campo `archivo`, seleccionar:

```text
Actividad_11/ejemplos/clases-1.cpp
```

Si se está seleccionando desde el explorador de archivos del sistema, la ruta del archivo dentro del repositorio es:

```text
lenguajes_computacion/Actividad_11/ejemplos/clases-1.cpp
```

4. Presionar **Execute**.
5. Esperar a que Ollama realice el análisis.
6. Revisar la respuesta o descargar el archivo generado.

Para el archivo:

```text
clases-1.cpp
```

la API genera un nombre de salida como:

```text
clases-1_big_o.cpp
```

El archivo contiene comentarios de complejidad línea por línea y un bloque final similar a:

```cpp
// RESUMEN DE COMPLEJIDAD - Big-O
// Suma de complejidades individuales: O(1) + O(n) + O(n^2) = O(n^2)
// Complejidad de mayor grado: O(n^2)
// O(n^2) domina a los términos de menor crecimiento.
```

La expresión exacta depende del programa analizado.

---

## 10. Probar Big-Omega

En Swagger:

1. Abrir `POST /complejidad/big-omega`.
2. Presionar **Try it out**.
3. Seleccionar el mismo archivo `ejemplos/clases-1.cpp`.
4. Presionar **Execute**.
5. Revisar o descargar el archivo generado.

El nombre de salida será similar a:

```text
clases-1_big_omega.cpp
```

El archivo contiene comentarios del mejor caso y un resumen final similar a:

```cpp
// RESUMEN DE COMPLEJIDAD - Big-Omega (Ω)
// Suma de complejidades individuales: Ω(1) + Ω(n) = Ω(n)
// Complejidad de mayor grado: Ω(n)
// Ω(n) es el término de mayor crecimiento identificado para el mejor caso.
```

---

# Probar desde la terminal con curl

Con FastAPI ejecutándose, abrir otra terminal y entrar a:

```bash
cd ~/Downloads/lenguajes_computacion/Actividad_11
```

La ruta anterior es solo un ejemplo si el repositorio fue clonado dentro de `~/Downloads`. Si se clonó en otro lugar, utilizar la ruta correspondiente.

## Big-O

```bash
curl -X POST \
  -F "archivo=@ejemplos/clases-1.cpp" \
  -OJ \
  http://127.0.0.1:8000/complejidad/big-o
```

El servidor debe devolver un archivo llamado:

```text
clases-1_big_o.cpp
```

Puede revisarse con:

```bash
cat clases-1_big_o.cpp
```

o abrirse con un editor:

```bash
code clases-1_big_o.cpp
```

## Big-Omega

```bash
curl -X POST \
  -F "archivo=@ejemplos/clases-1.cpp" \
  -OJ \
  http://127.0.0.1:8000/complejidad/big-omega
```

El servidor debe devolver:

```text
clases-1_big_omega.cpp
```

---

# Flujo recomendado de ejecución

Una vez que Ollama y `llama3.2` ya están instalados, el flujo diario es sencillo.

### Terminal 1: verificar Ollama

```bash
curl http://127.0.0.1:11434/api/tags
```

Si no responde:

```bash
ollama serve
```

### Terminal 2: ejecutar FastAPI

```bash
cd lenguajes_computacion/Actividad_11
source .venv/bin/activate
fastapi dev main.py
```

### Navegador

Abrir:

```text
http://127.0.0.1:8000/docs
```

---

# Endpoint 1: peor caso con Big-O

## Ruta

```http
POST /complejidad/big-o
```

## Propósito

Analiza el programa recibido considerando el **peor caso** de ejecución y utiliza notación **Big-O**.

El modelo puede identificar costos asociados a:

- asignaciones y operaciones constantes;
- ciclos;
- ciclos anidados;
- condicionales;
- búsquedas;
- ordenamientos;
- llamadas a funciones;
- recursión;
- acceso a estructuras de datos;
- operaciones de entrada/salida.

## Entrada

El endpoint utiliza `multipart/form-data` y espera un campo llamado:

```text
archivo
```

El archivo debe ser texto codificado en UTF-8.

## Salida

La respuesta es directamente un archivo de texto descargable con el código original anotado.

Ejemplo:

```text
Entrada:  clases-1.cpp
Salida:   clases-1_big_o.cpp
```

---

# Endpoint 2: mejor caso con Big-Omega

## Ruta

```http
POST /complejidad/big-omega
```

## Propósito

Analiza el programa recibido considerando el **mejor caso** de ejecución y utiliza notación **Big-Omega (Ω)**.

Esto permite representar escenarios donde un algoritmo puede terminar antes dependiendo de sus datos de entrada.

## Entrada

También utiliza `multipart/form-data` con el campo:

```text
archivo
```

## Salida

Ejemplo:

```text
Entrada:  clases-1.cpp
Salida:   clases-1_big_omega.cpp
```

---

# Validaciones implementadas

Antes de consultar a Ollama, el backend valida el archivo.

| Código HTTP | Situación |
|---|---|
| `400` | No se recibió un nombre de archivo, el archivo está vacío o no está codificado en UTF-8. |
| `413` | El archivo supera el límite de 1 MB. |
| `502` | Ollama respondió vacío o con un formato inesperado. |
| `503` | FastAPI no pudo comunicarse con Ollama o con el modelo `llama3.2`. |

---

# Formato de respuesta

Los endpoints de complejidad responden directamente con el archivo anotado y no con un JSON.

Encabezados principales:

```text
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="..."
X-Complexity-Notation: ...
```

---

# Funcionamiento interno

El flujo del analizador es:

```text
Archivo de código fuente
        |
        v
FastAPI
        |
        | construye prompt de análisis
        v
Ollama / llama3.2
        |
        | genera código anotado
        v
FastAPI
        |
        | Content-Disposition: attachment
        v
Archivo de salida
```

El prototipo original utilizaba la misma idea general: leer un archivo, construir un prompt especializado, consultar el endpoint local de Ollama y guardar el resultado. En la API actual esta lógica se integró directamente al backend de FastAPI y el archivo llega mediante una petición HTTP.

---

# Funciones principales agregadas en `main.py`

## `generar_respuesta_ollama()`

Realiza la petición a:

```text
http://localhost:11434/api/generate
```

utilizando `llama3.2`.

Los errores de conexión se convierten en una respuesta HTTP `503`.

## `construir_prompt_complejidad()`

Genera las instrucciones para el modelo según:

- el nombre del archivo;
- la notación solicitada;
- el peor o mejor caso.

También solicita que se conserve el código fuente y que se agreguen comentarios apropiados para el lenguaje.

## `limpiar_respuesta_modelo()`

Elimina un bloque Markdown accidental si el modelo devuelve el código entre triple acento grave.

## `analizar_archivo_complejidad()`

Contiene la lógica común de ambos endpoints:

1. valida el archivo;
2. comprueba el límite de tamaño;
3. decodifica UTF-8;
4. construye el prompt;
5. consulta Ollama;
6. limpia la respuesta;
7. genera el nombre del archivo de salida;
8. devuelve el archivo al cliente.

---

# Diferencia entre ambos endpoints

| Característica | `/complejidad/big-o` | `/complejidad/big-omega` |
|---|---|---|
| Caso analizado | Peor caso | Mejor caso |
| Notación | Big-O | Big-Omega (Ω) |
| Sufijo de salida | `_big_o` | `_big_omega` |
| Entrada | Archivo UTF-8 | Archivo UTF-8 |
| Salida | Archivo anotado | Archivo anotado |

---

# Suma y complejidad dominante

El archivo generado incluye tanto la suma de complejidades individuales como la complejidad de mayor grado.

Por ejemplo:

```text
O(1) + O(n) + O(n²) = O(n²)
```

Asintóticamente, el término con mayor crecimiento domina la suma.

El análisis producido por un modelo de lenguaje es una aproximación automática y puede requerir revisión humana en programas complejos, especialmente cuando el costo depende de bibliotecas, estructuras internas o condiciones que no pueden inferirse completamente a partir del código fuente.

---

# Solución de problemas

## `fastapi: command not found`

Activar primero el entorno virtual:

```bash
source .venv/bin/activate
```

Si todavía no está instalado:

```bash
python -m pip install -r ../requirements.txt
```

## `ollama: command not found`

En Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Después:

```bash
ollama --version
```

## Error HTTP `503`

Comprobar primero Ollama:

```bash
curl http://127.0.0.1:11434/api/tags
```

Después comprobar que `llama3.2` está instalado:

```bash
ollama list
```

Si no aparece:

```bash
ollama pull llama3.2
```

## `address already in use` al ejecutar `ollama serve`

El puerto `11434` probablemente ya está siendo utilizado por Ollama. Comprobarlo con:

```bash
curl http://127.0.0.1:11434/api/tags
```

Si responde con JSON, Ollama ya está funcionando y no se necesita otro `ollama serve`.

---

# Prueba mínima recomendada para evaluación

1. Clonar el repositorio.
2. Entrar a `lenguajes_computacion/Actividad_11`.
3. Crear y activar `.venv`.
4. Instalar `../requirements.txt`.
5. Verificar Ollama.
6. Verificar `llama3.2`.
7. Ejecutar `fastapi dev main.py`.
8. Abrir `http://127.0.0.1:8000/docs`.
9. Probar `POST /complejidad/big-o` con `ejemplos/clases-1.cpp`.
10. Probar `POST /complejidad/big-omega` con el mismo archivo.
11. Revisar los archivos devueltos y confirmar que contienen comentarios línea por línea y el resumen final.
