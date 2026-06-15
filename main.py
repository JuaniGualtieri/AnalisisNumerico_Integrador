# -*- coding: utf-8 -*-
"""
============================================================================
        TRABAJO FINAL INTEGRADOR  --  ANÁLISIS NUMÉRICO  (I.S.I.)
        Universidad de la Cuenca del Plata
============================================================================
  Aplicación de escritorio que resuelve los dos ejercicios del integrador:

    [ Ejercicio 1 ]  Resolución de una E.D.O. de primer orden  y' = f(x,y)
                     por Euler Modificado / Runge-Kutta 4 / Milne, con
                     interpolación del valor y(x0).

    [ Ejercicio 2 ]  Cálculo de un autovalor y su autovector mediante el
                     método de la Potencia Inversa.

  Tecnologías:  Python 3 + CustomTkinter (interfaz) + Matplotlib (gráficos)
                + NumPy / SymPy (cálculo).

  Ejecutar con:   python main.py
============================================================================
"""

import customtkinter as ctk

import tema
from vista_edo import VistaEDO
from vista_potencia import VistaPotencia


# Configuración global de apariencia.
ctk.set_appearance_mode("Dark")          # "Dark" / "Light" / "System"
ctk.set_default_color_theme("blue")


class Aplicacion(ctk.CTk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Análisis Numérico · Trabajo Final Integrador")
        self.geometry("1280x820")
        self.minsize(1100, 720)
        self.configure(fg_color=tema.FONDO_APP)

        self._construir_encabezado()
        self._construir_pestanas()
        self._construir_pie()

        # Centrar la ventana en la pantalla.
        self.after(10, self._centrar)

    # ---------------------------------------------------------------- encabezado
    def _construir_encabezado(self):
        cab = ctk.CTkFrame(self, fg_color=tema.FONDO_PANEL, corner_radius=0,
                           height=78, border_width=0)
        cab.pack(fill="x", side="top")
        cab.pack_propagate(False)

        izq = ctk.CTkFrame(cab, fg_color="transparent")
        izq.pack(side="left", padx=24, pady=10)

        ctk.CTkLabel(izq, text="📐  Análisis Numérico",
                     font=tema.fuente(22, "bold"),
                     text_color=tema.TEXTO).pack(anchor="w")
        ctk.CTkLabel(izq, text="Trabajo Final Integrador · Ing. en Sistemas de Información",
                     font=tema.fuente(12),
                     text_color=tema.TEXTO_TENUE).pack(anchor="w")

        der = ctk.CTkFrame(cab, fg_color="transparent")
        der.pack(side="right", padx=24)

        self.sw_tema = ctk.CTkSwitch(der, text="Modo claro",
                                     command=self._alternar_tema,
                                     font=tema.fuente(12),
                                     progress_color=tema.ACENTO)
        self.sw_tema.pack(side="right", pady=8)

    # ---------------------------------------------------------------- pestañas
    def _construir_pestanas(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color=tema.FONDO_APP,
            segmented_button_fg_color=tema.FONDO_PANEL,
            segmented_button_selected_color=tema.ACENTO,
            segmented_button_selected_hover_color=tema.ACENTO_HOVER,
            segmented_button_unselected_color=tema.FONDO_PANEL,
            text_color=tema.TEXTO, corner_radius=12,
        )
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(12, 4))
        self.tabs._segmented_button.configure(font=tema.fuente(13, "bold"))

        t_inicio = self.tabs.add("  🏠  Inicio  ")
        t_edo = self.tabs.add("  📈  EDO + Interpolación  ")
        t_pot = self.tabs.add("  🧮  Potencia Inversa  ")

        self._construir_inicio(t_inicio)
        self.vista_edo = VistaEDO(t_edo)
        self.vista_edo.pack(fill="both", expand=True)
        self.vista_pot = VistaPotencia(t_pot)
        self.vista_pot.pack(fill="both", expand=True)

        self.tabs.set("  📈  EDO + Interpolación  ")

    def _construir_inicio(self, master):
        cont = ctk.CTkScrollableFrame(master, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=8, pady=8)

        # Tarjeta de bienvenida
        bienv = ctk.CTkFrame(cont, fg_color=tema.FONDO_PANEL, corner_radius=16,
                             border_width=1, border_color=tema.BORDE)
        bienv.pack(fill="x", padx=20, pady=(10, 16))
        ctk.CTkLabel(bienv, text="Bienvenido/a 👋",
                     font=tema.fuente(24, "bold"), text_color=tema.TEXTO).pack(
            anchor="w", padx=24, pady=(20, 4))
        intro = ("Esta aplicación resuelve por completo los dos ejercicios del "
                 "Examen Integrador de Análisis Numérico. Elegí una pestaña "
                 "para comenzar. Cada módulo incluye la teoría aplicada, una "
                 "tabla con el procedimiento paso a paso y gráficos interactivos.")
        ctk.CTkLabel(bienv, text=intro, font=tema.fuente(14),
                     text_color=tema.TEXTO_TENUE, justify="left",
                     wraplength=980).pack(anchor="w", padx=24, pady=(0, 20))

        # Dos tarjetas descriptivas
        fila = ctk.CTkFrame(cont, fg_color="transparent")
        fila.pack(fill="x", padx=20)
        fila.grid_columnconfigure((0, 1), weight=1, uniform="x")

        self._tarjeta_resumen(
            fila, 0, "📈  Ejercicio 1 — EDO + Interpolación",
            "Resuelve y' = f(x, y) con y(a) conocido en el intervalo [a, b].",
            [
                "• Métodos: Euler Modificado · Runge-Kutta 4 · Milne.",
                "• Paso h = (b − a) / n  (fracción del intervalo).",
                "• Interpolación de y(x₀) por Newton o Lagrange.",
                "• Compara con la solución exacta y muestra el error.",
                "• Gráfico de la solución, los nodos y el punto interpolado.",
            ],
            tema.ACENTO)

        self._tarjeta_resumen(
            fila, 1, "🧮  Ejercicio 2 — Potencia Inversa",
            "Halla un autovalor y su autovector de una matriz n × n.",
            [
                "• Método de la potencia inversa con desplazamiento σ.",
                "• Factorización LU con pivoteo parcial (una sola vez).",
                "• σ = 0 → autovalor de menor módulo.",
                "• Tabla de iteraciones y curva de convergencia.",
                "• Verificación con numpy.linalg.eig.",
            ],
            tema.VIOLETA)

        # Cómo usar
        guia = ctk.CTkFrame(cont, fg_color=tema.FONDO_PANEL, corner_radius=16,
                            border_width=1, border_color=tema.BORDE)
        guia.pack(fill="x", padx=20, pady=16)
        ctk.CTkLabel(guia, text="¿Cómo se usa?", font=tema.fuente(18, "bold"),
                     text_color=tema.TEXTO).pack(anchor="w", padx=24, pady=(18, 6))
        pasos = ("1.  Elegí la pestaña del ejercicio.\n"
                 "2.  Cargá los datos (o usá un ejemplo precargado).\n"
                 "3.  Presioná «Calcular» para ver la tabla y los gráficos.\n"
                 "4.  Con el switch de arriba a la derecha cambiás el tema claro/oscuro.")
        ctk.CTkLabel(guia, text=pasos, font=tema.fuente(14),
                     text_color=tema.TEXTO_TENUE, justify="left").pack(
            anchor="w", padx=24, pady=(0, 20))

    def _tarjeta_resumen(self, master, col, titulo, subtitulo, items, color):
        card = ctk.CTkFrame(master, fg_color=tema.FONDO_PANEL, corner_radius=16,
                            border_width=1, border_color=tema.BORDE)
        card.grid(row=0, column=col, sticky="nsew", padx=10, pady=4)
        barra = ctk.CTkFrame(card, fg_color=color, height=6, corner_radius=6)
        barra.pack(fill="x", padx=20, pady=(16, 10))
        ctk.CTkLabel(card, text=titulo, font=tema.fuente(17, "bold"),
                     text_color=tema.TEXTO, justify="left",
                     wraplength=420).pack(anchor="w", padx=20)
        ctk.CTkLabel(card, text=subtitulo, font=tema.fuente(13),
                     text_color=tema.TEXTO_TENUE, justify="left",
                     wraplength=420).pack(anchor="w", padx=20, pady=(2, 10))
        for it in items:
            ctk.CTkLabel(card, text=it, font=tema.fuente(13),
                         text_color=tema.TEXTO, justify="left",
                         wraplength=420).pack(anchor="w", padx=20, pady=1)
        ctk.CTkLabel(card, text="", height=8).pack()

    # ---------------------------------------------------------------- pie
    def _construir_pie(self):
        pie = ctk.CTkFrame(self, fg_color=tema.FONDO_PANEL, corner_radius=0,
                           height=32)
        pie.pack(fill="x", side="bottom")
        pie.pack_propagate(False)
        ctk.CTkLabel(pie, text="Universidad de la Cuenca del Plata · Análisis Numérico",
                     font=tema.fuente(11), text_color=tema.TEXTO_TENUE).pack(
            side="left", padx=20)
        ctk.CTkLabel(pie, text="Python · CustomTkinter · NumPy · Matplotlib · SymPy",
                     font=tema.fuente(11), text_color=tema.TEXTO_TENUE).pack(
            side="right", padx=20)

    # ---------------------------------------------------------------- acciones
    def _alternar_tema(self):
        modo = "Light" if self.sw_tema.get() else "Dark"
        ctk.set_appearance_mode(modo)
        self.sw_tema.configure(text="Modo oscuro" if modo == "Light" else "Modo claro")
        # Notificar a las vistas para re-estilizar gráficos y tablas.
        self.vista_edo.refrescar_tema()
        self.vista_pot.refrescar_tema()

    def _centrar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{max(0, y - 20)}")


def main():
    app = Aplicacion()
    app.mainloop()


if __name__ == "__main__":
    main()
