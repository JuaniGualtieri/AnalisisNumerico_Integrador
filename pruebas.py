# -*- coding: utf-8 -*-
"""
============================================================================
  pruebas.py  --  Pruebas automáticas del núcleo numérico (sin interfaz)
============================================================================
Verifica que los métodos den resultados correctos comparando con soluciones
exactas conocidas. Ejecutar con:   python pruebas.py
============================================================================
"""

import numpy as np
import metodos_numericos as mn


def aprox(a, b, tol):
    assert abs(a - b) < tol, f"  esperado {b}, obtenido {a} (tol {tol})"


def prueba_edo():
    print("• E.D.O.  y' = y,  y(0)=1  →  exacto e^x")
    f, _ = mn.construir_funcion("y")
    objetivo = np.e
    # RK4 y Milne deben ser muy precisos; Euler modificado algo menos.
    r = mn.euler_modificado(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-3); print(f"    Euler Mod. y(1)={r['ys'][-1]:.8f}  OK")
    r = mn.runge_kutta_4(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-6); print(f"    RK4        y(1)={r['ys'][-1]:.8f}  OK")
    r = mn.milne(f, 0, 1, 1, 20)
    aprox(r["ys"][-1], objetivo, 1e-5); print(f"    Milne      y(1)={r['ys'][-1]:.8f}  OK")


def prueba_edo2():
    print("• E.D.O.  y' = x + y,  y(0)=1  →  exacto 2e^x - x - 1")
    f, _ = mn.construir_funcion("x + y")
    r = mn.runge_kutta_4(f, 0, 1, 1, 50)
    exacto = 2 * np.e - 2
    aprox(r["ys"][-1], exacto, 1e-6); print(f"    RK4 y(1)={r['ys'][-1]:.8f}  exacto={exacto:.8f}  OK")


def prueba_interpolacion():
    print("• Interpolación de e^x en x0=0.55")
    f, _ = mn.construir_funcion("y")
    r = mn.runge_kutta_4(f, 0, 1, 1, 10)
    for nombre, fn in mn.METODOS_INTERPOLACION.items():
        res = fn(r["xs"], r["ys"], 0.55, grado=4)
        aprox(res["valor"], np.exp(0.55), 1e-4)
        print(f"    {nombre:24} y(0.55)={res['valor']:.8f}  OK")


def prueba_parser_seguro():
    print("• Parser seguro rechaza código peligroso")
    for mala in ["__import__('os')", "open('x')", "z + 1"]:
        try:
            mn.construir_funcion(mala)
            raise AssertionError(f"    NO rechazó: {mala}")
        except ValueError:
            pass
    # Acepta '^' como potencia
    f, _ = mn.construir_funcion("x^2 + y")
    aprox(f(3, 1), 10, 1e-12)
    print("    rechazo de nombres no permitidos y '^'→'**'  OK")


def prueba_lu():
    print("• Factorización LU con pivoteo  (P A = L U)")
    A = np.array([[2, 1, 1], [4, -6, 0], [-2, 7, 2]], dtype=float)
    L, U, piv = mn.lu_pivoteo(A)
    PA = A[piv]
    aprox(np.linalg.norm(PA - L @ U), 0.0, 1e-10)
    # Resolver A x = b
    b = np.array([5, -2, 9], dtype=float)
    x = mn.resolver_lu(L, U, piv, b)
    aprox(np.linalg.norm(A @ x - b), 0.0, 1e-10)
    print("    P·A = L·U  y  A·x = b  OK")


def prueba_potencia_inversa():
    print("• Potencia inversa (autovalor de menor módulo)")
    A = [[4, 1, 0], [1, 3, 1], [0, 1, 2]]
    res = mn.potencia_inversa(A, sigma=0.0, tol=1e-12)
    vals, _ = mn.verificar_autovalores(A)
    menor = min(vals, key=abs)
    aprox(res["autovalor_rayleigh"], float(menor), 1e-8)
    assert res["residuo"] < 1e-8
    print(f"    λ={res['autovalor_rayleigh']:.8f}  referencia={float(menor):.8f}  "
          f"residuo={res['residuo']:.1e}  OK")

    print("• Potencia inversa con desplazamiento σ=5 (autovalor cercano a 5)")
    res = mn.potencia_inversa(A, sigma=5.0, tol=1e-12)
    cercano = min(vals, key=lambda v: abs(v - 5))
    aprox(res["autovalor_rayleigh"], float(cercano), 1e-8)
    print(f"    λ={res['autovalor_rayleigh']:.8f}  referencia={float(cercano):.8f}  OK")


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
