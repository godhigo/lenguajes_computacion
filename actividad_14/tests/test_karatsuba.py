"""Pruebas unitarias comparando contra la multiplicación nativa como oráculo."""

import random
import unittest

from karatsuba import Estadisticas, multiplicar


METODOS = [("escuela", 1), ("divide4", 1),
           ("karatsuba", 1), ("karatsuba", 8), ("karatsuba", 16)]


class PruebasMultiplicacion(unittest.TestCase):
    def verificar_todos(self, a, b):
        esperado = str(int(a) * int(b))  # Sólo en pruebas: referencia independiente.
        for metodo, umbral in METODOS:
            with self.subTest(a=str(a)[:25], b=str(b)[:25],
                              metodo=metodo, umbral=umbral):
                datos = Estadisticas()
                obtenido = multiplicar(a, b, metodo=metodo,
                                      umbral=umbral, datos=datos)
                self.assertEqual(obtenido, esperado)
                self.assertGreaterEqual(datos.llamadas, 1)

    def test_ejemplo_pequeno(self):
        self.verificar_todos("1234", "5678")

    def test_cero_signos_y_ceros_iniciales(self):
        for a, b in [("000", "-98312"), ("-00012", "+00045"),
                     ("-1", "-1"), ("8", "0"), ("0", "0"),
                     ("99999", "1"), ("1", "-99999")]:
            self.verificar_todos(a, b)

    def test_operandos_diferentes(self):
        for a, b in [("12345678901234567890", "9"),
                     ("1", "123456789012345678901234567890"),
                     ("1000000000000000000000", "100000"),
                     ("999999999999999", "999999999999999999")]:
            self.verificar_todos(a, b)

    def test_tamanos_obligatorios_20_50_100(self):
        generador = random.Random(2026)
        for digitos in (20, 50, 100):
            for _ in range(4):
                a = str(generador.randrange(1, 10)) + "".join(
                    str(generador.randrange(10)) for _ in range(digitos - 1))
                b = str(generador.randrange(1, 10)) + "".join(
                    str(generador.randrange(10)) for _ in range(digitos - 1))
                self.verificar_todos(a, b)

    def test_patrones_de_acarreo(self):
        for n in (20, 50, 100):
            self.verificar_todos("9" * n, "9" * n)
            self.verificar_todos("1" + "0" * (n - 1), "9" * n)

    def test_reduccion_de_multiplicaciones(self):
        a = "12345678901234567890123456789012345678901234567890"
        b = "98765432109876543210987654321098765432109876543210"
        escuela, karatsuba = Estadisticas(), Estadisticas()
        self.assertEqual(multiplicar(a, b, metodo="escuela", datos=escuela),
                         multiplicar(a, b, datos=karatsuba))
        self.assertLess(karatsuba.multiplicaciones_digito,
                        escuela.multiplicaciones_digito)

    def test_entradas_invalidas(self):
        for a, b in [("12.3", "4"), ("3e5", "4"), ("", "7"),
                     ("--5", "2"), ("  ", "2")]:
            with self.subTest(a=a, b=b):
                with self.assertRaises(ValueError):
                    multiplicar(a, b)
        with self.assertRaises(ValueError):
            multiplicar("10", "20", umbral=0)
        with self.assertRaises(ValueError):
            multiplicar("10", "20", metodo="otro")
        with self.assertRaises(TypeError):
            multiplicar(3.14, 8)


if __name__ == "__main__":
    unittest.main()
