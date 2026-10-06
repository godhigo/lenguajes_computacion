# Actividad 11. Analizador de complejidad

## Objetivo

Esta ampliación del backend agrega análisis de complejidad algorítmica a la API de FastAPI que previamente evaluaba autómatas AFD y AFN.

Se agregaron dos endpoints capaces de recibir **un archivo de código fuente**, enviarlo al modelo local `llama3.2` mediante Ollama y devolver **otro archivo del mismo tipo** con comentarios de complejidad línea por línea y un resumen final.

Los dos análisis disponibles son:

- **Big-O:** complejidad en el peor de los casos.
- **Big-Omega (Ω):** complejidad en el mejor de los casos.

El analizador está pensado para código fuente de distintos lenguajes. El modelo recibe el nombre/extensión del archivo y se le indica que utilice el estilo de comentarios correspondiente al lenguaje, por ejemplo `#` en Python o `//` en C/C++/Java/JavaScript.

---

## Arquitectura utilizada

El flujo general es:

```text
Cliente
  |
  | multipart/form-data (archivo)
  v
FastAPI
  |
  | construye el prompt de análisis
  v
Ollama / llama3.2
  |
  | devuelve el código anotado
  v
FastAPI
  |
  | respuesta con Content-Disposition: attachment
  v
Archivo comentado descargable
```

El backend conserva los endpoints anteriores:

```http
POST /afd
POST /afn
```

Y agrega:

```http
POST /complejidad/big-o
POST /complejidad/big-omega
```

---

## Requisitos

Instalar las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

Además, la máquina debe tener **Ollama** disponible y el modelo `llama3.2` descargado:

```bash
ollama pull llama3.2
```

Ollama debe estar ejecutándose y escuchando normalmente en:

```text
http://localhost:11434
```

Si es necesario iniciarlo manualmente:

```bash
ollama serve
```

---

## Ejecución del backend

Desde la raíz del repositorio:

```bash
fastapi dev main.py
```

También puede utilizarse:

```bash
uvicorn main:app --reload
```

La API queda disponible normalmente en:

```text
http://127.0.0.1:8000
```

Y Swagger UI en:

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

El modelo debe identificar el costo de operaciones como:

- asignaciones y operaciones constantes;
- ciclos;
- ciclos anidados;
- condicionales;
- búsquedas;
- ordenamientos;
- llamadas a funciones;
- recursión;
- accesos a estructuras de datos;
- operaciones de entrada/salida.

## Entrada

El endpoint utiliza `multipart/form-data` y espera un campo llamado:

```text
archivo
```

El valor debe ser un archivo de texto UTF-8 que contenga código fuente.

Ejemplo con `curl`:

```bash
curl -X POST \
  -F "archivo=@ejemplos/clases-1.cpp" \
  -OJ \
  http://127.0.0.1:8000/complejidad/big-o
```

La opción `-O -J` de `curl` guarda la respuesta utilizando el nombre enviado por el servidor en el encabezado `Content-Disposition`.

## Salida

Si se envía:

```text
clases-1.cpp
```

la API devuelve un archivo llamado:

```text
clases-1_big_o.cpp
```

El contenido conserva el programa y agrega comentarios de complejidad. Al final se solicita un bloque de comentarios como:

```cpp
// RESUMEN DE COMPLEJIDAD - Big-O
// Suma de complejidades individuales: O(1) + O(n) + O(n^2) = O(n^2)
// Complejidad de mayor grado: O(n^2)
// O(n^2) domina a los términos de menor crecimiento.
```

La expresión exacta dependerá del programa analizado.

---

# Endpoint 2: mejor caso con Big-Omega

## Ruta

```http
POST /complejidad/big-omega
```

## Propósito

Analiza el mismo tipo de archivo pero considerando el **mejor caso** de ejecución y utiliza notación **Big-Omega (Ω)**.

Esto permite distinguir situaciones donde un algoritmo puede terminar antes dependiendo de los datos de entrada. Por ejemplo, una búsqueda lineal puede encontrar el elemento en la primera posición en su mejor caso.

## Entrada

También usa `multipart/form-data` con el campo:

```text
archivo
```

Ejemplo:

```bash
curl -X POST \
  -F "archivo=@ejemplos/clases-1.cpp" \
  -OJ \
  http://127.0.0.1:8000/complejidad/big-omega
```

## Salida

Para el archivo:

```text
clases-1.cpp
```

se devuelve:

```text
clases-1_big_omega.cpp
```

El archivo incluye los comentarios línea por línea y un bloque final similar a:

```cpp
// RESUMEN DE COMPLEJIDAD - Big-Omega (Ω)
// Suma de complejidades individuales: Ω(1) + Ω(n) = Ω(n)
// Complejidad de mayor grado: Ω(n)
// Ω(n) es el término de mayor crecimiento identificado para el mejor caso.
```

---

## Validaciones implementadas

Antes de consultar a Ollama, el backend valida el archivo recibido.

| Código HTTP | Situación |
|---|---|
| `400` | No se recibió nombre de archivo, el archivo está vacío o no está codificado en UTF-8. |
| `413` | El archivo supera el límite de 1 MB. |
| `502` | Ollama respondió vacío o con un formato inesperado. |
| `503` | No se pudo conectar con Ollama o con el modelo `llama3.2`. |

El límite de tamaño evita enviar archivos excesivamente grandes al modelo local.

---

## Formato de respuesta

Los dos endpoints responden directamente con el contenido del archivo anotado.

Encabezados principales:

```text
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="..."
X-Complexity-Notation: ...
```

Por esta razón, la respuesta no es un JSON: el entregable del endpoint es el **archivo modificado**.

---

## Lógica utilizada del prototipo original

El prototipo incluido en `analizador.ipynb` ya contenía la idea principal:

1. leer código fuente;
2. construir un prompt especializado en complejidad;
3. llamar a `http://localhost:11434/api/generate` con `llama3.2`;
4. guardar la respuesta como una variante comentada del archivo.

Para integrarlo al backend anterior se trasladó esta lógica a funciones reutilizables dentro de `main.py`. En lugar de trabajar con una ruta fija como `clases-1.cpp`, ahora el archivo llega mediante HTTP y el resultado se devuelve directamente al cliente.

También se agregó limpieza defensiva para retirar bloques Markdown si el modelo llegara a responder con triple acento grave a pesar de la instrucción de devolver únicamente código fuente.

---

## Funciones principales agregadas

### `generar_respuesta_ollama()`

Realiza la petición HTTP a Ollama usando el modelo `llama3.2`. Convierte fallos de conexión en un error HTTP `503` y valida la estructura de la respuesta.

### `construir_prompt_complejidad()`

Genera un prompt distinto según:

- archivo recibido;
- notación solicitada;
- peor o mejor caso.

El prompt obliga al modelo a conservar el código, utilizar comentarios propios del lenguaje y agregar el resumen final.

### `limpiar_respuesta_modelo()`

Elimina un bloque Markdown accidental si el modelo encierra el código entre triple acento grave.

### `analizar_archivo_complejidad()`

Contiene la lógica común de ambos endpoints:

1. valida el archivo;
2. lee UTF-8;
3. construye el prompt;
4. consulta Ollama;
5. limpia la respuesta;
6. genera el nombre de salida;
7. devuelve el archivo como descarga.

---

## Diferencia entre ambos endpoints

| Característica | `/complejidad/big-o` | `/complejidad/big-omega` |
|---|---|---|
| Caso analizado | Peor caso | Mejor caso |
| Notación | Big-O | Big-Omega (Ω) |
| Sufijo de salida | `_big_o` | `_big_omega` |
| Tipo de entrada | Archivo UTF-8 | Archivo UTF-8 |
| Tipo de salida | Archivo anotado | Archivo anotado |

---

## Consideración sobre la suma de complejidades

El archivo final incluye la suma de las complejidades individuales porque así lo solicita la actividad. Asintóticamente, una suma conserva el término de mayor crecimiento. Por ejemplo:

```text
O(1) + O(n) + O(n²) = O(n²)
```

Por eso el resumen también identifica explícitamente la **complejidad de mayor grado**.

El análisis generado por un modelo de lenguaje es una aproximación automática y puede requerir revisión humana en programas complejos, especialmente cuando el costo depende de bibliotecas, estructuras internas o condiciones difíciles de inferir solo a partir del archivo.

---

## Prueba rápida desde Swagger

1. Ejecutar FastAPI.
2. Abrir `http://127.0.0.1:8000/docs`.
3. Seleccionar `POST /complejidad/big-o` o `POST /complejidad/big-omega`.
4. Presionar **Try it out**.
5. Elegir un archivo en el campo `archivo`.
6. Presionar **Execute**.
7. Revisar la respuesta y el archivo devuelto.

El archivo `ejemplos/clases-1.cpp` incluido en el repositorio puede utilizarse para esta prueba.
