# Evaluador de AFD y AFN con FastAPI

## Identificación del equipo

| Dato | Información |
|---|---|
| Nombre de la actividad | Evaluador de AFD y AFN a través de un servicio web |
| Integrante 1 | **Diego Navarro Sánchez**
| No. de cuenta | **202497** 
| Integrante 2 | **Yohualli  Ollin Luna Reyes** |
| No. de cuenta | **189670** |
| Materia | **Lenguajes de Computación** |
| Profesor(a) | **Paulo Vázquez** |

---

## Objetivo

Implementar un servicio web utilizando **FastAPI** que permita evaluar cadenas mediante:

- Autómatas Finitos Deterministas (**AFD**).
- Autómatas Finitos No Deterministas (**AFN**).

Cada evaluador cuenta con su propio endpoint y recibe la definición del autómata junto con una o más cadenas.

El servicio devuelve:

- Estados totales.
- Cantidad de estados.
- Alfabeto.
- Estado inicial.
- Estados finales.
- Resultado de cada cadena.
- Notación de cada transición realizada.

---

## Estructura del proyecto

```text
evaluador_automatas/
├── main.py
├── requirements.txt
└── README.md
```

---

## Instalación

Se recomienda utilizar un entorno virtual.

### 1. Crear entorno virtual

```bash
python -m venv .venv
```

### 2. Activarlo

En Windows:

```bash
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Ejecutar el servidor

```bash
fastapi dev main.py
```

También puede ejecutarse con:

```bash
uvicorn main:app --reload
```

El servidor estará disponible normalmente en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI puede consultarse en:

```text
http://127.0.0.1:8000/docs
```

---

# Ejercicio 1: Evaluación de un AFD

## Definición

Se utiliza un AFD sobre el alfabeto:

```text
Σ = {0, 1}
```

Estados:

```text
Q = {q0, q1}
```

Estado inicial:

```text
q0
```

Estado final:

```text
F = {q1}
```

Tabla de transición:

| Estado | 0 | 1 |
|---|---|---|
| q0 | q0 | q1 |
| q1 | q0 | q1 |

Este AFD acepta las cadenas binarias que terminan en `1`.

## Endpoint

```http
POST /afd
```

## JSON enviado

```json
{
  "tabla_transicion": {
    "q0": {
      "0": "q0",
      "1": "q1"
    },
    "q1": {
      "0": "q0",
      "1": "q1"
    }
  },
  "cadenas": [
    "101",
    "100",
    "111",
    ""
  ],
  "estado_inicial": "q0",
  "estados_finales": [
    "q1"
  ]
}
```

## Resultado esperado

- `101` → ACEPTADA.
- `100` → RECHAZADA.
- `111` → ACEPTADA.
- Cadena vacía `""` → RECHAZADA.

Ejemplo de las transiciones para `101`:

```text
δ(q0, 1) = q1
δ(q1, 0) = q0
δ(q0, 1) = q1
```

El estado final alcanzado es `q1`; como `q1 ∈ F`, la cadena es aceptada.

---

# Ejercicio 2: Evaluación de un AFN

## Definición

Se utiliza un AFN sobre el alfabeto:

```text
Σ = {a, b}
```

Estados:

```text
Q = {q0, q1, q2}
```

Estado inicial:

```text
q0
```

Estado final:

```text
F = {q2}
```

Tabla de transición:

| Estado | a | b |
|---|---|---|
| q0 | {q0, q1} | {q0} |
| q1 | ∅ | {q2} |
| q2 | ∅ | ∅ |

Este AFN acepta cadenas en las que existe un camino que permite llegar a `q2`.

## Endpoint

```http
POST /afn
```

## JSON enviado

```json
{
  "tabla_transicion": {
    "q0": {
      "a": ["q0", "q1"],
      "b": ["q0"]
    },
    "q1": {
      "a": [],
      "b": ["q2"]
    },
    "q2": {
      "a": [],
      "b": []
    }
  },
  "cadenas": [
    "ab",
    "aab",
    "aaa",
    "b"
  ],
  "estado_inicial": "q0",
  "estados_finales": [
    "q2"
  ]
}
```

## Resultado esperado

- `ab` → ACEPTADA.
- `aab` → ACEPTADA.
- `aaa` → RECHAZADA.
- `b` → RECHAZADA.

Ejemplo de evaluación de `ab`:

```text
ε-cierre({q0}) = {q0}
δ({q0}, a) = {q0, q1}
ε-cierre({q0, q1}) = {q0, q1}
δ({q0, q1}, b) = {q0, q2}
ε-cierre({q0, q2}) = {q0, q2}
```

Como el conjunto final contiene `q2`, la cadena es aceptada.

---

## Formato de respuesta del endpoint AFD

Ejemplo reducido:

```json
{
  "tipo": "AFD",
  "estados_totales": ["q0", "q1"],
  "cantidad_estados": 2,
  "alfabeto": ["0", "1"],
  "estado_inicial": "q0",
  "estados_finales": ["q1"],
  "resultados": [
    {
      "cadena": "101",
      "aceptada": true,
      "resultado": "ACEPTADA",
      "estado_al_terminar": "q1",
      "transiciones": [
        "δ(q0, 1) = q1",
        "δ(q1, 0) = q0",
        "δ(q0, 1) = q1"
      ],
      "error": null
    }
  ]
}
```

---

## Formato de respuesta del endpoint AFN

Ejemplo reducido:

```json
{
  "tipo": "AFN",
  "estados_totales": ["q0", "q1", "q2"],
  "cantidad_estados": 3,
  "alfabeto": ["a", "b"],
  "estado_inicial": "q0",
  "estados_finales": ["q2"],
  "resultados": [
    {
      "cadena": "ab",
      "aceptada": true,
      "resultado": "ACEPTADA",
      "estados_al_terminar": ["q0", "q2"],
      "transiciones": [
        "ε-cierre({q0}) = {q0}",
        "δ({q0}, a) = {q0, q1}",
        "ε-cierre({q0, q1}) = {q0, q1}",
        "δ({q0, q1}, b) = {q0, q2}",
        "ε-cierre({q0, q2}) = {q0, q2}"
      ],
      "error": null
    }
  ]
}
```

---

## Conclusiones

La práctica permitió implementar la evaluación de autómatas finitos mediante una API REST.

En el caso del **AFD**, cada combinación de estado y símbolo produce como máximo un único estado siguiente.

En el caso del **AFN**, una transición puede producir varios estados posibles, por lo que durante la evaluación se mantiene un conjunto de estados activos.

Además, el endpoint del AFN implementado admite transiciones epsilon, representadas mediante `ε`, `epsilon`, `eps` o una cadena vacía como clave de transición.

FastAPI facilita la validación de los datos enviados en formato JSON y genera automáticamente documentación interactiva para probar los endpoints.
