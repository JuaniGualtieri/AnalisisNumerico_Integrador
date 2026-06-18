# -*- coding: utf-8 -*-
"""
============================================================================
  metodos_numericos.py  --  "La calculadora" del programa
============================================================================
Este archivo es el CEREBRO matemático del trabajo. Acá están programados, paso
a paso y "a mano" (sin usar funciones mágicas que resuelvan todo solas), los
métodos que pide la cátedra. La interfaz (las ventanas, botones y gráficos)
está en otros archivos; este se encarga SOLO de los cálculos.

¿Qué problemas resolvemos?

  EJERCICIO 1 — Resolver una ecuación diferencial y luego interpolar.
     Tenemos una ecuación de la forma  y' = f(x, y)  (conocemos la "pendiente"
     de la curva en cada punto) y sabemos cuánto vale y en el inicio: y(a).
     Con eso reconstruimos la curva solución avanzando de a pasitos. Lo hacemos
     con tres métodos a elección:
        * Euler Modificado  (el más simple)
        * Runge-Kutta 4     (el más usado, muy preciso)
        * Milne             (usa varios puntos anteriores)
     Después calculamos el valor de la curva en un punto x0 cualquiera que
     elija el usuario, usando interpolación de Newton o de Lagrange.

  EJERCICIO 2 — Hallar un autovalor y su autovector de una matriz.
     Lo hacemos con el método de la POTENCIA INVERSA, que por dentro necesita
     resolver un sistema de ecuaciones en cada paso; para eso usamos la
     factorización LU.

Idea importante: casi todas las funciones devuelven, además del resultado, un
"detalle" paso a paso. Eso es lo que después la interfaz muestra en las tablas
y los gráficos.


============================================================================
"""

from __future__ import annotations

import numpy as np

# SymPy es una librería de matemática simbólica. La usamos para UNA sola cosa
# opcional: cuando la ecuación tiene una solución "exacta" conocida, SymPy la
# calcula y así podemos mostrar qué tan lejos quedó nuestra aproximación (el
# error real). Si SymPy no estuviera instalado, el programa igual funciona.
try:
    import sympy as sp
    HAY_SYMPY = True
except Exception:  # pragma: no cover
    HAY_SYMPY = False


# ===========================================================================
#  1) ENTENDER LA ECUACIÓN QUE ESCRIBE EL USUARIO  ( y' = f(x, y) )
# ===========================================================================

# Lista de ecuaciones de ejemplo que aparecen en el menú desplegable.
# Cada una guarda: el texto de la ecuación y unos valores sugeridos
# (intervalo [a, b], valor inicial y0 y punto a interpolar x0).
# Elegimos a propósito ecuaciones con solución exacta conocida, para poder
# comparar y mostrar el error.
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


# Operaciones matemáticas que el usuario tiene permitido usar al escribir la
# ecuación (senos, cosenos, exponencial, raíz, etc.). Usamos las versiones de
# numpy porque permiten calcular sobre muchos puntos a la vez.
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
    Convierte el TEXTO que escribe el usuario (por ejemplo "x + y" o "x*sin(y)")
    en una función de Python que la computadora puede calcular con números.


    Lo hace de forma SEGURA: revisa que el texto use solamente x, y y las
    funciones matemáticas de la lista de arriba, y bloquea el acceso a cualquier
    otra cosa. 

    Devuelve dos cosas:
        * f    -> la función lista para usar, que se llama como f(x, y)
        * texto -> la misma expresión original (para mostrarla en pantalla)
    """
    # Comodidad: en matemática se escribe "x^2", pero en Python la potencia es
    # "x**2". Cambiamos el ^ por ** para que el usuario pueda usar cualquiera.
    expr_norm = expresion.replace('^', '**')

    # Pre-compilamos el texto. Si está mal escrito, avisamos con un mensaje claro.
    try:
        codigo = compile(expr_norm, "<ecuacion>", "eval")
    except SyntaxError as err:
        raise ValueError(f"La ecuación «{expresion}» tiene un error de sintaxis.\n{err}")

    # Control de seguridad: recorremos todos los "nombres" que aparecen en la
    # expresión y nos aseguramos de que sean válidos (x, y o una función permitida).
    for nombre in codigo.co_names:
        if nombre not in _FUNCIONES_PERMITIDAS and nombre not in ('x', 'y'):
            raise ValueError(
                f"Nombre no permitido en la ecuación: «{nombre}».\n"
                "Use sólo x, y y funciones como sin, cos, exp, log, sqrt, ...")

    # Preparamos el "entorno" con las funciones permitidas y SIN las funciones
    # internas de Python (__builtins__ vacío) para que la evaluación sea segura.
    entorno_base = dict(_FUNCIONES_PERMITIDAS)
    entorno_base['__builtins__'] = {}

    # Esta es la función que vamos a devolver: recibe x e y y calcula el resultado.
    def f(xv, yv):
        entorno = dict(entorno_base)
        entorno['x'] = xv
        entorno['y'] = yv
        return float(eval(codigo, entorno))

    # Probamos evaluar la ecuación en algunos puntos para detectar errores graves
    # temprano (por ej. una función mal usada). Un error puntual de aritmética
    # (dividir por cero justo en un punto, etc.) no invalida la ecuación: puede
    # no ocurrir en los puntos que realmente vamos a usar.
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
    Intenta encontrar la solución EXACTA de la
    ecuación, usando SymPy; si la
    conseguimos, podemos mostrar qué tan cerca quedó nuestra aproximación.

    Devuelve:
        * la función exacta y la fórmula de la solución, SI se pudo calcular;
        * (None, None) si la ecuación no tiene solución sencilla o falla algo.
    """
    if not HAY_SYMPY:
        return None, None
    try:
        x = sp.symbols('x')
        y = sp.Function('y')
        # Volvemos a leer la ecuación pero tratando a "y" como una función y(x),
        # que es lo que SymPy necesita para resolver una ecuación diferencial.
        ysim = sp.symbols('y')
        permitidos = {
            'x': x, 'y': ysim,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'ln': sp.log, 'sqrt': sp.sqrt,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'pi': sp.pi, 'e': sp.E,
        }
        expr = sp.sympify(expresion, locals=permitidos).subs(ysim, y(x))
        # Planteamos  y'(x) = f(x, y)  y la resolvemos con la condición y(a)=y0.
        ode = sp.Eq(y(x).diff(x), expr)
        sol = sp.dsolve(ode, y(x), ics={y(a): y0})
        rhs = sol.rhs
        if rhs.free_symbols - {x}:
            return None, None  # quedaron constantes sin determinar: no sirve
        # Convertimos la fórmula simbólica en una función numérica para graficar.
        f_exact = sp.lambdify(x, rhs, modules=['numpy'])
        return f_exact, rhs
    except Exception:
        return None, None


# ===========================================================================
#  2) LOS TRES MÉTODOS PARA RESOLVER LA ECUACIÓN DIFERENCIAL
#
#  Los tres reciben lo mismo:
#     f  -> la pendiente y' = f(x, y)
#     a, b -> el intervalo donde buscamos la solución
#     y0 -> el valor conocido al inicio, y(a)
#     n  -> en cuántos pasos dividimos el intervalo  (el paso es h = (b-a)/n)
#
#  Y los tres devuelven un diccionario con:
#     'xs'    -> los puntos x donde calculamos        (lista)
#     'ys'    -> la aproximación de y en cada x        (lista)  ← RESULTADO
#     'h'     -> el tamaño del paso
#     'pasos' -> el detalle de cómo se obtuvo cada valor (para la tabla)
#     'nombre'-> el nombre del método
# ===========================================================================

def euler_modificado(f, a, b, y0, n, tol=1e-10, max_corr=50):
    """
    EULER MODIFICADO — el más simple de los tres.

    La idea es que para pasar de un punto al siguiente lo hacemos en dos
    etapas.
        1) PREDECIMOS a dónde llegaríamos usando la pendiente del punto actual.
        2) CORREGIMOS esa estimación promediando la pendiente de DONDE
           ESTÁBAMOS con la pendiente de DONDE LLEGAMOS. Esa corrección se
           repite unas pocas veces hasta que el valor casi no cambia.

    Es el menos preciso de los tres (su error es del orden de h²: si achicamos
    el paso a la mitad, el error baja aproximadamente 4 veces).
    """
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]      # los puntos x: a, a+h, a+2h, ...
    ys = [0.0] * (n + 1)                          # acá guardamos las y aproximadas
    ys[0] = y0                                    # el primer valor lo conocemos
    pasos = []                                    # detalle para mostrar en la tabla

    for i in range(n):
        xi, yi = xs[i], ys[i]
        fi = f(xi, yi)                            # pendiente en el punto actual
        # 1) Predicción (un paso de Euler común)
        y_pred = yi + h * fi
        # 2) Corrección: promediamos las pendientes y repetimos hasta estabilizar
        y_corr = y_pred
        n_iter = 0
        for _ in range(max_corr):
            n_iter += 1
            y_nuevo = yi + (h / 2.0) * (fi + f(xs[i + 1], y_corr))
            if abs(y_nuevo - y_corr) < tol:      # ya casi no cambia: cortamos
                y_corr = y_nuevo
                break
            y_corr = y_nuevo
        ys[i + 1] = y_corr                        # guardamos el valor corregido
        pasos.append({
            "i": i, "x": xi, "y": yi, "f": fi,
            "predictor": y_pred, "corrector": y_corr,
            "iter_corr": n_iter, "x_sig": xs[i + 1], "y_sig": y_corr,
        })

    return {"nombre": "Euler Modificado", "xs": xs, "ys": ys, "h": h, "pasos": pasos}


def runge_kutta_4(f, a, b, y0, n):
    """
    RUNGE-KUTTA 4 — el método más usado en la práctica.

    La idea es que en lugar de mirar la pendiente en un solo lugar, mira
    CUATRO pendientes dentro de cada paso —una al principio, dos en el medio y
    una al final— y las combina con un promedio en el que las del medio pesan
    más. Con eso logra muchísima precisión.

    Su error es del orden de h⁴: si achicamos el paso a la mitad, el error baja
    unas 16 veces. Por eso suele dar resultados casi perfectos.
    """
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [0.0] * (n + 1)
    ys[0] = y0
    pasos = []

    for i in range(n):
        xi, yi = xs[i], ys[i]
        k1 = f(xi, yi)                          # pendiente al inicio del paso
        k2 = f(xi + h / 2.0, yi + h / 2.0 * k1)  # pendiente en el medio (con k1)
        k3 = f(xi + h / 2.0, yi + h / 2.0 * k2)  # pendiente en el medio (con k2)
        k4 = f(xi + h, yi + h * k3)              # pendiente al final del paso
        # Promedio ponderado: las del medio (k2, k3) cuentan doble.
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
    MILNE — un método "multipaso": usa varios puntos anteriores, no solo el último.

    La idea es que para calcular el siguiente valor se apoya en los CUATRO
    puntos previos. El problema es que al arrancar solo tenemos uno (el inicial),
    así que primero usamos Runge-Kutta para conseguir los primeros tres puntos y
    recién después aplicamos Milne. Como los otros dos métodos buenos, también
    trabaja en dos etapas (predice y después corrige).

    Es tan preciso como Runge-Kutta (error de orden h⁴). Necesita al menos 4
    pasos (n >= 4) para poder arrancar.
    """
    if n < 4:
        raise ValueError("El método de Milne requiere al menos 4 pasos (n >= 4).")

    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [0.0] * (n + 1)
    ys[0] = y0
    pasos = []

    # --- Arranque: usamos Runge-Kutta para los primeros 3 puntos (y1, y2, y3) ---
    arranque = runge_kutta_4(f, a, a + 3 * h, y0, 3)
    for i in range(1, 4):
        ys[i] = arranque["ys"][i]
        pasos.append({
            "i": i, "x": xs[i], "tipo": "RK4 (arranque)",
            "predictor": np.nan, "corrector": ys[i],
            "iter_corr": 0, "y_sig": ys[i],
        })

    # Guardamos la pendiente f en cada punto ya conocido.
    fval = [f(xs[i], ys[i]) for i in range(4)] + [0.0] * (n - 3)

    # --- A partir del cuarto punto ya podemos aplicar Milne ---
    for i in range(3, n):
        # 1) Predicción: fórmula de Milne usando los puntos anteriores
        y_pred = ys[i - 3] + (4.0 * h / 3.0) * (2 * fval[i - 2] - fval[i - 1] + 2 * fval[i])
        # 2) Corrección: fórmula tipo "regla de Simpson", repetida hasta estabilizar
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


# "Catálogo" de métodos: relaciona el nombre que se ve en la interfaz con la
# función que hay que llamar. Así la interfaz no necesita conocer los detalles.
METODOS_EDO = {
    "Euler Modificado": euler_modificado,
    "Runge-Kutta 4": runge_kutta_4,
    "Milne": milne,
}


# ===========================================================================
#  3) INTERPOLACIÓN: estimar el valor de la curva en un punto x0
#
#  Una vez que tenemos la solución en los puntos de la malla (x0, x1, ..., xn),
#  el x0 que pide el usuario casi nunca cae justo en uno de esos puntos. La
#  interpolación construye un polinomio que pasa por los puntos cercanos y lo
#  usa para estimar el valor en el x0 pedido.
# ===========================================================================

def _ventana_nodos(xs, x0, grado):
    """
    Elige qué puntos usar para interpolar: toma un grupo de (grado+1) puntos
    VECINOS a x0. ¿Por qué no usamos todos? Porque un polinomio que pasa por
    muchísimos puntos tiende a "ondularse" y empeora la estimación (es el famoso
    fenómeno de Runge). Usando solo los vecinos, el resultado es más estable.

    Devuelve los índices de inicio y fin del grupo de puntos elegido.
    """
    m = grado + 1
    n = len(xs)
    if m >= n:
        return 0, n  # si pedimos más puntos de los que hay, usamos todos
    # Buscamos el punto de la malla más cercano a x0 y armamos el grupo a su
    # alrededor, cuidando no salirnos de los bordes.
    j = min(range(n), key=lambda k: abs(xs[k] - x0))
    ini = j - m // 2
    ini = max(0, min(ini, n - m))
    return ini, ini + m


def interpolacion_newton(xs, ys, x0, grado=None):
    """
    INTERPOLACIÓN DE NEWTON (por "diferencias divididas").

    La idea es que con los puntos cercanos arma una tabla de "diferencias"
    (cuánto cambia y respecto de x, y cuánto cambian esos cambios, etc.). Con esa
    tabla construye un polinomio que pasa exactamente por los puntos, y lo evalúa
    en x0 para estimar el valor buscado.

    Devuelve un diccionario con:
        'valor'   -> la estimación de y en x0  ← RESULTADO
        'P'       -> el polinomio como función (para dibujarlo)
        'coef'    -> los coeficientes del polinomio
        'tabla'   -> la tabla de diferencias divididas (se muestra en pantalla)
        'xnodos', 'ynodos' -> los puntos que se usaron
        'grado'   -> el grado del polinomio
    """
    n_total = len(xs)
    if grado is None:
        grado = n_total - 1
    grado = max(1, min(grado, n_total - 1))      # acotamos a un grado válido

    ini, fin = _ventana_nodos(xs, x0, grado)     # elegimos los puntos vecinos
    xn = list(xs[ini:fin])
    yn = list(ys[ini:fin])
    m = len(xn)

    # Construimos la tabla de diferencias divididas (una matriz triangular).
    # La primera columna son los valores de y; cada columna siguiente se calcula
    # restando las de la anterior y dividiendo por la distancia entre puntos.
    tabla = [[0.0] * m for _ in range(m)]
    for i in range(m):
        tabla[i][0] = yn[i]
    for j in range(1, m):
        for i in range(m - j):
            tabla[i][j] = (tabla[i + 1][j - 1] - tabla[i][j - 1]) / (xn[i + j] - xn[i])

    # Los coeficientes del polinomio son la primera fila de la tabla.
    coef = [tabla[0][j] for j in range(m)]

    # Esta función arma y evalúa el polinomio (sirve para dibujar la curva).
    def P(x):
        x = np.asarray(x, dtype=float)
        resultado = np.full_like(x, coef[0], dtype=float) if x.ndim else coef[0]
        producto = np.ones_like(x, dtype=float) if x.ndim else 1.0
        for j in range(1, m):
            producto = producto * (x - xn[j - 1])
            resultado = resultado + coef[j] * producto
        return resultado

    valor = float(_eval_escalar(coef, xn, x0))   # el valor que nos interesa: y(x0)

    return {
        "metodo": "Newton (diferencias divididas)",
        "valor": valor, "P": P, "coef": coef,
        "tabla": tabla, "xnodos": xn, "ynodos": yn, "grado": m - 1,
        "rango_nodos": (ini, fin - 1),
    }


def _eval_escalar(coef, xn, x0):
    """Evalúa el polinomio de Newton en un único punto x0 (de forma eficiente)."""
    m = len(coef)
    resultado = coef[0]
    producto = 1.0
    for j in range(1, m):
        producto *= (x0 - xn[j - 1])
        resultado += coef[j] * producto
    return resultado


def interpolacion_lagrange(xs, ys, x0, grado=None):
    """
    INTERPOLACIÓN DE LAGRANGE.

    La idea es que construye el mismo tipo de polinomio que Newton (pasa
    por los puntos cercanos), pero con otra receta. Para cada punto arma una
    "función base" que vale 1 en ese punto y 0 en todos los demás; después suma
    los valores de y multiplicados por esas bases. El resultado en x0 es el mismo
    que con Newton, solo cambia la forma de calcularlo.

    Devuelve un diccionario con:
        'valor'   -> la estimación de y en x0  ← RESULTADO
        'P'       -> el polinomio como función (para dibujarlo)
        'pesos'   -> el aporte de cada punto en el resultado
        'xnodos', 'ynodos' -> los puntos usados
    """
    n_total = len(xs)
    if grado is None:
        grado = n_total - 1
    grado = max(1, min(grado, n_total - 1))

    ini, fin = _ventana_nodos(xs, x0, grado)
    xn = list(xs[ini:fin])
    yn = list(ys[ini:fin])
    m = len(xn)

    # "Función base" L_i: vale 1 en el punto i y 0 en los demás puntos.
    def L(i, x):
        prod = np.ones_like(np.asarray(x, dtype=float))
        for j in range(m):
            if j != i:
                prod = prod * (x - xn[j]) / (xn[i] - xn[j])
        return prod

    # El polinomio completo = suma de cada y multiplicado por su función base.
    def P(x):
        x = np.asarray(x, dtype=float)
        s = np.zeros_like(x, dtype=float)
        for i in range(m):
            s = s + yn[i] * L(i, x)
        return s

    # Calculamos el valor en x0 y, de paso, el "peso" (aporte) de cada punto.
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


# Catálogo de métodos de interpolación (nombre visible -> función).
METODOS_INTERPOLACION = {
    "Newton (dif. divididas)": interpolacion_newton,
    "Lagrange": interpolacion_lagrange,
}


# ===========================================================================
#  4) EJERCICIO 2: AUTOVALOR Y AUTOVECTOR POR LA POTENCIA INVERSA
#
#  Recordatorio rápido: un AUTOVECTOR de una matriz A es un vector que, al
#  multiplicarlo por A, no cambia de dirección (solo se estira o se encoge).
#  Cuánto se estira es el AUTOVALOR. El método de la potencia inversa encuentra
#  uno de esos pares (autovalor, autovector).
# ===========================================================================

def lu_pivoteo(A):
    """
    FACTORIZACIÓN LU con pivoteo parcial. Descompone la matriz A en el producto
    de dos matrices triangulares: una inferior (L) y una superior (U).

    ¿Para qué sirve? Para resolver sistemas de ecuaciones A·x = b rápido. La
    gracia es que la parte "cara" (esta factorización) se hace UNA sola vez, y
    después cada sistema se resuelve en dos pasos sencillos. Esto es clave para
    la potencia inversa, que resuelve un sistema en cada iteración.

    El "pivoteo" es un truco para evitar dividir por números muy chiquitos (que
    arruinarían la precisión): en cada paso se reordena para usar el número más
    grande disponible.

    Devuelve L, U y 'piv' (el reordenamiento de filas que se hizo).
    """
    A = np.array(A, dtype=float)
    n = A.shape[0]
    U = A.copy()
    L = np.eye(n)
    piv = list(range(n))  # lleva el registro de cómo reordenamos las filas

    for k in range(n):
        # Pivoteo: buscamos la fila con el número más grande en esta columna...
        p = k + int(np.argmax(np.abs(U[k:, k])))
        if abs(U[p, k]) < 1e-15:
            raise ValueError("La matriz (A - sigma·I) es singular: elija otro "
                             "desplazamiento sigma.")
        if p != k:
            # ...y la subimos intercambiando filas.
            U[[k, p], :] = U[[p, k], :]
            piv[k], piv[p] = piv[p], piv[k]
            if k > 0:
                L[[k, p], :k] = L[[p, k], :k]
        # Eliminación: hacemos ceros debajo de la diagonal (como en Gauss).
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] -= L[i, k] * U[k, k:]

    return L, U, piv


def resolver_lu(L, U, piv, b):
    """
    Resuelve el sistema A·x = b aprovechando la factorización L y U ya calculada.

    Lo hace en dos pasos muy simples:
        1) "hacia adelante": resuelve L·y = b
        2) "hacia atrás":    resuelve U·x = y
    Como L y U son triangulares, cada despeje es directo. Devuelve la solución x.
    """
    n = len(b)
    b = np.array(b, dtype=float)
    pb = b[piv]                       # reordenamos b según el pivoteo
    # Paso 1 — sustitución hacia adelante (L·y = b)
    y = np.zeros(n)
    for i in range(n):
        y[i] = pb[i] - np.dot(L[i, :i], y[:i])
    # Paso 2 — sustitución hacia atrás (U·x = y)
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i + 1:], x[i + 1:])) / U[i, i]
    return x


def potencia_inversa(A, sigma=0.0, x0=None, tol=1e-10, max_iter=200, norma="inf"):
    """
    MÉTODO DE LA POTENCIA INVERSA — halla un autovalor y su autovector.

    La idea es que: el método clásico de la "potencia" encuentra el
    autovalor MÁS GRANDE de una matriz repitiendo multiplicaciones. Acá usamos
    una variante: trabajando con la INVERSA, encontramos en cambio el autovalor
    MÁS CHICO. Y con un "desplazamiento" sigma podemos buscar el autovalor más
    cercano a cualquier número que queramos (con sigma = 0 sale el de menor módulo).

    El truco para no invertir la matriz (que sería costoso): en cada vuelta
    RESOLVEMOS un sistema de ecuaciones usando la factorización LU, normalizamos
    el vector resultante y estimamos el autovalor. Repetimos hasta que el
    autovalor se estabiliza.

    Devuelve un diccionario con:
        'autovalor', 'autovalor_rayleigh' -> el autovalor hallado (el segundo es
                                             la versión más precisa)  ← RESULTADO
        'autovector'   -> el autovector correspondiente            ← RESULTADO
        'iteraciones'  -> cuántas vueltas necesitó
        'convergio'    -> si llegó a la tolerancia (True) o se quedó sin vueltas
        'residuo'      -> medida de calidad: cuán cerca está de cumplir A·v = λ·v
        'detalle', 'historial_lambda', 'historial_error' -> datos por iteración
                          (para la tabla y los gráficos de convergencia)
    """
    A = np.array(A, dtype=float)
    n = A.shape[0]
    if A.shape[0] != A.shape[1]:
        raise ValueError("La matriz debe ser cuadrada (orden n x n).")

    # Vector inicial: si no nos dan uno, arrancamos con un vector de unos.
    if x0 is None:
        x = np.ones(n)
    else:
        x = np.array(x0, dtype=float)
        if x.shape[0] != n:
            raise ValueError("El vector inicial debe tener la misma dimensión que A.")
    if np.linalg.norm(x) == 0:
        x = np.ones(n)

    # "Normalizar" = reescalar el vector para que no crezca sin control entre
    # vueltas. Se puede usar la norma infinito (el componente más grande) o la
    # euclidiana (la longitud del vector).
    def normalizar(v):
        if norma == "inf":
            return v / np.max(np.abs(v))
        return v / np.linalg.norm(v)

    x = normalizar(x)

    # Construimos B = A - sigma·I y la factorizamos UNA sola vez. En cada
    # iteración reutilizamos esta factorización (esa es la gran ventaja).
    B = A - sigma * np.eye(n)
    L, U, piv = lu_pivoteo(B)

    detalle = []
    lambda_ant = None
    historial_lambda = []
    historial_error = []
    convergio = False
    autovalor = None

    for k in range(1, max_iter + 1):
        # En vez de invertir B, resolvemos  B·y = x.
        y = resolver_lu(L, U, piv, x)

        # El componente más grande de y nos da el "factor de escala", que
        # permite estimar el autovalor de A.
        idx = int(np.argmax(np.abs(y)))
        mu = y[idx]                      # autovalor dominante de la inversa
        autovalor = sigma + 1.0 / mu     # lo convertimos al autovalor de A

        x_nuevo = normalizar(y)

        # Cociente de Rayleigh: una forma más precisa de estimar el autovalor a
        # partir del autovector actual.
        rayleigh = float((x_nuevo @ (A @ x_nuevo)) / (x_nuevo @ x_nuevo))

        # El "error" es cuánto cambió el autovalor respecto de la vuelta anterior.
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

        x = x_nuevo
        # Si el autovalor casi no cambió, ya convergimos: cortamos.
        if error < tol and lambda_ant is not None:
            convergio = True
            lambda_ant = autovalor
            break
        lambda_ant = autovalor

    # Dejamos el autovector "prolijo": longitud 1 y con el componente más grande
    # positivo (así siempre se ve igual y no aparece con el signo cambiado).
    autovector = x / np.linalg.norm(x)
    idx = int(np.argmax(np.abs(autovector)))
    if autovector[idx] < 0:
        autovector = -autovector

    # Estimación final más precisa del autovalor (cociente de Rayleigh).
    rayleigh_final = float((autovector @ (A @ autovector)) / (autovector @ autovector))

    # Residuo = qué tan bien se cumple A·v = λ·v. Si es casi cero, ¡el resultado
    # es correcto! Es nuestra mejor prueba de calidad.
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
    Calcula TODOS los autovalores y autovectores de A con la función ya probada
    de numpy (numpy.linalg.eig). No es parte del método: lo usamos solo para
    CONTRASTAR y demostrar que nuestro resultado es correcto.
    """
    A = np.array(A, dtype=float)
    valores, vectores = np.linalg.eig(A)
    return valores, vectores


def autovalor_de_referencia(A, autovalor):
    """
    De todos los autovalores que calcula numpy, devuelve el que más se parece al
    que encontró nuestro método (para poder compararlos lado a lado).
    """
    valores, _ = verificar_autovalores(A)
    valores_reales = valores
    idx = int(np.argmin(np.abs(valores_reales - autovalor)))
    return valores[idx], idx


# ===========================================================================
#  PRUEBA RÁPIDA: si ejecutás este archivo solo (python metodos_numericos.py)
#  corre una mini-demostración para verificar que todo funciona.
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
