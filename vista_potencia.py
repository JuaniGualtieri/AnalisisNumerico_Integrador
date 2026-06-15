# -*- coding: utf-8 -*-
"""
============================================================================
  vista_potencia.py  --  EJERCICIO 2: Método de la Potencia Inversa
============================================================================
Interfaz del segundo ejercicio. Permite:
  * cargar una matriz cuadrada de orden n (manual, ejemplo o aleatoria);
  * fijar el vector inicial, el desplazamiento σ, la tolerancia y el máximo
    de iteraciones;
  * hallar un autovalor y su autovector por el método de la potencia inversa;
  * ver la tabla de iteraciones, la curva de convergencia y la verificación
    contra numpy.linalg.eig.
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
    try:
        if isinstance(x, complex):
            if abs(x.imag) < 1e-9:
                return f"{x.real:.{dec}f}"
            return f"{x.real:.{dec}f}{'+' if x.imag >= 0 else '−'}{abs(x.imag):.{dec}f}i"
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return "—"
        if isinstance(x, float) and np.isinf(x):
            return "∞"
        return f"{x:.{dec}f}"
    except Exception:
        return str(x)


def vector_str(v, dec=4):
    return "[ " + "  ".join(f"{c:+.{dec}f}" for c in v) + " ]"


# Matrices de ejemplo por orden.
EJEMPLOS_MATRIZ = {
    2: [[6, 2], [2, 3]],                                  # autovalores 7 y 2
    3: [[4, 1, 0], [1, 3, 1], [0, 1, 2]],                 # menor |λ| ≈ 1.2679
    4: [[10, 1, 0, 0], [1, 9, 1, 0], [0, 1, 8, 1], [0, 0, 1, 7]],
}


class VistaPotencia(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._ultimo = None
        self.entradas_matriz = []   # matriz de CTkEntry
        self.entradas_vector = []   # vector inicial
        self.tablas = []
        self.orden = 3

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_entradas()
        self._construir_panel_resultados()
        self._reconstruir_grilla(self.orden, ejemplo=True)

    # ====================================================================
    #  PANEL IZQUIERDO — ENTRADAS
    # ====================================================================
    def _construir_panel_entradas(self):
        izq = ctk.CTkScrollableFrame(self, fg_color="transparent", width=400)
        izq.grid(row=0, column=0, sticky="ns", padx=(6, 8), pady=6)

        # --- Orden de la matriz ---
        t0 = cp.Tarjeta(izq, "Dimensión", "📐")
        t0.pack(fill="x", pady=(0, 10))
        c0 = t0.cuerpo()
        fila = ctk.CTkFrame(c0, fg_color="transparent")
        fila.pack(fill="x")
        ctk.CTkLabel(fila, text="Orden  n =", font=tema.fuente(13),
                     text_color=tema.TEXTO).pack(side="left")
        self.cmb_orden = ctk.CTkOptionMenu(
            fila, values=[str(i) for i in range(2, 9)], width=80,
            command=self._cambiar_orden, font=tema.fuente(13),
            fg_color=tema.FONDO_SUAVE, button_color=tema.ACENTO,
            button_hover_color=tema.ACENTO_HOVER)
        self.cmb_orden.set("3")
        self.cmb_orden.pack(side="left", padx=8)

        fbtn = ctk.CTkFrame(c0, fg_color="transparent")
        fbtn.pack(fill="x", pady=(10, 0))
        cp.boton(fbtn, "Ejemplo", self._cargar_ejemplo, ancho=110, icono="📋",
                 color=tema.FONDO_SUAVE, hover=tema.BORDE).pack(side="left", padx=(0, 6))
        cp.boton(fbtn, "Aleatoria", self._cargar_aleatoria, ancho=110, icono="🎲",
                 color=tema.FONDO_SUAVE, hover=tema.BORDE).pack(side="left", padx=(0, 6))
        cp.boton(fbtn, "Simétrica", self._cargar_simetrica, ancho=110, icono="🔁",
                 color=tema.FONDO_SUAVE, hover=tema.BORDE).pack(side="left")

        # --- Matriz A ---
        t1 = cp.Tarjeta(izq, "Matriz  A", "🔢")
        t1.pack(fill="x", pady=(0, 10))
        self.cont_matriz = t1.cuerpo()

        # --- Vector inicial ---
        t2 = cp.Tarjeta(izq, "Vector inicial  x₀", "➡️")
        t2.pack(fill="x", pady=(0, 10))
        self.cont_vector = t2.cuerpo()

        # --- Parámetros ---
        t3 = cp.Tarjeta(izq, "Parámetros del método", "⚙️")
        t3.pack(fill="x", pady=(0, 10))
        c3 = t3.cuerpo()
        self.ent_sigma = cp.campo(c3, "Desplazamiento  σ", "0",
                                  ayuda="Busca el autovalor MÁS CERCANO a σ.\n"
                                        "σ = 0  →  autovalor de menor módulo.")
        self.ent_tol = cp.campo(c3, "Tolerancia", "1e-10",
                                ayuda="Corte cuando |Δλ| < tolerancia.")
        self.ent_iter = cp.campo(c3, "Máx. iteraciones", "200")
        ctk.CTkLabel(c3, text="Normalización:", font=tema.fuente(12),
                     text_color=tema.TEXTO_TENUE, anchor="w").pack(fill="x", pady=(6, 0))
        self.cmb_norma = ctk.CTkOptionMenu(
            c3, values=["infinito (∞)", "euclidiana (2)"],
            font=tema.fuente(12), fg_color=tema.FONDO_SUAVE,
            button_color=tema.ACENTO, button_hover_color=tema.ACENTO_HOVER)
        self.cmb_norma.pack(fill="x", pady=(4, 0))

        # --- Botones ---
        botones = ctk.CTkFrame(izq, fg_color="transparent")
        botones.pack(fill="x", pady=(4, 12))
        cp.boton(botones, "Calcular", self.calcular, icono="▶",
                 color=tema.EXITO, hover=tema.EXITO_HOVER).pack(fill="x", pady=(0, 6))
        cp.boton(botones, "Limpiar", self.limpiar, icono="🗑",
                 color=tema.FONDO_SUAVE, hover=tema.BORDE).pack(fill="x")

    def _reconstruir_grilla(self, n, ejemplo=False, valores=None):
        """Crea la grilla de n×n entradas para la matriz y n entradas de vector."""
        self.orden = n
        for w in self.cont_matriz.winfo_children():
            w.destroy()
        for w in self.cont_vector.winfo_children():
            w.destroy()

        grilla = ctk.CTkFrame(self.cont_matriz, fg_color="transparent")
        grilla.pack()
        self.entradas_matriz = []
        ancho_celda = max(48, 72 - 4 * n)
        for i in range(n):
            filaw = []
            for j in range(n):
                e = ctk.CTkEntry(grilla, width=ancho_celda, height=34,
                                 font=tema.fuente_mono(12), justify="center")
                e.grid(row=i, column=j, padx=3, pady=3)
                filaw.append(e)
            self.entradas_matriz.append(filaw)

        # Vector inicial
        gridv = ctk.CTkFrame(self.cont_vector, fg_color="transparent")
        gridv.pack()
        self.entradas_vector = []
        for j in range(n):
            e = ctk.CTkEntry(gridv, width=ancho_celda, height=34,
                             font=tema.fuente_mono(12), justify="center")
            e.grid(row=0, column=j, padx=3, pady=3)
            e.insert(0, "1")
            self.entradas_vector.append(e)

        # Rellenar valores
        if valores is not None:
            self._set_matriz(valores)
        elif ejemplo:
            self._cargar_ejemplo()

    def _set_matriz(self, M):
        for i in range(self.orden):
            for j in range(self.orden):
                self.entradas_matriz[i][j].delete(0, "end")
                self.entradas_matriz[i][j].insert(0, str(M[i][j]))

    def _cambiar_orden(self, valor):
        self._reconstruir_grilla(int(valor), ejemplo=True)

    def _cargar_ejemplo(self):
        n = self.orden
        if n in EJEMPLOS_MATRIZ:
            self._set_matriz(EJEMPLOS_MATRIZ[n])
        else:
            # Tridiagonal diagonalmente dominante como ejemplo genérico.
            M = [[0] * n for _ in range(n)]
            for i in range(n):
                M[i][i] = n + 2 - i
                if i > 0:
                    M[i][i - 1] = 1
                if i < n - 1:
                    M[i][i + 1] = 1
            self._set_matriz(M)

    def _cargar_aleatoria(self):
        n = self.orden
        M = np.random.randint(-6, 7, size=(n, n))
        # Aseguramos que no sea singular reforzando la diagonal.
        for i in range(n):
            M[i, i] += n * 2
        self._set_matriz(M.tolist())

    def _cargar_simetrica(self):
        n = self.orden
        M = np.random.randint(-5, 6, size=(n, n))
        M = M + M.T
        for i in range(n):
            M[i, i] += n * 2
        self._set_matriz(M.tolist())

    # ====================================================================
    #  PANEL DERECHO — RESULTADOS
    # ====================================================================
    def _construir_panel_resultados(self):
        der = ctk.CTkFrame(self, fg_color="transparent")
        der.grid(row=0, column=1, sticky="nsew", padx=(0, 6), pady=6)
        der.grid_rowconfigure(1, weight=1)
        der.grid_columnconfigure(0, weight=1)

        self.tarjeta_res = ctk.CTkFrame(der, fg_color=tema.FONDO_PANEL,
                                        corner_radius=14, border_width=1,
                                        border_color=tema.BORDE)
        self.tarjeta_res.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.lbl_resumen = ctk.CTkLabel(
            self.tarjeta_res,
            text="Cargá la matriz y presioná «Calcular» para hallar el autovalor.",
            font=tema.fuente(14), text_color=tema.TEXTO_TENUE,
            justify="left", anchor="w")
        self.lbl_resumen.pack(fill="x", padx=20, pady=16)

        self.subtabs = ctk.CTkTabview(
            der, fg_color=tema.FONDO_PANEL,
            segmented_button_fg_color=tema.FONDO_SUAVE,
            segmented_button_selected_color=tema.ACENTO,
            segmented_button_selected_hover_color=tema.ACENTO_HOVER,
            text_color=tema.TEXTO, corner_radius=12)
        self.subtabs.grid(row=1, column=0, sticky="nsew")

        self.tab_iter = self.subtabs.add("📋  Iteraciones")
        self.tab_conv = self.subtabs.add("📈  Convergencia")
        self.tab_verif = self.subtabs.add("🔎  Verificación")

        self.cont_tabla = ctk.CTkFrame(self.tab_iter, fg_color="transparent")
        self.cont_tabla.pack(fill="both", expand=True, padx=6, pady=6)
        self.tabla_iter = None

        self._construir_grafico(self.tab_conv)

        self.box_verif = ctk.CTkTextbox(self.tab_verif, font=tema.fuente_mono(12),
                                        fg_color=tema.FONDO_PANEL,
                                        text_color=tema.TEXTO, wrap="none")
        self.box_verif.pack(fill="both", expand=True, padx=8, pady=8)
        self.box_verif.insert("1.0", "Aquí se mostrará la verificación con "
                                     "numpy.linalg.eig.")
        self.box_verif.configure(state="disabled")

    def _construir_grafico(self, master):
        cont = ctk.CTkFrame(master, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=6, pady=6)
        self.fig = Figure(figsize=(7, 4.6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        tema.estilizar_figura(self.fig, [self.ax1, self.ax2])
        self.canvas = FigureCanvasTkAgg(self.fig, master=cont)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        barra = tk.Frame(cont, bg=tema.colores_grafico()["fondo"])
        barra.pack(fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, barra)
        self.toolbar.update()
        self.fig.tight_layout()
        self.canvas.draw()

    # ====================================================================
    #  LÓGICA
    # ====================================================================
    def _leer_matriz(self):
        n = self.orden
        A = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                txt = self.entradas_matriz[i][j].get().strip()
                if txt == "":
                    raise ValueError(f"Falta el valor en la posición "
                                     f"({i + 1}, {j + 1}).")
                try:
                    A[i, j] = float(txt)
                except ValueError:
                    raise ValueError(f"«{txt}» no es un número válido en la "
                                     f"posición ({i + 1}, {j + 1}).")
        return A

    def _leer_vector(self):
        n = self.orden
        v = np.zeros(n)
        for j in range(n):
            txt = self.entradas_vector[j].get().strip()
            v[j] = float(txt) if txt else 0.0
        if np.linalg.norm(v) == 0:
            v = np.ones(n)
        return v

    def calcular(self):
        try:
            A = self._leer_matriz()
            x0 = self._leer_vector()
            sigma = float(self.ent_sigma.get())
            tol = float(self.ent_tol.get())
            max_iter = int(float(self.ent_iter.get()))
            norma = "inf" if self.cmb_norma.get().startswith("infinito") else "2"

            res = mn.potencia_inversa(A, sigma=sigma, x0=x0, tol=tol,
                                      max_iter=max_iter, norma=norma)

            # Verificación con numpy.
            vals, vecs = mn.verificar_autovalores(A)
            ref, idx = mn.autovalor_de_referencia(A, res["autovalor"])

            datos = dict(A=A, res=res, vals=vals, vecs=vecs, ref=ref,
                         idx=idx, sigma=sigma)
            self._ultimo = datos

            self._mostrar_resumen(datos)
            self._mostrar_tabla(datos)
            self._mostrar_verificacion(datos)
            self._dibujar(datos)
        except Exception as err:
            messagebox.showerror("Error", str(err))

    # ---------------------------------------------------------------- resumen
    def _mostrar_resumen(self, d):
        res = d["res"]
        estado = "✓ convergió" if res["convergio"] else "⚠ alcanzó el máximo de iteraciones"
        ref = d["ref"]
        try:
            difer = abs(complex(ref) - res["autovalor_rayleigh"])
        except Exception:
            difer = float("nan")
        partes = [
            f"AUTOVALOR hallado:  λ ≈ {fmt(res['autovalor_rayleigh'], 8)}      "
            f"({estado} en {res['iteraciones']} iteraciones)",
            f"AUTOVECTOR (normalizado):  v ≈ {vector_str(res['autovector'])}",
            f"Residuo  ‖A·v − λ·v‖ = {res['residuo']:.2e}      |      "
            f"σ = {fmt(d['sigma'])}",
            f"Referencia (numpy)  λ = {fmt(ref, 8)}   →   diferencia = {difer:.2e}",
        ]
        self.lbl_resumen.configure(text="\n".join(partes), text_color=tema.TEXTO,
                                   font=tema.fuente_mono(13))

    # ---------------------------------------------------------------- tabla
    def _mostrar_tabla(self, d):
        for w in self.cont_tabla.winfo_children():
            w.destroy()
        cols = ["k", "λ (escala)", "λ (Rayleigh)", "|Δλ|", "autovector  vᵀ"]
        anchos = [50, 150, 150, 110, 360]
        filas = []
        for it in d["res"]["detalle"]:
            filas.append((
                it["k"], fmt(it["lambda"], 8), fmt(it["rayleigh"], 8),
                "—" if not np.isfinite(it["error"]) else f"{it['error']:.2e}",
                vector_str(it["vector"], 4),
            ))
        self.tabla_iter = cp.Tabla(self.cont_tabla, cols, anchos, altura=18)
        self.tabla_iter.pack(fill="both", expand=True)
        self.tabla_iter.cargar(filas)
        self.tablas = [self.tabla_iter]

    # ---------------------------------------------------------------- verif
    def _mostrar_verificacion(self, d):
        A = d["A"]; res = d["res"]; vals = d["vals"]; vecs = d["vecs"]
        L = []
        L.append("=" * 66)
        L.append("  VERIFICACIÓN CON numpy.linalg.eig")
        L.append("=" * 66)
        L.append("  Matriz A:")
        for fila in A:
            L.append("     [ " + "  ".join(f"{v:8.3f}" for v in fila) + " ]")
        L.append("")
        L.append("  Todos los autovalores de A:")
        orden = np.argsort(np.abs(vals))
        for r, k in enumerate(orden):
            marca = "  ← hallado por el método" if k == d["idx"] else ""
            L.append(f"     λ{r + 1} = {fmt(vals[k], 8):>16}   "
                     f"(|λ| = {abs(vals[k]):.6f}){marca}")
        L.append("")
        L.append("  Autovector de referencia (numpy) para el λ hallado:")
        vref = np.real_if_close(vecs[:, d["idx"]])
        vref = vref / np.linalg.norm(vref)
        if vref[np.argmax(np.abs(vref))] < 0:
            vref = -vref
        L.append("     " + vector_str(vref, 6))
        L.append("")
        L.append("  Autovector hallado por el método:")
        L.append("     " + vector_str(res["autovector"], 6))
        L.append("")
        # Comparación de autovectores (ángulo).
        cos = abs(np.dot(vref, res["autovector"]))
        cos = min(1.0, cos)
        ang = np.degrees(np.arccos(cos))
        L.append(f"  Coincidencia de autovectores:  cos θ = {cos:.8f}  "
                 f"(ángulo ≈ {ang:.4f}°)")
        L.append("")
        L.append("-" * 66)
        L.append(f"  CONCLUSIÓN:  el método de la potencia inversa con σ = "
                 f"{fmt(d['sigma'])}")
        L.append(f"  recuperó correctamente el autovalor  λ = "
                 f"{fmt(res['autovalor_rayleigh'], 8)}")
        L.append(f"  con un residuo de {res['residuo']:.2e}.")
        L.append("-" * 66)

        self.box_verif.configure(state="normal")
        self.box_verif.delete("1.0", "end")
        self.box_verif.insert("1.0", "\n".join(L))
        self.box_verif.configure(state="disabled")

    # ---------------------------------------------------------------- gráfico
    def _dibujar(self, d):
        c = tema.colores_grafico()
        res = d["res"]
        self.ax1.clear(); self.ax2.clear()

        ks = [it["k"] for it in res["detalle"]]
        lam = [it["lambda"] for it in res["detalle"]]
        ray = [it["rayleigh"] for it in res["detalle"]]
        errs = [it["error"] for it in res["detalle"]]

        # (1) Convergencia del autovalor
        self.ax1.plot(ks, lam, "-o", color=c["serie1"], ms=4, lw=1.6,
                      label="λ (factor de escala)")
        self.ax1.plot(ks, ray, "-s", color=c["serie3"], ms=3.5, lw=1.4,
                      label="λ (Rayleigh)")
        self.ax1.axhline(float(np.real(d["ref"])), color=c["serie2"], ls="--",
                         lw=1.4, label=f"λ referencia = {float(np.real(d['ref'])):.5f}")
        self.ax1.set_xlabel("iteración k")
        self.ax1.set_ylabel("λ")
        self.ax1.set_title("Convergencia del autovalor")
        leg1 = self.ax1.legend(loc="best", fontsize=8)

        # (2) Error en escala logarítmica
        kk = [k for k, e in zip(ks, errs) if np.isfinite(e) and e > 0]
        ee = [e for e in errs if np.isfinite(e) and e > 0]
        if ee:
            self.ax2.semilogy(kk, ee, "-o", color=c["punto"], ms=4, lw=1.6,
                              label="|Δλ| entre iteraciones")
            leg2 = self.ax2.legend(loc="best", fontsize=8)
        else:
            # Convergencia exacta/inmediata: no hay error positivo que graficar.
            leg2 = None
            self.ax2.text(0.5, 0.5, "Convergencia inmediata\n(sin variación de λ)",
                          ha="center", va="center", transform=self.ax2.transAxes,
                          color=c["texto"], fontsize=11)
        self.ax2.set_xlabel("iteración k")
        self.ax2.set_ylabel("error (log)")
        self.ax2.set_title("Error de convergencia")

        for leg in (leg1, leg2):
            if leg:
                leg.get_frame().set_facecolor(c["fondo"])
                leg.get_frame().set_edgecolor(c["borde"])
                for txt in leg.get_texts():
                    txt.set_color(c["texto"])

        tema.estilizar_figura(self.fig, [self.ax1, self.ax2])
        self.fig.tight_layout()
        self.canvas.draw()

    # ====================================================================
    def limpiar(self):
        self._ultimo = None
        self.lbl_resumen.configure(
            text="Cargá la matriz y presioná «Calcular» para hallar el autovalor.",
            text_color=tema.TEXTO_TENUE, font=tema.fuente(14))
        for w in self.cont_tabla.winfo_children():
            w.destroy()
        self.box_verif.configure(state="normal")
        self.box_verif.delete("1.0", "end")
        self.box_verif.configure(state="disabled")
        self.ax1.clear(); self.ax2.clear()
        tema.estilizar_figura(self.fig, [self.ax1, self.ax2])
        self.canvas.draw()

    def refrescar_tema(self):
        for t in self.tablas:
            try:
                t.refrescar_tema()
            except Exception:
                pass
        if self._ultimo:
            self._dibujar(self._ultimo)
        else:
            self.ax1.clear(); self.ax2.clear()
            tema.estilizar_figura(self.fig, [self.ax1, self.ax2])
            self.canvas.draw()
