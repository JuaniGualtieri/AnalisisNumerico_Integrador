# 🎤 Guion de Exposición — Trabajo Final Integrador de Análisis Numérico



## 👥 División del trabajo (5 integrantes)

| # | Persona | Tema | Qué muestra | Tiempo |
|---|---------|------|-------------|--------|
| 1 | **Introducción** | Consignas, qué construimos, arquitectura, tecnologías | Pestaña **Inicio** + `README.md` + estructura de archivos | 3 min |
| 2 | **Ejercicio 1 – Parte A** | Teoría de EDO + Euler Modificado + Runge-Kutta 4 | `metodos_numericos.py` (funciones de EDO) | 4 min |
| 3 | **Ejercicio 1 – Parte B** | Milne + Interpolación (Newton y Lagrange) + **DEMO** | `metodos_numericos.py` + pestaña **EDO + Interpolación** | 4 min |
| 4 | **Ejercicio 2 – Parte A** | Autovalores, método de la Potencia Inversa + LU | `metodos_numericos.py` (LU y potencia inversa) | 4 min |
| 5 | **Ejercicio 2 – Parte B** | **DEMO** + verificación con NumPy + conclusiones | Pestaña **Potencia Inversa** | 4 min |

> 💡 **Consejo de coordinación:** las personas 3 y 5 son las que hacen la
> *demostración en vivo*, así que conviene que sean quienes mejor manejen la
> app. Las personas 2 y 4 explican la teoría "dura" (los métodos), así que
> conviene que sean quienes más cómodos estén con la matemática.

---

# 🟦 PARTE 1 — Introducción (Persona 1)

### Qué mostrar
1. Abrir la app → quedarse en la pestaña **🏠 Inicio**.
2. Tener a mano el `README.md` y la lista de archivos del proyecto.

### Guion hablado
> *"Buenas. Nuestro trabajo integrador resuelve los **dos ejercicios** que pidió
> la cátedra, pero en lugar de scripts sueltos armamos **una sola aplicación de
> escritorio en Python** con interfaz gráfica, gráficos y el procedimiento paso
> a paso.*
>
> *El **primer ejercicio** pide resolver una **ecuación diferencial ordinaria de
> primer orden** —es decir, una ecuación de la forma `y' = f(x, y)` con un valor
> inicial `y(a)` conocido— y aproximar la solución en un intervalo `[a, b]`.
> Después hay que **interpolar** el valor de la solución en un punto `x₀` que
> elige el usuario.*
>
> *El **segundo ejercicio** pide hallar **un autovalor y su autovector** de una
> matriz de orden `n`, usando específicamente el **método de la potencia
> inversa**.*
>
> *Para que sea ordenado, separamos el proyecto en dos capas:* (mostrar la tabla
> de archivos del README) *por un lado el **núcleo matemático**, que es el
> archivo `metodos_numericos.py` donde están programados todos los métodos desde
> cero, sin usar funciones mágicas que resuelvan todo solas; y por otro lado la
> **interfaz**, repartida en `main.py` y las dos vistas. Esto nos permite
> probar la matemática por separado: de hecho tenemos un archivo `pruebas.py`
> que verifica automáticamente que cada método dé el resultado correcto.*
>
> *Las tecnologías que usamos son: **Python** como lenguaje, **NumPy** para el
> cálculo con matrices, **SymPy** para interpretar la ecuación que escribe el
> usuario, **Matplotlib** para los gráficos y **CustomTkinter** para la interfaz.*
>
> *Ahora [nombre de la persona 2] va a explicar cómo resolvimos el primer
> ejercicio."*

---

# 🟦 PARTE 2 — Ejercicio 1: EDO + métodos de un paso (Persona 2)

### Qué mostrar
- `metodos_numericos.py`, funciones **`euler_modificado`** y **`runge_kutta_4`**.

### Guion hablado
> *"El primer ejercicio es un **problema de valores iniciales**. Tenemos la
> derivada `y' = f(x, y)`, sabemos cuánto vale `y` en el extremo inicial `a`, y
> queremos reconstruir la curva solución avanzando de a pasitos. El tamaño del
> paso es `h = (b − a) / n`, o sea dividimos el intervalo en `n` partes iguales.*
>
> *El primer método que programamos es el **Euler Modificado**, también llamado
> predictor-corrector o método de Heun.* (mostrar la función `euler_modificado`)
> *La idea es: primero hacemos una **predicción** con el método de Euler común
> —avanzamos usando la pendiente en el punto actual—; eso nos da un valor
> aproximado `y*`. Después lo **corregimos** promediando la pendiente del punto
> inicial con la pendiente en el punto de llegada. Esa corrección se puede
> repetir varias veces hasta que el valor se estabilice; por eso en el código hay
> un pequeño bucle interno que itera el corrector hasta que la diferencia sea
> menor que una tolerancia. Este método tiene un **error de orden h²**.*
>
> *El segundo método es **Runge-Kutta de cuarto orden**, que es el más usado en
> la práctica por su precisión.* (mostrar la función `runge_kutta_4`) *En vez de
> una sola pendiente, calcula **cuatro pendientes** dentro del paso: una al
> principio (`k1`), dos en el punto medio (`k2` y `k3`) y una al final (`k4`).
> Después combina esas cuatro pendientes con un promedio ponderado, donde las
> del medio pesan el doble. El resultado es un método con **error de orden h⁴**:
> si achicamos el paso a la mitad, el error se reduce unas dieciséis veces.*
>
> *Para que se note la diferencia: con el mismo paso, en el ejemplo `y' = y`
> Euler Modificado nos da un error de orden 10⁻³ y Runge-Kutta de orden 10⁻⁶.
> Ahora [persona 3] sigue con el tercer método y la interpolación."*

### Apoyo teórico 
```
Euler Modificado:
   Predictor:  y* = yᵢ + h·f(xᵢ, yᵢ)
   Corrector:  yᵢ₊₁ = yᵢ + (h/2)·[ f(xᵢ,yᵢ) + f(xᵢ₊₁, y*) ]     → O(h²)

Runge-Kutta 4:
   k1 = f(xᵢ, yᵢ)
   k2 = f(xᵢ + h/2, yᵢ + h/2·k1)
   k3 = f(xᵢ + h/2, yᵢ + h/2·k2)
   k4 = f(xᵢ + h,   yᵢ + h·k3)
   yᵢ₊₁ = yᵢ + (h/6)·(k1 + 2k2 + 2k3 + k4)                       → O(h⁴)
```

---

# 🟦 PARTE 3 — Ejercicio 1: Milne, interpolación y DEMO (Persona 3)

### Qué mostrar
1. `metodos_numericos.py`, función **`milne`** y las de **interpolación**.
2. **DEMO** en la pestaña **📈 EDO + Interpolación**.

### Guion hablado — Milne
> *"El tercer método es el de **Milne**, que es **multipaso**: en vez de usar
> solo el punto anterior, usa los **cuatro puntos anteriores** para predecir el
> siguiente. El problema es que al principio no tenemos esos cuatro puntos, así
> que el método **arranca con Runge-Kutta** para calcular los primeros tres y
> recién después aplica las fórmulas de Milne.* (mostrar la función `milne`)
> *Milne también es predictor-corrector: el predictor usa una fórmula con los
> puntos anteriores y el corrector usa la **regla de Simpson**. Es de orden h⁴
> como Runge-Kutta, y por eso pedimos que `n` sea al menos 4."*

### Guion hablado — Interpolación
> *"Una vez que tenemos la solución en los puntos de la malla `x₀, x₁, …, xₙ`,
> falta lo que pide la consigna: el valor en un punto `x₀` cualquiera que
> normalmente **no cae justo** en la malla. Para eso interpolamos, con dos
> métodos a elección.*
>
> *El de **Newton por diferencias divididas** arma una tabla triangular de
> diferencias y con eso construye el polinomio que pasa por los puntos.* (mostrar
> `interpolacion_newton`) *El de **Lagrange** combina los valores con unos pesos
> que valen 1 en su nodo y 0 en los demás.* (mostrar `interpolacion_lagrange`)
> *Para evitar que el polinomio oscile —el llamado fenómeno de Runge— no usamos
> todos los puntos sino una **ventana de nodos cercanos a x₀**."*

### DEMO 
1. Pestaña **EDO + Interpolación**. Dejar el ejemplo `y' = x + y`.
2. Decir: *"acá cargamos la ecuación, el intervalo, la condición inicial, el
   número de pasos y el punto x₀ a interpolar"*.
3. Elegir método **Runge-Kutta 4** y apretar **Calcular**.
4. Mostrar la pestaña **📋 Aproximaciones**: *"esta es la tabla con el valor en
   cada paso; en Runge-Kutta se ven las cuatro pendientes k1 a k4, y como esta
   ecuación tiene solución exacta, comparamos y mostramos el error real."*
5. Mostrar **🔢 Interpolación**: *"acá está la tabla de diferencias divididas y
   el resultado y(x₀)."*
6. Mostrar **📊 Gráfico** (ver machete de gráficos en el anexo).
7. *"Ahora [persona 4] explica el segundo ejercicio."*

---

# 🟦 PARTE 4 — Ejercicio 2: Potencia Inversa + LU (Persona 4)

### Qué mostrar
- `metodos_numericos.py`, funciones **`lu_pivoteo`**, **`resolver_lu`** y
  **`potencia_inversa`**.

### Guion hablado
> *"El segundo ejercicio es de **álgebra lineal**: dada una matriz, queremos un
> **autovalor** y su **autovector**. Recordemos que un autovector es un vector
> que, al multiplicarlo por la matriz, no cambia de dirección, solo se estira o
> encoge; cuánto se estira es el autovalor.*
>
> *El método clásico de la **potencia** encuentra el autovalor **más grande** en
> módulo. Pero la consigna pide el método de la **potencia inversa**, que es un
> truco muy elegante: si en lugar de la matriz `A` trabajamos con su **inversa**,
> el autovalor más chico de `A` se transforma en el más grande de la inversa. Y
> generalizando con un **desplazamiento σ**, podemos buscar el autovalor más
> cercano a cualquier número que queramos. Con σ = 0 obtenemos el de **menor
> módulo**.*
>
> *Ahora, invertir una matriz en cada iteración sería carísimo. El truco que
> usamos es que **en vez de invertir, resolvemos un sistema de ecuaciones** en
> cada paso. Y para resolverlo rápido usamos la **factorización LU con pivoteo
> parcial**, que descompone la matriz en una triangular inferior `L` y una
> superior `U`.* (mostrar `lu_pivoteo`) *Lo bueno es que esta factorización se
> calcula **una sola vez** y se reutiliza en todas las iteraciones, porque la
> matriz no cambia; solo cambia el vector del lado derecho.* (mostrar
> `resolver_lu`: sustitución hacia adelante y hacia atrás)
>
> *Entonces el método queda así:* (mostrar `potencia_inversa`) *partimos de un
> vector inicial, en cada iteración resolvemos `(A − σI)·y = x`, normalizamos el
> resultado, y estimamos el autovalor. Iteramos hasta que el autovalor se
> estabilice por debajo de la tolerancia. Al final refinamos el resultado con el
> **cociente de Rayleigh**, que es la mejor estimación del autovalor dado un
> autovector, y calculamos el **residuo** `‖A·v − λ·v‖` para medir qué tan bueno
> es el resultado. Ahora [persona 5] lo muestra funcionando."*

### Apoyo teórico
```
Idea:  λ cercano a σ  ⇔  1/(λ−σ) es el autovalor DOMINANTE de (A − σI)⁻¹.

Iteración:
   Resolver (con LU):   (A − σI)·yₖ = xₖ₋₁
   Normalizar:          xₖ = yₖ / ‖yₖ‖
   Estimar:             λ ≈ σ + 1/μ     (μ = factor de escala dominante)
Refinamiento:           λ = (xᵀ A x)/(xᵀ x)   (cociente de Rayleigh)
```

---

# 🟦 PARTE 5 — Ejercicio 2: DEMO, verificación y conclusiones (Persona 5)

### Qué mostrar
- **DEMO** en la pestaña **🧮 Potencia Inversa**.

### DEMO (hacerlo mientras se habla)
1. Pestaña **Potencia Inversa**. Dejar el ejemplo de orden 3 (botón **Ejemplo**).
2. *"Cargamos la matriz; se puede escribir a mano, usar un ejemplo o generar una
   aleatoria. Dejamos σ = 0 para buscar el autovalor de menor módulo."*
3. Apretar **Calcular**.
4. Mostrar el **resumen de arriba**: autovalor, autovector, residuo.
5. Pestaña **📋 Iteraciones**: *"acá se ve cómo en cada iteración el autovalor se
   va estabilizando y el error baja."*
6. Pestaña **📈 Convergencia**: explicar los dos gráficos (ver machete).
7. Pestaña **🔎 Verificación**: *"acá comparamos nuestro resultado con la función
   `numpy.linalg.eig`, que calcula todos los autovalores de otra forma. Como ven,
   coincide, y la coincidencia de autovectores da un coseno prácticamente 1, o
   sea el mismo vector."*
8. **Cambiar σ** (por ejemplo a 5) y recalcular: *"si cambiamos el
   desplazamiento, el método encuentra otro autovalor, el más cercano a 5. Esto
   muestra la flexibilidad del método."*

### Conclusiones 
> *"Para cerrar: implementamos **los tres métodos de resolución de EDO** que
> daba la cátedra —Euler Modificado, Runge-Kutta y Milne—, las **dos
> interpolaciones**, y el **método de la potencia inversa** con factorización
> LU, todo programado desde cero y verificado contra soluciones exactas y contra
> NumPy. Comprobamos en la práctica lo que dice la teoría: que Runge-Kutta y
> Milne son mucho más precisos que Euler, y que la potencia inversa recupera el
> autovalor con un residuo prácticamente nulo. Muchas gracias."*

---

# 📎 ANEXO A — Preguntas probables 

**¿Por qué el corrector se itera en Euler Modificado y en Milne?**
> Porque el corrector usa la pendiente en el punto de llegada, que todavía no
> conocemos con exactitud. Al repetir el cálculo, el valor converge al punto fijo
> de la fórmula y mejora la precisión. Cortamos cuando la diferencia es menor que
> la tolerancia.

**¿Por qué Milne arranca con Runge-Kutta?**
> Porque es un método multipaso: necesita 4 valores iniciales para empezar, y
> solo tenemos 1 (la condición inicial). Los otros 3 los generamos con RK4.

**¿Qué pasa si el paso h es muy grande?**
> El error crece y los métodos pueden volverse inestables. Por eso conviene un
> `n` razonable. Se puede mostrar en vivo subiendo y bajando `n`.

**¿Por qué LU y no calcular la inversa?**
> Calcular la inversa es más costoso y numéricamente menos estable. Con LU
> factorizamos una sola vez y cada iteración solo cuesta dos sustituciones
> (adelante y atrás), que son muy baratas.

**¿Para qué sirve el pivoteo parcial?**
> Para evitar dividir por números muy chicos (o por cero), lo que dispararía los
> errores de redondeo. Se intercambian filas para usar siempre el pivote más
> grande.

**¿Qué es el cociente de Rayleigh?**
> Es la mejor estimación del autovalor a partir de un autovector aproximado:
> `λ = (xᵀAx)/(xᵀx)`. Lo usamos para refinar el resultado final.

**¿Qué garantiza que el resultado es correcto?**
> El **residuo** `‖A·v − λ·v‖`: si es prácticamente cero, el par (λ, v) cumple la
> definición de autovalor/autovector. Además lo verificamos con `numpy.linalg.eig`.

**¿Por qué a veces no hay solución exacta para comparar?**
> Porque no toda EDO tiene solución analítica en términos elementales. Cuando
> SymPy no puede resolverla, simplemente mostramos la aproximación numérica sin
> la curva exacta.

---

# 📎 ANEXO B — gráficos 

### Gráfico del Ejercicio 1 (pestaña 📊 Gráfico)
- **Línea verde** → solución exacta (cuando existe). Es la referencia "real".
- **Puntos azules** → las aproximaciones que calculó el método en cada paso.
- **Línea naranja punteada** → el polinomio interpolante alrededor de x₀.
- **Estrella roja** → el valor interpolado `y(x₀)`, lo que pide la consigna.
- **Línea roja vertical punteada** → marca la posición de x₀.
> *"Lo importante es que los puntos azules caen prácticamente sobre la curva
> verde: eso muestra que la aproximación es muy buena."*

### Gráficos del Ejercicio 2 (pestaña 📈 Convergencia)
- **Gráfico de arriba** → cómo el autovalor estimado (líneas azul y naranja) se
  acerca al valor de referencia (línea verde punteada) iteración tras iteración.
- **Gráfico de abajo (escala logarítmica)** → cómo el error entre iteraciones
  cae rápidamente; en escala log, una caída en línea recta indica convergencia
  geométrica (muy rápida).
> *"Se ve que en pocas iteraciones el autovalor ya se estabilizó."*





*Universidad de la Cuenca del Plata — Análisis Numérico — I.S.I.*
