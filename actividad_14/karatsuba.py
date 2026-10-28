"""Multiplicación de enteros arbitrariamente grandes con dígitos decimales.

No se usa la multiplicación nativa de enteros grandes para calcular resultados.
La multiplicación elemental ocurre únicamente entre dígitos (0..9).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Estadisticas:
    """Contadores empíricos de trabajo y profundidad recursiva."""

    llamadas: int = 0
    casos_base: int = 0
    multiplicaciones_digito: int = 0
    profundidad_maxima: int = 0


def _normalizar(numero: str | int) -> tuple[int, str]:
    """Convierte un entero decimal en (signo, magnitud sin ceros iniciales)."""
    if not isinstance(numero, (str, int)) or isinstance(numero, bool):
        raise TypeError("El número debe ser un entero o una cadena decimal")
    texto = str(numero).strip()
    if not texto:
        raise ValueError("El número no puede estar vacío")
    signo = -1 if texto.startswith("-") else 1
    if texto[0] in "+-":
        texto = texto[1:]
    if not texto or any(d < "0" or d > "9" for d in texto):
        raise ValueError("Se espera un número entero decimal válido")
    digitos = texto.lstrip("0") or "0"
    return (1 if digitos == "0" else signo), digitos


def _limpiar(numero: str) -> str:
    return numero.lstrip("0") or "0"


def _sumar(a: str, b: str) -> str:
    """Suma magnitudes decimales; no convierte a int grande."""
    i, j, acarreo = len(a) - 1, len(b) - 1, 0
    resultado = []
    while i >= 0 or j >= 0 or acarreo:
        da = ord(a[i]) - 48 if i >= 0 else 0
        db = ord(b[j]) - 48 if j >= 0 else 0
        suma = da + db + acarreo
        resultado.append(str(suma % 10))
        acarreo = suma // 10
        i -= 1
        j -= 1
    return "".join(reversed(resultado))


def _mayor_igual(a: str, b: str) -> bool:
    return len(a) > len(b) or (len(a) == len(b) and a >= b)


def _restar(a: str, b: str) -> str:
    """Calcula a-b para magnitudes con a >= b."""
    if not _mayor_igual(a, b):
        raise ValueError("La resta de magnitudes requiere a >= b")
    i, j, prestamo = len(a) - 1, len(b) - 1, 0
    resultado = []
    while i >= 0:
        da = ord(a[i]) - 48 - prestamo
        db = ord(b[j]) - 48 if j >= 0 else 0
        prestamo = int(da < db)
        if prestamo:
            da += 10
        resultado.append(str(da - db))
        i -= 1
        j -= 1
    return _limpiar("".join(reversed(resultado)))


def _desplazar(a: str, posiciones: int) -> str:
    """a * 10**posiciones, desplazando caracteres y no multiplicando enteros."""
    return a + "0" * posiciones if a != "0" else "0"


def _escuela(a: str, b: str, datos: Estadisticas) -> str:
    """Algoritmo tradicional O(len(a) * len(b)) con arreglo de dígitos."""
    if a == "0" or b == "0":
        return "0"
    resultado = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        acarreo = 0
        da = ord(a[i]) - 48
        for j in range(len(b) - 1, -1, -1):
            db = ord(b[j]) - 48
            datos.multiplicaciones_digito += 1
            pos = i + j + 1
            total = resultado[pos] + da * db + acarreo
            resultado[pos] = total % 10
            acarreo = total // 10
        resultado[i] += acarreo
    return _limpiar("".join(map(str, resultado)))


def _recursivo(a: str, b: str, metodo: str, umbral: int,
               datos: Estadisticas, profundidad: int) -> str:
    datos.llamadas += 1
    datos.profundidad_maxima = max(datos.profundidad_maxima, profundidad)
    if a == "0" or b == "0":
        datos.casos_base += 1
        return "0"
    n = max(len(a), len(b))
    if n <= umbral:
        datos.casos_base += 1
        return _escuela(a, b, datos)

    # Fase 1: DIVISIÓN. x = x_alta * 10**m + x_baja.
    m = n // 2
    a_alta, a_baja = _limpiar(a[:-m] or "0"), _limpiar(a[-m:])
    b_alta, b_baja = _limpiar(b[:-m] or "0"), _limpiar(b[-m:])

    # Fase 2: CONQUISTA. Resolución recursiva de subproblemas.
    z0 = _recursivo(a_baja, b_baja, metodo, umbral, datos, profundidad + 1)
    z2 = _recursivo(a_alta, b_alta, metodo, umbral, datos, profundidad + 1)
    if metodo == "karatsuba":
        # Sólo 3 productos recursivos: el término cruzado se calcula restando.
        suma_a = _sumar(a_alta, a_baja)
        suma_b = _sumar(b_alta, b_baja)
        producto_sumas = _recursivo(
            suma_a, suma_b, metodo, umbral, datos, profundidad + 1
        )
        cruzado = _restar(_restar(producto_sumas, z2), z0)
    else:
        # Divide y vencerás clásico: 4 productos recursivos.
        z01 = _recursivo(a_baja, b_alta, metodo, umbral, datos, profundidad + 1)
        z10 = _recursivo(a_alta, b_baja, metodo, umbral, datos, profundidad + 1)
        cruzado = _sumar(z01, z10)

    # Fase 3: INTEGRACIÓN. Combinar sin productos entre enteros grandes.
    return _sumar(_sumar(_desplazar(z2, 2 * m), _desplazar(cruzado, m)), z0)


def multiplicar(a: str | int, b: str | int, *, metodo: str = "karatsuba",
                umbral: int = 1, datos: Estadisticas | None = None) -> str:
    """Multiplica dos enteros decimales con el método solicitado.

    Métodos: 'escuela', 'divide4' y 'karatsuba'.
    `umbral` determina a partir de cuántos dígitos se usa escuela en la recursión.
    Se devuelve siempre una cadena para no perder precisión.
    """
    if metodo not in {"escuela", "divide4", "karatsuba"}:
        raise ValueError("Método inválido: escuela, divide4 o karatsuba")
    if type(umbral) is not int or umbral < 1:
        raise ValueError("El umbral debe ser un entero >= 1")
    if datos is not None and not isinstance(datos, Estadisticas):
        raise TypeError("datos debe ser una instancia de Estadisticas")

    signo_a, magnitud_a = _normalizar(a)
    signo_b, magnitud_b = _normalizar(b)
    metricas = datos if datos is not None else Estadisticas()
    if metodo == "escuela":
        metricas.llamadas += 1
        metricas.casos_base += 1
        producto = _escuela(magnitud_a, magnitud_b, metricas)
    else:
        producto = _recursivo(magnitud_a, magnitud_b, metodo, umbral, metricas, 0)
    signo = "-" if signo_a != signo_b and producto != "0" else ""
    return signo + producto


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multiplicación exacta sin límite fijo de dígitos")
    parser.add_argument("a", help="Primer entero decimal")
    parser.add_argument("b", help="Segundo entero decimal")
    parser.add_argument("--metodo", choices=["escuela", "divide4", "karatsuba"],
                        default="karatsuba")
    parser.add_argument("--umbral", type=int, default=1)
    argumentos = parser.parse_args()
    estadisticas = Estadisticas()
    print("Resultado:", multiplicar(argumentos.a, argumentos.b,
                                     metodo=argumentos.metodo,
                                     umbral=argumentos.umbral, datos=estadisticas))
    print("Estadísticas:", estadisticas)
