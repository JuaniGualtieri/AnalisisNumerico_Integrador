# Trabajo Final Integrador — Análisis Numérico (I.S.I.)

Aplicación de escritorio en **Python** que resuelve los dos ejercicios del
Examen Integrador de *Análisis Numérico* (Ing. en Sistemas de Información —
Universidad de la Cuenca del Plata).

Incluye una interfaz gráfica moderna (modo claro/oscuro), procedimiento paso a
paso en tablas y gráficos interactivos.

---

## ✨ ¿Qué hace?

### Ejercicio 1 — E.D.O. de primer orden + Interpolación
Resuelve un problema de valores iniciales

> y ′ = f(x, y),  con  y(a) = y₀,  en el intervalo [a, b]

y luego **interpola** el valor `y(x₀)` para un `x₀` interior al intervalo.

- **Métodos de resolución:** Euler Modificado · Runge-Kutta de 4º orden · Milne.
- **Paso:** `h = (b − a) / n` (una fracción de la longitud del intervalo).
- **Interpolación:** Newton (diferencias divididas) o Lagrange.
- Compara con la **solución exacta** (cuando puede obtenerse) y muestra el error.
- Grafica la solución, los nodos calculados, el polinomio interpolante y el
  punto `(x₀, y(x₀))`.

### Ejercicio 2 — Autovalor y autovector por Potencia Inversa
Dada una matriz cuadrada de orden *n*, halla **un autovalor y su autovector**
mediante el **método de la potencia inversa**.

- Permite un **desplazamiento σ**: encuentra el autovalor más cercano a σ
  (con σ = 0 obtiene el de **menor módulo**).
- Usa **factorización LU con pivoteo parcial** (se factoriza una sola vez y se
  reutiliza en cada iteración).
- Muestra la **tabla de iteraciones**, la **curva de convergencia** y una
  **verificación** contra `numpy.linalg.eig`.

---

## ▶️ Cómo ejecutar

### Opción A — Desde el código fuente (recomendado para desarrollar)
1. Instalar Python 3.10+ (en Windows, marcar *Add Python to PATH*).
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar:
   ```bash
   python main.py
   ```
   o hacer doble clic en **`Ejecutar.bat`**.

### Opción B — Generar un ejecutable `.exe` (un solo archivo)
Hacer doble clic en **`Construir_EXE.bat`** (o ejecutarlo en consola). Al
terminar, el ejecutable queda en:
```
dist\AnalisisNumerico_Integrador.exe
```
Ese `.exe` se puede abrir en cualquier Windows **sin tener Python instalado**.

---

## 🧮 Fundamento matemático (resumen)

### Euler Modificado (predictor-corrector)
```
Predictor:  y* = yᵢ + h · f(xᵢ, yᵢ)
Corrector:  yᵢ₊₁ = yᵢ + (h/2) · [ f(xᵢ, yᵢ) + f(xᵢ₊₁, y*) ]   (se itera)
```
Orden global O(h²).

### Runge-Kutta 4 (RK4)
```
k₁ = f(xᵢ, yᵢ)
k₂ = f(xᵢ + h/2, yᵢ + h/2·k₁)
k₃ = f(xᵢ + h/2, yᵢ + h/2·k₂)
k₄ = f(xᵢ + h,   yᵢ + h·k₃)
yᵢ₊₁ = yᵢ + (h/6)·(k₁ + 2k₂ + 2k₃ + k₄)
```
Orden global O(h⁴).

### Milne (multipaso, arranque con RK4)
```
Predictor:  y*ᵢ₊₁ = yᵢ₋₃ + (4h/3)·(2fᵢ₋₂ − fᵢ₋₁ + 2fᵢ)
Corrector:  yᵢ₊₁  = yᵢ₋₁ + (h/3)·(fᵢ₋₁ + 4fᵢ + fᵢ₊₁)   (se itera)
```
Orden global O(h⁴). Requiere `n ≥ 4`.

### Interpolación de Newton (diferencias divididas)
```
P(x) = f[x₀] + f[x₀,x₁](x−x₀) + f[x₀,x₁,x₂](x−x₀)(x−x₁) + …
```

### Interpolación de Lagrange
```
P(x) = Σ yᵢ · Lᵢ(x),   Lᵢ(x) = Π_{j≠i} (x − xⱼ)/(xᵢ − xⱼ)
```

### Método de la Potencia Inversa
Si `λ` es el autovalor de `A` más cercano a `σ`, entonces `1/(λ−σ)` es el
autovalor **dominante** de `(A − σI)⁻¹`. Se aplica la iteración de la potencia
a esa inversa, resolviendo en cada paso (con LU) en vez de invertir:
```
(A − σI) · yₖ = xₖ₋₁
xₖ = yₖ / ‖yₖ‖
λ ≈ σ + 1/μ   (μ = factor de escala dominante)
```
El autovalor se refina con el **cociente de Rayleigh** `λ = (xᵀAx)/(xᵀx)`.

---

## 📁 Estructura del proyecto

| Archivo                 | Contenido                                                      |
|-------------------------|---------------------------------------------------------------|
| `main.py`               | Punto de entrada y ventana principal (pestañas, tema, etc.)   |
| `metodos_numericos.py`  | **Núcleo matemático**: EDO, interpolación, LU, potencia inversa |
| `vista_edo.py`          | Interfaz del Ejercicio 1 (EDO + interpolación)                |
| `vista_potencia.py`     | Interfaz del Ejercicio 2 (potencia inversa)                   |
| `componentes.py`        | Widgets reutilizables (tarjetas, campos, tablas, tooltips)    |
| `tema.py`               | Paleta de colores y estilos (claro/oscuro)                    |
| `requirements.txt`      | Dependencias                                                   |
| `Ejecutar.bat`          | Lanza la app desde el código                                  |
| `Construir_EXE.bat`     | Genera el ejecutable `.exe` con PyInstaller                   |

> Para verificar el núcleo matemático por separado:
> `python metodos_numericos.py`

---

## 🛠️ Tecnologías
Python 3 · CustomTkinter · Matplotlib · NumPy · SymPy

---

*Universidad de la Cuenca del Plata — Análisis Numérico — I.S.I.*
