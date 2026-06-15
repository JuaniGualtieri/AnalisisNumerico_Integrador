# -*- coding: utf-8 -*-
"""
============================================================================
  metodos_numericos.py
============================================================================
Núcleo matemático del Trabajo Final Integrador de Análisis Numérico (I.S.I.).

Contiene, implementados "desde cero" (sin usar solucionadores de alto nivel),
los métodos pedidos por la cátedra:

  EJERCICIO 1 -- Resolución de E.D.O. de primer orden  y' = f(x, y),  y(a)=y0
    * Método de Euler Modificado (predictor-corrector / Heun)
    * Método de Runge-Kutta de 4º orden (RK4)
    * Método de Milne (predictor-corrector multipaso, arrancado con RK4)
    e interpolación del valor y(x0):
    * Interpolación de Newton (diferencias divididas)
    * Interpolación de Lagrange

  EJERCICIO 2 -- Autovalor y autovector por el método de la POTENCIA INVERSA
    * Factorización LU con pivoteo parcial (resuelve el sistema en cada paso)
    * Iteración de la potencia inversa (con desplazamiento opcional sigma)

El código está pensado para ser leído: cada función documenta sus fórmulas y
devuelve, además del resultado, el "detalle" paso a paso para mostrarlo en
pantalla (tablas e informes).

Autor: (completar con tu nombre y legajo)
============================================================================
"""

from __future__ import annotations

import numpy as np

# sympy se usa sólo para interpretar la ecuación que tipea el usuario y, si es
# posible, obtener la solución exacta para comparar el error.  Si no estuviera
# instalado, el resto del programa sigue funcionando.
try:
    import sympy as sp
    HAY_SYMPY = True
except Exception:  # pragma: no cover
    HAY_SYMPY = False


# ===========================================================================
#  1) INTERPRETACIÓN DE LA ECUACIÓN DIFERENCIAL  y' = f(x, y)
# ===========================================================================

# Ecuaciones de ejemplo (nombre -> (expresión f(x,y), a, b, y0, x0))
# Se eligieron casos con solución analítica conocida para poder mostrar el error.
EJEMPLOS_EDO = {
    "y' = x + y                (sol: -x-1+2e^x)": ("x + y", 0.0, 1.0, 1.0, 0.5),
    "y' = y                    (sol: e^x)":        ("y", 0.0, 1.0, 1.0, 0.5),
    "y' = x*y                  (sol: e^(x^2/2))":  ("x*y", 0.0, 2.0, 1.0, 1.0),
    "y' = x - y                (decaimiento)":     ("x - y", 0.0, 2.0, 1.0, 1.0),
    "y' = -2*x*y               (gaussiana)":       ("-2*x*y", 0.0, 2.0, 1.0, 1.0),
    "y' = (x - y)/2":                              ("(x - y)/2", 0.0, 3.0, 1.0, 1.5),
    "y' = cos(x)               (sol: sin(x)+y0)":  ("cos(x)", 0.0, 6.283185, 0.0, 3.1416),
    "y' = y*(1 - y)            (logística)":       ("y*(1 - y)", 0.0, 6.0, 0.1, 3.0),
}


# Funciones y constantes matemáticas permitidas al interpretar la ecuación.
# Se usan las versiones de numpy para poder evaluar sobre arreglos.
_FUNCIONES_PERMITIDAS = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
    'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
    'exp': np.exp, 'log': np.log, 'ln': np.log, 'log10': np.log10,
    'sqrt': np.sqrt, 'abs': np.abs, 'fabs': np.abs,
    'pow': np.power, 'sign': np.sign,
    'pi': np.pi, 'e': np.e,
}


def construir_funcion(expresion: str):
    """
    Convierte el texto que ingresa el usuario (por ej. "x + y", "x*sin(y)")
    en una función Python f(x, y) evaluable numéricamente.

    El análisis es SEGURO: se compila la expresión y se verifica que sólo use
    los nombres permitidos (x, y y las funciones matemáticas de la lista). Se
    evalúa sin acceso a las funciones internas de Python ('__builtins__' vacío),
    por lo que no puede ejecutar código peligroso.

    Devuelve: (funcion_f, texto_expresion)
    """
    # Comodidad: aceptar '^' como potencia (notación matemática habitual).
    expr_norm = expresion.replace('^', '**')

    try:
        codigo = compile(expr_norm, "<ecuacion>", "eval")
    except SyntaxError as err:
        raise ValueError(f"La ecuación «{expresion}» tiene un error de sintaxis.\n{err}")

    # Validar que sólo se usen nombres permitidos.
    for nombre in codigo.co_names:
        if nombre not in _FUNCIONES_PERMITIDAS and nombre not in ('x', 'y'):
            raise ValueError(
                f"Nombre no permitido en la ecuación: «{nombre}».\n"
                "Use sólo x, y y funciones como sin, cos, exp, log, sqrt, ...")

    entorno_base = dict(_FUNCIONES_PERMITIDAS)
    entorno_base['__builtins__'] = {}

    def f(xv, yv):
        entorno = dict(entorno_base)
        entorno['x'] = xv
        entorno['y'] = yv
        return float(eval(codigo, entorno))

    # Prueba rápida de evaluación para detectar errores ESTRUCTURALES temprano
    # (por ej. una función mal usada). Los errores meramente aritméticos en un
    # punto puntual (división por cero, dominio del log, etc.) no invalidan la
    # ecuación: pueden no ocurrir en los nodos reales.
    for xp, yp in ((1.0, 1.0), (0.5, 0.5), (2.0, 1.0)):
        try:
            f(xp, yp)
            break
        except (ArithmeticError, ValueError, OverflowError):
            continue
        except Exception as err:
            raise ValueError(f"No se pudo evaluar la ecuación «{expresion}».\n{err}")

    return f, expresion


def solucion_exacta(expresion: str, a: float, y0: float):
    """
    Intenta obtener la solución analítica exacta y(x) del problema de valores
    iniciales  y' = f(x,y), y(a)=y0,  usando sympy.dsolve.

    Devuelve (funcion_exacta, expresion_solucion) o (None, None) si no se pudo.
    Es OPCIONAL: sirve únicamente para comparar y mostrar el error real.
    """
    if not HAY_SYMPY:
        return None, None
    try:
        x = sp.symbols('x')
        y = sp.Function('y')
        # Reparseamos reemplazando el símbolo 'y' por la función y(x).
        ysim = sp.symbols('y')
        permitidos = {
            'x': x, 'y': ysim,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'ln': sp.log, 'sqrt': sp.sqrt,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'pi': sp.pi, 'e': sp.E,
        }
        expr = sp.sympify(expresion, locals=permitidos).subs(ysim, y(x))
        ode = sp.Eq(y(x).diff(x), expr)
        sol = sp.dsolve(ode, y(x), ics={y(a): y0})
        rhs = sol.rhs
        if rhs.free_symbols - {x}:
            return None, None  # quedaron constantes sin resolver
        f_exact = sp.lambdify(x, rhs, modules=['numpy'])
        return f_exact, rhs
    except Exception:
        return None, None


# ===========================================================================
#  2) MÉTODOS PARA RESOLVER LA E.D.O.
#     Todos parten de y(a)=y0 y avanzan con paso h = (b-a)/n.
#     Devuelven un diccionario con:  xs, ys, h, pasos (detalle) y nombre.
# ===========================================================================

def euler_modificado(f, a, b, y0, n, tol=1e-10, max_corr=50):
    """
    MÉTODO DE EULER MODIFICADO  (predictor-corrector, también llamado de Heun).

    En cada paso:
        Predictor (Euler):   y* = y_i + h * f(x_i, y_i)
        Corrector (trapecio):
            y_{i+1} = y_i + (h/2) * [ f(x_i, y_i) + f(x_{i+1}, y*) ]
        El corrector se ITERA hasta que dos aproximaciones difieran menos que
        'tol' (o hasta 'max_corr' iteraciones).

    Orden global del método: O(h^2).
    """
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [0.0] * (n + 1)
    ys[0] = y0
    pasos = []  # detalle para la tabla

    for i in range(n):
        xi, yi = xs[i], ys[i]
        fi = f(xi, yi)
        # Predictor
        y_pred = yi + h * fi
        # Corrector iterado
        y_corr = y_pred
        n_iter = 0
        for _ in range(max_corr):
            n_iter += 1
            y_nuevo = yi + (h / 2.0) * (fi + f(xs[i + 1], y_corr))
            if abs(y_nuevo - y_corr) < tol:
                y_corr = y_nuevo
                break
            y_corr = y_nuevo
        ys[i + 1] = y_corr
        pasos.append({
            "i": i, "x": xi, "y": yi, "f": fi,
            "predictor": y_pred, "corrector": y_corr,
            "iter_corr": n_iter, "x_sig": xs[i + 1], "y_sig": y_corr,
        })

    return {"nombre": "Euler Modificado", "xs": xs, "ys": ys, "h": h, "pasos": pasos}


def runge_kutta_4(f, a, b, y0, n):
    """
    MÉTODO DE RUNGE-KUTTA DE 4º ORDEN (RK4).

    En cada paso se calculan cuatro pendientes:
        k1 = f(x_i,        y_i)
        k2 = f(x_i + h/2,   y_i + h/2 * k1)
        k3 = f(x_i + h/2,   y_i + h/2 * k2)
        k4 = f(x_i + h,     y_i + h   * k3)
    y se combina:
        y_{i+1} = y_i + (h/6) * (k1 + 2 k2 + 2 k3 + k4)

    Es un método de un paso, muy preciso.  Orden global: O(h^4).
    """
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [0.0] * (n + 1)
    ys[0] = y0
    pasos = []

    for i in range(n):
        xi, yi = xs[i], ys[i]
        k1 = f(xi, yi)
        k2 = f(xi + h / 2.0, yi + h / 2.0 * k1)
        k3 = f(xi + h / 2.0, yi + h / 2.0 * k2)
        k4 = f(xi + h, yi + h * k3)
        y_sig = yi + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        ys[i + 1] = y_sig
        pasos.append({
            "i": i, "x": xi, "y": yi,
            "k1": k1, "k2": k2, "k3": k3, "k4": k4,
            "x_sig": xs[i + 1], "y_sig": y_sig,
        })

    return {"nombre": "Runge-Kutta 4", "xs": xs, "ys": ys, "h": h, "pasos": pasos}


def milne(f, a, b, y0, n, tol=1e-10, max_corr=50):
    """
    MÉTODO DE MILNE  (predictor-corrector multipaso de 4 puntos).

    Necesita 4 valores iniciales (y0..y3); los obtenemos con RK4 (autoarranque).
    Luego, para i = 3, 4, ..., n-1:

        Predictor (de Milne):
            y*_{i+1} = y_{i-3} + (4h/3) * ( 2 f_{i-2} - f_{i-1} + 2 f_i )

        Corrector (regla de Simpson):
            y_{i+1} = y_{i-1} + (h/3) * ( f_{i-1} + 4 f_i + f_{i+1} )
        donde f_{i+1} se evalúa con el último valor disponible (se itera el
        corrector hasta converger).

    Orden global: O(h^4).  Requiere n >= 4 (al menos un paso de Milne).
    """
    if n < 4:
        raise ValueError("El método de Milne requiere al menos 4 pasos (n >= 4).")

    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [0.0] * (n + 1)
    ys[0] = y0
    pasos = []

    # --- Arranque con RK4 para y1, y2, y3 ---
    arranque = runge_kutta_4(f, a, a + 3 * h, y0, 3)
    for i in range(1, 4):
        ys[i] = arranque["ys"][i]
        pasos.append({
            "i": i, "x": xs[i], "tipo": "RK4 (arranque)",
            "predictor": np.nan, "corrector": ys[i],
            "iter_corr": 0, "y_sig": ys[i],
        })

    # f en cada nodo conocido
    fval = [f(xs[i], ys[i]) for i in range(4)] + [0.0] * (n - 3)

    # --- Iteración de Milne ---
    for i in range(3, n):
        # Predictor de Milne
        y_pred = ys[i - 3] + (4.0 * h / 3.0) * (2 * fval[i - 2] - fval[i - 1] + 2 * fval[i])
        # Corrector (Simpson), iterado
        y_corr = y_pred
        n_iter = 0
        for _ in range(max_corr):
            n_iter += 1
            f_sig = f(xs[i + 1], y_corr)
            y_nuevo = ys[i - 1] + (h / 3.0) * (fval[i - 1] + 4 * fval[i] + f_sig)
            if abs(y_nuevo - y_corr) < tol:
                y_corr = y_nuevo
                break
            y_corr = y_nuevo
        ys[i + 1] = y_corr
        fval[i + 1] = f(xs[i + 1], y_corr)
        pasos.append({
            "i": i + 1, "x": xs[i + 1], "tipo": "Milne",
            "predictor": y_pred, "corrector": y_corr,
            "iter_corr": n_iter, "y_sig": y_corr,
        })

    return {"nombre": "Milne", "xs": xs, "ys": ys, "h": h, "pasos": pasos}


# Registro de métodos disponibles para el ejercicio 1 (nombre visible -> función)
METODOS_EDO = {
    "Euler Modificado": euler_modificado,
    "Runge-Kutta 4": runge_kutta_4,
    "Milne": milne,
}


# ===========================================================================
#  3) INTERPOLACIÓN DE y(x0)
# ===========================================================================

def _ventana_nodos(xs, x0, grado):
    """
    Elige el bloque CONTIGUO de (grado+1) nodos más cercano a x0.
    Trabajar con nodos vecinos evita las oscilaciones (fenómeno de Runge)
    que aparecen al interpolar con polinomios de grado muy alto.
    """
    m = grado + 1
    n = len(xs)
    if m >= n:
        return 0, n  # usar todos los nodos
    # nodo más cercano a x0
    j = min(range(n), key=lambda k: abs(xs[k] - x0))
    ini = j - m // 2
    ini = max(0, min(ini, n - m))
    return ini, ini + m


def interpolacion_newton(xs, ys, x0, grado=None):
    """
    INTERPOLACIÓN POLINÓMICA DE NEWTON por DIFERENCIAS DIVIDIDAS.

    Construye la tabla de diferencias divididas y evalúa el polinomio
        P(x) = f[x0] + f[x0,x1](x-x0) + f[x0,x1,x2](x-x0)(x-x1) + ...
    en el punto pedido.

    Devuelve un diccionario con el valor interpolado, la tabla de diferencias,
    los coeficientes, los nodos usados y una función P(x) para graficar.
    """
    n_total = len(xs)
    if grado is None:
        grado = n_total - 1
    grado = max(1, min(grado, n_total - 1))

    ini, fin = _ventana_nodos(xs, x0, grado)
    xn = list(xs[ini:fin])
    yn = list(ys[ini:fin])
    m = len(xn)

    # Tabla de diferencias divididas (matriz triangular).
    tabla = [[0.0] * m for _ in range(m)]
    for i in range(m):
        tabla[i][0] = yn[i]
    for j in range(1, m):
        for i in range(m - j):
            tabla[i][j] = (tabla[i + 1][j - 1] - tabla[i][j - 1]) / (xn[i + j] - xn[i])

    # Coeficientes del polinomio = primera fila de la tabla.
    coef = [tabla[0][j] for j in range(m)]

    def P(x):
        x = np.asarray(x, dtype=float)
        resultado = np.full_like(x, coef[0], dtype=float) if x.ndim else coef[0]
        producto = np.ones_like(x, dtype=float) if x.ndim else 1.0
        for j in range(1, m):
            producto = producto * (x - xn[j - 1])
            resultado = resultado + coef[j] * producto
        return resultado

    valor = float(_eval_escalar(coef, xn, x0))

    return {
        "metodo": "Newton (diferencias divididas)",
        "valor": valor, "P": P, "coef": coef,
        "tabla": tabla, "xnodos": xn, "ynodos": yn, "grado": m - 1,
        "rango_nodos": (ini, fin - 1),
    }


def _eval_escalar(coef, xn, x0):
    """Evalúa el polinomio de Newton (forma anidada) en un escalar x0."""
    m = len(coef)
    resultado = coef[0]
    producto = 1.0
    for j in range(1, m):
        producto *= (x0 - xn[j - 1])
        resultado += coef[j] * producto
    return resultado


def interpolacion_lagrange(xs, ys, x0, grado=None):
    """
    INTERPOLACIÓN POLINÓMICA DE LAGRANGE.

        P(x) = Σ_i  y_i * L_i(x),   con   L_i(x) = Π_{j≠i} (x - x_j)/(x_i - x_j)

    Devuelve el valor interpolado, los nodos usados, los pesos L_i(x0) y una
    función P(x) para graficar.
    """
    n_total = len(xs)
    if grado is None:
        grado = n_total - 1
    grado = max(1, min(grado, n_total - 1))

    ini, fin = _ventana_nodos(xs, x0, grado)
    xn = list(xs[ini:fin])
    yn = list(ys[ini:fin])
    m = len(xn)

    def L(i, x):
        prod = np.ones_like(np.asarray(x, dtype=float))
        for j in range(m):
            if j != i:
                prod = prod * (x - xn[j]) / (xn[i] - xn[j])
        return prod

    def P(x):
        x = np.asarray(x, dtype=float)
        s = np.zeros_like(x, dtype=float)
        for i in range(m):
            s = s + yn[i] * L(i, x)
        return s

    # Pesos L_i(x0) y valor.
    pesos = []
    valor = 0.0
    for i in range(m):
        Li = 1.0
        for j in range(m):
            if j != i:
                Li *= (x0 - xn[j]) / (xn[i] - xn[j])
        pesos.append(Li)
        valor += yn[i] * Li

    return {
        "metodo": "Lagrange",
        "valor": float(valor), "P": P,
        "pesos": pesos, "xnodos": xn, "ynodos": yn, "grado": m - 1,
        "rango_nodos": (ini, fin - 1),
    }


METODOS_INTERPOLACION = {
    "Newton (dif. divididas)": interpolacion_newton,
    "Lagrange": interpolacion_lagrange,
}


# ===========================================================================
#  4) EJERCICIO 2 -- FACTORIZACIÓN LU Y MÉTODO DE LA POTENCIA INVERSA
# ===========================================================================

def lu_pivoteo(A):
    """
    Factorización LU con PIVOTEO PARCIAL:   P A = L U
        L : triangular inferior con 1 en la diagonal
        U : triangular superior
        P : matriz de permutación (registrada como lista de índices)

    Se calcula UNA sola vez y luego se reutiliza para resolver el sistema en
    cada iteración de la potencia inversa (gran ventaja del método).
    """
    A = np.array(A, dtype=float)
    n = A.shape[0]
    U = A.copy()
    L = np.eye(n)
    piv = list(range(n))  # permutación

    for k in range(n):
        # Pivoteo parcial: fila con mayor |U[i,k]|
        p = k + int(np.argmax(np.abs(U[k:, k])))
        if abs(U[p, k]) < 1e-15:
            raise ValueError("La matriz (A - sigma·I) es singular: elija otro "
                             "desplazamiento sigma.")
        if p != k:
            U[[k, p], :] = U[[p, k], :]
            piv[k], piv[p] = piv[p], piv[k]
            if k > 0:
                L[[k, p], :k] = L[[p, k], :k]
        # Eliminación
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] -= L[i, k] * U[k, k:]

    return L, U, piv


def resolver_lu(L, U, piv, b):
    """Resuelve A x = b usando la factorización P A = L U (sust. directa e inversa)."""
    n = len(b)
    b = np.array(b, dtype=float)
    pb = b[piv]                       # aplicar permutación P b
    # Sustitución hacia adelante: L y = Pb
    y = np.zeros(n)
    for i in range(n):
        y[i] = pb[i] - np.dot(L[i, :i], y[:i])
    # Sustitución hacia atrás: U x = y
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i + 1:], x[i + 1:])) / U[i, i]
    return x


def potencia_inversa(A, sigma=0.0, x0=None, tol=1e-10, max_iter=200, norma="inf"):
    """
    MÉTODO DE LA POTENCIA INVERSA.

    Halla el autovalor de A MÁS CERCANO al desplazamiento 'sigma' (y su
    autovector).  Con sigma = 0 obtiene el autovalor de MENOR módulo.

    Idea: si lambda es autovalor de A cercano a sigma, entonces 1/(lambda-sigma)
    es el autovalor DOMINANTE de (A - sigma·I)^{-1}.  Aplicamos la iteración
    de la potencia a esa inversa, pero en vez de invertir resolvemos:

        (A - sigma·I) y_{k} = x_{k-1}        (vía LU, factorizado una sola vez)
        x_{k} = y_{k} / ||y_{k}||            (normalización)
        mu_k  = factor de escala dominante   ->   lambda_k = sigma + 1/mu_k

    Se itera hasta que el autovalor se estabilice (|Δlambda| < tol).

    Devuelve un diccionario con autovalor, autovector, nº de iteraciones,
    convergencia y el detalle por iteración (para tabla y gráficos).
    """
    A = np.array(A, dtype=float)
    n = A.shape[0]
    if A.shape[0] != A.shape[1]:
        raise ValueError("La matriz debe ser cuadrada (orden n x n).")

    # Vector inicial
    if x0 is None:
        x = np.ones(n)
    else:
        x = np.array(x0, dtype=float)
        if x.shape[0] != n:
            raise ValueError("El vector inicial debe tener la misma dimensión que A.")
    if np.linalg.norm(x) == 0:
        x = np.ones(n)

    def normalizar(v):
        if norma == "inf":
            return v / np.max(np.abs(v))
        return v / np.linalg.norm(v)

    x = normalizar(x)

    # Factorizamos B = A - sigma·I  una sola vez.
    B = A - sigma * np.eye(n)
    L, U, piv = lu_pivoteo(B)

    detalle = []
    lambda_ant = None
    historial_lambda = []
    historial_error = []
    convergio = False
    autovalor = None

    for k in range(1, max_iter + 1):
        y = resolver_lu(L, U, piv, x)

        # Factor de escala dominante (componente de mayor módulo de y).
        idx = int(np.argmax(np.abs(y)))
        mu = y[idx]                      # autovalor dominante de B^{-1}
        autovalor = sigma + 1.0 / mu     # autovalor de A

        x_nuevo = normalizar(y)

        # Cociente de Rayleigh: estimación refinada del autovalor de A.
        rayleigh = float((x_nuevo @ (A @ x_nuevo)) / (x_nuevo @ x_nuevo))

        # Error como variación del autovalor entre iteraciones.
        if lambda_ant is None:
            error = np.inf
        else:
            error = abs(autovalor - lambda_ant)

        historial_lambda.append(autovalor)
        historial_error.append(error if np.isfinite(error) else np.nan)
        detalle.append({
            "k": k, "lambda": autovalor, "rayleigh": rayleigh,
            "error": error, "vector": x_nuevo.copy(),
        })

        # Alinear el signo del vector para que sea estable visualmente.
        x = x_nuevo
        if error < tol and lambda_ant is not None:
            convergio = True
            lambda_ant = autovalor
            break
        lambda_ant = autovalor

    # Autovector final normalizado en norma euclídea y con signo canónico
    # (la componente de mayor módulo positiva).
    autovector = x / np.linalg.norm(x)
    idx = int(np.argmax(np.abs(autovector)))
    if autovector[idx] < 0:
        autovector = -autovector

    # Cociente de Rayleigh final (autovalor más preciso).
    rayleigh_final = float((autovector @ (A @ autovector)) / (autovector @ autovector))

    # Residuo  ||A v - lambda v||  como medida de calidad.
    residuo = float(np.linalg.norm(A @ autovector - rayleigh_final * autovector))

    return {
        "autovalor": autovalor,
        "autovalor_rayleigh": rayleigh_final,
        "autovector": autovector,
        "iteraciones": len(detalle),
        "convergio": convergio,
        "residuo": residuo,
        "sigma": sigma,
        "detalle": detalle,
        "historial_lambda": historial_lambda,
        "historial_error": historial_error,
    }


def verificar_autovalores(A):
    """
    Calcula los autovalores/autovectores 'de referencia' con numpy
    (numpy.linalg.eig) para CONTRASTAR el resultado del método propio.
    Sólo se usa como verificación.
    """
    A = np.array(A, dtype=float)
    valores, vectores = np.linalg.eig(A)
    return valores, vectores


def autovalor_de_referencia(A, autovalor):
    """Devuelve el autovalor exacto (numpy) más cercano al hallado por el método."""
    valores, _ = verificar_autovalores(A)
    valores_reales = valores
    idx = int(np.argmin(np.abs(valores_reales - autovalor)))
    return valores[idx], idx


# ===========================================================================
#  Pequeña batería de autocomprobación (se ejecuta con:  python metodos_numericos.py)
# ===========================================================================
if __name__ == "__main__":
    print("== Autocomprobación del núcleo numérico ==\n")

    # --- EDO: y' = y, y(0)=1  ->  solución exacta e^x ---
    f, _ = construir_funcion("y")
    for metodo in (euler_modificado, runge_kutta_4, milne):
        r = metodo(f, 0.0, 1.0, 1.0, 10)
        aprox = r["ys"][-1]
        print(f"{r['nombre']:18}  y(1) ≈ {aprox:.8f}   error vs e = {abs(aprox-np.e):.2e}")

    # --- Interpolación ---
    r = runge_kutta_4(f, 0.0, 1.0, 1.0, 10)
    intp = interpolacion_newton(r["xs"], r["ys"], 0.55, grado=4)
    print(f"\nInterpolación Newton  y(0.55) ≈ {intp['valor']:.8f}   "
          f"(exacto e^0.55 = {np.exp(0.55):.8f})")

    # --- Potencia inversa ---
    A = [[4, 1, 0], [1, 3, 1], [0, 1, 2]]
    res = potencia_inversa(A, sigma=0.0, tol=1e-12)
    vals, _ = verificar_autovalores(A)
    print(f"\nPotencia inversa (menor |λ|): λ ≈ {res['autovalor']:.8f}  "
          f"(referencia: {min(vals, key=abs):.8f})")
    print("Autovector:", np.round(res["autovector"], 6))
    print(f"Residuo ||Av-λv|| = {res['residuo']:.2e}")
    print("\nOK." )
