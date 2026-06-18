# -*- coding: utf-8 -*-
"""
============================================================================
  vista_edo.py  --  EJERCICIO 1: E.D.O. de primer orden + Interpolación
============================================================================
Interfaz del primer ejercicio. Permite:
  * ingresar y' = f(x, y), el intervalo [a, b], y(a), el nº de pasos n y x0;
  * resolver con Euler Modificado, Runge-Kutta 4 o Milne;
  * interpolar y(x0) por Newton o Lagrange;
  * ver la tabla de aproximaciones, el detalle de la interpolación y los
    gráficos (solución, nodos, polinomio interpolante y solución exacta).
============================================================================
"""

import tkinter as tk
from tkinter import messagebox

import numpy as np
import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

import tema
import componentes as cp
import metodos_numericos as mn


def fmt(x, dec=6):
    """Formatea un número para mostrarlo en tablas/etiquetas."""
    try:
        if x is None or (isinstance(x, float) and (np.isnan(x))):
            return "—"
        if isinstance(x, float) and np.isinf(x):
            return "∞"
        return f"{x:.{dec}f}"
    except Exception:
        return str(x)


class VistaEDO(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._ultimo = None          # datos del último cálculo (para re-graficar)
        self.tablas = []             # tablas a re-estilizar al cambiar de tema

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_entradas()
        self._construir_panel_resultados()

    # ====================================================================
    #  PANEL IZQUIERDO — ENTRADAS
    # ====================================================================
    def _construir_panel_entradas(self):
        izq = ctk.CTkScrollableFrame(self, fg_color="transparent", width=360)
        izq.grid(row=0, column=0, sticky="ns", padx=(6, 8), pady=6)

        # --- Tarjeta: ecuación y ejemplos ---
        t1 = cp.Tarjeta(izq, "Ecuación diferencial", "📝")
        t1.pack(fill="x", pady=(0, 10))
        c1 = t1.cuerpo()

        ctk.CTkLabel(c1, text="Ejemplos precargados:", font=tema.fuente(12),
                     text_color=tema.TEXTO_TENUE, anchor="w").pack(fill="x")
        self.cmb_ejemplo = ctk.CTkOptionMenu(
            c1, values=list(mn.EJEMPLOS_EDO.keys()),
            command=self._cargar_ejemplo, font=tema.fuente_mono(11),
            fg_color=tema.FONDO_SUAVE, button_color=tema.ACENTO,
            button_hover_color=tema.ACENTO_HOVER, dropdown_font=tema.fuente_mono(11))
        self.cmb_ejemplo.pack(fill="x", pady=(4, 10))

        fila = ctk.CTkFrame(c1, fg_color="transparent")
        fila.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(fila, text="y ′ = ", font=tema.fuente_mono(15, "bold"),
                     text_color=tema.ACENTO).pack(side="left")
        self.ent_f = ctk.CTkEntry(fila, font=tema.fuente_mono(13),
                                  placeholder_text="x + y")
        self.ent_f.pack(side="left", fill="x", expand=True)
        cp.Tooltip(self.ent_f,
                   "Función f(x, y). Operadores: + - * / **\n"
                   "Funciones: sin, cos, tan, exp, log, sqrt, ...\n"
                   "Ejemplos:  x + y   ·   x*y   ·   y*(1-y)   ·   cos(x)")

        # --- Tarjeta: parámetros del intervalo ---
        t2 = cp.Tarjeta(izq, "Datos del problema", "🎯")
        t2.pack(fill="x", pady=(0, 10))
        c2 = t2.cuerpo()
        self.ent_a = cp.campo(c2, "Extremo inicial  a", "0",
                              ayuda="Inicio del intervalo [a, b].")
        self.ent_b = cp.campo(c2, "Extremo final  b", "1",
                              ayuda="Fin del intervalo [a, b].")
        self.ent_y0 = cp.campo(c2, "Condición inicial  y(a)", "1",
                               ayuda="Valor conocido de y en x = a.")
        self.ent_n = cp.campo(c2, "Cantidad de pasos  n", "10",
                              ayuda="El paso es h = (b − a) / n.\n"
                                    "Milne requiere n ≥ 4.")
        self.ent_n.bind("<KeyRelease>", lambda e: self._actualizar_h())
        self.ent_a.bind("<KeyRelease>", lambda e: self._actualizar_h())
        self.ent_b.bind("<KeyRelease>", lambda e: self._actualizar_h())

        self.lbl_h = ctk.CTkLabel(c2, text="h = 0.100000",
                                  font=tema.fuente_mono(12, "bold"),
                                  text_color=tema.EXITO, anchor="w")
        self.lbl_h.pack(fill="x", pady=(4, 0))

        self.ent_x0 = cp.campo(c2, "Punto a interpolar  x₀", "0.55",
                               ayuda="Debe cumplir  a < x₀ < b.")

        # --- Tarjeta: métodos ---
        t3 = cp.Tarjeta(izq, "Métodos numéricos", "⚙️")
        t3.pack(fill="x", pady=(0, 10))
        c3 = t3.cuerpo()
        ctk.CTkLabel(c3, text="Método para la EDO:", font=tema.fuente(12),
                     text_color=tema.TEXTO_TENUE, anchor="w").pack(fill="x")
        self.cmb_metodo = ctk.CTkOptionMenu(
            c3, values=list(mn.METODOS_EDO.keys()),
            font=tema.fuente(12), fg_color=tema.FONDO_SUAVE,
            button_color=tema.ACENTO, button_hover_color=tema.ACENTO_HOVER)
        self.cmb_metodo.set("Runge-Kutta 4")
        self.cmb_metodo.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(c3, text="Método de interpolación:", font=tema.fuente(12),
                     text_color=tema.TEXTO_TENUE, anchor="w").pack(fill="x")
        self.cmb_interp = ctk.CTkOptionMenu(
            c3, values=list(mn.METODOS_INTERPOLACION.keys()),
            font=tema.fuente(12), fg_color=tema.FONDO_SUAVE,
            button_color=tema.ACENTO, button_hover_color=tema.ACENTO_HOVER)
        self.cmb_interp.pack(fill="x", pady=(4, 10))

        self.ent_grado = cp.campo(c3, "Grado del polinomio", "auto", ancho=90,
                                  ayuda="Nº de nodos = grado + 1, tomados alrededor\n"
                                        "de x₀. Escriba 'auto' para elegirlo solo.")

        # --- Botones ---
        botones = ctk.CTkFrame(izq, fg_color="transparent")
        botones.pack(fill="x", pady=(4, 12))
        cp.boton(botones, "Calcular", self.calcular, icono="▶",
                 color=tema.EXITO, hover=tema.EXITO_HOVER).pack(
            fill="x", pady=(0, 6))
        cp.boton(botones, "Limpiar", self.limpiar, icono="🗑",
                 color=tema.FONDO_SUAVE, hover=tema.BORDE).pack(fill="x")

        self._cargar_ejemplo(list(mn.EJEMPLOS_EDO.keys())[0])

    # ====================================================================
    #  PANEL DERECHO — RESULTADOS
    # ====================================================================
    def _construir_panel_resultados(self):
        der = ctk.CTkFrame(self, fg_color="transparent")
        der.grid(row=0, column=1, sticky="nsew", padx=(0, 6), pady=6)
        der.grid_rowconfigure(1, weight=1)
        der.grid_columnconfigure(0, weight=1)

        # Tarjeta resumen (arriba)
        self.tarjeta_res = ctk.CTkFrame(der, fg_color=tema.FONDO_PANEL,
                                        corner_radius=14, border_width=1,
                                        border_color=tema.BORDE)
        self.tarjeta_res.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.lbl_resumen = ctk.CTkLabel(
            self.tarjeta_res,
            text="Cargá los datos y presioná «Calcular» para ver los resultados.",
            font=tema.fuente(14), text_color=tema.TEXTO_TENUE,
            justify="left", anchor="w")
        self.lbl_resumen.pack(fill="x", padx=20, pady=16)

        # Sub-pestañas (gráfico / tabla / interpolación)
        self.subtabs = ctk.CTkTabview(
            der, fg_color=tema.FONDO_PANEL,
            segmented_button_fg_color=tema.FONDO_SUAVE,
            segmented_button_selected_color=tema.ACENTO,
            segmented_button_selected_hover_color=tema.ACENTO_HOVER,
            text_color=tema.TEXTO, corner_radius=12)
        self.subtabs.grid(row=1, column=0, sticky="nsew")

        self.tab_graf = self.subtabs.add("📊  Gráfico")
        self.tab_tabla = self.subtabs.add("📋  Aproximaciones")
        self.tab_interp = self.subtabs.add("🔢  Interpolación")

        self._construir_grafico(self.tab_graf)
        self._construir_tabla(self.tab_tabla)
        self._construir_interp(self.tab_interp)

    def _construir_grafico(self, master):
        cont = ctk.CTkFrame(master, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=6, pady=6)
        self.fig = Figure(figsize=(7, 4.6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        tema.estilizar_figura(self.fig, self.ax)
        self.ax.set_title("Solución de la E.D.O. e interpolación")
        self.canvas = FigureCanvasTkAgg(self.fig, master=cont)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        barra = tk.Frame(cont, bg=tema.colores_grafico()["fondo"])
        barra.pack(fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, barra)
        self.toolbar.update()
        self.fig.tight_layout()
        self.canvas.draw()

    def _construir_tabla(self, master):
        self.cont_tabla = ctk.CTkFrame(master, fg_color="transparent")
        self.cont_tabla.pack(fill="both", expand=True, padx=6, pady=6)
        self.tabla_aprox = None

    def _construir_interp(self, master):
        self.box_interp = ctk.CTkTextbox(master, font=tema.fuente_mono(12),
                                         fg_color=tema.FONDO_PANEL,
                                         text_color=tema.TEXTO, wrap="none")
        self.box_interp.pack(fill="both", expand=True, padx=8, pady=8)
        self.box_interp.insert("1.0", "Aquí se mostrará el detalle de la "
                                       "interpolación (tabla y polinomio).")
        self.box_interp.configure(state="disabled")

    # ====================================================================
    #  EVENTOS / LÓGICA
    # ====================================================================
    def _cargar_ejemplo(self, clave):
        expr, a, b, y0, x0 = mn.EJEMPLOS_EDO[clave]
        self.ent_f.delete(0, "end"); self.ent_f.insert(0, expr)
        self.ent_a.delete(0, "end"); self.ent_a.insert(0, str(a))
        self.ent_b.delete(0, "end"); self.ent_b.insert(0, str(b))
        self.ent_y0.delete(0, "end"); self.ent_y0.insert(0, str(y0))
        self.ent_x0.delete(0, "end"); self.ent_x0.insert(0, str(x0))
        self._actualizar_h()

    def _actualizar_h(self):
        try:
            a = float(self.ent_a.get()); b = float(self.ent_b.get())
            n = int(float(self.ent_n.get()))
            if n > 0 and b != a:
                h = (b - a) / n
                self.lbl_h.configure(text=f"h = (b − a) / n = {h:.6f}")
            else:
                self.lbl_h.configure(text="h = —")
        except Exception:
            self.lbl_h.configure(text="h = —")

    def _leer_datos(self):
        """Lee y valida las entradas; lanza ValueError con mensaje claro."""
        try:
            a = float(self.ent_a.get()); b = float(self.ent_b.get())
        except ValueError:
            raise ValueError("Los extremos a y b deben ser números.")
        if b <= a:
            raise ValueError("Debe cumplirse  a < b.")
        try:
            y0 = float(self.ent_y0.get())
        except ValueError:
            raise ValueError("y(a) debe ser un número.")
        try:
            n = int(float(self.ent_n.get()))
        except ValueError:
            raise ValueError("El número de pasos n debe ser un entero.")
        if n < 1:
            raise ValueError("El número de pasos n debe ser ≥ 1.")
        try:
            x0 = float(self.ent_x0.get())
        except ValueError:
            raise ValueError("x₀ debe ser un número.")
        if not (a < x0 < b):
            raise ValueError(f"x₀ debe estar dentro del intervalo: {a} < x₀ < {b}.")

        metodo = self.cmb_metodo.get()
        if metodo == "Milne" and n < 4:
            raise ValueError("El método de Milne requiere n ≥ 4.")

        grado_txt = self.ent_grado.get().strip().lower()
        grado = None if grado_txt in ("", "auto") else int(float(grado_txt))

        expr = self.ent_f.get().strip()
        if not expr:
            raise ValueError("Ingrese la función f(x, y).")
        return expr, a, b, y0, n, x0, metodo, grado

    def calcular(self):
        try:
            expr, a, b, y0, n, x0, metodo, grado = self._leer_datos()
            f, expr_sym = mn.construir_funcion(expr)

            # Resolver la EDO con el método elegido.
            resultado = mn.METODOS_EDO[metodo](f, a, b, y0, n)
            xs, ys = resultado["xs"], resultado["ys"]

            # Interpolación de y(x0).
            metodo_int = self.cmb_interp.get()
            interp = mn.METODOS_INTERPOLACION[metodo_int](xs, ys, x0, grado)

            # Solución exacta (opcional).
            f_exacta, sol_sym = mn.solucion_exacta(expr, a, y0)

            datos = dict(expr=expr, expr_sym=expr_sym, a=a, b=b, y0=y0, n=n,
                         x0=x0, metodo=metodo, metodo_int=metodo_int,
                         resultado=resultado, interp=interp,
                         f_exacta=f_exacta, sol_sym=sol_sym)
            self._ultimo = datos

            self._mostrar_resumen(datos)
            self._mostrar_tabla(datos)
            self._mostrar_interp(datos)
            self._dibujar(datos)
        except Exception as err:
            messagebox.showerror("Error en los datos", str(err))

    # ---------------------------------------------------------------- resumen
    def _mostrar_resumen(self, d):
        r = d["resultado"]; interp = d["interp"]
        h = r["h"]
        y_x0 = interp["valor"]
        partes = [
            f"Método:  {r['nombre']}      |      h = {fmt(h)}      |      n = {d['n']} pasos",
            f"y({fmt(d['b'])}) ≈ {fmt(r['ys'][-1], 8)}   (último nodo)",
            f"Interpolación ({d['metodo_int']}):   y(x₀ = {fmt(d['x0'])}) ≈ {fmt(y_x0, 8)}",
        ]
        if d["f_exacta"] is not None:
            exacto = float(d["f_exacta"](d["x0"]))
            err = abs(exacto - y_x0)
            partes.append(
                f"Solución exacta:   y(x₀) = {fmt(exacto, 8)}   →   "
                f"error |exacto − interp| = {err:.2e}")
        else:
            partes.append("Solución exacta: no disponible (no se pudo resolver "
                          "analíticamente).")
        self.lbl_resumen.configure(text="\n".join(partes), text_color=tema.TEXTO,
                                   font=tema.fuente_mono(13))

    # ---------------------------------------------------------------- tabla
    def _filas_y_columnas(self, d):
        """Construye columnas y filas de la tabla de aproximaciones según el
        método (incluye el detalle del procedimiento)."""
        r = d["resultado"]; metodo = d["metodo"]
        xs, ys = r["xs"], r["ys"]
        f_ex = d["f_exacta"]
        n = d["n"]

        usa_exacta = f_ex is not None

        if metodo == "Runge-Kutta 4":
            cols = ["i", "xᵢ", "yᵢ", "k1", "k2", "k3", "k4"]
            anchos = [40, 90, 110, 90, 90, 90, 90]
            filas = [(0, fmt(xs[0]), fmt(ys[0], 7), "—", "—", "—", "—")]
            for p in r["pasos"]:
                filas.append((p["i"] + 1, fmt(xs[p["i"] + 1]), fmt(p["y_sig"], 7),
                              fmt(p["k1"], 5), fmt(p["k2"], 5),
                              fmt(p["k3"], 5), fmt(p["k4"], 5)))
        elif metodo == "Euler Modificado":
            cols = ["i", "xᵢ", "yᵢ", "predictor", "corrector", "it"]
            anchos = [40, 100, 120, 120, 120, 50]
            filas = [(0, fmt(xs[0]), fmt(ys[0], 7), "—", "—", "—")]
            for p in r["pasos"]:
                filas.append((p["i"] + 1, fmt(xs[p["i"] + 1]), fmt(p["y_sig"], 7),
                              fmt(p["predictor"], 6), fmt(p["corrector"], 6),
                              p["iter_corr"]))
        else:  # Milne
            cols = ["i", "xᵢ", "yᵢ", "tipo", "predictor", "corrector", "it"]
            anchos = [40, 90, 110, 110, 110, 110, 50]
            filas = [(0, fmt(xs[0]), fmt(ys[0], 7), "inicial", "—", "—", "—")]
            for p in r["pasos"]:
                filas.append((p["i"], fmt(p["x"]), fmt(p["y_sig"], 7),
                              p.get("tipo", ""), fmt(p["predictor"], 6),
                              fmt(p["corrector"], 6), p.get("iter_corr", "")))

        # Añadir columnas de solución exacta y error si están disponibles.
        if usa_exacta:
            cols = cols + ["y exacta", "|error|"]
            anchos = anchos + [120, 100]
            nuevas = []
            for fila in filas:
                i = fila[0]
                ye = float(f_ex(xs[i]))
                err = abs(ye - ys[i])
                nuevas.append(tuple(fila) + (fmt(ye, 7), f"{err:.2e}"))
            filas = nuevas

        return cols, anchos, filas

    def _mostrar_tabla(self, d):
        for w in self.cont_tabla.winfo_children():
            w.destroy()
        cols, anchos, filas = self._filas_y_columnas(d)
        self.tabla_aprox = cp.Tabla(self.cont_tabla, cols, anchos,
                                    altura=18)
        self.tabla_aprox.pack(fill="both", expand=True)
        self.tabla_aprox.cargar(filas)
        self.tablas = [self.tabla_aprox]

    # ---------------------------------------------------------------- interp
    def _mostrar_interp(self, d):
        interp = d["interp"]; x0 = d["x0"]
        L = []
        L.append("=" * 64)
        L.append(f"  INTERPOLACIÓN — {interp['metodo']}")
        L.append("=" * 64)
        L.append(f"  Punto pedido:   x₀ = {fmt(x0)}")
        L.append(f"  Grado del polinomio: {interp['grado']}   "
                 f"(nodos usados: {interp['grado'] + 1})")
        ini, fin = interp["rango_nodos"]
        L.append(f"  Nodos del intervalo: índices {ini} … {fin}")
        L.append("")
        L.append("  Nodos (xᵢ, yᵢ):")
        for xi, yi in zip(interp["xnodos"], interp["ynodos"]):
            L.append(f"      x = {fmt(xi):>12}    y = {fmt(yi, 8):>14}")
        L.append("")

        if interp["metodo"].startswith("Newton"):
            L.append("  TABLA DE DIFERENCIAS DIVIDIDAS:")
            tabla = interp["tabla"]; m = len(tabla)
            enc = "     " + "".join(f"orden {j:<10}" for j in range(m))
            L.append(enc)
            for i in range(m):
                fila = "   " + "".join(
                    f"{tabla[i][j]:>14.6f}" for j in range(m - i))
                L.append(fila)
            L.append("")
            L.append("  Coeficientes del polinomio de Newton (b₀, b₁, …):")
            for j, b in enumerate(interp["coef"]):
                L.append(f"      b{j} = {b: .8f}")
            L.append("")
            L.append("  P(x) = b₀ + b₁(x−x₀) + b₂(x−x₀)(x−x₁) + …")
        else:
            L.append("  PESOS DE LAGRANGE  Lᵢ(x₀):")
            for i, (xi, w) in enumerate(zip(interp["xnodos"], interp["pesos"])):
                L.append(f"      L{i}(x₀) = {w: .8f}     (nodo x = {fmt(xi)})")
            L.append("")
            L.append("  P(x₀) = Σ  yᵢ · Lᵢ(x₀)")

        L.append("")
        L.append("-" * 64)
        L.append(f"  RESULTADO:   y(x₀ = {fmt(x0)})  ≈  {fmt(interp['valor'], 8)}")
        if d["f_exacta"] is not None:
            exacto = float(d["f_exacta"](x0))
            L.append(f"  Exacto:      y({fmt(x0)})  =  {fmt(exacto, 8)}")
            L.append(f"  Error:       {abs(exacto - interp['valor']):.3e}")
        L.append("-" * 64)

        self.box_interp.configure(state="normal")
        self.box_interp.delete("1.0", "end")
        self.box_interp.insert("1.0", "\n".join(L))
        self.box_interp.configure(state="disabled")

    # ---------------------------------------------------------------- gráfico
    def _dibujar(self, d):
        """Dibuja el gráfico del Ejercicio 1. En pantalla se ven CUATRO cosas:
              • línea verde  → solución exacta (la "respuesta real", si existe);
              • puntos azules → las aproximaciones del método en cada paso;
              • línea naranja punteada → el polinomio interpolante cerca de x₀;
              • estrella roja → el valor interpolado y(x₀) que pide la consigna.
           Que los puntos azules caigan sobre la curva verde = buena aproximación.
        """
        c = tema.colores_grafico()
        self.ax.clear()
        r = d["resultado"]; interp = d["interp"]
        xs, ys = r["xs"], r["ys"]
        a, b, x0 = d["a"], d["b"], d["x0"]

        # Solución exacta (si existe), de fondo.
        if d["f_exacta"] is not None:
            xx = np.linspace(a, b, 400)
            try:
                yy = d["f_exacta"](xx)
                self.ax.plot(xx, yy, color=c["serie2"], lw=2.2,
                             label="Solución exacta", alpha=0.9)
            except Exception:
                pass

        # Aproximación numérica (línea + nodos).
        self.ax.plot(xs, ys, color=c["serie1"], lw=1.6, alpha=0.55,
                     zorder=2)
        self.ax.scatter(xs, ys, color=c["serie1"], s=34, zorder=3,
                        label=f"Aprox. {r['nombre']}", edgecolors="white",
                        linewidths=0.6)

        # Polinomio interpolante en su ventana de nodos.
        xn = interp["xnodos"]
        xx = np.linspace(min(xn), max(xn), 300)
        try:
            yy = interp["P"](xx)
            self.ax.plot(xx, yy, color=c["serie3"], lw=2.0, ls="--",
                         label=f"Interpolante ({interp['metodo'].split()[0]})")
        except Exception:
            pass

        # Punto interpolado (x0, y(x0)).
        y_x0 = interp["valor"]
        self.ax.scatter([x0], [y_x0], color=c["punto"], s=130, zorder=5,
                        marker="*", edgecolors="white", linewidths=1.0,
                        label=f"y(x₀)={y_x0:.4f}")
        self.ax.axvline(x0, color=c["punto"], ls=":", lw=1.1, alpha=0.6)

        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y(x)")
        self.ax.set_title(f"E.D.O.  y′ = {d['expr']}   ·   {r['nombre']}")
        leg = self.ax.legend(loc="best", framealpha=0.9, fontsize=9)
        if leg:
            leg.get_frame().set_facecolor(c["fondo"])
            leg.get_frame().set_edgecolor(c["borde"])
            for txt in leg.get_texts():
                txt.set_color(c["texto"])
        tema.estilizar_figura(self.fig, self.ax)
        self.fig.tight_layout()
        self.canvas.draw()

    # ====================================================================
    def limpiar(self):
        self._ultimo = None
        self.lbl_resumen.configure(
            text="Cargá los datos y presioná «Calcular» para ver los resultados.",
            text_color=tema.TEXTO_TENUE, font=tema.fuente(14))
        for w in self.cont_tabla.winfo_children():
            w.destroy()
        self.box_interp.configure(state="normal")
        self.box_interp.delete("1.0", "end")
        self.box_interp.configure(state="disabled")
        self.ax.clear()
        tema.estilizar_figura(self.fig, self.ax)
        self.ax.set_title("Solución de la E.D.O. e interpolación")
        self.canvas.draw()

    def refrescar_tema(self):
        """Re-estiliza tablas y vuelve a dibujar al cambiar claro/oscuro."""
        for t in self.tablas:
            try:
                t.refrescar_tema()
            except Exception:
                pass
        if self._ultimo:
            self._dibujar(self._ultimo)
        else:
            self.ax.clear()
            tema.estilizar_figura(self.fig, self.ax)
            self.ax.set_title("Solución de la E.D.O. e interpolación")
            self.canvas.draw()
