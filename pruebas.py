# -*- coding: utf-8 -*-
"""
============================================================================
  pruebas.py  --  "El control de calidad" del programa
============================================================================
Este archivo NO tiene interfaz: su único trabajo es COMPROBAR, de forma
automática, que todos los métodos del archivo metodos_numericos.py dan
resultados correctos.

¿Cómo lo comprueba? Comparando lo que calcula nuestro programa contra
RESPUESTAS QUE YA CONOCEMOS de antemano (por ejemplo, la solución exacta de una
ecuación, o el resultado de una función ya probada como la de numpy). Si todo
coincide dentro de un margen de error razonable, las pruebas "pasan".

demuestra que los métodos no solo "andan",
sino que dan los números correctos. Se ejecuta con:   python pruebas.py
============================================================================
"""

import numpy as np
import metodos_numericos as mn


def aprox(a, b, tol):
    """
    Comprueba que dos números sean (casi) iguales. Como trabajamos con
    aproximaciones, nunca van a coincidir exactamente, así que aceptamos una
    pequeña diferencia 'tol' (tolerancia). Si la diferencia es mayor, la prueba
    falla y avisa qué se esperaba y qué se obtuvo.
    """
    assert abs(a - b) < tol, f"  esperado {b}, obtenido {a} (tol {tol})"


def prueba_edo():
    """Comprueba los tres métodos de EDO con un caso de respuesta conocida:
    la ecuación  y' = y  con y(0)=1 tiene como solución exacta e^x, así que
    en x=1 el resultado tiene que dar el número e (≈ 2.71828)."""
    print("• E.D.O.  y' = y,  y(0)=1  →  exacto e^x")
    f, _ = mn.construir_funcion("y")
    objetivo = np.e
    # Runge-Kutta y Milne deben ser muy precisos; a Euler le exigimos un poco menos.
    r = mn.euler_modificado(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-3); print(f"    Euler Mod. y(1)={r['ys'][-1]:.8f}  OK")
    r = mn.runge_kutta_4(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-6); print(f"    RK4        y(1)={r['ys'][-1]:.8f}  OK")
    r = mn.milne(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-5); print(f"    Milne      y(1)={r['ys'][-1]:.8f}  OK")


def prueba_edo2():
    """Otro caso con respuesta conocida: y' = x + y con y(0)=1 tiene solución
    exacta 2e^x - x - 1. Verificamos que Runge-Kutta la reproduzca con precisión."""
    print("• E.D.O.  y' = x + y,  y(0)=1  →  exacto 2e^x - x - 1")
    f, _ = mn.construir_funcion("x + y")
    r = mn.runge_kutta_4(f, 0, 1, 1, 50)
    exacto = 2 * np.e - 2
    aprox(r["ys"][-1], exacto, 1e-6); print(f"    RK4 y(1)={r['ys'][-1]:.8f}  exacto={exacto:.8f}  OK")


def prueba_interpolacion():
    """Comprueba que las dos interpolaciones (Newton y Lagrange) estimen bien.
    Sabemos que e^0.55 ≈ 1.73325, así que el valor interpolado en x0=0.55 tiene
    que acercarse a ese número."""
    print("• Interpolación de e^x en x0=0.55")
    f, _ = mn.construir_funcion("y")
    r = mn.runge_kutta_4(f, 0, 1, 1, 10)
    for nombre, fn in mn.METODOS_INTERPOLACION.items():
        res = fn(r["xs"], r["ys"], 0.55, grado=4)
        aprox(res["valor"], np.exp(0.55), 1e-4)
        print(f"    {nombre:24} y(0.55)={res['valor']:.8f}  OK")


def prueba_parser_seguro():
    """Comprueba la SEGURIDAD del lector de ecuaciones: que rechace texto
    peligroso o inválido (intentos de ejecutar código, variables raras) y que,
    en cambio, acepte cosas válidas como el símbolo '^' para la potencia."""
    print("• Parser seguro rechaza código peligroso")
    for mala in ["__import__('os')", "open('x')", "z + 1"]:
        try:
            mn.construir_funcion(mala)
            raise AssertionError(f"    NO rechazó: {mala}")
        except ValueError:
            pass  # perfecto: tenía que rechazarlo
    # Y debe aceptar '^' como potencia: x^2 + y evaluado en (3,1) da 10.
    f, _ = mn.construir_funcion("x^2 + y")
    aprox(f(3, 1), 10, 1e-12)
    print("    rechazo de nombres no permitidos y '^'→'**'  OK")


def prueba_lu():
    """Comprueba la factorización LU de dos formas:
    1) que al multiplicar L·U se recupere la matriz original (reordenada), y
    2) que el sistema A·x = b que resuelve con LU efectivamente lo cumpla."""
    print("• Factorización LU con pivoteo  (P A = L U)")
    A = np.array([[2, 1, 1], [4, -6, 0], [-2, 7, 2]], dtype=float)
    L, U, piv = mn.lu_pivoteo(A)
    PA = A[piv]
    aprox(np.linalg.norm(PA - L @ U), 0.0, 1e-10)   # ¿L·U reconstruye A?
    # Resolvemos un sistema y verificamos que A·x dé realmente b.
    b = np.array([5, -2, 9], dtype=float)
    x = mn.resolver_lu(L, U, piv, b)
    aprox(np.linalg.norm(A @ x - b), 0.0, 1e-10)
    print("    P·A = L·U  y  A·x = b  OK")


def prueba_potencia_inversa():
    """Comprueba el método de la potencia inversa contra numpy (que calcula los
    autovalores de otra forma). Probamos dos situaciones: sin desplazamiento
    (debe dar el autovalor de menor módulo) y con desplazamiento σ=5 (debe dar
    el autovalor más cercano a 5)."""
    print("• Potencia inversa (autovalor de menor módulo)")
    A = [[4, 1, 0], [1, 3, 1], [0, 1, 2]]
    res = mn.potencia_inversa(A, sigma=0.0, tol=1e-12)
    vals, _ = mn.verificar_autovalores(A)
    menor = min(vals, key=abs)                       # el menor según numpy
    aprox(res["autovalor_rayleigh"], float(menor), 1e-8)
    assert res["residuo"] < 1e-8                      # el residuo casi cero = correcto
    print(f"    λ={res['autovalor_rayleigh']:.8f}  referencia={float(menor):.8f}  "
          f"residuo={res['residuo']:.1e}  OK")

    print("• Potencia inversa con desplazamiento σ=5 (autovalor cercano a 5)")
    res = mn.potencia_inversa(A, sigma=5.0, tol=1e-12)
    cercano = min(vals, key=lambda v: abs(v - 5))     # el más cercano a 5 según numpy
    aprox(res["autovalor_rayleigh"], float(cercano), 1e-8)
    print(f"    λ={res['autovalor_rayleigh']:.8f}  referencia={float(cercano):.8f}  OK")


# Si ejecutamos este archivo directamente, corremos TODAS las pruebas en orden
# y, si ninguna falla, mostramos el cartel final de éxito.
if __name__ == "__main__":
    print("=" * 60)
    print("  PRUEBAS AUTOMÁTICAS DEL NÚCLEO NUMÉRICO")
    print("=" * 60)
    prueba_edo()
    prueba_edo2()
    prueba_interpolacion()
    prueba_parser_seguro()
    prueba_lu()
    prueba_potencia_inversa()
    print("=" * 60)
    print("  ✓ TODAS LAS PRUEBAS PASARON")
    print("=" * 60)
